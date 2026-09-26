# NoBoom — Anomaly Detection in Chemical Processes

Sensor recordings from **real distillation rigs** plus one industrial process,
split into normal training runs and anomalous test runs. The largest and most
interesting dataset in this collection, and the only multi-rig one.

- **Source:** [kaggle.com/datasets/faebs94/noboom-anomaly-detection-in-chemical-processes](https://www.kaggle.com/datasets/faebs94/noboom-anomaly-detection-in-chemical-processes)
- **Licence:** not recorded — verify on the Kaggle page.
- **Nature:** measured from physical laboratory columns (not simulated).
- **Size:** 8.0 GB · 177 CSV files + 148 metadata YAML files

## Layout

```
noboom/
├── <process_family>/
│   ├── FeaturesOverview_*.csv          ← sensor dictionary for this family
│   └── operating_point_NNN/
│       ├── train_normal_experiment_NNN.csv
│       ├── train_normal_experiment_NNN_metadata.yaml
│       └── test_anormal_experiment_NNN.csv
└── cont_single_component_water/versions/1.0.2.txt   ← changelog
```

`train_normal_*` = normal operation (58 files). `test_anormal_*` = contains
anomalies (114 files). Note the source spells it **"anormal"**, not "abnormal" —
glob accordingly.

## The six process families

| Family | Files | Size | Process |
|---|---|---|---|
| `industry_process` | 24 | **7.4 GB** | Industrial plant, 8 numbered units |
| `batch_dist_ternary_butan-1-ol+propan-2-ol+water` | 91 | 77 MB | Batch distillation, ternary mixture |
| `batch_dist_ternary_acetone+butan-1-ol+methanol` | 25 | 14 MB | Batch distillation, ternary mixture |
| `cont_single_component_water` | 12 | 9.2 MB | Continuous column, water only |
| `cont_binary_component_n_butanol` | 16 | 1.7 MB | Continuous column, butanol/water |
| `cont_reactive_ome` | 9 | 740 KB | Continuous reactive distillation (OME) |

## Two different schemas

**Lab rigs** (all families except `industry_process`) — 29 columns:

- `Time` — clock time as `HH:MM:SS`, **not a date**. No day component, so runs
  crossing midnight need care.
- **8 label columns**, giving you a choice of target and difficulty:
  `Label (common/hard fault)`, `(common/soft fault)`, `(common/controller fault)`,
  `(common/hard and soft)`, `(common/all)`, `(advanced/hard fault)`,
  `(advanced/soft fault)`, `(advanced/controller fault)`
- **Sensors:** `T101`–`T116` (temperatures), `PDIC101`–`PDIC103` (differential
  pressure control), `PIC101` (pressure control), `A101`/`M101`–`A103`/`M103`
  (analyser / mass-flow pairs), `R` (reflux ratio).
- `FeaturesOverview_*.csv` in the family folder maps every sensor name to a
  plain-English description. **Read it first** — it is the data dictionary.

**`industry_process`** — 245 columns, completely different and anonymised:

- `Anomaly` (target, float 0.0/1.0), then `F1`–`F68` (flows), `L1`–`L27`
  (levels), `P1`–`P41` (pressures), `T1`–`T71` (temperatures).
- No `FeaturesOverview` file and no units — the sensor meanings are not published.
- Rows end with a trailing comma, so pandas sees a final unnamed empty column.
  Drop it.
- Some test files are split `_a` / `_b` (e.g. `test_anormal_experiment_001_a.csv`);
  these are two parts of one run, not two runs.

## Metadata YAML

Each experiment has a sibling `*_metadata.yaml` recording the operating point —
the conditions that make an "operating point" distinct. Example:

```yaml
Feed in kg/h: '7'
Pressure: '1400.93'
Feed Temperature: '82.65'
Mass Fraction OME: OME1-0.3576 OME2-0.1895 ...
Reflux Ratio: '0.5'
Bottom Flow Rate: '0.59'
```

Values are quoted strings — cast them yourself. These are worth loading as
features, or at minimum as grouping keys, since a model trained on one operating
point will not transfer to another.

## Notes

- **Split by operating point, not by row.** Within one operating point the rows
  are a single continuous run; random splitting leaks.
- `industry_process` is 7.4 GB of the 8.0 GB total. Start with the small lab
  families (`cont_reactive_ome` is 740 KB) to build a pipeline, then scale up.
- Only 58 normal files against 114 anomalous ones — the *file* balance is
  inverted relative to the usual anomaly-detection setup. Check the per-row
  balance before choosing a method.
