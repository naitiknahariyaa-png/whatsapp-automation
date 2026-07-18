"""
Celery Task Queue - Async Processing for WhatsApp Bot
Handle 10,000+ users with background task processing.
"""

import os
import logging
from typing import List, Dict, Any
from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "whatsapp_bot",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)


@celery_app.task(bind=True, max_retries=3)
def process_whatsapp_message(self, sender: str, message: str, message_id: str) -> Dict[str, Any]:
    """
    Process WhatsApp message in background
    
    Args:
        sender: Phone number of sender
        message: Message text
        message_id: Unique message ID
        
    Returns:
        Dict with status and response
    """
    try:
        # Import here to avoid circular imports
        from src.core.reply_engine import ReplyEngine
        from src.core.whatsapp_client import WhatsAppClient
        
        # Process message
        engine = ReplyEngine()
        response = engine.process_message(sender, message)
        
        # Send response back to user
        client = WhatsAppClient()
        client.send_message(sender, response)
        
        # Log in database
        from src.core.database import get_database
        db = get_database()
        db.add_message(sender, message, response)
        
        return {
            "status": "success",
            "sender": sender,
            "message": message,
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        
        # Retry on failure
        try:
            self.retry(countdown=60, exc=e)
        except self.MaxRetriesExceededError:
            return {
                "status": "failed",
                "error": str(e),
                "message_id": message_id
            }


@celery_app.task
def send_bulk_messages(numbers: List[str], message: str) -> Dict[str, Any]:
    """
    Send bulk messages to many users
    
    Args:
        numbers: List of phone numbers
        message: Message to send
        
    Returns:
        Dict with results summary
    """
    from src.core.whatsapp_client import WhatsAppClient
    from src.utils.alerts import send_alert
    
    client = WhatsAppClient()
    results = []
    
    for i, number in enumerate(numbers):
        try:
            client.send_message(number, message)
            results.append({
                "number": number,
                "status": "sent",
                "index": i
            })
            
            # Log progress every 10 messages
            if (i + 1) % 10 == 0:
                logger.info(f"Sent {i + 1}/{len(numbers)} messages")
                
        except Exception as e:
            results.append({
                "number": number,
                "status": "failed",
                "error": str(e),
                "index": i
            })
    
    success_count = len([r for r in results if r["status"] == "sent"])
    failed_count = len(results) - success_count
    
    # Send alert when complete
    send_alert(
        f"📊 Bulk message complete!\n"
        f"Total: {len(numbers)}\n"
        f"Sent: {success_count}\n"
        f"Failed: {failed_count}",
        "INFO"
    )
    
    return {
        "total": len(numbers),
        "sent": success_count,
        "failed": failed_count,
        "results": results
    }


@celery_app.task
def cleanup_old_messages(days: int = 30) -> Dict[str, Any]:
    """
    Cleanup old messages from database
    
    Args:
        days: Delete messages older than this many days
        
    Returns:
        Dict with cleanup results
    """
    from src.core.database import get_database
    
    try:
        db = get_database()
        deleted = db.cleanup_old_messages(days)
        
        logger.info(f"Cleaned up {deleted} old messages")
        
        return {
            "status": "success",
            "deleted": deleted,
            "days": days
        }
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def send_daily_summary() -> Dict[str, Any]:
    """
    Send daily summary report to admin
    
    Returns:
        Dict with summary statistics
    """
    from src.core.database import get_database
    from src.utils.alerts import send_alert
    from datetime import datetime, timedelta
    
    try:
        db = get_database()
        
        # Get today's stats
        today = datetime.now().date()
        stats = db.get_stats()
        
        # Format summary
        summary = f"""
📊 Daily Summary - {today}

💬 Messages: {stats.get('total_messages', 0)}
👥 Unique Users: {stats.get('unique_users', 0)}
✅ Replies Sent: {stats.get('replies_sent', 0)}

🤖 Bot Status: Running
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
"""
        
        # Send to Telegram
        send_alert(summary, "INFO")
        
        return {
            "status": "success",
            "date": str(today),
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Daily summary error: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def send_scheduled_message(phone: str, message: str, schedule_time: str) -> Dict[str, Any]:
    """
    Schedule a message to be sent later
    
    Args:
        phone: Recipient phone number
        message: Message to send
        schedule_time: ISO format datetime string
        
    Returns:
        Dict with task info
    """
    from src.core.whatsapp_client import WhatsAppClient
    from datetime import datetime
    import time
    
    try:
        # Calculate delay
        scheduled_dt = datetime.fromisoformat(schedule_time)
        now = datetime.now()
        delay_seconds = max(0, (scheduled_dt - now).total_seconds())
        
        # Wait until scheduled time
        if delay_seconds > 0:
            time.sleep(delay_seconds)
        
        # Send message
        client = WhatsAppClient()
        client.send_message(phone, message)
        
        return {
            "status": "sent",
            "phone": phone,
            "scheduled_time": schedule_time
        }
        
    except Exception as e:
        logger.error(f"Scheduled message error: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


# Periodic tasks schedule
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup scheduled tasks"""
    
    # Daily summary at 9 AM
    sender.add_periodic_task(
        crontab(hour=9, minute=0),
        send_daily_summary.s(),
        name="daily-summary"
    )
    
    # Cleanup old messages at 2 AM
    sender.add_periodic_task(
        crontab(hour=2, minute=0),
        cleanup_old_messages.s(30),
        name="cleanup-old-messages"
    )
    
    # Health check every 5 minutes
    sender.add_periodic_task(
        crontab(minute="*/5"),
        health_check.s(),
        name="health-check"
    )


@celery_app.task
def health_check() -> Dict[str, Any]:
    """Check if all services are healthy"""
    from src.core.whatsapp_client import WhatsAppClient
    from src.ai.providers import AIManager
    
    status = {
        "whatsapp": False,
        "ai": False,
        "database": False
    }
    
    try:
        # Check WhatsApp
        client = WhatsAppClient()
        status["whatsapp"] = client.is_connected()
    except:
        pass
    
    try:
        # Check AI
        ai = AIManager()
        status["ai"] = ai.get_status()["configured"]
    except:
        pass
    
    try:
        # Check Database
        from src.core.database import get_database
        db = get_database()
        db.get_stats()
        status["database"] = True
    except:
        pass
    
    return status


# Celery Beat schedule (for periodic tasks)
celery_app.conf.beat_schedule = {
    "daily-summary": {
        "task": "src.integrations.celery_tasks.send_daily_summary",
        "schedule": crontab(hour=9, minute=0),
    },
    "cleanup-old-messages": {
        "task": "src.integrations.celery_tasks.cleanup_old_messages",
        "schedule": crontab(hour=2, minute=0),
    },
    "health-check": {
        "task": "src.integrations.celery_tasks.health_check",
        "schedule": crontab(minute="*/5"),
    },
}


if __name__ == "__main__":
    # Start worker: celery -A src.integrations.celery_tasks worker --loglevel=info
    # Start beat: celery -A src.integrations.celery_tasks beat --loglevel=info
    # Or run both: celery -A src.integrations.celery_tasks worker --beat --loglevel=info
    celery_app.start()
