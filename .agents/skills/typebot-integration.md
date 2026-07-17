# Typebot Integration Skill

## Purpose
Add interactive forms/flows from Typebot to WhatsApp.

## What is Typebot?
Open-source form builder with conversational flows.

## Setup

### 1. Install Typebot
```bash
# Using Docker
docker run -d \
  -p 3000:3000 \
  -e DATABASE_URL=file:///db \
  -v typebot_data:/db \
  botpress/typebot
```

### 2. Create Form in Typebot
1. Go to Typebot Studio
2. Create quiz/form/chatflow
3. Publish and get Public ID
4. Get webhook URL

### 3. Connect to WhatsApp
```python
# In reply_engine.py
import requests

TYPEBOT_URL = "https://your-typebot.com"
TYPEBOT_PUBLIC_ID = "your-form-id"

def get_typebot_response(session_id, message, user_answer=None):
    """Get next question from Typebot"""
    response = requests.post(
        f"{TYPEBOT_URL}/api/v1/sessions/{session_id}/continue",
        json={
            "message": user_answer or message,
            "type": "text"
        }
    )
    return response.json()
```

## Features

| Feature | Description |
|---------|-------------|
| Visual Builder | Drag-drop forms |
| Conditional Logic | Branch based on answers |
| Calculate | Math in forms |
| File Upload | Collect documents |
| Payments | Stripe integration |

## Use Cases

### Lead Collection
```
WhatsApp → "Hi!" → Typebot Form → "What's your name?" → Save to DB
```

### Order Taking
```
WhatsApp → "Order" → Typebot Quiz → Items + Address → Create Order
```

### Appointment Booking
```
WhatsApp → "Book" → Typebot → Select Date/Time → Confirm Booking
```

## Environment Variables
```
TYPEBOT_URL=https://typebot.yoursite.com
TYPEBOT_PUBLIC_ID=abc123
TYPEBOT_API_KEY=xxx
```

## More Info
- Website: https://typebot.io
- GitHub: https://github.com/baptisteArno/typebot.io
