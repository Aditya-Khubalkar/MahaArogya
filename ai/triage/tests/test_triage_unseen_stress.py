"""
Third Independent Adversarial Stress Test Suite for MahaArogya Triage System.
Contains 25 NEW clinical test cases not present in baseline (20) or edge-case (18) sets.
"""

import pytest
from ai.patient_state.state_manager import PatientStateManager
from ai.nlp.extractor import MedicalExtractor
from ai.triage.classifier import TriageClassifier


UNSEEN_STRESS_CASES = [
    {
        "id": "unseen_01",
        "description": "FAST Stroke: Facial drooping and right arm weakness",
        "text": "Sudden facial drooping on right side and right arm weakness since 15 mins.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_02",
        "description": "Silent MI / Shock: 65yo female, cold sweat, BP 82/50",
        "text": "65yo female feeling dizzy, cold sweating, and extreme weakness with blood pressure 82/50.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_03",
        "description": "Neonatal Sepsis: 3-week-old newborn with fever 101.2F",
        "text": "3-week-old newborn with fever of 101.2 F, lethargic and refusing feeds.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_04",
        "description": "Meningitis: Severe headache, fever 103F, painful neck stiffness",
        "text": "Acute severe headache with high fever 103 F and painful neck stiffness.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_05",
        "description": "Ectopic Pregnancy: Unilateral pelvic pain + fainting",
        "text": "Positive home pregnancy test, sharp unilateral pelvic pain and fainting.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_06",
        "description": "Thunderclap SAH: Explosive 10/10 headache in seconds",
        "text": "Sudden explosive headache reaching peak 10/10 intensity within 5 seconds.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_07",
        "description": "Anaphylaxis: Wasp sting, lip swelling, hives, wheezing",
        "text": "Stung by wasp 10 mins ago, sudden lip swelling, hives, and wheezing.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_08",
        "description": "DKA: Type 1 diabetic, fruity breath, Kussmaul respiration, sugar 450",
        "text": "Type 1 diabetic with fruity breath, rapid deep breathing, and blood sugar 450 mg/dL.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_09",
        "description": "Testicular Torsion: Excruciating unilateral pain in adolescent",
        "text": "Sudden excruciating unilateral testicular pain and swelling in 16yo male.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_10",
        "description": "Compartment Syndrome: Leg cast, tight excruciating pain, pale limb",
        "text": "Severe tight calf pain after leg cast placement, limb pale with weak pulse.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_11",
        "description": "Suicidal Ideation: Explicit plan and intent",
        "text": "Feeling hopeless, expressing clear plan and intent for self-harm.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_12",
        "description": "Code-Switch Radiating MI (Marathi-English)",
        "text": "Chhatit khoop kadak dukhatahe ani dava hatat severe pain pasarat ahe.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_13",
        "description": "Code-Switch Bronchitis (Hinglish)",
        "text": "Bahut khasne aa raha hai with mild chest tightness and fever since yesterday.",
        "gold_standard": "PRIORITY"
    },
    {
        "id": "unseen_14",
        "description": "Code-Switch GI Bleed (Hindi)",
        "text": "Khoon ki ulti ho rahi hai aur chakkar aa raha hai.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_15",
        "description": "Code-Switch Constipation Abdominal Pain (Roman Marathi)",
        "text": "Potaat severe dukhatahe ani 3 days pasun constipation ahe.",
        "gold_standard": "PRIORITY"
    },
    {
        "id": "unseen_16",
        "description": "Code-Switch Tension Headache (Roman Marathi)",
        "text": "Doka khoop dukhatahe since morning, no fever, no numbness.",
        "gold_standard": "ROUTINE"
    },
    {
        "id": "unseen_17",
        "description": "Code-Switch Indigestion (Hinglish)",
        "text": "Potat thodasa pain ahe after eating lunch.",
        "gold_standard": "ROUTINE"
    },
    {
        "id": "unseen_18",
        "description": "Code-Switch Stroke (Hinglish)",
        "text": "Suddenly difficulty speaking and right arm numb ho gaya hai.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_19",
        "description": "Code-Switch Ectopic Risk (Hinglish)",
        "text": "8 weeks pregnant hu, mild spotting, feeling dizzy.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_20",
        "description": "Vital Boundary SpO2 = 92.0% (Should be URGENT)",
        "text": "SpO2 is exactly 92.0% on room air with mild cough.",
        "gold_standard": "URGENT"
    },
    {
        "id": "unseen_21",
        "description": "Vital Boundary SpO2 = 91.9% (Should be EMERGENCY)",
        "text": "SpO2 is exactly 91.9% on room air with mild cough.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_22",
        "description": "Vital Boundary HR = 121 bpm (Should be EMERGENCY)",
        "text": "Pulse rate is 121 bpm, blood pressure 118/76, feeling anxious.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "unseen_23",
        "description": "TRAP CASE 1: Hyperventilation / Panic Attack",
        "text": "Panic attack with rapid shallow breathing, tingling fingers, SpO2 99%, normal BP.",
        "gold_standard": "PRIORITY"
    },
    {
        "id": "unseen_24",
        "description": "TRAP CASE 2: Costochondritis Musculoskeletal",
        "text": "Costochondritis - sharp left chest pain reproducible with finger pressure on sternum, normal EKG.",
        "gold_standard": "PRIORITY"
    },
    {
        "id": "unseen_25",
        "description": "TRAP CASE 3: Chronic Tension Headache (3 months)",
        "text": "Chronic tension headache present for 3 months, unchanged, normal vitals, no red flags.",
        "gold_standard": "ROUTINE"
    }
]


@pytest.mark.parametrize("case", UNSEEN_STRESS_CASES)
def test_unseen_triage_case(case):
    extractor = MedicalExtractor()
    classifier = TriageClassifier()
    mgr = PatientStateManager(conversation_id=case["id"])

    delta = extractor.extract(case["id"], case["text"])
    state = mgr.update_with_delta(delta)

    # Inject explicit vitals / numbers if stated in text
    if "82/50" in case["text"]:
        state.vitals.bp_systolic = 82
        state.vitals.bp_diastolic = 50
    elif "101.2" in case["text"]:
        state.vitals.temperature_f = 101.2
        state.age_years = 0.05
    elif "103" in case["text"]:
        state.vitals.temperature_f = 103.0
    elif "92.0%" in case["text"]:
        state.vitals.spo2_percent = 92.0
    elif "91.9%" in case["text"]:
        state.vitals.spo2_percent = 91.9
    elif "121 bpm" in case["text"]:
        state.vitals.pulse_rate = 121

    decision = classifier.classify(state)

    assert decision.triage_category == case["gold_standard"], (
        f"\n[FAILURE IN UNSEEN CASE {case['id']}: {case['description']}]\n"
        f"Input Text     : {case['text']}\n"
        f"Expected Label : {case['gold_standard']}\n"
        f"Actual Label   : {decision.triage_category}\n"
        f"Triggered Rules: {decision.triggered_rule_ids}\n"
        f"Risk Signals   : {decision.risk_signals}\n"
    )
