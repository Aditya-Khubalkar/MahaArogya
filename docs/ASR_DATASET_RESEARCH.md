# ASR Dataset Research for MahaArogya Rebuild

This document outlines the verified dataset sizes and licenses for free and legally usable speech datasets suitable for training the new MahaArogya ASR module. The focus is strictly on **Marathi, Hindi, and English**.

## 1. Mozilla Common Voice (v17.0)
- **Official Source**: Mozilla Foundation (`mozilla-foundation/common_voice_17_0`)
- **License**: CC-0 (Public Domain)
- **Language(s)**: English, Hindi, Marathi
- **Speaker Metadata**: Age, gender, accent available.
- **Suitability**: Spontaneous and read speech with diverse backgrounds.
- **Commercial Use**: Permitted (No restrictions).
- **Redistribution**: Permitted.
- **Access Requirements**: Hugging Face gated access (Requires token).
- **Verified Downloadable Sizes (Validated Split)**:
  - English: ~3,400 hours
  - Hindi: ~21 hours
  - Marathi: ~13 hours

## 2. Kathbath (AI4Bharat)
- **Official Source**: AI4Bharat (`ai4bharat/kathbath`)
- **License**: CC-BY 4.0
- **Language(s)**: Hindi, Marathi, English
- **Speaker Metadata**: Provided in metadata files.
- **Suitability**: High-quality read speech recorded across Indian districts.
- **Commercial Use**: Permitted (with attribution).
- **Redistribution**: Permitted (with attribution).
- **Access Requirements**: Open access on Hugging Face.
- **Verified Downloadable Sizes**: 
  - Hindi: ~2,285 hours
  - Marathi: ~760 hours
  - English: ~530 hours

## 3. FLEURS (Google)
- **Official Source**: Google (`google/fleurs`)
- **License**: CC-BY 4.0
- **Language(s)**: English (en_us), Hindi (hi_in), Marathi (mr_in)
- **Speaker Metadata**: Split by train/val/test.
- **Suitability**: Good for robust evaluation and fine-tuning.
- **Commercial Use**: Permitted (with attribution).
- **Redistribution**: Permitted (with attribution).
- **Access Requirements**: Open access.
- **Verified Downloadable Sizes**: ~12 hours per language.

## 4. IndicVoices (AI4Bharat)
- **Official Source**: AI4Bharat
- **License**: CC-BY 4.0
- **Language(s)**: Hindi, Marathi, etc.
- **Speaker Metadata**: Available.
- **Suitability**: Spontaneous conversational speech.
- **Commercial Use**: Permitted.
- **Redistribution**: Permitted.
- **Access Requirements**: Hugging Face gated or via AI4Bharat portal.
- **Verified Downloadable Sizes**: ~50-100 hours per language.

---

## Dataset Rejection Criteria
We will **NOT** use:
- Proprietary internal datasets.
- Datasets with "Non-Commercial" (NC) clauses.
- Datasets where the transcript does not match the audio language (e.g., transliteration datasets).
- Synthetic audio (TTS) datasets for the primary training set.
