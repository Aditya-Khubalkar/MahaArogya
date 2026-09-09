import json
import collections
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "processed" / "question_ranking"

def load_data(split):
    with open(DATA_DIR / f"{split}.jsonl", "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def run_audit():
    train = load_data("train")
    val = load_data("val")
    test = load_data("test")
    all_data = train + val + test
    
    print(f"Total Examples: {len(all_data)}")
    
    q_counts = collections.Counter(ex["positive_question_id"] for ex in all_data)
    print("\nQuestion Distribution (Top 10):")
    for qid, c in q_counts.most_common(10):
        print(f"  {qid}: {c} ({c/len(all_data)*100:.1f}%)")
        
    print("\nQuestion Distribution (Bottom 5):")
    for qid, c in q_counts.most_common()[-5:]:
        print(f"  {qid}: {c} ({c/len(all_data)*100:.1f}%)")
        
    # Domains based on qid prefixes
    domains = collections.Counter(ex["positive_question_id"].split("_")[1] if ex["positive_question_id"].startswith("q_") else "other" for ex in all_data)
    print("\nDomain Distribution (approx based on QID):")
    for d, c in domains.most_common():
        print(f"  {d}: {c} ({c/len(all_data)*100:.1f}%)")

    # Template / Exact match check
    history_strings = collections.Counter(ex["conversation_history"][0] for ex in all_data if ex["conversation_history"])
    print("\nMost Common History Strings (Top 5):")
    for h, c in history_strings.most_common(5):
        print(f"  {h}: {c}")
        
    # Language detection in history (naive)
    langs = collections.Counter()
    for ex in all_data:
        h = " ".join(ex["conversation_history"]).lower()
        if "patient: i am experiencing" in h:
            langs["en_synthetic"] += 1
        elif "ahe" in h or "nahi" in h:
            langs["mr_roman"] += 1
        else:
            langs["other_meditod"] += 1
            
    print("\nDetected Language Distribution:")
    for l, c in langs.most_common():
        print(f"  {l}: {c} ({c/len(all_data)*100:.1f}%)")
        
if __name__ == "__main__":
    run_audit()
