---
name: openwa-gateway
description: OpenWA is a free, open-source WhatsApp API gateway that provides a REST API to send/receive messages, manage sessions, and integrate with AI agents. Use this skill when setting up WhatsApp automation, configuring webhooks, or integrating WhatsApp with other services.
trigger phrases: ["openwa", "whatsapp gateway", "whatsapp api", "setup whatsapp", "whatsapp integration"]
tags: [whatsapp, gateway, api, automation, messaging]
complexity: medium
cost: free
self-hosted: true
---

# OpenWA Gateway Skill

## Overview

**OpenWA** (formerly whatsapp-web.js based gateway) is a free, open-source WhatsApp API that provides production-grade stability for WhatsApp automation.

### Key Features

- ✅ **REST API** - Easy HTTP endpoints for all operations
- ✅ **Multi-session** - Run 500+ WhatsApp accounts
- ✅ **Webhooks** - Receive incoming messages in real-time
- ✅ **MCP Server** - AI agent integration ready
- ✅ **Dashboard** - No-code session management
- ✅ **100% Free** - MIT License, no hidden costs

## Quick Start

### 1. Start with Docker

```bash
docker run -d \
  --name openwa \
  -p 3000:3000 \
  -p 3001:3001 \
  waha/waha:latest
```

### 2. Get API Key

1. Open http://localhost:3000
2. Go to Settings → API
3. Copy your API key

### 3. Connect WhatsApp

1. Open Dashboard at http://localhost:3000
2. Click "Start" to scan QR code
3. Wait for "Connected" status

### 4. Send Message

```bash
curl -X POST http://localhost:3000/api/messages/sendText \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session": "default",
    "chatId": "919876543210@c.us",
    "text": "Hello from OpenWA!"
  }'
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3000 | HTTP server port |
| `API_KEY` | - | Required for API access |
| `WEBHOOK_URL` | - | Receive incoming messages |
| `LOG_LEVEL` | info | Logging verbosity |

### Docker Compose

```yaml
services:
  openwa:
    image: waha/waha:latest
    ports:
      - "3000:3000"  # API
      - "3001:3001"  # Dashboard
    environment:
      - WHATSAPP_SESSION=default
    volumes:
      - ./data:/data
```

## API Reference

### Send Message

```http
POST /api/messages/sendText
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| session | string | Yes | Session name |
| chatId | string | Yes | Phone number with @c.us |
| text | string | Yes | Message content |

### Send Media

```http
POST /api/messages/sendFile
```

```json
{
  "session": "default",
  "chatId": "919876543210@c.us",
  "fileUrl": "https://example.com/image.jpg",
  "caption": "Check this out!"
}
```

### Get Messages

```http
GET /api/messages?session=default&limit=50
```

### Webhook Setup

Set webhook in OpenWA settings:
```
http://your-server:8000/webhook
```

Webhook receives JSON:
```json
{
  "event": "message",
  "session": "default",
  "payload": {
    "from": "919876543210@c.us",
    "message": {
      "conversation": "Hello!"
    }
  }
}
```

## Python Integration

```python
import requests

OPENWA_URL = "http://localhost:3000"
API_KEY = "your-api-key"

def send_message(phone, text):
    response = requests.post(
        f"{OPENWA_URL}/api/messages/sendText",
        headers={"X-API-Key": API_KEY},
        json={
            "session": "default",
            "chatId": f"{phone}@c.us",
            "text": text
        }
    )
    return response.status_code == 200
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code not loading | Clear browser cache, use Chrome |
| Session disconnected | Restart container, re-scan QR |
| API returns 401 | Check API key is correct |
| Webhook not working | Verify URL is publicly accessible |

## Alternatives

If OpenWA doesn't work for you, try:
- **WAHA** - Simpler setup, different engine
- **Evolution API** - Feature-rich, active development
- **ChatWoot** - Full customer support platform

## Next Steps

- Set up webhook for auto-replies
- Integrate with AI for smart responses
- Add multiple WhatsApp sessions
- Configure media handling
