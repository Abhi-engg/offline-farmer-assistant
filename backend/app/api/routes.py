"""
FastAPI Router for Farmer AI Voice Assistant.
Endpoints for voice processing, text chat, speech synthesis, audio streaming, and system status.
"""
import os
import shutil
import tempfile
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.conversation import pipeline, session_manager
from app.services.retrieval import retriever
from app.languages.registry import get_supported_languages, get_language_config
from app.models.asr import asr_engine
from app.models.llm import llm_engine
from app.models.tts import tts_engine, AUDIO_OUTPUT_DIR

router = APIRouter()

class TextQueryRequest(BaseModel):
    query: str
    language: str = "hi"
    session_id: Optional[str] = None

class AddDocumentRequest(BaseModel):
    id: str
    title: str
    language: str
    crop: str
    category: str
    keywords: List[str]
    content: str
    source: str

@router.get("/languages")
async def list_languages():
    """Returns list of supported regional languages with native names."""
    return {"languages": get_supported_languages()}

@router.get("/status")
async def system_status():
    """Checks offline readiness of all pipeline components."""
    ollama_ready = await llm_engine.is_engine_available()
    return {
        "status": "online",
        "offline_ready": True,
        "asr_ready": asr_engine.is_ready(),
        "llm_engine": f"ollama/{llm_engine.model_name}" if ollama_ready else "local_grounded_rag_engine",
        "ollama_connected": ollama_ready,
        "knowledge_documents_count": len(retriever.documents),
        "tts_ready": True
    }

@router.post("/chat/text")
async def chat_text(req: TextQueryRequest):
    """Processes a text question from a farmer."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    result = await pipeline.process_text_turn(
        query=req.query,
        language_code=req.language,
        session_id=req.session_id
    )
    return result

@router.post("/chat/voice")
async def chat_voice(
    audio: UploadFile = File(...),
    language: str = Form("hi"),
    session_id: Optional[str] = Form(None)
):
    """
    Processes recorded voice from the farmer.
    1. Saves uploaded audio to a temporary file.
    2. Runs faster-whisper ASR.
    3. Runs RAG + LLM reasoning.
    4. Synthesizes voice response.
    """
    temp_dir = tempfile.gettempdir()
    file_ext = os.path.splitext(audio.filename)[1] or ".webm"
    temp_audio_path = os.path.join(temp_dir, f"farmer_voice_{os.urandom(4).hex()}{file_ext}")

    try:
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        result = await pipeline.process_voice_turn(
            audio_file_path=temp_audio_path,
            language_code=language,
            session_id=session_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except Exception:
                pass

@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serves synthesized audio response files."""
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Audio file not found")
    media_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    return FileResponse(filepath, media_type=media_type)

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Retrieves conversation history for an active session."""
    history = session_manager.get_history(session_id)
    return {"session_id": session_id, "history": history}

@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clears conversation history for a new inquiry."""
    session_manager.clear_session(session_id)
    return {"session_id": session_id, "message": "History cleared successfully"}

@router.post("/knowledge/add")
async def add_knowledge_doc(doc: AddDocumentRequest):
    """Allows administrators or extension workers to add verified crop guides."""
    success = retriever.add_document(doc.dict())
    if not success:
        raise HTTPException(status_code=400, detail="Invalid document structure")
    return {"message": "Document added to local verified knowledge base successfully"}

class FeedbackRequest(BaseModel):
    query: str
    language: str = "hi"
    rating: str # 'helpful' or 'unhelpful'
    comment: Optional[str] = None

@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    """Records farmer or field worker feedback on response quality."""
    from app.services.gap_telemetry import gap_telemetry
    gap_telemetry.record_user_feedback(
        query=req.query,
        language=req.language,
        rating=req.rating,
        comment=req.comment
    )
    return {"message": "Feedback recorded successfully for continuous model improvement"}

@router.get("/gaps/recent")
async def list_recent_gaps(limit: int = 50):
    """Lists unhandled farmer queries, missing crops, and low-confidence turns."""
    from app.services.gap_telemetry import gap_telemetry
    gaps = gap_telemetry.get_recent_gaps(limit=limit)
    return {"count": len(gaps), "gaps": gaps}

@router.get("/gaps/summary")
async def gaps_summary():
    """Returns analytics and clustering on unhandled queries to guide Phase 3 dataset creation."""
    from app.services.gap_telemetry import gap_telemetry
    return gap_telemetry.get_summary()

@router.get("/gaps/export")
async def export_gaps_file():
    """Allows offline export/download of the JSONL unhandled questions ledger."""
    from app.services.gap_telemetry import GAP_LOG_FILE
    if not os.path.exists(GAP_LOG_FILE):
        raise HTTPException(status_code=404, detail="No gap telemetry logs found yet")
    return FileResponse(GAP_LOG_FILE, filename="unhandled_farmer_gaps.jsonl", media_type="application/jsonlines")

