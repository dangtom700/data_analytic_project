# Heat Exchanger Fouling — Sensor Data

Heat exchanger readings with a binary fouling label. The smallest and
best-balanced classification set here — a good first dataset for a new pipeline.

- **Source:** [kaggle.com/datasets/drsayed/heat-exchanger-fouling-sensor](https://www.kaggle.com/datasets/drsayed/heat-exchanger-fouling-sensor)
- **Licence:** not recorded — verify on the Kaggle page.
- **Nature:** synthetic.
- **Size:** 7.3 MB · 40,267 rows · 12 columns · **CRLF endings**

## Schema

| Column | Meaning |
|---|---|
| `Hot_Inlet_Temp_C`, `Hot_Outlet_Temp_C` | Hot-side temperatures |
| `Cold_Inlet_Temp_C`, `Cold_Outlet_Temp_C` | Cold-side temperatures |
| `Hot_Flow_m3h`, `Cold_Flow_m3h` | Flows |
| `Hot_Side_Pressure_Drop_bar`, `Cold_Side_Pressure_Drop_bar` | Pressure drops |
| `Heat_Transfer_Rate_kW` | Duty |
| `Overall_HTC_W_m2K` | Overall heat-transfer coefficient |
| `Thermal_Effectiveness_pct` | Effectiveness |
| **`Fouling_Detected`** | **Target** — 0/1 |

## Class balance

| Value | Count | Share |
|---|---|---|
| 1 (fouled) | 20,134 | 50.0% |
| 0 (clean) | 20,133 | 50.0% |

A 50/50 split to within one row. Convenient, and a clear sign of a generated
dataset — real fouling data is never balanced.

## Data quality

**~5% missing in all 11 feature columns**, uniformly. Target complete. Impute
rather than drop.

## Notes

- `Overall_HTC_W_m2K` and `Thermal_Effectiveness_pct` are the *standard
  indicators* of fouling — they are close to being the label restated in physical
  units. A model using them will score very well and will have learned nothing.
  For a meaningful exercise, predict fouling from **temperatures, flows and
  pressure drops only**, and use the HTC-based model as your ceiling.
- LMTD and effectiveness-NTU features can be derived from the four temperatures
  and two flows — good practice, and physically motivated.
- **CRLF endings**, target is the last column — strip `\r` if parsing by hand.
- Same generator fingerprint as `industrial-control-valve-sensor-data` and
  `pump-station-sensor-data`.
