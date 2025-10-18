#!/usr/bin/env python3
"""
Simple Smart AI API Server
FastAPI server for the enhanced simple_smart_ai.py with RAG + AI model
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import time
import logging
from simple_smart_ai import SimpleSmartAI

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
ai_assistant = SimpleSmartAI()
logger.info("✅ Simple Smart AI ready!")

# Pydantic models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: float
    network_data: dict
    request_id: str
    ai_model_used: bool
    rag_enabled: bool

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
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Chat error: {e}")
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
        return {
            "ai_model_loaded": ai_assistant.model is not None,
            "rag_enabled": ai_assistant.vectorizer is not None,
            "knowledge_base_size": len(ai_assistant.knowledge_base),
            "model_name": "distilgpt2" if ai_assistant.model else None,
            "vectorizer_ready": ai_assistant.vectorizer is not None
        }
    except Exception as e:
        logger.error(f"AI status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Simple Smart AI API Server...")
    print("📡 API will be available at: http://localhost:8088")
    print("🌐 Web interface: http://localhost:8502")
    print("📚 API docs: http://localhost:8088/docs")
    print("🧠 AI Brain: Ready with RAG + lightweight model!")
    
    uvicorn.run(app, host="0.0.0.0", port=8088)