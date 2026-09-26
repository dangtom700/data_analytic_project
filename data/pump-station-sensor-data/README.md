# Pump Station — Sensor Data

Centrifugal pump readings with efficiency as a continuous target. A compact,
clean regression problem.

- **Source:** [kaggle.com/datasets/drsayed/pump-station-sensor-data](https://www.kaggle.com/datasets/drsayed/pump-station-sensor-data)
- **Licence:** not recorded — verify on the Kaggle page.
- **Nature:** synthetic.
- **Size:** 17 MB · 100,000 rows · 11 columns · **CRLF endings**

## Schema

No timestamp — independent observations.

| Column | Meaning |
|---|---|
| `Suction_Pressure_bar` | Inlet pressure |
| `Discharge_Pressure_bar` | Outlet pressure |
| `Flow_Rate_m3h` | Volumetric flow |
| `Motor_Current_A` | Motor current |
| `Vibration_mm_s` | Vibration velocity |
| `Bearing_Temperature_C` | Bearing temperature |
| `Ambient_Temperature_C` | Ambient temperature |
| `Runtime_hours` | Cumulative operating hours |
| `Fluid_Density_kgm3` | Pumped fluid density |
| `Pump_Speed_rpm` | Shaft speed |
| **`Pump_Efficiency_Pct`** | **Regression target** |

## Data quality

**~5% missing in all 10 feature columns**, uniformly; the target is complete.
`dropna()` would cost you roughly 40% of the rows for no good reason — impute.

## Notes

- Differential head (`Discharge_Pressure_bar - Suction_Pressure_bar`) is the
  physically meaningful quantity and a better feature than either pressure alone.
  Hydraulic power ∝ flow × head is worth constructing too.
- Pump affinity laws mean flow, head and power all scale with `Pump_Speed_rpm`.
  Normalising by speed often linearises the problem considerably.
- **CRLF endings.** Strip `\r` if not using pandas.
- Same generator fingerprint as `industrial-control-valve-sensor-data` and
  `heat-exchanger-fouling-sensor` (same author, CRLF, uniform 5% missingness,
  no timestamp).
