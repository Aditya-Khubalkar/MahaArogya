"""
MahaArogya - Question Ranker Evaluation Script
Evaluates the trained MuRIL ranker on Top-1, Top-3, and MRR metrics.
"""

import json
import pathlib
import sys
import torch
from transformers import AutoTokenizer
from tqdm import tqdm

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ai.questions.ranker import QuestionRanker
from ai.questions.question_bank import get_all_questions

MODEL_NAME = "google/muril-base-cased"
MODEL_PATH = ROOT / "models" / "checkpoints" / "question_ranker" / "best_model.pt"
TEST_DATA = ROOT / "data" / "processed" / "question_ranking" / "test.jsonl"

QUESTION_BANK = {q.question_id: q for q in get_all_questions()}

def main():
    if not MODEL_PATH.exists():
        print(f"Error: Model not found at {MODEL_PATH}")
        sys.exit(1)
        
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading model from {MODEL_PATH} onto {device}...")
    
    model = QuestionRanker.load_from_checkpoint(MODEL_PATH, MODEL_NAME)
    model.to(device)
    model.eval()
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    examples = []
    with open(TEST_DATA, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
                
    print(f"Loaded {len(examples)} test examples.")
    
    top1_hits = 0
    top3_hits = 0
    mrr_sum = 0.0
    
    with torch.no_grad():
        for ex in tqdm(examples, desc="Evaluating"):
            # Format context
            state = ex["extracted_state"]
            state_str = ", ".join(f"{k}: {v}" for k, v in state.items() if v)
            history_str = " | ".join(ex["conversation_history"][-4:])
            context = f"[STATE] {state_str} [HISTORY] {history_str}"
            
            pos_qid = ex["positive_question_id"]
            candidates = list(set(ex.get("candidate_question_ids", [])))
            
            # Ensure positive is in candidates
            if pos_qid not in candidates:
                candidates.append(pos_qid)
                
            scores = []
            for cid in candidates:
                if cid not in QUESTION_BANK:
                    scores.append((cid, -999.0))
                    continue
                
                q_text = QUESTION_BANK[cid].wording_en
                encoding = tokenizer(
                    context,
                    q_text,
                    truncation=True,
                    max_length=256,
                    return_tensors="pt"
                ).to(device)
                
                score = model(encoding["input_ids"], encoding["attention_mask"]).item()
                scores.append((cid, score))
                
            # Sort descending
            scores.sort(key=lambda x: x[1], reverse=True)
            ranked_ids = [s[0] for s in scores]
            
            try:
                rank = ranked_ids.index(pos_qid) + 1
            except ValueError:
                rank = len(ranked_ids) + 1
                
            if rank == 1:
                top1_hits += 1
            if rank <= 3:
                top3_hits += 1
                
            mrr_sum += 1.0 / rank
            
    n = len(examples)
    top1_acc = top1_hits / n
    top3_acc = top3_hits / n
    mrr = mrr_sum / n
    
    print("\n--- Evaluation Results ---")
    print(f"Total Examples: {n}")
    print(f"Top-1 Accuracy: {top1_acc:.4f} (Target: >0.50)")
    print(f"Top-3 Accuracy: {top3_acc:.4f} (Target: >0.70)")
    print(f"MRR           : {mrr:.4f} (Target: >0.60)")
    
    if top1_acc > 0.50 and top3_acc > 0.70 and mrr > 0.60:
        print("\nSUCCESS: Model meets all evaluation targets!")
    else:
        print("\nWARNING: Model did not meet all evaluation targets.")

if __name__ == "__main__":
    main()
