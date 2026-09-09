# ASR Rebuild Plan: Phase 1

## 1. Justification for Rebuild
The previous `whisper_finetuned_v2_full` model was thoroughly audited and rejected. The model achieved a >100% Word Error Rate (WER) and a 0% Emergency Extraction Recall. The primary root cause was a catastrophic dataset misalignment (the "Devanagari Transliteration Bug") where English and regional languages were forcefully transliterated or incorrectly translated into Devanagari script. This breaks downstream NLP extraction (`MedicalExtractor`), rendering the ASR unusable for production triage.

## 2. Dataset Sources, Licensing, and Sizes
The training corpus will be built using the following open-license, commercially usable datasets to ensure true acoustic diversity across Marathi, Hindi, and English:

| Dataset Name | Official Source | License | Languages | Est. Hours |
|--------------|----------------|---------|-----------|------------|
| **Common Voice (v17)** | Mozilla | CC-0 (Public Domain) | English, Hindi, Marathi | Eng: 3000+, Hi: 30+, Mr: 25+ |
| **Kathbath** | AI4Bharat | CC-BY 4.0 | Hindi, Marathi | Hi: ~2000, Mr: ~700 |
| **FLEURS** | Google | CC-BY 4.0 | English, Hindi, Marathi | ~12 per language |
| **IndicVoices** | AI4Bharat | CC-BY 4.0 | Hindi, Marathi | ~50-100 per language |

**Speaker Counts**: Cumulatively, these datasets provide tens of thousands of unique speakers, ensuring extreme acoustic diversity and generalization across regional accents.

## 3. Data Preprocessing & Cleaning Policy
- **No Synthetic Data**: Absolutely no TTS or synthetic audio will be used in the primary training corpus to prevent artifact memorization.
- **Silence Trimming**: Extraneous lead-in and lead-out silence will be trimmed using VAD (Voice Activity Detection).
- **Audio Standardization**: All audio will be resampled to 16,000 Hz, mono-channel, 16-bit PCM (Whisper standard).

## 4. Transcript Policy
A strict 1:1 language-to-script policy is enforced (see `ASR_TRANSCRIPTION_POLICY.md` for full details):
- English audio maps strictly to Latin script.
- Hindi and Marathi audio maps strictly to Devanagari script.
- No transliteration. No forced translations.
- Numbers and clinical entities (e.g., SpO2, heart rate) must be preserved flawlessly in digit format to accommodate the Regex extractors.

## 5. Train/Validation/Test Split Strategy
**CRITICAL**: Splitting will be strictly **SPEAKER-BASED**, not file-based.
- No speaker in the TRAIN set will appear in the VALIDATION or TEST sets.
- This prevents the model from memorizing speaker-specific acoustic profiles and ensures true zero-shot evaluation on unseen voices.
- Split ratios: 80% Train, 10% Validation, 10% Test (by speaker count).
- Data splits are managed under `C:\MahaArogya\data\splits\asr\`.

## 6. Model Architecture & RTX 5060 Training Config
- **Base Model**: `openai/whisper-small` (fresh initialization).
- **Hardware**: Local NVIDIA RTX 5060 (8GB VRAM).
- **Configuration**:
  - **Precision**: Mixed Precision (FP16) to fit within 8GB VRAM and accelerate training.
  - **Gradient Accumulation**: Steps set to 8 or 16 to simulate a larger batch size (effective batch size ~32 or 64).
  - **Gradient Checkpointing**: Enabled to reduce VRAM footprint during backpropagation.
  - **Optimizer**: AdamW with linear warmup and cosine decay.
  - **Checkpointing**: Save every 500 steps, evaluate on validation set, and retain the best checkpoint (`load_best_model_at_end=True`).
  - **Seed**: 42 (Reproducible).

## 7. Evaluation Methodology & Medical Metrics
Standard generic metrics (WER/CER) are insufficient for safe medical triage. Evaluation will be conducted on dedicated unseen benchmarks located in `C:\MahaArogya\data\test\asr\`:

1. **Standard ASR Metrics**:
   - Word Error Rate (WER)
   - Character Error Rate (CER)
2. **Medical ASR Metrics (Vital/Number Accuracy)**:
   - Evaluated on `numbers_vitals_test/`. Ensures "oxygen is 88" does not degrade to "oxygen is 80".
3. **Emergency Extraction Metrics**:
   - Evaluated end-to-end through the `MedicalExtractor` and `SafetyRuleEngine`.
   - **Emergency Phrase Recall**: Percentage of emergency audio clips correctly routed to `EMERGENCY` triage level despite minor transcription artifacts.

**Success Condition**: Training is successful if and only if Emergency Phrase Recall is 100% on the medical/emergency test sets, and numbers/vitals are perfectly preserved.
