"""
MahaArogya — Spec Section 5 Benchmark Evaluation Engine
Includes ASR (15 samples), Extraction (25 samples), Standard Triage (20 samples),
and Ambiguous Clinical Edge Cases (18 samples with Fail-Safe / Fail-Unsafe safety audit).
"""

import time
import json
import sys
import torch
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.nlp.extractor import MedicalExtractor
from ai.triage.classifier import TriageClassifier
from ai.patient_state.state_manager import PatientStateManager
from ai.patient_state.schemas import SymptomDetail, Vitals


def compute_wer_cer(ref: str, hyp: str) -> tuple[float, float]:
    """Calculates Word Error Rate (WER) and Character Error Rate (CER) with text normalization."""
    import string
    translator = str.maketrans("", "", string.punctuation)
    
    ref_clean = ref.lower().translate(translator).strip()
    hyp_clean = hyp.lower().translate(translator).strip()
    
    ref_words = ref_clean.split()
    hyp_words = hyp_clean.split()
    
    if not ref_words:
        return (0.0 if not hyp_words else 1.0, 0.0 if not hyp_words else 1.0)
        
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1): d[i][0] = i
    for j in range(len(hyp_words) + 1): d[0][j] = j
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = 1 + min(d[i-1][j], d[i][j-1], d[i-1][j-1])
    wer = d[len(ref_words)][len(hyp_words)] / len(ref_words)
    
    ref_chars = list(ref_clean.replace(" ", ""))
    hyp_chars = list(hyp_clean.replace(" ", ""))
    if not ref_chars:
        return (wer, 0.0 if not hyp_chars else 1.0)
        
    dc = [[0] * (len(hyp_chars) + 1) for _ in range(len(ref_chars) + 1)]
    for i in range(len(ref_chars) + 1): dc[i][0] = i
    for j in range(len(hyp_chars) + 1): dc[0][j] = j
    for i in range(1, len(ref_chars) + 1):
        for j in range(1, len(hyp_chars) + 1):
            if ref_chars[i-1] == hyp_chars[j-1]:
                dc[i][j] = dc[i-1][j-1]
            else:
                dc[i][j] = 1 + min(dc[i-1][j], dc[i][j-1], dc[i-1][j-1])
    cer = dc[len(ref_chars)][len(hyp_chars)] / len(ref_chars)
    return round(wer, 4), round(cer, 4)


def evaluate_asr_suite():
    print("\n" + "=" * 75)
    print(" 1. EVALUATING ASR SUBSYSTEM (faster-whisper CUDA on 15 Audio Utterances)")
    print("=" * 75)
    
    asr_test_file = Path("evaluation/test_sets/asr_test_set.json")
    if not asr_test_file.exists():
        raise FileNotFoundError(f"ASR test set not found at {asr_test_file}")
        
    with open(asr_test_file, "r", encoding="utf-8") as f:
        test_samples = json.load(f)
        
    from ai.asr.service import get_asr_service
    asr_svc = get_asr_service()
    
    wers, cers, latencies = [], [], []
    sample_results = []
    
    vram_before_mb = 0.0
    if torch.cuda.is_available():
        free_b, tot_b = torch.cuda.mem_get_info(0)
        vram_before_mb = (tot_b - free_b) / (1024 * 1024)
        
    print(f"{'ID':<12} | {'Ref Length':<10} | {'WER':<8} | {'CER':<8} | {'Latency':<8} | {'Reference vs Hypothesis'}")
    print("-" * 95)
    
    for s in test_samples:
        t0 = time.perf_counter()
        res = asr_svc.transcribe(s["audio_path"], language=s.get("lang", "en"))
        elapsed = time.perf_counter() - t0
        
        wer, cer = compute_wer_cer(s["reference"], res.transcript)
        wers.append(wer)
        cers.append(cer)
        latencies.append(elapsed)
        
        sample_results.append({
            "id": s["id"],
            "reference": s["reference"],
            "hypothesis": res.transcript,
            "wer": wer,
            "cer": cer,
            "latency_sec": round(elapsed, 3)
        })
        
        ref_short = (s["reference"][:25] + "..") if len(s["reference"]) > 25 else s["reference"]
        hyp_short = (res.transcript[:25] + "..") if len(res.transcript) > 25 else res.transcript
        print(f"{s['id']:<12} | {len(s['reference'].split()):<10} | {wer*100:6.1f}% | {cer*100:6.1f}% | {elapsed:6.3f}s | '{ref_short}' vs '{hyp_short}'")

    vram_after_mb = 0.0
    if torch.cuda.is_available():
        free_b2, tot_b2 = torch.cuda.mem_get_info(0)
        vram_after_mb = (tot_b2 - free_b2) / (1024 * 1024)
        
    mean_wer = round(sum(wers) / len(wers), 4)
    mean_cer = round(sum(cers) / len(cers), 4)
    mean_latency = round(sum(latencies) / len(latencies), 3)
    
    print("-" * 95)
    print(f"  [SUMMARY]: Evaluated {len(test_samples)} audio clips.")
    print(f"  [SUMMARY]: Mean WER: {mean_wer*100:.2f}% | Mean CER: {mean_cer*100:.2f}% | Mean Latency: {mean_latency:.3f}s")
    print(f"  [SUMMARY]: Total GPU Memory Used: {vram_after_mb:.2f} MB (Delta: {vram_after_mb - vram_before_mb:.2f} MB)")
    
    return {
        "mean_wer": mean_wer,
        "mean_cer": mean_cer,
        "mean_latency_sec": mean_latency,
        "vram_used_mb": round(vram_after_mb, 2),
        "vram_delta_mb": round(vram_after_mb - vram_before_mb, 2),
        "sample_count": len(test_samples),
        "per_sample": sample_results
    }


def evaluate_extraction_suite():
    print("\n" + "=" * 75)
    print(" 2. EVALUATING MEDICAL ENTITY EXTRACTOR (25 Test Sentences)")
    print("=" * 75)
    
    ext_file = Path("evaluation/test_sets/extraction_test_set.json")
    if not ext_file.exists():
        raise FileNotFoundError(f"Extraction test set not found at {ext_file}")
        
    with open(ext_file, "r", encoding="utf-8") as f:
        test_samples = json.load(f)
        
    extractor = MedicalExtractor()
    total_tp, total_fp, total_fn = 0, 0, 0
    latencies = []
    
    print(f"{'ID':<10} | {'TP/FP/FN':<10} | {'Expected Symptoms':<30} | {'Extracted Symptoms'}")
    print("-" * 95)
    
    for s in test_samples:
        t0 = time.perf_counter()
        delta = extractor.extract("eval_session", s["text"])
        elapsed = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed)
        
        extracted = list(delta.new_symptoms.keys())
        expected = s["expected_symptoms"]
        
        tp = sum(1 for k in extracted if k in expected)
        fp = sum(1 for k in extracted if k not in expected)
        fn = sum(1 for k in expected if k not in extracted)
        
        total_tp += tp
        total_fp += fp
        total_fn += fn
        
        exp_str = ",".join(expected[:2])
        ext_str = ",".join(extracted[:2]) if extracted else "NONE"
        print(f"{s['id']:<10} | {tp}/{fp}/{fn:<6} | {exp_str:<30} | {ext_str}")

    precision = round(total_tp / max(1, total_tp + total_fp), 4)
    recall = round(total_tp / max(1, total_tp + total_fn), 4)
    f1_score = round(2 * (precision * recall) / max(1e-5, precision + recall), 4)
    mean_latency_ms = round(sum(latencies) / len(latencies), 2)
    
    print("-" * 95)
    print(f"  [SUMMARY]: Evaluated {len(test_samples)} sentences.")
    print(f"  [SUMMARY]: Micro Precision: {precision*100:.1f}% | Recall: {recall*100:.1f}% | F1-Score: {f1_score*100:.1f}% | Avg Latency: {mean_latency_ms:.2f}ms")
    
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "mean_latency_ms": mean_latency_ms,
        "sample_count": len(test_samples)
    }


def evaluate_triage_suite():
    print("\n" + "=" * 75)
    print(" 3. EVALUATING STANDARD TRIAGE SUITE (20 Clear Cases)")
    print("=" * 75)
    
    trg_file = Path("evaluation/test_sets/triage_test_set.json")
    if not trg_file.exists():
        raise FileNotFoundError(f"Triage test set not found at {trg_file}")
        
    with open(trg_file, "r", encoding="utf-8") as f:
        test_samples = json.load(f)
        
    classifier = TriageClassifier()
    tp, fp, tn, fn = 0, 0, 0, 0
    latencies = []
    
    print(f"{'ID':<10} | {'Actual vs Pred':<22} | {'Symptom':<20} | {'Status'}")
    print("-" * 95)
    
    for s in test_samples:
        t0 = time.perf_counter()
        mgr = PatientStateManager(conversation_id=f"eval_trg_{s['id']}")
        mgr.state.symptoms[s["symptom"]] = SymptomDetail(severity=s["severity"], present=True)
        decision = classifier.classify(mgr.state)
        elapsed = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed)
        
        pred_emergency = (decision.triage_category == "EMERGENCY")
        actual_emergency = s["is_emergency"]
        
        if actual_emergency and pred_emergency:
            tp += 1
            status = "[OK] TRUE POSITIVE"
        elif not actual_emergency and not pred_emergency:
            tn += 1
            status = "[OK] TRUE NEGATIVE"
        elif not actual_emergency and pred_emergency:
            fp += 1
            status = "[WARN] FALSE POSITIVE"
        else:
            fn += 1
            status = "[FAIL] FALSE NEGATIVE"
            
        act_str = "EMERGENCY" if actual_emergency else "NON-EMG"
        pred_str = decision.triage_category
        print(f"{s['id']:<10} | {act_str:<9} -> {pred_str:<10} | {s['symptom']:<20} | {status}")

    recall = round(tp / max(1, tp + fn), 4)
    precision = round(tp / max(1, tp + fp), 4)
    specificity = round(tn / max(1, tn + fp), 4)
    f1_score = round(2 * (precision * recall) / max(1e-5, precision + recall), 4)
    accuracy = round((tp + tn) / len(test_samples), 4)
    mean_latency_ms = round(sum(latencies) / len(latencies), 2)
    
    print("-" * 95)
    print(f"  [SUMMARY]: Confusion Matrix: TP={tp}, FP={fp}, TN={tn}, FN={fn}")
    print(f"  [SUMMARY]: Emergency Recall (Sensitivity): {recall*100:.1f}%")
    print(f"  [SUMMARY]: Precision: {precision*100:.1f}% | Specificity: {specificity*100:.1f}%")
    print(f"  [SUMMARY]: Overall Accuracy: {accuracy*100:.1f}% | F1-Score: {f1_score*100:.1f}% | Avg Latency: {mean_latency_ms:.2f}ms")
    
    return {
        "confusion_matrix": {"TP": tp, "FP": fp, "TN": tn, "FN": fn},
        "emergency_recall": recall,
        "precision": precision,
        "specificity": specificity,
        "accuracy": accuracy,
        "f1_score": f1_score,
        "mean_latency_ms": mean_latency_ms,
        "sample_count": len(test_samples)
    }


def evaluate_triage_edge_cases():
    print("\n" + "=" * 75)
    print(" 4. STRESS-TESTING AMBIGUOUS CLINICAL EDGE CASES (18 Scenarios)")
    print("=" * 75)
    
    edge_file = Path("evaluation/test_sets/triage_edge_cases.json")
    if not edge_file.exists():
        raise FileNotFoundError(f"Edge case test set not found at {edge_file}")
        
    with open(edge_file, "r", encoding="utf-8") as f:
        edge_samples = json.load(f)
        
    classifier = TriageClassifier()
    
    CATEGORY_ORDER = {"ROUTINE": 1, "PRIORITY": 2, "URGENT": 3, "EMERGENCY": 4}
    
    correct_count = 0
    fail_safe_count = 0  # Over-triage (cautious, acceptable for safety)
    fail_unsafe_count = 0  # Under-triage (dangerous, missing real emergency)
    
    audit_log = []
    
    print(f"{'ID':<8} | {'Gold Standard':<12} | {'Predicted':<12} | {'Safety Status':<22} | {'Category'}")
    print("-" * 95)
    
    for s in edge_samples:
        mgr = PatientStateManager(conversation_id=f"edge_{s['id']}")
        
        # Populate symptom & vitals & answers & age
        symptom_key = s["symptom"]
        mgr.state.symptoms[symptom_key] = SymptomDetail(severity=s["severity"], present=True)
        mgr.state.answers = s.get("answers", {})
        mgr.state.body_locations = s.get("body_locations", [])
        mgr.state.age_years = s.get("age_years")
        
        v_dict = s.get("vitals", {})
        if v_dict:
            mgr.state.vitals = Vitals(
                spo2_percent=v_dict.get("spo2_percent"),
                bp_systolic=v_dict.get("bp_systolic"),
                bp_diastolic=v_dict.get("bp_diastolic"),
                pulse_rate=v_dict.get("pulse_rate"),
                temperature_f=v_dict.get("temperature_f")
            )
            
        decision = classifier.classify(mgr.state)
        
        pred_cat = decision.triage_category
        gold_cat = s["gold_standard_category"]
        
        pred_val = CATEGORY_ORDER.get(pred_cat, 1)
        gold_val = CATEGORY_ORDER.get(gold_cat, 1)
        
        if pred_cat == gold_cat:
            correct_count += 1
            safety_status = "[OK] MATCH"
        elif pred_val > gold_val:
            fail_safe_count += 1
            safety_status = "[SAFE] OVER-TRIAGE"
        else:
            fail_unsafe_count += 1
            safety_status = "[UNSAFE] UNDER-TRIAGE"
            
        audit_log.append({
            "id": s["id"],
            "input_text": s["input_text"],
            "gold_standard": gold_cat,
            "predicted": pred_cat,
            "safety_status": safety_status,
            "clinical_rationale": s["clinical_rationale"]
        })
        
        cat_short = s["category"][:20]
        print(f"{s['id']:<8} | {gold_cat:<12} | {pred_cat:<12} | {safety_status:<22} | {cat_short}")

    total = len(edge_samples)
    match_pct = round((correct_count / total) * 100, 1)
    fail_safe_pct = round((fail_safe_count / total) * 100, 1)
    fail_unsafe_pct = round((fail_unsafe_count / total) * 100, 1)
    
    print("-" * 95)
    print(f"  [EDGE CASE AUDIT SUMMARY]: Evaluated {total} ambiguous clinical scenarios.")
    print(f"  [OK] Exact Matches: {correct_count} / {total} ({match_pct}%)")
    print(f"  [SAFE] Over-Triage (Fail-Safe / Cautious Escalation): {fail_safe_count} / {total} ({fail_safe_pct}%)")
    print(f"  [ALERT] Under-Triage (Fail-Unsafe / Missed Urgency): {fail_unsafe_count} / {total} ({fail_unsafe_pct}%)")
    print("-" * 95)
    
    return {
        "sample_count": total,
        "exact_matches": correct_count,
        "match_percentage": match_pct,
        "fail_safe_overtriage_count": fail_safe_count,
        "fail_safe_percentage": fail_safe_pct,
        "fail_unsafe_undertriage_count": fail_unsafe_count,
        "fail_unsafe_percentage": fail_unsafe_pct,
        "audit_details": audit_log
    }


def run_full_suite():
    print("=" * 75)
    print("  MahaArogya Full Spec Section 5 Benchmark Evaluation Suite")
    print("=" * 75)
    
    asr_res = evaluate_asr_suite()
    ext_res = evaluate_extraction_suite()
    std_trg_res = evaluate_triage_suite()
    edge_res = evaluate_triage_edge_cases()
    
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "asr_metrics": {
            "sample_count": asr_res["sample_count"],
            "mean_wer": f"{asr_res['mean_wer']*100:.2f}%",
            "mean_cer": f"{asr_res['mean_cer']*100:.2f}%",
            "mean_latency_sec": f"{asr_res['mean_latency_sec']}s",
            "vram_used_mb": f"{asr_res['vram_used_mb']} MB",
            "vram_delta_mb": f"{asr_res['vram_delta_mb']} MB"
        },
        "medical_extraction_metrics": {
            "sample_count": ext_res["sample_count"],
            "precision": f"{ext_res['precision']*100:.1f}%",
            "recall": f"{ext_res['recall']*100:.1f}%",
            "f1_score": f"{ext_res['f1_score']*100:.1f}%",
            "mean_latency_ms": f"{ext_res['mean_latency_ms']}ms"
        },
        "standard_triage_metrics": {
            "sample_count": std_trg_res["sample_count"],
            "emergency_recall": f"{std_trg_res['emergency_recall']*100:.1f}%",
            "specificity": f"{std_trg_res['specificity']*100:.1f}%",
            "overall_accuracy": f"{std_trg_res['accuracy']*100:.1f}%"
        },
        "edge_case_triage_audit": {
            "sample_count": edge_res["sample_count"],
            "exact_matches": edge_res["exact_matches"],
            "match_percentage": f"{edge_res['match_percentage']}%",
            "fail_safe_overtriage": f"{edge_res['fail_safe_overtriage_count']} ({edge_res['fail_safe_percentage']}%)",
            "fail_unsafe_undertriage": f"{edge_res['fail_unsafe_undertriage_count']} ({edge_res['fail_unsafe_percentage']}%)",
            "audit_details": edge_res["audit_details"]
        }
    }
    
    out_file = Path("evaluation/eval_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 75)
    print("  FINAL EXPANDED BENCHMARK METRICS SUMMARY")
    print("=" * 75)
    print(f"  • ASR Mean WER / CER: {report['asr_metrics']['mean_wer']} / {report['asr_metrics']['mean_cer']} (15 Audio Samples, Latency: {report['asr_metrics']['mean_latency_sec']})")
    print(f"  • Medical Extraction F1: {report['medical_extraction_metrics']['f1_score']} (25 Sentences, Latency: {report['medical_extraction_metrics']['mean_latency_ms']})")
    print(f"  • Edge Case Exact Matches: {report['edge_case_triage_audit']['match_percentage']} (18 Ambiguous Cases)")
    print(f"  • Fail-Safe Over-Triage Rate: {report['edge_case_triage_audit']['fail_safe_overtriage']}")
    print(f"  • Fail-Unsafe Under-Triage Rate: {report['edge_case_triage_audit']['fail_unsafe_undertriage']}")
    print(f"  • Total GPU VRAM Allocated: {report['asr_metrics']['vram_used_mb']} (Model Delta: {report['asr_metrics']['vram_delta_mb']})")
    print("=" * 75)
    return report


if __name__ == "__main__":
    run_full_suite()
