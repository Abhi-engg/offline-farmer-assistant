"""
Main FastAPI Application Entry Point for Offline Farmer AI Voice Assistant.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.models.asr import asr_engine

app = FastAPI(
    title="Offline Farmer AI Voice Assistant",
    description="Conversational offline-first AI assistant for Indian farmers supporting Hindi, Marathi, Telugu, and Bengali.",
    version="1.0.0"
)

# Enable CORS for local Vite development frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    print("Offline Farmer Voice Assistant API started. ASR models will load on demand.")

@app.get("/")
def root():
    return {
        "app": "Offline Farmer AI Voice Assistant",
        "version": "1.0.0",
        "docs": "/docs",
        "description": "Offline speech-in, speech-out conversational farming assistant"
    }
