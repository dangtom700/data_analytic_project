# Industrial Sensor Anomaly Detection (SWaT / WADI samples)

Two small files carrying the column names of **SWaT** and **WADI**, the
well-known water-treatment ICS security testbeds. Read the warning below before
using these for anything you intend to report.

- **Source:** [kaggle.com/datasets/colabsss/industrial-sensor-anomaly-detection-dataset](https://www.kaggle.com/datasets/colabsss/industrial-sensor-anomaly-detection-dataset)
- **Licence:** not recorded — verify on the Kaggle page.
- **Nature:** **unclear provenance — see below.**
- **Size:** 2.2 MB total

## ⚠ These are not the real SWaT and WADI datasets

| | This folder | Genuine SWaT / WADI |
|---|---|---|
| Rows | 1,000 and 500 | Hundreds of thousands to ~1 M |
| Values | Pre-standardised, ≈ N(0,1) | Raw engineering units |
| Access | Public Kaggle download | Signed request form, iTrust / SUTD |

The real datasets come from Singapore University of Technology and Design's
iTrust centre and **require a signed request** — they are not freely
redistributable. These files are ~1,000 rows of already-z-scored values, and they
mix authentic SWaT/WADI tag names (`P206`, `DPIT301`, `1_AIT_001_PV`) with
generic `Sensor_N` columns, which the originals do not have.

**So:** fine for wiring up an anomaly-detection pipeline. **Do not cite results
from these as SWaT or WADI results** — they are a small, transformed derivative
of unclear lineage, and at 1,000 rows nothing you measure will be stable. If you
need the real thing, request it from iTrust.

## Files

### `SWAT_Dataset.csv` — 1,000 rows × 53 columns

- Authentic SWaT tags: `P206`, `DPIT301`, `FIT301`, `LIT301`, `MV301`–`MV304`,
  `P301`/`P302`, `AIT401`/`AIT402`, `FIT401`, `LIT401`, `P401`–`P404`, `UV401`,
  `AIT501`–`AIT504`, `FIT501`–`FIT504`, `P501`/`P502`, `PIT501`–`PIT503`,
  `FIT601`, `P601`–`P603` — plus `Sensor_0`–`Sensor_15`
- Target: **`Normal/Attack`** (string) — note the `/` in the column name

| Class | Count | Share |
|---|---|---|
| Normal | 850 | 85.0% |
| Attack | 150 | 15.0% |

### `WADI.csv` — 500 rows × 129 columns

- `Date` and `Time` as **two separate columns** — combine them
- Authentic WADI tags: `1_AIT_001_PV`–`1_AIT_005_PV`, `1_FIT_001_PV`,
  `1_LS_001_AL`/`002_AL`, `1_LT_001_PV`, `1_MV_001_STATUS`–`004_STATUS`,
  `1_P_001_STATUS`–`006_STATUS`, `2_DPIT_001_PV` — plus `Sensor_21`–`Sensor_120`
- Then `LEAK_DIFF_PRESSURE`, `PLANT_START_STOP_LOG`,
  `TOTAL_CONS_REQUIRED_FLOW`
- Target: **`Attack`** (0/1)

| Class | Count | Share |
|---|---|---|
| 0 (normal) | 450 | 90.0% |
| 1 (attack) | 50 | 10.0% |

## Notes

- **Already standardised** — do not scale again. It also means you cannot sanity-
  check values against physical plausibility, which is normally how you'd catch
  problems in ICS data.
- The two files have **different schemas and different target columns** — they are
  two datasets in one folder, not a train/test pair.
- In `SWAT_Dataset.csv` the target `Normal/Attack` is the **last column**; the
  slash in the name also trips up `df.query()` and formula interfaces. Rename it
  on load.
- 50 attack rows in WADI means a single split can swing wildly. Use
  cross-validation and report variance, or better, treat these as a smoke test
  only.
