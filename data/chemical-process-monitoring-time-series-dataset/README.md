# Chemical Process Monitoring — Time Series

Multi-reactor process data with fault type and a time-to-fault countdown, so it
supports classification *and* remaining-useful-life regression.

- **Source:** [kaggle.com/datasets/rohit8527kmr7518/chemical-process-monitoring-time-series-dataset](https://www.kaggle.com/datasets/rohit8527kmr7518/chemical-process-monitoring-time-series-dataset)
- **Licence:** not recorded — verify on the Kaggle page.
- **Nature:** synthetic.
- **Size:** 201 MB · 777,600 rows · 21 columns · LF endings
- **Span:** starts 2024-01-01 00:00:00

## Schema

| Column | Role | Notes |
|---|---|---|
| `timestamp` | index | |
| `operating_regime` | group | Categorical (`A`, …) |
| `reactor_id` | group | e.g. `A_R1` — regime and reactor encoded together |
| `ambient_temp_effect` | feature | |
| `reactor_temp`, `reactor_pressure` | feature | Paired with setpoints below |
| `feed_flow_rate`, `coolant_flow_rate`, `agitator_speed_rpm` | feature | |
| `reaction_rate`, `conversion_rate`, `selectivity`, `yield_pct` | feature | Process performance |
| `vibration_rms`, `motor_current`, `power_consumption_kw` | feature | Mechanical/electrical |
| `temp_setpoint`, `pressure_setpoint` | feature | **Deviation from setpoint is the signal** — engineer `reactor_temp - temp_setpoint` |
| `fault_type` | **target** | Classification |
| `efficiency_loss_pct` | target | Regression |
| `time_to_fault_min` | **target** | RUL — see below |

## Data quality

| Issue | Detail |
|---|---|
| Missing values | **~6% in every sensor column**, uniformly (measured on a 50k-row sample) |
| `time_to_fault_min` | **90.6% missing** |

The uniform ~6% missingness across unrelated columns is injected at random, not a
sensor pattern — so simple interpolation is defensible here in a way it wouldn't
be for real dropouts.

`time_to_fault_min` being 90.6% empty is **expected, not broken**: it is only
populated during the run-up to a fault. Filter to those rows for RUL work rather
than imputing; imputing a countdown that doesn't exist invents the target.

## Notes

- **Group by `reactor_id`** when splitting — consecutive rows from one reactor
  are strongly autocorrelated.
- 201 MB is comfortable in memory, but downcast to `float32` if you're also
  holding the TEP data.
