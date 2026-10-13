# Offline AI Voice Assistant for Indian Farmers (किसान आवाज़ - Kisan Vaani)

A complete, functional, 100% offline-first conversational AI voice assistant tailored for Indian farmers. 

Unlike translation tools, **Kisan Vaani** is a true **farmer-to-assistant conversational companion**: the farmer speaks in their regional language, the assistant listens, reasons over verified agricultural knowledge, generates a practical, safe answer, and speaks it back aloud in their native tongue.

---

## 🌾 Key Highlights

- **Direct Voice-In / Voice-Out Flow**: No complex keyboard typing or multi-screen toggling. Just one large microphone button.
- **Strictly Offline-First**: Runs ASR, RAG, Reasoning, and TTS locally on the device without any cloud API dependency or farmer data telemetry.
- **Multilingual Support**:
  - **हिन्दी (Hindi)** — Uttar Pradesh, Bihar, Madhya Pradesh, Rajasthan, Haryana
  - **मराठी (Marathi)** — Maharashtra
  - **తెలుగు (Telugu)** — Andhra Pradesh, Telangana
  - **বাংলা (Bengali)** — West Bengal, Tripura
- **Grounded Agricultural RAG**: Retrieves verified ICAR, KVK, and State Agricultural University documents before generating an answer.
- **Safety First**:
  - Avoids definitive diagnoses from vague symptoms.
  - Asks clarifying questions when information is insufficient.
  - Never invents chemical dosages or speculative pesticide treatments.
  - Flags offline limitations for volatile data (live weather, daily mandi rates, latest scheme updates).

---

## 🏛️ System Architecture

```text
[ Farmer Speaks ] ──▶ [ faster-whisper ASR (int8) ] 
                                  │
                          (Text Transcript)
                                  ▼
                    [ Local Agricultural RAG ]
                    (ICAR/KVK Verified Knowledge)
                                  │
                                  ▼
               [ Local Conversational Reasoner / LLM ]
                   (Qwen2.5 Instruct / Grounded Engine)
                                  │
                                  ▼
                     [ Indic Neural TTS Engine ]
                    (edge-tts / pyttsx3 Fallback)
                                  │
[ Farmer Listens ] ◀── [ Spoken Audio + Native Text ]
```

---

## 💻 Hardware & Performance Requirements

- **GPU Target**: NVIDIA GeForce RTX 3050 (6 GB VRAM) or equivalent.
- **CPU Fallback**: Fully supported with 8-bit quantized faster-whisper and quantized small LLM models.
- **RAM**: Minimum 8 GB (16 GB recommended).
- **Storage**: ~3-5 GB for offline models and agricultural knowledge bases.

---

## 🚀 Quick Setup & Run

### 1. Clone the Repository
```bash
git clone https://github.com/NISHANTTMAURYA/offline-farmer-assistant.git
cd offline-farmer-assistant
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Run pipeline verification test
python scripts/verify_pipeline.py

# Start Backend Server (runs on http://localhost:8000)
python scripts/run_local.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173 in your browser
```

---

## 🧪 Testing & Verification

Run the verification test suite:
```bash
python scripts/verify_pipeline.py
```
Outputs:
- Language registry capabilities test
- Local RAG retrieval scoring (Hindi wheat disease, Marathi cotton bollworm, PM-KISAN)
- Multi-turn session persistence
- End-to-end voice/text query to TTS audio generation

---

## 📜 Model Licenses
- **faster-whisper**: MIT License
- **Qwen2.5**: Apache 2.0 License
- **Indic TTS / edge-tts**: Open-source / MIT License

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for details.
