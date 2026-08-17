"""
MahaArogya — Multilingual Medical Information Extractor
Rule + Pattern-based entity extraction for Marathi, Hindi, English, Roman Marathi, and Hinglish.
Clause-aware negation scoping and PatientStateDelta generation.
"""

import re
from typing import Dict, List, Tuple
from ai.patient_state.schemas import PatientStateDelta, SymptomDetail, Vitals


# Multilingual Dictionary & Flexible Pattern Mapping (Native Marathi, Hindi, English, Hinglish, Roman Marathi)
SYMPTOM_PATTERNS = {
    "abdominal_pain": [
        r"पोट.*?दुख", r"पोटात.*?कळ", r"पोटात.*?वेदना", r"पोटात.*?तीव्र", r"पेट.*?दर्द", r"पेट.*?दुख",
        r"pot.*?dukh", r"pot.*?dukhtay", r"stomach.*?pain", r"abdominal.*?pain", r"belly.*?ache", r"pelvic.*?pain", r"pelvic"
    ],
    "fever": [
        r"\b(?:fever|temp|temperature)\b", r"(?:\b|\s|^)(?:tap|bukhar|ताप|बुखार)(?:\b|\s|$)",
        r"ताप", r"बुखार"
    ],
    "vomiting": [
        r"उलटी", r"उल्टी", r"उलट्या", r"ओकणे", r"वमन", r"\b(?:vomit|vomiting|emesis)\b", r"(?:\b|\s|^)ulti(?:\b|\s|$)"
    ],
    "chest_pain": [
        r"छातीत.*?दुख", r"छातीत.*?कळ", r"छातीत.*?दाब", r"छाती.*?भारीपन", r"सीने.*?दर्द", r"सीने.*?खिंचाव", r"छाती.*?दर्द",
        r"chhati.*?dukh", r"chhatit.*?pain", r"chhati.*?pain", r"chest.*?pain", r"chest.*?heaviness",
        r"chest.*?pressure", r"chest.*?tightness", r"crushing.*?chest", r"crushing.*?substernal", r"substernal"
    ],
    "breathlessness": [
        r"श्वास.*?त्रास", r"श्वास.*?लाग", r"दम.*?लाग", r"श्वास.*?घेण्या", r"सांस.*?तकलीफ", r"सांस.*?फूल", r"सांस.*?लेने",
        r"shwas.*?tras", r"shwas.*?trouble", r"breathless", r"shortness of breath", r"breathing problem", r"dyspnea"
    ],
    "diarrhea": [
        r"जुलाब", r"संडास", r"दस्त", r"पतला.*?दस्त", r"loose motion", r"diarrhea", r"loose.*?stool"
    ],
    "dizziness": [
        r"चक्कर", r"भोवळ", r"अंधारी", r"chakkar", r"\b(?:dizzy|dizziness|lightheaded|faint)\b"
    ],
    "headache": [
        r"डोके.*?दुख", r"डोकेदुखी", r"माथा.*?दुख", r"सिर.*?दर्द", r"सिरदर्द", r"doka.*?dukh", r"\b(?:headache|head pain)\b"
    ],
    "numbness": [
        r"सुन्न", r"मुंग्या", r"सुन", r"(?:\b|\s|^)sunn(?:\b|\s|$)", r"\b(?:numbness|tingling|numb)\b"
    ],
    "cough": [
        r"खोकला", r"खांसी", r"(?:\b|\s|^)(?:khokla|khansi)(?:\b|\s|$)", r"\bcough\b"
    ],
    "sore_throat": [
        r"घसा.*?दुख", r"घसा.*?खवखव", r"घशात.*?खवखव", r"गले.*?खराश", r"गले.*?दर्द", r"gala.*?kharab", r"galyat.*?dukh", r"sore throat", r"throat pain"
    ],
    "burning_urination": [
        r"लघवी.*?जळजळ", r"लघवी.*?त्रास", r"मूत्रखडा", r"पेशाब.*?जलन", r"पेशाब.*?दर्द",
        r"mutrakhada", r"peshab.*?jalan", r"burning.*?urination", r"urination.*?burn", r"dysuria", r"burning sensation.*?urination"
    ],
    "joint_pain": [
        r"सांधे.*?दुख", r"सांधेदुखी", r"सांधेवात", r"जोड़ों.*?दर्द", r"गुडघे.*?दुख",
        r"sandhe.*?dukh", r"sandhivata", r"joint.*?pain", r"arthritis"
    ],
    "swelling": [
        r"सूज", r"सुजले", r"सूजणे", r"सूजन", r"(?:\b|\s|^)sujan(?:\b|\s|$)", r"\b(?:swelling|swollen|edema)\b"
    ],
    "fatigue": [
        r"थकवा", r"अशक्तपणा", r"कमजोरी", r"गळाल्यासारखे", r"(?:\b|\s|^)(?:thakawa|ashaktapana|kamjori)(?:\b|\s|$)",
        r"\b(?:fatigue|exhaustion|weakness|tired)\b"
    ],
    "nausea": [
        r"मळमळ", r"उलटीसारखे", r"जी.*?मिचला", r"(?:\b|\s|^)malmal(?:\b|\s|$)", r"\b(?:nausea|queasy)\b"
    ]
}

# Negation patterns for Marathi, Hindi, English
NEGATION_PATTERNS = [
    r"नाही", r"नाहीत", r"नसून", r"(?:\b|\s|^)(?:nahi|nahit)(?:\b|\s|$)",
    r"नहीं", r"नही",
    r"\b(?:no|not|without|denies|absent)\b"
]

DURATION_PATTERNS = [
    (r"(\d+|दोन|तीन|चार|पाच|एक)\s*(दिवस|दिवसांपासून|दिवसभर|days?|hours?|तास)", r"\1 \2"),
    (r"काल\s*पासून|काल\s*रात्रीपासून|since\s*yesterday|yesterday", "since yesterday"),
    (r"आज\s*सकाळपासून|since\s*this\s*morning|since\s*morning", "since morning"),
]

FREQUENCY_PATTERNS = [
    (r"(\d+|दोन|तीन|चार)\s*(वेळा|बार|times)", r"\1 times"),
]

CLAUSE_DELIMITERS = r"[,;.\n|।॥]|\s+(?:आणि|व|पण|परंतु|किंतु|और|पर|मगर|par|but|however|lekin|ani|and)\s+"


class MedicalExtractor:
    """Extracts structured medical entities and clause-scoped negations from patient text."""

    def extract(self, conversation_id: str, input_text: str) -> PatientStateDelta:
        """
        Extracts medical facts from text and returns a PatientStateDelta.
        """
        text_lower = input_text.lower()
        extracted_symptoms: Dict[str, SymptomDetail] = {}
        negated_symptoms: List[str] = []
        extracted_answers: Dict[str, bool] = {}

        # Extract structured answers for red flags across code-switched text
        if re.search(r"radiat|jaw|left arm|left hand|dava hat|dava hatat|back|shoulder", text_lower):
            extracted_answers["chest_pain_radiation"] = True

        if re.search(r"diaphoresis|sweating|sweat|cold sweat", text_lower):
            extracted_answers["diaphoresis"] = True

        if re.search(r"after eating|postprandial|spicy food|antacid", text_lower):
            extracted_answers["postprandial"] = True

        if re.search(r"palpation|reproducible|leaning forward|sternum|costochondritis|positional", text_lower):
            extracted_answers["positional"] = True

        if re.search(r"khoon ki ulti|ulti.*?rakt|vomit.*?blood|blood in vomit", text_lower):
            extracted_answers["vomit_blood"] = True

        if re.search(r"slurred speech|dysarthria|difficulty speaking|speech difficulty", text_lower):
            extracted_answers["slurred_speech"] = True

        if re.search(r"facial droop|facial drooping|arm weakness|face droop", text_lower):
            extracted_answers["slurred_speech"] = True

        if re.search(r"neck stiffness|nuchal rigidity|stiff neck", text_lower):
            extracted_answers["neck_stiffness"] = True

        if re.search(r"positive.*pregnancy|pregnant|pregnancy test", text_lower):
            extracted_answers["pregnant"] = True

        if re.search(r"explosive headache|thunderclap|worst headache|peak.*within seconds", text_lower):
            extracted_answers["thunderclap"] = True

        if re.search(r"spotting|vaginal bleeding|bleeding per vaginum", text_lower):
            extracted_answers["first_trimester_bleeding"] = True

        if re.search(r"stung|sting|hives|lip swelling|airway swelling|anaphylaxis", text_lower):
            extracted_answers["anaphylaxis"] = True

        if re.search(r"diabetic|diabetes", text_lower):
            extracted_answers["diabetic"] = True

        if re.search(r"fruity breath|kussmaul|blood sugar \d{3}|dka", text_lower):
            extracted_answers["fruity_breath"] = True

        if re.search(r"testicular|testicle|scrotal", text_lower):
            extracted_answers["testicular_pain"] = True

        if re.search(r"cast.*?pain|compartment|pale limb|tight calf", text_lower):
            extracted_answers["compartment_syndrome"] = True

        if re.search(r"suicidal|self-harm|self harm|intent for self-harm|plan to die", text_lower):
            extracted_answers["suicidal_ideation"] = True

        # Extract duration & frequency
        extracted_duration = None
        for pattern, canon in DURATION_PATTERNS:
            match = re.search(pattern, input_text, re.IGNORECASE)
            if match:
                extracted_duration = match.group(0)
                break

        extracted_freq = None
        for pattern, canon in FREQUENCY_PATTERNS:
            match = re.search(pattern, input_text, re.IGNORECASE)
            if match:
                extracted_freq = match.group(0)
                break

        # Split input into clauses so negation does not leak across clauses
        clauses = re.split(CLAUSE_DELIMITERS, input_text, flags=re.IGNORECASE)

        for clause in clauses:
            clause_str = clause.strip()
            if not clause_str:
                continue

            # Special case for phrases like 'थांबत नाहीत' (doesn't stop) vs symptom negation
            clause_is_negated = any(re.search(neg_p, clause_str, re.IGNORECASE) for neg_p in NEGATION_PATTERNS)
            if "थांबत नाही" in clause_str or "थांबत नाहीत" in clause_str or "रुक नहीं" in clause_str or "रुक नही" in clause_str or "won't stop" in clause_str.lower() or "doesn't stop" in clause_str.lower():
                clause_is_negated = False

            # Special case: 'facial weakness' is a neurological symptom (not generalized fatigue)
            if "facial weakness" in clause_str.lower() or "arm weakness" in clause_str.lower() or "leg weakness" in clause_str.lower():
                temp_clause = re.sub(r"facial weakness|arm weakness|leg weakness", "", clause_str, flags=re.IGNORECASE)
            else:
                temp_clause = clause_str

            for sym_code, patterns in SYMPTOM_PATTERNS.items():
                target_text = temp_clause if sym_code == "fatigue" else clause_str
                for p in patterns:
                    if re.search(p, target_text, re.IGNORECASE | re.DOTALL):
                        if clause_is_negated:
                            if sym_code not in negated_symptoms:
                                negated_symptoms.append(sym_code)
                        else:
                            detail = SymptomDetail(
                                present=True,
                                duration=extracted_duration,
                                frequency=extracted_freq,
                                severity="severe" if "severe" in text_lower or "khup" in text_lower or "खूप" in text_lower or "तीव्र" in text_lower or "acute" in text_lower or "crushing" in text_lower else "moderate"
                            )
                            extracted_symptoms[sym_code] = detail
                        break

        return PatientStateDelta(
            conversation_id=conversation_id,
            new_input=input_text,
            new_symptoms=extracted_symptoms,
            new_negations=negated_symptoms,
            new_answers=extracted_answers
        )
