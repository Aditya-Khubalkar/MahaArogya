"""
End-to-End Integration Tests for MahaArogya AI Subsystem.
Verifies complete conversation pipeline: Text/Voice -> Extractor -> PatientState -> Question Selector -> Triage -> Routing.
"""

import pytest
from ai.orchestrator import MahaArogyaOrchestrator
from ai.cv.occupancy import CCTVOccupancyEstimator


def test_full_multiturn_marathi_conversation():
    orchestrator = MahaArogyaOrchestrator()
    cid = "test_multiturn_mr_01"

    # TURN 1: "माझं पोट दोन दिवसांपासून खूप दुखत आहे."
    res1 = orchestrator.process_turn(
        conversation_id=cid,
        text_input="माझं पोट दोन दिवसांपासून खूप दुखत आहे.",
        language="mr",
        modality="text"
    )
    assert res1.conversation_id == cid
    assert "abdominal_pain" in res1.patient_state.symptoms
    assert res1.ai_response_text != ""

    # TURN 2: "मला काल २ वेळा उलट्या झाल्या."
    res2 = orchestrator.process_turn(
        conversation_id=cid,
        text_input="मला काल २ वेळा उलट्या झाल्या.",
        language="mr",
        modality="text"
    )
    assert "vomiting" in res2.patient_state.symptoms

    # TURN 3: "ताप नाही."
    res3 = orchestrator.process_turn(
        conversation_id=cid,
        text_input="ताप नाही.",
        language="mr",
        modality="text"
    )
    assert "fever" in res3.patient_state.negated_symptoms
    assert res3.triage_decision.triage_category in ["ROUTINE", "PRIORITY", "URGENT"]


def test_emergency_chest_pain_integration():
    orchestrator = MahaArogyaOrchestrator()
    cid = "test_emergency_hi_01"

    res = orchestrator.process_turn(
        conversation_id=cid,
        text_input="छाती में बहुत तेज दर्द हो रहा है और सांस लेने में तकलीफ है।",
        language="hi",
        modality="text"
    )

    assert res.triage_decision.triage_category == "EMERGENCY"
    assert len(res.hospital_recommendations) > 0
    assert res.hospital_recommendations[0].hospital.emergency_capable is True
    assert "🚨" in res.ai_response_text


def test_cctv_bed_occupancy_integration():
    estimator = CCTVOccupancyEstimator()
    res = estimator.estimate_ward_occupancy(
        camera_id="cam_icu_01",
        ward_id="ward_icu_A",
        detected_occupied_beds=9,
        total_beds=10,
        db_authoritative_occupied=7,
        confidence=0.85
    )

    assert res.discrepancy_detected is True
    assert res.human_verification_required is True
