# MahaArogya — AI/ML Workspace Audit

**Audit Date**: 2026-08-17
**Hardware**: NVIDIA GeForce RTX 5060 Laptop GPU (8,151 MiB VRAM)
**Runtime**: PyTorch 2.11.0+cu128 · CUDA 12.8 · Python 3.12.0 · Transformers 5.15.0
**Repository**: C:\MahaArogya

---

## Environment Snapshot

```
GPU:           NVIDIA GeForce RTX 5060 Laptop GPU
VRAM:          8,151 MiB (6,474 MiB free at audit time)
PyTorch:       2.11.0+cu128
CUDA Runtime:  12.8 (KMD 610.88)
Transformers:  5.15.0
Python:        3.12.0
Regression:    212/212 tests pass (15.30s)
```

---

## MODEL 1 — Whisper ASR v1 (Decoder-Only Fine-Tune)

| Field | Value |
|---|---|
| Base Model | openai/whisper-small |
| Trainable Parameters | 153,580,800 of 241,734,912 |
| Dataset | AI4Bharat Kathbath (Hindi + Marathi) |
| Dataset Size | 12,684 training samples |
| Training Method | Decoder-only fine-tune (encoder frozen), AdamW |
| Steps | 1,200 |
| Batch Size | 16 |
| Peak VRAM | 7.26 GB |
| Training Time | 1,326 sec (~22 min) |
| Best Checkpoint | models/whisper_finetuned_v1_decoder_only/best_model.pt |
| Best Val WER (combined) | 61.63% |
| Hindi WER | 48.58% |
| Marathi WER | 74.67% |
| Hindi CER | 31.27% |
| Marathi CER | 46.20% |
| Known Failures | Marathi WER high. Encoder frozen limits acoustic adaptation. |
| Status | EXPERIMENTAL — Superseded by v2 |

---

## MODEL 2 — Whisper ASR v2 (Full Encoder+Decoder Fine-Tune)

| Field | Value |
|---|---|
| Base Model | openai/whisper-small |
| Init Checkpoint | whisper_finetuned_v1_decoder_only/best_model.pt (warm start) |
| Trainable Parameters | 241,734,912 (all) |
| Dataset | AI4Bharat Kathbath — same manifest as v1 |
| Dataset Size | 12,684 training samples |
| Training Method | Full enc+dec, differential LR (enc 1e-5 / dec 3e-5), gradient_checkpointing=True, grad_accum=4 |
| Effective Batch Size | 16 (physical 4 x accum 4) |
| Steps | 2,400 (no early stop) |
| Best Step | 1,920 |
| Peak VRAM | 6.20 GB |
| Training Time | 6,421 sec (~107 min) |
| Best Checkpoint | models/whisper_finetuned_v2_full/best_model.pt (step 1920) |
| Best Val WER (combined) | 57.35% |
| Hindi WER | 46.86% |
| Marathi WER | 67.85% |
| FLEURS Real-Speech Hindi WER | 53.57% |
| FLEURS Real-Speech Marathi WER | 109.38% (CATASTROPHIC — insertions > words) |
| FLEURS Overall WER | 81.47% |
| Known Failures | Marathi real speech completely fails. No medical vocab. No code-switching data. |
| Status | EXPERIMENTAL — Best tuned ASR but not production-safe for Marathi |

---

## MODEL 3 — faster-whisper (Production ASR)

| Field | Value |
|---|---|
| Model | faster-whisper small (CTranslate2 INT8) |
| Base Model | openai/whisper-small (untuned) |
| Training Method | None (zero-shot) |
| FLEURS Hindi WER | 53.57% (avg latency 0.89s) |
| FLEURS Marathi WER | 109.38% (avg latency 1.62s) |
| Known Failures | Identical to v2: Marathi degraded, no medical domain, no code-switching |
| Status | PRODUCTION — Used in ai/asr/service.py. Chosen for latency. |

---

## MODEL 4 — Neural Symptom Extraction (REJECTED)

| Field | Value |
|---|---|
| Model | MultilingualSymptomExtractor |
| Base Model | google/muril-base-cased + MeanPool + LinearHead |
| Parameters | ~236M |
| Labels | 16 symptom classes |
| Dataset | 767 synthetic examples (536 train / 115 val / 116 test) |
| Training Method | Multi-label classification, AdamW, 3 epochs |
| Batch Size | 16 |
| Best Val F1 | 0.0% (run_manifest) |
| Benchmark F1 | 18.18% (TP=40, FP=360 — predicts ALL 16 symptoms for every input) |
| Known Failures | SEVERE OVER-ACTIVATION. No negation. 767 examples far too few for 16-class multi-label. |
| Status | REJECTED — Clinical safety failure. Rule engine remains authority. |

---

## MODEL 5 — Rule-Based Symptom Extraction (PRODUCTION)

| Field | Value |
|---|---|
| Model | MedicalExtractor (regex + rules) |
| Implementation | ai/nlp/extractor.py |
| Languages | Marathi (Devanagari), Hindi, English, Roman Marathi, Hinglish |
| Symptoms Covered | 16 |
| Benchmark F1 | 100.00% (TP=40, FP=0, FN=0 on 25-case benchmark) |
| Negation | Clause-scoped (nahi, nahit, no, not, absent, denies + Devanagari) |
| Known Failures | Limited to 16 coded symptoms. Cannot generalise. Hinglish is heuristic. |
| Status | PRODUCTION — Sole clinical authority for extraction. |

---

## MODEL 6 — Neural Triage Classifier (REJECTED — SAFETY FAILURE)

| Field | Value |
|---|---|
| Model | MultimodalTriageClassifier |
| Base Model | google/muril-base-cased + tabular fusion head |
| Parameters | 237,668,612 |
| Tabular Features | systolic_bp, diastolic_bp, heart_rate, resp_rate, temperature, spo2, pain_score, age |
| Dataset | FedMML-ED-Triage (87,234 rows — 6-hospital synthetic ED) |
| Unique Patients | 96 templates x ~908 synthetic jitter rows |
| Split | Patient-grouped 67/14/15 patients |
| Epochs | 4 (best epoch 2) |
| Batch Size | 64 |
| Peak VRAM | 5.27 GB |
| Training Time | 1,627 sec (~27 min) |
| Best Checkpoint | models/triage_classifier/best_model.pt (epoch 2) |
| In-Distribution Val Accuracy | 100.0% |
| In-Distribution Emergency Recall | 100.0% |
| OOD Test Accuracy | 10.0% (2/20 on triage_test_set.json) |
| OOD Emergency Recall | 11.1% (2/18 clinical edge cases) |
| Root Cause | 87K rows = 96 templates x jitter. Model memorised templates. Fails OOD. |
| Known Failures | STEMI triaged as ROUTINE. 16/18 critical red-flags under-triaged. |
| Status | REJECTED — CLINICAL SAFETY FAILURE |

---

## MODEL 7 — Deterministic Safety/Triage Engine (PRODUCTION)

| Field | Value |
|---|---|
| Implementation | ai/triage/safety_rules.py + ai/triage/classifier.py |
| Clinical Rules | 18+ named rules (CARDIAC_01, RESP_01, HEMORRHAGE_01, STROKE_FAST, PREGNANCY_ABDO, SILENT_MI, NEONATAL_FEVER, PEDIATRIC_HIGH_FEVER, SHOCK_BP, TACHYCARDIAC_HR, HYPOXIA_SPO2, MENINGITIS_TRIAD, THUNDERCLAP, ANAPHYLAXIS, DKA, TESTICULAR_TORSION, COMPARTMENT_SYNDROME, SUICIDAL_IDEATION + standalone flags) |
| Emergency Recall | 18/18 (100%) on clinical edge case set |
| Under-Triage | 0 |
| Known Failures | Cannot escalate presentations outside coded rule set. |
| Status | PRODUCTION — Sole clinical triage authority. ML CANNOT override. |

---

## MODEL 8 — Question Selector (PRODUCTION STOPGAP — REPLACEMENT TARGET)

| Field | Value |
|---|---|
| Implementation | ai/questions/selector.py + ai/questions/question_bank.py |
| Mechanism | Priority-sort over 8 hardcoded questions in 5 languages |
| Symptoms Covered | chest_pain, breathlessness, abdominal_pain, fever, vomiting (5 of 16) |
| Languages | mr, hi, en, roman-mr, hinglish (template lookup only) |
| Known Failures | HARDCODED — no context adaptation, no language generation, 5/16 symptoms, no mixed-language generation |
| Status | PRODUCTION (stopgap) — PRIMARY REPLACEMENT TARGET |

---

## MODEL 9 — PatientState Manager (PRODUCTION)

| Field | Value |
|---|---|
| Implementation | ai/patient_state/state_manager.py + schemas.py |
| Key Fields | conversation_id, age_years, gender, language, symptoms Dict, negated_symptoms, vitals, answers, risk_signals, triage_category |
| Language Values | mr, hi, en, roman-mr, hinglish |
| Status | PRODUCTION |

---

## MODEL 10 — Hospital Routing + OPD Token (PRODUCTION)

| Field | Value |
|---|---|
| Implementation | ai/routing/ |
| Coverage | MMR hospital grid (KEM, Sion, JJ, Sassoon, GMCH etc.) |
| E2E Verification | 7/7 stages verified, 0 inconsistencies |
| Status | PRODUCTION |

---

## Dataset Registry

| Dataset | License | Language | Size | Status | Purpose |
|---|---|---|---|---|---|
| AI4Bharat Kathbath | CC0 | hi, mr | 12,684 clips used | IN USE | ASR fine-tuning |
| Google FLEURS (hi_in, mr_in) | CC-BY-4.0 | hi, mr | 50 clips | IN USE | ASR benchmark |
| MediTOD | CC0 (research) | en | 833KB dialogs.json | DOWNLOADED | Question model candidate |
| FedMML-ED-Triage | CC-BY-4.0 | en | 87,234 rows | USED/REJECTED | Neural triage (OOD failure) |
| BC5CDR | Public Domain | en | 1,500 PubMed articles | DOWNLOADED | NER reference |
| NCBI Disease | Public Domain | en | 793 abstracts | DOWNLOADED | NER reference |
| Symptom-to-Diagnosis | Apache-2.0 | en | 1,065 examples | DOWNLOADED | Symptom classification |
| MedQuAD | CC-BY-4.0 | en | NIH QA pairs | DOWNLOADED | Medical QA reference |
| Synthetic (in-project) | Internal | mr,hi,en,roman-mr,hinglish | 767 examples | IN USE | Extraction benchmark |

---

## CRITICAL NEGATIVE FINDINGS — DO NOT HIDE

### 1. Neural Triage — Clinical Safety Failure
- OOD Emergency Recall: 11.1% (2/18)
- 16/18 critical red-flags under-triaged (STEMI -> ROUTINE)
- Root cause: 87K FedMML rows = 96 templates x jitter. Zero real diversity.
- STATUS: REJECTED. Deterministic rule engine is sole triage authority.

### 2. Neural Symptom Extraction — Over-Activation
- Benchmark F1: 18.18% (FP=360, TP=40 — all 16 symptoms predicted for every input)
- Root cause: 767 synthetic examples, no real data, no negation model
- STATUS: REJECTED. Rule extractor is sole extraction authority.

### 3. ASR — Marathi Real-Speech Catastrophic Failure
- Marathi WER on FLEURS real human speech: 109.38%
- WER >100% means hallucinated insertions exceed actual spoken words
- Neither v1 nor v2 fine-tune resolves this adequately
- No medical domain vocabulary in training data
- No code-switching (Hinglish / Marathi-English) coverage
- STATUS: Production ASR usable for Hindi (~53%) but NOT production-safe for Marathi.

### 4. Question Selector — Not Trained Intelligence
- Current system is hardcoded priority-sort over 8 fixed template questions
- No context adaptation, no language generation, covers 5 of 16 symptom codes
- STATUS: Stopgap. Trained adaptive question model is PRIMARY new development objective.

---

## Target Architecture (Full Trained System)

```
USER INPUT (voice/text)
        |
[ASR] faster-whisper / IndicWhisper (PRODUCTION / Under improvement)
        |
[Language Detector] Script + vocab fingerprint -> language state lock
        |
[NLP] MedicalExtractor rule engine (PRODUCTION)
        |
[PatientState] Accumulated structured memory (PRODUCTION)
        |
[TRAINED QUESTION MODEL] Context-aware next-question selection
  Inputs: PatientState + ConversationHistory + LanguageState
  Output: Best next question (in patient's language/style)
        |
USER ANSWER -> PatientState Update -> Question Model again
        |
[SafetyRuleEngine] Deterministic red-flag override (PRODUCTION — immovable)
        |
[TriageClassifier] Deterministic urgency scoring (PRODUCTION)
        |
[HospitalRouter] Distance + capacity ranker (PRODUCTION)
        |
OPD Token issued
```

---

## Next Development Priorities

### PRIORITY 1 — Trained Adaptive Question Model
Goal: Replace hardcoded QuestionSelector with model trained on real doctor-patient dialogs
Primary dataset: MediTOD (data/raw/meditod/data/dialogs.json — already downloaded)
Secondary: Research MTS-Dialog, ChatDoctor, medical dialogue HF datasets
Architecture options:
  A. Ranking: PatientState + ConversationHistory + candidate questions -> score/rank
  B. Generation: PatientState + ConversationHistory -> seq2seq next question (T5/mT5-small)
Language: Must generate in patient's detected language (mr/hi/en/hinglish/mixed)
VRAM budget: <=7GB peak on RTX 5060 8GB

### PRIORITY 2 — Language Detection and Style Tracking
Goal: Auto-populate PatientState.language from input text
Approach: fastText lid classifier + script detection + medical vocab fingerprint
Languages: en, hi, mr, roman-mr, hinglish (code-switched)

### PRIORITY 3 — ASR Improvement (Marathi)
Goal: Reduce Marathi WER from 109% to <40% on real human speech
Near-term option: Test IndicWhisper (AI4Bharat, MIT license) as drop-in replacement
Blocker for further fine-tuning: HF token required for Kathbath/IndicVoices

### PRIORITY 4 — Extraction Expansion
Goal: Expand beyond 16 symptoms, improve Hinglish patterns
Approach: Extend rules + consider NER model when real labeled data available

---

## Preserved Artifacts — Do Not Delete

- models/whisper_finetuned_v1_decoder_only/best_model.pt  (967MB)
- models/whisper_finetuned_v2_full/best_model.pt          (967MB)
- models/whisper_finetuned_v2_full/checkpoint_step_*.pt   (9 checkpoints)
- models/triage_classifier/best_model.pt                  (negative finding reference)
- models/extraction_classifier/best_model.pt              (negative finding reference)
- evaluation/eval_report.md
- evaluation/eval_results.json
- data/source_registry.csv
- data/raw/meditod/
- data/raw/fedmml_ed_triage/
- ai/triage/safety_rules.py                               (DO NOT MODIFY without clinical review)
- ai/nlp/extractor.py
- ai/questions/question_bank.py

---

Audit generated 2026-08-17. All metrics from run_manifest.json and evaluation/eval_report.md.
No results have been fabricated or hidden.
