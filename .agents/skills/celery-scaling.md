# Celery Task Queue Skill

## Purpose
Handle 10,000+ users with async task processing.

## What is Celery?
Distributed task queue - process messages in background workers.

## Setup

### 1. Install
```bash
pip install celery[redis]
```

### 2. Install Redis (message broker)
```bash
docker run -d -p 6379:6379 redis
```

### 3. Create Tasks
```python
# tasks.py
from celery import Celery

celery_app = Celery(
    "whatsapp_bot",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def process_whatsapp_message(sender, message):
    """Process message in background"""
    from src.core.reply_engine import ReplyEngine
    
    engine = ReplyEngine()
    response = engine.process_message(sender, message)
    
    # Send response
    from src.core.whatsapp_client import WhatsAppClient
    client = WhatsAppClient()
    client.send_message(sender, response)
    
    return {"status": "sent", "response": response}

@celery_app.task
def send_scheduled_bulk_message(numbers, message):
    """Send bulk message to many users"""
    from src.core.whatsapp_client import WhatsAppClient
    client = WhatsAppClient()
    
    results = []
    for number in numbers:
        try:
            client.send_message(number, message)
            results.append({"number": number, "status": "sent"})
        except Exception as e:
            results.append({"number": number, "status": "failed", "error": str(e)})
    
    return {"total": len(numbers), "results": results}

@celery_app.task
def cleanup_old_messages():
    """Scheduled cleanup task"""
    from src.core.database import get_database
    db = get_database()
    db.cleanup_old_messages(days=30)
    return {"cleaned": True}
```

### 4. Start Workers
```bash
# Start worker
celery -A tasks worker --loglevel=info

# Start multiple workers for scale
celery -A tasks worker --loglevel=info --concurrency=10

# Start with systemd
celery -A tasks worker --detach --logfile=/var/log/celery.log
```

### 5. Use in Bot
```python
# In webhook.py or whatsapp_client.py
from tasks import process_whatsapp_message

def on_message(sender, message):
    # Queue message for processing
    task = process_whatsapp_message.delay(sender, message)
    
    # Or schedule for later
    from datetime import timedelta
    process_whatsapp_message.apply_async(
        args=[sender, message],
        countdown=60  # Process after 60 seconds
    )
    
    return "Processing your message..."

# Check task status
task_id = task.id
task_result = process_whatsapp_message.AsyncResult(task_id)
print(task_result.state)  # PENDING, SUCCESS, FAILURE
```

## Scaling to 10k Users

```bash
# Start multiple workers on multiple machines
celery -A tasks worker --concurrency=100 --hostname=worker1@%h
celery -A tasks worker --concurrency=100 --hostname=worker2@%h
celery -A tasks worker --concurrency=100 --hostname=worker3@%h
```

## Scheduled Tasks
```python
# In celery.py
@celery_app.task
def daily_summary():
    """Send daily summary to admin"""
    pass

# Schedule with celery beat
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Send daily summary at 9 AM
    sender.add_periodic_task(
        crontab(hour=9, minute=0),
        daily_summary.s(),
    )
    
    # Cleanup every night at 2 AM
    sender.add_periodic_task(
        crontab(hour=2, minute=0),
        cleanup_old_messages.s(),
    )
```

## Features

| Feature | Description |
|---------|-------------|
| Async Processing | Don't block main thread |
| Task Scheduling | Run tasks later |
| Retry Failed | Auto-retry on error |
| Rate Limiting | Control speed |
| Monitoring | Flower dashboard |

## Environment Variables
```
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Monitoring with Flower
```bash
pip install flower
celery -A tasks flower --port=5555
# Open http://localhost:5555
```

## More Info
- Website: https://docs.celeryproject.io
- GitHub: https://github.com/celery/celery
