# Industrial Data Analytics

A working collection of **16 industrial process & predictive-maintenance datasets**
(~17 GB) together with the completed data-analysis notebooks built from them.

The theme is industrial condition monitoring: fault detection, anomaly detection
and remaining-useful-life estimation on chemical reactors, distillation columns,
heat exchangers, pumps, valves, boilers and factory machinery.

| | |
|---|---|
| **Datasets** | 16 (15 Kaggle + 1 Mendeley) · ~17 GB on disk · **not in git** |
| **Completed analyses** | 12, in [`archive/`](archive/) |
| **Catalogue** | [`docs/DATASETS.md`](docs/DATASETS.md) — source, licence, schema, quirks |
| **Course notes** | [`docs/ml-course-notes.md`](docs/ml-course-notes.md) |

---

## Quick start

```bash
# 1. Environment
conda env create -f environment.yml
conda activate data_science

# 2. Datasets (~15 GB download, needs a Kaggle API token)
python data_download.py
```

`data_download.py` pulls the 15 Kaggle datasets into `data/<dataset-slug>/` via
`kagglehub`. It skips any folder that already exists, so it is safe to re-run.

**One dataset needs a manual download** — IndPenSim (penicillin fermentation) is
hosted on Mendeley Data, not Kaggle. See
[`data/indpensim-penicillin-fermentation/README.md`](data/indpensim-penicillin-fermentation/README.md).

> `environment.yml` is a full conda export from **Windows / Python 3.14** and
> pins exact build strings, so it will not solve on macOS or Linux. On another
> platform install the essentials instead:
> `pandas numpy scipy scikit-learn matplotlib seaborn statsmodels jupyter tabulate`
> (plus `tensorflow` for `archive/lab4`, `scikit-learn-extra` for `archive/lab3`,
> `opencv` + `dlib` for `archive/MSE413_project`).

---

## Layout

```
data_analytic_project/
├── data/                  16 datasets, one folder each, git-ignored
│   └── <dataset>/README.md    ← the only tracked files in here
├── archive/               12 completed analyses (notebooks + reports)
├── docs/
│   ├── DATASETS.md            full data catalogue
│   └── ml-course-notes.md     MSE 413 study notes
├── awesome-industrial-datasets-master/   third-party catalogue, git-ignored
├── data_download.py       Kaggle fetch script
└── environment.yml        conda environment (Windows)
```

### Why the data isn't in git

At ~17 GB the datasets are far larger than a git repo should carry, and every
one of them is re-downloadable from its source. `.gitignore` excludes everything
under `data/` **except** each dataset's `README.md` — so the documentation
travels with the repo while the bytes do not.

If you clone this repo fresh, `data/` will contain only those README files until
you run `data_download.py`.

### `awesome-industrial-datasets-master/`

A clone of [awesome-industrial-datasets](https://github.com/dalmia/awesome-industrial-datasets)
— 190 industrial datasets described in JSON and Markdown, plus a taxonomy. Kept
as a reference for finding *more* data; nothing here depends on it, and it is
git-ignored because it is someone else's repository.

---

## The datasets

Full detail — row counts, every column, licences, known data-quality problems —
lives in **[`docs/DATASETS.md`](docs/DATASETS.md)**. Summary:

| Dataset | Size | Rows | Task |
|---|---|---|---|
| [`tep-csv`](data/tep-csv/README.md) | 5.7 GB | 15.3 M | Tennessee Eastman process — 20-fault classification |
| [`noboom-…-chemical-processes`](data/noboom-anomaly-detection-in-chemical-processes/README.md) | 8.0 GB | 177 files | Distillation column anomaly detection, real rigs |
| [`indpensim-penicillin-fermentation`](data/indpensim-penicillin-fermentation/README.md) | 2.4 GB | 113,935 | Batch fermentation + Raman spectra |
| [`metropt-3-dataset`](data/metropt-3-dataset/README.md) | 209 MB | 1.52 M | Metro train air compressor failures (real) |
| [`chemical-process-monitoring-…`](data/chemical-process-monitoring-time-series-dataset/README.md) | 201 MB | 777,600 | Reactor fault type + time-to-fault |
| [`shell-and-tube-heat-exchanger-…`](data/shell-and-tube-heat-exchanger-fouling-simulation/README.md) | 167 MB | 700,800 | Heat exchanger fouling regression |
| [`industrial-pump-…-digital-twin`](data/industrial-pump-physics-grounded-digital-twin/README.md) | 116 MB | 379,786 | Pump RUL + failure probability |
| [`industrial-control-valve-sensor-data`](data/industrial-control-valve-sensor-data/README.md) | 76 MB | 200,000 | Valve failure classification |
| [`smart-factory-predictive-maintenance`](data/smart-factory-predictive-maintenance-dataset/README.md) | 41 MB | 100,000 | Machine failure + failure type (72 cols) |
| [`time-series-of-industrial-boiler-…`](data/time-series-of-industrial-boiler-operations/README.md) | 39 MB | 86,400 ×2 | Boiler sensor time series (real, published) |
| [`pump-station-sensor-data`](data/pump-station-sensor-data/README.md) | 17 MB | 100,000 | Pump efficiency regression |
| [`heat-exchanger-fouling-sensor`](data/heat-exchanger-fouling-sensor/README.md) | 7.3 MB | 40,267 | Fouling detection (balanced 50/50) |
| [`industrial-iot-predictive-maintenance-pdm`](data/industrial-iot-predictive-maintenance-pdm/README.md) | 3.6 MB | 36,000 | 3-class machine status |
| [`petrochemical-process-optimization-…`](data/petrochemical-process-optimization-and-maintenance/README.md) | 2.7 MB | 10,000 | Yield / energy-intensity regression |
| [`industrial-sensor-anomaly-detection`](data/industrial-sensor-anomaly-detection-dataset/README.md) | 2.2 MB | 1,000 + 500 | SWaT / WADI samples (tiny, pre-scaled) |
| [`batch-reactor-anomaly-data-sample`](data/batch-reactor-anomaly-data-sample/README.md) | 156 KB | 4,901 | Batch reactor EDA sample |

**Most of these are synthetic.** Only MetroPT-3, the industrial boiler data, the
NoBoom distillation rigs and IndPenSim are measured or published-simulator data.
The rest are generated Kaggle datasets — fine for practising a pipeline,
not for claiming a result about real equipment. `docs/DATASETS.md` marks each one.

---

## Completed analyses

12 finished analyses live in [`archive/`](archive/) — see
[`archive/README.md`](archive/README.md) for what each one covers. They are
self-contained: notebook, rendered HTML and (for coursework) the submitted PDF
report. None of them read from `data/`; they predate this dataset collection and
load their own data inline or from Kaggle directly.

## Conventions

- One dataset per folder under `data/`, named for its Kaggle slug.
- Every dataset folder has a `README.md`: source URL, licence, size, schema,
  and any data-quality traps found while profiling it.
- Analyses are self-contained folders under `archive/`.
- Data files are never committed. Documentation always is.
