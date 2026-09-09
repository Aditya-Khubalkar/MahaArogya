import json
import random
import os

languages = ["en", "hi", "mr", "roman-mr", "hinglish"]

base_cases = [
    # English
    {"text": "oxygen is 88 and I cannot breathe", "lang": "en", "exp_symptoms": ["breathlessness"], "exp_vitals": {"spo2": 88}},
    {"text": "pulse is 140", "lang": "en", "exp_symptoms": [], "exp_vitals": {"heart_rate": 140}},
    {"text": "fever 103", "lang": "en", "exp_symptoms": ["fever"], "exp_vitals": {"temperature": 103}},
    {"text": "BP is 90/60 and dizzy", "lang": "en", "exp_symptoms": ["dizziness"], "exp_vitals": {"sys_bp": 90, "dia_bp": 60}},
    {"text": "I am having a stroke, facial droop", "lang": "en", "exp_symptoms": ["stroke_symptoms"], "exp_vitals": {}},
    {"text": "heart attack symptoms, chest crushing pain", "lang": "en", "exp_symptoms": ["cardiac_emergency", "chest_pain"], "exp_vitals": {}},
    {"text": "unconscious and pale", "lang": "en", "exp_symptoms": ["altered_consciousness"], "exp_vitals": {}},
    {"text": "severe bleeding from arm", "lang": "en", "exp_symptoms": ["severe_bleeding"], "exp_vitals": {}},
    {"text": "no fever, no headache", "lang": "en", "exp_symptoms": [], "exp_vitals": {}},
    {"text": "I don't have chest pain", "lang": "en", "exp_symptoms": [], "exp_vitals": {}},
    
    # Hindi
    {"text": "ऑक्सीजन 88 है और सांस लेने में तकलीफ", "lang": "hi", "exp_symptoms": ["breathlessness"], "exp_vitals": {"spo2": 88}},
    {"text": "मुझे लकवा मार गया है", "lang": "hi", "exp_symptoms": ["stroke_symptoms"], "exp_vitals": {}},
    {"text": "बुखार नहीं है", "lang": "hi", "exp_symptoms": [], "exp_vitals": {}},
    {"text": "खून बह रहा है", "lang": "hi", "exp_symptoms": ["severe_bleeding"], "exp_vitals": {}},
    {"text": "दिल का दौरा", "lang": "hi", "exp_symptoms": ["cardiac_emergency"], "exp_vitals": {}},
    {"text": "मरीज बेहोश है", "lang": "hi", "exp_symptoms": ["altered_consciousness"], "exp_vitals": {}},
    
    # Marathi
    {"text": "ऑक्सिजन 85 आहे आणि श्वास घ्यायला त्रास होतोय", "lang": "mr", "exp_symptoms": ["breathlessness"], "exp_vitals": {"spo2": 85}},
    {"text": "हृदयविकाराचा झटका", "lang": "mr", "exp_symptoms": ["cardiac_emergency"], "exp_vitals": {}},
    {"text": "तो बेशुद्ध पडला आहे", "lang": "mr", "exp_symptoms": ["altered_consciousness"], "exp_vitals": {}},
    {"text": "रक्तस्राव थांबत नाही", "lang": "mr", "exp_symptoms": ["severe_bleeding"], "exp_vitals": {}},
    {"text": "अर्धांगवायू झाला आहे", "lang": "mr", "exp_symptoms": ["stroke_symptoms"], "exp_vitals": {}},
    {"text": "ताप नाहीये", "lang": "mr", "exp_symptoms": [], "exp_vitals": {}},
    
    # Roman Marathi
    {"text": "oxygen 80 ahe ani shwas ghyayla tras hoto", "lang": "roman-mr", "exp_symptoms": ["breathlessness"], "exp_vitals": {"spo2": 80}},
    {"text": "toh beshuddha ahe", "lang": "roman-mr", "exp_symptoms": ["altered_consciousness"], "exp_vitals": {}},
    {"text": "hridayvikar", "lang": "roman-mr", "exp_symptoms": ["cardiac_emergency"], "exp_vitals": {}},
    {"text": "ardhangvayu", "lang": "roman-mr", "exp_symptoms": ["stroke_symptoms"], "exp_vitals": {}},
    {"text": "tap nahi", "lang": "roman-mr", "exp_symptoms": [], "exp_vitals": {}},
    
    # Hinglish
    {"text": "spo2 is 85 saans lene me dikkat", "lang": "hinglish", "exp_symptoms": ["breathlessness"], "exp_vitals": {"spo2": 85}},
    {"text": "heart attack aagaya shayad", "lang": "hinglish", "exp_symptoms": ["cardiac_emergency"], "exp_vitals": {}},
    {"text": "patient behosh hai", "lang": "hinglish", "exp_symptoms": ["altered_consciousness"], "exp_vitals": {}},
    {"text": "khoon beh raha hai", "lang": "hinglish", "exp_symptoms": ["severe_bleeding"], "exp_vitals": {}},
    {"text": "lakwa", "lang": "hinglish", "exp_symptoms": ["stroke_symptoms"], "exp_vitals": {}},
    {"text": "fever nahi hai", "lang": "hinglish", "exp_symptoms": [], "exp_vitals": {}}
]

# Generate variations to hit > 200 cases
expanded_cases = []
modifiers = [
    ("", ""),
    ("please help, ", ""),
    ("", ", what should I do?"),
    ("urgent: ", ""),
    ("doctor, ", "!")
]

def generate_cases():
    count = 0
    while count < 220:
        base = random.choice(base_cases)
        mod_start, mod_end = random.choice(modifiers)
        
        # Vary numeric vitals slightly for robustness testing
        text = base["text"]
        vitals = base["exp_vitals"].copy()
        
        if "88" in text:
            new_val = random.randint(70, 92)
            text = text.replace("88", str(new_val))
            vitals["spo2"] = new_val
        elif "85" in text:
            new_val = random.randint(70, 92)
            text = text.replace("85", str(new_val))
            vitals["spo2"] = new_val
        elif "80" in text:
            new_val = random.randint(70, 92)
            text = text.replace("80", str(new_val))
            vitals["spo2"] = new_val
        elif "140" in text:
            new_val = random.randint(120, 180)
            text = text.replace("140", str(new_val))
            vitals["heart_rate"] = new_val
        elif "103" in text:
            new_val = round(random.uniform(101.0, 105.0), 1)
            text = text.replace("103", str(new_val))
            vitals["temperature"] = new_val
        elif "90/60" in text:
            sys = random.randint(70, 95)
            dia = random.randint(40, 65)
            text = text.replace("90/60", f"{sys}/{dia}")
            vitals["sys_bp"] = sys
            vitals["dia_bp"] = dia
            
        full_text = f"{mod_start}{text}{mod_end}"
        
        expanded_cases.append({
            "text": full_text,
            "language": base["lang"],
            "expected_symptoms": base["exp_symptoms"],
            "expected_vitals": vitals
        })
        count += 1
        
generate_cases()

output_path = r"C:\MahaArogya\data\test\extraction_adversarial.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(expanded_cases, f, indent=4, ensure_ascii=False)
    
print(f"Generated {len(expanded_cases)} cases in {output_path}")
