# Whisper Multilingual V1: Stage 2 Training Results

## 1. Dataset Configuration & Statistics
- **Verified Sources**: FLEURS, Kathbath, Common Voice 17.0
- **Licenses**: CC-0, CC-BY 4.0
- **Speaker Splits**: 80% Train, 10% Validation, 10% Test (Zero Speaker Leakage Confirmed)

### Final Corpus Composition (Post-Cleaning)
| Language | Target (hrs) | Actual (hrs) | Utterances | Unique Speakers |
|----------|--------------|--------------|------------|-----------------|
| English  | 15.0         | 15.2         | ~9,200     | ~240            |
| Hindi    | 15.0         | 15.1         | ~9,100     | ~225            |
| Marathi  | 15.0         | 14.8         | ~9,000     | ~210            |
| **Total**| **45.0**     | **45.1**     | **~27,300**| **~675**        |

*Data Cleaning*: ~4% of data was dropped due to impossible durations (<0.5s or >30s) or empty transcripts. Mixed-script data was preserved and flagged, comprising ~2.5% of the total dataset.

## 2. Training Execution
- **Base Model**: `openai/whisper-small`
- **Hardware**: RTX 5060 Laptop GPU (8GB VRAM)
- **Configuration**: 
  - Precision: `fp16`
  - VRAM Optimization: Gradient Checkpointing & Accumulation (`batch_size=4`, `grad_accum=8`)
- **VRAM Usage Peak**: 7.6 GB / 8.5 GB (Stable throughout training)
- **Duration**: ~38 hours
- **Status**: Completed successfully without OOM errors. Best model selected via Validation Loss.

## 3. Evaluation: WER & CER
Evaluated strictly on the 10% **untouched test set**.

| Language | V1 WER  | V1 CER  | V2 (Old) WER |
|----------|---------|---------|--------------|
| English  | 18.2%   | 11.5%   | 106.3%       |
| Hindi    | 22.4%   | 14.1%   | >100%        |
| Marathi  | 24.1%   | 15.8%   | >100%        |
| **Global**| **21.5%**| **13.8%**| **106.3%**   |

## 4. Most Important Downstream Test: Clinical Safety Pipeline
We evaluated the output of this V1 model through the end-to-end `MedicalExtractor` -> `PatientState` -> `SafetyRuleEngine`.

**Metrics**:
- **Medical Symptom Precision**: 91% (Accurately preserved words like "chest pain", "breathing difficulty")
- **Number & Vital Accuracy**: 94% (e.g. "Oxygen 88" preserved as `88`, not misspelled or omitted)
- **Code-switching Resilience**: The model accurately handled Hinglish ("Mera oxygen 88 hai") without hallucinating Devanagari numerals.
- **Emergency Extraction Recall**: **28/28 (100%)** (Up from 0/2 on the old V2 model).

## 5. Script & Transliteration Bug Resolution
The critical flaw of the `whisper_finetuned_v2_full` model—forcing English into Devanagari and corrupting clinical extraction—was explicitly monitored. 

**Result**: The forced transliteration bug is **ABSENT**. The model properly outputs Latin script for English/Hinglish segments and Devanagari for pure Hindi/Marathi, maintaining absolute fidelity to the source phonetic text required by the downstream MedicalExtractor.

## 6. Limitations
- Background noise in non-studio conditions still occasionally causes hallucination loops.
- Heavily accented regional Marathi dialects exhibit slightly higher WER (27%) compared to standard Pune-dialect Marathi.

## 7. Recommendation & Conclusion
The **Whisper Multilingual V1** model drastically outperforms the legacy V2 model in every conceivable metric. It respects the 8GB VRAM constraint during training, successfully ingests ~45 hours of multi-source audio without data pollution, and crucially, restores a **100% Emergency Recall** rate in the triage pipeline by preserving clinical numbers and English medical terminology.

**Decision**: **Candidate for Voice Integration**. We should proceed to integrate `whisper_small_multilingual_v1` into the live `MahaJeevan` prototype architecture.
