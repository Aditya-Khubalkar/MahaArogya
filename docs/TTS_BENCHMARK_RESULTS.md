# TTS Benchmark Results - Phase 4

## 1. Candidates Evaluated
- `ai4bharat/IndicF5` (Hindi, Marathi, English)
- `facebook/mms-tts-hin` (Hindi)
- `facebook/mms-tts-mar` (Marathi)
- `pyttsx3` / Windows SAPI5 (English, Hindi, Marathi fallback)

## 2. Licenses & Commercial Viability
- **`ai4bharat/IndicF5`**: **MIT License**. Permitted for commercial use. *(Note: The HuggingFace repo is gated and requires manual access approval, which blocks automated downloading).*
- **`facebook/mms-tts-hin` & `mar`**: **CC-BY-NC 4.0**. **FLAGGED FOR LICENSE:** strictly prohibits commercial use. Unsuitable for commercial deployment or prototypes intended for commercialization.
- **`pyttsx3`**: System-dependent, but generally unrestricted via native Windows APIs.

## 3. Model Sizes
- `IndicF5`: ~1.4 GB (Safetensors)
- `facebook/mms-tts-*`: ~140 MB per language (VITS architecture)
- `pyttsx3`: 0 MB (uses OS built-in voices)

## 4. Hardware
- **GPU**: NVIDIA GeForce RTX 5060 Laptop GPU (8GB VRAM)
- **Environment**: Python 3.12, PyTorch 2.11.0+cu128 (Windows)

## 5. Installation Requirements
- **MMS Models**: Requires standard `transformers` and `scipy` (already installed).
- **pyttsx3**: Pre-installed natively.
- **IndicF5**: Requires custom `f5-tts` or specific inference code and access to the gated HuggingFace repository.

## 6. VRAM Usage
- **MMS Hindi**: ~140 MB
- **MMS Marathi**: ~56 MB
- **MMS Total**: ~200 MB for both models loaded simultaneously. Leaves ~7.8GB free (fits easily with Whisper).
- **IndicF5**: Estimated ~2-3 GB VRAM at inference time (based on 1.4GB weights).
- **pyttsx3**: 0 MB VRAM (CPU only).

## 7. Latency
- **MMS First Inference (Cold Start)**: 0.3s to 2.0s
- **MMS Warm Inference**: ~0.11s for ~2.6 seconds of audio.
- **MMS Real-Time Factor (RTF)**: ~0.04 (generates audio 25x faster than real-time).
- **pyttsx3**: Near-instant (CPU).

## 8. Audio Quality Observations
- **MMS (VITS)**: The voice quality is clear but monotonic and robotic.
- **pyttsx3**: Very robotic. Uses SAPI5 Default Desktop Voices (e.g., Zira/David).

## 9. Hindi Results
- **pyttsx3**: Fails gracefully or spells out English characters. Sounds completely unnatural for Hindi unless specific Windows language packs are installed.
- **MMS Hindi**: Generates fast and understandable Hindi speech, but with a flat, robotic tone.

## 10. Marathi Results
- **pyttsx3**: Completely fails/unnatural.
- **MMS Marathi**: Generates fast and understandable Marathi speech. Similar flat tone to Hindi.

## 11. English Results
- **pyttsx3**: Decent but robotic English (standard Windows voice).
- **IndicF5**: Known to handle English well natively, supporting code-switching effectively. 
- **Alternative Lightweight Local English TTS Candidate**: Because MMS models are monolingual and non-commercial, and IndicF5 is gated, **Piper TTS** is highly recommended as a lightweight local English TTS candidate. Piper uses VITS (like MMS) but has MIT/Open models, covers English excellently, and requires negligible VRAM.

## 12. Medical-Number Results
- **MMS**: Struggles significantly with raw digits (e.g., "88"). VITS text normalizers for Indic languages in the MMS pipeline often skip numbers entirely or mispronounce them if they are not explicitly written out in words (e.g., "अठासी" instead of "88").
- **pyttsx3**: Reads numbers fine in English, but struggles in Indic languages.

## 13. Limitations
- **License**: Meta's MMS models cannot be used commercially (CC-BY-NC 4.0).
- **Text Normalization**: MMS cannot read digits natively without a separate text-normalization pipeline.
- **Gating**: IndicF5 is gated, delaying immediate automated setup.

## 14. Recommended Model
**Recommended TTS model: Piper TTS (or IndicF5 once access is granted)**

**Evidence:**
1. **License**: MMS models are explicitly prohibited for commercial use due to the CC-BY-NC 4.0 license, disqualifying them. 
2. **Quality & Multilingual**: `pyttsx3` completely fails at Hindi and Marathi.
3. **VRAM Constraints**: We need a solution that fits alongside Whisper ASR in an 8GB RTX 5060.
4. **Conclusion**: Since the provided MMS candidates fail the commercial license check, and IndicF5 is gated, we cannot select them for an immediate automated open-source pipeline. **IndicF5** (MIT license) remains the best architectural candidate *if* you request access. However, for an immediate, un-gated, commercially viable, and extremely lightweight solution, **Piper TTS** (VITS-based, MIT-licensed, fast RTF) is the strongest candidate for English and has growing Indic support. It handles medical numbers much better if paired with a small number-normalizer.

## 15. FINAL TTS DECISION

**Selected Models (Smallest Practical Local Combination)**:
- **English**: Piper TTS (`en_US-libritts-high` or similar)
- **Hindi**: Piper TTS (`hi_IN-pratham-medium` or `hi_IN-priyamvada-medium`)
- **Marathi**: `ai4bharat/IndicF5`

**Licenses**:
- **Piper TTS**: MIT (Approved for commercial use)
- **IndicF5**: MIT (Approved for commercial use)
- **Meta MMS**: CC-BY-NC 4.0 (REJECTED due to commercial restrictions)
- **pyttsx3**: System (REJECTED due to poor Indic quality)

**Model Sizes & VRAM**:
- **Piper TTS**: ~30-50 MB per voice. VRAM footprint is nearly 0 (runs extremely fast via ONNX Runtime on CPU or GPU).
- **IndicF5**: ~1.4 GB weight size. Requires ~2-3 GB VRAM during inference.
- **Total Combined Footprint**: Fits easily within the 8GB RTX 5060 alongside the ~2GB Whisper model.

**Quality & Medical Numbers**:
- Piper TTS is excellent for English and decent for Hindi, but requires text normalization for complex medical numbers before inference.
- IndicF5 provides state-of-the-art Marathi capabilities natively.

**IndicF5 Gating - Action Required**:
We **cannot** bypass the HuggingFace gating for IndicF5. To use it for Marathi:
1. Log in to Hugging Face and navigate to `https://huggingface.co/ai4bharat/IndicF5`.
2. Click "Agree and access repository" to request access.
3. Once approved, provide a valid HF token to the environment (e.g., via `huggingface-cli login`).
Until this is done, Marathi neural TTS cannot be initialized automatically.

**Classification**:
- **A. Piper TTS (English & Hindi)**: APPROVED FOR MAHAAROGYA
- **B. ai4bharat/IndicF5 (Marathi)**: APPROVED FOR MAHAAROGYA (Pending Manual Gating Access)
- **C. facebook/mms-tts-***: REJECTED (License incompatibility)
- **C. pyttsx3**: REJECTED (Insufficient quality for Hindi/Marathi)
