"""
MahaArogya — Evaluation Test Set Builder
Constructs reusable, inspectable test sets for ASR, Medical Extraction, and Triage Classification.
Saves to evaluation/test_sets/ directory per Spec Section 5.
"""

import json
import pyttsx3
from pathlib import Path


def build_asr_test_set():
    test_dir = Path("evaluation/test_sets")
    test_dir.mkdir(parents=True, exist_ok=True)
    audio_sample_dir = Path("data/test/asr_samples")
    audio_sample_dir.mkdir(parents=True, exist_ok=True)
    
    asr_samples = [
        # English Utterances
        {"id": "asr_en_01", "lang": "en", "reference": "I have severe abdominal pain for two days"},
        {"id": "asr_en_02", "lang": "en", "reference": "High fever and persistent cough since yesterday morning"},
        {"id": "asr_en_03", "lang": "en", "reference": "I am experiencing sharp chest pain and shortness of breath"},
        {"id": "asr_en_04", "lang": "en", "reference": "I vomited twice this afternoon and feel dehydrated"},
        {"id": "asr_en_05", "lang": "en", "reference": "Feeling very dizzy and lightheaded when standing up"},
        {"id": "asr_en_06", "lang": "en", "reference": "I have a sore throat and difficulty swallowing food"},
        {"id": "asr_en_07", "lang": "en", "reference": "Severe diarrhea and stomach cramps for twenty four hours"},
        {"id": "asr_en_08", "lang": "en", "reference": "Numbness and tingling sensation in my left hand"},
        {"id": "asr_en_09", "lang": "en", "reference": "Burning sensation during urination and frequent urge"},
        {"id": "asr_en_10", "lang": "en", "reference": "Extreme fatigue and body pain after physical exertion"},
        
        # Multilingual Utterances (Marathi, Hindi, Hinglish references)
        {"id": "asr_mr_01", "lang": "en", "reference": "My stomach is hurting severely for three days"},
        {"id": "asr_mr_02", "lang": "en", "reference": "I have high fever and severe headache since last night"},
        {"id": "asr_hi_01", "lang": "en", "reference": "Severe pain in chest and difficulty in breathing"},
        {"id": "asr_hi_02", "lang": "en", "reference": "Vomiting and loose motions since two days"},
        {"id": "asr_rm_01", "lang": "en", "reference": "Dizziness and nausea since morning"},
    ]
    
    # Synthesize audio for each utterance
    engine = pyttsx3.init()
    for sample in asr_samples:
        audio_file = audio_sample_dir / f"{sample['id']}.wav"
        sample["audio_path"] = str(audio_file)
        engine.save_to_file(sample["reference"], str(audio_file))
    engine.runAndWait()
    
    out_file = test_dir / "asr_test_set.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(asr_samples, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved {len(asr_samples)} ASR audio test samples -> {out_file}")


def build_extraction_test_set():
    test_dir = Path("evaluation/test_sets")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    extraction_samples = [
        # English Medical Utterances
        {"id": "ext_01", "text": "I have severe abdominal pain for two days", "expected_symptoms": ["abdominal_pain"]},
        {"id": "ext_02", "text": "Patient presents with high fever and severe headache", "expected_symptoms": ["fever", "headache"]},
        {"id": "ext_03", "text": "Chest pain with shortness of breath since morning", "expected_symptoms": ["chest_pain", "breathlessness"]},
        {"id": "ext_04", "text": "Experiencing vomiting and diarrhea for 24 hours", "expected_symptoms": ["vomiting", "diarrhea"]},
        {"id": "ext_05", "text": "Complaining of dizziness and nausea", "expected_symptoms": ["dizziness", "nausea"]},
        {"id": "ext_06", "text": "Patient has sore throat and cough", "expected_symptoms": ["cough", "sore_throat"]},
        {"id": "ext_07", "text": "Burning sensation during urination", "expected_symptoms": ["burning_urination"]},
        {"id": "ext_08", "text": "Numbness in left arm and facial weakness", "expected_symptoms": ["numbness"]},
        {"id": "ext_09", "text": "Joint pain and swelling in knees", "expected_symptoms": ["joint_pain", "swelling"]},
        {"id": "ext_10", "text": "Extreme fatigue and muscle weakness", "expected_symptoms": ["fatigue"]},
        
        # Marathi Medical Utterances
        {"id": "ext_11", "text": "मला ३ दिवसांपासून पोटात तीव्र दुखत आहे", "expected_symptoms": ["abdominal_pain"]},
        {"id": "ext_12", "text": "मला काल रात्रीपासून खूप ताप आला आहे आणि डोकेदुखी आहे", "expected_symptoms": ["fever", "headache"]},
        {"id": "ext_13", "text": "माझ्या छातीत दुखतंय आणि श्वास घ्यायला त्रास होतोय", "expected_symptoms": ["chest_pain", "breathlessness"]},
        {"id": "ext_14", "text": "कालपासून चार वेळा उलट्या झाल्या आहेत", "expected_symptoms": ["vomiting"]},
        {"id": "ext_15", "text": "मला चक्कर येत आहे आणि डोके दुखत आहे", "expected_symptoms": ["dizziness", "headache"]},
        {"id": "ext_16", "text": "माझ्या घशात खवखव आहे आणि खोकला येतोय", "expected_symptoms": ["cough", "sore_throat"]},
        {"id": "ext_17", "text": "दोन दिवसांपासून जुलाब थांबत नाहीत", "expected_symptoms": ["diarrhea"]},
        {"id": "ext_18", "text": "लघवी करताना खूप जळजळ होत आहे", "expected_symptoms": ["burning_urination"]},
        
        # Hindi Medical Utterances
        {"id": "ext_19", "text": "मुझे दो दिनों से पेट में तेज दर्द हो रहा है", "expected_symptoms": ["abdominal_pain"]},
        {"id": "ext_20", "text": "कल रात से तेज बुखार और सिरदर्द है", "expected_symptoms": ["fever", "headache"]},
        {"id": "ext_21", "text": "छाती में भारीपन है और सांस लेने में तकलीफ हो रही है", "expected_symptoms": ["chest_pain", "breathlessness"]},
        {"id": "ext_22", "text": "मुझे तीन बार उल्टी आ चुकी है और दस्त हैं", "expected_symptoms": ["vomiting", "diarrhea"]},
        
        # Romanized Marathi / Hinglish Medical Utterances
        {"id": "ext_23", "text": "Majha pot don divas pasun khup dukhtay", "expected_symptoms": ["abdominal_pain"]},
        {"id": "ext_24", "text": "Mala tap ala ahe ani khokla ahe", "expected_symptoms": ["fever", "cough"]},
        {"id": "ext_25", "text": "Chhati madhe pain ahe ani breathing problem ahe", "expected_symptoms": ["chest_pain", "breathlessness"]},
    ]
    
    out_file = test_dir / "extraction_test_set.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(extraction_samples, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved {len(extraction_samples)} Medical Extraction test samples -> {out_file}")


def build_triage_test_set():
    test_dir = Path("evaluation/test_sets")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    triage_samples = [
        # EMERGENCY Cases (Red Flag Triggered)
        {"id": "trg_01", "symptom": "chest_pain", "severity": "severe", "is_emergency": True, "expected_category": "EMERGENCY"},
        {"id": "trg_02", "symptom": "breathlessness", "severity": "severe", "is_emergency": True, "expected_category": "EMERGENCY"},
        {"id": "trg_03", "symptom": "hematemesis", "severity": "severe", "is_emergency": True, "expected_category": "EMERGENCY"},
        {"id": "trg_04", "symptom": "stroke_numbness", "severity": "severe", "is_emergency": True, "expected_category": "EMERGENCY"},
        {"id": "trg_05", "symptom": "pediatric_high_fever", "severity": "severe", "is_emergency": True, "expected_category": "EMERGENCY"},
        {"id": "trg_06", "symptom": "anaphylaxis_allergy", "severity": "severe", "is_emergency": True, "expected_category": "EMERGENCY"},
        {"id": "trg_07", "symptom": "trauma_bleeding", "severity": "severe", "is_emergency": True, "expected_category": "EMERGENCY"},
        {"id": "trg_08", "symptom": "unconscious", "severity": "severe", "is_emergency": True, "expected_category": "EMERGENCY"},
        {"id": "trg_09", "symptom": "seizure", "severity": "severe", "is_emergency": True, "expected_category": "EMERGENCY"},
        {"id": "trg_10", "symptom": "cyanosis_spo2", "severity": "severe", "is_emergency": True, "expected_category": "EMERGENCY"},

        # NON-EMERGENCY Cases (Routine / Priority / Urgent)
        {"id": "trg_11", "symptom": "headache", "severity": "mild", "is_emergency": False, "expected_category": "ROUTINE"},
        {"id": "trg_12", "symptom": "cough", "severity": "mild", "is_emergency": False, "expected_category": "ROUTINE"},
        {"id": "trg_13", "symptom": "acidity", "severity": "mild", "is_emergency": False, "expected_category": "ROUTINE"},
        {"id": "trg_14", "symptom": "rash", "severity": "mild", "is_emergency": False, "expected_category": "ROUTINE"},
        {"id": "trg_15", "symptom": "back_pain", "severity": "mild", "is_emergency": False, "expected_category": "ROUTINE"},
        {"id": "trg_16", "symptom": "abdominal_pain", "severity": "severe", "is_emergency": False, "expected_category": "PRIORITY"},
        {"id": "trg_17", "symptom": "diarrhea", "severity": "moderate", "is_emergency": False, "expected_category": "PRIORITY"},
        {"id": "trg_18", "symptom": "fever", "severity": "moderate", "is_emergency": False, "expected_category": "PRIORITY"},
        {"id": "trg_19", "symptom": "vomiting", "severity": "moderate", "is_emergency": False, "expected_category": "PRIORITY"},
        {"id": "trg_20", "symptom": "earache", "severity": "mild", "is_emergency": False, "expected_category": "ROUTINE"},
    ]
    
    out_file = test_dir / "triage_test_set.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(triage_samples, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved {len(triage_samples)} Triage test samples -> {out_file}")


def build_all():
    print("=" * 60)
    print("  Building MahaArogya Evaluation Test Sets")
    print("=" * 60)
    build_asr_test_set()
    build_extraction_test_set()
    build_triage_test_set()
    print("=" * 60)
    print("  All evaluation test sets built successfully!")
    print("=" * 60)


if __name__ == "__main__":
    build_all()
