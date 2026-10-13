"""
Offline Speech Recognition (ASR) Module using faster-whisper.
Runs Whisper locally on CPU/CUDA with automatic language detection and fallback.
"""
import os
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OfflineASR:
    def __init__(self, model_size: str = "small", device: str = "cpu", compute_type: str = "int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self._is_loaded = False

    def load_model(self):
        """Loads faster-whisper model into memory."""
        if self._is_loaded:
            return

        try:
            from faster_whisper import WhisperModel
            logger.info(f"Loading faster-whisper model ({self.model_size}) on {self.device} ({self.compute_type})...")
            # Uses models_cache or default huggingface local cache
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=os.path.join(os.getcwd(), "models_cache", "whisper")
            )
            self._is_loaded = True
            logger.info("faster-whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load faster-whisper model: {e}")
            self._is_loaded = False
            self.model = None

    def is_ready(self) -> bool:
        return self._is_loaded and self.model is not None

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribes given audio file.
        Returns transcript, detected language, confidence, and latency in seconds.
        """
        start_time = time.time()

        if not self.is_ready():
            self.load_model()

        if not self.is_ready():
            raise RuntimeError("ASR model is not loaded. Please download whisper model or check configuration.")

        # Whisper supports language hints or None for auto-detection
        lang_hint = language if language and language != "auto" else None

        segments, info = self.model.transcribe(
            audio_path,
            language=lang_hint,
            beam_size=3,
            vad_filter=True, # Filter silence and background noise
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        transcript_parts = []
        for segment in segments:
            transcript_parts.append(segment.text.strip())

        full_transcript = " ".join(transcript_parts).strip()
        elapsed = time.time() - start_time

        return {
            "transcript": full_transcript,
            "detected_language": info.language,
            "language_probability": round(info.language_probability, 3),
            "duration": round(info.duration, 2),
            "latency_seconds": round(elapsed, 3)
        }

# Global singleton instance
asr_engine = OfflineASR()
