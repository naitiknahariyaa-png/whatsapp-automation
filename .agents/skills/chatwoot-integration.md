# Chatwoot Integration Skill

## Purpose
Integrate WhatsApp bot with Chatwoot for unified customer inbox.

## What is Chatwoot?
Open-source customer engagement suite - combines WhatsApp, email, chat in one inbox.

## Setup

### 1. Install Chatwoot
```bash
# Using Docker (recommended)
docker run -d \
  -p 3000:3000 \
  -v chatwoot-docker:/var/lib/chatwoot \
  chatwoot/chatwoot
```

### 2. Create WhatsApp Channel
1. Go to Chatwoot Dashboard
2. Settings → Inboxes → Add Inbox
3. Select WhatsApp
4. Get Webhook URL for WhatsApp

### 3. Connect to WhatsApp Bot
```python
# Add to webhook.py
import requests

CHATWOOT_API_URL = "https://your-chatwoot-server.com"
CHATWOOT_API_TOKEN = "your-api-token"

def send_to_chatwoot(conversation_id, message):
    """Forward WhatsApp message to Chatwoot"""
    response = requests.post(
        f"{CHATWOOT_API_URL}/api/v1/conversations/{conversation_id}/messages",
        headers={"api_access_token": CHATWOOT_API_TOKEN},
        json={"content": message, "message_type": "incoming"}
    )
    return response.json()
```

## Features

| Feature | Description |
|---------|-------------|
| Unified Inbox | All messages in one place |
| Team Management | Assign conversations |
| Canned Responses | Quick reply templates |
| Analytics | Track response times |
| WhatsApp + Web Chat | Multiple channels |

## Environment Variables
```
CHATWOOT_API_URL=https://app.chatwoot.com
CHATWOOT_API_TOKEN=xxx
CHATWOOT_INBOX_ID=1
```

## Code Example
```python
from src.integrations.chatwoot import ChatwootClient

cw = ChatwootClient(
    api_url=os.getenv("CHATWOOT_API_URL"),
    api_token=os.getenv("CHATWOOT_API_TOKEN")
)

# Forward message
cw.create_message(
    inbox_id=1,
    content="Customer inquiry",
    message_type="incoming"
)
```

## More Info
- Website: https://www.chatwoot.com
- GitHub: https://github.com/chatwoot/chatwoot
