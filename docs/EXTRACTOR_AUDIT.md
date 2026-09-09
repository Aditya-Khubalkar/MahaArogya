# MahaArogya Medical Extractor Audit

## 1. Supported Symptoms
The current extractor supports 21 symptom categories:
`abdominal_pain`, `fever`, `vomiting`, `chest_pain`, `breathlessness`, `diarrhea`, `dizziness`, `headache`, `numbness`, `cough`, `sore_throat`, `burning_urination`, `joint_pain`, `swelling`, `fatigue`, `nausea`, `vision_loss`, `hearing_loss`, `skin_rash`, `frequent_urination`, `hematuria`.

## 2. Supported Languages
The dictionary uses regex combinations for Marathi, Hindi, English.
However, **Roman Marathi and Hinglish** coverage is sporadic. For instance, "pot dukhtay" is present, but missing many variations.

## 3. Supported Numeric Extraction
**NONE.** The extractor completely ignores numeric values.

## 4. Supported Vital Extraction
**NONE.** The `extract` method does not instantiate or populate the `new_vitals` field of `PatientStateDelta`.

## 5. Missing Emergency Patterns
Critical omissions from `SYMPTOM_PATTERNS`:
- `unconsciousness` / `altered_consciousness`
- `stroke_symptoms` (facial droop, slurred speech are in answers, but not mapped as explicit symptoms for triage)
- `severe_bleeding` (hemorrhage, external bleeding)
- `cardiac_emergency` (heart attack phrasing)
- `anaphylaxis` (throat closing, severe allergy)

## 6. Missing Multilingual Patterns
- **Hindi:** Missing standard phrasing for stroke ("लकवा", "फालिज"), severe bleeding ("खून बह रहा है").
- **Marathi:** Missing phrasing for unconsciousness ("बेशुद्ध").
- **Hinglish / Roman Marathi:** Extremely poor coverage of critical emergencies (e.g., "chakkar aake gir gaya", "saans lene me takleef").
