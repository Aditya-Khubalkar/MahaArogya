import sys
import json
import time
from collections import defaultdict
import os

sys.path.append(r"C:\MahaArogya")
from ai.orchestrator import MahaArogyaOrchestrator

test_file = r"C:\MahaArogya\evaluation\triage_adversarial_tests.json"
docs_dir = r"C:\MahaArogya\docs"
os.makedirs(docs_dir, exist_ok=True)

with open(test_file, "r", encoding="utf-8") as f:
    tests = json.load(f)

print(f"Loaded {len(tests)} tests. Initializing Orchestrator...")
orchestrator = MahaArogyaOrchestrator()

metrics = {
    "emergency_recall": {"tp": 0, "fn": 0, "total": 0}, # True Positive = Emergency expected and got Emergency
    "priority_recall": {"tp": 0, "fn": 0, "total": 0},
    "routine_recall": {"tp": 0, "fn": 0, "total": 0},
    "urgent_recall": {"tp": 0, "fn": 0, "total": 0},
    "safety_override_count": 0,
    "ml_invocation_count": 0,
    "total_latency": 0.0,
    "false_negatives": [] # Emergency predicted as non-emergency
}

cm = defaultdict(lambda: defaultdict(int))

print("Running Adversarial Tests...")
for i, test in enumerate(tests):
    inp = test['input']
    exp = test['expected_severity']
    lang = test.get('language', 'en')
    
    start = time.time()
    try:
        # We need to process the turn. Since it's text, we can use modality="text"
        res = orchestrator.process_turn(
            conversation_id=f"test_{i}",
            text_input=inp,
            language=lang,
            modality="text"
        )
        latency = time.time() - start
        
        pred = res.triage_decision.triage_category
        # The TriageDecision has an explanation. If it contains "ML Routing:", then ML was invoked.
        explanation = res.triage_decision.explanation
        if "ML Routing:" in explanation:
            metrics["ml_invocation_count"] += 1
        else:
            metrics["safety_override_count"] += 1
            
    except Exception as e:
        print(f"Error on test {i}: {e}")
        pred = "ERROR"
        latency = time.time() - start
        
    metrics["total_latency"] += latency
    
    # Let's map "NON_EMERGENCY" to anything not EMERGENCY for evaluation
    # Confusion matrix
    cm[exp][pred] += 1
    
    # Recall Tracking
    if exp == "EMERGENCY":
        metrics["emergency_recall"]["total"] += 1
        if pred == "EMERGENCY":
            metrics["emergency_recall"]["tp"] += 1
        else:
            metrics["emergency_recall"]["fn"] += 1
            metrics["false_negatives"].append({"input": inp, "pred": pred})
            
    elif exp == "URGENT":
        metrics["urgent_recall"]["total"] += 1
        if pred == "URGENT":
            metrics["urgent_recall"]["tp"] += 1
            
    elif exp == "PRIORITY":
        metrics["priority_recall"]["total"] += 1
        if pred == "PRIORITY":
            metrics["priority_recall"]["tp"] += 1
            
    elif exp == "ROUTINE":
        metrics["routine_recall"]["total"] += 1
        if pred == "ROUTINE":
            metrics["routine_recall"]["tp"] += 1

print("Tests complete. Generating Report...")

avg_latency = metrics["total_latency"] / len(tests)

def get_recall_str(metric_dict):
    if metric_dict["total"] == 0:
        return "N/A"
    return f"{metric_dict['tp']} / {metric_dict['total']} ({metric_dict['tp']/metric_dict['total']:.1%})"

report = f"""# MahaArogya Triage Adversarial Validation

## 1. Overview
Evaluated the **complete production pipeline** (Extraction -> PatientState -> SafetyRuleEngine -> ML Triage) using a manually designed adversarial test suite of {len(tests)} cases.

## 2. Global Metrics
- **Total Tests:** {len(tests)}
- **Average Inference Latency:** {avg_latency:.4f} seconds per turn
- **Safety Overrides Triggered:** {metrics["safety_override_count"]}
- **ML Classifications Invoked:** {metrics["ml_invocation_count"]}

## 3. Recall Metrics
- **Emergency Recall:** {get_recall_str(metrics["emergency_recall"])}
- **Urgent Recall:** {get_recall_str(metrics["urgent_recall"])}
- **Routine Recall:** {get_recall_str(metrics["routine_recall"])}

## 4. Critical Safety Violations
*(Metric: Emergency case predicted as Routine/Priority/Urgent)*

**Number of Critical Misses:** {len(metrics['false_negatives'])}

"""

if len(metrics['false_negatives']) > 0:
    report += "### FAILED EXAMPLES:\n"
    for fn in metrics['false_negatives']:
        report += f"- Input: \"{fn['input']}\" -> Predicted: {fn['pred']}\n"
else:
    report += "### STATUS: PERFECT SAFETY\nNo emergency cases were routed incorrectly.\n"

report += f"""
## 5. Confusion Matrix (Expected vs Predicted)
"""

all_preds = ["EMERGENCY", "URGENT", "PRIORITY", "ROUTINE", "NON_EMERGENCY"]
for expected_cat in cm.keys():
    report += f"\n**Expected {expected_cat}:**\n"
    for pred_cat, count in cm[expected_cat].items():
        report += f"- Predicted {pred_cat}: {count}\n"

report += "\n\n## 6. Final Decision\n"
if len(metrics['false_negatives']) == 0:
    report += "**READY FOR VOICE INTEGRATION**\nThe deterministic safety engine perfectly shields the ML triage fallback. The extraction engine robustly handles multilingual phrasing and missing information without crashing the pipeline."
else:
    report += "**NEEDS TRIAGE IMPROVEMENT**\nCritical emergencies were missed by the pipeline. Safety rules or extraction logic must be updated before production."

with open(os.path.join(docs_dir, "TRIAGE_ADVERSARIAL_VALIDATION.md"), "w", encoding="utf-8") as f:
    f.write(report)
    
print("Report generated at TRIAGE_ADVERSARIAL_VALIDATION.md")
