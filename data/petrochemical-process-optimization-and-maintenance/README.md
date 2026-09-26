# Petrochemical Process Optimization & Maintenance

A small, wide-ranging table spanning catalyst condition, energy consumption and
yield across several named process units. Aimed at optimisation rather than
fault detection.

- **Source:** [kaggle.com/datasets/masoudfazli/petrochemical-process-optimization-and-maintenance](https://www.kaggle.com/datasets/masoudfazli/petrochemical-process-optimization-and-maintenance)
- **Licence:** not recorded — verify on the Kaggle page.
- **Nature:** synthetic.
- **Size:** 2.7 MB · 10,000 rows · 16 columns
- **Span:** starts 2020-01-01 00:00:00

## Schema

| Column | Meaning |
|---|---|
| `Timestamp` | Hourly readings |
| `Unit_Name` | e.g. `Methanol_Complex_03` — **grouping key** |
| `Catalyst_Type` | e.g. `Iron_Standard_V5` (categorical) |
| `Catalyst_Age_Days` | Catalyst service age |
| `Sensor_Health_Index` | 0–1 instrument health |
| `Vibration_Level_mm_s` | Rotating equipment vibration |
| `Valve_Opening_Percent` | Control valve position |
| `Feedstock_Flow_m3h` | Feed rate |
| `Reactor_Temp_C`, `Reactor_Pressure_Bar` | Reactor conditions |
| `Electricity_MWh`, `Natural_Gas_m3h`, `Steam_Tons_h` | Utility consumption |
| `Ambient_Temp_C` | Ambient (goes negative — winter, not an error) |
| **`Product_Yield_Tons`** | **Regression target** |
| **`Energy_Intensity`** | **Regression target** (energy per unit product) |

## ⚠ Encoding

The file begins with a **UTF-8 BOM**, so the first column name parses as
`﻿Timestamp` (with an invisible prefix) and `df['Timestamp']` raises `KeyError`.
Read it as:

```python
pd.read_csv('petrochemical_advanced_data.csv', encoding='utf-8-sig')
```

This is the single most likely thing to waste your time on in this folder.

## Notes

- **`Energy_Intensity` is derived from `Product_Yield_Tons` and the utility
  columns.** Predicting either target while the other and the utilities are in
  your feature set is circular. Pick one target and drop its inputs.
- `Catalyst_Age_Days` against yield is the most interesting relationship here —
  catalyst deactivation is a real and well-understood decay process.
- **Group by `Unit_Name`** when splitting; different units have different
  baselines.
- 10,000 rows is small. Cross-validate rather than relying on a single holdout.
- No missing values.
