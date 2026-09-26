# Dataset Catalogue

All 16 datasets in `data/`, profiled by direct inspection (row counts, class
balances and missing-value rates below were measured, not copied from the source
pages). Each dataset's own `README.md` has the full schema.

- **Total:** ~17 GB · 16 datasets · none in git (see [`../README.md`](../README.md))
- **Fetch:** `python data_download.py` gets 15 of them; IndPenSim is manual.

---

## 1. Provenance — what is actually real

This matters more than anything else here. Only four of the sixteen are measured
or peer-reviewed simulator data. **Results on synthetic data demonstrate that
your pipeline works; they do not tell you anything about real equipment.**

| Dataset | Provenance |
|---|---|
| `metropt-3-dataset` | **Real** — metro train compressor, 7 months in service |
| `time-series-of-industrial-boiler-operations` | **Real** — published in *Scientific Data* (2025) |
| `noboom-…-chemical-processes` | **Real** — measured on physical distillation rigs |
| `indpensim-penicillin-fermentation` | Simulated, but a **published, validated** industrial simulator |
| `tep-csv` | Simulated — the **canonical peer-reviewed benchmark** (Downs & Vogel 1993) |
| `shell-and-tube-heat-exchanger-fouling-simulation` | Simulated, physics-grounded |
| `industrial-pump-physics-grounded-digital-twin` | Simulated (digital twin) |
| `batch-reactor-anomaly-data-sample` | Synthetic |
| `chemical-process-monitoring-time-series-dataset` | Synthetic |
| `heat-exchanger-fouling-sensor` | Synthetic |
| `industrial-control-valve-sensor-data` | Synthetic |
| `industrial-iot-predictive-maintenance-pdm` | Synthetic |
| `petrochemical-process-optimization-and-maintenance` | Synthetic |
| `pump-station-sensor-data` | Synthetic |
| `smart-factory-predictive-maintenance-dataset` | Synthetic (timestamps dated 2026) |
| `industrial-sensor-anomaly-detection-dataset` | **Unclear** — small transformed derivative of SWaT/WADI |

Three of them — `heat-exchanger-fouling-sensor`, `pump-station-sensor-data` and
`industrial-control-valve-sensor-data` — share an author and an identical
fingerprint (CRLF endings, no timestamp, uniform ~5% injected missingness). Treat
findings across those three as **one** result, not three independent ones.

## 2. Licences — mostly unverified

Only one dataset here ships a licence file. **The rest were downloaded without
recording a licence**, and Kaggle pages don't render for automated fetching, so
these need a manual check.

| Dataset | Licence |
|---|---|
| `batch-reactor-anomaly-data-sample` | **CC BY-NC 4.0** (data) + MIT-style (code) — **non-commercial only** |
| `time-series-of-industrial-boiler-operations` | Governed by the *Scientific Data* record — cite the paper |
| `metropt-3-dataset` | Upstream UCI record is CC BY 4.0 — confirm the Kaggle mirror |
| `indpensim-penicillin-fermentation` | Mendeley Data record (likely CC BY 4.0) — confirm |
| *all others* | **Not recorded** — check the Kaggle page before publishing or sharing |

**To do:** open each source page, record the licence in that dataset's
`README.md`, and replace the "not recorded" line. Fifteen minutes of work that
prevents a real problem later.

## 3. Quick reference

| Dataset | Size | Rows | Cols | Target | Task |
|---|---|---|---|---|---|
| `noboom-…-chemical-processes` | 8.0 GB | 177 files | 29 / 245 | 8 label cols / `Anomaly` | Anomaly detection |
| `tep-csv` | 5.7 GB | 15,330,000 | 55 | `faultNumber` | 21-class fault ID |
| `indpensim-penicillin-fermentation` | 2.4 GB | 113,935 | 2,239 | `Fault flag` / yield | Batch quality, spectra |
| `metropt-3-dataset` | 209 MB | 1,516,948 | 17 | *none — build it* | Failure prediction |
| `chemical-process-monitoring-…` | 201 MB | 777,600 | 21 | `fault_type`, `time_to_fault_min` | Classification + RUL |
| `shell-and-tube-heat-exchanger-…` | 167 MB | 700,800 | 25 | `Rf_m2K_W` | Fouling regression |
| `industrial-pump-…-digital-twin` | 116 MB | 379,786 | 32 | `time_to_failure_hours` | RUL |
| `industrial-control-valve-sensor-data` | 76 MB | 200,000 | 25 | `Valve_Failure` | Binary (60/40) |
| `smart-factory-predictive-maintenance` | 41 MB | 100,000 | 72 | `machine_failure`, `failure_type` | Binary (98.5/1.5) + 7-class |
| `time-series-of-industrial-boiler-…` | 39 MB | 86,400 ×2 | 31 | *none* | Unsupervised / forecasting |
| `pump-station-sensor-data` | 17 MB | 100,000 | 11 | `Pump_Efficiency_Pct` | Regression |
| `heat-exchanger-fouling-sensor` | 7.3 MB | 40,267 | 12 | `Fouling_Detected` | Binary (50/50) |
| `industrial-iot-predictive-maintenance-pdm` | 3.6 MB | 36,000 | 7 | `machine_status` | 3-class (97.5/2/0.5) |
| `petrochemical-process-optimization-…` | 2.7 MB | 10,000 | 16 | `Product_Yield_Tons`, `Energy_Intensity` | Regression |
| `industrial-sensor-anomaly-detection` | 2.2 MB | 1,000 + 500 | 53 / 129 | `Normal/Attack`, `Attack` | Binary (85/15, 90/10) |
| `batch-reactor-anomaly-data-sample` | 156 KB | 4,901 | 7 | *none* | Unsupervised |

## 4. Target leakage — read before modelling

Five datasets ship columns computed **from** the target. Using them produces an
excellent score and a worthless model. This is the most common way to waste a
weekend on this collection.

| Dataset | Drop these |
|---|---|
| `industrial-pump-…-digital-twin` | `predicted_time_to_failure`, `prediction_*`, `hazard_score`, `failure_probability_*`, `recommended_action`, `urgency_level`, and the `*_loss_usd` columns |
| `smart-factory-predictive-maintenance` | `failure_probability`, `remaining_useful_life_hours`, `maintenance_priority`, `machine_health_score`, all six `*_health`, all five `*_anomaly_score` |
| `shell-and-tube-heat-exchanger-…` | `U_overall_W_m2K`, `thermal_efficiency`, `Q_W`, `*_total` — all analytic functions of `Rf_m2K_W` |
| `heat-exchanger-fouling-sensor` | `Overall_HTC_W_m2K`, `Thermal_Effectiveness_pct` — these *are* fouling, restated |
| `petrochemical-process-optimization-…` | The two targets are derived from each other and the utility columns — pick one |

The pattern: if a column is something a model *outputs* rather than something an
instrument *measures*, it isn't a feature.

## 5. Grouping keys — never split randomly

Almost every dataset has repeated-measures structure. A random `train_test_split`
puts the same machine, batch or run on both sides and inflates your score.

| Dataset | Group by |
|---|---|
| `tep-csv` | `simulationRun` |
| `noboom-…` | operating-point folder |
| `indpensim-…` | `Batch ID` (**100 batches is the real sample size, not 113,935 rows**) |
| `chemical-process-monitoring-…` | `reactor_id` |
| `shell-and-tube-…` | `scenario_id` (and each inter-CIP interval) |
| `industrial-pump-…` | `trajectory_id` |
| `smart-factory-…` | `machine_id` (5,000 machines × 20 rows) |
| `industrial-iot-…-pdm` | `machine_id` |
| `petrochemical-…` | `Unit_Name` |
| `batch-reactor-…` | `Reactor_Run_ID` |

Use `GroupKFold` / `GroupShuffleSplit`, or `TimeSeriesSplit` where order matters.

## 6. Loading gotchas

| Dataset | Gotcha |
|---|---|
| `petrochemical-…` | **UTF-8 BOM** → first column reads as `﻿Timestamp`. Use `encoding='utf-8-sig'` |
| `heat-exchanger-fouling-sensor`, `pump-station-…`, `industrial-control-valve-…`, `smart-factory-…` | **CRLF endings** and the target is the last column → `1\r` becomes a phantom class if not parsed with pandas |
| `metropt-3-dataset` | Unnamed leading pandas index → `index_col=0` |
| `noboom-…/industry_process` | Trailing comma on every row → phantom empty final column |
| `noboom-…` lab rigs | `Time` is `HH:MM:SS` with **no date** |
| `indpensim-…` | 2,239 columns; units are baked into column names; `usecols` is essential |
| `industrial-sensor-anomaly-…` | Already z-scored — **don't scale again**; `Normal/Attack` contains a `/` |
| `industrial-sensor-anomaly-…` | `WADI.csv` splits `Date` and `Time` into two columns |
| `tep-csv` | `TEP_Faulty_Testing.csv` is 3.4 GB → read in chunks or convert to Parquet |
| `indpensim-…` | Missing values are the literal string `NaN` |

## 7. Missing data

| Dataset | Missing | Is it a problem? |
|---|---|---|
| `heat-exchanger-fouling-sensor` | ~5% in all 11 features | Injected at random → impute. `dropna()` costs ~40% of rows |
| `pump-station-sensor-data` | ~5% in all 10 features | Same |
| `industrial-control-valve-sensor-data` | ~5% in all 24 features | Same — `dropna()` costs ~70% of rows |
| `chemical-process-monitoring-…` | ~6% in all sensors | Same |
| `chemical-process-monitoring-…` | `time_to_fault_min` 90.6% | **By design** — only populated before a fault. Filter, don't impute |
| `industrial-pump-…` | `failure_type` 99.9%, `maintenance_type` 99.7% | **By design** — event annotations, not measurements |
| `industrial-pump-…` | `temperature_c` 1.9% | Real dropout (see `sensor_dropout`) |
| `indpensim-…` | Offline assay columns mostly `NaN` | **By design** — offline samples are infrequent |
| `time-series-of-industrial-boiler-…` | 30 cells in `data.csv` | Or use `data_AutoReg.csv`, which has them filled |
| *all others* | None | — |

## 8. Where to start

- **New pipeline?** `industrial-iot-predictive-maintenance-pdm` — 3.6 MB, four
  features, one clean label.
- **Want a result that means something?** `metropt-3-dataset` or
  `time-series-of-industrial-boiler-operations` — real equipment, real messiness.
  Note that both are unlabelled: constructing the target is the work.
- **Benchmarking against literature?** `tep-csv`. Decades of published baselines,
  and faults 3, 9 and 15 are conventionally excluded as undetectable.
- **Something genuinely hard?** `noboom-…` — real rigs, six process families,
  multiple label definitions, and a required transfer across operating points.

## 9. Finding more data

`awesome-industrial-datasets-master/` (git-ignored) is a clone of
[awesome-industrial-datasets](https://github.com/dalmia/awesome-industrial-datasets)
— 190 industrial datasets described in `json/` and `markdown/`, with a taxonomy
in `DATASET_TAXONOMY.md`. Nothing here depends on it; it's a lookup table for
finding the next dataset.
