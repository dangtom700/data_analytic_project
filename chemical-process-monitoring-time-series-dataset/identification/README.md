# Two-zone state-space identification — MATLAB vs Controller-Toolbox

Identifies one linearised discrete state-space model per operating zone (A, B) from the
cleaned per-reactor records, twice: once with the MATLAB System Identification Toolbox
(`n4sid`) and once with Controller-Toolbox (`ctrl.n4sid`), then compares them.

`Ts = 60 s`. Inputs `coolant_flow_rate, feed_flow_rate, agitator_speed_rpm,
ambient_temp_effect` → outputs `reactor_temp, reactor_pressure`.

---

## Read this before interpreting any model these scripts produce

The dataset contains **no process dynamics**, and the two zones differ only by
offset, not by gain. Measured on the longest contiguous fault-free runs, full records:

| Evidence | Measurement |
|---|---|
| Autocorrelation, every process column | white beyond lag 1 (lag-2 ACF 0.00–0.10). Only `ambient_temp_effect` is smooth (ACF 0.93 at 1 day) — and it is exogenous |
| Cross-correlation input→output | peaks at **lag 0** and is **symmetric** in lag. A causal dynamic system is asymmetric with the peak at positive lag |
| ARX vs static regression, 70/30 holdout | static R² 0.060 → ARX R² 0.068. Identified pole **0.06**, i.e. τ ≈ 21 s at `Ts = 60 s`: shorter than one sample, so no memory |
| Singular-value spectrum | **no knee.** Largest ratio in the first 10 is 1.15 (A) / 1.09 (B); `sv[10]/sv[0] ≈ 0.72`. A true order-2 system gives `sv[2]/sv[0] ≈ 0.01` |
| Free-run fit, bias removed | `reactor_temp` 2–5%, `reactor_pressure` ≈ **0%** |
| Static gains, zone A vs zone B | `d(temp)/d(coolant)` −0.03491 vs −0.03486; `d(temp)/d(ambient)` +0.03086 vs +0.03089 — identical to 4 s.f. |

Two consequences:

- **`reactor_pressure` is unmodellable from these columns.** A static map explains 0.08%
  of its variance and ARX 0.4%; it is noise around a constant. Note also that the
  recorded `pressure_setpoint` (A 12.0 / B 13.5) is nowhere near the measured pressure
  (A 15.68 / B 17.57), so it is not a regulated variable in this data either.
- **Two *linearisations* of a nonlinear plant would differ in gain.** These differ only
  in offset, which means the generator was one static linear equation evaluated at two
  bias levels. The data supports one static map, not two state-space models.

This is consistent with what the dataset is for: it is a fault-**monitoring**
classification set, generated with plausible marginal distributions and static
correlations. Dynamics were never part of its construction.

**So read the output of these scripts as a measurement of the dataset, not of either
tool.** The useful result is that two independent `n4sid` implementations agree — which
validates Controller-Toolbox against MATLAB — while both report no identifiable system.

### What the dataset does legitimately support

Two clean, well-separated operating points; per-zone static gains; residual σ for EKF
covariances (`reactor_temp` 0.49 / 0.59, `reactor_pressure` 0.099 / 0.119); a realistic
6% dropout pattern; and the fault signatures.

### Consequence for the EKF → MPC → PI chain

The project's decision "identify the closed inner loop by PRBS-stepping the temperature
setpoint" is **not executable on this data**: `temp_setpoint` and `pressure_setpoint` are
regime constants, so there is zero setpoint excitation to identify an SP→PV response
from. A closed-loop plant model for the MPC needs either a simulated plant or a logged
experiment in which the setpoint actually moved.

---

## How to run

Order matters: the prep step writes the matrices both identification scripts read.

```bash
# 1. shared preparation (already run; re-run to change --max-samples)
conda run -n data_science python prepare_id_data.py

# 2. either order
matlab -batch "addpath('.'); identify_matlab"
conda run -n data_science python identify_ctrl_toolbox.py

# 3. compare (works with whichever result files exist)
conda run -n data_science python compare_models.py
```

`identify_ctrl_toolbox.py` locates `ctrl_toolbox*.pyd` by walking up from its own
directory and putting that folder on `sys.path`, so it runs from this subfolder without
needing `ctrl_bridge.py`.

### Files

| File | Role |
|---|---|
| `prepare_id_data.py` | picks the longest contiguous fault-free run per reactor, interpolates dropouts, converts to deviation variables, writes `id_data/` + `prep_manifest.json` |
| `identify_matlab.m` | MATLAB `n4sid` per zone, MOESP weighting → `results_matlab.json` |
| `identify_ctrl_toolbox.py` | `ctrl.n4sid` per zone → `results_ctrl_toolbox.json` |
| `compare_models.py` | diffs the two on realisation invariants → `COMPARISON.md` |
| `id_data/` | the exact matrices both tools consume |

---

## Design decisions

**One shared prep step.** Both tools read byte-identical CSVs, so any difference in the
results is attributable to the algorithms rather than to preprocessing.

**Deviation variables.** A model identified from absolute data would spend its dynamics
on the ~181 °C DC offset. Every record is mean-centred on the *identification* record's
means, which are the linearisation point, recorded in the manifest. The same offsets are
applied to the held-out records so all records share one origin.

**Held out by reactor, never randomly.** Each zone identifies on its longest-run reactor
and validates on the other two, honouring the project rule to split by reactor /
operating point.

**Bias-removed metrics reported alongside raw.** Reactors within a zone sit at slightly
different absolute levels (zone A: 182.3 / 181.2 / 180.1 °C). Against a shared origin
that leaves a constant bias on held-out reactors, so the raw holdout fit would blame the
dynamics for an offset error. The bias-removed variant allows one free DC term per
record and isolates the gain/dynamic fit. Both are in the JSON.

**MOESP on both sides.** `ctrl.n4sid` defaults to MOESP weighting, so the MATLAB call
sets `n4sidOptions('N4Weight','MOESP')`. Without this the two tools solve differently
weighted problems and the comparison means much less.

**Comparison on invariants, not on A/B/C/D.** Subspace identification returns an
arbitrary state basis: two tools can identify the same system and return matrices
related by a similarity transform `(T⁻¹AT, T⁻¹B, CT, D)`. The comparison therefore uses
eigenvalues, DC gain `C(I−A)⁻¹B+D`, step response, and held-out fit — all invariant
under `T`. (Verified: pushing a model through a random similarity transform leaves every
reported difference at 0.0.)

**Free-run simulation with `x0 = 0` as the primary metric.** Computed by an explicit
loop on both sides rather than `compare()`/`sim()`, so the definition is provably
identical. Free-run uses only the inputs, so unlike one-step prediction it cannot flatter
a model by feeding it the measured output.

---

## Things that will bite

- **Orientation.** `ctrl.n4sid` wants `Y` as `(p × N)` — channels in rows, time in
  columns. MATLAB's `iddata` wants the transpose. Neither raises on the wrong one; you
  silently identify a model of the wrong thing. Both scripts assert their shapes.
- **`suggest_order(max_order=-1)` returns 20 on this data.** Its max-consecutive-ratio
  heuristic latches onto the numerical tail of the spectrum, where neighbouring singular
  values are both tiny and their ratio means nothing. Always pass a real `max_order` on
  noise-dominated data. Both the guarded and unguarded values are recorded.
- **Order ≥ 3 may blow up.** In a NumPy reference check, orders ≥ 3 produced enormous
  `B`/`D` and free-run fits of −10⁶%, because with no deterministic subspace the
  least-squares step is ill-conditioned. If `ctrl.n4sid` does the same, that is the
  dataset, not a bug — but compare against the MATLAB column before concluding either
  way.
- **`--max-samples` defaults to 20000**, truncated contiguously from the start of the
  run (never decimated, which would change `Ts`). `n4sid` builds Hankel blocks of
  `(i_horizon·(p+m)) × (N − 2·i_horizon + 1)`; the full 75k-sample run is needlessly
  heavy for a model this small. Both tools must use the same value — which they do,
  because they read the same prepared files.

## Run results (2026-10-13)

Both tools have now been run for real. Everything executed; `COMPARISON.md` is the
generated output.

**The dataset verdict held.** Best free-run fit on `reactor_temp` was 2.10% (zone A)
and 1.96% (zone B); `reactor_pressure` came in at 0.0x% everywhere; no knee in either
zone. Nothing identifiable, as measured.

**The toolbox validated against MATLAB.** This is the result worth keeping:

| Check | Zone A | Zone B |
|---|---|---|
| Singular-value spectrum, largest ratio in first 10 | 1.146 (ctrl) vs 1.147 (MATLAB) | 1.088 vs 1.088 |
| `sv[10]/sv[0]` | 0.727 vs 0.726 | 0.712 vs 0.712 |
| max abs eigenvalue difference, order 1 | 1.4e-03 | 6.2e-03 |

Two independent MOESP implementations — Controller-Toolbox's `SubspaceID` and the
hand-rolled projection in `localSingularValues` — reproduce the same spectrum to three
decimals, and agree on the poles to ~1e-3 at low order. On a dataset with no
deterministic subspace that agreement is not forced by the data, so it is real evidence
that `SubspaceID` is correct.

### Two bugs found and fixed by the run

**1. `n4sid` must be told to estimate `D`.** MATLAB's `max|B|` reached 1e6–1.5e7 at
order ≥ 5 and its free-run fit collapsed to −4e6%, while Controller-Toolbox stayed at
~2% with `max|B| ≈ 0.005`. Cause: `n4sid` defaults to **`D = 0`** (no feedthrough),
and MATLAB's `D` was exactly zero at every order while `ctrl_toolbox`'s was 0.013–0.033.
In this dataset the whole input→output relationship is *instantaneous* — the
cross-correlation peaks at lag 0 — so all of it belongs in `D`. Forbidden from using
`D`, `n4sid` has to fake an instantaneous response through `C(zI−A)⁻¹B`, which needs an
enormous `B` and is numerically hopeless in free-run. Fixed by passing
`'Feedthrough', true(1,nu)`. Controller-Toolbox was never affected because it estimates
`D` unconditionally — **a real robustness advantage on feedthrough-dominated data**.

The DC-gain differences in the first run (10–70%) are contaminated by the same cause:
with `D` pinned at 0, MATLAB's entire steady-state gain had to come from
`C(I−A)⁻¹B`. Expect these to drop sharply on the re-run.

**2. The step-response comparison silently reported `n/a`.** MATLAB writes the
`step_response_60` keys as `u0..u3` (struct fields cannot begin with a digit) and NumPy
writes `0..3`; `compare_models.py` required the same key in *both* dicts, so no row ever
matched. Now resolved per side independently.

### Order sweep capped at 4

Both scripts now default to orders `[1 2 3 4]`. Evidence from the first run:

| order | rho(A) zone A | rho(A) zone B | bias-rm holdout fit, zone A |
|---|---|---|---|
| 1 | 0.0786 | 0.8100 | 3.80% |
| 2 | 0.3775 | 0.7765 | 3.80% |
| 3 | 0.6277 | 0.9711 | 3.79% |
| 4 | 0.7844 | 0.9430 | 3.79% |
| 5 | 0.9108 | 0.9842 | 3.79% |
| 6 | 0.9141 | **0.9975** | 3.75% |
| 8 | 0.9614 | 0.9507 | 3.70% |

Past order 4 the poles crowd the unit circle, which is where free-run simulation turns
numerically sensitive and where MATLAB's `max|B|` reached 1e6–1.5e7. Holdout fit never
improves with added states, so nothing is lost by capping. Pass `--orders` / `'orders'`
to override.

### Re-run needed

```bash
conda run -n data_science python identify_ctrl_toolbox.py
matlab -batch "addpath('.'); identify_matlab"
conda run -n data_science python compare_models.py
```

Re-run both identification scripts rather than just MATLAB, so the two JSONs cover the
same order set and the comparison table has no half-empty rows. (The existing
Controller-Toolbox numbers at orders 1–4 are already correct — this is only for a clean
table.)

Expected after the fix: MATLAB's order ≥ 5 blow-up disappears, its `D` becomes non-zero
and close to Controller-Toolbox's, its ident fit rises to ~2% matching, and the DC-gain
and step-response differences fall by an order of magnitude or more. The dataset verdict
will not change — there is still nothing to identify.
