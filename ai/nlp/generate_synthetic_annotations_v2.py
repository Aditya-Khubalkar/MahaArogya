import json
import random
import re
from pathlib import Path
from typing import List, Dict, Any

SEED = 42
random.seed(SEED)

OUTPUT_DIR = Path("C:/MahaArogya/data/annotations_v2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BENCHMARK_PATH = Path("C:/MahaArogya/evaluation/test_sets/extraction_test_set.json")

# 16 Core Symptoms
SYMPTOM_NAMES = [
    "abdominal_pain", "fever", "headache", "chest_pain", "breathlessness",
    "vomiting", "diarrhea", "dizziness", "cough", "sore_throat",
    "burning_urination", "numbness", "joint_pain", "swelling", "fatigue", "nausea"
]

# Varied phrasing dictionaries per language
PHRASES_MR = {
    "abdominal_pain": ["पोटात तीव्र कळा येत आहेत", "पोटात असह्य दुखत आहे", "पोट खूप दुखत आहे", "पोटात बारीक दुखत राहते", "पोटात पेटके येत आहेत"],
    "fever": ["अंगात खूप भरून ताप आला आहे", "रात्रीपासून हुडहुडी भरून ताप आहे", "खूप ताप चढला आहे", "अंग तापाने फणफणले आहे", "सतत ताप जाणवतो"],
    "headache": ["डोक्यात प्रचंड ठणका लागला आहे", "डोके फुटल्यासारखे दुखते आहे", "डोकेदुखी अजिबात थांबत नाही", "कपाळात तीव्र ठणका आहे", "डोके खूप जड झाले आहे"],
    "chest_pain": ["छातीत डाव्या बाजूला खूप दुखते आहे", "छातीवर प्रचंड दाब जाणवत आहे", "छातीत तीव्र टोचल्यासारखे होतेय", "छातीत असह्य वेदना होत आहेत"],
    "breathlessness": ["श्वास घ्यायला खूप धाप लागते आहे", "श्वास पूर्ण भरून घेता येत नाही", "दम लागतो आहे", "श्वास घेताना छातीत आवळल्यासारखे वाटते"],
    "vomiting": ["सतत पित्ताच्या उलट्या होत आहेत", "काहीही खाल्ले की लगेच उलटी होते", "सकाळपासून उलट्यांचा त्रास आहे", "उलट्या होऊन खूप गळून गेलो आहे"],
    "diarrhea": ["पातळ जुलाब सतत सुरू आहेत", "संडासला पाण्यासारखे पातळ होते आहे", "शौचाला वारंवार पातळ होत आहे", "जुलाब थांबत नाहीत"],
    "dizziness": ["उठून उभे राहिले की भोवळ येते", "डोळ्यांसमोर अंधारी येऊन चक्कर येते", "चक्कर येऊन पडल्यासारखे होते", "डोकं गरगर फिरत आहे"],
    "cough": ["कोरडा खोकला खूप येतो आहे", "छातीतून कफयुक्त खोकला निघत आहे", "सतत खोकल्याची उबळ येत आहे", "खोकून खोकून छाती दुखायला लागली"],
    "sore_throat": ["घसा खूप सुजल्यासारखा वाटतोय", "घशात भयंकर दुखते आहे व गिळता येत नाही", "घसा आतून लाल झाला आहे", "घशात तीव्र आग होतेय"],
    "burning_urination": ["लघवीला भयंकर जळजळ होते आहे", "लघवी करताना खूप त्रास होतोय", "लघवीला थेंब थेंब आग होते", "लघवी करताना आग होऊन आगपेटीसारखे वाटते"],
    "numbness": ["डाव्या हाताला मुंग्या येऊन बधिर झाला आहे", "पायाची बोटे सुन्न झाली आहेत", "हातापायाला बधिरता आली आहे", "चेहऱ्याची एक बाजू सुन्न वाटते"],
    "joint_pain": ["दोन्ही गुडघ्यांचे सांधे खूप दुखत आहेत", "हातापायांचे सांधे प्रचंड दुखतात", "सांधे जखडल्यासारखे वाटतात", "गुडघे व मनगटाचे सांधे ठणकतात"],
    "swelling": ["पायाला आणि घोट्याला खूप सूज आली आहे", "चेहऱ्यावर आणि हातावर सूज चढली आहे", "दोन्ही पायांवर पाणी भरल्यासारखी सूज आहे", "पायाची सूज वाढत चालली आहे"],
    "fatigue": ["अंगात अजिबात त्राण उरलेला नाही", "प्रचंड अशक्तपणा जाणवतो आहे", "हातपाय पूर्ण गळाले आहेत", "अतिशय थकवा येऊन पडून राहावेसे वाटते"],
    "nausea": ["सारखे मळमळल्यासारखे वाटते आहे", "छातीत मळमळत असून अस्वस्थ वाटते", "अन्नाचा वास आला की जीव मळमळतो", "सारखी मळमळ होत आहे"]
}

PHRASES_HI = {
    "abdominal_pain": ["पेट में बहुत जोर से मरोड़ उठ रही है", "पेट का दर्द बर्दाश्त से बाहर है", "पेट के निचले हिस्से में तेज दर्द है", "पेट में खिंचाव और दर्द है"],
    "fever": ["तेज बुखार से पूरा बदन तप रहा है", "कल से कंपकंपी लगकर बुखार आ रहा है", "बदन में बहुत तेज हरारत और बुखार है", "बुखार टूट ही नहीं रहा है"],
    "headache": ["सिर में बहुत तेज भारीपन और दर्द है", "सिर हथौड़े की तरह फट रहा है", "आधे सिर में असहनीय दर्द हो रहा है", "सिर का दर्द कम नहीं हो रहा"],
    "chest_pain": ["सीने के बीच में बहुत भारी दर्द महसूस हो रहा है", "सीने में दबाव और खिंचाव सा लग रहा है", "सीने में बहुत तेज चुभन वाला दर्द है"],
    "breathlessness": ["सांस बहुत उखड़ रही है और फूल रही है", "गहरी सांस लेने में भारी तकलीफ हो रही है", "सांस घुटती हुई महसूस हो रही है"],
    "vomiting": ["लगातार उल्टियां हो रही हैं कुछ पच नहीं रहा", "पानी पीने पर भी उल्टी आ रही है", "सुबह से तीन-चार बार उल्टी हो चुकी है"],
    "diarrhea": ["पानी की तरह पतले दस्त हो रहे हैं", "पेट खराब है और बार-बार दस्त लग रहे हैं", "दस्त की वजह से बहुत कमजोरी आ गई है"],
    "dizziness": ["सिर चकरा रहा है और चक्कर आ रहे हैं", "खड़े होने पर आंखों के आगे अंधेरा छा जाता है", "कमजोरी से सिर घूम रहा है"],
    "cough": ["बहुत तेज सूखी खांसी उठ रही है", "खांसते खांसते सीने में दर्द होने लगा है", "बलगम वाली खांसी बहुत परेशान कर रही है"],
    "sore_throat": ["गले में बहुत खराश और दर्द है", "पानी निगलने में भी गले में तेज दर्द हो रहा है", "गला पूरी तरह बैठा और छिला हुआ है"],
    "burning_urination": ["पेशाब करते समय बहुत तेज जलन हो रही है", "पेशाब में आग जैसी जलन महसूस होती है", "पेशाब रुक-रुक कर और जलन के साथ आता है"],
    "numbness": ["बाएं हाथ में सुन्नपन और झनझनाहट हो रही है", "पैर बिल्कुल सुन्न पड़ गया है", "उंगलियों में कोई अहसास नहीं हो रहा"],
    "joint_pain": ["घुटनों और जोड़ों में भयंकर दर्द है", "उठने बैठने में जोड़ों में दर्द होता है", "सारे जोड़ों में जकड़न और दर्द महसूस हो रहा है"],
    "swelling": ["पैरों के पंजों और टखनों पर भारी सूजन है", "हाथ और चेहरे पर सूजन आ गई है", "घुटने पर सूजन और लाली है"],
    "fatigue": ["शरीर में बहुत ज्यादा कमजोरी और थकान है", "बिस्तर से उठने की भी ताकत नहीं बची है", "पूरा शरीर टूट रहा है और सुस्ती है"],
    "nausea": ["जी बहुत मिचला रहा है और घबराहट हो रही है", "कुछ भी खाने की महक से जी मतलाता है", "पेट में भारीपन और उल्टी जैसा लग रहा है"]
}

PHRASES_EN = {
    "abdominal_pain": ["I have severe cramping pain in my lower abdomen", "My stomach aches severely after meals", "Sharp abdominal tenderness on the right side"],
    "fever": ["I am running a high body temperature with severe chills", "Spiking fevers reaching 102 degrees since last night", "Feeling very feverish and shivering constantly"],
    "headache": ["Throbbing headache around my temples and eyes", "Splitting headache that is not responding to paracetamol", "Severe tension across my forehead and head"],
    "chest_pain": ["Crushing retrosternal chest pain", "Severe tightness in the chest extending outward", "Constant heavy pressure across my chest wall"],
    "breathlessness": ["Shortness of breath even when resting in bed", "Gasping for air and unable to breathe comfortably", "Severe dyspnea and wheezing when inhaling"],
    "vomiting": ["Vomiting multiple times today and cannot keep fluids down", "Violent nausea leading to repeated emesis", "Episodes of forceful vomiting"],
    "diarrhea": ["Frequent watery bowel movements for the last twenty four hours", "Loose stools with urgent cramps", "Severe diarrhea causing dehydration"],
    "dizziness": ["Feeling extremely lightheaded and unsteady on my feet", "Experiencing vertigo where the room is spinning", "Dizziness whenever I stand up abruptly"],
    "cough": ["Persistent hacking cough disrupting my sleep", "Productive cough producing thick yellow phlegm", "Continuous dry irritation in the lungs with cough"],
    "sore_throat": ["Severe burning pharyngitis making swallowing painful", "Scratchy and inflamed throat since yesterday", "Throat feels constricted and raw"],
    "burning_urination": ["Excruciating burning during micturition", "Dysuria and painful urination throughout the day", "Severe scalding sensation when passing urine"],
    "numbness": ["Paresthesia and loss of sensation in left fingertips", "Numbness extending along the forearm", "Tingling sensation and weakness in toes"],
    "joint_pain": ["Severe arthralgia and stiffness in both knee joints", "Aching pain in multiple joints especially ankles", "Inflammatory pain across hand and wrist joints"],
    "swelling": ["Marked peripheral edema in both lower legs and feet", "Swelling around the face and periorbital area", "Puffy swollen ankles causing shoe tightness"],
    "fatigue": ["Overwhelming exhaustion and muscle lethargy", "Severe malaise and utter lack of energy to walk", "Feeling completely worn out and drained"],
    "nausea": ["Persistent sickening sensation in the stomach", "Severe queasiness preventing me from looking at food", "Continuous nausea throughout the afternoon"]
}

PHRASES_ROMAN_MR = {
    "abdominal_pain": ["Majha pot khup dukhat ahe", "Pota madhe achanak teevra kal yet ahe", "Potat khup ghadbad ani vedna ahe"],
    "fever": ["Kharach khup tap chadla ahe angaat", "Kal pasun khup bhari tap ahe", "Anga taptay tapane"],
    "headache": ["Doke phutlya sarkhe dukhayla lagle ahe", "Mala khup teevra dokedukhi hot ahe", "Kapaal khup thanktay"],
    "chest_pain": ["Chhati madhe dava baju khup dab yet ahe", "Chhatit teevra vedna ahet", "Chhati gachch zali ahe"],
    "breathlessness": ["Shwas ghyayla khup tras hoto ahe", "Dam lagto ahe thoda challe tari", "Shwas purna gheta yet nahiye"],
    "vomiting": ["Sakal pasun teen vela ulti zali", "Kahi khal ki lagech ulti yete", "Khup pitta chi ulti hot ahe"],
    "diarrhea": ["Khup patal julab suru ahet", "Panyasarkhi sandas hot ahe", "Julab thambayche nav ghet nahit"],
    "dizziness": ["Dolyansamor andhari yeun chakkar yete", "Doke gar gar firat ahe", "Ubhe rahile ki chakkar yet ahe"],
    "cough": ["Khup korda khokla yet ahe", "Khoklun khoklun chhati dukhtey", "Kaphacha khokla tras detoy"],
    "sore_throat": ["Ghashat khav khav ani vedna ahe", "Ghashat ghaslya sarkhe dukhtey", "Ghaltana khup tras hoto"],
    "burning_urination": ["Laghvi kartana khup jaljal hot ahe", "Laghvit aag hot ahe", "Laghvila themb themb tras hoto"],
    "numbness": ["Dava hatala mungya yet ahet ani sunna zala", "Paya chi bote badhir zali ahet", "Hatavar cha sparsh kalat nahi"],
    "joint_pain": ["Gudghe ani sandhe khup dukhtat", "Sandhyanmadhe khup jakadlepan ahe", "Chaltana sandhe dukhun yetat"],
    "swelling": ["Paya var khup sooj aali ahe", "Chehryavar ani dolyansamor sooj ahe", "Ghotyala sooj chhadli ahe"],
    "fatigue": ["Angat kahihi taqat urleli nahi", "Khup ashaktpana ahe", "Thakun purna galun gelo ahe"],
    "nausea": ["Sarva vel malmallya sarkhe hot ahe", "Potat ghabar ghabar hotey ani malmal ahe", "Kahihi khaychi iccha nahi malmal muly"]
}

PHRASES_HINGLISH = {
    "abdominal_pain": ["Pet me bahut heavy pain ho raha hai", "Stomach me cramp aur severe pain hai", "Lower pet me achanak dard shuru hua"],
    "fever": ["Bahut high fever hai body me chills ke sath", "Kal rat se temperature down nahi ho raha", "Poori body fever se tap rahi hai"],
    "headache": ["Sir me bahut sharp headache ho raha hai", "Headache itna tez hai ki aankhein nahi khul rahi", "Sir bilkul phat raha hai"],
    "chest_pain": ["Chest me left side bahut tightness feel ho rahi hai", "Chest pain ho raha hai aur heavy lag raha hai", "Chhati me severe pain hai"],
    "breathlessness": ["Breathing problem ho rahi hai deeply saans nahi le pa raha", "Thoda chalte hi saans phool rahi hai", "Shortness of breath bahut jyada hai"],
    "vomiting": ["Subah se loose motions aur vomiting ho rahi hai", "Kuchh bhi digest nahi ho raha vomit ho jata hai", "Frequent vomiting se dehydration ho raha hai"],
    "diarrhea": ["Bahut watery loose motions ho rahe hain", "Loose motion ruk hi nahi rahe kal se", "Pet me loose motion ki wajah se weakness aa gayi"],
    "dizziness": ["Khade hote hi chakkar aa raha hai dizzy feel ho raha", "Aankhon ke aage andhera aa raha hai dizziness hai", "Head spinning ho raha hai"],
    "cough": ["Continuous cough hai chest me congestion ke sath", "Dry cough itna hai ki throat pain ho gaya", "Coughing bouts aa rahe hain"],
    "sore_throat": ["Throat me severe pain aur swallowing me difficulty hai", "Gala poora kharab hai sore throat feel ho raha", "Throat me burning sensation hai"],
    "burning_urination": ["Urine pass karte waqt bahut burning sensation ho rahi hai", "Peshap me severe burning hai", "Urination ke time irritation aur jalan hai"],
    "numbness": ["Left arm me numbness aur tingling sensation ho rahi hai", "Haath bilkul numb ho gaya hai feel nahi ho raha", "Fingers me loss of sensation hai"],
    "joint_pain": ["Knee joints me bahut severe joint pain hai", "Joints me stiffness aur swelling ke sath pain hai", "Saare joints me pain ho raha hai"],
    "swelling": ["Feet aur ankles par visible swelling aa gayi hai", "Legs me severe edema aur swelling hai", "Face par subah se swelling dikh rahi hai"],
    "fatigue": ["Extreme fatigue aur weakness feel ho rahi hai", "Bina kuch kiye body me exhaustion hai", "Poori tarah drained out feel ho raha hai"],
    "nausea": ["Continuous nausea feel ho raha hai vomiting aane wali hai", "Food smell se bhi nausea aur ghabrahat ho rahi hai", "Stomach me nauseous feeling hai"]
}

# Negation Templates per language
NEG_PHRASES = {
    "mr": [
        ("ताप अजिबात नाही", "fever"),
        ("छातीत काहीही दुखत नाही", "chest_pain"),
        ("उलट्यांचा त्रास अजिबात नाही", "vomiting"),
        ("खोकला नाहीये", "cough"),
        ("डोकेदुखी नाही", "headache"),
        ("पोट दुखत नाही", "abdominal_pain"),
        ("श्वासाला त्रास नाही", "breathlessness")
    ],
    "hi": [
        ("बुखार बिल्कुल नहीं है", "fever"),
        ("सीने में कोई दर्द नहीं है", "chest_pain"),
        ("उल्टी नहीं हो रही है", "vomiting"),
        ("खांसी नहीं है", "cough"),
        ("सिर में कोई दर्द नहीं है", "headache"),
        ("पेट में दर्द नहीं है", "abdominal_pain"),
        ("सांस लेने में कोई दिक्कत नहीं है", "breathlessness")
    ],
    "en": [
        ("no fever or chills present", "fever"),
        ("denies any chest pain", "chest_pain"),
        ("no nausea or vomiting", "vomiting"),
        ("cough is absent", "cough"),
        ("no headache reported", "headache"),
        ("no abdominal tenderness", "abdominal_pain"),
        ("no shortness of breath", "breathlessness")
    ],
    "roman-mr": [
        ("tap ajibat nahiye", "fever"),
        ("chhati dukhat nahiye", "chest_pain"),
        ("ulti cha tras nahiye", "vomiting"),
        ("khokla nahi ahe", "cough"),
        ("doke dukhat nahi", "headache"),
        ("potat kahi dukhat nahi", "abdominal_pain"),
        ("shwasala tras nahi", "breathlessness")
    ],
    "hinglish": [
        ("fever bilkul nahi hai", "fever"),
        ("chest me koi pain nahi hai", "chest_pain"),
        ("vomiting nahi ho rahi hai", "vomiting"),
        ("coughing nahi hai", "cough"),
        ("headache absent hai", "headache"),
        ("pet me dard nahi hai", "abdominal_pain"),
        ("breathing me koi issue nahi hai", "breathlessness")
    ]
}

# Distractor contexts
DISTRACTORS = {
    "mr": ["काल बाजारात गेलो होतो तेव्हापासून", "ऑफिसमधून घरी आल्यावर", "सकाळी चहा प्यायल्यानंतर", "दुपारी जेवण झाल्यावर"],
    "hi": ["कल बाजार गया था तब से", "ऑफिस से लौटने के बाद", "सुबह चाय पीने के बाद", "दोपहर के खाने के बाद"],
    "en": ["Started after coming back from market", "Noticed after arriving home from work", "Began after drinking tea this morning", "Occurring after lunch"],
    "roman-mr": ["Kal bazarat gelo hoto tevhasun", "Officemadhun ghari alyavar", "Sakali chaha pyalyanantar", "Dupari jevan zalyanantar"],
    "hinglish": ["Kal market gaya tha tab se", "Office se ghar aane ke baad", "Morning tea lene ke baad", "Lunch karne ke baad"]
}


def load_benchmark_sentences() -> List[str]:
    if not BENCHMARK_PATH.exists():
        return []
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [d["text"].strip().lower() for d in data]


def calculate_token_overlap(s1: str, s2: str) -> float:
    t1 = set(re.findall(r"\w+", s1.lower()))
    t2 = set(re.findall(r"\w+", s2.lower()))
    if not t1 or not t2:
        return 0.0
    return len(t1 & t2) / max(len(t1), len(t2))


def generate_dataset():
    benchmark_texts = load_benchmark_sentences()
    samples: List[Dict[str, Any]] = []
    sample_id = 1

    lang_phrases = {
        "mr": PHRASES_MR,
        "hi": PHRASES_HI,
        "en": PHRASES_EN,
        "roman-mr": PHRASES_ROMAN_MR,
        "hinglish": PHRASES_HINGLISH
    }

    # 1. Single Symptom Sentences (with distractors)
    for lang, phrases_map in lang_phrases.items():
        dist_list = DISTRACTORS[lang]
        for sym, phrase_list in phrases_map.items():
            for p in phrase_list:
                dist = random.choice(dist_list)
                text = f"{dist}, {p}" if random.random() > 0.5 else f"{p} ({dist.lower()})"
                samples.append({
                    "id": f"ann_v2_{sample_id:04d}",
                    "language": lang,
                    "text": text,
                    "symptoms": [sym],
                    "negated_symptoms": [],
                    "symptom_count": 1
                })
                sample_id += 1

    # 2. Multi-Symptom Combos
    for lang, phrases_map in lang_phrases.items():
        syms_available = list(phrases_map.keys())
        for _ in range(65):
            selected_syms = random.sample(syms_available, k=random.choice([2, 3]))
            chosen_phrases = [random.choice(phrases_map[s]) for s in selected_syms]
            connector = " आणि " if lang in ["mr", "roman-mr"] else (" और " if lang in ["hi", "hinglish"] else " and also ")
            text = connector.join(chosen_phrases)
            samples.append({
                "id": f"ann_v2_{sample_id:04d}",
                "language": lang,
                "text": text,
                "symptoms": selected_syms,
                "negated_symptoms": [],
                "symptom_count": len(selected_syms)
            })
            sample_id += 1

    # 3. Explicit Negations
    for lang, phrases_map in lang_phrases.items():
        syms_available = list(phrases_map.keys())
        neg_pairs = NEG_PHRASES[lang]
        for _ in range(40):
            pos_sym = random.choice(syms_available)
            pos_phrase = random.choice(phrases_map[pos_sym])
            neg_phrase, neg_sym = random.choice(neg_pairs)
            if pos_sym == neg_sym:
                continue

            connector = " पण " if lang == "mr" else (" लेकिन " if lang == "hi" else (" but " if lang == "en" else (" pan " if lang == "roman-mr" else " but ")))
            text = f"{pos_phrase}{connector}{neg_phrase}"
            samples.append({
                "id": f"ann_v2_{sample_id:04d}",
                "language": lang,
                "text": text,
                "symptoms": [pos_sym],
                "negated_symptoms": [neg_sym],
                "symptom_count": 1
            })
            sample_id += 1

    # 4. Leakage Verification against Benchmark
    cleaned_samples = []
    leakage_count = 0
    for s in samples:
        s_text = s["text"].strip().lower()
        is_leaked = False
        for b_text in benchmark_texts:
            if s_text == b_text or calculate_token_overlap(s_text, b_text) > 0.75:
                is_leaked = True
                leakage_count += 1
                break
        if not is_leaked:
            cleaned_samples.append(s)

    # 5. Automated Label Consistency Check
    validated_samples = []
    for s in cleaned_samples:
        # Check: positive symptoms should not intersect with negated symptoms
        overlap = set(s["symptoms"]) & set(s["negated_symptoms"])
        if not overlap and len(s["symptoms"]) > 0:
            validated_samples.append(s)

    # Shuffle
    random.shuffle(validated_samples)

    total_len = len(validated_samples)
    train_end = int(total_len * 0.70)
    val_end = int(total_len * 0.85)

    train_data = validated_samples[:train_end]
    val_data = validated_samples[train_end:val_end]
    test_data = validated_samples[val_end:]

    # Write splits
    for split_name, data in [("train", train_data), ("validation", val_data), ("test", test_data)]:
        with open(OUTPUT_DIR / f"{split_name}.jsonl", "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    metadata = {
        "dataset_name": "mahaarogya_multilingual_annotations_v2",
        "total_rows": total_len,
        "train_rows": len(train_data),
        "val_rows": len(val_data),
        "test_rows": len(test_data),
        "languages": {l: sum(1 for s in validated_samples if s["language"] == l) for l in ["mr", "hi", "en", "roman-mr", "hinglish"]},
        "symptom_coverage": {s: sum(1 for row in validated_samples if s in row["symptoms"]) for s in SYMPTOM_NAMES},
        "negated_coverage": {s: sum(1 for row in validated_samples if s in row["negated_symptoms"]) for s in SYMPTOM_NAMES},
        "leakage_filtered_out": leakage_count,
        "seed": SEED
    }

    with open(OUTPUT_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("============================================================================")
    print(" MULTILINGUAL EXTRACTION DATASET V2 GENERATION COMPLETE")
    print("============================================================================")
    print(f"Total Validated Rows: {metadata['total_rows']}")
    print(f"  • Train:      {len(train_data)} rows ({len(train_data)/total_len*100:.1f}%)")
    print(f"  • Validation: {len(val_data)} rows ({len(val_data)/total_len*100:.1f}%)")
    print(f"  • Test:       {len(test_data)} rows ({len(test_data)/total_len*100:.1f}%)")
    print(f"Leakage Filtered Out: {metadata['leakage_filtered_out']} (0 benchmark overlap)")
    print(f"\nLanguage Distribution:\n{json.dumps(metadata['languages'], indent=2)}")
    print(f"\nSymptom Coverage (Positive Occurrences):\n{json.dumps(metadata['symptom_coverage'], indent=2)}")
    print(f"\nNegation Coverage:\n{json.dumps(metadata['negated_coverage'], indent=2)}")


if __name__ == "__main__":
    generate_dataset()
