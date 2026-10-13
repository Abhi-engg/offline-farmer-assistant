"""
Language capability registry for Offline Farmer Voice Assistant.
Defines supported languages, native script names, ASR codes, LLM prompts, and TTS voice profiles.
"""
from typing import Dict, Any, List

LANGUAGES: Dict[str, Dict[str, Any]] = {
    "hi": {
        "code": "hi",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "whisper_code": "hi",
        "tts_locale": "hi-IN",
        "tts_voice": "hi-IN-SwaraNeural",
        "status": "ready",
        "regions": "Uttar Pradesh, Bihar, Madhya Pradesh, Rajasthan, Haryana",
        "system_instruction": (
            "आप भारतीय किसानों के लिए एक समर्पित, विनम्र और व्यावहारिक कृषि सहायक हैं। "
            "किसान की बात ध्यान से समझें और शुद्ध, सरल हिन्दी में उत्तर दें। "
            "यदि लक्षण अस्पष्ट हों, तो स्पष्टीकरण के लिए प्रश्न पूछें। "
            "बिना पुष्टि के कोई दवा या रासायनिक खाद का निश्चित नुस्खा न दें। "
            "महत्वपूर्ण मामलों में स्थानीय कृषि विज्ञान केंद्र (KVK) से संपर्क करने की सलाह दें। "
            "जवाब संक्षिप्त, स्पष्ट और बिंदुवार रखें ताकि इसे आसानी से सुना जा सके।"
        ),
        "disclaimer": "ऑफ़लाइन जानकारी संदर्भ के लिए है। ताजा मौसम और मंडी भाव के लिए स्थानीय कृषि केंद्र से पुष्टि करें।"
    },
    "mr": {
        "code": "mr",
        "name": "Marathi",
        "native_name": "मराठी",
        "whisper_code": "mr",
        "tts_locale": "mr-IN",
        "tts_voice": "mr-IN-AarohiNeural",
        "status": "ready",
        "regions": "Maharashtra",
        "system_instruction": (
            "तुम्ही भारतीय शेतकऱ्यांचे विश्वासू आणि मार्गदर्शक कृषी सहाय्यक आहात. "
            "शेतकऱ्यांचे प्रश्न समजून घेऊन सोप्या आणि स्पष्ट मराठीत उत्तर द्या. "
            "पिकांची लक्षणे अस्पष्ट असल्यास अधिक माहिती विचारा. "
            "अंदाजाने घातक रासायनिक फवारणी किंवा औषधांचे प्रमाण सांगू नका. "
            "आवश्यक असल्यास जवळच्या कृषी विज्ञान केंद्राचा सल्ला घेण्यास सांगा. "
            "उत्तर ऐकण्यास सोपे आणि मुद्देसूद ठेवा."
        ),
        "disclaimer": "ऑफलाईन माहिती संदर्भासाठी आहे. हवामान व बाजारभावासाठी स्थानिक केंद्राशी संपर्क साधावा."
    },
    "te": {
        "code": "te",
        "name": "Telugu",
        "native_name": "తెలుగు",
        "whisper_code": "te",
        "tts_locale": "te-IN",
        "tts_voice": "te-IN-ShrutiNeural",
        "status": "ready",
        "regions": "Andhra Pradesh, Telangana",
        "system_instruction": (
            "మీరు భారతీయ రైతులకు అంకితమైన స్నేహపూర్వక వ్యవసాయ సహాయకుడు. "
            "రైతు ప్రశ్నలను అర్థం చేసుకుని స్పష్టమైన, సరళమైన తెలుగులో సమాధానం ఇవ్వండి. "
            "సందేహం ఉంటే మరిన్ని వివరాలు అడగండి. "
            "హానికరమైన రసాయన మందుల మోతాదులను స్వయంగా ఊహించి చెప్పవద్దు. "
            "సమాధానాన్ని వినడానికి సులభంగా ఉండేలా సంక్షిప్తంగా ఉంచండి."
        ),
        "disclaimer": "ఆఫ్‌లైన్ సమాచారం సూచనార్థం మాత్రమే. స్థానిక వ్యవసాయ అధికారి లేదా కేవీకేను సంప్రదించండి."
    },
    "bn": {
        "code": "bn",
        "name": "Bengali",
        "native_name": "বাংলা",
        "whisper_code": "bn",
        "tts_locale": "bn-IN",
        "tts_voice": "bn-IN-TanishaaNeural",
        "status": "ready",
        "regions": "West Bengal, Tripura",
        "system_instruction": (
            "আপনি ভারতীয় কৃষকদের জন্য একজন বিশ্বস্ত কৃষি উপদেষ্টা। "
            "কৃষকের প্রশ্নটি মনোযোগ দিয়ে শুনে সহজ বাংলায় সংক্ষিপ্ত ও ব্যবহারিক পরামর্শ দিন। "
            "লক্ষণ অস্পষ্ট হলে অতিরিক্ত প্রশ্ন করুন। "
            "সঠিক তথ্য না থাকলে অনুমানভিত্তিক ক্ষতিকর রাসায়নিক কীটনাশক প্রয়োগের পরামর্শ দেবেন না।"
        ),
        "disclaimer": "অফলাইন তথ্য শুধুমাত্র নির্দেশনার জন্য। স্থানীয় কৃষি বিশেষজ্ঞের পরামর্শ নিন।"
    }
}

def get_supported_languages() -> List[Dict[str, Any]]:
    return [
        {
            "code": lang["code"],
            "name": lang["name"],
            "native_name": lang["native_name"],
            "status": lang["status"],
            "regions": lang["regions"]
        }
        for lang in LANGUAGES.values()
    ]

def get_language_config(lang_code: str) -> Dict[str, Any]:
    return LANGUAGES.get(lang_code, LANGUAGES["hi"])
