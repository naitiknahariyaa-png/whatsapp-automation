"""
====================================================================
FASTAPI WEBHOOK - Professional Webhook Endpoint
====================================================================
"""

import asyncio
import logging
from typing import Optional, List
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logger = logging.getLogger(__name__)

# Pydantic models for request/response
class MessageRequest(BaseModel):
    """Incoming message request"""
    sender: str
    message: str
    session_id: Optional[str] = "default"

class MessageResponse(BaseModel):
    """Message response"""
    response: str
    provider: str
    cached: bool = False

class StatsResponse(BaseModel):
    """Statistics response"""
    total_messages: int
    total_replies: int
    total_ai_responses: int
    keywords_count: int
    cache_stats: dict

class KeywordRequest(BaseModel):
    """Add keyword request"""
    keyword: str
    response: str
    category: Optional[str] = "general"

# Create FastAPI app
app = FastAPI(
    title="WhatsApp AI Bot API",
    description="Professional webhook API for WhatsApp automation",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global AI manager and database (initialized on startup)
ai_manager = None
db = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global ai_manager, db
    
    # Import here to avoid circular imports
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from src.ai.providers import AIManager
    from src.core.database import get_database
    from src.core.config import load_config
    
    # Load config
    config = load_config()
    
    # Initialize AI
    ai_manager = AIManager()
    if config.ai.openrouter_api_key:
        ai_manager.configure("openrouter", config.ai.openrouter_api_key, config.ai.model)
    elif config.ai.groq_api_key:
        ai_manager.configure("groq", config.ai.groq_api_key, config.ai.model)
    
    # Initialize database
    db = get_database(config.database.path)
    
    logger.info("WhatsApp Bot API started!")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "WhatsApp AI Bot API",
        "version": "3.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/webhook/message", response_model=MessageResponse)
async def handle_message(request: MessageRequest):
    """
    Handle incoming WhatsApp message
    This is the main webhook endpoint
    """
    try:
        # Generate response
        context = db.get_conversation_context(request.session_id) if db else ""
        response, provider = ai_manager.generate(request.message, context)
        
        # Log message
        if db:
            db.log_message(request.sender, request.message, response, provider != "keyword")
            db.add_conversation(request.session_id, request.sender, "user", request.message)
            db.add_conversation(request.session_id, "bot", "assistant", response)
        
        return MessageResponse(
            response=response or "I'm having trouble responding right now.",
            provider=provider,
            cached=False
        )
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/keyword", response_model=dict)
async def add_keyword(request: KeywordRequest):
    """Add a new keyword"""
    try:
        if db:
            db.add_keyword(request.keyword, request.response, request.category)
            return {"success": True, "keyword": request.keyword}
        raise HTTPException(status_code=500, detail="Database not initialized")
    except Exception as e:
        logger.error(f"Error adding keyword: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get bot statistics"""
    try:
        if db:
            stats = db.get_stats()
            keywords = db.get_all_keywords()
            cache_stats = ai_manager.get_status()["cache"] if ai_manager else {}
            
            return StatsResponse(
                total_messages=stats.get("total_messages", 0),
                total_replies=stats.get("total_replies", 0),
                total_ai_responses=stats.get("total_ai_responses", 0),
                keywords_count=len(keywords),
                cache_stats=cache_stats
            )
        raise HTTPException(status_code=500, detail="Database not initialized")
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/keywords")
async def get_keywords():
    """Get all keywords"""
    try:
        if db:
            return {"keywords": db.get_all_keywords()}
        raise HTTPException(status_code=500, detail="Database not initialized")
    except Exception as e:
        logger.error(f"Error getting keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/keywords/{keyword}")
async def delete_keyword(keyword: str):
    """Delete a keyword"""
    try:
        if db:
            db.delete_keyword(keyword)
            return {"success": True, "deleted": keyword}
        raise HTTPException(status_code=500, detail="Database not initialized")
    except Exception as e:
        logger.error(f"Error deleting keyword: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/configure")
async def configure_ai(provider: str, api_key: str, model: Optional[str] = None):
    """Configure AI provider"""
    try:
        if ai_manager:
            ai_manager.configure(provider, api_key, model)
            return {"success": True, "provider": provider}
        raise HTTPException(status_code=500, detail="AI not initialized")
    except Exception as e:
        logger.error(f"Error configuring AI: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai/status")
async def get_ai_status():
    """Get AI provider status"""
    try:
        if ai_manager:
            return ai_manager.get_status()
        raise HTTPException(status_code=500, detail="AI not initialized")
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server"""
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    run_server()
