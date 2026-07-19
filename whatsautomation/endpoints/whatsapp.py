"""
WhatsApp Endpoints
==================

Endpoints for WhatsApp messaging and status via OpenWA Gateway.

Features:
- Send text messages
- Send images
- Get connection status
- Monitor incoming messages
"""

import os
import logging
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field
import requests

logger = logging.getLogger(__name__)
router = APIRouter()

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

OPENWA_URL = os.getenv("OPENWA_URL", "http://localhost:3000")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "")
OPENWA_SESSION = os.getenv("OPENWA_SESSION_ID", "default")

# ═══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class SendMessageRequest(BaseModel):
    phone: str = Field(..., description="Phone number with country code (919876543210)")
    message: str = Field(..., description="Message text")
    session: Optional[str] = Field(OPENWA_SESSION, description="Session ID")

class SendImageRequest(BaseModel):
    phone: str = Field(..., description="Phone number")
    image_url: str = Field(..., description="Image URL")
    caption: Optional[str] = Field(None, description="Image caption")
    session: Optional[str] = Field(OPENWA_SESSION)

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_headers():
    """Get OpenWA API headers"""
    return {
        "X-API-Key": OPENWA_API_KEY,
        "Content-Type": "application/json"
    }

def format_phone(phone: str) -> str:
    """Format phone number for WhatsApp"""
    phone = phone.replace("+", "").replace(" ", "").replace("-", "")
    if not phone.endswith("@c.us"):
        phone = f"{phone}@c.us"
    return phone

# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/status")
async def get_whatsapp_status():
    """Get WhatsApp connection status"""
    if not OPENWA_API_KEY:
        return {
            "status": "not_configured",
            "message": "OPENWA_API_KEY not set",
            "connected": False
        }
    
    try:
        headers = get_headers()
        r = requests.get(
            f"{OPENWA_URL}/api/connection",
            headers=headers,
            timeout=10
        )
        
        if r.status_code == 200:
            data = r.json()
            return {
                "status": "connected",
                "connected": True,
                "session": OPENWA_SESSION,
                "details": data
            }
        else:
            return {
                "status": "disconnected",
                "connected": False,
                "error": f"HTTP {r.status_code}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "status": "not_running",
            "connected": False,
            "message": "OpenWA not running. Start with: docker run -d --name openwa -p 3000:3000 waha/waha:latest"
        }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "error": str(e)
        }

@router.post("/send")
async def send_message(request: SendMessageRequest):
    """Send WhatsApp text message"""
    if not OPENWA_API_KEY:
        raise HTTPException(status_code=500, detail="OPENWA_API_KEY not configured")
    
    try:
        headers = get_headers()
        session = request.session or OPENWA_SESSION
        
        data = {
            "session": session,
            "chatId": format_phone(request.phone),
            "text": request.message
        }
        
        r = requests.post(
            f"{OPENWA_URL}/api/messages/sendText",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if r.status_code == 200 or r.status_code == 201:
            return {
                "status": "success",
                "message": "Message sent",
                "phone": request.phone
            }
        else:
            raise HTTPException(
                status_code=r.status_code,
                detail=f"Failed to send: {r.text}"
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail="OpenWA not running")
    except Exception as e:
        logger.error(f"Send message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-image")
async def send_image(request: SendImageRequest):
    """Send WhatsApp image message"""
    if not OPENWA_API_KEY:
        raise HTTPException(status_code=500, detail="OPENWA_API_KEY not configured")
    
    try:
        headers = get_headers()
        session = request.session or OPENWA_SESSION
        
        data = {
            "session": session,
            "chatId": format_phone(request.phone),
            "mediaType": "image",
            "mediaUrl": request.image_url,
            "caption": request.caption or ""
        }
        
        r = requests.post(
            f"{OPENWA_URL}/api/messages/sendMedia",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if r.status_code == 200 or r.status_code == 201:
            return {
                "status": "success",
                "message": "Image sent",
                "phone": request.phone
            }
        else:
            raise HTTPException(status_code=r.status_code, detail=r.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chats")
async def get_chats(limit: int = Query(20, ge=1, le=100)):
    """Get chat list"""
    if not OPENWA_API_KEY:
        raise HTTPException(status_code=500, detail="OPENWA_API_KEY not configured")
    
    try:
        headers = get_headers()
        r = requests.get(
            f"{OPENWA_URL}/api/chats",
            headers=headers,
            params={"limit": limit, "session": OPENWA_SESSION},
            timeout=10
        )
        
        if r.status_code == 200:
            return {
                "status": "success",
                "chats": r.json()
            }
        return {"status": "error", "message": r.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages/{phone}")
async def get_messages(phone: str, limit: int = Query(20, ge=1, le=100)):
    """Get messages from a specific chat"""
    if not OPENWA_API_KEY:
        raise HTTPException(status_code=500, detail="OPENWA_API_KEY not configured")
    
    try:
        headers = get_headers()
        chat_id = format_phone(phone)
        
        r = requests.get(
            f"{OPENWA_URL}/api/messages/{chat_id}",
            headers=headers,
            params={"limit": limit, "session": OPENWA_SESSION},
            timeout=10
        )
        
        if r.status_code == 200:
            return {
                "status": "success",
                "phone": phone,
                "messages": r.json()
            }
        return {"status": "error", "message": r.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast")
async def broadcast_message(
    phones: List[str] = Body(..., description="List of phone numbers"),
    message: str = Body(..., description="Message to send")
):
    """Broadcast message to multiple phones"""
    if not OPENWA_API_KEY:
        raise HTTPException(status_code=500, detail="OPENWA_API_KEY not configured")
    
    results = {"sent": 0, "failed": 0, "errors": []}
    
    for phone in phones:
        try:
            headers = get_headers()
            data = {
                "session": OPENWA_SESSION,
                "chatId": format_phone(phone),
                "text": message
            }
            
            r = requests.post(
                f"{OPENWA_URL}/api/messages/sendText",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if r.status_code in [200, 201]:
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({"phone": phone, "error": r.text})
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"phone": phone, "error": str(e)})
    
    return {
        "status": "completed",
        "total": len(phones),
        **results
    }
