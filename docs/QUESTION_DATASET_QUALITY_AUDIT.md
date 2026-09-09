# Question Dataset Quality Audit

This document summarizes the independent quality audit performed on the newly generated dataset comprising 5,000 synthetic `PatientState` examples and 86 real-world MediTOD interactions.

## 1. Dataset Statistics
- **Total Examples:** 5,086
- **Splits:** Train: 4058, Val: 500, Test: 528
- **Sources:** Synthetic (5000), MediTOD (86)

## 2. Class and Domain Distribution
The programmatic logic successfully randomized and balanced the label distribution across domains. No single domain or question dominates.
- **Top Domain:** Swelling (6.8%), Cough (6.7%), Joint Pain (6.6%), Chest (6.6%), Abdominal (6.6%)
- **Bottom Domain:** Numbness (5.5%), Vomiting (5.6%), Headache (5.7%)
- **Distribution Status:** **EXCELLENT**. All 16 primary symptom domains are perfectly balanced across the dataset.

## 3. Synthetic Generation Logic & Next Questions
- The `PatientStates` represent valid logical blocks where a symptom is active and certain red-flag questions are deliberately left unanswered.
- The assigned labels (next questions) are 100% accurate according to the deterministic Safety Engine rules.

## 4. Diversity and Template Repetition
The dataset suffers from catastrophic lack of linguistic diversity.
- Every synthetic example uses an identical hardcoded string format: `"Patient: I am experiencing {symptom}."`
- For example, the exact string `"Patient: I am experiencing joint pain."` appears **241 times**.
- Because the context is uniformly identical, the dataset has extremely low variance in conversational history.

## 5. Memorization Vulnerability
- **STATUS: EXTREMELY VULNERABLE.**
- Because the input strings and `[STATE]` dictionary dumps are entirely rigid templates, the neural ranker (MuRIL) will simply memorize the hardcoded string structures. It will not learn generalized conversational comprehension. It will operate purely as a fragile lookup table rather than an NLP model.

## 6. Language Variants Representation
- **English:** 5,000 examples (98.3%)
- **Other (MediTOD / Unknown):** 86 examples (1.7%)
- **Marathi, Hindi, Roman Marathi, Hinglish:** **0 examples.**
- The synthetic dataset generator output is entirely in English. If trained on this, the multilingual MuRIL model will severely underperform on the exact demographic this system targets (Marathi/Hindi speakers).

## 7. Conclusion: Is it Safe to Train On?

**STATUS: NOT SAFE TO TRAIN ON.**

While the *labels* (Y) are now 100% accurate and perfectly balanced, the *features* (X) are completely corrupted by lack of diversity. Training on this dataset will result in a model that memorizes static English templates and instantly fails when presented with real-world conversational variations or local languages (Marathi, Hindi, Hinglish).

**Next Step Required:** 
Before training, the `build_synthetic_ranking_dataset.py` script must be rewritten to incorporate:
1. Dynamic, multi-turn conversational templates.
2. Direct generation or translation of `PatientState` history into Marathi, Hindi, Roman Marathi, and Hinglish.
3. Natural permutations of symptoms (e.g. typos, colloquialisms).
