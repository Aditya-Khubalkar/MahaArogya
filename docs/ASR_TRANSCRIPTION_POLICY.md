# ASR Transcription Policy

To prevent the catastrophic alignment failures observed in earlier models (where the model learned to transliterate English into Devanagari or improperly translate audio), MahaArogya mandates a strict, one-to-one script fidelity policy for all ASR training data.

## Core Directives

1. **Strict Language-to-Script Mapping**:
   - **English Audio**: MUST be transcribed in **English (Latin)** script.
   - **Hindi Audio**: MUST be transcribed in **Hindi (Devanagari)** script.
   - **Marathi Audio**: MUST be transcribed in **Marathi (Devanagari)** script.
   - **Roman Marathi**: ONLY permissible if the ground-truth transcript is genuinely annotated in Roman Marathi. Otherwise, Marathi speech must map to Devanagari.

2. **No Transliteration**:
   - Do NOT transliterate English words into Devanagari (e.g., "blood pressure" must NOT become "ब्लड प्रेशर" unless the speaker is speaking a mixed Hindi/Marathi sentence where the loan word is naturally used, and the dataset convention supports it. For pure English sentences, strictly Latin).

3. **No Translation**:
   - The transcript MUST represent exactly what the speaker said. 
   - Do NOT translate Hindi to English or Marathi to Hindi.

4. **Hinglish / Mixed Code-Switching**:
   - Preserve the actual mixed-language transcription exactly as the dataset provides it. If a speaker switches mid-sentence, the transcript must reflect that code-switching faithfully in the dataset's native annotation style, provided it doesn't violate the transliteration ban for pure monolingual utterances.

## Clinical Number and Term Preservation
- Numbers (e.g., SpO2, heart rate, temperature, duration) MUST be transcribed accurately. Loss or alteration of a clinical number (e.g., "88" to "80") is considered a critical safety failure.
- Medical terminology (e.g., "oxygen", "breathlessness", "diarrhea") must be spelled consistently according to the source language dictionary.

## Pre-Processing / Normalization
- Remove extraneous punctuation unless grammatically necessary for clause splitting (which the `MedicalExtractor` relies on).
- Standardize numbers to text or digits based on a single unified dataset rule (e.g., all numbers represented as digits `88` vs spelled out `eighty eight`), but ensure consistency across the corpus. Digit representation is preferred for medical vitals to match `MedicalExtractor` regexes.
