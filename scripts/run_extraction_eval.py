import json
import sys
sys.path.append(r"C:\MahaArogya")

from ai.nlp.extractor import MedicalExtractor

dataset_path = r"C:\MahaArogya\data\test\extraction_adversarial.json"

with open(dataset_path, "r", encoding="utf-8") as f:
    tests = json.load(f)

extractor = MedicalExtractor()

metrics = {
    "symptom_tp": 0,
    "symptom_fp": 0,
    "symptom_fn": 0,
    "vital_correct": 0,
    "vital_total": 0,
    "emergency_tp": 0,
    "emergency_fn": 0,
    "lang_perf": {}
}

emergency_symptoms = ["breathlessness", "stroke_symptoms", "cardiac_emergency", "altered_consciousness", "severe_bleeding", "anaphylaxis"]

for test in tests:
    lang = test["language"]
    if lang not in metrics["lang_perf"]:
        metrics["lang_perf"][lang] = {"tp": 0, "fn": 0, "fp": 0, "vital_correct": 0, "vital_total": 0}
        
    res = extractor.extract("test", test["text"])
    
    extracted_symp = list(res.new_symptoms.keys())
    # Negated symptoms should not count as present
    for n in res.new_negations:
        if n in extracted_symp:
            extracted_symp.remove(n)
            
    expected_symp = test["expected_symptoms"]
    
    # Symptom metrics
    for s in expected_symp:
        if s in extracted_symp:
            metrics["symptom_tp"] += 1
            metrics["lang_perf"][lang]["tp"] += 1
            if s in emergency_symptoms:
                metrics["emergency_tp"] += 1
        else:
            metrics["symptom_fn"] += 1
            metrics["lang_perf"][lang]["fn"] += 1
            if s in emergency_symptoms:
                metrics["emergency_fn"] += 1
                
    for s in extracted_symp:
        if s not in expected_symp:
            metrics["symptom_fp"] += 1
            metrics["lang_perf"][lang]["fp"] += 1
            
    # Vital metrics
    exp_vit = test["expected_vitals"]
    v = res.new_vitals
    if exp_vit:
        metrics["vital_total"] += len(exp_vit)
        metrics["lang_perf"][lang]["vital_total"] += len(exp_vit)
        
        if "spo2" in exp_vit and v and v.spo2_percent == exp_vit["spo2"]:
            metrics["vital_correct"] += 1
            metrics["lang_perf"][lang]["vital_correct"] += 1
        if "heart_rate" in exp_vit and v and v.pulse_rate == exp_vit["heart_rate"]:
            metrics["vital_correct"] += 1
            metrics["lang_perf"][lang]["vital_correct"] += 1
        if "temperature" in exp_vit and v and v.temperature_f == exp_vit["temperature"]:
            metrics["vital_correct"] += 1
            metrics["lang_perf"][lang]["vital_correct"] += 1
        if "sys_bp" in exp_vit and v and v.bp_systolic == exp_vit["sys_bp"] and v.bp_diastolic == exp_vit["dia_bp"]:
            metrics["vital_correct"] += 1
            metrics["lang_perf"][lang]["vital_correct"] += 1

print(f"--- EXTRACTION EVALUATION REPORT ---")
print(f"Total Cases: {len(tests)}")
print(f"\n1. Symptom Extraction:")
precision = metrics['symptom_tp'] / (metrics['symptom_tp'] + metrics['symptom_fp']) if (metrics['symptom_tp'] + metrics['symptom_fp']) > 0 else 0
recall = metrics['symptom_tp'] / (metrics['symptom_tp'] + metrics['symptom_fn']) if (metrics['symptom_tp'] + metrics['symptom_fn']) > 0 else 0
print(f"Precision: {precision:.1%}")
print(f"Recall: {recall:.1%}")

print(f"\n2. Vital Extraction Accuracy:")
v_acc = metrics['vital_correct'] / metrics['vital_total'] if metrics['vital_total'] > 0 else 0
print(f"Accuracy: {v_acc:.1%} ({metrics['vital_correct']}/{metrics['vital_total']})")

print(f"\n3. Emergency Phrase Recall: MUST BE 100%")
e_rec = metrics['emergency_tp'] / (metrics['emergency_tp'] + metrics['emergency_fn']) if (metrics['emergency_tp'] + metrics['emergency_fn']) > 0 else 0
print(f"Recall: {e_rec:.1%} ({metrics['emergency_tp']}/{metrics['emergency_tp'] + metrics['emergency_fn']})")

print(f"\n4. Language-wise Performance:")
for l, data in metrics['lang_perf'].items():
    l_rec = data['tp'] / (data['tp'] + data['fn']) if (data['tp'] + data['fn']) > 0 else 1.0
    l_vacc = data['vital_correct'] / data['vital_total'] if data['vital_total'] > 0 else 1.0
    print(f" - {l.upper()}: Symptom Recall = {l_rec:.1%} | Vital Accuracy = {l_vacc:.1%}")
