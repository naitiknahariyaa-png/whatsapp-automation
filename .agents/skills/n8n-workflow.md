# N8N Workflow Automation Skill

## Purpose
Connect WhatsApp bot with N8N for powerful automations.

## What is N8N?
Workflow automation tool - connect apps, automate tasks.

## Setup

### 1. Install N8N
```bash
# Using Docker
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

### 2. Create Webhook in N8N
1. Open N8N Studio (http://localhost:5678)
2. Create new workflow
3. Add "Webhook" node
4. Copy webhook URL

### 3. Connect to WhatsApp
```python
# In webhook.py or reply_engine.py
import requests

N8N_WEBHOOK_URL = "https://your-n8n-server/webhook/whatsapp"

def trigger_n8n_workflow(message_data):
    """Trigger N8N automation"""
    response = requests.post(
        N8N_WEBHOOK_URL,
        json={
            "message": message_data["text"],
            "sender": message_data["sender"],
            "timestamp": message_data["timestamp"],
            "source": "whatsapp"
        }
    )
    return response.json()
```

## Popular N8N Workflows

### CRM Integration
```
WhatsApp → N8N → Create HubSpot Lead
              ↓
           Send confirmation back
```

### Email Automation
```
WhatsApp → N8N → Send Email via Gmail
              ↓
           Save to Google Sheets
```

### Calendar Booking
```
WhatsApp → N8N → Check Google Calendar
              ↓
           Book slot → Send confirmation
```

### Order Processing
```
WhatsApp → N8N → Create WooCommerce Order
              ↓
           Send invoice via Email
```

## Features

| Feature | Description |
|---------|-------------|
| 400+ Integrations | Google, Slack, CRM |
| Code Nodes | Run JavaScript/Python |
| Conditional Logic | Branch workflows |
| Loops | Process arrays |
| Error Handling | Retry failed tasks |

## Environment Variables
```
N8N_WEBHOOK_URL=https://n8n.yoursite.com/webhook/xxx
N8N_API_KEY=xxx
```

## Code Example
```python
from src.integrations.n8n import N8NClient

n8n = N8NClient(
    webhook_url=os.getenv("N8N_WEBHOOK_URL")
)

# Trigger on new message
async def on_message(sender, message):
    # Trigger N8N workflow
    result = await n8n.trigger({
        "event": "new_message",
        "sender": sender,
        "message": message
    })
    
    # Send N8N response back
    if result.get("response"):
        return result["response"]
```

## More Info
- Website: https://n8n.io
- GitHub: https://github.com/n8n-io/n8n
