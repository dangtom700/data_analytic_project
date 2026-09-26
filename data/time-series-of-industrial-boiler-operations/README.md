# Industrial Boiler Operations — Time Series

**Real**, peer-reviewed sensor data from an industrial boiler, published as a
*Scientific Data* descriptor. Comes with a proper data dictionary, which makes it
the best-documented dataset in this collection.

- **Source:** [kaggle.com/datasets/nikitamanaenkov/time-series-of-industrial-boiler-operations](https://www.kaggle.com/datasets/nikitamanaenkov/time-series-of-industrial-boiler-operations)
- **Original:** Nature *Scientific Data* (2025), "A long-tailed distribution
  time-series dataset in boiler equipment" — [doi:10.1038/s41597-025-05096-4](https://www.nature.com/articles/s41597-025-05096-4)
- **Licence:** not recorded on Kaggle — the *Scientific Data* record is the
  authority; cite the paper if you publish.
- **Nature:** **measured on real equipment.**
- **Size:** 39 MB · 86,400 rows per file · 31 columns
- **Span:** 2022-03-27 14:28:54 → 2022-04-01 14:28:49 (5 days at 5 s intervals)

## Files

| File | Rows | Empty cells | Notes |
|---|---|---|---|
| `data.csv` | 86,400 | **30** | The raw data |
| `data_AutoReg.csv` | 86,400 | **0** | Same data with those 30 gaps filled |
| `columns.csv` | 30 | — | **Data dictionary — sensor tag → description** |
| `41597_2025_5096_Fig3_HTML.png` | — | — | Figure 3 from the paper (boiler process diagram) |

The two data files differ on exactly 30 lines. `data.csv` has 30 empty cells;
`data_AutoReg.csv` has none. So `data_AutoReg` is the autoregression-imputed
version — **use `data.csv` if you want to handle the gaps yourself**, which for
30 cells out of 2.6 M is trivially done and more honest than inheriting someone
else's imputation.

## Schema

Columns are DCS tags of the form `TE_8319A.AV_0#`. `columns.csv` maps each to a
description; the prefix tells you the instrument type:

| Prefix | Instrument | Examples |
|---|---|---|
| `PT_` | Pressure transmitter | `PT_8313A`–`PT_8313F` — upper furnace pressure, 6 locations |
| `PTCA_` | Pressure (vapour/pot) | `PTCA_8324` outlet vapour pressure, `PTCA_8322A` pot pressure |
| `TE_` | Temperature element | economizer outlet flue gas, furnace chamber, air preheaters, boiler outlet steam |
| `TV_` | Control valve | `TV_8329ZC` desuperheater steam temperature valve |
| `FT_` | Flow transmitter | primary/secondary fan outlet, return air chamber |
| `AIR_` | Flue gas oxygen | `AIR_8301A/B` upper economiser inlet O₂ |
| `YFJ3_` | Induced draft fan | motor current, bearing shell vibration (A/B) |
| *(pinyin codes)* | Differential pressures & flows | `SXLTCYZ/Y`, `ZCLCCY`, `YCLCCY`, `YJJWSLL`, `ZZQBCHLL` |

`date` is the timestamp column.

## Notes

- **Unlabelled.** There is no fault column — the paper's framing is the
  *long-tailed distribution* of operating states. Treat it as unsupervised
  (anomaly / regime detection) or forecast one tag from the others.
- Several pressure readings are legitimately **negative** (furnace draft is below
  atmospheric). Don't "clean" those away.
- Sensors come in left/right or A–F pairs across the furnace. Those are
  physically redundant and strongly correlated — expect trouble from any method
  assuming independent features, and consider averaging them.
- The pinyin-derived tag names are decoded in `columns.csv`; nowhere else.
