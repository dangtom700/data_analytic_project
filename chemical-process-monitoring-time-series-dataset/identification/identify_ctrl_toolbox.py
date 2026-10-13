#!/usr/bin/env python3
"""
Two-zone subspace state-space identification via Controller-Toolbox (ctrl_toolbox).

Counterpart to identify_matlab.m. Both read the SAME matrices written by
prepare_id_data.py and write results in the SAME JSON schema, so compare_models.py
can diff them on realisation-invariant quantities.

Run AFTER prepare_id_data.py, from the data_science env:

    conda run -n data_science python identify_ctrl_toolbox.py

Orientation trap
----------------
ctrl.n4sid wants Y as (p x N) and U as (m x N) -- channels in ROWS, time in COLUMNS.
MATLAB's iddata wants the transpose (time down rows). Passing the wrong one does not
raise; it silently identifies a model of the wrong thing. Shapes are asserted below.

Metric conventions (must stay identical to identify_matlab.m)
-------------------------------------------------------------
fit_pct = 100 * (1 - ||y - yhat|| / ||y - mean(y)||)    <- MATLAB `compare` convention
r2      = 1 - SSE/SST
Primary metric is FREE-RUN simulation (x[k+1]=Ax+Bu, y=Cx+Du, x0 = 0) on data the
model never saw. Data is mean-centred, so x0 = 0 is the correct origin and removes
any x0-estimation difference between the two tools. One-step prediction via the
Kalman gain is reported separately and is NOT directly comparable to free-run.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------------------------------
# import ctrl_toolbox
# --------------------------------------------------------------------------
def import_ctrl_toolbox():
    """`pip install --target .` put the .pyd in the data_analytic_project root, so
    `import ctrl_toolbox` only resolves when that root is on sys.path. Walk up and
    add whichever ancestor actually holds the module."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if list(parent.glob("ctrl_toolbox*.pyd")) or list(parent.glob("ctrl_toolbox*.so")):
            sys.path.insert(0, str(parent))
            break
    try:
        import ctrl_toolbox as ctrl
    except ImportError as exc:
        raise SystemExit(
            f"cannot import ctrl_toolbox: {exc}\n"
            "Checked these folders for ctrl_toolbox*.pyd:\n  "
            + "\n  ".join(str(p) for p in here.parents)
            + "\nRun from the project root, or reinstall the bindings."
        ) from exc

    if not hasattr(ctrl, "n4sid"):
        raise SystemExit(
            "ctrl_toolbox imported but has no n4sid -- this build was configured with\n"
            "CTRL_ENABLE_SUBSPACE=OFF, so CTRL_HAS_SUBSPACE is undefined and the\n"
            "SubspaceID bindings were compiled out. Rebuild with -DCTRL_ENABLE_SUBSPACE=ON."
        )
    return ctrl


# --------------------------------------------------------------------------
# metrics -- keep byte-identical in meaning to the MATLAB side
# --------------------------------------------------------------------------
def simulate(A, B, C, D, U):
    """Free-run simulation. U is (m x N); returns Yhat (p x N). x0 = 0."""
    n, N = A.shape[0], U.shape[1]
    x = np.zeros(n)
    Yh = np.empty((C.shape[0], N))
    for k in range(N):
        Yh[:, k] = C @ x + D @ U[:, k]
        x = A @ x + B @ U[:, k]
    return Yh


def score(Y, Yh):
    """Per-output-channel fit, reported two ways.

    Each reactor in a zone sits at a slightly different absolute operating point
    (zone A: 182.3 / 181.2 / 180.1 degC). Every record is centred on the IDENT
    record's means, which is correct for a single per-zone model but leaves a
    constant bias on the held-out reactors. Reporting only the raw number would
    blame the dynamics for what is actually an offset, so a bias-removed variant
    (one free DC term per record) is reported alongside it:

        raw           -- model must also get the absolute level right
        bias_removed  -- isolates the dynamic/gain fit
    """
    out = []
    for i in range(Y.shape[0]):
        y, yh = Y[i], Yh[i]
        offset = float((y - yh).mean())
        rec = {"offset": offset}
        for label, pred in (("", yh), ("_bias_removed", yh + offset)):
            sse = float(np.sum((y - pred) ** 2))
            sst = float(np.sum((y - y.mean()) ** 2))
            rec["fit_pct" + label] = 100.0 * (
                1.0 - np.linalg.norm(y - pred) / np.linalg.norm(y - y.mean()))
            rec["r2" + label] = 1.0 - sse / sst
            rec["rmse" + label] = float(np.sqrt(sse / len(y)))
        out.append(rec)
    return out


def sv_diagnostics(sv, max_candidate=10, knee_threshold=3.0):
    """Order selection is only meaningful if the singular-value spectrum has a knee.
    For a true order-n system sv(n)/sv(n+1) is large; a smooth decay means the data
    has no deterministic subspace and any 'order' is a fit to noise.

    The ratio search is restricted to the first `max_candidate` positions on purpose.
    The tail of the spectrum is a numerical floor where neighbouring values are both
    tiny, so their ratio can be large without meaning anything -- an unrestricted
    max-consecutive-ratio search (which is what ctrl.suggest_order does with
    max_order=-1) latches onto that tail and reports an absurd order. Always pass a
    real max_order to suggest_order on noise-dominated data."""
    sv = np.asarray(sv, dtype=float)
    sv = sv[sv > 0]
    if sv.size < 2:
        return {"max_ratio": None}
    ratios = sv[:-1] / sv[1:]
    lim = int(min(max_candidate, ratios.size))
    head = ratios[:lim]
    return {"max_ratio": float(head.max()),
            "argmax_ratio_order": int(head.argmax()) + 1,
            "max_ratio_unrestricted": float(ratios.max()),
            "argmax_ratio_unrestricted": int(ratios.argmax()) + 1,
            "candidate_limit": lim,
            "knee_threshold": knee_threshold,
            "sv_normalised": (sv / sv[0]).tolist(),
            "decay_first_to_tenth": float(sv[min(9, sv.size - 1)] / sv[0]),
            "knee_present": bool(head.max() > knee_threshold)}


def invariants(A, B, C, D):
    """Realisation-invariant descriptors. A/B/C/D themselves are basis-dependent and
    will NOT match between tools even for an identical system -- these will."""
    n = A.shape[0]
    ev = np.linalg.eigvals(A)
    order = np.argsort(-np.abs(ev))
    ev = ev[order]
    try:
        dc = C @ np.linalg.solve(np.eye(n) - A, B) + D
        dc_list = dc.tolist()
    except np.linalg.LinAlgError:
        dc_list = None
    # unit step on each input, 60 samples (= 1 hour at Ts=60 s)
    steps = {}
    for j in range(B.shape[1]):
        Uj = np.zeros((B.shape[1], 60))
        Uj[j, :] = 1.0
        steps[j] = simulate(A, B, C, D, Uj).tolist()
    return {
        "eig_real": ev.real.tolist(),
        "eig_imag": ev.imag.tolist(),
        "eig_abs": np.abs(ev).tolist(),
        "spectral_radius": float(np.max(np.abs(ev))),
        "dc_gain": dc_list,
        "step_response_60": steps,
    }


# --------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id-data", type=Path, default=Path(__file__).resolve().parent / "id_data")
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).resolve().parent / "results_ctrl_toolbox.json")
    ap.add_argument("--orders", type=int, nargs="+", default=[1, 2, 3, 4],
                    help="Capped at 4 deliberately. Measured on this data, rho(A) "
                         "crosses 0.9 at order 5 (zone A) and reaches 0.9975 by "
                         "order 6 (zone B): poles that close to the unit circle on a "
                         "noise-fitted model make free-run simulation numerically "
                         "sensitive, and MATLAB's max|B| hit 1e6-1.5e7 there. "
                         "Bias-removed holdout fit degrades monotonically with order "
                         "regardless, so the cap costs nothing.")
    ap.add_argument("--i-horizon", type=int, default=20,
                    help="block-row count. Held fixed across orders so the sweep is "
                         "comparable; must be >= n_order+1 and >= 2*n_order/p.")
    args = ap.parse_args()

    ctrl = import_ctrl_toolbox()
    print(f"ctrl_toolbox: {ctrl.__file__}")

    man = json.loads((args.id_data / "prep_manifest.json").read_text())
    Ts, ucols, ycols = man["Ts"], man["u_cols"], man["y_cols"]
    results = {"tool": "ctrl_toolbox", "module": str(ctrl.__file__), "Ts": Ts,
               "u_cols": ucols, "y_cols": ycols, "i_horizon": args.i_horizon, "zones": {}}

    for z, zinfo in man["zones"].items():
        print(f"\n================ zone {z} ================")

        def load(fname):
            df = pd.read_csv(args.id_data / fname)
            Y = np.ascontiguousarray(df[ycols].to_numpy().T)   # (p x N)
            U = np.ascontiguousarray(df[ucols].to_numpy().T)   # (m x N)
            assert Y.shape[0] == len(ycols) and U.shape[0] == len(ucols), "orientation"
            assert Y.shape[1] == U.shape[1]
            return Y, U

        Yi, Ui = load(zinfo["ident"]["file"])
        vals = [(v["tag"], *load(v["file"])) for v in zinfo["validation"]]
        print(f"ident {zinfo['ident']['tag']}: Y{Yi.shape} U{Ui.shape}   "
              f"val {[v[0] for v in vals]}")

        zres = {"ident_tag": zinfo["ident"]["tag"],
                "operating_point": zinfo["operating_point"], "models": {}}

        for n_order in args.orders:
            if args.i_horizon < n_order + 1:
                print(f"  order {n_order}: skipped (i_horizon {args.i_horizon} < n+1)")
                continue
            res = ctrl.n4sid(Y=Yi, U=Ui, n_order=n_order,
                             i_horizon=args.i_horizon, Ts=Ts)
            if not res.success:
                print(f"  order {n_order}: FAILED -- {res.message}")
                zres["models"][f"order_{n_order}"] = {"success": False,
                                                       "message": res.message}
                continue

            m = res.get_model()
            A = np.asarray(m.A); Bm = np.asarray(m.B)
            C = np.asarray(m.C); Dm = np.asarray(m.D)

            entry = {"success": True, "n_order": n_order,
                     "A": A.tolist(), "B": Bm.tolist(), "C": C.tolist(), "D": Dm.tolist(),
                     "Ts": float(m.Ts),
                     "singular_values": np.asarray(res.singular_values).ravel().tolist(),
                     "kalman_gain": np.asarray(res.kalman_gain).tolist(),
                     "innov_cov": np.asarray(res.innov_cov).tolist(),
                     **invariants(A, Bm, C, Dm)}

            entry["fit_ident"] = score(Yi, simulate(A, Bm, C, Dm, Ui))
            entry["fit_val"] = {tag: score(Yv, simulate(A, Bm, C, Dm, Uv))
                                for tag, Yv, Uv in vals}
            zres["models"][f"order_{n_order}"] = entry

            sr = entry["spectral_radius"]
            fi = "  ".join(f"{c}={entry['fit_ident'][i]['fit_pct']:7.2f}%"
                           for i, c in enumerate(ycols))
            print(f"  order {n_order}: rho(A)={sr:7.4f}   ident {fi}")
            for tag in entry["fit_val"]:
                fv = "  ".join(
                    f"{c}={entry['fit_val'][tag][i]['fit_pct']:8.2f}%"
                    f"(bias-rm {entry['fit_val'][tag][i]['fit_pct_bias_removed']:6.2f}%)"
                    for i, c in enumerate(ycols))
                print(f"            holdout {tag}: {fv}")

        # order the library itself suggests, from the singular-value spectrum
        first = next((v for v in zres["models"].values() if v.get("success")), None)
        if first:
            sv = np.asarray(first["singular_values"], dtype=float)
            # unguarded: what the library returns by default (max_order=-1)
            zres["suggested_order_unguarded"] = int(
                ctrl.suggest_order(sv=sv, threshold=0.01, max_order=-1))
            # guarded: capped at a physically plausible order
            zres["suggested_order"] = int(
                ctrl.suggest_order(sv=sv, threshold=0.01, max_order=max(args.orders)))
            zres["singular_values"] = sv.tolist()
            zres["sv_diagnostics"] = sv_diagnostics(sv)
            d = zres["sv_diagnostics"]
            print(f"  ctrl.suggest_order: max_order=-1 -> {zres['suggested_order_unguarded']}"
                  f"   capped -> {zres['suggested_order']}")
            print("  singular values: " +
                  "  ".join(f"{v:.4g}" for v in sv[:10]))
            print(f"  largest sv ratio (first {d['candidate_limit']}) = {d['max_ratio']:.3f} "
                  f"at order {d['argmax_ratio_order']}  ->  knee_present={d['knee_present']}")
            print(f"  sv[10]/sv[0] = {d['decay_first_to_tenth']:.3f}"
                  "   (a true order-n system drops sharply after n; smooth decay = noise)")

        results["zones"][z] = zres

    # Prove the real bindings agree with the NumPy simulation used for the sweep.
    # Nothing in this project had ever been executed against ctrl_toolbox before.
    chk = next(iter(results["zones"].values()))
    mdl = next(v for v in chk["models"].values() if v.get("success"))
    A = np.asarray(mdl["A"]); Bm = np.asarray(mdl["B"])
    C = np.asarray(mdl["C"]); Dm = np.asarray(mdl["D"])
    ss = ctrl.StateSpace(A=A, B=Bm, C=C, D=Dm, Ts=Ts)
    Utest = np.zeros((Bm.shape[1], 50)); Utest[0, :] = 1.0
    x = np.zeros(A.shape[0]); y_tb = []
    for k in range(50):
        y, x = ctrl.ss_step_copy(sys=ss, x=x, u=Utest[:, k])
        y_tb.append(np.asarray(y))
    delta = float(np.max(np.abs(np.array(y_tb).T - simulate(A, Bm, C, Dm, Utest))))
    results["binding_crosscheck_max_abs_diff"] = delta
    print(f"\nss_step_copy vs NumPy simulation: max |diff| = {delta:.3e}")

    args.out.write_text(json.dumps(results, indent=1))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
