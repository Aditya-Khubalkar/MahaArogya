"""
MahaArogya — Isolated SpO2 Vital Sign Boundary Test
Tests exact SpO2 operator (< 92.0 vs <= 92.0) on a routine chief complaint (mild fatigue).
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.patient_state.schemas import SymptomDetail, Vitals
from ai.patient_state.state_manager import PatientStateManager
from ai.triage.classifier import TriageClassifier


def test_isolated_spo2_boundary():
    print("=" * 70)
    print("  Isolated SpO2 Vital Sign Boundary Operator Test")
    print("=" * 70)
    
    classifier = TriageClassifier()
    
    # -------------------------------------------------------------------------
    # TEST 1: SpO2 = 92.0% exactly (Mild fatigue, no red-flag symptoms)
    # Expected: URGENT (since 92.0% is NOT < 92.0%; 92-95% = URGENT)
    # -------------------------------------------------------------------------
    mgr1 = PatientStateManager("spo2_test_92_0", language="en")
    state1 = mgr1.get_state()
    state1.symptoms["fatigue"] = SymptomDetail(present=True, severity="mild")
    state1.vitals = Vitals(spo2_percent=92.0, bp_systolic=120, pulse_rate=75)
    
    dec1 = classifier.classify(state1)
    
    print("\n[TEST 1] Chief Complaint: 'Mild fatigue' | SpO2 = 92.0% (Exact Boundary)")
    print(f"  • Expected Category: URGENT (since 92.0% is NOT < 92.0%)")
    print(f"  • Actual Category:   {dec1.triage_category}")
    print(f"  • Triggered Rules:   {dec1.triggered_rule_ids}")
    print(f"  • Explanation:       {dec1.explanation}")
    match1 = (dec1.triage_category == "URGENT")
    print(f"  • Status:            {'[OK] PASSED - Correctly classified as URGENT' if match1 else '[FAIL] Off-by-one error (Incorrectly classified as ' + dec1.triage_category + ')'}")

    # -------------------------------------------------------------------------
    # TEST 2: SpO2 = 91.9% (Mild fatigue, no red-flag symptoms)
    # Expected: EMERGENCY (since 91.9% IS < 92.0%)
    # -------------------------------------------------------------------------
    mgr2 = PatientStateManager("spo2_test_91_9", language="en")
    state2 = mgr2.get_state()
    state2.symptoms["fatigue"] = SymptomDetail(present=True, severity="mild")
    state2.vitals = Vitals(spo2_percent=91.9, bp_systolic=120, pulse_rate=75)
    
    dec2 = classifier.classify(state2)
    
    print("\n[TEST 2] Chief Complaint: 'Mild fatigue' | SpO2 = 91.9% (Below Boundary)")
    print(f"  • Expected Category: EMERGENCY (since 91.9% IS < 92.0%)")
    print(f"  • Actual Category:   {dec2.triage_category}")
    print(f"  • Triggered Rules:   {dec2.triggered_rule_ids}")
    print(f"  • Explanation:       {dec2.explanation}")
    match2 = (dec2.triage_category == "EMERGENCY")
    print(f"  • Status:            {'[OK] PASSED - Correctly classified as EMERGENCY' if match2 else '[FAIL] Missed emergency override'}")

    print("\n" + "=" * 70)
    print(f"  OVERALL BOUNDARY TEST RESULT: {'PASSED BOTH TESTS' if (match1 and match2) else 'DISCREPANCY FOUND'}")
    print("=" * 70)


if __name__ == "__main__":
    test_isolated_spo2_boundary()
