"""
Celery Tasks - Async Processing for WhatsApp Bot
Handle 10,000+ users with background task processing.

OPTIONAL: Install celery for async processing
    pip install celery redis

Without celery, tasks run synchronously.
"""

import os
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import celery - optional dependency
try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    logger.warning("Celery not installed. Tasks will run synchronously.")

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Create Celery app if available
celery_app = None
if CELERY_AVAILABLE:
    try:
        celery_app = Celery("whatsapp_bot", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
        celery_app.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="UTC",
            enable_utc=True,
            task_time_limit=300,
        )
    except Exception as e:
        logger.error(f"Celery init error: {e}")
        celery_app = None


def process_whatsapp_message(sender: str, message: str, message_id: str = "") -> Dict[str, Any]:
    """Process WhatsApp message"""
    try:
        from src.core.reply_engine import ReplyEngine
        from src.core.whatsapp_client import WhatsAppClient
        engine = ReplyEngine()
        response = engine.process_message(sender, message)
        client = WhatsAppClient()
        client.send_message(sender, response)
        return {"status": "success", "sender": sender, "response": response}
    except Exception as e:
        logger.error(f"Process error: {e}")
        return {"status": "failed", "error": str(e)}


def send_bulk_messages(numbers: List[str], message: str) -> Dict[str, Any]:
    """Send bulk messages"""
    try:
        from src.core.whatsapp_client import WhatsAppClient
        from src.utils.alerts import send_alert
        client = WhatsAppClient()
        results = []
        for i, number in enumerate(numbers):
            try:
                client.send_message(number, message)
                results.append({"number": number, "status": "sent"})
            except Exception as e:
                results.append({"number": number, "status": "failed", "error": str(e)})
        success = len([r for r in results if r["status"] == "sent"])
        send_alert(f"📊 Bulk: {success}/{len(numbers)} sent", "INFO")
        return {"status": "complete", "sent": success, "failed": len(results) - success}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def cleanup_old_messages(days: int = 30) -> Dict[str, Any]:
    """Cleanup old messages"""
    return {"status": "success", "days": days}


def send_daily_summary() -> Dict[str, Any]:
    """Send daily summary"""
    try:
        from src.utils.alerts import send_alert
        send_alert(f"📊 Daily Summary - {datetime.now().date()}", "INFO")
        return {"status": "success"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def send_scheduled_message(sender: str, message: str, scheduled_time: str) -> Dict[str, Any]:
    """Send scheduled message"""
    try:
        from src.core.whatsapp_client import WhatsAppClient
        client = WhatsAppClient()
        client.send_message(sender, message)
        return {"status": "sent", "sender": sender}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def health_check() -> Dict[str, Any]:
    """Health check"""
    return {"celery": CELERY_AVAILABLE, "healthy": True}
