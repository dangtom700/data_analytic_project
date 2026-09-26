# Smart Factory — Predictive Maintenance

The widest table in the collection: 72 columns covering sensors, maintenance
history, component health scores and pre-computed anomaly scores across a
multi-factory machine fleet.

- **Source:** [kaggle.com/datasets/mobeenfatimah/smart-factory-predictive-maintenance-dataset](https://www.kaggle.com/datasets/mobeenfatimah/smart-factory-predictive-maintenance-dataset)
- **Licence:** not recorded — verify on the Kaggle page.
- **Nature:** synthetic (timestamps are dated **2026**, i.e. future-dated).
- **Size:** 41 MB · 100,000 rows · 72 columns · **CRLF endings**

## Schema by group

**Identity:** `machine_id`, `monitoring_id`, `timestamp`, `factory_id`,
`production_line`, `machine_type` (Milling Machine, Compressor, Pump, CNC
Machine, Hydraulic Press, Conveyor System), `manufacturer`, `model`

**Machine spec:** `installation_year`, `machine_age`, `machine_capacity`,
`machine_power_kw`, `machine_weight_kg`

**Sensors:** `temperature_c`, `vibration_mm_s`, `pressure_bar`,
`rotational_speed_rpm`, `torque_nm`, `voltage_v`, `current_a`,
`power_consumption_kw`, `humidity_percent`, `acoustic_level_db`,
`bearing_temperature_c`, `motor_temperature_c`, `oil_temperature_c`,
`coolant_temperature_c`, `oil_pressure_bar`, `hydraulic_pressure_bar`,
`air_pressure_bar`

**Operations:** `operating_hours`, `idle_hours`, `production_cycles`,
`load_percentage`, `production_rate`, `downtime_hours`, `shift_hours`,
`energy_consumption_kwh`, `factory_shift`

**Environment:** `ambient_temperature_c`, `ambient_humidity_percent`,
`dust_level`, `air_quality_index`, `noise_level_db`

**Maintenance history:** `last_maintenance_date`, `days_since_maintenance`,
`maintenance_count`, `maintenance_cost`, `last_repair_duration_hours`,
`replacement_parts_count`, `technician_experience_years`, `maintenance_type`,
`previous_failure_count`, `days_since_previous_failure`, `failure_frequency`

**Derived health & anomaly scores:** `bearing_health`, `motor_health`,
`pump_health`, `hydraulic_health`, `electrical_health`,
`cooling_system_health`, `temperature_anomaly_score`,
`vibration_anomaly_score`, `pressure_anomaly_score`,
`electrical_anomaly_score`, `energy_anomaly_score`, `machine_health_score`,
`failure_probability`, `maintenance_priority`, `remaining_useful_life_hours`

**Targets:** `failure_type`, `machine_failure`

## Class balance — severely imbalanced

`machine_failure`: **98.5% / 1.5%** (98,528 vs 1,472)

`failure_type`:

| Class | Count | Share |
|---|---|---|
| No Failure | 98,528 | 98.5% |
| Pressure Failure | 265 | 0.3% |
| Bearing Failure | 255 | 0.3% |
| Mechanical Failure | 250 | 0.2% |
| Motor Failure | 242 | 0.2% |
| Electrical Failure | 238 | 0.2% |
| Overheating | 222 | 0.2% |

Around 240 examples per failure class. **Accuracy is meaningless here** —
predicting "No Failure" always scores 98.5%. Use precision/recall, PR-AUC or
balanced accuracy, and stratify every split.

## Notes

- **Heavy leakage risk.** `failure_probability`,
  `remaining_useful_life_hours`, `maintenance_priority`, `machine_health_score`,
  the six `*_health` columns and the five `*_anomaly_score` columns are all
  derived from the target. Using them makes the problem trivial and meaningless.
  **Restrict to raw sensors, spec, operations, environment and maintenance
  history** — that is still ~45 columns of honest features.
- **`machine_failure` is the last column with CRLF endings** — strip `\r` or you
  get classes `0`, `1\r`.
- `machine_id` repeats across rows (5,000 machines × 20 readings). **Group by
  `machine_id`** when splitting, or the same machine appears in train and test.
- Mixed types throughout — `maintenance_type`, `factory_shift`, `machine_type`,
  `manufacturer` and dates all need encoding. Check dtypes on load.
