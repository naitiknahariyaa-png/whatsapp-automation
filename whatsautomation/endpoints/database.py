"""
Database Endpoints
==================

Endpoints for database operations:
- Messages
- Keywords/Templates
- Statistics
- Customers
"""

import os
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# ═══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class MessageResponse(BaseModel):
    id: int
    sender: str
    message: str
    response: Optional[str]
    timestamp: str
    is_read: bool

class KeywordResponse(BaseModel):
    keyword: str
    response: str

class StatsResponse(BaseModel):
    total_messages: int
    total_keywords: int
    total_customers: int
    messages_today: int

class AddMessageRequest(BaseModel):
    sender: str
    message: str
    response: Optional[str] = ""

# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get database statistics"""
    try:
        from src.core.database import get_database
        db = get_database()
        
        keywords = db.get_all_keywords()
        messages = db.get_all_messages(limit=1000)
        
        # Count messages from today
        today = datetime.now().date()
        messages_today = 0
        for msg in messages:
            try:
                msg_date = datetime.fromisoformat(msg.get("timestamp", "")).date()
                if msg_date == today:
                    messages_today += 1
            except:
                pass
        
        return StatsResponse(
            total_messages=len(messages),
            total_keywords=len(keywords),
            total_customers=0,  # Would need customer table
            messages_today=messages_today
        )
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages")
async def get_messages(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Get message history"""
    try:
        from src.core.database import get_database
        db = get_database()
        messages = db.get_all_messages(limit=limit, offset=offset)
        return {
            "status": "success",
            "count": len(messages),
            "messages": messages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages")
async def add_message(request: AddMessageRequest):
    """Add a message to the database"""
    try:
        from src.core.database import get_database
        db = get_database()
        
        msg_id = db.add_message(
            sender=request.sender,
            message=request.message,
            response=request.response or ""
        )
        
        return {
            "status": "success",
            "id": msg_id,
            "message": "Message added"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keywords")
async def get_keywords():
    """Get all auto-reply keywords"""
    try:
        from src.core.database import get_database
        db = get_database()
        keywords = db.get_all_keywords()
        
        return {
            "status": "success",
            "count": len(keywords),
            "keywords": [
                {"keyword": k, "response": v}
                for k, v in keywords
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/keywords")
async def add_keyword(
    keyword: str = Body(...),
    response: str = Body(...)
):
    """Add auto-reply keyword"""
    try:
        from src.core.database import get_database
        db = get_database()
        
        db.add_keyword(keyword, response)
        
        return {
            "status": "success",
            "message": f"Added keyword: {keyword}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/keywords/{keyword}")
async def delete_keyword(keyword: str):
    """Delete auto-reply keyword"""
    try:
        from src.core.database import get_database
        db = get_database()
        
        db.remove_keyword(keyword)
        
        return {
            "status": "success",
            "message": f"Deleted keyword: {keyword}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers")
async def get_customers():
    """Get all customers"""
    try:
        from src.core.database import get_database
        db = get_database()
        customers = db.get_all_customers()
        
        return {
            "status": "success",
            "count": len(customers),
            "customers": customers
        }
    except Exception as e:
        # Return empty list if method doesn't exist
        return {"status": "success", "count": 0, "customers": []}

@router.post("/customers")
async def add_customer(phone: str = Body(...)):
    """Add a customer"""
    try:
        from src.core.database import get_database
        db = get_database()
        
        db.add_customer(phone)
        
        return {
            "status": "success",
            "message": f"Added customer: {phone}"
        }
    except AttributeError:
        # Method doesn't exist
        return {"status": "success", "message": "Customer feature not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup")
async def backup_database():
    """Create database backup"""
    try:
        from src.core.database import get_database
        import shutil
        from pathlib import Path
        
        db = get_database()
        db_file = Path("data/whatsapp.db")
        
        if not db_file.exists():
            return {"status": "error", "message": "Database file not found"}
        
        backup_dir = Path("data/backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.db"
        
        shutil.copy2(db_file, backup_file)
        
        return {
            "status": "success",
            "backup_file": str(backup_file),
            "message": "Backup created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/messages/old")
async def cleanup_old_messages(days: int = Query(30, ge=1, le=365)):
    """Delete messages older than specified days"""
    try:
        from src.core.database import get_database
        db = get_database()
        
        if hasattr(db, 'cleanup_old_messages'):
            db.cleanup_old_messages(days=days)
            return {
                "status": "success",
                "message": f"Deleted messages older than {days} days"
            }
        return {"status": "success", "message": "Cleanup not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
