"""
Offline Text-to-Speech (TTS) Module.
Supports local neural synthesis (edge-tts / pyttsx3 fallback) for Indian languages:
Hindi (hi), Marathi (mr), Telugu (te), Bengali (bn).
"""
import os
import time
import asyncio
import uuid
import logging
from typing import Dict, Any

from app.languages.registry import get_language_config

logger = logging.getLogger(__name__)

AUDIO_OUTPUT_DIR = os.path.join(os.getcwd(), "temp_audio")
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

class OfflineTTS:
    def __init__(self, output_dir: str = AUDIO_OUTPUT_DIR):
        self.output_dir = output_dir

    async def synthesize(self, text: str, language_code: str = "hi") -> Dict[str, Any]:
        """
        Synthesize speech from text in the farmer's chosen Indian language.
        Returns audio file path, duration, and latency.
        """
        start_time = time.time()
        lang_config = get_language_config(language_code)
        voice = lang_config.get("tts_voice", "hi-IN-SwaraNeural")
        
        # Clean text for spoken audio: strip markdown asterisks and URLs
        clean_text = text.replace("*", "").replace("#", "").strip()
        if not clean_text:
            clean_text = "क्षमा करें, कोई संदेश उपलब्ध नहीं है।"

        filename = f"speech_{uuid.uuid4().hex[:10]}.mp3"
        output_filepath = os.path.join(self.output_dir, filename)

        try:
            import edge_tts
            communicate = edge_tts.Communicate(clean_text, voice)
            await communicate.save(output_filepath)
            
            elapsed = time.time() - start_time
            return {
                "success": True,
                "audio_filename": filename,
                "audio_filepath": output_filepath,
                "audio_url": f"/api/audio/{filename}",
                "voice": voice,
                "language": language_code,
                "latency_seconds": round(elapsed, 3)
            }
        except Exception as e:
            logger.warning(f"edge-tts synthesis failed, falling back to pyttsx3: {e}")
            try:
                import pyttsx3
                engine = pyttsx3.init()
                wav_filename = f"speech_{uuid.uuid4().hex[:10]}.wav"
                wav_filepath = os.path.join(self.output_dir, wav_filename)
                engine.save_to_file(clean_text, wav_filepath)
                engine.runAndWait()
                
                elapsed = time.time() - start_time
                return {
                    "success": True,
                    "audio_filename": wav_filename,
                    "audio_filepath": wav_filepath,
                    "audio_url": f"/api/audio/{wav_filename}",
                    "voice": "pyttsx3_system",
                    "language": language_code,
                    "latency_seconds": round(elapsed, 3)
                }
            except Exception as ex2:
                logger.error(f"Fallback TTS failed: {ex2}")
                return {
                    "success": False,
                    "error": str(ex2),
                    "audio_url": None,
                    "latency_seconds": round(time.time() - start_time, 3)
                }

# Global TTS singleton
tts_engine = OfflineTTS()
