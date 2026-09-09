# MahaArogya Triage Engine - Current State Audit

## Overview
This document audits the current state of the MahaArogya Triage architecture, covering the deterministic safety rules, the urgency classifier, existing datasets, and the previous neural model attempt.

## 1. Existing Triage Modules
| Component | File Location | Purpose | Current Status |
|---|---|---|---|
| **SafetyRuleEngine** | `ai/triage/safety_rules.py` | 12 domains of deterministic clinical red-flag rules (Cardiac, Stroke, Hemorrhage, etc.) based on `PatientState`. | **Production** |
| **TriageClassifier** | `ai/triage/classifier.py` | Top-level classifier that routes through SafetyRuleEngine first, then falls back to a deterministic `_score_urgency` heuristic for non-emergency cases. | **Production** |
| **TriageDecision / SafetyRuleResult** | `ai/triage/schemas.py` | Data schemas for outputting structured triage decisions and rule audit trails. | **Production** |

## 2. Existing Safety Engine
- **Status:** **Production / Highest Authority**
- **Purpose:** Forces `EMERGENCY_AMBULANCE` and `URGENT_EVALUATION` escalation if specific red-flag signals (e.g., hypotension, FAST stroke criteria, severe chest pain with radiation) are detected in the `PatientState`.
- **Constraint:** AI triage must never override these deterministic outputs.

## 3. Existing Severity Classes
1. **EMERGENCY** (Escalation: `EMERGENCY_AMBULANCE`)
2. **URGENT** (Escalation: `URGENT_EVALUATION`)
3. **PRIORITY** (Escalation: `OPD_ROUTINE` or Priority Queue)
4. **ROUTINE** (Escalation: `OPD_ROUTINE`)

## 4. Existing Datasets
| Dataset | Location | Purpose | Status |
|---|---|---|---|
| **FedMML-ED-Triage** | `data/raw/fedmml_ed_triage/fedmml_ed_triage_dataset.csv` | Dataset of Chief Complaints, clinical notes, and 8 vitals channels mapped to triage scores. | **Experimental/Archived** |

## 5. Previous Failed Triage Model
| Component | File Location | Purpose | Current Status |
|---|---|---|---|
| **MultimodalTriageClassifier** | `models/triage_classifier/best_model.pt` | Neural model fusing MuRIL text embeddings + 8-dim Tabular Vitals MLP. | **Rejected** |

## 6. Previous Training Scripts
| Component | File Location | Purpose | Current Status |
|---|---|---|---|
| **train_multimodal_triage.py** | `ai/triage/train_multimodal_triage.py` | Fine-tunes the multimodal transformer + MLP head on FedMML data. | **Experimental** |

## 7. Previous Evaluation Results
- **Location:** `models/triage_classifier/run_manifest.json`
- **Results:** The model claimed **100% Accuracy (1.0) and 1.0 Emergency Recall** on validation.
- **Why it failed (Rejected):** The manifest shows the dataset was constrained to only **96 unique patients** (67 train, 14 val). The model completely memorized the tiny patient pool, leading to catastrophic overfitting. The "100% accuracy" is mathematically artificial and useless for real-world generalization.

## 8. Current Production Path
The current pipeline successfully avoids the failed neural model entirely. It operates via:
1. `TriageClassifier.classify(state)` is called.
2. The `PatientState` is fed into `SafetyRuleEngine`.
3. If an emergency red flag is found, it immediately returns `EMERGENCY`.
4. If no red flags are found, it falls back to `_score_urgency()`, which uses hardcoded heuristics (e.g., duration > 30 days = `ROUTINE`; SpO2 < 95% = `URGENT`) to assign severity.

---

## Recommendation for Next Steps

### Option Analysis

- **A) Retrain a proper triage model:** Training a robust, multimodal neural model requires an enormous, perfectly balanced, and highly diverse clinical dataset (which we lack, as seen by the 96-patient failure). Furthermore, we cannot use paid APIs or LLMs to synthetically augment this dataset right now.
- **B) Improve deterministic triage engine:** Creating thousands of hardcoded symptom rules (as forbidden by the user) is unscalable and brittle.
- **C) Combine both (Recommended):** The current deterministic `SafetyRuleEngine` is an excellent, un-overridable safety net. However, the fallback `_score_urgency()` is currently relying on very brittle hardcoded heuristics. We should **retain the existing Safety Engine** for absolute red flags, but **replace the fallback `_score_urgency` with a lightweight, robust Machine Learning classifier** (e.g., XGBoost, Random Forest, or a properly trained local LLM/Transformer if a large open-source clinical dataset is available locally). This gives us the scalability of ML for the "gray area" cases, while guaranteeing the Safety Engine catches the black-and-white emergencies.

**Final Recommendation:** **Option C (Combine both).** Keep the `SafetyRuleEngine` as the highest un-overrideable authority, but train a new, properly validated local AI model strictly to handle the non-emergency fallback routing.
