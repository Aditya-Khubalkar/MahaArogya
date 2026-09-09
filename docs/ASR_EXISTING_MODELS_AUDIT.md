# ASR Existing Models Audit

## 1. Overview
The previous hackathon team trained multiple versions of `whisper-small` for the Triage Voice Module. The latest version, `whisper_finetuned_v2_full`, was reported to have an overall Validation WER of 57.35%. However, an independent audit and benchmark have revealed critical flaws in the model's behavior, rendering it unusable for production triage.

## 2. Model Specifications
- **Base Architecture**: `openai/whisper-small` (~241M parameters)
- **VRAM Usage**: Peak ~6.2 GB during inference/training.
- **Languages Target**: English, Hindi, Marathi, Roman Marathi.

## 3. Independent Medical Benchmark Results
An independent pipeline evaluation was conducted using 15 realistic medical triage audio samples generated locally. The pipeline evaluated the end-to-end performance (`Audio` → `ASR` → `Language Detection` → `MedicalExtractor` → `PatientState` → `SafetyRuleEngine`).

### ASR Metrics
- **Total Samples**: 15
- **Overall WER**: 106.3%
- **Overall CER**: 89.9%
- **Emergency Extraction Recall**: 0/2 (0%)

### Language Breakdown
| Language | Samples | WER | CER |
|----------|---------|-----|-----|
| English  | 10      | 103.75% | 91.30% |
| Marathi  | 2       | 128.57% | 90.79% |
| Hindi    | 2       | 100.00% | 83.56% |
| Roman Mr | 1       | 100.00% | 87.18% |

## 4. Critical Failure Analysis (The "Devanagari Transliteration" Bug)
The >100% WER is not simply due to poor acoustic recognition. The model is suffering from severe **dataset misalignment** injected during the previous fine-tuning phase.

### Observation
The model forces all transcriptions into Devanagari script, regardless of the spoken language. Furthermore, it often translates regional languages into English, and then transcribes that English translation using Devanagari characters.

**Examples:**
1. **English Audio:** "I have severe abdominal pain for two days."
   - **Hypothesis:** "आयाव सविर अब्डमिटल पैन फूर टू डेश" (Literal transliteration of the English words).
2. **Marathi Audio:** "माझं पोट दोन दिवसांपासून खूप दुखत आहे."
   - **Hypothesis:** "माई स्टमिक इस हर्टिंग सविरली फूर थ्री डेश" (Translated to English: "My stomach is hurting severely for three days", then transliterated into Devanagari).

### Root Cause
The training dataset used by the previous team contained corrupted target labels. English text was algorithmically transliterated into Devanagari, and regional languages were likely passed through a broken translation pipeline before transliteration. The model learned to perform this bizarre English-to-Devanagari transliteration instead of actual Automatic Speech Recognition.

Because the `MedicalExtractor` expects standard language representations (English in Latin script, Marathi/Hindi in Devanagari), the ASR output completely bypasses all extraction rules, resulting in a **0% Emergency Recall**.

## 5. Final Decision & Next Steps
**Classification**: REQUIRES NEW TRAINING PIPELINE.

The existing `whisper_finetuned_v2_full` model is fundamentally broken due to poisoned training data. It cannot be salvaged through further fine-tuning. 

**Next Steps**:
1. Discard the existing `v2_full` model weights for production.
2. We must build a clean, verifiable dataset mapping Indian medical speech to proper Latin/Devanagari scripts.
3. Train a new ASR model from the `openai/whisper-small` baseline, ensuring strict data quality controls.
