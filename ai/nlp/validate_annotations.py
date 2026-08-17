"""
MahaArogya — Annotation Validator
Validates JSONL annotation files against the Phase 6A schema and reports quality statistics.
"""

import json
import sys
from pathlib import Path
from pydantic import ValidationError

# UTF-8 stdout protection
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.nlp.schemas import MedicalAnnotationRecord


def validate_jsonl_file(jsonl_path: Path) -> tuple[int, int, list[str]]:
    """
    Validates a JSONL annotation file.
    
    Returns:
        tuple (valid_count, invalid_count, list_of_errors)
    """
    if not jsonl_path.exists():
        return 0, 0, [f"File not found: {jsonl_path}"]

    valid_count = 0
    invalid_count = 0
    errors = []

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                MedicalAnnotationRecord(**data)
                valid_count += 1
            except json.JSONDecodeError as e:
                invalid_count += 1
                errors.append(f"Line {line_num}: JSON syntax error - {e}")
            except ValidationError as e:
                invalid_count += 1
                errors.append(f"Line {line_num}: Schema validation error - {e}")

    return valid_count, invalid_count, errors


def main():
    annotations_dir = PROJECT_ROOT / "data" / "annotations"
    print(f"\n{'='*60}")
    print("MahaArogya — Annotation Dataset Validation")
    print(f"Directory: {annotations_dir}")
    print(f"{'='*60}\n")

    files = ["train.jsonl", "validation.jsonl", "test.jsonl"]
    total_valid = 0
    total_invalid = 0

    for fname in files:
        fpath = annotations_dir / fname
        valid, invalid, errors = validate_jsonl_file(fpath)
        total_valid += valid
        total_invalid += invalid

        status = "[OK]" if invalid == 0 and valid > 0 else "[WARN]"
        print(f"{status} {fname:<18} | Valid: {valid:<4} | Invalid: {invalid:<4}")

        for err in errors[:5]:
            print(f"    - {err}")

    print(f"\nTotal Valid Records:   {total_valid}")
    print(f"Total Invalid Records: {total_invalid}")


if __name__ == "__main__":
    main()
