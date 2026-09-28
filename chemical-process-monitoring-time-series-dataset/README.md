# Chemical Process Monitoring — Time Series

A simulated continuous chemical reactor system: six reactors across two
operating regimes, minute-resolution sensors, gradual fault development and a
seasonal ambient effect. Supports fault classification, efficiency regression
and time-to-fault forecasting from the same table.

## At a glance

| | |
|---|---|
| **Source** | [kaggle.com/datasets/rohit8527kmr7518/chemical-process-monitoring-time-series-dataset](https://www.kaggle.com/datasets/rohit8527kmr7518/chemical-process-monitoring-time-series-dataset) |
| **Licence** | **CC0 (Public Domain)** — no restrictions, no attribution required |
| **Nature** | Fully synthetic, rule-based process simulation. No real plant data. |
| **Raw file** | `chemical_process_timeseries.csv` · 201 MB · LF endings |
| **Shape** | **777,600 rows × 21 columns** |
| **Structure** | 6 reactors (`A_R1`–`A_R3`, `B_R1`–`B_R3`) × 129,600 minutes each |
| **Sampling** | 1 minute |
| **Span** | 2024-01-01 00:00:00 → 2024-03-30 23:59:00 (**90 days**) |

Regimes are exactly balanced: 388,800 rows each, three reactors apiece.

### ⚠ The published description disagrees with the file

The Kaggle description states **~260,000 rows** over **~180 days**. The file
actually contains **777,600 rows** over **90 days**:

```
6 reactors × 129,600 minutes = 777,600 rows
129,600 minutes ÷ 1440       = 90 days per reactor
```

260,000 rows ≈ 180 days of a *single* minute-resolution series, so the
description appears to describe an earlier single-reactor version. **Trust the
file, not the description** — the figures in this README were all measured
directly.

## What the simulation models

**Two operating regimes** (`operating_regime`):

| Regime | Conditions | Reactors |
|---|---|---|
| **A — baseline** | Nominal temperature and pressure, efficient cooling, lower fault probability. Stable long-term operation. | `A_R1`, `A_R2`, `A_R3` |
| **B — stress** | Higher temperature and pressure, reduced cooling efficiency, more sensor noise, higher fault probability. Harsh / high-throughput operation. | `B_R1`, `B_R2`, `B_R3` |

**Multi-reactor setup** — reactors follow identical process logic with small
unit-specific differences. This is the interesting part of the dataset: it
supports cross-asset generalization, **leave-one-reactor-out validation** and
transfer learning between regimes.

**Seasonal ambient effect** — `ambient_temp_effect` is a slow sinusoid over
time, influencing cooling efficiency, temperature variability and pressure
stability. It makes the series deliberately non-stationary.

**Gradual faults** — faults develop progressively rather than instantaneously.
Sensor drift and variance rise before failure, and efficiency degrades on the
way in. Detection is therefore a genuine early-warning problem, not a
threshold check.

## Fault modes

| Code | Fault | Rows | Share |
|---|---|---|---|
| 0 | Normal operation | 749,699 | 96.412% |
| 1 | Cooling system degradation | 9,143 | 1.176% |
| 2 | Feed flow blockage | 6,842 | 0.880% |
| 3 | Sensor drift | 4,474 | 0.575% |
| 4 | Mechanical wear | 7,442 | 0.957% |

**27,901 fault rows in total — 3.59%.** Heavily imbalanced by design, and no
single fault class exceeds 1.2%. Accuracy is a useless metric here; predicting
"normal" always scores 96.4%. Use per-class recall, PR-AUC or balanced
accuracy, and stratify every split.

## Data dictionary

| Category | Column | Description |
|---|---|---|
| **Time & identity** | `timestamp` | Reading time, 1-minute steps |
| | `operating_regime` | `A` = baseline, `B` = stressed |
| | `reactor_id` | Reactor unit, e.g. `A_R1` |
| **Environment** | `ambient_temp_effect` | Slow seasonal ambient influence (sinusoidal) |
| **Core sensors** | `reactor_temp` | Internal reactor temperature |
| | `reactor_pressure` | Internal reactor pressure |
| | `feed_flow_rate` | Material inflow rate |
| | `coolant_flow_rate` | Cooling fluid flow rate |
| | `agitator_speed_rpm` | Agitator mixing speed |
| **Process performance** | `reaction_rate` | Speed of the reaction |
| | `conversion_rate` | Fraction of feed converted to product |
| | `selectivity` | Product purity / focus |
| | `yield_pct` | Overall process yield |
| **Mechanical & electrical** | `vibration_rms` | RMS vibration level |
| | `motor_current` | Motor current draw |
| | `power_consumption_kw` | Electrical power usage |
| **Control** | `temp_setpoint` | Target temperature — **see note below** |
| | `pressure_setpoint` | Target pressure — **see note below** |
| **Targets** | `fault_type` | Fault class, 0–4 (classification) |
| | `efficiency_loss_pct` | Estimated efficiency degradation (regression) |
| | `time_to_fault_min` | Minutes until fault onset (forecasting / survival) |

### The setpoints are regime constants, not control signals

Measured across all 777,600 rows, each setpoint takes exactly **one value per
regime**:

| Regime | `temp_setpoint` | `pressure_setpoint` |
|---|---|---|
| A | 180.0 | 12.0 |
| B | 192.0 | 13.5 |

So both columns are **perfectly collinear with `operating_regime`** and carry no
independent information. Deviation from setpoint
(`reactor_temp - temp_setpoint`) is still a sound engineered feature, but
within a single regime it is just a shifted `reactor_temp`. Feeding the raw
setpoint columns to a model is equivalent to leaking the regime label.

## Data quality

| Issue | Measured on the full file |
|---|---|
| Sensor dropouts | **~6% missing in every sensor column** |
| `efficiency_loss_pct` | 46,919 missing (6.0%) |
| `time_to_fault_min` | 751,313 missing (**96.6%**) |

Two of these are not defects:

**The ~6% missingness is simulated sensor dropout, injected at random.** The
source confirms it is *not* target-driven. That makes interpolation,
forward/backward fill or model-based imputation all defensible here — which is
rarely true of real dropouts, where missingness usually correlates with the
fault you are trying to detect.

**`time_to_fault_min` is 96.6% empty by design.** It is a countdown, populated
only on the approach to a fault. Filter to the populated rows for RUL work.
Imputing it invents the target.

## Derived files in this folder

Produced by `cleaning.ipynb`. The raw CSV is untouched and remains canonical.

| File | Rows | Cols | Contents |
|---|---|---|---|
| `chemical_process_timeseries.csv` | 777,600 | 21 | **Raw, as downloaded** |
| `chemical_process_timeseries_A_R1…B_R3.csv` | 129,600 each | 17 | One file per reactor |
| `chemical_process_timeseries_faults.csv` | 27,901 | 21 | Fault rows only (`fault_type` ≠ 0) |
| `chemical_process_timeseries_*_fault0_scatter.png` | — | — | Per-reactor scatter plots |
| `cleaning.ipynb` | — | — | The cleaning and export notebook |

### Transformations applied

**`timestamp` → `minute`.** Recast as integer minutes since
2024-01-01 00:00:00, so each reactor file runs `0` … `129599`. Easier to model
than a datetime, and makes the regular 1-minute grid explicit.

**Per-reactor files drop 4 columns.** `operating_regime` and `reactor_id` are
constant within a file, and `temp_setpoint` / `pressure_setpoint` are regime
constants (above) — so all four are redundant once the data is split by
reactor. 21 − 5 + 1 (`minute` replacing `timestamp`) = 17 columns.

**`efficiency_loss_pct` NaNs filled with 0 where `fault_type == 0`.** Verified
exhaustively across the full file:

| Within `fault_type == 0` | Rows |
|---|---|
| `efficiency_loss_pct` exactly 0 | 704,424 |
| `efficiency_loss_pct` non-zero | **0** |
| `efficiency_loss_pct` missing | 45,275 |

Every known value under normal operation is exactly zero, with **no
counterexamples** — so filling those 45,275 NaNs with 0 is sound rather than an
assumption.

⚠ **This leaves 1,644 still missing** (46,919 − 45,275), all in fault rows
1–4, where 0 is *not* a safe fill — a fault with zero efficiency loss is a
different claim. Handle those separately.

⚠ **After filling, `efficiency_loss_pct == 0` implies `fault_type == 0`.** The
regression target now encodes the classification target. Don't use one to
predict the other.

## Modelling notes

- **Split by `reactor_id`** — `GroupKFold` or `GroupShuffleSplit`. Consecutive
  minutes within a reactor are strongly autocorrelated; a random split leaks
  neighbouring minutes into the test set and will flatter any model.
- **Leave-one-reactor-out is the honest evaluation** here, and the setup the
  dataset was built for. Six reactors means six folds.
- **Train on A, test on B** (or the reverse) for domain shift — the regimes
  differ in temperature, pressure, cooling and noise, so this is a real
  distribution-shift experiment rather than a synthetic one.
- **Gradual onset means labels are soft.** Rows shortly before a fault are
  labelled `0` but already show drift. Predicting `time_to_fault_min` or a
  pre-fault window often works better than classifying `fault_type` directly.
- 201 MB loads comfortably, but downcast to `float32` if you are also holding
  `tep-csv` in memory.
