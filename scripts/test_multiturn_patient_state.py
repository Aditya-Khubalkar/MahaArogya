"""
MahaArogya — Multi-Turn PatientState Verification & Determinism Audit
Tests state accumulation, symptom corrections, off-topic handling, answer updating, and byte-for-byte determinism.
"""

import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.patient_state.schemas import PatientStateDelta, SymptomDetail, Vitals
from ai.patient_state.state_manager import PatientStateManager


def run_multiturn_verification():
    print("=" * 80)
    print("  MahaArogya Multi-Turn PatientState Memory Accumulation Audit")
    print("=" * 80)
    
    # Session setup
    conversation_id = "test_multiturn_session_99"
    fixed_timestamp = "2026-08-16T12:00:00.000000"
    
    turns = [
        # Turn 1: Initial complaint
        PatientStateDelta(
            conversation_id=conversation_id,
            new_input="I have abdominal pain since yesterday, it's mild.",
            new_symptoms={
                "abdominal_pain": SymptomDetail(present=True, severity="mild", duration="since yesterday", location="abdomen")
            },
            timestamp=fixed_timestamp
        ),
        # Turn 2: Add related symptom
        PatientStateDelta(
            conversation_id=conversation_id,
            new_input="Also feeling nauseous and vomited 2 times.",
            new_symptoms={
                "nausea": SymptomDetail(present=True, severity="moderate"),
                "vomiting": SymptomDetail(present=True, frequency="2 times")
            },
            timestamp=fixed_timestamp
        ),
        # Turn 3: Correction / Update of duration & severity
        PatientStateDelta(
            conversation_id=conversation_id,
            new_input="Actually the pain started this morning, not yesterday, and it's severe now.",
            new_symptoms={
                "abdominal_pain": SymptomDetail(present=True, severity="severe", duration="this morning", location="abdomen")
            },
            timestamp=fixed_timestamp
        ),
        # Turn 4: Off-topic / irrelevant chatter
        PatientStateDelta(
            conversation_id=conversation_id,
            new_input="My neighbor told me to drink ginger tea for stomach ache.",
            timestamp=fixed_timestamp
        ),
        # Turn 5: Red-flag screening question confirmation
        PatientStateDelta(
            conversation_id=conversation_id,
            new_input="No blood in vomit, but I am 8 weeks pregnant.",
            new_negations=["vomit_blood"],
            new_answers={"pregnant": True, "vomit_blood": False},
            timestamp=fixed_timestamp
        ),
        # Turn 6: Vitals recording
        PatientStateDelta(
            conversation_id=conversation_id,
            new_input="Vitals measured: SpO2 98%, Blood Pressure 115/75, Pulse 82.",
            new_vitals=Vitals(spo2_percent=98.0, bp_systolic=115, bp_diastolic=75, pulse_rate=82),
            timestamp=fixed_timestamp
        )
    ]
    
    mgr = PatientStateManager(conversation_id=conversation_id, patient_id="test_patient_001", language="en")
    
    # Override dynamic state timestamps for deterministic audit comparison
    mgr.state.created_at = fixed_timestamp
    mgr.state.updated_at = fixed_timestamp
    
    print("\n--- EXECUTING 6-TURN MULTI-TURN CONVERSATION ---")
    for i, delta in enumerate(turns, start=1):
        state = mgr.update_with_delta(delta)
        state.updated_at = fixed_timestamp  # freeze timestamp for comparison
        
        # Serialize raw state object
        raw_state_dict = state.model_dump()
        print(f"\n==================== TURN {i} RAW STATE OUTPUT ====================")
        print(f"User Input: '{delta.new_input}'")
        print(json.dumps(raw_state_dict, indent=2, ensure_ascii=False))
        print("=" * 67)
        
    return mgr.get_state().model_dump()


def run_determinism_check():
    print("\n" + "=" * 80)
    print("  DETERMINISM VERIFICATION: Executing exact same sequence twice")
    print("=" * 80)
    
    run1_json = run_multiturn_verification_silent("session_det_1")
    run2_json = run_multiturn_verification_silent("session_det_1")
    
    is_identical = (run1_json == run2_json)
    
    print(f"Run 1 Byte Length: {len(run1_json)} chars")
    print(f"Run 2 Byte Length: {len(run2_json)} chars")
    print(f"Byte-for-Byte Identical Match: {is_identical}")
    
    if is_identical:
        print("[VERIFIED DETERMINISM]: PatientState accumulation is 100% deterministic & byte-for-byte identical across runs!")
    else:
        print("[FAIL]: Non-deterministic behavior detected!")
        

def run_multiturn_verification_silent(cid: str) -> str:
    fixed_ts = "2026-08-16T12:00:00.000000"
    mgr = PatientStateManager(conversation_id=cid, patient_id="test_patient_001", language="en")
    mgr.state.created_at = fixed_ts
    mgr.state.updated_at = fixed_ts
    
    deltas = [
        PatientStateDelta(conversation_id=cid, new_input="I have abdominal pain since yesterday, it's mild.", new_symptoms={"abdominal_pain": SymptomDetail(present=True, severity="mild", duration="since yesterday", location="abdomen")}, timestamp=fixed_ts),
        PatientStateDelta(conversation_id=cid, new_input="Also feeling nauseous and vomited 2 times.", new_symptoms={"nausea": SymptomDetail(present=True, severity="moderate"), "vomiting": SymptomDetail(present=True, frequency="2 times")}, timestamp=fixed_ts),
        PatientStateDelta(conversation_id=cid, new_input="Actually the pain started this morning, not yesterday, and it's severe now.", new_symptoms={"abdominal_pain": SymptomDetail(present=True, severity="severe", duration="this morning", location="abdomen")}, timestamp=fixed_ts),
        PatientStateDelta(conversation_id=cid, new_input="My neighbor told me to drink ginger tea for stomach ache.", timestamp=fixed_ts),
        PatientStateDelta(conversation_id=cid, new_input="No blood in vomit, but I am 8 weeks pregnant.", new_negations=["vomit_blood"], new_answers={"pregnant": True, "vomit_blood": False}, timestamp=fixed_ts),
        PatientStateDelta(conversation_id=cid, new_input="Vitals measured: SpO2 98%, Blood Pressure 115/75, Pulse 82.", new_vitals=Vitals(spo2_percent=98.0, bp_systolic=115, bp_diastolic=75, pulse_rate=82), timestamp=fixed_ts)
    ]
    
    for d in deltas:
        state = mgr.update_with_delta(d)
        state.updated_at = fixed_ts
        
    return json.dumps(mgr.get_state().model_dump(), sort_keys=True)


if __name__ == "__main__":
    run_multiturn_verification()
    run_determinism_check()
