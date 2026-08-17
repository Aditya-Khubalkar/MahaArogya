"""
MahaArogya — Novel Clinical Boundary Spot-Check
Tests an un-seen borderline clinical scenario testing exact threshold comparisons (SpO2=92.0%, SBP=90, HR=120, Age=72).
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.patient_state.schemas import SymptomDetail, Vitals
from ai.patient_state.state_manager import PatientStateManager
from ai.triage.classifier import TriageClassifier


def run_novel_spotcheck():
    print("=" * 70)
    print("  MahaArogya Novel Clinical Boundary Spot-Check")
    print("=" * 70)
    
    # Construct Novel Scenario
    input_text = "72-year-old patient complaining of mild nausea and indigestion since morning, feeling cold sweating. SpO2 is 92.0%, Blood Pressure is 90/60 mmHg, Pulse Rate is 120 bpm."
    
    mgr = PatientStateManager("novel_spotcheck_01", language="en")
    state = mgr.get_state()
    state.age_years = 72.0
    state.vitals = Vitals(
        spo2_percent=92.0,      # Exact 92.0% threshold boundary!
        bp_systolic=90,         # Exact 90 mmHg threshold boundary!
        bp_diastolic=60,
        pulse_rate=120          # Exact 120 bpm threshold boundary!
    )
    state.symptoms["nausea"] = SymptomDetail(present=True, severity="mild")
    state.symptoms["indigestion"] = SymptomDetail(present=True, severity="mild")
    state.answers = {
        "diaphoresis": True,    # Cold sweating
        "diabetic": True
    }
    
    gold_standard = "EMERGENCY"
    clinical_reasoning = (
        "ESI Level 2 (EMERGENCY). Elderly 72yo diabetic presenting with acute nausea & diaphoresis "
        "and borderline vitals (SpO2=92.0%, SBP=90 mmHg, HR=120 bpm). "
        "Must trigger EMERGENCY for atypical silent MI / acute coronary syndrome evaluation."
    )
    
    classifier = TriageClassifier()
    decision = classifier.classify(state)
    
    actual_pred = decision.triage_category
    matched = (actual_pred == gold_standard)
    
    print(f"• Construct Input Text:      '{input_text}'")
    print(f"• Age / Gender:              {state.age_years} years old")
    print(f"• Boundary Vitals Tested:    SpO2 = {state.vitals.spo2_percent}%, SBP = {state.vitals.bp_systolic} mmHg, HR = {state.vitals.pulse_rate} bpm")
    print(f"• Symptoms & Answers:        {list(state.symptoms.keys())} | Diaphoresis={state.answers.get('diaphoresis')}")
    print("-" * 70)
    print(f"• Clinical Gold Standard:    {gold_standard}")
    print(f"• Medical Rationale:         {clinical_reasoning}")
    print("-" * 70)
    print(f"• Classifier Actual Output:  {actual_pred} (Confidence: {decision.triage_confidence})")
    print(f"• Triggered Red-Flag Rules:  {decision.triggered_rule_ids}")
    print(f"• Rule Explanation:          {decision.explanation}")
    print("-" * 70)
    
    if matched:
        print("  [VERIFIED MATCH]: Classifier matched the Clinical Gold Standard!")
    else:
        print("  [DISCREPANCY]: Classifier output differed from Clinical Gold Standard.")
    print("=" * 70)


if __name__ == "__main__":
    run_novel_spotcheck()
