"""Download the Kaggle datasets for this project into ./data/.

Requires a Kaggle API token (~/.kaggle/kaggle.json or the KAGGLE_USERNAME /
KAGGLE_KEY environment variables). Roughly 15 GB total.

Safe to re-run: any dataset folder that already exists is skipped.

NOT handled here: IndPenSim (penicillin fermentation) is hosted on Mendeley
Data, not Kaggle, and must be downloaded manually -- see
data/indpensim-penicillin-fermentation/README.md

See docs/DATASETS.md for what each dataset contains.
"""

import os
import shutil
import sys

import kagglehub

# Kaggle dataset handles, as "owner/dataset-slug".
# Each lands in data/<dataset-slug>/.
DATASETS = [
    "nikitamanaenkov/time-series-of-industrial-boiler-operations",
    "afrniomelo/tep-csv",
    "faebs94/noboom-anomaly-detection-in-chemical-processes",
    "gagandeepgambhir2/industrial-iot-predictive-maintenance-pdm",
    "mobeenfatimah/smart-factory-predictive-maintenance-dataset",
    "fdavidsantillan/shell-and-tube-heat-exchanger-fouling-simulation",
    "ishanpradhan95/industrial-pump-physics-grounded-digital-twin",
    "rohit8527kmr7518/chemical-process-monitoring-time-series-dataset",
    "drsayed/industrial-control-valve-sensor-data",
    "colabsss/industrial-sensor-anomaly-detection-dataset",
    "joebeachcapital/metropt-3-dataset",
    "masoudfazli/petrochemical-process-optimization-and-maintenance",
    "aimindteams/batch-reactor-anomaly-data-sample",
    "drsayed/pump-station-sensor-data",
    "drsayed/heat-exchanger-fouling-sensor",
]

# Datasets that must be fetched by hand, and where from.
MANUAL = {
    "indpensim-penicillin-fermentation": "Mendeley Data -- search 'IndPenSim 100 batches'",
}

TARGET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def main() -> int:
    os.makedirs(TARGET_DIR, exist_ok=True)

    downloaded, skipped, failed = [], [], []

    for i, handle in enumerate(sorted(set(DATASETS)), start=1):
        slug = handle.split("/")[-1]
        dest = os.path.join(TARGET_DIR, slug)

        # A folder holding only our README.md counts as not-yet-downloaded.
        existing = os.path.isdir(dest) and set(os.listdir(dest)) - {"README.md"}
        if existing:
            print(f"[{i}/{len(set(DATASETS))}] {slug}: already present, skipping")
            skipped.append(slug)
            continue

        print(f"[{i}/{len(set(DATASETS))}] {slug}: downloading...")
        try:
            cache_path = kagglehub.dataset_download(handle)
        except Exception as exc:
            print(f"    FAILED: {exc}")
            failed.append((slug, str(exc)))
            continue

        # Copy out of the kagglehub cache, preserving our README.md if present.
        os.makedirs(dest, exist_ok=True)
        shutil.copytree(cache_path, dest, dirs_exist_ok=True)
        print(f"    -> {dest}")
        downloaded.append(slug)

    print("\n" + "=" * 60)
    print(f"downloaded: {len(downloaded)}   skipped: {len(skipped)}   failed: {len(failed)}")
    for slug, exc in failed:
        print(f"  FAILED  {slug}: {exc}")
    if MANUAL:
        print("\nManual downloads still required:")
        for slug, where in MANUAL.items():
            present = os.path.isdir(os.path.join(TARGET_DIR, slug)) and (
                set(os.listdir(os.path.join(TARGET_DIR, slug))) - {"README.md"}
            )
            mark = "present" if present else "MISSING"
            print(f"  [{mark}] {slug} -- {where}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
