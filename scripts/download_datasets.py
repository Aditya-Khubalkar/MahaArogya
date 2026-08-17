"""
MahaArogya — Phase 3 Dataset Downloader
Downloads priority datasets to data/raw/ and updates source_registry.csv dates.

Usage:
    python scripts/download_datasets.py --dataset <name>
    python scripts/download_datasets.py --all-ungated
"""

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

# Reconfigure stdout/stderr to UTF-8 for Windows console safety
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(r"C:\MahaArogya")
DATA_RAW = PROJECT_ROOT / "data" / "raw"
REGISTRY_PATH = PROJECT_ROOT / "data" / "source_registry.csv"


def update_registry_date(dataset_name: str):
    """Update the date_acquired field in source_registry.csv for a dataset."""
    rows = []
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row["dataset_name"] == dataset_name:
                row["date_acquired"] = datetime.now().strftime("%Y-%m-%d")
            rows.append(row)

    with open(REGISTRY_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [OK] Updated source_registry.csv for '{dataset_name}'")


def download_symptom_to_diagnosis():
    """Download gretelai/symptom_to_diagnosis from Hugging Face (Apache-2.0, ~218KB)."""
    name = "Symptom-to-Diagnosis"
    dest = DATA_RAW / "symptom_to_diagnosis"
    dest.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Downloading: {name}")
    print(f"Source: huggingface.co/datasets/gretelai/symptom_to_diagnosis")
    print(f"License: Apache-2.0")
    print(f"Destination: {dest}")
    print(f"{'='*60}")

    from datasets import load_dataset

    ds = load_dataset("gretelai/symptom_to_diagnosis")

    # Save as CSV for easy inspection
    for split_name, split_data in ds.items():
        out_path = dest / f"{split_name}.csv"
        split_data.to_csv(str(out_path), index=False)
        print(f"  [OK] Saved {split_name}: {len(split_data)} rows -> {out_path.name}")

    update_registry_date(name)
    print(f"  [OK] {name} download complete.\n")


def download_bc5cdr():
    """Download BC5CDR from Hugging Face (Public Domain, biomedical NER)."""
    name = "BC5CDR"
    dest = DATA_RAW / "bc5cdr"
    dest.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Downloading: {name}")
    print(f"Source: huggingface.co/datasets/bigbio/bc5cdr")
    print(f"License: Public Domain")
    print(f"Destination: {dest}")
    print(f"{'='*60}")

    from datasets import load_dataset

    ds = load_dataset("bigbio/bc5cdr", "bc5cdr_bigbio_kb", trust_remote_code=True)

    for split_name, split_data in ds.items():
        out_path = dest / f"{split_name}.json"
        split_data.to_json(str(out_path))
        print(f"  [OK] Saved {split_name}: {len(split_data)} documents -> {out_path.name}")

    update_registry_date(name)
    print(f"  [OK] {name} download complete.\n")


def download_ncbi_disease():
    """Download NCBI Disease corpus from Hugging Face (Public Domain, disease NER)."""
    name = "NCBI Disease Corpus"
    dest = DATA_RAW / "ncbi_disease"
    dest.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Downloading: {name}")
    print(f"Source: huggingface.co/datasets/ncbi/ncbi_disease")
    print(f"License: Public Domain (NIH)")
    print(f"Destination: {dest}")
    print(f"{'='*60}")

    from datasets import load_dataset

    ds = load_dataset("ncbi/ncbi_disease", trust_remote_code=True)

    for split_name, split_data in ds.items():
        out_path = dest / f"{split_name}.json"
        split_data.to_json(str(out_path))
        print(f"  [OK] Saved {split_name}: {len(split_data)} documents -> {out_path.name}")

    update_registry_date(name)
    print(f"  [OK] {name} download complete.\n")


def download_medquad():
    """Clone MedQuAD from GitHub (CC-BY-4.0, medical QA pairs)."""
    name = "MedQuAD"
    dest = DATA_RAW / "medquad"

    print(f"\n{'='*60}")
    print(f"Downloading: {name}")
    print(f"Source: github.com/abachaa/MedQuAD")
    print(f"License: CC-BY-4.0")
    print(f"Destination: {dest}")
    print(f"{'='*60}")

    if dest.exists():
        print(f"  [WARN] Directory already exists, skipping clone.")
    else:
        import subprocess
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/abachaa/MedQuAD.git", str(dest)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  [FAIL] Git clone failed: {result.stderr}")
            return
        print(f"  [OK] Cloned MedQuAD repository.")

    update_registry_date(name)
    print(f"  [OK] {name} download complete.\n")


DATASET_FUNCTIONS = {
    "symptom_to_diagnosis": download_symptom_to_diagnosis,
    "bc5cdr": download_bc5cdr,
    "ncbi_disease": download_ncbi_disease,
    "medquad": download_medquad,
}

UNGATED_DATASETS = ["symptom_to_diagnosis", "bc5cdr", "ncbi_disease", "medquad"]


def main():
    parser = argparse.ArgumentParser(description="MahaArogya Dataset Downloader")
    parser.add_argument("--dataset", choices=list(DATASET_FUNCTIONS.keys()),
                        help="Download a specific dataset")
    parser.add_argument("--all-ungated", action="store_true",
                        help="Download all datasets that don't require HF authentication")
    args = parser.parse_args()

    if args.all_ungated:
        print("Downloading all ungated datasets...")
        for ds_name in UNGATED_DATASETS:
            try:
                DATASET_FUNCTIONS[ds_name]()
            except Exception as e:
                print(f"  [FAIL] Failed to download {ds_name}: {e}")
    elif args.dataset:
        try:
            DATASET_FUNCTIONS[args.dataset]()
        except Exception as e:
            print(f"  [FAIL] Failed to download {args.dataset}: {e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
