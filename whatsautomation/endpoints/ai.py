"""
AI Endpoints
============

Endpoints for AI chat completions and model management.

Providers: Groq, OpenRouter, Ollama, HuggingFace, Gemini
"""

import os
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# ═══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    context: Optional[str] = Field("", description="System context")
    model: Optional[str] = Field(None, description="Model name (optional)")

class ConfigRequest(BaseModel):
    provider: str = Field(..., description="Provider: groq, openrouter, ollama, keyword")
    api_key: Optional[str] = Field(None, description="API key")
    model: Optional[str] = Field(None, description="Model name")

class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str
    tokens_used: Optional[int] = None

# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/status")
async def get_ai_status():
    """Get AI provider status"""
    try:
        from src.ai.providers import AIManager
        ai = AIManager()
        status = ai.get_status()
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        logger.error(f"AI status error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Generate AI chat response"""
    try:
        from src.ai.providers import AIManager
        ai = AIManager()
        
        response, provider, model = ai.get_response(
            message=request.message,
            context=request.context,
            model=request.model
        )
        
        return ChatResponse(
            response=response,
            provider=provider,
            model=model or "default"
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configure")
async def configure_ai(request: ConfigRequest):
    """Configure AI provider"""
    try:
        from src.ai.providers import AIManager
        ai = AIManager()
        
        ai.configure(
            provider=request.provider,
            api_key=request.api_key,
            model=request.model
        )
        
        return {
            "status": "success",
            "message": f"Configured {request.provider}",
            "model": request.model or "default"
        }
    except Exception as e:
        logger.error(f"Configure error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_models():
    """List available AI models"""
    return {
        "status": "success",
        "models": {
            "groq": [
                "llama-3.1-8b-instant",
                "llama-3.2-1b-preview", 
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            "openrouter": [
                "openai/gpt-4o-mini",
                "anthropic/claude-3-haiku",
                "google/gemini-2.0-flash-thinking-exp-01-21",
                "meta-llama/llama-3.1-8b-instruct"
            ],
            "ollama": [
                "llama3.2",
                "mistral",
                "phi",
                "deepseek-r1"
            ]
        }
    }

@router.post("/test")
async def test_ai(message: str = Body("Hello, how are you?")):
    """Test AI with a simple message"""
    try:
        from src.ai.providers import AIManager
        ai = AIManager()
        
        response, provider, model = ai.get_response(message)
        
        return {
            "status": "success",
            "input": message,
            "output": response,
            "provider": provider,
            "model": model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keywords")
async def get_keywords():
    """Get auto-reply keywords"""
    try:
        from src.core.database import get_database
        db = get_database()
        keywords = db.get_all_keywords()
        return {
            "status": "success",
            "keywords": [{"keyword": k, "response": v} for k, v in keywords]
        }
    except Exception as e:
        logger.error(f"Keywords error: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/keywords")
async def add_keyword(keyword: str = Body(...), response: str = Body(...)):
    """Add auto-reply keyword"""
    try:
        from src.core.database import get_database
        db = get_database()
        db.add_keyword(keyword, response)
        return {"status": "success", "message": f"Added keyword: {keyword}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
