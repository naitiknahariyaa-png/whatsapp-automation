---
name: healthchecks-monitoring
description: Healthchecks.io integration for monitoring WhatsApp Hub uptime and receiving alerts when the service goes down. Use for production monitoring and reliability assurance.
trigger phrases: ["healthcheck", "uptime", "monitoring", "alerts", "reliability"]
tags: [monitoring, uptime, alerts, healthcheck, production]
complexity: low
cost: free
self-hosted: false
---

# Healthchecks Monitoring Skill

## Overview

Monitor WhatsApp Hub uptime with free healthchecks service.

## Setup

### 1. Create Account

1. Go to https://healthchecks.io
2. Create free account
3. Add new check
4. Copy the ping URL

### 2. Add to Docker

```bash
docker run -d \
  --name whatsapp-hub \
  -p 8000:8000 \
  -e HEALTHCHECK_URL=https://hc-ping.com/your-uuid \
  whatsapp-hub
```

### 3. Or Add to Code

```python
import requests

HEALTHCHECK_URL = "https://hc-ping.com/your-uuid"

def ping_health():
    try:
        requests.get(HEALTHCHECK_URL + "/start")
    except:
        pass

def ping_success():
    try:
        requests.get(HEALTHCHECK_URL)
    except:
        pass

def ping_fail():
    try:
        requests.get(HEALTHCHECK_URL + "/fail")
    except:
        pass
```

## Why Use Healthchecks?

- ✅ **Free** for 20 checks
- ✅ **Email alerts** when down
- ✅ **Simple API** - Just ping URLs
- ✅ **Dashboard** - See all services

## Alternative: UptimeRobot

- Free tier: 50 monitors
- Dashboard: https://uptimerobot.com

## Alternative: Cronitor

- Free tier: 1 monitor
- Dashboard: https://cronitor.io
