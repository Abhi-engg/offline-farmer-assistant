"""
Unit and integration test runner for Offline Farmer AI Assistant.
"""
import sys
import os
import asyncio

# Fix Windows console UTF-8 printing
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Setup sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.languages.registry import get_supported_languages, get_language_config
from app.services.retrieval import AgriculturalKnowledgeRetriever
from app.services.conversation import SessionManager, ConversationPipeline

def test_language_registry():
    print("Testing Language Registry...")
    supported = get_supported_languages()
    assert len(supported) == 4, f"Expected 4 languages, got {len(supported)}"
    codes = [l["code"] for l in supported]
    assert "hi" in codes and "mr" in codes and "te" in codes and "bn" in codes
    print("  [PASS] All 4 priority languages registered (Hindi, Marathi, Telugu, Bengali).")

def test_local_rag():
    print("Testing Local RAG Retrieval...")
    retriever = AgriculturalKnowledgeRetriever()
    
    # Hindi query
    query_hi = "मेरी गेहूँ की फसल के पत्ते पीले हो रहे हैं"
    res_hi = retriever.search(query_hi, language="hi")
    assert len(res_hi) > 0, "Expected match for wheat yellowing"
    print(f"  [PASS] Hindi RAG Matched: '{res_hi[0]['title']}' (Score: {res_hi[0]['score']})")

    # Marathi query
    query_mr = "कापूस बोंडअळी नियंत्रण"
    res_mr = retriever.search(query_mr, language="mr")
    assert len(res_mr) > 0, "Expected match for cotton bollworm"
    print(f"  [PASS] Marathi RAG Matched: '{res_mr[0]['title']}' (Score: {res_mr[0]['score']})")

    # Scheme query
    query_scheme = "पीएम किसान सम्मान निधि 6000"
    res_scheme = retriever.search(query_scheme, language="hi")
    assert len(res_scheme) > 0, "Expected match for PM-KISAN"
    print(f"  [PASS] Government Scheme RAG Matched: '{res_scheme[0]['title']}'")

def test_session_state():
    print("Testing Session Conversation Management...")
    sm = SessionManager()
    sid = sm.get_or_create_session()
    sm.add_turn(sid, "user", "गेहूँ में खाद कब डालें?")
    sm.add_turn(sid, "assistant", "पहली सिंचाई के समय यूरिया दें।")
    history = sm.get_history(sid)
    assert len(history) == 2
    print("  [PASS] Session memory and multi-turn state retained.")

async def test_full_pipeline():
    print("Testing Complete Conversational Pipeline (Query -> RAG -> Reasoner -> TTS)...")
    pipeline = ConversationPipeline()
    res = await pipeline.process_text_turn(
        query="मेरी गेहूँ की फसल के पत्ते पीले हो रहे हैं, मुझे क्या करना चाहिए?",
        language_code="hi"
    )
    assert res["status"] == "success"
    assert len(res["answer"]) > 20
    assert len(res["sources"]) > 0
    print(f"  [PASS] Answer generated: {res['answer'][:70]}...")
    print(f"  [PASS] Grounded Sources: {res['sources']}")
    print(f"  [PASS] Latency: Total={res['metrics']['total_latency']}s, RAG={res['metrics']['rag_latency']}s, TTS={res['metrics']['tts_latency']}s")

if __name__ == "__main__":
    test_language_registry()
    test_local_rag()
    test_session_state()
    asyncio.run(test_full_pipeline())
    print("\nALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
