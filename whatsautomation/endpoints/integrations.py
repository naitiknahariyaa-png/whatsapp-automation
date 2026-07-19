"""
Integrations Endpoints
======================

Endpoints for 50+ external service integrations.

Categories:
- AI: Groq, OpenRouter, Ollama, HuggingFace
- Database: Supabase, Redis, MongoDB
- CRM: Notion, Linear, Cal.com
- Analytics: Posthog, Sentry, Plausible
- Notifications: Discord, Ntfy, Telegram
- Storage: Cloudflare R2, MinIO
"""

import os
import logging
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# ═══════════════════════════════════════════════════════════════
# AVAILABLE INTEGRATIONS
# ═══════════════════════════════════════════════════════════════

INTEGRATIONS = {
    # AI & ML
    "groq": {"name": "Groq", "category": "ai", "free": True},
    "openrouter": {"name": "OpenRouter", "category": "ai", "free": True},
    "ollama": {"name": "Ollama", "category": "ai", "free": True},
    "huggingface": {"name": "HuggingFace", "category": "ai", "free": True},
    "gemini": {"name": "Google Gemini", "category": "ai", "free": True},
    
    # Database
    "supabase": {"name": "Supabase", "category": "database", "free": True},
    "redis": {"name": "Redis", "category": "database", "free": True},
    "mongodb": {"name": "MongoDB", "category": "database", "free": True},
    
    # Search
    "meilisearch": {"name": "Meilisearch", "category": "search", "free": True},
    "qdrant": {"name": "Qdrant", "category": "search", "free": True},
    
    # CRM
    "notion": {"name": "Notion", "category": "crm", "free": True},
    "linear": {"name": "Linear", "category": "crm", "free": True},
    "cal": {"name": "Cal.com", "category": "crm", "free": True},
    
    # Analytics
    "posthog": {"name": "PostHog", "category": "analytics", "free": True},
    "sentry": {"name": "Sentry", "category": "analytics", "free": True},
    "plausible": {"name": "Plausible", "category": "analytics", "free": True},
    
    # Notifications
    "discord": {"name": "Discord", "category": "notifications", "free": True},
    "ntfy": {"name": "Ntfy", "category": "notifications", "free": True},
    "telegram": {"name": "Telegram", "category": "notifications", "free": True},
    
    # Storage
    "cloudflare_r2": {"name": "Cloudflare R2", "category": "storage", "free": True},
    "minio": {"name": "MinIO", "category": "storage", "free": True},
    
    # Automation
    "n8n": {"name": "N8N", "category": "automation", "free": True},
    "activepieces": {"name": "ActivePieces", "category": "automation", "free": True},
    "celery": {"name": "Celery", "category": "automation", "free": True},
    
    # Chatbots
    "botpress": {"name": "Botpress", "category": "chatbots", "free": True},
    "typebot": {"name": "Typebot", "category": "chatbots", "free": True},
    "chatwoot": {"name": "Chatwoot", "category": "chatbots", "free": True},
}

# ═══════════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════════

class NotificationRequest(BaseModel):
    message: str = Field(..., description="Notification message")
    title: Optional[str] = Field(None, description="Notification title")

class DiscordRequest(BaseModel):
    content: str = Field(..., description="Discord message content")
    embeds: Optional[List[Dict]] = Field(None, description="Embed objects")

# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/list")
async def list_integrations():
    """List all available integrations"""
    return {
        "status": "success",
        "count": len(INTEGRATIONS),
        "categories": {
            "ai": [v for k, v in INTEGRATIONS.items() if v["category"] == "ai"],
            "database": [v for k, v in INTEGRATIONS.items() if v["category"] == "database"],
            "search": [v for k, v in INTEGRATIONS.items() if v["category"] == "search"],
            "crm": [v for k, v in INTEGRATIONS.items() if v["category"] == "crm"],
            "analytics": [v for k, v in INTEGRATIONS.items() if v["category"] == "analytics"],
            "notifications": [v for k, v in INTEGRATIONS.items() if v["category"] == "notifications"],
            "storage": [v for k, v in INTEGRATIONS.items() if v["category"] == "storage"],
            "automation": [v for k, v in INTEGRATIONS.items() if v["category"] == "automation"],
            "chatbots": [v for k, v in INTEGRATIONS.items() if v["category"] == "chatbots"],
        }
    }

@router.get("/{integration}")
async def get_integration_info(integration: str):
    """Get information about an integration"""
    integration = integration.lower()
    
    if integration not in INTEGRATIONS:
        raise HTTPException(status_code=404, detail=f"Integration '{integration}' not found")
    
    info = INTEGRATIONS[integration]
    
    # Check if configured
    configured = False
    env_vars = {
        "supabase": ["SUPABASE_URL", "SUPABASE_KEY"],
        "redis": ["REDIS_URL"],
        "mongodb": ["MONGODB_URI"],
        "notion": ["NOTION_API_KEY"],
        "linear": ["LINEAR_API_KEY"],
        "discord": ["DISCORD_WEBHOOK"],
        "posthog": ["POSTHOG_API_KEY"],
        "sentry": ["SENTRY_DSN"],
        "n8n": ["N8N_WEBHOOK_URL"],
    }.get(integration, [])
    
    configured = any(os.getenv(var) for var in env_vars)
    
    return {
        "status": "success",
        "integration": integration,
        **info,
        "configured": configured
    }

@router.post("/{integration}/test")
async def test_integration(integration: str):
    """Test an integration connection"""
    integration = integration.lower()
    
    if integration not in INTEGRATIONS:
        raise HTTPException(status_code=404, detail=f"Integration '{integration}' not found")
    
    try:
        if integration == "discord":
            webhook = os.getenv("DISCORD_WEBHOOK")
            if not webhook:
                return {"status": "error", "message": "DISCORD_WEBHOOK not configured"}
            
            import requests
            r = requests.post(webhook, json={"content": "✅ WhatsAutomation API Test"})
            
            if r.status_code == 204:
                return {"status": "success", "message": "Discord webhook working!"}
            return {"status": "error", "message": f"HTTP {r.status_code}"}
        
        elif integration == "groq":
            key = os.getenv("GROQ_API_KEY")
            if not key:
                return {"status": "error", "message": "GROQ_API_KEY not configured"}
            
            import requests
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "hi"}]},
                timeout=10
            )
            
            if r.status_code == 200:
                return {"status": "success", "message": "Groq API working!"}
            return {"status": "error", "message": r.json().get("error", {}).get("message", "Error")}
        
        elif integration == "redis":
            import redis
            url = os.getenv("REDIS_URL", "redis://localhost:6379")
            try:
                r = redis.from_url(url)
                r.ping()
                return {"status": "success", "message": "Redis connected!"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        elif integration == "supabase":
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if not url or not key:
                return {"status": "error", "message": "Supabase not configured"}
            
            import requests
            r = requests.get(f"{url}/rest/v1/", headers={"apikey": key})
            
            if r.status_code == 200:
                return {"status": "success", "message": "Supabase connected!"}
            return {"status": "error", "message": f"HTTP {r.status_code}"}
        
        elif integration == "telegram":
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not token:
                return {"status": "error", "message": "TELEGRAM_BOT_TOKEN not configured"}
            
            import requests
            r = requests.get(f"https://api.telegram.org/bot{token}/getMe")
            
            if r.status_code == 200:
                data = r.json()
                return {"status": "success", "message": f"Bot @{data['result']['username']} working!"}
            return {"status": "error", "message": r.json().get("description", "Error")}
        
        else:
            return {"status": "info", "message": f"Test not implemented for {integration}"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/discord/send")
async def send_discord(request: DiscordRequest):
    """Send message to Discord webhook"""
    webhook = os.getenv("DISCORD_WEBHOOK")
    if not webhook:
        raise HTTPException(status_code=500, detail="DISCORD_WEBHOOK not configured")
    
    try:
        import requests
        data = {"content": request.content}
        if request.embeds:
            data["embeds"] = request.embeds
        
        r = requests.post(webhook, json=data)
        
        if r.status_code == 204:
            return {"status": "success", "message": "Message sent to Discord"}
        raise HTTPException(status_code=r.status_code, detail=r.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ntfy/send")
async def send_ntfy(
    topic: str = Body(...),
    message: str = Body(...),
    title: Optional[str] = Body(None)
):
    """Send notification via Ntfy"""
    url = os.getenv("NTFY_URL", "https://ntfy.sh")
    
    try:
        import requests
        data = message.encode('utf-8')
        headers = {"Topic": topic}
        if title:
            headers["Title"] = title
        
        r = requests.post(f"{url}/{topic}", data=data, headers=headers)
        
        if r.status_code == 200:
            return {"status": "success", "message": "Notification sent"}
        raise HTTPException(status_code=r.status_code, detail=r.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/telegram/send")
async def send_telegram(
    chat_id: str = Body(...),
    message: str = Body(...)
):
    """Send message via Telegram bot"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN not configured")
    
    try:
        import requests
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message}
        )
        
        if r.status_code == 200:
            return {"status": "success", "message": "Message sent"}
        raise HTTPException(status_code=r.status_code, detail=r.json().get("description", "Error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
