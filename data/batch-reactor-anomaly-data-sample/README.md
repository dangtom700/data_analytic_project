# Batch Reactor — Anomaly Data (Sample)

A small excerpt of a batch-reactor dataset, shipped with an EDA notebook and
explicit licence files. The smallest dataset here.

- **Source:** [kaggle.com/datasets/aimindteams/batch-reactor-anomaly-data-sample](https://www.kaggle.com/datasets/aimindteams/batch-reactor-anomaly-data-sample)
- **Nature:** synthetic.
- **Size:** 156 KB · 4,901 rows · 7 columns

## ⚠ Licence — the only restrictive one in this collection

This folder ships its own licence files, and they differ:

| File | Covers | Licence |
|---|---|---|
| `LICENSE-DATA.txt` | The CSV | **CC BY-NC 4.0** — Attribution–**NonCommercial** |
| `LICENSE-CODE.txt` | The notebook | MIT-style permissive (© 2026 AI Mind Teams) |

**The data is non-commercial only.** Coursework and personal projects are fine;
anything commercial is not. This is the one dataset here with a licence you can
actually verify, so honour it — and attribute AI Mind Teams if you publish.

## Files

- `reactor_sample_5k.csv` — the data
- `Reactor_EDA_and_PoV.ipynb` — the publisher's own EDA / proof-of-value notebook
- `LICENSE-DATA.txt`, `LICENSE-CODE.txt`

## Schema

| Column | Meaning |
|---|---|
| `Timestamp_min` | Minutes from batch start (0, 1, 2, …) |
| `Reactor_Temp_C` | Reactor temperature |
| `Jacket_Flow_Rate_L_min` | Cooling jacket flow |
| `Pressure_atm` | Reactor pressure |
| `Reactant_A_Conc_mol_L` | Reactant A concentration (falls over the batch) |
| `Product_B_Conc_mol_L` | Product B concentration (rises from 0) |
| `Reactor_Run_ID` | Batch id — **the grouping key** |

## Notes

- **No label column.** Despite "anomaly" in the name, there is no anomaly flag —
  this is an unsupervised problem, or you define anomalies yourself from the
  batch trajectories. Check the bundled notebook for the publisher's framing.
- A **"5k sample"** of a larger commercial dataset, and 4,901 rows across several
  batches is a handful of trajectories. Fine for prototyping, too small for
  conclusions.
- Reactant A falling while Product B rises is the expected reaction profile —
  batch progress is largely a function of `Timestamp_min`, so beware of
  "predicting" concentration from time and calling it a model.
- No missing values.
