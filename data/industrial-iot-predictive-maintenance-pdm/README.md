# Industrial IoT — Predictive Maintenance (PdM)

A deliberately simple three-class problem: four sensors, one status label. Good
for teaching or as a sanity check on a pipeline.

- **Source:** [kaggle.com/datasets/gagandeepgambhir2/industrial-iot-predictive-maintenance-pdm](https://www.kaggle.com/datasets/gagandeepgambhir2/industrial-iot-predictive-maintenance-pdm)
- **Licence:** not recorded — verify on the Kaggle page.
- **Nature:** synthetic.
- **Size:** 3.6 MB · 36,000 rows · 7 columns
- **Span:** starts 2024-01-01T00:00:00 (ISO 8601 with `T` separator)

## Schema

| Column | Role |
|---|---|
| `timestamp` | ISO 8601 |
| `machine_id` | `M-01` … — **the grouping key** |
| `sensor_temperature` | feature |
| `sensor_vibration` | feature |
| `sensor_pressure` | feature |
| `power_draw_kw` | feature |
| **`machine_status`** | **target** — 3 classes |

## Class balance

| Class | Count | Share |
|---|---|---|
| Normal | 35,100 | 97.5% |
| Warning | 720 | 2.0% |
| Failure | 180 | 0.5% |

Strongly imbalanced, with only 180 failures. Stratify your splits and report
per-class recall — the Failure class is the whole point and is easy to lose.

## Notes

- Four features and a clean label make this the **easiest dataset here to start
  with**. Build your pipeline on this, then move to TEP or NoBoom.
- `Warning` sits between `Normal` and `Failure`, so the target is **ordinal**.
  Ordinal models, or treating Warning as an early-failure signal, can beat plain
  multiclass.
- Genuine time series per machine — rolling statistics over `machine_id` windows
  should help considerably, and **group by `machine_id`** when splitting.
- No missing values.
