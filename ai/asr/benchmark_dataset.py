"""
MahaArogya — Multilingual ASR Benchmark Dataset (100 Utterances)
Reference transcriptions covering Marathi, Hindi, English, Roman Marathi, Hinglish, and Code-Switching.
Used for WER (Word Error Rate), CER (Character Error Rate), and Medical Term Accuracy benchmarking.
"""

import json
from pathlib import Path

BENCHMARK_UTTERANCES = [
    # --- 1-20: MARATHI (DEVANAGARI) ---
    {"id": "mr_01", "lang": "mr", "category": "Marathi", "reference": "माझं पोट दोन दिवसांपासून खूप दुखत आहे.", "medical_terms": ["पोट दुखणे"], "symptoms": ["abdominal pain"]},
    {"id": "mr_02", "lang": "mr", "category": "Marathi", "reference": "मला काल रात्रीपासून खूप ताप आला आहे.", "medical_terms": ["ताप"], "symptoms": ["fever"]},
    {"id": "mr_03", "lang": "mr", "category": "Marathi", "reference": "माझ्या छातीत दुखतंय आणि श्वास घ्यायला त्रास होतोय.", "medical_terms": ["छातीत दुखणे", "श्वास त्रास"], "symptoms": ["chest pain", "breathlessness"]},
    {"id": "mr_04", "lang": "mr", "category": "Marathi", "reference": "उजव्या हातात आणि खांद्यात कळ मारत आहे.", "medical_terms": ["हात", "खांदा"], "symptoms": ["arm pain", "shoulder pain"]},
    {"id": "mr_05", "lang": "mr", "category": "Marathi", "reference": "कालपासून चार वेळा उलट्या झाल्या आहेत.", "medical_terms": ["उलट्या"], "symptoms": ["vomiting"]},
    {"id": "mr_06", "lang": "mr", "category": "Marathi", "reference": "मला चक्कर येत आहे आणि डोके खूप दुखत आहे.", "medical_terms": ["चक्कर", "डोकेदुखी"], "symptoms": ["dizziness", "headache"]},
    {"id": "mr_07", "lang": "mr", "category": "Marathi", "reference": "माझ्या घशात खवखव आहे आणि खोकला येतोय.", "medical_terms": ["घसा", "खोकला"], "symptoms": ["cough", "sore throat"]},
    {"id": "mr_08", "lang": "mr", "category": "Marathi", "reference": "दोन दिवसांपासून जुलाब थांबत नाहीत.", "medical_terms": ["जुलाब"], "symptoms": ["diarrhea"]},
    {"id": "mr_09", "lang": "mr", "category": "Marathi", "reference": "माझ्या पाय दुखतात आणि पायावर सूज आली आहे.", "medical_terms": ["पाय", "सूज"], "symptoms": ["leg pain", "swelling"]},
    {"id": "mr_10", "lang": "mr", "category": "Marathi", "reference": "मला मधुमेहाचा आजार आहे आणि माझी साखरेची पातळी वाढली आहे.", "medical_terms": ["मधुमेह", "साखर"], "symptoms": ["diabetes"]},
    {"id": "mr_11", "lang": "mr", "category": "Marathi", "reference": "डोळ्यांसमोर अंधारी येत आहे आणि मळमळ होत आहे.", "medical_terms": ["अंधारी", "मळमळ"], "symptoms": ["nausea", "blurred vision"]},
    {"id": "mr_12", "lang": "mr", "category": "Marathi", "reference": "माझ्या पाठीत तीव्र वेदना होत आहेत.", "medical_terms": ["पाठ", "वेदना"], "symptoms": ["back pain"]},
    {"id": "mr_13", "lang": "mr", "category": "Marathi", "reference": "लघवी करताना खूप जळजळ होत आहे.", "medical_terms": ["लघवी", "जळजळ"], "symptoms": ["burning urination"]},
    {"id": "mr_14", "lang": "mr", "category": "Marathi", "reference": "माझ्या मुलाला ३ दिवसांपासून १०२ डिग्री ताप आहे.", "medical_terms": ["ताप"], "symptoms": ["high fever"]},
    {"id": "mr_15", "lang": "mr", "category": "Marathi", "reference": "अचानक डावा हात सुन्न झाला आहे.", "medical_terms": ["हात सुन्न"], "symptoms": ["numbness"]},
    {"id": "mr_16", "lang": "mr", "category": "Marathi", "reference": "मला रक्ताची उलटी झाली आहे.", "medical_terms": ["रक्त", "उलटी"], "symptoms": ["hematemesis"]},
    {"id": "mr_17", "lang": "mr", "category": "Marathi", "reference": "माझ्या कानात खूप जोरात वेदना होत आहेत.", "medical_terms": ["कान", "वेदना"], "symptoms": ["earache"]},
    {"id": "mr_18", "lang": "mr", "category": "Marathi", "reference": "त्वचेवर लाल पुरळ उठले आहेत आणि खाज येत आहे.", "medical_terms": ["पुरळ", "खाज"], "symptoms": ["rash", "itching"]},
    {"id": "mr_19", "lang": "mr", "category": "Marathi", "reference": "माझे डोके फिरल्यासारखे वाटत आहे आणि थकवा आहे.", "medical_terms": ["थकवा"], "symptoms": ["fatigue"]},
    {"id": "mr_20", "lang": "mr", "category": "Marathi", "reference": "अपघात झाल्यामुळे पायाला जबर दुखापत झाली आहे.", "medical_terms": ["दुखापत"], "symptoms": ["trauma"]},

    # --- 21-40: HINDI (DEVANAGARI) ---
    {"id": "hi_01", "lang": "hi", "category": "Hindi", "reference": "मुझे दो दिनों से पेट में तेज दर्द हो रहा है।", "medical_terms": ["पेट दर्द"], "symptoms": ["abdominal pain"]},
    {"id": "hi_02", "lang": "hi", "category": "Hindi", "reference": "कल रात से तेज बुखार और सिरदर्द है।", "medical_terms": ["बुखार", "सिरदर्द"], "symptoms": ["fever", "headache"]},
    {"id": "hi_03", "lang": "hi", "category": "Hindi", "reference": "छाती में भारीपन है और सांस लेने में तकलीफ हो रही है।", "medical_terms": ["छाती", "सांस तकलीफ"], "symptoms": ["chest pain", "shortness of breath"]},
    {"id": "hi_04", "lang": "hi", "category": "Hindi", "reference": "मुझे तीन बार उल्टी आ चुकी है।", "medical_terms": ["उल्टी"], "symptoms": ["vomiting"]},
    {"id": "hi_05", "lang": "hi", "category": "Hindi", "reference": "चक्कर आ रहे हैं और आंखें बंद करने का मन कर रहा है।", "medical_terms": ["चक्कर"], "symptoms": ["dizziness"]},
    {"id": "hi_06", "lang": "hi", "category": "Hindi", "reference": "गले में खराश है और लगातार खांसी आ रही है।", "medical_terms": ["गला", "खांसी"], "symptoms": ["sore throat", "cough"]},
    {"id": "hi_07", "lang": "hi", "category": "Hindi", "reference": "दस्त रुक नहीं रहे हैं और कमजोरी लग रही है।", "medical_terms": ["दस्त", "कमजोरी"], "symptoms": ["diarrhea", "weakness"]},
    {"id": "hi_08", "lang": "hi", "category": "Hindi", "reference": "दाएं हाथ में दर्द और सुन्नपन महसूस हो रहा है।", "medical_terms": ["हाथ", "सुन्नपन"], "symptoms": ["numbness"]},
    {"id": "hi_09", "lang": "hi", "category": "Hindi", "reference": "मुझे उच्च रक्तचाप और मधुमेह की बीमारी है।", "medical_terms": ["रक्तचाप", "मधुमेह"], "symptoms": ["hypertension", "diabetes"]},
    {"id": "hi_10", "lang": "hi", "category": "Hindi", "reference": "पैरों में सूजन है और चलने में दर्द होता है।", "medical_terms": ["सूजन", "दर्द"], "symptoms": ["swelling"]},
    {"id": "hi_11", "lang": "hi", "category": "Hindi", "reference": "जी मिचला रहा है और उल्टी जैसा महसूस हो रहा है।", "medical_terms": ["जी मिचलाना"], "symptoms": ["nausea"]},
    {"id": "hi_12", "lang": "hi", "category": "Hindi", "reference": "कमर में तेज लचक आ गई है।", "medical_terms": ["कमर"], "symptoms": ["back pain"]},
    {"id": "hi_13", "lang": "hi", "category": "Hindi", "reference": "पेशाब में जलन और बार-बार जाने की जरूरत होती है।", "medical_terms": ["पेशाब", "जलन"], "symptoms": ["dysuria"]},
    {"id": "hi_14", "lang": "hi", "category": "Hindi", "reference": "बच्चे को १०१ डिग्री बुखार है और वह कुछ खा नहीं रहा है।", "medical_terms": ["बुखार"], "symptoms": ["child fever"]},
    {"id": "hi_15", "lang": "hi", "category": "Hindi", "reference": "अचानक चेहरे की एक तरफ का हिस्सा सुन्न हो गया है।", "medical_terms": ["चेहरा", "सुन्न"], "symptoms": ["facial paralysis"]},
    {"id": "hi_16", "lang": "hi", "category": "Hindi", "reference": "खून की उल्टी हुई है तुरंत डॉक्टर को दिखाना है।", "medical_terms": ["खून", "उल्टी"], "symptoms": ["hematemesis"]},
    {"id": "hi_17", "lang": "hi", "category": "Hindi", "reference": "कान में तेज दर्द और घंटी बजने जैसी आवाज आ रही है।", "medical_terms": ["कान", "दर्द"], "symptoms": ["tinnitus"]},
    {"id": "hi_18", "lang": "hi", "category": "Hindi", "reference": "शरीर पर लाल चकत्ते पड़ गए हैं।", "medical_terms": ["चकत्ते"], "symptoms": ["rash"]},
    {"id": "hi_19", "lang": "hi", "category": "Hindi", "reference": "बहुत ज्यादा थकान और आलस महसूस हो रहा है।", "medical_terms": ["थकान"], "symptoms": ["fatigue"]},
    {"id": "hi_20", "lang": "hi", "category": "Hindi", "reference": "हाथ में चोट लग गई है और खून बह रहा है।", "medical_terms": ["चोट", "खून"], "symptoms": ["bleeding"]},

    # --- 41-60: ENGLISH ---
    {"id": "en_01", "lang": "en", "category": "English", "reference": "I have severe abdominal pain for two days.", "medical_terms": ["abdominal pain"], "symptoms": ["abdominal pain"]},
    {"id": "en_02", "lang": "en", "category": "English", "reference": "High fever and persistent cough since yesterday morning.", "medical_terms": ["fever", "cough"], "symptoms": ["fever", "cough"]},
    {"id": "en_03", "lang": "en", "category": "English", "reference": "I am experiencing sharp chest pain and shortness of breath.", "medical_terms": ["chest pain", "shortness of breath"], "symptoms": ["chest pain", "shortness of breath"]},
    {"id": "en_04", "lang": "en", "category": "English", "reference": "I vomited twice this afternoon and feel dehydrated.", "medical_terms": ["vomited", "dehydrated"], "symptoms": ["vomiting"]},
    {"id": "en_05", "lang": "en", "category": "English", "reference": "Feeling very dizzy and lightheaded when standing up.", "medical_terms": ["dizzy", "lightheaded"], "symptoms": ["dizziness"]},
    {"id": "en_06", "lang": "en", "category": "English", "reference": "I have a sore throat and difficulty swallowing food.", "medical_terms": ["sore throat", "swallowing"], "symptoms": ["sore throat"]},
    {"id": "en_07", "lang": "en", "category": "English", "reference": "Severe diarrhea and stomach cramps for twenty four hours.", "medical_terms": ["diarrhea", "cramps"], "symptoms": ["diarrhea"]},
    {"id": "en_08", "lang": "en", "category": "English", "reference": "Numbness and tingling sensation in my left hand.", "medical_terms": ["numbness", "tingling"], "symptoms": ["numbness"]},
    {"id": "en_09", "lang": "en", "category": "English", "reference": "I am a diabetic patient with high blood sugar levels.", "medical_terms": ["diabetic", "blood sugar"], "symptoms": ["hyperglycemia"]},
    {"id": "en_10", "lang": "en", "category": "English", "reference": "Swelling in both ankles and difficulty walking.", "medical_terms": ["swelling", "ankles"], "symptoms": ["edema"]},
    {"id": "en_11", "lang": "en", "category": "English", "reference": "Constant nausea and loss of appetite.", "medical_terms": ["nausea", "appetite"], "symptoms": ["nausea"]},
    {"id": "en_12", "lang": "en", "category": "English", "reference": "Lower back pain radiating down my right leg.", "medical_terms": ["lower back pain", "radiating"], "symptoms": ["sciatica"]},
    {"id": "en_13", "lang": "en", "category": "English", "reference": "Burning sensation during urination and frequent urge.", "medical_terms": ["burning sensation", "urination"], "symptoms": ["UTI"]},
    {"id": "en_14", "lang": "en", "category": "English", "reference": "My child has a temperature of one hundred two degrees.", "medical_terms": ["temperature"], "symptoms": ["fever"]},
    {"id": "en_15", "lang": "en", "category": "English", "reference": "Sudden facial weakness on the right side.", "medical_terms": ["facial weakness"], "symptoms": ["stroke signal"]},
    {"id": "en_16", "lang": "en", "category": "English", "reference": "Coughing up blood and feeling extremely weak.", "medical_terms": ["coughing up blood"], "symptoms": ["hemoptysis"]},
    {"id": "en_17", "lang": "en", "category": "English", "reference": "Acute ear pain and reduced hearing capability.", "medical_terms": ["ear pain", "hearing"], "symptoms": ["otitis"]},
    {"id": "en_18", "lang": "en", "category": "English", "reference": "Allergic skin rash with severe itchiness.", "medical_terms": ["skin rash", "itchiness"], "symptoms": ["allergy"]},
    {"id": "en_19", "lang": "en", "category": "English", "reference": "Extreme fatigue and body pain after physical exertion.", "medical_terms": ["fatigue", "body pain"], "symptoms": ["fatigue"]},
    {"id": "en_20", "lang": "en", "category": "English", "reference": "Deep laceration on knee with active bleeding.", "medical_terms": ["laceration", "bleeding"], "symptoms": ["wound"]},

    # --- 61-75: ROMAN MARATHI ---
    {"id": "rm_01", "lang": "mr", "category": "Roman Marathi", "reference": "Majha pot don divas pasun khup dukhtay.", "medical_terms": ["pot dukhtay"], "symptoms": ["abdominal pain"]},
    {"id": "rm_02", "lang": "mr", "category": "Roman Marathi", "reference": "Mala kal ratri pasun motha tap ala ahe.", "medical_terms": ["tap"], "symptoms": ["fever"]},
    {"id": "rm_03", "lang": "mr", "category": "Roman Marathi", "reference": "Majhya chhatit dukhatahe ani shwas ghyayla tras hoto.", "medical_terms": ["chhatit dukhatahe", "shwas tras"], "symptoms": ["chest pain"]},
    {"id": "rm_04", "lang": "mr", "category": "Roman Marathi", "reference": "Kal pasun 4 vela vomit zala ahe.", "medical_terms": ["vomit"], "symptoms": ["vomiting"]},
    {"id": "rm_05", "lang": "mr", "category": "Roman Marathi", "reference": "Mala khup chakkar yet ahe ani doka dukhtay.", "medical_terms": ["chakkar", "doka"], "symptoms": ["dizziness"]},
    {"id": "rm_06", "lang": "mr", "category": "Roman Marathi", "reference": "Ghasyat tras ahe ani khokla yeth ahe.", "medical_terms": ["khokla"], "symptoms": ["cough"]},
    {"id": "rm_07", "lang": "mr", "category": "Roman Marathi", "reference": "Don divas pasun loose motions thambat nahit.", "medical_terms": ["loose motions"], "symptoms": ["diarrhea"]},
    {"id": "rm_08", "lang": "mr", "category": "Roman Marathi", "reference": "Dava hat sunn jhala ahe.", "medical_terms": ["hat sunn"], "symptoms": ["numbness"]},
    {"id": "rm_09", "lang": "mr", "category": "Roman Marathi", "reference": "Mala sugar cha tras ahe ani bp pan vadhla ahe.", "medical_terms": ["sugar", "bp"], "symptoms": ["diabetes"]},
    {"id": "rm_10", "lang": "mr", "category": "Roman Marathi", "reference": "Payala khup sooj ali ahe.", "medical_terms": ["sooj"], "symptoms": ["swelling"]},
    {"id": "rm_11", "lang": "mr", "category": "Roman Marathi", "reference": "Malmal hota ahe ani ulti sarki vatate.", "medical_terms": ["malmal", "ulti"], "symptoms": ["nausea"]},
    {"id": "rm_12", "lang": "mr", "category": "Roman Marathi", "reference": "Pathit khup severe pain ahe.", "medical_terms": ["severe pain"], "symptoms": ["back pain"]},
    {"id": "rm_13", "lang": "mr", "category": "Roman Marathi", "reference": "Urine karta burning hoto.", "medical_terms": ["burning"], "symptoms": ["UTI"]},
    {"id": "rm_14", "lang": "mr", "category": "Roman Marathi", "reference": "Bala la 102 fever ahe 3 divas pasun.", "medical_terms": ["fever"], "symptoms": ["child fever"]},
    {"id": "rm_15", "lang": "mr", "category": "Roman Marathi", "reference": "Achanak face cha ek side numbness ala.", "medical_terms": ["numbness"], "symptoms": ["stroke signal"]},

    # --- 76-90: HINGLISH ---
    {"id": "hg_01", "lang": "hi", "category": "Hinglish", "reference": "Mera stomach 2 days se severe pain kar raha hai.", "medical_terms": ["severe pain"], "symptoms": ["abdominal pain"]},
    {"id": "hg_02", "lang": "hi", "category": "Hinglish", "reference": "Kal night se fever aur headache hai.", "medical_terms": ["fever", "headache"], "symptoms": ["fever"]},
    {"id": "hg_03", "lang": "hi", "category": "Hinglish", "reference": "Chest me heavy feeling aur breathing problem ho rahi hai.", "medical_terms": ["breathing problem"], "symptoms": ["chest pain"]},
    {"id": "hg_04", "lang": "hi", "category": "Hinglish", "reference": "Aaj morning se 3 baar vomit ho chuka hai.", "medical_terms": ["vomit"], "symptoms": ["vomiting"]},
    {"id": "hg_05", "lang": "hi", "category": "Hinglish", "reference": "Mujhe dizziness aa rahi hai aur chakkar aa rahe hain.", "medical_terms": ["dizziness"], "symptoms": ["dizziness"]},
    {"id": "hg_06", "lang": "hi", "category": "Hinglish", "reference": "Throat pain hai aur dry cough chal raha hai.", "medical_terms": ["dry cough"], "symptoms": ["cough"]},
    {"id": "hg_07", "lang": "hi", "category": "Hinglish", "reference": "Loose motion stop nahi ho rahe hain.", "medical_terms": ["loose motion"], "symptoms": ["diarrhea"]},
    {"id": "hg_08", "lang": "hi", "category": "Hinglish", "reference": "Right arm me numbness and weakness feel ho raha hai.", "medical_terms": ["numbness"], "symptoms": ["numbness"]},
    {"id": "hg_09", "lang": "hi", "category": "Hinglish", "reference": "Mai high blood pressure aur diabetes ka patient hu.", "medical_terms": ["blood pressure", "diabetes"], "symptoms": ["hypertension"]},
    {"id": "hg_10", "lang": "hi", "category": "Hinglish", "reference": "Legs me swelling hai aur walk karne me problem hai.", "medical_terms": ["swelling"], "symptoms": ["edema"]},
    {"id": "hg_11", "lang": "hi", "category": "Hinglish", "reference": "Nausea ho raha hai aur khane ka man nahi hai.", "medical_terms": ["Nausea"], "symptoms": ["nausea"]},
    {"id": "hg_12", "lang": "hi", "category": "Hinglish", "reference": "Lower back pain radiant ho raha hai leg tak.", "medical_terms": ["Lower back pain"], "symptoms": ["back pain"]},
    {"id": "hg_13", "lang": "hi", "category": "Hinglish", "reference": "Urine pass karte wakt burning sensation hota hai.", "medical_terms": ["burning sensation"], "symptoms": ["UTI"]},
    {"id": "hg_14", "lang": "hi", "category": "Hinglish", "reference": "Baby ko 101 degree high fever hai.", "medical_terms": ["high fever"], "symptoms": ["child fever"]},
    {"id": "hg_15", "lang": "hi", "category": "Hinglish", "reference": "Face ka ek side suddenly paralyze lag raha hai.", "medical_terms": ["paralyze"], "symptoms": ["stroke signal"]},

    # --- 91-100: CODE-SWITCHING (MARATHI-ENGLISH & HINDI-ENGLISH) ---
    {"id": "cs_01", "lang": "mr", "category": "Code-Switching", "reference": "Majha pot dukhtay, mala lagta severe gastritis cha problem ahe.", "medical_terms": ["gastritis"], "symptoms": ["abdominal pain"]},
    {"id": "cs_02", "lang": "mr", "category": "Code-Switching", "reference": "Kal se fever ahe, temperature check kela tar 101 hot.", "medical_terms": ["fever", "temperature"], "symptoms": ["fever"]},
    {"id": "cs_03", "lang": "mr", "category": "Code-Switching", "reference": "Mala breathless feel hotay, emergency room kuthe ahe?", "medical_terms": ["breathless", "emergency room"], "symptoms": ["breathlessness"]},
    {"id": "cs_04", "lang": "hi", "category": "Code-Switching", "reference": "Mujhe 2 din se vomiting ho rahi hai, lagta hai food poisoning ho gaya.", "medical_terms": ["food poisoning"], "symptoms": ["vomiting"]},
    {"id": "cs_05", "lang": "hi", "category": "Code-Switching", "reference": "Chest pain starting ho gaya hai aur left shoulder tak ja raha hai.", "medical_terms": ["Chest pain"], "symptoms": ["chest pain"]},
    {"id": "cs_06", "lang": "mr", "category": "Code-Switching", "reference": "Mala doctor sobat consult karaychay, OPD token ghyaycha ahe.", "medical_terms": ["OPD token"], "symptoms": ["routine OPD"]},
    {"id": "cs_07", "lang": "hi", "category": "Code-Switching", "reference": "Urine test karwana hai, burning sensation aara hai.", "medical_terms": ["Urine test", "burning sensation"], "symptoms": ["UTI"]},
    {"id": "cs_08", "lang": "mr", "category": "Code-Switching", "reference": "Doka khup pain hotay, migraine cha attack ahe vatta.", "medical_terms": ["migraine"], "symptoms": ["headache"]},
    {"id": "cs_09", "lang": "hi", "category": "Code-Switching", "reference": "Blood pressure high ho gaya hai, dizzy feel ho raha hai.", "medical_terms": ["Blood pressure"], "symptoms": ["hypertension"]},
    {"id": "cs_10", "lang": "mr", "category": "Code-Switching", "reference": "Accident madhe knee fracture jhala ahe, immediately hospital pahije.", "medical_terms": ["knee fracture", "hospital"], "symptoms": ["fracture"]},
]


import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def save_benchmark_dataset(out_path: Path):
    """Save 100-utterance benchmark set to JSON file in data/test/."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(BENCHMARK_UTTERANCES, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved 100-utterance ASR benchmark reference set -> {out_path}")


if __name__ == "__main__":
    out_json = Path(r"C:\MahaArogya\data\test\asr_100_utterances.json")
    save_benchmark_dataset(out_json)
