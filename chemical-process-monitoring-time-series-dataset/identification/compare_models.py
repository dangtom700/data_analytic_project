#!/usr/bin/env python3
"""
Compare the MATLAB and Controller-Toolbox identification results per operating zone.

    python compare_models.py                 # writes COMPARISON.md

Why not compare A, B, C, D directly
-----------------------------------
A subspace identifier returns an arbitrary state-space BASIS. Two tools can identify
the identical system and return completely different A/B/C/D related by a similarity
transform T: (T^-1 A T, T^-1 B, C T, D). Comparing the matrices elementwise would
report a disagreement that is not there. Everything below is invariant under that
transform:

    eigenvalues of A      -- the poles: where the dynamics actually are
    DC gain C(I-A)^-1B+D  -- the steady-state input/output map
    step response         -- the full transient, basis-free
    fit on held-out data  -- the only thing that matters operationally

Runs with whichever result files exist, so it is useful before the MATLAB side
has been run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def arr(x, two_d=False):
    """MATLAB's jsonencode collapses 1x1 to a scalar and Nx1 to a flat list;
    NumPy's tolist() does not. Normalise both to the same shape."""
    if x is None:
        return None
    a = np.atleast_2d(np.asarray(x, dtype=float)) if two_d else np.atleast_1d(
        np.asarray(x, dtype=float))
    return a


def load(p: Path):
    if not p.exists():
        return None
    return json.loads(p.read_text())


def eig_sorted(m):
    re, im = arr(m.get("eig_real")), arr(m.get("eig_imag"))
    if re is None:
        return None
    if im is None or im.size != re.size:
        im = np.zeros_like(re)
    ev = re + 1j * im
    return ev[np.lexsort((ev.real, -np.abs(ev)))]


def rel(a, b):
    """Relative difference with a sane denominator."""
    den = max(np.max(np.abs(a)), np.max(np.abs(b)), 1e-30)
    return float(np.max(np.abs(a - b)) / den)


def fmt_fit(entry, ycols, key="fit_ident"):
    s = entry.get(key)
    if s is None:
        return "n/a"
    if isinstance(s, dict):                      # MATLAB single-output edge case
        s = [s]
    return "  ".join(f"{c}={s[i].get('fit_pct', float('nan')):7.2f}%"
                     for i, c in enumerate(ycols) if i < len(s))


def main() -> None:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--ctrl", type=Path, default=here / "results_ctrl_toolbox.json")
    ap.add_argument("--matlab", type=Path, default=here / "results_matlab.json")
    ap.add_argument("--out", type=Path, default=here / "COMPARISON.md")
    args = ap.parse_args()

    R = {"ctrl_toolbox": load(args.ctrl), "matlab": load(args.matlab)}
    have = [k for k, v in R.items() if v]
    if not have:
        raise SystemExit(f"no result files found ({args.ctrl.name}, {args.matlab.name})")

    L: list[str] = ["# Two-zone identification: MATLAB vs Controller-Toolbox", ""]
    L.append(f"Result files present: {', '.join(have)}")
    missing = [k for k in R if not R[k]]
    if missing:
        L.append(f"\n> Missing: {', '.join(missing)}. "
                 "Sections needing both tools are omitted.")

    ref = R[have[0]]
    ycols, ucols = ref["y_cols"], ref["u_cols"]
    L += ["", f"- Sample time `Ts = {ref['Ts']} s`",
          f"- Inputs `{ucols}`", f"- Outputs `{ycols}`", ""]

    for z in sorted(ref["zones"]):
        L += [f"## Zone {z}", ""]
        op = ref["zones"][z].get("operating_point", {})
        if op:
            L.append("Linearisation point: " +
                     ", ".join(f"`{k}={float(v):.4f}`" for k, v in op.items()))
        L.append(f"\nIdentification record: `{ref['zones'][z].get('ident_tag')}`\n")

        # ---- order selection evidence ----
        L += ["### Order selection", ""]
        for tool in have:
            zz = R[tool]["zones"].get(z, {})
            d = zz.get("sv_diagnostics")
            if not d:
                L.append(f"- **{tool}**: no singular-value spectrum recorded")
                continue
            L.append(
                f"- **{tool}**: largest sv ratio within first {d.get('candidate_limit')} "
                f"= **{d.get('max_ratio'):.3f}** at order {d.get('argmax_ratio_order')}; "
                f"`sv[10]/sv[0] = {d.get('decay_first_to_tenth'):.3f}`; "
                f"knee_present = **{d.get('knee_present')}**")
            if d.get("max_ratio_unrestricted") is not None:
                L.append(f"  - unrestricted max-ratio search returns order "
                         f"{d.get('argmax_ratio_unrestricted')} "
                         f"(ratio {d.get('max_ratio_unrestricted'):.3f}) -- the "
                         "spectrum's numerical tail, not a real knee")
            if zz.get("suggested_order_unguarded") is not None:
                L.append(f"  - `suggest_order(max_order=-1)` -> "
                         f"**{zz['suggested_order_unguarded']}**, capped -> "
                         f"{zz.get('suggested_order')}")
        L.append("")

        # ---- per-order side by side ----
        orders = sorted(
            {k for t in have for k in R[t]["zones"].get(z, {}).get("models", {})},
            key=lambda s: int(s.split("_")[1]))

        L += ["### Fit per order (free-run simulation, x0 = 0)", "",
              "| order | tool | rho(A) | " +
              " | ".join(f"ident {c}" for c in ycols) +
              " | " + " | ".join(f"holdout {c} (bias-rm)" for c in ycols) + " |",
              "|---|---|---|" + "---|" * (2 * len(ycols))]
        for okey in orders:
            for tool in have:
                m = R[tool]["zones"].get(z, {}).get("models", {}).get(okey)
                if not m:
                    continue
                if not m.get("success", False):
                    L.append(f"| {okey.split('_')[1]} | {tool} | FAILED | " +
                             " | ".join(["--"] * 2 * len(ycols)) + " |")
                    continue
                fi = m.get("fit_ident", [])
                if isinstance(fi, dict):
                    fi = [fi]
                cells = [f"{fi[i].get('fit_pct', float('nan')):.2f}%"
                         if i < len(fi) else "--" for i in range(len(ycols))]
                fv = m.get("fit_val", {}) or {}
                hold = []
                for i in range(len(ycols)):
                    vals, braw = [], []
                    for tag, sc in fv.items():
                        if isinstance(sc, dict):
                            sc = [sc]
                        if i < len(sc):
                            braw.append(sc[i].get("fit_pct", np.nan))
                            vals.append(sc[i].get("fit_pct_bias_removed", np.nan))
                    hold.append(f"{np.nanmean(braw):.1f}% ({np.nanmean(vals):.2f}%)"
                                if vals else "--")
                L.append(f"| {okey.split('_')[1]} | {tool} | "
                         f"{m.get('spectral_radius', float('nan')):.4f} | " +
                         " | ".join(cells) + " | " + " | ".join(hold) + " |")
        L.append("")
        L.append("Holdout columns are averaged over the two held-out reactors; "
                 "the parenthesised value removes a constant per-record offset, "
                 "separating gain/dynamic error from operating-point bias.")
        L.append("")

        # ---- invariant agreement, only where both tools ran ----
        if len(have) == 2:
            L += ["### Do the two tools agree?", "",
                  "| order | max abs(d(eig)) | DC-gain rel. diff | step-resp rel. diff |",
                  "|---|---|---|---|"]
            for okey in orders:
                a = R["matlab"]["zones"].get(z, {}).get("models", {}).get(okey)
                b = R["ctrl_toolbox"]["zones"].get(z, {}).get("models", {}).get(okey)
                if not (a and b and a.get("success") and b.get("success")):
                    continue
                ea, eb = eig_sorted(a), eig_sorted(b)
                de = (f"{np.max(np.abs(ea - eb)):.3e}"
                      if ea is not None and eb is not None and ea.size == eb.size
                      else "size mismatch")
                da, db = arr(a.get("dc_gain"), True), arr(b.get("dc_gain"), True)
                dg = f"{rel(da, db):.3e}" if da is not None and db is not None \
                     and da.shape == db.shape else "n/a"
                sa, sb = a.get("step_response_60"), b.get("step_response_60")
                if sa and sb:
                    # The two tools key this dict differently -- MATLAB writes
                    # 'u0'..'u3' (struct fields cannot start with a digit), NumPy
                    # writes '0'..'3'. Resolve each side independently; requiring
                    # the same key in both silently yields n/a for every row.
                    def pick(d, j):
                        for k in (f"u{j}", str(j), f"u{j + 1}", str(j + 1)):
                            if k in d:
                                return arr(d[k], True)
                        return None
                    diffs = []
                    for j in range(len(ucols)):
                        xa, xb = pick(sa, j), pick(sb, j)
                        if xa is not None and xb is not None and xa.shape == xb.shape:
                            diffs.append(rel(xa, xb))
                    sr = f"{max(diffs):.3e}" if diffs else "n/a"
                else:
                    sr = "n/a"
                L.append(f"| {okey.split('_')[1]} | {de} | {dg} | {sr} |")
            L += ["", "Agreement here means both implementations extracted the same "
                      "system. Disagreement on a dataset with no deterministic "
                      "subspace is expected: each tool is fitting its own noise "
                      "direction, so the invariants are not pinned down by the data.", ""]

    # ---- verdict ----
    L += ["## Verdict", ""]
    for z in sorted(ref["zones"]):
        zz = ref["zones"][z]
        d = zz.get("sv_diagnostics") or {}
        best, bkey = None, None
        for okey, m in (zz.get("models") or {}).items():
            if not m.get("success"):
                continue
            fi = m.get("fit_ident", [])
            if isinstance(fi, dict):
                fi = [fi]
            if fi and (best is None or fi[0].get("fit_pct", -1e9) > best):
                best, bkey = fi[0].get("fit_pct"), okey
        L.append(f"- **Zone {z}**: knee_present = `{d.get('knee_present')}`; "
                 f"best ident free-run fit on `{ycols[0]}` = "
                 f"**{best:.2f}%** at {bkey}" if best is not None else
                 f"- **Zone {z}**: no successful model")
    L += ["", "A knee-free singular-value spectrum plus a single-digit free-run fit "
              "means the records contain no deterministic subspace to identify: the "
              "returned A/B/C/D are a fit to noise, and the poles land near the "
              "origin (no memory at Ts = 60 s). Read the numbers above as a "
              "measurement of the dataset, not of either tool.", ""]

    args.out.write_text("\n".join(L))
    print("\n".join(L))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
