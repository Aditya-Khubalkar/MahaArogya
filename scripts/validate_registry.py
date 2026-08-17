"""
MahaArogya — Source Registry Validator
Validates data/source_registry.csv for completeness, schema integrity, and license metadata per Spec Section 3.
"""

import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def validate_registry():
    registry_path = Path("data/source_registry.csv")
    if not registry_path.exists():
        print("  [FAIL]: data/source_registry.csv does not exist!")
        return False
        
    required_columns = [
        "dataset_name", "source_url", "license",
        "language", "modality", "date_acquired", "notes"
    ]
    
    with open(registry_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        
        for col in required_columns:
            if col not in fieldnames:
                print(f"  [FAIL]: Missing required column '{col}' in source_registry.csv")
                return False
                
        rows = list(reader)
        print(f"  [OK] Registry file found with {len(rows)} dataset entries.")
        
        valid_count = 0
        for i, row in enumerate(rows, 1):
            name = row.get("dataset_name", "").strip()
            url = row.get("source_url", "").strip()
            lic = row.get("license", "").strip()
            lang = row.get("language", "").strip()
            modality = row.get("modality", "").strip()
            
            if not name or not url or not lic or not lang or not modality:
                print(f"  [WARN] Row {i} has incomplete metadata: {row}")
            else:
                valid_count += 1
                
        print(f"  [OK] {valid_count} / {len(rows)} dataset entries fully validated.")
        return True


if __name__ == "__main__":
    validate_registry()
