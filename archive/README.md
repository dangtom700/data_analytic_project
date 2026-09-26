# Archive — Completed Analyses

12 finished analyses, each self-contained in its own folder: the notebook, a
rendered HTML export where one exists, and the submitted PDF report for
coursework.

**These predate the `data/` collection.** None of them read from `data/` — they
load their own data inline, from Kaggle directly, or from a file that was never
committed. So a notebook may not re-run as-is; treat these as **finished work and
worked examples**, not a live pipeline.

Folder names are kept as they were, including the ones with spaces. Quote paths
in scripts: `"archive/report - defect analysis/"`.

---

## MSE 413 coursework

The four labs and the final project from *Introduction to Machine Learning in
Mechatronics* ([course notes](../docs/ml-course-notes.md)). Each lab folder has
the assignment brief and/or the graded report PDF alongside the notebooks.

### `lab1/` — Regression

End-to-end regression, the first full pipeline.

| Notebook | Covers |
|---|---|
| `California_housing.ipynb` | "Lab1: End-to-end ML regression" — the canonical walkthrough |
| `lab1_data_discovery.ipynb` | EDA, concatenating and saving the dataset |
| `lab1_simple_linear_regression.ipynb` | Single-feature baseline, feature candidate selection |
| `lab1_multiple_linear_regression.ipynb` | Top-4 features per target by absolute correlation |
| `lab1_polynomial_regression.ipynb` | Degrees 2, 3 and 5 compared |

Reports: `MSE 413 Lab 1 Report - Tom Dang.pdf`
· *`MSE413_lab1_Tom_Dang.zip` (submission bundle, git-ignored)*

### `lab2/` — Classification

Five classifiers on a robot dataset, plus a separate binary task.

| Notebook | Covers |
|---|---|
| `MSE413_Lab2_Binary_Classification.ipynb` | Binary classification, comparing data-cleaning strategies |
| `MSE413_Lab2_Multiclass_Classification.ipynb` | Multiclass on the robot data |
| `MSE413_KNN_Classification.ipynb` | k-nearest neighbours |
| `MSE413_SVM_Classification.ipynb` | Support vector machines |
| `MSE413_Lab2_Random_Forest_Classifier.ipynb` | Random forest |

Reports: `MSE 413 Lab 2 Report.pdf`, `MSE413_Lab2_Assignment_2025.pdf` (brief)

### `lab3/` — Unsupervised learning

| Notebook | Covers |
|---|---|
| `MSE413_K_clustering.ipynb` | k-means / k-medoids (`scikit-learn-extra`) |
| `MSE413_inertia_silhouette.ipynb` | Choosing k by inertia and silhouette score |
| `MSE413_PCA_dimension_reduce.ipynb` | PCA dimensionality reduction |
| `MSE413_semi_supervised.ipynb` | Semi-supervised learning with partially missing labels |

Reports: `MSE413_Lab3_Report.pdf`
· *`MSE413_lab3_report_Tom_Dang.zip` (74 MB submission bundle, git-ignored)*

**Needs `scikit-learn-extra`** — not in `environment.yml`.

### `lab4/` — Deep learning

`MSE 413 Lab 4 Part 1-4.ipynb` — image classification with Keras, using
`image_dataset_from_directory`; reports dataset sizes, class information and
image shapes.

Reports: `MSE 413 Lab 4.pdf` · *`MSE413_Lab4.zip` (git-ignored)*

**Needs `tensorflow`** — not in `environment.yml`.

### `MSE413_project/` — Final project

`final_project.ipynb` — facial emotion recognition from images. Uses `opencv`,
`dlib` (facial landmarks) and `kagglehub` to pull the image data at runtime.

Reports: `MSE 413 Project Proposal.pdf`, `MSE 413 Final Project.pdf`

**Needs `opencv` and `dlib`** — neither is in `environment.yml`, and `dlib`
usually needs a compiler toolchain to install.

---

## Independent analyses

### `crime_rate/` — Crime vs socioeconomic factors

`crime_socioeconomic_analysis.ipynb` — the most thorough analysis here: dataset
framing, EDA, then modelling. Has its own `requirement.yml`. Rendered to
`crime_socioeconomic_analysis.html`.

### `report - intelligent streetlight/` — Intelligent streetlight control

`intelligent_streetlight.ipynb` + rendered report HTML. Time-series work using
`statsmodels` — the only analysis here that does classical statistical
modelling rather than scikit-learn.

### `report - defect analysis/` — Manufacturing defect analysis

`defect_analysis.ipynb` + `Defect Analysis Report.html`. Defect-rate analysis
with scikit-learn. Closest in subject matter to the `data/` collection.

### `text_analysis/` — Fuzzy text matching

Not a notebook-only folder — this one has working scripts:

| File | Purpose |
|---|---|
| `fuzzy.ipynb` | Fuzzy matching experiments (`scipy`, `sqlite3`) |
| `db2csv.py` | Exports a SQLite database to CSV |
| `export_item_matrix.py` | Builds an item matrix |
| `environment.yml` | Its own environment |

Reads from a SQLite `.db` file that is git-ignored and not present.

### `sale_data_visualization/` — Sales visualisation

`sales_data_visualization.ipynb` + rendered HTML. Pure
pandas/matplotlib/seaborn — no modelling. Useful as a plotting reference.

### `iris/` — Iris classification

`iris_data_analysis.ipynb` + rendered HTML. The classic dataset: 80/20 split,
MinMax scaling, classification. The simplest complete example here.

### `simple signal/` — Signal processing

`main.ipynb` — loads a CSV signal, 60/40 split, basic modelling. The least
developed folder; no report.

---

## Notes

- **Rendered HTML exports are large** (the streetlight one is 15 MB) because they
  embed every plot as base64. They are tracked in git, which is why `.git` is
  170 MB. Worth reconsidering if the repo needs to stay lean.
- **Submission `.zip` bundles are git-ignored** (`archive/**/*.zip`, ~92 MB
  total). They duplicate the extracted work already in these folders, but are
  kept on disk as the record of what was actually submitted.
- `environment.yml` at the repo root does **not** cover `tensorflow`,
  `scikit-learn-extra`, `opencv` or `dlib`. Labs 3 and 4 and the final project
  each need extra installs.
