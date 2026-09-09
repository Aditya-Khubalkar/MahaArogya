"""
MahaArogya - Synthetic Question Ranking Dataset Generator
Generates high-quality synthetic examples using deterministic state-based logic.
"""

import json
import random
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ai.patient_state.schemas import PatientState, SymptomDetail
from ai.questions.question_bank import get_all_questions

DATA_OUT = ROOT / "data" / "processed" / "question_ranking"
DATA_OUT.mkdir(parents=True, exist_ok=True)

QUESTION_BANK = get_all_questions()
ALL_QID_EN = {q.question_id: q.wording_en for q in QUESTION_BANK}

NUM_NEGATIVES = 5
random.seed(42)

def generate_synthetic_data(num_samples=5000):
    examples = []
    
    # 16 primary symptoms
    symptom_topics = [
        "chest_pain", "breathlessness", "abdominal_pain", "fever", 
        "vomiting", "diarrhea", "headache", "dizziness", "cough", 
        "sore_throat", "burning_urination", "numbness", "joint_pain", 
        "swelling", "fatigue", "nausea"
    ]
    
    # Map questions by topic
    questions_by_topic = {}
    for q in QUESTION_BANK:
        questions_by_topic.setdefault(q.topic, []).append(q)
        
    for i in range(num_samples):
        # Pick 1-3 active symptoms
        num_sym = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        active_syms = random.sample(symptom_topics, num_sym)
        
        state_answers = {}
        symptom_details = {}
        
        # We want the state to be partially complete so there is a specific next question
        # For each active symptom, we might randomly answer some of its questions
        target_question = None
        
        for sym in active_syms:
            symptom_details[sym] = SymptomDetail(present=True, duration=None, severity=None)
            
            # Get related questions
            related_qs = sorted(questions_by_topic.get(sym, []), key=lambda x: x.priority)
            
            # Answer a random prefix of the questions
            # To leave at least one unanswered, pick index 0 to len-1
            num_answered = random.randint(0, max(0, len(related_qs) - 1))
            
            for q in related_qs[:num_answered]:
                state_answers[q.information_collected] = "yes/no/val" # generic answered
                
            # The next unanswered question for this symptom is a candidate for the target
            unanswered = related_qs[num_answered:]
            if unanswered and not target_question:
                target_question = unanswered[0] # Just pick the highest priority unanswered one from the first symptom
                
        if not target_question:
            continue
            
        # Build history string (synthetic)
        history = [f"Patient: I am experiencing {', '.join(active_syms).replace('_', ' ')}."]
        
        # Build state dict for the model format
        extracted_state = {
            "symptoms": active_syms,
            "negated": []
        }
        for k in state_answers:
            extracted_state[f"{k}_status"] = True
            
        # Select negatives
        pool = [qid for qid in ALL_QID_EN.keys() if qid != target_question.question_id]
        negatives = random.sample(pool, min(NUM_NEGATIVES, len(pool)))
        
        example = {
            "dialog_id": f"synthetic_{i:06d}",
            "conversation_history": history,
            "extracted_state": extracted_state,
            "positive_question_id": target_question.question_id,
            "positive_question_en": target_question.wording_en,
            "candidate_question_ids": [target_question.question_id] + negatives,
            "source": "synthetic"
        }
        examples.append(example)
        
    return examples

def split_and_save(examples: list[dict], split_ratios=(0.8, 0.1, 0.1)):
    # Assuming examples are already independent cases
    random.shuffle(examples)
    
    n = len(examples)
    n_train = int(n * split_ratios[0])
    n_val = int(n * split_ratios[1])
    
    splits = {
        "train": examples[:n_train],
        "val": examples[n_train:n_train + n_val],
        "test": examples[n_train + n_val:]
    }
    
    for split_name, split_data in splits.items():
        out_path = DATA_OUT / f"synthetic_{split_name}.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for ex in split_data:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        print(f"  {split_name}: {len(split_data)} examples -> {out_path}")

def main():
    print("Generating synthetic dataset...")
    examples = generate_synthetic_data(5000)
    print(f"Total valid synthetic examples generated: {len(examples)}")
    split_and_save(examples)

if __name__ == "__main__":
    main()
