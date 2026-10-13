"""
Grounded Conversational AI Engine for Indian Farmers.
Follows a disciplined Two-Tier Architecture:
- Tier 1 (Primary): Intent Extraction + Slot Filling + Local Grounded RAG + Validated Templates.
  Zero hallucination, 100% deterministic, instant (<5ms) latency, sub-30MB footprint.
- Tier 2 (Optional Fallback): Local Small Language Model (SLM via Ollama / GGUF) for open-ended queries.
"""
import time
import json
import logging
from typing import Dict, Any, List, Optional
import httpx

from app.languages.registry import get_language_config
from app.services.intent_engine import intent_engine, IntentResult
from app.services.template_assembler import template_assembler

logger = logging.getLogger(__name__)

class LocalLLM:
    def __init__(self, ollama_url: str = "http://localhost:11434", default_model: str = "qwen2.5:1.5b", enable_slm_tier2: bool = False):
        self.ollama_url = ollama_url
        self.model_name = default_model
        self.enable_slm_tier2 = enable_slm_tier2
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
        
        for turn in history[-4:]:
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
        Generates farmer-friendly conversational response using Tier 1 Intent & Validated RAG Engine.
        Falls back to Tier 2 SLM only if explicitly enabled and query is unhandled.
        """
        start_time = time.time()
        rag_context = rag_context or []
        history = history or []

        # 1. Intent Extraction and Slot Filling
        intent_res: IntentResult = intent_engine.analyze(query)

        # 2. Tier 1: Grounded Validated Template Assembly (Zero Hallucination, Instant Latency)
        assembly_res = template_assembler.assemble(
            query=query,
            language_code=language_code,
            intent_res=intent_res,
            rag_context=rag_context
        )

        is_handled = assembly_res.get("is_handled", False)

        # 3. Tier 2: If Tier 1 cannot handle and SLM is enabled and Ollama is running
        if not is_handled and self.enable_slm_tier2:
            is_ollama_up = await self.is_engine_available()
            if is_ollama_up:
                try:
                    prompt = self.build_prompt(query, language_code, rag_context, history)
                    payload = {
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.2,
                            "top_p": 0.8,
                            "num_predict": 250
                        }
                    }
                    res = await self.client.post(f"{self.ollama_url}/api/generate", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        response_text = data.get("response", "").strip()
                        elapsed = time.time() - start_time
                        return {
                            "answer": response_text,
                            "engine": f"tier2_slm/{self.model_name}",
                            "intent": intent_res.intent,
                            "slots": intent_res.slots,
                            "is_handled": True,
                            "language": language_code,
                            "latency_seconds": round(elapsed, 3),
                            "sources": [d.get("title") for d in rag_context]
                        }
                except Exception as e:
                    logger.warning(f"Tier 2 SLM inference error: {e}")

        # Return Tier 1 result
        elapsed = time.time() - start_time
        return {
            "answer": assembly_res["answer"],
            "clarifying_question": assembly_res.get("clarifying_question"),
            "engine": "tier1_validated_intent_rag_engine",
            "intent": intent_res.intent,
            "slots": intent_res.slots,
            "is_handled": is_handled,
            "confidence": intent_res.confidence,
            "language": language_code,
            "latency_seconds": round(elapsed, 3),
            "sources": assembly_res.get("sources", [])
        }

# Global LLM instance
llm_engine = LocalLLM()
