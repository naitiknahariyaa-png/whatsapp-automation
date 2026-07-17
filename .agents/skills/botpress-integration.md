# Botpress Integration Skill

## Purpose
Connect WhatsApp bot with Botpress for advanced chatbot flows.

## What is Botpress?
Open-source conversational AI platform with visual flow builder.

## Setup

### 1. Install Botpress
```bash
# Using Docker
docker run -d \
  -p 3000:3000 \
  -v botpress_data:/botpress/data \
  botpress/server
```

### 2. Create Bot
1. Open Botpress Studio
2. Create new bot
3. Add WhatsApp channel
4. Get Webhook URL

### 3. Connect to WhatsApp Bot
```python
# In webhook.py
import requests

BOTPRESS_URL = "https://your-botpress-server.com"
BOTPRESS_BOT_ID = "your-bot-id"

def send_to_botpress(message, user_id):
    """Send message to Botpress for processing"""
    response = requests.post(
        f"{BOTPRESS_URL}/api/bots/{BOTPRESS_BOT_ID}/messages",
        json={
            "userId": user_id,
            "message": message,
            "type": "text"
        }
    )
    return response.json()
```

## Features

| Feature | Description |
|---------|-------------|
| Visual Flow Builder | No-code chatbot design |
| AI NLU | Understand user intent |
| Multi-channel | WhatsApp, Web, Slack |
| Knowledge Base | AI-powered FAQ |
| Analytics | Conversation insights |

## Environment Variables
```
BOTPRESS_URL=https://your-botpress.com
BOTPRESS_BOT_ID=xxx
BOTPRESS_API_KEY=xxx
```

## Code Example
```python
from src.integrations.botpress import BotpressClient

bp = BotpressClient(
    url=os.getenv("BOTPRESS_URL"),
    bot_id=os.getenv("BOTPRESS_BOT_ID")
)

# Process message through Botpress
response = bp.send_message(
    user_id="whatsapp-user-123",
    message="I want to order pizza"
)

# Send Botpress response back to WhatsApp
whatsapp.send_message(response["text"])
```

## Advanced: Use Botpress as AI Brain
```python
# Replace AIManager with Botpress
from src.integrations.botpress import BotpressAI

ai = BotpressAI(bot_id="whatsapp-brain-bot")
response = ai.think("Customer asked about pricing")
```

## More Info
- Website: https://botpress.com
- GitHub: https://github.com/botpress/botpress
