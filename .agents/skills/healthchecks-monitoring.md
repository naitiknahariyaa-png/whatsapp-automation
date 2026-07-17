# Healthchecks Monitoring Skill

## Purpose
Use Healthchecks for monitoring and alerts when bot is down.

## What is Healthchecks?
Cron job monitoring service - alerts when checks miss.

## Setup

### 1. Self-Host Healthchecks (or use cloud)
```bash
# Using Docker
docker run -d \
  -p 8000:8000 \
  -v hc_data:/data \
  healthchecks/checks
```

### 2. Create Check
1. Go to Healthchecks dashboard
2. Create new check: "whatsapp-bot-heartbeat"
3. Copy the ping URL

### 3. Add to Bot
```python
# In main.py or webhook.py
import requests
import time

HEALTHCHECKS_URL = "https://your-healthchecks.com/ping/xxx"

def send_heartbeat():
    """Send heartbeat to Healthchecks"""
    try:
        requests.get(HEALTHCHECKS_URL, timeout=5)
    except:
        pass

def start_heartbeat_thread():
    """Send heartbeat every 5 minutes"""
    import threading
    def loop():
        while True:
            send_heartbeat()
            time.sleep(300)  # 5 minutes
    threading.Thread(target=loop, daemon=True).start()
```

## Environment Variables
```
HEALTHCHECKS_PING_URL=https://hc-ping.com/xxx
HEALTHCHECKS_API_KEY=xxx
```

## Features

| Feature | Description |
|---------|-------------|
| Heartbeat | Regular "I'm alive" pings |
| Cron Monitoring | Track scheduled tasks |
| Failure Alerts | Email/Slack/PagerDuty |
| Uptime Reports | Monthly uptime % |

## Code Integration
```python
# In webhook.py health endpoint
@app.get("/health")
async def health_check():
    # Send heartbeat
    try:
        requests.get(f"{HEALTHCHECKS_URL}/start", timeout=3)
    except:
        pass
    
    return {"status": "ok"}

# Or send pings manually
from src.monitoring.healthchecks import HealthchecksMonitor

monitor = HealthchecksMonitor(ping_url=HEALTHCHECKS_URL)

# On success
monitor.ping("✅ Bot running")

# On failure
monitor.ping_fail("❌ Bot crashed")
```

## Failure Alert Channels
- Email
- Slack
- Discord
- Telegram (like your bot!)
- PagerDuty
- Webhooks

## More Info
- Cloud: https://healthchecks.io
- Self-hosted: https://github.com/healthchecks/healthchecks
