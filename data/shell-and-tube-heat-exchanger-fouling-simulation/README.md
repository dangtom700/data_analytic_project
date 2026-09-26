# Shell & Tube Heat Exchanger — Fouling Simulation

A physics-based simulation of fouling build-up in a shell-and-tube heat
exchanger, including clean-in-place (CIP) events. Well-suited to regression on a
continuously degrading target.

- **Source:** [kaggle.com/datasets/fdavidsantillan/shell-and-tube-heat-exchanger-fouling-simulation](https://www.kaggle.com/datasets/fdavidsantillan/shell-and-tube-heat-exchanger-fouling-simulation)
- **Licence:** not recorded — verify on the Kaggle page.
- **Nature:** synthetic, but **physics-grounded** (real heat-transfer correlations).
- **Size:** 167 MB · 700,800 rows · 25 columns
- **Note:** the CSV sits in an `output/` subfolder: `output/shell_tube_fouling_final.csv`

## Schema

| Column | Meaning |
|---|---|
| `scenario_id` | Operating scenario, e.g. `T50_Q3.0` (inlet temp / flow). **The grouping key.** |
| `T_in_C`, `T_in_K` | Inlet temperature — same value in °C and K, so **drop one** |
| `m_dot_nominal_kg_s` | Nominal mass flow |
| `time_h` | Hours since clean condition — the degradation clock |
| `Re` | Reynolds number |
| `u_m_s` | Fluid velocity |
| `tau_w_Pa` | Wall shear stress (governs fouling removal) |
| `dP_Pa` | Pressure drop |
| `Rf_m2K_W` | **Fouling resistance — the physical quantity of interest** |
| `U_clean_W_m2K` | Clean overall heat-transfer coefficient (baseline) |
| `U_overall_W_m2K` | Current overall HTC |
| `Q_W`, `Q_clean_W` | Current vs clean heat duty |
| `thermal_efficiency` | Q / Q_clean, starts at 1.0 |
| `fouling_factor_TEMA` | TEMA standard fouling class (categorical, e.g. `L`) |
| `T_in_measured_C`, `m_dot_measured_kg_s` | **Noisy sensor versions** of the true inputs |
| `cip_event` | 0/1 — clean-in-place performed |
| `cip_effectiveness` | How much fouling the clean removed |
| `R_wall_m2K_W` | Wall thermal resistance (constant) |
| `U_total_W_m2K`, `Q_total_W`, `efficiency_total` | Totals including wall resistance |
| `degradation_source` | Categorical mechanism, e.g. `corrosion` |

## Notes

- **Beware target leakage.** `Rf_m2K_W`, `U_overall_W_m2K`, `thermal_efficiency`,
  `Q_W` and the `*_total` columns are all analytic functions of one another. If
  you predict fouling from `U_overall`, you are predicting a number from itself.
  Realistic feature sets use only what a plant actually instruments:
  temperatures, flows and pressure drop — and prefer the `*_measured_*` columns,
  which carry sensor noise.
- **`T_in_C` and `T_in_K` are perfectly collinear.** Same for several derived
  pairs. Check the correlation matrix before fitting anything linear.
- `cip_event` resets the degradation trajectory. Split by `scenario_id`, and
  treat each inter-CIP interval as a separate degradation cycle.
- No missing values.
