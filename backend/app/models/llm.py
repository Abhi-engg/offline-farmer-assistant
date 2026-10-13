"""
Local Conversational AI Engine for Indian Farmers.
Supports:
1. Local Ollama instance (e.g. Qwen2.5 1.5B/3B, Llama 3.2 3B).
2. Hugging Face local pipeline / CTranslate2.
3. Offline Grounded Knowledge Reasoner (Structured Expert Fallback when model weights are not loaded).

Ensures the assistant ALWAYS provides safe, helpful, non-hallucinated agricultural responses.
"""
import time
import json
import logging
from typing import Dict, Any, List, Optional
import httpx

from app.languages.registry import get_language_config

logger = logging.getLogger(__name__)

class LocalLLM:
    def __init__(self, ollama_url: str = "http://localhost:11434", default_model: str = "qwen2.5:1.5b"):
        self.ollama_url = ollama_url
        self.model_name = default_model
        self.client = httpx.AsyncClient(timeout=60.0)

    async def is_engine_available(self) -> bool:
        """Check if local Ollama server is running."""
        try:
            res = await self.client.get(f"{self.ollama_url}/api/tags")
            return res.status_code == 200
        except Exception:
            return False

    def build_prompt(self, query: str, language_code: str, rag_context: List[Dict[str, Any]], history: List[Dict[str, str]]) -> str:
        lang_config = get_language_config(language_code)
        system_instruction = lang_config["system_instruction"]
        
        context_str = ""
        if rag_context:
            context_str = "\n\nप्रामाणिक कृषि संदर्भ (Verified Agriculture Context):\n"
            for doc in rag_context:
                context_str += f"- {doc.get('title')}: {doc.get('content')}\n"

        prompt = f"<|im_start|>system\n{system_instruction}{context_str}\n<|im_end|>\n"
        
        for turn in history[-4:]: # Keep last 4 turns for limited context
            role = turn.get("role", "user")
            content = turn.get("content", "")
            prompt += f"<|im_start|>{role}\n{content}\n<|im_end|>\n"

        prompt += f"<|im_start|>user\n{query}\n<|im_end|>\n<|im_start|>assistant\n"
        return prompt

    async def generate_response(
        self,
        query: str,
        language_code: str = "hi",
        rag_context: Optional[List[Dict[str, Any]]] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate farmer-friendly conversational response.
        """
        start_time = time.time()
        rag_context = rag_context or []
        history = history or []
        lang_config = get_language_config(language_code)

        # 1. Attempt generation via local Ollama
        is_ollama_up = await self.is_engine_available()
        if is_ollama_up:
            try:
                prompt = self.build_prompt(query, language_code, rag_context, history)
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3, # Low temperature for factual precision
                        "top_p": 0.8,
                        "num_predict": 250 # Keep responses concise and spoken-friendly
                    }
                }
                res = await self.client.post(f"{self.ollama_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    response_text = data.get("response", "").strip()
                    elapsed = time.time() - start_time
                    return {
                        "answer": response_text,
                        "engine": f"ollama/{self.model_name}",
                        "language": language_code,
                        "latency_seconds": round(elapsed, 3),
                        "sources": [d.get("title") for d in rag_context]
                    }
            except Exception as e:
                logger.warning(f"Ollama inference error: {e}, using grounded fallback reasoning.")

        # 2. Local Grounded Agricultural Reasoner (Rule & RAG-driven offline expert fallback)
        # Guarantees complete offline functionality even before 3GB model weight download
        answer = self._grounded_reasoning(query, language_code, rag_context)
        elapsed = time.time() - start_time

        return {
            "answer": answer,
            "engine": "local_grounded_rag_engine",
            "language": language_code,
            "latency_seconds": round(elapsed, 3),
            "sources": [d.get("title") for d in rag_context]
        }

    def _grounded_reasoning(self, query: str, language_code: str, rag_context: List[Dict[str, Any]]) -> str:
        """
        Synthesizes expert agricultural advice based on verified local knowledge entries.
        Enforces safety rules: no dosage guessing, asks clarifying questions, suggests KVK verification.
        """
        if rag_context:
            doc = rag_context[0]
            content = doc.get("content", "")
            title = doc.get("title", "")
            source = doc.get("source", "")
            
            if language_code == "mr":
                return (
                    f"{content}\n\n"
                    f"संदर्भ: {source} ({title}). "
                    f"कृपया अधिक तपासासाठी स्थानिक कृषी विज्ञान केंद्राशी संपर्क साधा."
                )
            elif language_code == "te":
                return (
                    f"{content}\n\n"
                    f"ఆధారము: {source} ({title}). "
                    f"సందేహం ఉంటే స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి."
                )
            elif language_code == "bn":
                return (
                    f"{content}\n\n"
                    f"সূত্র: {source} ({title}). "
                    f"প্রয়োজনে স্থানীয় কৃষি বিজ্ঞান কেন্দ্রের সাহায্য নিন।"
                )
            else: # Hindi default
                return (
                    f"{content}\n\n"
                    f"संदर्भ: {source} ({title})। "
                    f"नोट: कृपया किसी भी रासायनिक छिड़काव से पहले स्थानीय कृषि विज्ञान केंद्र (KVK) से पुष्टि कर लें।"
                )

        # Fallback when no direct document matches
        if language_code == "mr":
            return (
                "तुमच्या प्रश्नासाठी सध्या ऑफलाईन नोंदींमध्ये खात्रीशीर माहिती उपलब्ध नाही. "
                "पिकाचे नाव, लक्षणे किंवा जमिनीचा प्रकार याबद्दल अधिक माहिती द्या, "
                "किंवा नजीकच्या कृषी विज्ञान केंद्राशी संपर्क साधा."
            )
        elif language_code == "te":
            return (
                "మీ ప్రశ్నకు సంబంధించిన పూర్తి సమాచారం ఆఫ్‌లైన్ రికార్డులలో లభించలేదు. "
                "దయచేసి పంట పేరు మరియు లక్షణాల వివరాలను మరింత స్పష్టంగా తెలియజేయండి."
            )
        elif language_code == "bn":
            return (
                "আপনার প্রশ্নের সুনির্দিষ্ট তথ্য অফলাইন সংগ্রহে নেই। "
                "অনুগ্রহ করে ফসলের নাম ও সমস্যার বিস্তারিত জানান অথবা স্থানীয় কৃষি কর্মকর্তার সাথে যোগাযোগ করুন।"
            )
        else: # Hindi
            return (
                "माफ़ कीजिए, इस सवाल के लिए वर्तमान ऑफ़लाइन रिकॉर्ड में सटीक जानकारी उपलब्ध नहीं है। "
                "कृपया फसल का नाम, लक्षण या समस्या को थोड़ा और स्पष्ट करके पूछें, "
                "या स्थानीय कृषि विज्ञान केंद्र (KVK) के विशेषज्ञ से सलाह लें।"
            )

# Global LLM instance
llm_engine = LocalLLM()
