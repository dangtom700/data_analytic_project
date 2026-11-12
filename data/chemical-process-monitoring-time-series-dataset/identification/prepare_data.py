"""Prepare system-identification datasets from the cleaned per-reactor files.

A model can only be identified from data where the plant is behaving as one
plant.  A fault changes the plant, so every fault episode is a hard boundary:
the usable records are the fault-free stretches *between* consecutive fault
episodes, or between a fault episode and the start/end of the record.

For each reactor this script

  1. finds the fault episodes (contiguous runs of ``fault_type != 0``),
  2. forms the fault-free segments they delimit,
  3. optionally trims a guard band off every fault-adjacent end (faults
     develop gradually, so the last minutes before onset are labelled 0 but
     already drifting),
  4. picks the longest segment that passes the missing-data checks,
  5. exports it with the identification columns, and writes a catalogue of
     every segment plus a manifest describing what was chosen and why.

Sensor dropout in this dataset is ~6% missing-at-random in every sensor
column, injected by the simulator and *not* target-driven.  Subspace /
PEM identification routines (MATLAB ``iddata`` + ``n4sid``/``ssest``,
``nlgreyest``) tolerate NaN gaps, so the NaNs are preserved by default
rather than imputed -- imputing them would feed the estimator invented
dynamics.  The thresholds below are the acceptance test; raise
``INTERPOLATE_MAX_GAP`` only if the downstream estimator cannot take NaN.

Run from anywhere:  python identification/prepare_data.py
"""

from __future__ import annotations

import glob
import json
import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Paths -- resolved from this file, not from the current working directory
# --------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
DATASET_ROOT = os.path.dirname(HERE)
SOURCE_DIR = os.path.join(DATASET_ROOT, "cleaning")
EXPORT_DIR = os.path.join(HERE, "data")
SOURCE_GLOB = "chemical_process_timeseries_[AB]_R*.csv"

# --------------------------------------------------------------------------
# Signal selection (identification/README.md)
# --------------------------------------------------------------------------
TIME_COL = "minute"          # integer minutes since 2024-01-01 00:00:00
FAULT_COL = "fault_type"
TS_SECONDS = 60              # uniform sampling interval of the source grid

# ---- Plant point of view (what identification is run on) -----------------
# README.md's selection, taken at the plant boundary: PLANT_SIGNAL_COLS are
# the signals available to drive and condition the model, PLANT_OBSERVED_COLS
# are the variables the model has to explain.  These two groups decide what is
# exported and in what order.
PLANT_SIGNAL_COLS = [
    "ambient_temp_effect",
    "reactor_temp",
    "reactor_pressure",
    "feed_flow_rate",
    "coolant_flow_rate",
    "agitator_speed_rpm",
    "motor_current",
]

PLANT_OBSERVED_COLS = [
    "reaction_rate",
    "conversion_rate",
    "selectivity",
    "vibration_rms",
    "power_consumption_kw",
]

# ---- Controller point of view (channel roles for the MPC + EKF stage) ----
# The same twelve signals regrouped by the role they play once a controller is
# wrapped around the identified model.  Identification itself does not use this
# map; it is carried into the manifest so the control stage reads one
# definition instead of re-deriving it.  Re-assign a channel by editing this
# dict alone -- every signal must appear exactly once, which
# validate_control_roles() enforces before anything is written.
CONTROL_ROLES = {
    # Knobs the controller sets directly.
    "manipulated": [
        "feed_flow_rate",
        "coolant_flow_rate",
        "agitator_speed_rpm",
    ],
    # Actuator-side measurements: not knobs, but they observe the actuators
    # rather than the reaction, so they carry actuator state and load into the
    # estimator.  vibration_rms and power_consumption_kw are the other two
    # candidates for this group if agitator load is to be estimated from more
    # than motor_current alone -- they sit in "monitored" until then.
    "actuator_measured": [
        "motor_current",
    ],
    # Measured but not controllable: the disturbance the MPC has to reject.
    "disturbance": [
        "ambient_temp_effect",
    ],
    # Setpoint-tracking outputs.  Regime setpoints are constants:
    # A = 180 C / 12 bar, B = 192 C / 13.5 bar.
    "controlled": [
        "reactor_temp",
        "reactor_pressure",
    ],
    # Observed for performance and condition, not tracked by the controller.
    "monitored": [
        "reaction_rate",
        "conversion_rate",
        "selectivity",
        "vibration_rms",
        "power_consumption_kw",
    ],
}

SIGNAL_COLS = PLANT_SIGNAL_COLS + PLANT_OBSERVED_COLS
READ_COLS = [TIME_COL, FAULT_COL] + SIGNAL_COLS

# --------------------------------------------------------------------------
# Segmentation / acceptance parameters
# --------------------------------------------------------------------------
# Minutes trimmed off a segment end that touches a fault episode.  0 keeps the
# segment exactly as delimited by the fault labels; increase it to discard the
# gradual-onset lead-in (and the recovery tail) that is still labelled normal.
GUARD_MIN = 0

# Segments shorter than this are not worth identifying on (1 day).
MIN_SEGMENT_MIN = 1440

# Missing-data acceptance test, applied per signal column on the candidate
# segment.  A candidate failing either test is rejected and the next-longest
# candidate is tried.
NAN_MAX_FRAC = 0.10   # at most 10% missing in any one column
NAN_MAX_GAP = 10      # no single gap longer than 10 consecutive samples

# Fill NaN runs no longer than this many samples by linear interpolation;
# longer runs stay NaN.  0 disables filling and preserves every NaN.
INTERPOLATE_MAX_GAP = 0


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def validate_control_roles() -> None:
    """Every exported signal must carry exactly one controller-side role.

    Catches the two ways CONTROL_ROLES drifts out of step with the plant-side
    selection: a channel listed under two roles, and a channel added to (or
    removed from) the export without being given a role.
    """
    seen: dict[str, str] = {}
    for role, cols in CONTROL_ROLES.items():
        for col in cols:
            if col in seen:
                raise ValueError(
                    f"CONTROL_ROLES: {col!r} appears under both "
                    f"{seen[col]!r} and {role!r}"
                )
            seen[col] = role

    missing = [c for c in SIGNAL_COLS if c not in seen]
    unknown = [c for c in seen if c not in SIGNAL_COLS]
    if missing:
        raise ValueError(f"CONTROL_ROLES: exported but unassigned: {missing}")
    if unknown:
        raise ValueError(f"CONTROL_ROLES: assigned but not exported: {unknown}")


def max_true_run(mask: np.ndarray) -> int:
    """Length of the longest run of True in a 1-D boolean array."""
    mask = np.asarray(mask, dtype=bool)
    if mask.size == 0 or not mask.any():
        return 0
    padded = np.concatenate(([False], mask, [False]))
    edges = np.flatnonzero(padded[1:] != padded[:-1])
    return int((edges[1::2] - edges[0::2]).max())


def runs_of_true(mask: np.ndarray) -> list[tuple[int, int]]:
    """Inclusive (start, end) index pairs for every run of True."""
    mask = np.asarray(mask, dtype=bool)
    if mask.size == 0 or not mask.any():
        return []
    padded = np.concatenate(([False], mask, [False]))
    edges = np.flatnonzero(padded[1:] != padded[:-1])
    return [(int(a), int(b) - 1) for a, b in zip(edges[0::2], edges[1::2])]


@dataclass
class Segment:
    """A fault-free stretch of one reactor's record, in row positions."""

    reactor: str
    start: int                 # inclusive, after guard trim
    end: int                   # inclusive, after guard trim
    raw_start: int             # inclusive, as delimited by the fault labels
    raw_end: int
    left_boundary: str         # "series_begin" or "fault_<code>"
    right_boundary: str        # "series_end" or "fault_<code>"
    nan_frac: dict = field(default_factory=dict)
    nan_max_gap: dict = field(default_factory=dict)
    rejected: str | None = None

    @property
    def length(self) -> int:
        return self.end - self.start + 1

    @property
    def worst_nan_frac(self) -> float:
        return max(self.nan_frac.values()) if self.nan_frac else 0.0

    @property
    def worst_nan_gap(self) -> int:
        return max(self.nan_max_gap.values()) if self.nan_max_gap else 0


def fault_episodes(fault_type: np.ndarray) -> list[tuple[int, int, list[int]]]:
    """Contiguous runs of fault_type != 0, as (start, end, codes present)."""
    fault_type = np.asarray(fault_type)
    episodes = []
    for a, b in runs_of_true(fault_type != 0):
        codes = sorted({int(c) for c in fault_type[a : b + 1]})
        episodes.append((a, b, codes))
    return episodes


def fault_free_segments(
    reactor: str,
    fault_type: np.ndarray,
    guard: int = GUARD_MIN,
) -> list[Segment]:
    """Segments delimited by fault episodes and by the ends of the record.

    Boundary labels record what closed each end, so a segment can be traced
    back to "between fault 2 and fault 1" or "from the start of the record".
    """
    n = len(fault_type)
    episodes = fault_episodes(fault_type)

    segments: list[Segment] = []
    cursor = 0
    left_label = "series_begin"

    for a, b, codes in episodes:
        if a - cursor > 0:
            segments.append(
                Segment(
                    reactor=reactor,
                    start=cursor,
                    end=a - 1,
                    raw_start=cursor,
                    raw_end=a - 1,
                    left_boundary=left_label,
                    right_boundary="fault_" + "+".join(str(c) for c in codes),
                )
            )
        cursor = b + 1
        left_label = "fault_" + "+".join(str(c) for c in codes)

    if n - cursor > 0:
        segments.append(
            Segment(
                reactor=reactor,
                start=cursor,
                end=n - 1,
                raw_start=cursor,
                raw_end=n - 1,
                left_boundary=left_label,
                right_boundary="series_end",
            )
        )

    # Trim the guard band off fault-adjacent ends only; the record's own start
    # and end are not contaminated by a developing fault.
    if guard > 0:
        for seg in segments:
            if seg.left_boundary != "series_begin":
                seg.start += guard
            if seg.right_boundary != "series_end":
                seg.end -= guard

    return [s for s in segments if s.length > 0]


def score_missing(frame: pd.DataFrame, segment: Segment) -> None:
    """Fill in the per-column missing-data statistics of a segment."""
    block = frame.iloc[segment.start : segment.end + 1]
    for col in SIGNAL_COLS:
        mask = block[col].isna().to_numpy()
        segment.nan_frac[col] = float(mask.mean())
        segment.nan_max_gap[col] = max_true_run(mask)


def accept(segment: Segment) -> str | None:
    """Reason the segment is unusable, or None if it passes."""
    if segment.length < MIN_SEGMENT_MIN:
        return f"shorter than MIN_SEGMENT_MIN ({segment.length} < {MIN_SEGMENT_MIN})"
    if segment.worst_nan_frac > NAN_MAX_FRAC:
        worst = max(segment.nan_frac, key=segment.nan_frac.get)
        return (
            f"{worst} missing {segment.nan_frac[worst]:.1%} "
            f"> NAN_MAX_FRAC ({NAN_MAX_FRAC:.0%})"
        )
    if segment.worst_nan_gap > NAN_MAX_GAP:
        worst = max(segment.nan_max_gap, key=segment.nan_max_gap.get)
        return (
            f"{worst} has a {segment.nan_max_gap[worst]}-sample gap "
            f"> NAN_MAX_GAP ({NAN_MAX_GAP})"
        )
    return None


def interpolate_short_gaps(frame: pd.DataFrame, max_gap: int) -> pd.DataFrame:
    """Linearly fill interior NaN runs of at most ``max_gap`` samples.

    Longer runs are left as NaN -- pandas' own ``limit`` would fill the first
    ``max_gap`` samples of a long gap and leave a discontinuity behind.
    """
    if max_gap <= 0:
        return frame

    out = frame.copy()
    for col in SIGNAL_COLS:
        mask = out[col].isna().to_numpy()
        if not mask.any():
            continue
        filled = out[col].interpolate(method="linear", limit_area="inside")
        keep_nan = np.zeros(len(out), dtype=bool)
        for a, b in runs_of_true(mask):
            if b - a + 1 > max_gap:
                keep_nan[a : b + 1] = True
        filled = filled.to_numpy()
        filled[keep_nan] = np.nan
        out[col] = filled
    return out


# --------------------------------------------------------------------------
# Per-reactor processing
# --------------------------------------------------------------------------
def process_reactor(path: str) -> tuple[dict, list[Segment]]:
    filename = os.path.basename(path)
    reactor = filename.replace("chemical_process_timeseries_", "").replace(".csv", "")

    frame = pd.read_csv(path, usecols=READ_COLS)[READ_COLS]

    minute = frame[TIME_COL].to_numpy()
    if len(minute) > 1 and not np.all(np.diff(minute) == 1):
        raise ValueError(
            f"{filename}: {TIME_COL} is not a gap-free 1-minute grid; "
            "segment indices would not map to row positions"
        )

    segments = fault_free_segments(reactor, frame[FAULT_COL].to_numpy())
    for seg in segments:
        score_missing(frame, seg)

    # Longest first, then take the first candidate that passes the checks.
    ranked = sorted(segments, key=lambda s: s.length, reverse=True)
    chosen = None
    for seg in ranked:
        reason = accept(seg)
        if reason is None:
            chosen = seg
            break
        seg.rejected = reason

    if chosen is None:
        print(f"  !! {reactor}: no segment passed the checks -- nothing exported")
        for seg in ranked[:3]:
            print(f"     rejected [{seg.start}, {seg.end}] len={seg.length}: {seg.rejected}")
        return (
            {
                "reactor": reactor,
                "source_file": filename,
                "exported": False,
                "n_fault_episodes": len(segments) and len(segments) - 1,
                "reason": ranked[0].rejected if ranked else "no fault-free segment",
            },
            segments,
        )

    block = frame.iloc[chosen.start : chosen.end + 1]
    block = block[[TIME_COL] + SIGNAL_COLS].reset_index(drop=True)
    block = interpolate_short_gaps(block, INTERPOLATE_MAX_GAP)

    os.makedirs(EXPORT_DIR, exist_ok=True)
    out_path = os.path.join(EXPORT_DIR, filename)
    block.to_csv(out_path, index=False)

    remaining = {c: float(block[c].isna().mean()) for c in SIGNAL_COLS}
    worst_col = max(remaining, key=remaining.get)

    print(
        f"  {reactor}: [{chosen.start}, {chosen.end}] "
        f"len={chosen.length} min ({chosen.length / 1440:.1f} d)  "
        f"{chosen.left_boundary} -> {chosen.right_boundary}  "
        f"worst NaN {worst_col} {remaining[worst_col]:.2%}, "
        f"max gap {chosen.worst_nan_gap}"
    )

    record = {
        "reactor": reactor,
        "source_file": filename,
        "export_file": os.path.relpath(out_path, DATASET_ROOT).replace("\\", "/"),
        "exported": True,
        "n_segments": len(segments),
        "segment_rank_by_length": 1 + ranked.index(chosen),
        "minute_start": int(block[TIME_COL].iloc[0]),
        "minute_end": int(block[TIME_COL].iloc[-1]),
        "row_start": chosen.start,
        "row_end": chosen.end,
        "n_samples": chosen.length,
        "duration_days": round(chosen.length / 1440, 2),
        "left_boundary": chosen.left_boundary,
        "right_boundary": chosen.right_boundary,
        "guard_min": GUARD_MIN,
        "interpolate_max_gap": INTERPOLATE_MAX_GAP,
        "nan_frac_after_fill": {c: round(v, 5) for c, v in remaining.items()},
        "nan_max_gap": dict(chosen.nan_max_gap),
    }
    return record, segments


def main() -> None:
    validate_control_roles()

    sources = sorted(glob.glob(os.path.join(SOURCE_DIR, SOURCE_GLOB)))
    if not sources:
        raise SystemExit(f"No per-reactor files matched {SOURCE_GLOB!r} in {SOURCE_DIR}")

    print(f"Source : {SOURCE_DIR}")
    print(f"Export : {EXPORT_DIR}")
    print(
        f"Params : guard={GUARD_MIN} min, min_len={MIN_SEGMENT_MIN} min, "
        f"nan_max_frac={NAN_MAX_FRAC}, nan_max_gap={NAN_MAX_GAP}, "
        f"interpolate_max_gap={INTERPOLATE_MAX_GAP}"
    )
    print(
        f"Plant   : {len(PLANT_SIGNAL_COLS)} signal + "
        f"{len(PLANT_OBSERVED_COLS)} observed columns, Ts = {TS_SECONDS} s"
    )
    print(
        "Control : "
        + ", ".join(f"{len(v)} {k}" for k, v in CONTROL_ROLES.items())
    )
    print()

    records, catalogue = [], []
    for path in sources:
        record, segments = process_reactor(path)
        records.append(record)
        for seg in segments:
            catalogue.append(
                {
                    "reactor": seg.reactor,
                    "row_start": seg.start,
                    "row_end": seg.end,
                    "n_samples": seg.length,
                    "duration_days": round(seg.length / 1440, 2),
                    "left_boundary": seg.left_boundary,
                    "right_boundary": seg.right_boundary,
                    "worst_nan_frac": round(seg.worst_nan_frac, 5),
                    "worst_nan_gap": seg.worst_nan_gap,
                    "selected": bool(
                        record.get("exported")
                        and seg.start == record["row_start"]
                        and seg.end == record["row_end"]
                    ),
                    "rejected": seg.rejected or "",
                }
            )

    os.makedirs(EXPORT_DIR, exist_ok=True)

    seg_path = os.path.join(EXPORT_DIR, "segments.csv")
    pd.DataFrame(catalogue).sort_values(
        ["reactor", "row_start"]
    ).to_csv(seg_path, index=False)

    manifest = {
        "source_dir": os.path.relpath(SOURCE_DIR, DATASET_ROOT).replace("\\", "/"),
        "ts_seconds": TS_SECONDS,
        "time_col": TIME_COL,
        "plant_signal_cols": PLANT_SIGNAL_COLS,
        "plant_observed_cols": PLANT_OBSERVED_COLS,
        "control_roles": CONTROL_ROLES,
        "params": {
            "guard_min": GUARD_MIN,
            "min_segment_min": MIN_SEGMENT_MIN,
            "nan_max_frac": NAN_MAX_FRAC,
            "nan_max_gap": NAN_MAX_GAP,
            "interpolate_max_gap": INTERPOLATE_MAX_GAP,
        },
        "reactors": records,
    }
    man_path = os.path.join(EXPORT_DIR, "manifest.json")
    with open(man_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    exported = [r for r in records if r.get("exported")]
    total = sum(r["n_samples"] for r in exported)
    print()
    print(
        f"Exported {len(exported)}/{len(records)} reactors, "
        f"{total:,} samples ({total / 1440:.1f} reactor-days) of fault-free data"
    )
    print(f"Catalogue: {os.path.basename(seg_path)}   Manifest: {os.path.basename(man_path)}")


if __name__ == "__main__":
    main()
