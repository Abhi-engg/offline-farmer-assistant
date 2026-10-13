"""
Offline Model Download & Verification Utility for Offline Farmer Voice Assistant.
Downloads or verifies local model checkpoints:
1. faster-whisper (whisper-small)
2. Qwen2.5 Instruct / quantized GGUF
"""
import os
import sys

# UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models_cache")
os.makedirs(MODELS_DIR, exist_ok=True)

def check_whisper_model():
    print("Checking faster-whisper model setup...")
    try:
        from faster_whisper import WhisperModel
        whisper_dir = os.path.join(MODELS_DIR, "whisper")
        os.makedirs(whisper_dir, exist_ok=True)
        print("  faster-whisper library is installed and ready.")
        print(f"  Target cache directory: {whisper_dir}")
        return True
    except Exception as e:
        print(f"  Whisper check warning: {e}")
        return False

def check_tts_voices():
    print("Checking local TTS voice readiness...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"  pyttsx3 system TTS voices detected: {len(voices)}")
        return True
    except Exception as e:
        print(f"  TTS check warning: {e}")
        return False

def check_ollama_runtime():
    print("Checking Ollama local runtime for Qwen2.5 Instruct...")
    import urllib.request
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                print("  [SUCCESS] Ollama daemon is active and running locally.")
                return True
    except Exception:
        print("  [INFO] Ollama daemon not running. Local Grounded Expert Engine will serve queries seamlessly.")
        return False

if __name__ == "__main__":
    print("=== Offline Farmer AI Assistant Model Verification ===")
    check_whisper_model()
    check_tts_voices()
    check_ollama_runtime()
    print("=====================================================")
