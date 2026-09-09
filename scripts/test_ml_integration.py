import sys
sys.path.append(r"C:\MahaArogya")

import uuid
from ai.patient_state.schemas import PatientState, Vitals, SymptomDetail
from ai.triage.classifier import TriageClassifier

def run_tests():
    print("Initializing TriageClassifier (XGBoost)...")
    classifier = TriageClassifier(ml_model_type="xgboost")
    passed = 0
    total = 0

    def assert_eq(expected, actual, name):
        nonlocal passed, total
        total += 1
        if expected == actual:
            print(f"PASS: {name} (Expected {expected}, Got {actual})")
            passed += 1
        else:
            print(f"FAIL: {name} (Expected {expected}, Got {actual})")

    cid = lambda: str(uuid.uuid4())

    # 1. Emergency red flag case
    print("\n--- Test 1: Emergency Red Flag ---")
    state1 = PatientState(
        conversation_id=cid(),
        language="en",
        age_years=65.0,
        gender="Male",
        vitals=Vitals(bp_systolic=80), # Hypotension (red flag)
        symptoms={"chest_pain": SymptomDetail(severity="severe")}
    )
    res1 = classifier.classify(state1)
    assert_eq("EMERGENCY", res1.triage_category, "Triage Category")
    assert_eq(1.0, res1.triage_confidence, "Confidence")
    print(f"Explanation: {res1.explanation}")

    # 2. Normal fever case
    print("\n--- Test 2: Normal Fever ---")
    state2 = PatientState(
        conversation_id=cid(),
        language="en",
        age_years=25.0,
        gender="Female",
        vitals=Vitals(temperature_f=99.5, pulse_rate=80),
        symptoms={"fever": SymptomDetail(severity="mild")}
    )
    res2 = classifier.classify(state2)
    total += 1
    if res2.triage_category in ["ROUTINE", "PRIORITY", "URGENT"]:
        print(f"PASS: Non-emergency routing (Got {res2.triage_category})")
        passed += 1
    else:
        print(f"FAIL: Non-emergency routing (Got {res2.triage_category})")
    print(f"Explanation: {res2.explanation}")

    # 3. Missing vitals case
    print("\n--- Test 3: Missing Vitals ---")
    state3 = PatientState(
        conversation_id=cid(),
        language="en",
        age_years=40.0,
        gender="Male",
        vitals=Vitals(),
        symptoms={"headache": SymptomDetail(severity="moderate")}
    )
    res3 = classifier.classify(state3)
    total += 1
    if res3.triage_category in ["ROUTINE", "PRIORITY", "URGENT"]:
        print(f"PASS: Handled missing vitals (Got {res3.triage_category})")
        passed += 1
    else:
        print(f"FAIL: Handled missing vitals (Got {res3.triage_category})")
    print(f"Explanation: {res3.explanation}")

    # 4. Unknown symptom case
    print("\n--- Test 4: Unknown Symptom ---")
    state4 = PatientState(
        conversation_id=cid(),
        language="en",
        age_years=30.0,
        gender="Female",
        vitals=Vitals(pulse_rate=75),
        symptoms={"weird_feeling": SymptomDetail(severity="mild")}
    )
    res4 = classifier.classify(state4)
    total += 1
    if res4.triage_category in ["ROUTINE", "PRIORITY"]:
        print(f"PASS: Safe fallback for unknown symptom (Got {res4.triage_category})")
        passed += 1
    else:
        print(f"FAIL: Safe fallback for unknown symptom (Got {res4.triage_category})")
    print(f"Explanation: {res4.explanation}")

    # 5. Language variations (just checking robust inputs don't crash)
    print("\n--- Test 5: Multi-Language Safety Checks ---")
    state5 = PatientState(
        conversation_id=cid(),
        language="mr",
        original_input_history=["mala khokla yetoy"],
        age_years=50.0,
        gender="Male",
        vitals=Vitals(),
        symptoms={"cough": SymptomDetail(severity="mild")}
    )
    res5 = classifier.classify(state5)
    total += 1
    if res5.triage_category in ["ROUTINE", "PRIORITY", "URGENT"]:
        print(f"PASS: Marathi input handled (Got {res5.triage_category})")
        passed += 1
    else:
        print(f"FAIL: Marathi input handled (Got {res5.triage_category})")
    print(f"Explanation: {res5.explanation}")

    print(f"\nCompleted {total} tests. {passed} passed.")

if __name__ == "__main__":
    import time
    start = time.time()
    run_tests()
    print(f"Inference latency: {time.time() - start:.4f} seconds")
