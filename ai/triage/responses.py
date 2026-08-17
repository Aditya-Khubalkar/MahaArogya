"""
MahaArogya — User-Facing Safe Response Templates
Localized response templates for ROUTINE, PRIORITY, URGENT, and EMERGENCY triage states.
Ensures the UI never overstates diagnosis certainty and clearly provides emergency instructions.
"""

RESPONSES_BY_CATEGORY = {
    "EMERGENCY": {
        "mr": "🚨 **तातडीची वैद्यकीय मदत आवश्यक:** आपण दिलेल्या माहितीनुसार तातडीने वैद्यकीय तपासणी आवश्यक आहे. कृपया जवळच्या रुग्णालय आपत्कालीन विभागात जा किंवा १०८ रुग्णवाहिकेला कॉल करा.",
        "hi": "🚨 **आपातकालीन चिकित्सा आवश्यक:** आपकी दी गई जानकारी के अनुसार तुरंत डॉक्टर की सलाह आवश्यक है। कृपया नजदीकी अस्पताल के इमरजेंसी में जाएं या १०८ एम्बुलेंस को कॉल करें।",
        "en": "🚨 **EMERGENCY MEDICAL ASSESSMENT REQUIRED:** Based on the symptoms described, urgent emergency evaluation is required. Please proceed to the nearest Emergency Department immediately or call emergency ambulance (108).",
        "roman-mr": "🚨 **EMERGENCY MEDICAL HELP NEEDED:** Tumhi dilelya mahitinusar tabadtob emergency doctor chi garaj ahe. Krupaya javalchya hospital emergency madhe ja kiva 108 ambulance la call kara.",
        "hinglish": "🚨 **EMERGENCY MEDICAL CARE REQUIRED:** Aapki di gayi jankari ke according immediately emergency doctor evaluation zaroori hai. Kripya nearest hospital emergency jaye ya 108 ambulance call karein."
    },
    "URGENT": {
        "mr": "⚠️ **लवकर वैद्यकीय तपासणीची गरज:** आपल्या लक्षणांनुसार लवकरात लवकर डॉक्टरांचा सल्ला घेणे आवश्यक आहे. आम्ही आपल्याला जवळच्या रुग्णालयात ओपीडी टोकन मिळवून देऊ शकतो.",
        "hi": "⚠️ **शीघ्र डॉक्टर की सलाह आवश्यक:** आपके लक्षणों के आधार पर जल्द से जल्द डॉक्टर से परामर्श लेना उचित होगा। हम आपको नजदीकी अस्पताल में OPD स्लॉट दिलाने में मदद कर सकते हैं।",
        "en": "⚠️ **URGENT EVALUATION RECOMMENDED:** Your symptoms suggest a prompt medical evaluation is recommended. We can assist you in finding a suitable OPD slot today.",
        "roman-mr": "⚠️ **URGENT EVALUATION NEEDED:** Aaplya lakshananusar lavkarat lavkar doctor cha salla ghyava. Aamhi javalchya hospital madhe slot milvun deu shakto.",
        "hinglish": "⚠️ **URGENT DOCTOR ADVICE NEEDED:** Aapke symptoms ke according jaldi doctor consult karna advisable hai. Hum aapko nearby hospital me OPD slot book karne me help kar sakte hain."
    },
    "PRIORITY": {
        "mr": "ℹ️ **प्राधान्य क्रमाने तपासणी:** हे लक्षण सामान्य तपासणीसाठी योग्य वाटत आहे. आम्ही आपणास आजच्या सुयोग्य ओपीडी वेळेचे नियोजन करून देऊ शकतो.",
        "hi": "ℹ️ **प्राथमिकता परामर्श:** यह स्थिति सामान्य डॉक्टर जांच के लिए उपयुक्त प्रतीत होती है। हम आपके लिए आज का उपयुक्त OPD स्लॉट बुक कर सकते हैं।",
        "en": "ℹ️ **PRIORITY OPD CONSULTATION:** Your symptoms appear suitable for routine priority evaluation. We can help you schedule an OPD appointment.",
        "roman-mr": "ℹ️ **PRIORITY CONSULTATION:** He lakshan routine doctor checkup sathi yogya vatate. Aamhi aajcha OPD slot schedule karu shakto.",
        "hinglish": "ℹ️ **PRIORITY CONSULTATION:** Ye symptoms routine doctor checkup ke liye suitable hain. Hum aapke liye OPD slot schedule kar sakte hain."
    },
    "ROUTINE": {
        "mr": "✅ **नियमित ओपीडी सल्ला:** हे लक्षण नियमित वैद्यकीय तपासणीसाठी योग्य आहे. सोयीस्कर ओपीडी स्लॉट निवडण्यासाठी खालील पर्याय पहा.",
        "hi": "✅ **सामान्य OPD सलाह:** यह स्थिति नियमित डॉक्टर जांच के लिए उपयुक्त है। सुविधाजनक OPD स्लॉट चुनने के लिए नीचे दिए गए विकल्प देखें।",
        "en": "✅ **ROUTINE OPD EVALUATION:** This appears suitable for routine medical evaluation. We can help you find an appropriate OPD slot.",
        "roman-mr": "✅ **ROUTINE OPD CONSULTATION:** He lakshan regular doctor consultation sathi yogya ahe. Convenient OPD slot saathi khalil option paha.",
        "hinglish": "✅ **ROUTINE OPD CONSULTATION:** Ye symptoms routine medical checkup ke liye suitable hain. Convenient OPD slot chunne ke liye options dekhein."
    }
}


def get_safe_response(triage_category: str, language: str = "mr") -> str:
    """Returns safe, localized response text for the given triage category."""
    cat_dict = RESPONSES_BY_CATEGORY.get(triage_category, RESPONSES_BY_CATEGORY["ROUTINE"])
    return cat_dict.get(language, cat_dict["en"])
