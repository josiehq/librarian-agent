#!/usr/bin/env python3
"""
Box 3 Voice MCP Wrapper
Provides voice-to-text capabilities via whisper-large-v3
"""

import asyncio
import io
import logging
import time
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Box3 Voice MCP", version="1.0.0")

# Ollama configuration
OLLAMA_HOST = "http://localhost:11434"
WHISPER_MODEL = "whisper-large-v3"


# =============================================================================
# REQUEST MODELS
# =============================================================================

class TranscribeRequest(BaseModel):
    """Audio transcription request"""
    audio_url: Optional[str] = None
    audio_base64: Optional[str] = None
    language: Optional[str] = None  # Auto-detect if None
    task: str = "transcribe"  # "transcribe" or "translate"


class VoiceCommandRequest(BaseModel):
    """Voice command routing request"""
    audio_url: Optional[str] = None
    audio_base64: Optional[str] = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ollama_transcribe(audio_path: str, language: Optional[str] = None) -> str:
    """Call Ollama whisper for audio transcription"""
    url = f"{OLLAMA_HOST}/api/generate"
    
    # Whisper expects specific prompt format
    prompt = "Transcribe the following audio:"
    if language:
        prompt = f"Transcribe the following audio in {language}:"
    
    payload = {
        "model": WHISPER_MODEL,
        "prompt": prompt,
        "audio": audio_path,
        "stream": False
    }
    
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    
    result = response.json()
    return result.get("response", "")


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": WHISPER_MODEL
    }


@app.post("/voice/transcribe")
async def transcribe_audio(request: TranscribeRequest):
    """
    Transcribe audio to text using Whisper
    
    Use case: Voice commands, meeting transcription
    Speed: Real-time (1x) on GPU, 2x slower on CPU
    """
    start_time = time.time()
    
    try:
        # Determine audio source
        if request.audio_url:
            audio_input = request.audio_url
        elif request.audio_base64:
            audio_input = f"data:audio/wav;base64,{request.audio_base64}"
        else:
            raise HTTPException(status_code=400, detail="Must provide audio_url or audio_base64")
        
        # Transcribe via Ollama
        transcription = ollama_transcribe(audio_input, request.language)
        
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "transcription": transcription,
            "language": request.language or "auto-detected",
            "elapsed_seconds": elapsed,
            "model": WHISPER_MODEL
        }
    
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/upload")
async def transcribe_upload(
    file: UploadFile = File(...),
    language: Optional[str] = None
):
    """
    Upload audio file directly for transcription
    
    Supported formats: WAV, MP3, M4A, FLAC
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/whisper_{int(time.time())}.{file.filename.split('.')[-1]}"
        
        with open(temp_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Transcribe
        transcription = ollama_transcribe(temp_path, language)
        
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
        
        return {
            "success": True,
            "transcription": transcription,
            "filename": file.filename,
            "language": language or "auto-detected"
        }
    
    except Exception as e:
        logger.error(f"Upload transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/command")
async def voice_command(request: VoiceCommandRequest):
    """
    Voice command routing (transcribe + parse intent)
    
    Use case: "Find leather wallets on AliExpress" → B1 agent task
    Workflow:
    1. Transcribe audio with Whisper
    2. Parse intent (simple keyword matching for now)
    3. Return agent + task
    """
    try:
        # Transcribe
        if request.audio_url:
            audio_input = request.audio_url
        elif request.audio_base64:
            audio_input = f"data:audio/wav;base64,{request.audio_base64}"
        else:
            raise HTTPException(status_code=400, detail="Must provide audio")
        
        transcription = ollama_transcribe(audio_input)
        
        # Simple intent parsing (can be enhanced with LLM later)
        text_lower = transcription.lower()
        
        agent = None
        task_type = None
        
        if any(kw in text_lower for kw in ["search", "find", "look for"]):
            agent = "B1_Concrete"
            task_type = "search"
        elif any(kw in text_lower for kw in ["create listing", "add to amazon", "list product"]):
            agent = "B1_Concrete"
            task_type = "create_listing"
        elif any(kw in text_lower for kw in ["analyze", "check", "review"]):
            agent = "B1_Concrete"
            task_type = "analyze"
        elif any(kw in text_lower for kw in ["code", "generate", "write"]):
            agent = "C3_Clash"
            task_type = "code_generation"
        else:
            agent = "D1_Puckfairy"  # Default to orchestrator
            task_type = "general"
        
        return {
            "success": True,
            "transcription": transcription,
            "routing": {
                "agent": agent,
                "task_type": task_type
            }
        }
    
    except Exception as e:
        logger.error(f"Voice command error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/realtime")
async def realtime_transcription(file: UploadFile = File(...)):
    """
    Real-time streaming transcription (WebSocket alternative)
    
    Use case: Live voice control
    Note: For true real-time, implement WebSocket version
    """
    try:
        # For now, process full audio chunk
        temp_path = f"/tmp/whisper_rt_{int(time.time())}.wav"
        
        with open(temp_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Transcribe
        start = time.time()
        transcription = ollama_transcribe(temp_path)
        elapsed = time.time() - start
        
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
        
        # Calculate real-time factor (< 1.0 = faster than real-time)
        # Assume 1 second of audio for now (can calculate from file metadata)
        rt_factor = elapsed / 1.0
        
        return {
            "success": True,
            "transcription": transcription,
            "elapsed_seconds": elapsed,
            "realtime_factor": rt_factor,
            "is_realtime": rt_factor < 1.0
        }
    
    except Exception as e:
        logger.error(f"Real-time error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Box 3 Voice MCP Wrapper on port 8084")
    uvicorn.run(app, host="0.0.0.0", port=8084)
