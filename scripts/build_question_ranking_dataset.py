"""
MahaArogya - Question Ranking Dataset Builder
Constructs train/val/test splits from MediTOD dialogs and optionally ChatDoctor.

Output format (JSONL):
{
  "dialog_id": "meditod_001_turn_05",
  "conversation_history": ["Patient: ...", "Doctor: ..."],
  "extracted_state": {"symptoms": [...], "negated": [...], "has_fever": false, ...},
  "positive_question_id": "q_cough_duration",
  "positive_question_en": "How long have you had this cough?",
  "candidate_question_ids": ["q_cough_duration", "q_headache_thunderclap", ...],
  "source": "meditod"
}
"""

import json
import random
import re
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_OUT = ROOT / "data" / "processed" / "question_ranking"
DATA_OUT.mkdir(parents=True, exist_ok=True)

MEDITOD_PATH = ROOT / "data" / "raw" / "meditod" / "data" / "dialogs.json"

# Import the question bank for candidate pool
sys.path.insert(0, str(ROOT))
from ai.questions.question_bank import get_all_questions

QUESTION_BANK = get_all_questions()
ALL_QID_EN = {q.question_id: q.wording_en for q in QUESTION_BANK}

# Number of negative candidates per positive
NUM_NEGATIVES = 5

random.seed(42)

# ---------------------------------------------------------------------------
# MediTOD action -> question_id mapping
# ---------------------------------------------------------------------------
ACTION_TO_QID = {
    # Onset / duration
    "ask_onset": "q_cough_duration",
    "ask_duration": "q_cough_duration",
    # Severity
    "ask_severity": "q_chest_pain_character",
    # Associated symptoms
    "ask_associated_symptoms": "q_abdo_vomiting",
    # Blood in vomit / stool
    "ask_hemoptysis": "q_cough_blood",
    "ask_blood_vomit": "q_vomit_blood",
    "ask_blood_stool": "q_diarrhea_blood",
    # Breathing
    "ask_dyspnea": "q_breathless_severity",
    "ask_dyspnea_exertion": "q_breathless_exertional",
    # Fever
    "ask_fever": "q_fever_duration",
    # Cough
    "ask_cough": "q_cough_duration",
    "ask_cough_sputum": "q_cough_sputum",
    "ask_cough_blood": "q_cough_blood",
    # Headache
    "ask_headache": "q_headache_duration",
    "ask_neck_stiffness": "q_headache_neck_stiffness",
    # Chest pain
    "ask_chest_pain": "q_chest_pain_radiate",
    "ask_chest_radiation": "q_chest_pain_radiate",
    "ask_diaphoresis": "q_chest_pain_diaphoresis",
    # GI
    "ask_nausea": "q_nausea_duration",
    "ask_vomiting": "q_vomit_frequency",
    "ask_diarrhea": "q_diarrhea_frequency",
    # General
    "ask_fatigue": "q_fatigue_duration",
    "ask_weight_loss": "q_fatigue_weight_loss",
}


def extract_state_from_dialog(utterances: list, up_to_idx: int) -> dict:
    """Extract a simplified patient state from dialog history up to turn index."""
    state = {
        "symptoms": [],
        "negated": [],
        "has_fever": False,
        "has_cough": False,
        "has_breathlessness": False,
        "has_chest_pain": False,
        "has_abdominal_pain": False,
        "has_headache": False,
    }
    
    symptom_keywords = {
        "cough": "has_cough",
        "fever": "has_fever",
        "shortness of breath": "has_breathlessness",
        "breathless": "has_breathlessness",
        "dyspnea": "has_breathlessness",
        "chest pain": "has_chest_pain",
        "abdominal pain": "has_abdominal_pain",
        "stomach pain": "has_abdominal_pain",
        "headache": "has_headache",
    }
    
    negation_re = re.compile(
        r"(no|not|denies|deny|without|absence of|negative for|don.t have|does not have)\s+([a-z\s]+)",
        re.IGNORECASE
    )
    
    for utt in utterances[:up_to_idx]:
        if utt.get("speaker") != "patient":
            continue
        text = utt.get("text", "").lower()
        
        # Check positive symptoms from dialog_state
        ds = utt.get("dialog_state", {})
        pos_symptoms = ds.get("positive_symptom", [])
        if isinstance(pos_symptoms, list):
            state["symptoms"].extend(pos_symptoms)
        elif isinstance(pos_symptoms, str):
            state["symptoms"].append(pos_symptoms)
        
        neg_symptoms = ds.get("negative_symptom", [])
        if isinstance(neg_symptoms, list):
            state["negated"].extend(neg_symptoms)
        elif isinstance(neg_symptoms, str):
            state["negated"].append(neg_symptoms)
        
        # Direct keyword scan
        for kw, field in symptom_keywords.items():
            if kw in text:
                state[field] = True
    
    return state


def build_conversation_history(utterances: list, up_to_idx: int) -> list[str]:
    """Extract conversation history as list of 'Speaker: text' strings."""
    history = []
    for utt in utterances[:up_to_idx]:
        speaker = utt.get("speaker", "unknown").capitalize()
        text = utt.get("text", "")
        history.append(f"{speaker}: {text}")
    return history[-10:]  # Last 10 turns to keep context window manageable


def get_negative_candidates(positive_qid: str, n: int = NUM_NEGATIVES) -> list[str]:
    """Sample n question IDs that are NOT the positive."""
    pool = [qid for qid in ALL_QID_EN.keys() if qid != positive_qid]
    return random.sample(pool, min(n, len(pool)))


def process_meditod() -> list[dict]:
    """Process MediTOD dialogs into ranking examples."""
    examples = []
    
    with open(MEDITOD_PATH, encoding="utf-8") as f:
        dialogs = json.load(f)
    
    for dialog_id, dialog in dialogs.items():
        utterances = dialog.get("utterances", [])
        
        for idx, utt in enumerate(utterances):
            if utt.get("speaker") != "doctor":
                continue
            if idx == 0:
                continue  # Skip opening greeting
            
            # Check if this doctor turn has a mappable action
            actions = utt.get("actions", [])
            matched_qid = None
            
            for action_obj in actions:
                action = action_obj.get("action", "")
                if action in ACTION_TO_QID:
                    matched_qid = ACTION_TO_QID[action]
                    break
            
            # Also try text-based matching for "?" questions
            if matched_qid is None and "?" in utt.get("text", ""):
                # Try to match via question text similarity (heuristic)
                doctor_text = utt.get("text", "").lower()
                for q in QUESTION_BANK:
                    en_lower = q.wording_en.lower()
                    # Key word overlap
                    doc_words = set(re.findall(r'\b[a-z]+\b', doctor_text))
                    q_words = set(re.findall(r'\b[a-z]+\b', en_lower))
                    overlap = len(doc_words & q_words)
                    if overlap >= 3:
                        matched_qid = q.question_id
                        break
            
            if matched_qid is None:
                continue
            
            history = build_conversation_history(utterances, idx)
            state = extract_state_from_dialog(utterances, idx)
            negatives = get_negative_candidates(matched_qid)
            
            example = {
                "dialog_id": f"meditod_{dialog_id}_turn_{idx:03d}",
                "conversation_history": history,
                "extracted_state": state,
                "positive_question_id": matched_qid,
                "positive_question_en": ALL_QID_EN.get(matched_qid, ""),
                "candidate_question_ids": [matched_qid] + negatives,
                "source": "meditod",
            }
            examples.append(example)
    
    return examples


def process_chatdoctor(target_samples: int = 5000) -> list[dict]:
    """Process ChatDoctor dialogs into ranking examples."""
    examples = []
    
    try:
        import datasets
        ds = datasets.load_dataset('lavita/ChatDoctor-HealthCareMagic-100k', split='train')
    except ImportError:
        print("datasets library not installed, skipping ChatDoctor.")
        return []

    # Pre-tokenize question bank for faster matching
    q_tokens = {q.question_id: set(re.findall(r'\b[a-z]+\b', q.wording_en.lower())) for q in QUESTION_BANK}

    count = 0
    for idx, row in enumerate(ds):
        if count >= target_samples:
            break
            
        output_text = row.get("output", "")
        if "?" not in output_text:
            continue
            
        input_text = row.get("input", "")
        if not input_text:
            continue
            
        # Try to find a matched question
        sentences = re.split(r'(?<=[.!?])\s+', output_text)
        matched_qid = None
        
        for sent in sentences:
            if "?" in sent:
                sent_lower = sent.lower()
                doc_words = set(re.findall(r'\b[a-z]+\b', sent_lower))
                
                best_overlap = 0
                for qid, q_words in q_tokens.items():
                    overlap = len(doc_words & q_words)
                    # Require overlap to avoid false positives
                    if overlap >= 3 and overlap > best_overlap:
                        best_overlap = overlap
                        matched_qid = qid
                        
        if matched_qid:
            history = [f"Patient: {input_text}"]
            # We extract state using the same logic as MediTOD by wrapping input in a dummy utterance
            dummy_utterance = {"speaker": "patient", "text": input_text}
            state = extract_state_from_dialog([dummy_utterance], 1)
            negatives = get_negative_candidates(matched_qid)
            
            example = {
                "dialog_id": f"chatdoctor_{idx:06d}",
                "conversation_history": history,
                "extracted_state": state,
                "positive_question_id": matched_qid,
                "positive_question_en": ALL_QID_EN.get(matched_qid, ""),
                "candidate_question_ids": [matched_qid] + negatives,
                "source": "chatdoctor",
            }
            examples.append(example)
            count += 1
            
    return examples


def split_and_save(examples: list[dict], split_ratios=(0.8, 0.1, 0.1)):
    """Split by source to avoid leakage, then save as JSONL."""
    # Group by source dialog
    by_dialog = {}
    for ex in examples:
        base = ex["dialog_id"].split("_turn_")[0]
        by_dialog.setdefault(base, []).append(ex)
    
    dialog_ids = list(by_dialog.keys())
    random.shuffle(dialog_ids)
    
    n = len(dialog_ids)
    n_train = int(n * split_ratios[0])
    n_val = int(n * split_ratios[1])
    
    train_ids = dialog_ids[:n_train]
    val_ids = dialog_ids[n_train:n_train + n_val]
    test_ids = dialog_ids[n_train + n_val:]
    
    splits = {
        "train": [ex for did in train_ids for ex in by_dialog[did]],
        "val":   [ex for did in val_ids   for ex in by_dialog[did]],
        "test":  [ex for did in test_ids  for ex in by_dialog[did]],
    }
    
    for split_name, split_data in splits.items():
        out_path = DATA_OUT / f"meditod_{split_name}.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for ex in split_data:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        print(f"  {split_name}: {len(split_data)} examples -> {out_path}")


def main():
    print("Building MediTOD ranking dataset...")
    
    # 1. MediTOD examples
    print("\n[1/1] Processing MediTOD...")
    meditod_examples = process_meditod()
    print(f"  MediTOD examples: {len(meditod_examples)}")
    
    all_examples = meditod_examples
    
    print(f"\nTotal examples: {len(all_examples)}")
    print("\nSplitting and saving...")
    split_and_save(all_examples)
    
    # Summary
    print("\nDataset summary:")
    print(f"  Total: {len(all_examples)} ranking examples")
    print(f"  Candidates per example: {1 + NUM_NEGATIVES}")
    print(f"  Output: {DATA_OUT}")
    
    # Positive question distribution
    pos_dist = {}
    for ex in all_examples:
        qid = ex["positive_question_id"]
        pos_dist[qid] = pos_dist.get(qid, 0) + 1
    print("\nPositive question distribution (top 10):")
    for qid, count in sorted(pos_dist.items(), key=lambda x: -x[1])[:10]:
        print(f"  {count:4d}  {qid}")


if __name__ == "__main__":
    main()
