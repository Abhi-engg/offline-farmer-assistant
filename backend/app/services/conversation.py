"""
Conversational Orchestration Service for Farmer AI Assistant.
Maintains session history, links ASR -> RAG -> LLM -> TTS pipeline, and collects latency & metrics.
"""
import os
import time
import uuid
import logging
from typing import Dict, Any, List, Optional

from app.models.asr import asr_engine
from app.models.llm import llm_engine
from app.models.tts import tts_engine
from app.services.retrieval import retriever
from app.languages.registry import get_language_config

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        # Maps session_id to list of turns: {"role": "...", "content": "..."}
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        if not session_id or session_id not in self.sessions:
            new_id = session_id or str(uuid.uuid4())
            self.sessions[new_id] = []
            return new_id
        return session_id

    def add_turn(self, session_id: str, role: str, content: str):
        if session_id in self.sessions:
            self.sessions[session_id].append({"role": role, "content": content})

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.sessions.get(session_id, [])

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id] = []

session_manager = SessionManager()

class ConversationPipeline:
    def __init__(self):
        self.asr = asr_engine
        self.llm = llm_engine
        self.tts = tts_engine
        self.retriever = retriever

    async def process_voice_turn(
        self,
        audio_file_path: str,
        language_code: str = "hi",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete Voice-in to Voice-out Pipeline:
        Audio -> ASR -> Query -> RAG Retrieval -> LLM Reasoning -> TTS -> Audio & Text
        """
        pipeline_start = time.time()
        sid = session_manager.get_or_create_session(session_id)

        # 1. Speech Recognition (ASR)
        asr_res = self.asr.transcribe(audio_file_path, language=language_code)
        recognized_query = asr_res.get("transcript", "").strip()

        if not recognized_query:
            # Empty audio or silence
            return {
                "session_id": sid,
                "status": "empty_input",
                "query": "",
                "answer": "कोई आवाज़ सुनाई नहीं दी। कृपया माइक बटन दबाकर दोबारा बोलें।",
                "audio_url": None,
                "sources": [],
                "metrics": {
                    "asr_latency": asr_res.get("latency_seconds", 0),
                    "total_latency": round(time.time() - pipeline_start, 3)
                }
            }

        # 2. Process text turn using retrieved query
        text_turn_res = await self.process_text_turn(
            query=recognized_query,
            language_code=language_code,
            session_id=sid
        )

        # Combine ASR metrics
        text_turn_res["asr_metrics"] = asr_res
        text_turn_res["metrics"]["asr_latency"] = asr_res.get("latency_seconds", 0)
        text_turn_res["metrics"]["total_latency"] = round(time.time() - pipeline_start, 3)

        return text_turn_res

    async def process_text_turn(
        self,
        query: str,
        language_code: str = "hi",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Text Query -> RAG Retrieval -> LLM -> TTS -> Spoken Audio + Response
        """
        pipeline_start = time.time()
        sid = session_manager.get_or_create_session(session_id)
        history = session_manager.get_history(sid)

        # Record farmer question
        session_manager.add_turn(sid, "user", query)

        # 1. RAG Knowledge Retrieval
        rag_start = time.time()
        retrieved_docs = self.retriever.search(query, language=language_code, top_k=2)
        rag_latency = round(time.time() - rag_start, 3)

        # 2. Local LLM Reasoning
        llm_res = await self.llm.generate_response(
            query=query,
            language_code=language_code,
            rag_context=retrieved_docs,
            history=history
        )
        answer_text = llm_res.get("answer", "")
        session_manager.add_turn(sid, "assistant", answer_text)

        # 3. Text-to-Speech Synthesis (TTS)
        tts_res = await self.tts.synthesize(text=answer_text, language_code=language_code)

        total_latency = round(time.time() - pipeline_start, 3)

        return {
            "session_id": sid,
            "status": "success",
            "query": query,
            "answer": answer_text,
            "language": language_code,
            "sources": [d.get("title") for d in retrieved_docs],
            "source_documents": retrieved_docs,
            "audio_url": tts_res.get("audio_url"),
            "audio_filename": tts_res.get("audio_filename"),
            "engine": llm_res.get("engine"),
            "intent": llm_res.get("intent"),
            "slots": llm_res.get("slots"),
            "is_handled": llm_res.get("is_handled"),
            "metrics": {
                "rag_latency": rag_latency,
                "llm_latency": llm_res.get("latency_seconds", 0),
                "tts_latency": tts_res.get("latency_seconds", 0),
                "total_latency": total_latency
            }
        }

pipeline = ConversationPipeline()
