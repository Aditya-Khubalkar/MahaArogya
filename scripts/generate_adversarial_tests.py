# -*- coding: utf-8 -*-
import json

tests = []

# 1. Emergency Red Flags (20 cases)
emergencies = [
    "I have severe chest pain and I am sweating and having difficulty breathing.",
    "My oxygen is 88 and I cannot breathe.",
    "Patient is unconscious and not responding.",
    "There is severe bleeding from my arm that won't stop.",
    "I have sudden weakness on one side of my body and slurred speech.",
    "I ate peanuts and now my throat is closing up and I can't breathe.",
    "My systolic BP is 70 and I feel dizzy.",
    "I am having a heart attack.",
    "I suddenly cannot move my left arm and my face is drooping.",
    "I am coughing up large amounts of blood.",
    "I took a lot of pills and want to sleep forever.", # suicide/overdose
    "My child is having a seizure for the past 10 minutes.",
    "Severe chest crushing pain radiating to my jaw.",
    "I can't breathe, SpO2 is 85%.",
    "Patient collapsed.",
    "I have severe abdominal pain and vomiting blood.",
    "Sudden thunderclap headache, worst of my life.",
    "I was in a high speed car crash and my neck hurts.",
    "I am having an allergic reaction, my lips are swollen and wheezing.",
    "Very high fever and stiff neck, confused."
]
for text in emergencies:
    tests.append({"category": "Emergency", "input": text, "expected_severity": "EMERGENCY"})

# 2. Urgent (20 cases)
urgents = [
    "I have a fever of 103 for the last 3 days.",
    "I have moderate breathing issues but SpO2 is 96.",
    "Severe back pain, no numbness.",
    "I cut my finger, it's bleeding but I wrapped it.",
    "I feel very dizzy when I stand up.",
    "I have been vomiting all day and can't keep water down.",
    "My asthma is acting up a bit, I used my inhaler.",
    "Severe stomach ache after eating spicy food.",
    "I have a kidney stone, the pain is 8 out of 10.",
    "I fell and think my arm is broken, it's swollen.",
    "I have a terrible migraine, I want to throw up.",
    "I have a really bad toothache that is keeping me awake.",
    "I stepped on a rusty nail.",
    "My blood pressure is 160 over 95 and I have a headache.",
    "I have a rash all over my body, it's very itchy.",
    "I have been having diarrhea for 2 days.",
    "I have a bad cough and feel very weak.",
    "My eye is very red and painful.",
    "I have a burn on my hand from the stove.",
    "I feel palpitations but no chest pain."
]
for text in urgents:
    tests.append({"category": "Urgent", "input": text, "expected_severity": "URGENT"})

# 3. Routine (20 cases)
routines = [
    "I have a mild cold and runny nose.",
    "I have a minor headache since morning.",
    "Just a routine consultation for my diabetes.",
    "I need a refill for my blood pressure medicine.",
    "I have a small scrape on my knee.",
    "I feel a bit tired today.",
    "I have mild lower back pain after lifting a box.",
    "I want to check my cholesterol levels.",
    "I have a slight sore throat.",
    "My knee aches when it rains.",
    "I have a mild rash on my arm.",
    "I need a doctor's note for work.",
    "I have a little bit of heartburn.",
    "I want to know if I should take vitamins.",
    "My hair is thinning.",
    "I have a mild stomach ache.",
    "I sneezed a few times today.",
    "I have a minor sunburn.",
    "I want to get a flu shot.",
    "I have a slight earache."
]
for text in routines:
    tests.append({"category": "Routine", "input": text, "expected_severity": "ROUTINE"})

# 4. Missing Information (20 cases)
missing = [
    "I don't feel good.",
    "Something is wrong.",
    "I need a doctor.",
    "Help me.",
    "I am sick.",
    "It hurts.",
    "My body aches.",
    "I'm not sure what's wrong.",
    "Can I see someone?",
    "I have a problem.",
    "Just feel off.",
    "I don't know.",
    "I have some pain.",
    "I need medical advice.",
    "I am unwell.",
    "Please help.",
    "I need to go to the hospital.",
    "I feel bad.",
    "Is a doctor available?",
    "I want a checkup."
]
for text in missing:
    # Expect safe fallback, likely ROUTINE or PRIORITY depending on extraction. 
    # But not EMERGENCY.
    tests.append({"category": "Missing", "input": text, "expected_severity": "NON_EMERGENCY"})

# 5. Multilingual (20 cases)
multilingual = [
    # Hindi
    ("मुझे बहुत तेज सीने में दर्द हो रहा है और पसीना आ रहा है।", "hi", "EMERGENCY"),
    ("मुझे हल्का बुखार है।", "hi", "ROUTINE"),
    ("मेरे पेट में बहुत तेज दर्द है।", "hi", "URGENT"),
    ("मुझे चक्कर आ रहा है।", "hi", "URGENT"),
    # Marathi
    ("माझ्या छातीत खूप दुखत आहे आणि मला घाम येत आहे.", "mr", "EMERGENCY"),
    ("मला थोडा खोकला आहे.", "mr", "ROUTINE"),
    ("माझे डोके खूप दुखत आहे.", "mr", "URGENT"),
    ("मला श्वास घ्यायला त्रास होत आहे.", "mr", "EMERGENCY"),
    # Roman Marathi
    ("majhya chhatit khup dukhat ahe ani gham yetoy.", "roman-mr", "EMERGENCY"),
    ("mala thoda khokla yetoy.", "roman-mr", "ROUTINE"),
    ("majhe doke khup dukhat ahe.", "roman-mr", "URGENT"),
    ("mala shwas ghyayla tras hoto ahe.", "roman-mr", "EMERGENCY"),
    # Hinglish
    ("mujhe chest pain ho raha hai aur breathing problem hai.", "hinglish", "EMERGENCY"),
    ("mujhe mild cold hai.", "hinglish", "ROUTINE"),
    ("mujhe severe back pain hai.", "hinglish", "URGENT"),
    ("mujhe ajeeb sa lag raha hai.", "hinglish", "NON_EMERGENCY"),
    # Extra
    ("I have fever and mala khokla yetoy", "hinglish", "URGENT"),
    ("SpO2 85 hai, can't breathe", "hinglish", "EMERGENCY"),
    ("Just a routine checkup ahe", "roman-mr", "ROUTINE"),
    ("Mujhe heart attack jaisa lag raha hai", "hi", "EMERGENCY")
]
for text, lang, exp in multilingual:
    tests.append({"category": "Multilingual", "input": text, "language": lang, "expected_severity": exp})

import os
os.makedirs(r"C:\MahaArogya\evaluation", exist_ok=True)
with open(r"C:\MahaArogya\evaluation\triage_adversarial_tests.json", "w", encoding="utf-8") as f:
    json.dump(tests, f, indent=4, ensure_ascii=False)
print(f"Generated {len(tests)} tests.")
