#!/usr/bin/env python3
"""
Shared preparation step for the two-zone state-space identification.

Writes the exact matrices that BOTH identify_matlab.m and identify_ctrl_toolbox.py
consume, so any difference between the two results is attributable to the
identification algorithms and not to preprocessing.

Per operating zone (A, B):
  * one IDENT record  -- the reactor with the longest contiguous fault-free run
  * two VAL records   -- the remaining two reactors of that zone, held out entirely
    (honours the project rule: split by reactor / operating point, never randomly)

Deviation variables
-------------------
A state-space model identified from absolute data would spend its dynamics on the
~181 degC DC offset. Every record is therefore mean-centred using the IDENT record's
means, which ARE the linearisation point. The same offsets are applied to the VAL
records so all records share one coordinate system -- otherwise cross-reactor
validation silently compares different origins.

Usage
-----
    python prepare_id_data.py                       # defaults
    python prepare_id_data.py --max-samples 40000
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

# --- what the model is ------------------------------------------------------
U_COLS = ["coolant_flow_rate", "feed_flow_rate", "agitator_speed_rpm", "ambient_temp_effect"]
Y_COLS = ["reactor_temp", "reactor_pressure"]
TS = 60.0          # seconds. Data is 1-minute sampling; the library works in seconds.
ZONES = ("A", "B")
REACTORS = ("R1", "R2", "R3")


def longest_fault_free_run(fault: np.ndarray) -> tuple[int, int]:
    """Return [start, end) of the longest contiguous fault_type == 0 block.

    Filtering fault_type == 0 globally would remove ~3.6% of rows *in bursts*, and a
    subspace identifier reads every hole as a one-sample jump. The longest contiguous
    run is used instead.
    """
    ok = (fault == 0).astype(np.int8)
    edges = np.flatnonzero(np.diff(np.concatenate(([0], ok, [0]))) != 0)
    starts, ends = edges[0::2], edges[1::2]
    if starts.size == 0:
        raise ValueError("no fault-free samples at all")
    j = int(np.argmax(ends - starts))
    return int(starts[j]), int(ends[j])


def load_record(csv: Path) -> dict:
    df = pd.read_csv(csv)
    s, e = longest_fault_free_run(df["fault_type"].to_numpy())
    sub = df.iloc[s:e][U_COLS + Y_COLS].copy()

    # ~6% sensor dropouts, injected at random and not target-driven, so
    # interpolation is defensible. Count what was filled rather than hiding it.
    filled = {c: int(sub[c].isna().sum()) for c in sub.columns}
    sub = sub.interpolate(limit_direction="both")
    if sub.isna().any().any():
        raise ValueError(f"{csv.name}: NaNs survived interpolation")

    return {"source": csv.name, "run_start": s, "run_end": e,
            "n_rows": int(len(sub)), "nan_filled": filled, "frame": sub}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent.parent,
                    help="folder holding chemical_process_timeseries_<Z>_<R>.csv")
    ap.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent / "id_data")
    ap.add_argument("--max-samples", type=int, default=20000,
                    help="cap on IDENT length. n4sid builds Hankel blocks of "
                         "(i_horizon*(p+m)) x (N - 2*i_horizon + 1); the full 75k-sample "
                         "run is needlessly heavy for a model this small. Truncated "
                         "contiguously -- never decimated, which would change Ts.")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {"Ts": TS, "u_cols": U_COLS, "y_cols": Y_COLS,
                "max_samples": args.max_samples, "zones": {}}

    for z in ZONES:
        recs = []
        for r in REACTORS:
            csv = args.data_dir / "cleaning" / f"chemical_process_timeseries_{z}_{r}.csv"
            if not csv.exists():
                raise SystemExit(f"missing {csv}")
            rec = load_record(csv)
            rec["tag"] = f"{z}_{r}"
            recs.append(rec)

        recs.sort(key=lambda d: d["n_rows"], reverse=True)
        ident, vals = recs[0], recs[1:]

        ident_frame = ident["frame"].iloc[: args.max_samples]
        # The linearisation point: absolute operating conditions of the IDENT record.
        op = ident_frame.mean()

        def emit(frame: pd.DataFrame, path: Path) -> None:
            dev = frame - op                      # one shared coordinate system
            dev.to_csv(path, index=False, float_format="%.10g")

        ipath = args.out_dir / f"zone_{z}_ident.csv"
        emit(ident_frame, ipath)
        zinfo = {
            "ident": {"tag": ident["tag"], "file": ipath.name,
                      "n_samples": int(len(ident_frame)),
                      "available_in_run": ident["n_rows"],
                      "run_start": ident["run_start"], "run_end": ident["run_end"],
                      "nan_filled": ident["nan_filled"]},
            "operating_point": {k: float(v) for k, v in op.items()},
            "validation": [],
        }
        for v in vals:
            vpath = args.out_dir / f"zone_{z}_val_{v['tag']}.csv"
            emit(v["frame"], vpath)
            zinfo["validation"].append(
                {"tag": v["tag"], "file": vpath.name, "n_samples": v["n_rows"],
                 "run_start": v["run_start"], "run_end": v["run_end"],
                 "nan_filled": v["nan_filled"]})
        manifest["zones"][z] = zinfo

        print(f"zone {z}: ident={ident['tag']} "
              f"({len(ident_frame)} of {ident['n_rows']} samples)  "
              f"val={[v['tag'] for v in vals]}")
        print("   operating point: " + "  ".join(f"{k}={op[k]:.4f}" for k in Y_COLS + U_COLS))

    mpath = args.out_dir / "prep_manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2))
    print(f"\nwrote {mpath}")


if __name__ == "__main__":
    main()
