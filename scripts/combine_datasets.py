import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "processed" / "question_ranking"

def combine():
    for split in ["train", "val", "test"]:
        meditod_path = DATA_DIR / f"meditod_{split}.jsonl"
        synthetic_path = DATA_DIR / f"synthetic_{split}.jsonl"
        out_path = DATA_DIR / f"{split}.jsonl"
        
        combined_lines = []
        if meditod_path.exists():
            with open(meditod_path, "r", encoding="utf-8") as f:
                combined_lines.extend(f.readlines())
        if synthetic_path.exists():
            with open(synthetic_path, "r", encoding="utf-8") as f:
                combined_lines.extend(f.readlines())
                
        with open(out_path, "w", encoding="utf-8") as f:
            for line in combined_lines:
                f.write(line)
                
        print(f"Combined {split}.jsonl: {len(combined_lines)} lines")

if __name__ == "__main__":
    combine()
