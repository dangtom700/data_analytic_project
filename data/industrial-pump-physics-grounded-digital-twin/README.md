# Industrial Pump — Physics-Grounded Digital Twin

Pump degradation trajectories with failure events, maintenance actions, cost
accounting and pre-computed failure probabilities. Unusually rich on the
decision/economics side.

- **Source:** [kaggle.com/datasets/ishanpradhan95/industrial-pump-physics-grounded-digital-twin](https://www.kaggle.com/datasets/ishanpradhan95/industrial-pump-physics-grounded-digital-twin)
- **Licence:** not recorded — verify on the Kaggle page.
- **Nature:** synthetic (digital twin simulation).
- **Size:** 116 MB · 379,786 rows · 32 columns
- **Span:** starts 2023-12-04

## Schema

**Grouping & time:** `step`, `trajectory_id` (**the grouping key**), `timestamp`

**Actual sensors — only three:** `vibration_g`, `temperature_c`, `power_factor`

**Events:** `failure_event`, `failure_type`, `time_to_failure_hours` (**RUL target**),
`maintenance_event`, `maintenance_type`, `maintenance_cost_usd`, `downtime_hours`

**Model outputs already baked in:** `predicted_time_to_failure`,
`prediction_error_margin`, `prediction_confidence`, `hazard_score`,
`failure_probability_next_24h`, `failure_probability_next_7d`,
`recommended_action`, `urgency_level`

**Sensor-fault simulation:** `sensor_bias`, `sensor_drift`, `false_alarm_flag`,
`sensor_dropout`

**Economics:** `cost_per_hour_downtime`, `expected_savings_if_actioned`,
`downtime_loss_usd`, `cumulative_loss_usd`, `preventable_loss_usd`

**Other:** `killer_trajectory`, `machine_status` (e.g. `OPTIMAL`)

## Data quality

| Column | Missing | Interpretation |
|---|---|---|
| `failure_type` | 99.9% | **Expected** — only set on the row where a failure occurs |
| `maintenance_type` | 99.7% | **Expected** — only set on maintenance rows |
| `temperature_c` | 1.9% | Genuine sensor dropout (see `sensor_dropout`) |

Don't impute the first two — they are event annotations, not measurements.

## Notes

- **This dataset largely contains someone else's model's answers.** If your goal
  is to build a predictive-maintenance model, your features are
  `vibration_g`, `temperature_c`, `power_factor` and time — and your target is
  `time_to_failure_hours`. Every `predicted_*`, `hazard_score`,
  `failure_probability_*`, `recommended_action` and `urgency_level` column is
  **leakage**, and so are the loss columns derived from them. Drop them or you
  will get a suspiciously excellent model that learned to copy.
- Those columns *are* useful as a **baseline to beat** — compare your RUL
  estimate against `predicted_time_to_failure`.
- Three real sensors against a 32-column table is a thin signal. Feature
  engineering over `trajectory_id` windows (rolling means, slopes) is where the
  work is.
- `sensor_bias`, `sensor_drift` and `sensor_dropout` let you study robustness to
  instrument faults deliberately — a genuinely interesting angle here.
- **Split by `trajectory_id`.**
