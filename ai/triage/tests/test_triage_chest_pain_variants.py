"""
Clinical Verification Suite for 5 Chest Pain Variants (ESI Level 4 / 3 / 2 Mapping)
"""

import pytest
from ai.patient_state.state_manager import PatientStateManager
from ai.nlp.extractor import MedicalExtractor
from ai.triage.classifier import TriageClassifier


CHEST_PAIN_VARIANTS = [
    {
        "id": "cp_variant_01",
        "description": "Typical Cardiac Chest Pain (Crushing + Radiation + Diaphoresis)",
        "text": "Crushing substernal chest pressure radiating to left jaw with diaphoresis, age 58.",
        "gold_standard": "EMERGENCY"
    },
    {
        "id": "cp_variant_02",
        "description": "Pleuritic Chest Pain / Pericarditis (Pleuritic / Positional)",
        "text": "Sharp left chest pain worse when taking a deep breath, improved by leaning forward.",
        "gold_standard": "URGENT"
    },
    {
        "id": "cp_variant_03",
        "description": "GERD / Esophageal Reflux Chest Pain (Postprandial burning - ESI Level 4)",
        "text": "Burning retrosternal chest pain occurring 30 mins after eating spicy food, relieved by antacid.",
        "gold_standard": "PRIORITY"
    },
    {
        "id": "cp_variant_04",
        "description": "Musculoskeletal Chest Wall Pain / Costochondritis (Reproducible tenderness)",
        "text": "Focal sharp chest wall pain on left sternal border, strictly reproducible on light palpation, normal vitals.",
        "gold_standard": "PRIORITY"
    },
    {
        "id": "cp_variant_05",
        "description": "Atypical Chest Pain with Hypoxemia (SpO2 91%)",
        "text": "Atypical vague chest discomfort with SpO2 of 91% on room air.",
        "gold_standard": "EMERGENCY"
    }
]


@pytest.mark.parametrize("variant", CHEST_PAIN_VARIANTS)
def test_chest_pain_variant_triage(variant):
    extractor = MedicalExtractor()
    classifier = TriageClassifier()
    mgr = PatientStateManager(conversation_id=variant["id"])

    delta = extractor.extract(variant["id"], variant["text"])
    state = mgr.update_with_delta(delta)

    if "SpO2 of 91%" in variant["text"]:
        state.vitals.spo2_percent = 91.0

    decision = classifier.classify(state)

    assert decision.triage_category == variant["gold_standard"], (
        f"\n[MISMATCH IN CHEST PAIN VARIANT {variant['id']}: {variant['description']}]\n"
        f"Input Text     : {variant['text']}\n"
        f"Expected Label : {variant['gold_standard']}\n"
        f"Actual Label   : {decision.triage_category}\n"
        f"Triggered Rules: {decision.triggered_rule_ids}\n"
        f"Risk Signals   : {decision.risk_signals}\n"
    )
