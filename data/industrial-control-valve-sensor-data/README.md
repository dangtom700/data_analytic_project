# Industrial Control Valve — Sensor Data

Control-valve condition monitoring with a binary failure label. The largest of
the three same-author sensor datasets in this collection.

- **Source:** [kaggle.com/datasets/drsayed/industrial-control-valve-sensor-data](https://www.kaggle.com/datasets/drsayed/industrial-control-valve-sensor-data)
- **Licence:** not recorded — verify on the Kaggle page.
- **Nature:** synthetic.
- **Size:** 76 MB · 200,000 rows · 25 columns · **CRLF endings**

## Schema

No timestamp — rows are independent observations, not a time series.

| Group | Columns |
|---|---|
| Position / control | `Valve_Position_pct`, `Command_Signal_mA`, `Position_Error_pct`, `Response_Time_s` |
| Process | `Upstream_Pressure_bar`, `Downstream_Pressure_bar`, `Pressure_Drop_bar`, `Flow_Rate_m3h`, `Fluid_Temperature_C`, `Fluid_Density_kgm3` |
| Actuator | `Actuator_Current_mA`, `Actuator_Temperature_C`, `Actuator_Power_W` |
| Vibration | `Vibration_X_mm_s`, `Vibration_Y_mm_s`, `Vibration_Z_mm_s`, `Vibration_Total_mm_s` |
| Mechanical | `Stem_Torque_Nm`, `Packing_Temperature_C`, `Leak_Rate_ml_min` |
| Service history | `Cycle_Count`, `Time_Since_Last_Maintenance_d` |
| Ambient / supply | `Ambient_Temperature_C`, `Supply_Pressure_bar` |
| **Target** | `Valve_Failure` — 0/1 |

## Class balance

| Value | Count | Share |
|---|---|---|
| 0 (healthy) | 121,497 | 60.7% |
| 1 (failed) | 78,503 | 39.3% |

Close to balanced — unusually so for a failure dataset, and a hint that it is
generated rather than observed. Accuracy is a usable metric here, which is rarely
true of real predictive-maintenance data.

## Data quality

**~5% missing in every one of the 24 feature columns**, uniformly, with the
target complete. Injected at random rather than any physical dropout pattern, so
mean/median imputation is defensible. Dropping rows loses ~70% of the data
(24 columns × 5% independent), so **impute rather than `dropna()`** — this is the
classic trap with this file.

## Notes

- **CRLF line endings**, and the target is the last column. If you parse by hand
  rather than with pandas, `Valve_Failure` will come out as `1\r` and silently
  become two classes. Strip `\r`.
- `Vibration_Total_mm_s` is derivable from the X/Y/Z components — collinear.
- `Pressure_Drop_bar` = upstream − downstream. Same issue.
- Same author and same fingerprint (CRLF, uniform 5% missingness, no timestamp)
  as `pump-station-sensor-data` and `heat-exchanger-fouling-sensor`. Probably one
  generator; treat conclusions across the three as one result, not three.
