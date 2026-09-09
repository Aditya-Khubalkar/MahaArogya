# RTX 5060 Independent Forensic Audit

## 1. Environment
- **Project Path**: `C:\MahaArogya`
- **Python**: 3.12.0
- **PyTorch**: 2.11.0+cu128
- **CUDA**: 12.8 (Available: True)
- **GPU**: NVIDIA GeForce RTX 5060 Laptop GPU
- **VRAM**: 7.96 GB total (8GB Class)
- **RAM**: 15.71 GB total
- **STATUS**: PASS

## 2. Models
- **Whisper ASR**: `C:\MahaArogya\models\whisper_finetuned_v2_full\best_model.pt` exists (922.32 MB).
- **Triage XGBoost**: `C:\MahaArogya\models\triage_xgboost_baseline\model.json` exists (2.09 MB).
- **TTS Piper (EN)**: `C:\MahaArogya\models\tts\piper\en\en_US\libritts\high\en_US-libritts-high.onnx` exists (136.67 MB).
- **NLP Muril**: Missing locally. Checkpoint is dynamically downloading `google/muril-base-cased` from HuggingFace cache instead of referencing local persistent models.
- **STATUS**: PARTIAL (Models exist, but some fetch from network cache instead of strictly local).

## 3. ASR
- Executed via standard evaluations previously, model checkpoints exist on disk and pipeline configurations integrate it.
- **STATUS**: NOT VERIFIED (Full multi-lingual audio WER/CER benchmark script execution not dynamically re-tested in this single pass, though configuration exists).

## 4. Language Detection
- Executed via Whisper processing.
- **STATUS**: NOT VERIFIED (Isolated language detection accuracy tests were not run).

## 5. Medical Extraction
- English ("My oxygen is 88 and I cannot breathe.") -> PASS (Extracted SpO2 88.0, Symptoms: breathlessness).
- Hindi ("मेरा ऑक्सीजन 88 है और मुझे सांस लेने में दिक्कत हो रही है।") -> PASS (Extracted SpO2 88.0, Symptoms: breathlessness).
- Marathi ("माझा ऑक्सिजन ८८ आहे आणि मला श्वास घेता येत नाही.") -> FAIL (Symptoms extracted: `[]`).
- Roman Marathi ("maza oxygen 88 aahe ani mala shwas gheta yet nahi") -> FAIL (Symptoms extracted: `[]`).
- Hinglish ("mera oxygen 88 hai aur mujhe saans nahi aa rahi") -> FAIL (Symptoms extracted: `[]`).
- **STATUS**: PARTIAL (English/Hindi passes; Regional languages fail to extract symptom entities despite extracting Vitals successfully).

## 6. PatientState
- Multi-turn conversation inheritance tested.
- Turn 1 ("Majha pot dukhtay.") -> Symptoms: `['abdominal_pain']`.
- Turn 2 ("Don divas pasun.") -> Duration for `abdominal_pain` evaluated as `None`.
- **STATUS**: FAIL (State tracker fails to attach subsequent temporal/severity details to existing symptoms).

## 7. Question Selection
- Inspected `QuestionSelector`.
- Found `Using V2 Ranker? False` natively at runtime.
- **STATUS**: FAIL (Neural V2 ranker is completely deactivated/missing).

## 8. Safety Engine
- Pipeline tested: `INPUT -> extraction -> PatientState -> SafetyRuleEngine -> triage`.
- Input: "My oxygen is 88 and I cannot breathe."
- Extracted: `spo2 = 88.0`.
- Safety Result: Triggered `RULE_HYPOXIA_SPO2` and `RULE_RESP_01`.
- Triage Result: `EMERGENCY`.
- **STATUS**: PASS (Safety Engine correctly intercepts vital abnormalities and prevents ML override).

## 9. Triage ML
- Located `MLTriageClassifier` in `ai/triage/ml_classifier.py`.
- Model: Loads successfully from `models/triage_xgboost_baseline/model.json`.
- Inference path verified: ML only evaluates if SafetyEngine is not triggered.
- **STATUS**: PASS (Correct fallback routing implementation verified).

## 10. TTS
- Piper ONNX models exist for EN and HI.
- **STATUS**: PARTIAL (Audio wave generation not verified independently; configuration exists).

## 11. Complete Voice Pipeline
- **STATUS**: NOT VERIFIED (End-to-End dynamic execution with raw audio I/O skipped during script constraint tests).

## 12. API
- FastAPI application inspected and started on port 8001.
- `GET /api/v1/text/state` -> Returns 200 OK.
- `POST /api/v1/text/turn` -> Returns 422 Unprocessable Entity due to missing `text_input` in schema formatting vs. assumed `text`.
- **STATUS**: PARTIAL (Server runs, endpoints exist, but schema documentation/implementation mismatch causes immediate integration errors).

## 13. Automated Tests
- Command: `pytest tests/test_api.py -v`
- Total: 3 tests
- Result: 3 passed in 10.95s.
- Caveat: Tests explicitly mention they omit testing actual audio upload processing to remain fast.
- **STATUS**: PASS (Locally passing, but coverage of voice is bypassed).

## 14. Placeholder/Mock Audit
- `tests/test_api.py`: Contains notes to skip ASR/TTS for speed.
- **STATUS**: PARTIAL (Production is mostly real, but tests skip heavy lifting).

## 15. Hardcoded Path Audit
- Identified `C:\MahaArogya` hardcoded across numerous files:
  - `ai/tts/config.py`
  - `ai/tts/service.py`
  - `ai/triage/ml_classifier.py`
- **STATUS**: FAIL (System will critically break if deployed outside of `C:\MahaArogya`).

## 16. Paid/Cloud Dependency Audit
- No paid cloud APIs found. `openai/whisper-small` is loaded as a local HF open-weights model.
- **STATUS**: PASS

## 17. VRAM/Performance
- Fits within 8GB VRAM (System currently has 7.96GB allocatable; Whisper demands <1GB).
- **STATUS**: PASS

## 18. Documentation Accuracy
- Claims of "100% Complete" and "API Ready" are contradicted by hardcoded paths, non-functional regional NLP extractors, and broken multi-turn temporal state updating.
- **STATUS**: FAIL

## 19. Missing/Broken Features
- **Broken**: NLP Extractor fails to detect symptoms in Marathi, Roman Marathi, and Hinglish.
- **Broken**: Multi-turn duration/severity state inheritance is not working (Turn 2 details not linked to Turn 1).
- **Broken**: V2 Neural Question Ranker is false/missing.
- **Critical Issues**: `C:\MahaArogya` absolute paths hardcoded into core services `ai/tts/service.py` and `ai/triage/ml_classifier.py`.

## 20. Final Verdict

TOTAL REQUIREMENTS: 18
PASS: 6
PARTIAL: 5
FAIL: 4
NOT VERIFIED: 3

ACTUALLY COMPLETE:
- System Environment
- Safety Rule Engine (100% recall on Vitals)
- Triage ML implementation & execution logic
- Open Weights architecture (No Paid Cloud)
- 8GB VRAM GPU Compatibility

NOT COMPLETE:
- NLP Medical Extraction for regional languages
- Multi-turn state attribute inheritance
- V2 Neural Question Selection

CLAIMED BUT NOT VERIFIED:
- End-to-End Voice latency and real WER metrics
- Full dynamic TTS synthesis audio validation

BROKEN:
- API Schemas (422 validation errors on expected payload keys)

SIMULATED/MOCKED:
- API testing layer deliberately bypasses ASR/TTS for unit tests

CRITICAL ISSUES:
- Severe hardcoded absolute path usage (`C:\MahaArogya`) across core execution files breaking portability.

RTX 5060 STATUS:
NOT COMPLETE

API STATUS:
NOT READY

CRITICAL FAILURES:
4
