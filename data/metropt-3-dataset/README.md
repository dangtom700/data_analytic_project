# MetroPT-3 — Metro Train Air Compressor

**Real** sensor readings from the Air Production Unit (APU) of a metro train
compressor, recorded over seven months of service. One of the few genuinely
measured datasets in this collection — and therefore the one worth trusting.

- **Source:** [kaggle.com/datasets/joebeachcapital/metropt-3-dataset](https://www.kaggle.com/datasets/joebeachcapital/metropt-3-dataset)
- **Original:** MetroPT-3, Veloso et al. — also on the UCI ML Repository.
- **Licence:** not recorded — verify on the Kaggle page. The upstream UCI record
  is CC BY 4.0.
- **Nature:** **measured on real equipment.**
- **Size:** 209 MB · 1,516,948 rows · 17 columns
- **Span:** 2020-02-01 00:00:00 → 2020-09-01 03:59:50 (~213 days)

## Files

- `MetroPT3(AirCompressor).csv` — the time series
- `Data Description_Metro.pdf` — **the official sensor documentation. Read it.**

## Schema

| Column | Type | Meaning |
|---|---|---|
| *(unnamed first column)* | int | A leftover pandas index. **Drop it** — `index_col=0`. |
| `timestamp` | datetime | Reading time |
| `TP2` | analogue | Compressor pressure |
| `TP3` | analogue | Pneumatic panel pressure |
| `H1` | analogue | Pressure drop across the cyclonic separator |
| `DV_pressure` | analogue | Pressure drop from air-dryer discharge |
| `Reservoirs` | analogue | Downstream reservoir pressure |
| `Oil_temperature` | analogue | Compressor oil temperature |
| `Motor_current` | analogue | Motor phase current |
| `COMP` | digital | Air-intake valve signal |
| `DV_eletric` | digital | Compressor outlet valve *(source spelling — keep it)* |
| `Towers` | digital | Which drying tower is active |
| `MPG` | digital | Intake-valve trigger |
| `LPS` | digital | Low-pressure signal |
| `Pressure_switch` | digital | Air-dryer discharge detection |
| `Oil_level` | digital | Oil-level low signal |
| `Caudal_impulses` | digital | Air-flow pulse counter |

## Notes

- **No label column.** Failure periods are described in the accompanying PDF and
  the source paper as date ranges — you must construct the target yourself by
  marking those windows. This is the single most important thing to know about
  this dataset.
- Sampling is nominally 1 Hz but **irregular with gaps**; 213 days at 1 Hz would
  be ~18 M rows, not 1.5 M. Resample rather than assuming a fixed step.
- Analogue and digital columns want different treatment — the digital ones are
  0/1 state flags, not continuous signals to be scaled.
- Being real data, it has real-world messiness (drift, sensor dropouts). That is
  the point of using it.
