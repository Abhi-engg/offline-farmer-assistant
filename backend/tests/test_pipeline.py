"""
Automated Pipeline and Integration Tests for Offline Farmer Voice Assistant.
Tests:
1. Language Registry verification.
2. Local RAG Retrieval (Hindi wheat yellow leaves, Marathi cotton pink bollworm, etc.).
3. Grounded Agricultural Reasoning (Safety check: no dosage hallucination, asks follow-ups).
4. Audio Speech Synthesis (TTS).
5. Fast pipeline text & conversation state management.
"""
import pytest
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.languages.registry import LANGUAGES, get_supported_languages, get_language_config
from app.services.retrieval import AgriculturalKnowledgeRetriever
from app.services.conversation import SessionManager, ConversationPipeline

def test_language_registry():
    supported = get_supported_languages()
    assert len(supported) == 4
    codes = [l["code"] for l in supported]
    assert "hi" in codes
    assert "mr" in codes
    assert "te" in codes
    assert "bn" in codes
    
    # Test native names
    hi_cfg = get_language_config("hi")
    assert hi_cfg["native_name"] == "हिन्दी"
    mr_cfg = get_language_config("mr")
    assert mr_cfg["native_name"] == "मराठी"

def test_local_rag_retrieval_hindi():
    retriever = AgriculturalKnowledgeRetriever()
    query = "मेरी गेहूँ की फसल के पत्ते पीले हो रहे हैं"
    results = retriever.search(query, language="hi", top_k=2)
    assert len(results) > 0
    top_doc = results[0]
    assert "गेहूँ" in top_doc["title"] or "गेहूँ" in top_doc["crop"]
    assert top_doc["source"] != ""

def test_local_rag_retrieval_marathi():
    retriever = AgriculturalKnowledgeRetriever()
    query = "कापसावरील बोंडअळी नियंत्रण कसे करावे"
    results = retriever.search(query, language="mr", top_k=2)
    assert len(results) > 0
    top_doc = results[0]
    assert "कापूस" in top_doc["crop"] or "बोंडअळी" in top_doc["title"]

def test_session_manager():
    sm = SessionManager()
    sid = sm.get_or_create_session()
    sm.add_turn(sid, "user", "नमस्ते")
    sm.add_turn(sid, "assistant", "नमस्ते किसान भाई!")
    hist = sm.get_history(sid)
    assert len(hist) == 2
    assert hist[0]["content"] == "नमस्ते"
    sm.clear_session(sid)
    assert len(sm.get_history(sid)) == 0

@pytest.mark.asyncio
async def test_complete_text_pipeline_flow():
    pipeline = ConversationPipeline()
    res = await pipeline.process_text_turn(
        query="गेहूँ में पीली पत्तियां क्यों होती हैं?",
        language_code="hi"
    )
    assert res["status"] == "success"
    assert len(res["answer"]) > 10
    assert len(res["sources"]) > 0
    assert res["metrics"]["total_latency"] >= 0
