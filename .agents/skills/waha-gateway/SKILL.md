---
name: waha-gateway
description: WAHA (WhatsApp HTTP API) is an alternative open-source WhatsApp gateway with multiple engine options (Baileys, websocket.js). Use when you need simpler setup than OpenWA or want different underlying engine.
trigger phrases: ["waha", "whatsapp http api", "alternative whatsapp gateway"]
tags: [whatsapp, gateway, alternative, baileys]
complexity: medium
cost: free
self-hosted: true
---

# WAHA Gateway Skill

## Overview

**WAHA** (WhatsApp HTTP API) is an alternative WhatsApp gateway that supports multiple underlying engines.

### Key Features

- ✅ **Multiple Engines** - Baileys, websocket.js, etc.
- ✅ **Simple Setup** - Quick to get started
- ✅ **REST API** - Standard HTTP endpoints
- ✅ **Webhook Support** - Real-time message handling
- ✅ **Free & Open Source**

## Quick Start

### Docker Setup

```bash
docker run -d \
  --name waha \
  -p 3000:3000 \
  -e WHATSAPP_SESSION=default \
  devnulllabs/waha:latest
```

### Dashboard

Access at: http://localhost:3000

## API Endpoints

### Send Message

```bash
curl -X POST http://localhost:3000/api/sendText \
  -H "Content-Type: application/json" \
  -d '{
    "chatId": "919876543210@c.us",
    "message": "Hello!"
  }'
```

### Get Status

```bash
curl http://localhost:3000/api/status
```

## Python Integration

```python
import requests

WAHA_URL = "http://localhost:3000"

def send(phone, text):
    return requests.post(
        f"{WAHA_URL}/api/sendText",
        json={"chatId": f"{phone}@c.us", "message": text}
    ).ok
```

## When to Use WAHA vs OpenWA

| Feature | OpenWA | WAHA |
|---------|--------|------|
| Engine | whatsapp-web.js | Multiple options |
| Setup Complexity | Medium | Easy |
| Dashboard | Good | Basic |
| MCP Server | Yes | No |
| Active Development | High | Medium |

Choose **WAHA** if you want simpler setup.
Choose **OpenWA** if you need MCP integration.
