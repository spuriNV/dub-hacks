#!/usr/bin/env python3
"""
Simple Smart AI API Server
FastAPI server for the enhanced simple_smart_ai.py with RAG + AI model
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import time
import logging
import os
from pathlib import Path
from simple_smart_ai import SimpleSmartAI
from piper_tts_module import get_piper_tts

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Simple Smart Network AI",
    description="AI-powered network analysis with RAG and lightweight models",
    version="7.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the AI assistant
logger.info("🧠 Initializing Simple Smart AI...")
ai_assistant = SimpleSmartAI(test_mode=False)  # Normal mode for real network analysis
logger.info("✅ Simple Smart AI ready!")

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    generate_audio: bool = False  # Option to generate audio response

class ChatResponse(BaseModel):
    response: str
    timestamp: float
    network_data: dict
    request_id: str
    ai_model_used: bool
    rag_enabled: bool
    audio_url: str | None = None  # URL to audio file if generated

class TTSRequest(BaseModel):
    text: str
    max_length: int = 500

# API Endpoints
@app.get("/")
async def root():
    return {
        "service": "Simple Smart Network AI",
        "version": "7.0.0",
        "status": "running",
        "ai_model_loaded": ai_assistant.model is not None,
        "rag_enabled": ai_assistant.vectorizer is not None,
        "capabilities": [
            "Real-time network analysis",
            "RAG knowledge retrieval",
            "Lightweight AI model (distilgpt2)",
            "CLI-based network diagnostics",
            "Intelligent troubleshooting",
            "Cross-platform support (Mac/Linux)"
        ],
        "message": "AI brain ready to analyze your network!"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "message": "Simple Smart AI service running",
        "ai_model_loaded": ai_assistant.model is not None,
        "rag_enabled": ai_assistant.vectorizer is not None,
        "knowledge_base_size": len(ai_assistant.knowledge_base)
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the AI brain"""
    try:
        logger.info(f"AI Brain request: {request.message}")
        result = ai_assistant.chat(request.message)

        # Generate audio if requested
        audio_url = None
        if request.generate_audio:
            try:
                piper = get_piper_tts()
                if piper.piper_available:
                    audio_dir = Path(__file__).parent / "audio_responses"
                    audio_dir.mkdir(exist_ok=True)

                    timestamp = int(time.time() * 1000)
                    audio_filename = f"response_{timestamp}.wav"
                    audio_path = audio_dir / audio_filename

                    audio_result = piper.text_to_speech(result['response'], str(audio_path))
                    if audio_result:
                        audio_url = f"/audio/{audio_filename}"
                        logger.info(f"Audio generated: {audio_url}")
                else:
                    logger.warning("Piper TTS not available, skipping audio generation")
            except Exception as audio_error:
                logger.error(f"Audio generation failed: {audio_error}")
                # Continue without audio - don't fail the whole request

        # Ensure all required fields are present
        response_data = {
            "response": result.get('response', 'Sorry, I could not process your request.'),
            "timestamp": result.get('timestamp', time.time()),
            "network_data": result.get('network_data', {}),
            "request_id": result.get('request_id', f"req_{int(time.time() * 1000)}"),
            "ai_model_used": result.get('ai_model_used', False),
            "rag_enabled": result.get('rag_enabled', False),
            "audio_url": audio_url
        }

        return ChatResponse(**response_data)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/network-status")
async def network_status():
    """Get current network status"""
    try:
        network_data = ai_assistant.get_network_data()
        return {
            "timestamp": time.time(),
            "network_data": network_data,
            "status": "ok"
        }
    except Exception as e:
        logger.error(f"Network status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai-status")
async def ai_status():
    """Get AI model and RAG status"""
    try:
        # Get Piper TTS status
        piper = get_piper_tts()
        tts_status = piper.get_status()

        return {
            "ai_model_loaded": ai_assistant.model is not None,
            "rag_enabled": ai_assistant.vectorizer is not None,
            "knowledge_base_size": len(ai_assistant.knowledge_base),
            "model_name": "distilgpt2" if ai_assistant.model else None,
            "vectorizer_ready": ai_assistant.vectorizer is not None,
            "tts_available": tts_status['piper_available'],
            "tts_model": tts_status['model_path']
        }
    except Exception as e:
        logger.error(f"AI status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using Piper TTS"""
    try:
        piper = get_piper_tts()

        if not piper.piper_available:
            raise HTTPException(status_code=503, detail="Piper TTS not available")

        # Create audio directory
        audio_dir = Path(__file__).parent / "audio_responses"
        audio_dir.mkdir(exist_ok=True)

        # Generate unique filename
        timestamp = int(time.time() * 1000)
        audio_filename = f"response_{timestamp}.wav"
        audio_path = audio_dir / audio_filename

        # Generate audio
        result = piper.text_to_speech(request.text, str(audio_path), max_length=request.max_length)

        if result:
            return {
                "success": True,
                "audio_file": audio_filename,
                "audio_url": f"/audio/{audio_filename}",
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve generated audio files"""
    try:
        audio_dir = Path(__file__).parent / "audio_responses"
        audio_path = audio_dir / filename

        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")

        return FileResponse(
            path=str(audio_path),
            media_type="audio/wav",
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Simple Smart AI API Server...")
    print("📡 API will be available at: http://localhost:8088")
    print("🌐 Web interface: http://localhost:8502")
    print("📚 API docs: http://localhost:8088/docs")
    print("🧠 AI Brain: Ready with RAG + lightweight model!")
    
    uvicorn.run(app, host="0.0.0.0", port=8088)