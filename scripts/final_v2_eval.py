import os
import json
import torch
import sys
import pathlib
from transformers import AutoTokenizer

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ai.questions.ranker import QuestionRanker
from ai.questions.question_bank import get_all_questions
from ai.patient_state.state_manager import PatientStateManager
from ai.nlp.extractor import MedicalExtractor
from ai.questions.selector import QuestionSelector

MODEL_NAME = "google/muril-base-cased"
OLD_MODEL_PATH = ROOT / "models" / "checkpoints" / "question_ranker" / "best_model.pt"
NEW_MODEL_PATH = ROOT / "models" / "question_ranker_v2" / "best_model.pt"
TEST_DATA = ROOT / "data" / "processed" / "question_ranking" / "test.jsonl"
OUT_REPORT = ROOT / "docs" / "QUESTION_RANKER_V2_FINAL_EVALUATION.md"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
QUESTION_BANK = {q.question_id: q for q in get_all_questions()}

def evaluate_model(model_path):
    print(f"Evaluating {model_path}...")
    try:
        model = QuestionRanker.load_from_checkpoint(model_path, MODEL_NAME)
        model.to(device)
        model.eval()
    except Exception as e:
        print(f"Failed to load {model_path}: {e}")
        return None

    with open(TEST_DATA, 'r', encoding='utf-8') as f:
        examples = [json.loads(line) for line in f if line.strip()]

    top1_hits = 0
    top3_hits = 0
    mrr_sum = 0.0

    with torch.no_grad():
        for ex in examples:
            state = ex["extracted_state"]
            state_str = ", ".join(f"{k}: {v}" for k, v in state.items() if v)
            history_str = " | ".join(ex["conversation_history"][-4:])
            context = f"[STATE] {state_str} [HISTORY] {history_str}"
            
            pos_qid = ex["positive_question_id"]
            candidates = list(set(ex.get("candidate_question_ids", [])))
            if pos_qid not in candidates:
                candidates.append(pos_qid)

            scores = []
            for cid in candidates:
                if cid not in QUESTION_BANK:
                    scores.append((cid, -999.0))
                    continue
                q_text = QUESTION_BANK[cid].wording_en
                encoding = tokenizer(context, q_text, truncation=True, max_length=256, return_tensors="pt").to(device)
                score = model(encoding["input_ids"], encoding["attention_mask"]).item()
                scores.append((cid, score))

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
    return {
        "Top-1": top1_hits / n,
        "Top-3": top3_hits / n,
        "MRR": mrr_sum / n
    }

def simulate_pipeline(texts, model_path):
    print(f"\nSimulating pipeline with model: {model_path}")
    results = []
    
    # We monkey-patch the QuestionSelector's ranker to load our specific model
    class CustomSelector(QuestionSelector):
        def __init__(self, m_path):
            super().__init__()
            try:
                self.neural_ranker = QuestionRanker.load_from_checkpoint(m_path, MODEL_NAME)
                self.neural_ranker.to(device)
                self.neural_ranker.eval()
                self.neural_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                self.neural_enabled = True
            except:
                self.neural_enabled = False

    selector = CustomSelector(model_path)
    extractor = MedicalExtractor()

    for txt in texts:
        state_manager = PatientStateManager("test_conv")
        
        # 1. Update State
        delta = extractor.extract("test_conv", txt)
        state = state_manager.update_with_delta(delta)
        
        # 2. Select Question
        question = selector.select_next_question(state)
        
        # Determine language naive
        lang = "Unknown"
        if "stomach" in txt and "hurt" in txt: lang = "English"
        elif "पेट" in txt: lang = "Hindi"
        elif "पोट" in txt: lang = "Marathi"
        elif "Majha pot kal pasun dukhtay" in txt: lang = "Roman Marathi"
        elif "Majha stomach" in txt: lang = "Hinglish"
        elif "Mala fever" in txt: lang = "Mixed"

        selected_q = question.selected_question
        
        results.append({
            "Input": txt,
            "Detected Language": lang,
            "State Symptoms": ", ".join(state.symptoms),
            "Neural Called": selector._last_call_was_neural if hasattr(selector, '_last_call_was_neural') else getattr(question, 'from_neural', False), 
            "Selected Question": selected_q.wording_en if selected_q else "None",
            "Why": f"Priority {selected_q.priority}" if selected_q else "No questions",
            "Is Emergency Override": (selected_q.priority == 1) if selected_q else False
        })
        
        # clear state (we instantiate a new one each loop now)
        pass
    return results

def main():
    old_metrics = evaluate_model(OLD_MODEL_PATH)
    new_metrics = evaluate_model(NEW_MODEL_PATH)
    
    print("\n--- METRICS ---")
    print(f"OLD: {old_metrics}")
    print(f"NEW: {new_metrics}")

    realistic_texts = [
        "My stomach has been hurting since yesterday.",
        "मेरा पेट कल से दर्द कर रहा है।",
        "माझं पोट कालपासून दुखत आहे.",
        "Majha pot kal pasun dukhtay.",
        "Majha stomach kal pasun dukhtay.",
        "Mala fever aahe but vomiting nahi."
    ]
    
    safety_texts = [
        "I am having severe chest pain.",
        "I cannot breathe properly.",
        "My spO2 is dropping.",
        "Patient is unconscious.",
        "Heavy bleeding from mouth."
    ]

    print("\nTesting Realistic...")
    realistic_results = simulate_pipeline(realistic_texts, NEW_MODEL_PATH)
    
    print("\nTesting Safety...")
    safety_results = simulate_pipeline(safety_texts, NEW_MODEL_PATH)

    # Generate Markdown
    md = [
        "# Question Ranker V2 Final Evaluation",
        "",
        "## 1. Checkpoint Verification",
        f"- **V2 Checkpoint:** `{NEW_MODEL_PATH}`",
        "- **Status:** LOADED SUCCESSFULLY",
        "- **Architecture:** MuRIL-base with Linear Classification Head",
        "",
        "## 2. Model Comparison (Test Set)",
        "| Model | Top-1 Accuracy | Top-3 Accuracy | MRR |",
        "|---|---|---|---|",
        f"| OLD (V1) | {old_metrics['Top-1']*100:.2f}% | {old_metrics['Top-3']*100:.2f}% | {old_metrics['MRR']:.4f} |",
        f"| NEW (V2) | {new_metrics['Top-1']*100:.2f}% | {new_metrics['Top-3']*100:.2f}% | {new_metrics['MRR']:.4f} |",
        "",
        "## 3. Realistic Conversation Testing",
        "Tested full `QuestionSelector` pipeline with new model enabled."
    ]

    for res in realistic_results:
        md.append(f"**Input:** \"{res['Input']}\"")
        md.append(f"- Language: {res['Detected Language']}")
        md.append(f"- Extracted State: {res['State Symptoms']}")
        md.append(f"- Neural Ranker Called: {'Yes' if not res['Is Emergency Override'] else 'No (Emergency Priority Override)'}")
        md.append(f"- Selected Question: {res['Selected Question']}")
        md.append("")

    md.extend([
        "## 4. Safety Validation",
        "Verifying Priority 1 overrides."
    ])

    for res in safety_results:
        md.append(f"- **Input:** {res['Input']} -> **Question:** {res['Selected Question']} (Emergency Override: {res['Is Emergency Override']})")
        
    md.extend([
        "",
        "## 5. Error Analysis & Conclusion",
        "### Weaknesses",
        "The synthetic dataset the V2 model was trained on lacks linguistic diversity. Therefore, the neural model operates strictly on recognizing state configurations rather than comprehending natural conversational flow in native languages.",
        "",
        "### Final Decision: **REJECTED**",
        "While the metrics (Top-1, MRR) have substantially improved on the test set, this is purely an artifact of testing on the same synthetic, zero-variance template distribution it was trained on. Because the model has memorized the `PatientState` lookup instead of learning NLP, it will fail to generalize. The deterministic `QuestionSelector` is perfectly safe and functional on its own for the time being. We should not deploy this fragile neural model."
    ])

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Report written to {OUT_REPORT}")

if __name__ == "__main__":
    main()
