"""
WhatsAutomation API - FastAPI Application
========================================

A comprehensive REST API for WhatsApp automation with 50+ integrations.
All endpoints are test/production-ready with auto-generated Swagger docs.

Usage:
    uvicorn whatsautomation.app:app --reload --port 8000

Documentation:
    http://localhost:8000/docs - Swagger UI
    http://localhost:8000/redoc - ReDoc
    http://localhost:8000 - API Info
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# LOAD ENVIRONMENT
# ═══════════════════════════════════════════════════════════════

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ═══════════════════════════════════════════════════════════════
# INITIALIZE FASTAPI
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="WhatsAutomation API",
    description="""
## 🤖 WhatsAutomation API v1.0

A comprehensive WhatsApp automation API with 50+ integrations.

### Features
- **AI Providers**: Groq, OpenRouter, Ollama, HuggingFace, Gemini
- **WhatsApp**: OpenWA Gateway integration
- **Database**: SQLite, Supabase, Redis, MongoDB
- **CRM**: Notion, Linear, Cal.com
- **Analytics**: Posthog, Sentry, Plausible
- **Notifications**: Discord, Telegram, Ntfy
- **Storage**: Cloudflare R2, MinIO

### Quick Start
1. Configure API keys in `.env`
2. Run: `uvicorn whatsautomation.app:app --reload`
3. Test: `curl http://localhost:8000/health`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "WhatsAutomation",
        "url": "https://github.com/naitiknahariyaa-png/whatsapp-automation"
    }
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class MessageRequest(BaseModel):
    text: str = Field(..., description="Message text")
    chat_id: Optional[str] = Field(None, description="Chat ID (phone number)")

class SendMessageRequest(BaseModel):
    phone: str = Field(..., description="Phone number (with country code)")
    message: str = Field(..., description="Message text")
    
class AIRequest(BaseModel):
    message: str = Field(..., description="User message")
    context: Optional[str] = Field("", description="Conversation context")
    model: Optional[str] = Field(None, description="AI model to use")

class KeywordRequest(BaseModel):
    keyword: str = Field(..., description="Keyword to match")
    response: str = Field(..., description="Auto-reply response")

class ConfigRequest(BaseModel):
    provider: str = Field(..., description="Provider name")
    api_key: Optional[str] = Field(None, description="API key")
    model: Optional[str] = Field(None, description="Model name")

# ═══════════════════════════════════════════════════════════════
# HEALTH & STATUS ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    """API Information Page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WhatsAutomation API</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; background: #1a1a2e; color: #fff; }
            h1 { color: #667eea; }
            .card { background: #16213e; padding: 20px; border-radius: 10px; margin: 10px 0; }
            a { color: #667eea; }
            code { background: #0f3460; padding: 2px 8px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>🤖 WhatsAutomation API v1.0</h1>
        <div class="card">
            <h2>📚 Documentation</h2>
            <p><a href="/docs">🔷 Swagger UI</a> - Interactive API documentation</p>
            <p><a href="/redoc">📖 ReDoc</a> - Alternative documentation</p>
        </div>
        <div class="card">
            <h2>🚀 Quick Test</h2>
            <p><code>curl http://localhost:8000/health</code></p>
            <p><code>curl http://localhost:8000/api/v1/ai/status</code></p>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/v1/status")
async def get_status():
    """Get overall system status"""
    status = {
        "api": "✅ Running",
        "timestamp": datetime.now().isoformat()
    }
    
    # Check AI
    try:
        from src.ai.providers import AIManager
        ai = AIManager()
        ai_status = ai.get_status()
        status["ai"] = "✅ Active" if ai_status.get("groq_available") else "⚠️ Not configured"
    except Exception as e:
        status["ai"] = f"❌ Error: {str(e)[:50]}"
    
    # Check WhatsApp
    try:
        import requests
        url = os.getenv("OPENWA_URL", "http://localhost:3000")
        key = os.getenv("OPENWA_API_KEY", "")
        if key:
            r = requests.get(f"{url}/api/connection", headers={"X-API-Key": key}, timeout=5)
            status["whatsapp"] = "✅ Connected" if r.status_code == 200 else "❌ Not connected"
        else:
            status["whatsapp"] = "⚠️ Not configured"
    except Exception:
        status["whatsapp"] = "❌ Not running"
    
    return status

# ═══════════════════════════════════════════════════════════════
# INCLUDE ROUTERS
# ═══════════════════════════════════════════════════════════════

try:
    from .endpoints import ai, whatsapp, database, integrations
    app.include_router(ai.router, prefix="/api/v1/ai", tags=["🤖 AI"])
    app.include_router(whatsapp.router, prefix="/api/v1/whatsapp", tags=["📱 WhatsApp"])
    app.include_router(database.router, prefix="/api/v1/db", tags=["💾 Database"])
    app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["🔗 Integrations"])
    logger.info("✅ All routers loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ Some routers failed to load: {e}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
