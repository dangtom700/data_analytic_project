# Tennessee Eastman Process (CSV)

The reference benchmark for chemical-process fault detection. A simulated
plant producing two products from four reactants, with 20 pre-defined fault
modes injected into the simulation.

- **Source:** [kaggle.com/datasets/afrniomelo/tep-csv](https://www.kaggle.com/datasets/afrniomelo/tep-csv)
- **Original:** Downs & Vogel (1993) benchmark. These CSVs are a conversion of
  the extended simulation set by Rieth et al. (2017), *Additional Tennessee
  Eastman Process Simulation Data for Anomaly Detection Evaluation*, Harvard
  Dataverse.
- **Licence:** not recorded — verify on the Kaggle page before any publication.
- **Nature:** simulated (but the canonical, peer-reviewed simulator).
- **Size:** 5.7 GB across 4 files · 15,330,000 rows total · 55 columns · LF endings

## Files

| File | Size | Rows | Structure |
|---|---|---|---|
| `TEP_FaultFree_Training.csv` | 90 MB | 250,000 | 500 runs × 500 samples |
| `TEP_FaultFree_Testing.csv` | 172 MB | 480,000 | 500 runs × 960 samples |
| `TEP_Faulty_Training.csv` | 1.8 GB | 5,000,000 | 20 faults × 500 runs × 500 samples |
| `TEP_Faulty_Testing.csv` | 3.4 GB | 9,600,000 | 20 faults × 500 runs × 960 samples |

Row counts are exact and factor cleanly, which is a good integrity check.

## Schema (identical in all four files)

| Column | Meaning |
|---|---|
| `faultNumber` | 0 = fault-free, 1–20 = fault mode. The classification target. |
| `simulationRun` | Run id, 1–500. **Group by this when splitting** — samples within a run are not independent. |
| `sample` | Sample index within the run. 3-minute intervals. |
| `xmeas_1` … `xmeas_41` | 41 measured process variables (flows, temperatures, pressures, compositions). |
| `xmv_1` … `xmv_11` | 11 manipulated variables (valve positions / controller outputs). |

## Notes

- **Fault onset is not at sample 1.** In the training files the fault starts
  after sample 20; in the testing files after sample 160. Rows before onset are
  normal operation even though `faultNumber` is non-zero — label them by
  timestamp, not by file.
- Faults 3, 9 and 15 are famously near-undetectable; most published results
  exclude them. If your accuracy is suspiciously low, check whether those are in
  your subset.
- `TEP_Faulty_Testing.csv` is 3.4 GB — read it in chunks
  (`pd.read_csv(..., chunksize=...)`) or convert to Parquet once and work from that.
- No missing values.
