"""
MahaArogya — Approved Question Bank
Versioned, clinically audited, patient-friendly questions in Marathi, Hindi, English, Roman Marathi, and Hinglish.
Strict Safety Rule: The AI subsystem MUST ONLY select from this approved bank.
"""

from ai.questions.schemas import ApprovedQuestion

APPROVED_QUESTION_BANK: list[ApprovedQuestion] = [
    # --- MANDATORY EMERGENCY / CHEST PAIN QUESTIONS ---
    ApprovedQuestion(
        question_id="q_chest_pain_radiate",
        topic="chest_pain",
        purpose="Screen for acute myocardial infarction radiation to left arm/jaw",
        wording_mr="हा त्रास डाव्या हातात किंवा जबड्याकडे सरकत आहे का?",
        wording_hi="क्या यह दर्द बाएं हाथ या जबड़े की तरफ फैल रहा है?",
        wording_en="Is the pain radiating to your left arm or jaw?",
        wording_roman_mr="Ha tras dava hatat kiva jabdyakade sarakat ahe ka?",
        wording_hinglish="Kya ye pain left arm ya jaw ki taraf spread ho raha hai?",
        information_collected="chest_pain_radiation",
        priority=1,
        emergency_relevance=True,
        required_before_triage=True,
        safety_notes="Red flag screening for cardiac emergency"
    ),
    ApprovedQuestion(
        question_id="q_breathless_severity",
        topic="breathlessness",
        purpose="Screen for acute respiratory distress",
        wording_mr="तुम्हाला बोलताना किंवा बसल्या जागी श्वास घ्यायला त्रास होतोय का?",
        wording_hi="क्या आपको बोलते समय या बैठे-बैठे सांस लेने में ज्यादा तकलीफ हो रही है?",
        wording_en="Are you struggling to breathe even while sitting or speaking?",
        wording_roman_mr="Tumhala boltana kiva baslya jagi shwas ghyayla tras hotoay ka?",
        wording_hinglish="Kya aapko bolte wakt ya baithe baithe breathing me dikkat ho rahi hai?",
        information_collected="breathless_severity",
        priority=1,
        emergency_relevance=True,
        required_before_triage=True,
        safety_notes="Red flag screening for respiratory failure"
    ),

    # --- ABDOMINAL PAIN MODULE ---
    ApprovedQuestion(
        question_id="q_abdo_duration",
        topic="abdominal_pain",
        purpose="Determine duration of abdominal symptoms",
        wording_mr="कधीपासून पोट दुखत आहे?",
        wording_hi="कब से पेट दर्द हो रहा है?",
        wording_en="How long have you had abdominal pain?",
        wording_roman_mr="Kadhipasun pot dukhat ahe?",
        wording_hinglish="Kab se stomach pain ho raha hai?",
        information_collected="abdominal_pain_duration",
        priority=2,
        emergency_relevance=False,
        required_before_triage=True
    ),
    ApprovedQuestion(
        question_id="q_abdo_vomiting",
        topic="abdominal_pain",
        purpose="Check associated vomiting with abdominal pain",
        wording_mr="उलटी किंवा मळमळ होत आहे का?",
        wording_hi="क्या उल्टी या जी मिचलाने की शिकायत है?",
        wording_en="Are you experiencing any vomiting or nausea?",
        wording_roman_mr="Ulti kiva malmal hot ahe ka?",
        wording_hinglish="Kya vomit ya nausea ho raha hai?",
        information_collected="vomiting_status",
        priority=3,
        emergency_relevance=False,
        required_before_triage=False
    ),
    ApprovedQuestion(
        question_id="q_abdo_fever",
        topic="abdominal_pain",
        purpose="Check associated fever with abdominal pain",
        wording_mr="सोबत ताप पण आहे का?",
        wording_hi="क्या साथ में बुखार भी है?",
        wording_en="Do you also have a fever?",
        wording_roman_mr="Sobat tap pan ahe ka?",
        wording_hinglish="Kya saath me fever bhi hai?",
        information_collected="fever_status",
        priority=3,
        emergency_relevance=False,
        required_before_triage=False
    ),

    # --- FEVER MODULE ---
    ApprovedQuestion(
        question_id="q_fever_duration",
        topic="fever",
        purpose="Determine duration of fever",
        wording_mr="ताप किती दिवसांपासून येत आहे?",
        wording_hi="बुखार कितने दिनों से आ रहा है?",
        wording_en="How many days have you had a fever?",
        wording_roman_mr="Tap kiti divasanpasun yet ahe?",
        wording_hinglish="Fever kitne days se aa raha hai?",
        information_collected="fever_duration",
        priority=2,
        emergency_relevance=False,
        required_before_triage=True
    ),
    ApprovedQuestion(
        question_id="q_fever_chills",
        topic="fever",
        purpose="Check for chills / rigors (malaria / dengue screening)",
        wording_mr="थंडी वाजून ताप येतो का?",
        wording_hi="क्या ठंड लगकर बुखार आ रहा है?",
        wording_en="Is the fever accompanied by chills or shivering?",
        wording_roman_mr="Thandi vajun tap yeto ka?",
        wording_hinglish="Kya thand lagkar fever aa raha hai?",
        information_collected="fever_chills",
        priority=4,
        emergency_relevance=False,
        required_before_triage=False
    ),

    # --- VOMITING / DIARRHEA MODULE ---
    ApprovedQuestion(
        question_id="q_vomit_blood",
        topic="vomiting",
        purpose="Screen for upper GI bleeding (hematemesis)",
        wording_mr="उलटीमध्ये रक्त पडले आहे का?",
        wording_hi="क्या उल्टी में खून आया है?",
        wording_en="Have you seen any blood in your vomit?",
        wording_roman_mr="Ulti madhe rakt padle ahe ka?",
        wording_hinglish="Kya vomit me blood aaya hai?",
        information_collected="vomit_blood",
        priority=1,
        emergency_relevance=True,
        required_before_triage=True,
        safety_notes="Red flag screening for GI hemorrhage"
    )
]


def get_all_questions() -> list[ApprovedQuestion]:
    return APPROVED_QUESTION_BANK
