# IndPenSim — 100 Batches of Penicillin Fermentation

100 simulated batches of an industrial-scale (100,000 L) penicillin
fermentation, including **Raman spectroscopy** channels. The only dataset here
with spectral data, and the only one from Mendeley rather than Kaggle.

- **Source:** Mendeley Data — IndPenSim, Goldrick et al.
  Search "IndPenSim 100 batches" on [data.mendeley.com](https://data.mendeley.com/).
- **Nature:** simulated, from a published and validated industrial simulator.
- **Licence:** not recorded — verify on the Mendeley record (Mendeley Data
  defaults to CC BY 4.0, but confirm).
- **Size:** 2.4 GB · 113,935 rows · **2,239 columns**

> **Not downloaded by `data_download.py`** — it is not on Kaggle. Fetch it from
> Mendeley manually and drop both CSVs in this folder.

## Files

| File | Size | Rows | Contents |
|---|---|---|---|
| `100_Batches_IndPenSim_V3.csv` | 2.4 GB | 113,935 | The batch time series |
| `100_Batches_IndPenSim_Statistics.csv` | 3.9 KB | 100 | One summary row per batch |

## Schema

**~38 named columns**, then **~2,200 Raman channels.**

The named columns carry their units inside the column name, e.g.
`Aeration rate(Fg:L/h)`, `Temperature(T:K)`, `Penicillin concentration(P:g/L)` —
awkward to type but self-documenting. They cover:

- *Manipulated:* aeration rate, agitator RPM, sugar / acid / base / water feed
  rates, heating & cooling water flow, air head pressure, PAA flow, oil flow
- *Measured online:* substrate & dissolved-oxygen concentration, penicillin
  concentration, vessel volume & weight, pH, temperature, generated heat,
  off-gas CO₂ and O₂, oxygen uptake rate, carbon evolution rate
- *Measured offline:* `PAA_offline`, `NH3_offline`, `P_offline`, `X_offline`
  (biomass), `Viscosity_offline`
- *Reference / metadata:* `Fault reference`, `Control reference`
  (0 = recipe-driven, 1 = operator-controlled), `PAT reference`
  (Raman recording mode), `Batch reference`, `Batch ID`, `Fault flag`

**Raman channels** follow, labelled by wavenumber counting **down** from `2400`
(so column names are bare numbers — pandas will read them as strings).

`100_Batches_IndPenSim_Statistics.csv` gives per-batch outcomes:
`Batch ref`, `Penicllin_harvested_during_batch(kg)`,
`Penicllin_harvested_end_of_batch (kg)`, `Penicllin_yield_total (kg)`,
`Fault ref(0-NoFault 1-Fault)`. (The misspelling "Penicllin" is in the source —
keep it or you will break joins.)

## Notes

- **The offline columns are mostly `NaN` by design.** Offline assays are taken
  a handful of times per batch, not every timestep. This is not dirty data —
  don't drop those rows, and don't impute them without thinking about what an
  offline measurement means.
- Missing values are the literal string `NaN`, which pandas handles, but check
  if you read with anything else.
- **Load only the columns you need.** All 2,239 columns at float64 is far more
  than the 2.4 GB on disk once in memory. If you don't need spectra,
  `pd.read_csv(..., usecols=range(38))` makes this a small dataset.
- **Group by `Batch ID`** for any train/test split — 100 batches is your real
  sample size, not 113,935.
- Batch lengths differ, so batches are not directly stackable into a fixed-shape
  array without padding or resampling.
