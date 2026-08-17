"""
Unit tests verifying PatientState memory, state transition rules, and byte-for-byte determinism.
"""

import json
import pytest
from ai.patient_state.schemas import PatientStateDelta, SymptomDetail, Vitals
from ai.patient_state.state_manager import PatientStateManager


def test_patient_state_turn_sequence():
    mgr = PatientStateManager(conversation_id="conv_test_001", language="mr", modality="voice")
    
    # --- TURN 1: "Majha pot dukhtay." ---
    delta1 = PatientStateDelta(
        conversation_id="conv_test_001",
        new_input="Majha pot dukhtay.",
        new_symptoms={
            "abdominal_pain": SymptomDetail(present=True, location="abdomen")
        }
    )
    state1 = mgr.update_with_delta(delta1)
    
    assert "abdominal_pain" in state1.symptoms
    assert state1.symptoms["abdominal_pain"].present is True
    assert state1.symptoms["abdominal_pain"].duration is None
    assert "abdominal_pain_duration" in state1.missing_information
    assert "vomiting_status" in state1.missing_information
    assert "fever_status" in state1.missing_information

    # --- TURN 2: "Don divas pasun." ---
    delta2 = PatientStateDelta(
        conversation_id="conv_test_001",
        new_input="Don divas pasun.",
        new_symptoms={
            "abdominal_pain": SymptomDetail(present=True, duration="2 days")
        }
    )
    state2 = mgr.update_with_delta(delta2)
    
    assert state2.symptoms["abdominal_pain"].duration == "2 days"
    assert "abdominal_pain_duration" not in state2.missing_information

    # --- TURN 3: "Ho, kal don vela vomiting zala." ---
    delta3 = PatientStateDelta(
        conversation_id="conv_test_001",
        new_input="Ho, kal don vela vomiting zala.",
        new_symptoms={
            "vomiting": SymptomDetail(present=True, frequency="2 times", onset="previous day")
        }
    )
    state3 = mgr.update_with_delta(delta3)
    
    assert "vomiting" in state3.symptoms
    assert state3.symptoms["vomiting"].present is True
    assert state3.symptoms["vomiting"].frequency == "2 times"
    assert "vomiting_status" not in state3.missing_information

    # --- TURN 4: "Fever pan aahe." ---
    delta4 = PatientStateDelta(
        conversation_id="conv_test_001",
        new_input="Fever pan aahe.",
        new_symptoms={
            "fever": SymptomDetail(present=True)
        }
    )
    state4 = mgr.update_with_delta(delta4)
    
    assert "fever" in state4.symptoms
    assert state4.symptoms["fever"].present is True
    assert "fever_status" not in state4.missing_information


def test_multiturn_accumulation_and_update():
    """Tests 6-turn accumulation, symptom correction, off-topic handling, and answers updating."""
    cid = "test_multiturn_unit_01"
    mgr = PatientStateManager(conversation_id=cid, patient_id="patient_007", language="en")
    
    # Turn 1: Initial complaint (mild pain since yesterday)
    mgr.update_with_delta(PatientStateDelta(
        conversation_id=cid,
        new_input="I have abdominal pain since yesterday, it's mild.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True, severity="mild", duration="since yesterday", location="abdomen")}
    ))
    assert mgr.state.symptoms["abdominal_pain"].severity == "mild"
    assert mgr.state.symptoms["abdominal_pain"].duration == "since yesterday"
    
    # Turn 2: Add related symptom (nausea & vomiting)
    mgr.update_with_delta(PatientStateDelta(
        conversation_id=cid,
        new_input="Also feeling nauseous and vomited 2 times.",
        new_symptoms={
            "nausea": SymptomDetail(present=True, severity="moderate"),
            "vomiting": SymptomDetail(present=True, frequency="2 times")
        }
    ))
    assert "nausea" in mgr.state.symptoms
    assert "vomiting" in mgr.state.symptoms
    
    # Turn 3: Correction of duration & severity
    mgr.update_with_delta(PatientStateDelta(
        conversation_id=cid,
        new_input="Actually the pain started this morning, not yesterday, and it's severe now.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True, severity="severe", duration="this morning", location="abdomen")}
    ))
    assert mgr.state.symptoms["abdominal_pain"].severity == "severe"
    assert mgr.state.symptoms["abdominal_pain"].duration == "this morning"
    
    # Turn 4: Off-topic chatter
    mgr.update_with_delta(PatientStateDelta(
        conversation_id=cid,
        new_input="My neighbor told me to drink ginger tea for stomach ache."
    ))
    assert len(mgr.state.original_input_history) == 4
    
    # Turn 5: Answer update & red flag screening
    mgr.update_with_delta(PatientStateDelta(
        conversation_id=cid,
        new_input="No blood in vomit, but I am 8 weeks pregnant.",
        new_negations=["vomit_blood"],
        new_answers={"pregnant": True, "vomit_blood": False}
    ))
    assert mgr.state.answers["pregnant"] is True
    assert "vomit_blood" in mgr.state.negated_symptoms
    
    # Turn 6: Vitals update
    mgr.update_with_delta(PatientStateDelta(
        conversation_id=cid,
        new_input="Vitals measured: SpO2 98%, Blood Pressure 115/75, Pulse 82.",
        new_vitals=Vitals(spo2_percent=98.0, bp_systolic=115, bp_diastolic=75, pulse_rate=82)
    ))
    assert mgr.state.vitals.spo2_percent == 98.0
    assert mgr.state.vitals.bp_systolic == 115


def test_patient_state_determinism_byte_for_byte():
    """Runs the exact same multi-turn sequence twice and asserts byte-for-byte identity."""
    cid = "det_session_fixed"
    ts = "2026-08-16T12:00:00.000000"
    
    def run_sequence():
        mgr = PatientStateManager(conversation_id=cid, patient_id="test_patient_001", language="en")
        mgr.state.created_at = ts
        mgr.state.updated_at = ts
        
        deltas = [
            PatientStateDelta(conversation_id=cid, new_input="I have abdominal pain since yesterday.", new_symptoms={"abdominal_pain": SymptomDetail(present=True, duration="yesterday")}, timestamp=ts),
            PatientStateDelta(conversation_id=cid, new_input="Also nausea and vomiting.", new_symptoms={"nausea": SymptomDetail(present=True)}, timestamp=ts),
            PatientStateDelta(conversation_id=cid, new_input="Correction: pain started this morning.", new_symptoms={"abdominal_pain": SymptomDetail(present=True, duration="this morning")}, timestamp=ts)
        ]
        for d in deltas:
            state = mgr.update_with_delta(d)
            state.updated_at = ts
        return json.dumps(mgr.get_state().model_dump(), sort_keys=True)

    run1 = run_sequence()
    run2 = run_sequence()
    
    assert run1 == run2
