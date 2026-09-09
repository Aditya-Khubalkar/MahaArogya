import json
import collections
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "processed" / "question_ranking"

def load_data(split):
    with open(DATA_DIR / f"{split}.jsonl", "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def run_analysis():
    train = load_data("train")
    val = load_data("val")
    test = load_data("test")

    all_data = train + val + test
    
    print(f"Total examples: {len(all_data)}")
    print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

    # 1. Source representation
    sources = collections.Counter(ex["source"] for ex in all_data)
    print("\nSources:", sources)
    print("Train sources:", collections.Counter(ex["source"] for ex in train))
    print("Val sources:", collections.Counter(ex["source"] for ex in val))
    print("Test sources:", collections.Counter(ex["source"] for ex in test))

    # 2. Conversation IDs and Leakage
    def get_base(ex):
        return ex["dialog_id"].split("_turn_")[0]

    train_bases = set(get_base(ex) for ex in train)
    val_bases = set(get_base(ex) for ex in val)
    test_bases = set(get_base(ex) for ex in test)

    print("\nLeakage Check (Conversation ID overlap):")
    print("Train vs Val intersection:", len(train_bases.intersection(val_bases)))
    print("Train vs Test intersection:", len(train_bases.intersection(test_bases)))
    print("Val vs Test intersection:", len(val_bases.intersection(test_bases)))

    # 3. Duplicate contexts/questions
    def get_context(ex):
        state_str = ", ".join(f"{k}: {v}" for k, v in ex["extracted_state"].items() if v)
        history_str = " | ".join(ex["conversation_history"][-4:])
        # Just use state and history as a unique signature of the context
        return f"[STATE] {state_str} [HISTORY] {history_str}"

    train_contexts = set(get_context(ex) for ex in train)
    val_contexts = set(get_context(ex) for ex in val)
    test_contexts = set(get_context(ex) for ex in test)
    
    print("\nDuplicate Contexts across splits:")
    print("Train vs Val exact contexts overlap:", len(train_contexts.intersection(val_contexts)))
    print("Train vs Test exact contexts overlap:", len(train_contexts.intersection(test_contexts)))
    print("Val vs Test exact contexts overlap:", len(val_contexts.intersection(test_contexts)))

    # Analyze duplicates within train
    context_counts = collections.Counter(get_context(ex) for ex in train)
    duplicates = sum(1 for c, v in context_counts.items() if v > 1)
    print(f"Duplicate exact contexts within train: {duplicates}")

if __name__ == "__main__":
    run_analysis()
