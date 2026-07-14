# 🚀 Advanced Features Guide

## WhatsApp AI Automation Tool - Advanced Capabilities

---

## 1. 🤖 Multi-Provider AI System

### Switching Between AI Providers

The tool supports multiple AI providers with automatic fallback:

```python
# In config.yaml, set your provider:
ai:
  provider: "ollama"  # or openai, claude, gemini, deepseek
```

### Provider Comparison

| Provider | Cost | Privacy | Quality | Setup |
|----------|------|---------|--------|-------|
| **Ollama** | Free | High | Good | Local |
| **OpenAI** | Paid | Low | Excellent | API Key |
| **Claude** | Paid | Low | Excellent | API Key |
| **Gemini** | Free tier | Low | Good | API Key |
| **DeepSeek** | Cheap | Low | Good | API Key |

### Using Ollama (Recommended)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3.2:latest    # English
ollama pull qwen2.5:7b          # Multilingual
ollama pull mistral:latest      # Fast

# Start server
ollama serve

# Check available models
ollama list
```

---

## 2. 🎭 Multi-Personality Bot System

### Creating Custom Personalities

Edit `config.yaml`:

```yaml
personalities:
  # Default friendly assistant
  friendly:
    name: "Buddy"
    greeting: "Hey! What's up? 😊"
    tone: "casual"
    system_prompt: "You are a friendly, casual assistant."
    
  # Professional business bot
  business:
    name: "Assistant"
    greeting: "Good day. How may I assist you?"
    tone: "formal"
    system_prompt: "You are a professional business assistant."
    
  # Technical support bot
  support:
    name: "Tech Helper"
    greeting: "Hello! I'm here to help with technical issues."
    tone: "helpful"
    system_prompt: "You are a technical support specialist."
```

### Assigning Personalities to Contacts

```python
# In your code:
from src.core.database import Database

db = Database()
db.update_contact("John", personality="business")
db.update_contact("Mike", personality="support")
```

---

## 3. ⏰ Scheduled Messages

### Setting Up Scheduled Messages

```yaml
scheduled_messages:
  # Morning greeting
  - time: "09:00"
    message: "Good morning! We're now open. How can we help you today? 🌟"
    enabled: true
    
  # Evening closing
  - time: "21:00"
    message: "We're closing for today. Thanks for visiting! 👋"
    enabled: true
    
  # Weekly promotion
  - time: "10:00"
    day: "monday"
    message: "Happy Monday! This week only: 20% off!"
    enabled: true
```

### Programmatic Scheduling

```python
from src.core.database import Database

db = Database()

# Add a scheduled message
db.add_scheduled_message(
    message="Thanks for your order! Your delivery is on the way! 📦",
    scheduled_time="14:00",
    contact_name="Customer123",
    is_recurring=False
)

# Add recurring message
db.add_scheduled_message(
    message="Reminder: Your appointment is tomorrow at 10 AM ⏰",
    scheduled_time="18:00",
    is_recurring=True,
    recurrence_pattern="daily"
)
```

---

## 4. 🧠 Conversation Memory

### How It Works

The bot remembers the last N messages in each conversation:

```yaml
advanced:
  memory_enabled: true
  memory_limit: 10  # Remember last 10 exchanges
```

### Memory Features

- **Context Awareness**: Understands conversation flow
- **Personalization**: Remembers user preferences
- **Continuity**: Doesn't forget what was discussed

### Customizing Memory

```python
# In reply_engine.py, the memory stores:
{
    "John": [
        {"sender": "user", "content": "I want to order pizza", "time": "10:00"},
        {"sender": "bot", "content": "What toppings would you like?", "time": "10:00"},
        {"sender": "user", "content": "Extra cheese", "time": "10:01"},
        # ...
    ]
}
```

---

## 5. 📊 Analytics Dashboard

### Built-in Statistics

The dashboard tracks:
- Total messages received
- Auto-replies sent
- Unique contacts
- Peak activity times
- Response times

### Accessing Stats

```bash
python main.py --status
```

### Custom Analytics

```python
from src.core.database import Database

db = Database()

# Get comprehensive stats
stats = db.get_statistics()
print(f"Total messages: {stats['total_messages']}")
print(f"Auto-replied: {stats['auto_replied']}")

# Get contact activity
contacts = db.get_contacts()
for contact in contacts:
    print(f"{contact['name']}: {contact['message_count']} messages")

# Get message history
messages = db.get_messages(limit=100, contact="John")
```

---

## 6. 🔍 Intent Detection

### Automatic Intent Recognition

The bot automatically detects user intent:

```python
# Detected intents:
- greeting: "hi", "hello", "hey"
- goodbye: "bye", "tata"
- question: "?", "what", "how"
- order: "buy", "order", "purchase"
- price: "price", "cost", "how much"
- support: "help", "issue", "problem"
```

### Sentiment Analysis

```yaml
advanced:
  sentiment_analysis: true
```

The bot detects:
- **Positive**: Happy, satisfied customers
- **Negative**: Upset, frustrated customers
- **Neutral**: Normal inquiries

---

## 7. 🌐 Multi-Language Support

### Supported Languages

The AI models support:
- English (best)
- Hindi (with Qwen/LLaMA models)
- Spanish
- And many more...

### Configuration

```yaml
ai:
  ollama:
    model: "qwen2.5:7b"  # Great for multilingual
    
  system_prompt: |
    You are a helpful assistant that can respond in both English and Hindi.
    Match the language the user is using.
```

### Example Conversations

```
User: "नमस्ते" (Hindi)
Bot: "नमस्ते! मैं आपकी कैसे मदद कर सकता हूं?" (Hindi response)

User: "Hello"
Bot: "Hi! How can I help you today?" (English response)
```

---

## 8. 🔗 Integration Capabilities

### Webhook Integration

Receive events from external services:

```python
# Send data when auto-reply is triggered
import requests

webhook_url = "https://your-webhook.com/endpoint"

def on_auto_reply(sender, message, response):
    requests.post(webhook_url, json={
        "event": "auto_reply",
        "sender": sender,
        "message": message,
        "response": response,
        "timestamp": datetime.now().isoformat()
    })
```

### API for External Control

```python
# Expose control via REST API
from fastapi import FastAPI

app = FastAPI()

@app.post("/send-message")
def send_message(contact: str, message: str):
    whatsapp.send_message(message, contact)
    return {"status": "sent"}

@app.post("/add-keyword")
def add_keyword(keyword: str, response: str):
    reply_engine.add_keyword(keyword, response)
    return {"status": "added"}
```

---

## 9. 🔒 Security Features

### Rate Limiting

```yaml
security:
  rate_limit: true
  max_messages_per_minute: 10
```

### Contact Blacklist/Whitelist

```python
# Block specific contacts
db.update_contact("Spammer123", is_blacklisted=True)

# Only reply to specific contacts
config['contacts']['whitelist'] = ["Friend1", "Family", "Customer123"]
```

### Session Encryption

```yaml
security:
  encrypt_sessions: true
```

---

## 10. 📱 Mobile App Ready

### REST API Endpoints

```python
# Mobile app can control the bot
@app.get("/status")
def get_status():
    return {
        "bot_online": True,
        "messages_today": 150,
        "ai_provider": "ollama"
    }

@app.get("/messages")
def get_recent_messages(limit: int = 50):
    return db.get_messages(limit)

@app.post("/trigger-reply")
def trigger_manual_reply(contact: str, message: str):
    response = reply_engine.get_reply(message, ai_router)
    whatsapp.send_message(response, contact)
    return {"sent": True}
```

---

## 11. 🚀 Performance Optimization

### Async Operations

```python
import asyncio

async def process_messages():
    messages = await whatsapp.get_new_messages_async()
    tasks = [reply_engine.get_reply_async(msg) for msg in messages]
    responses = await asyncio.gather(*tasks)
    return responses
```

### Caching Responses

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(message_hash):
    # Cache common responses
    return generate_response(message_hash)
```

---

## 12. 🎨 Customization Options

### Custom Auto-Reply Rules

```yaml
auto_reply:
  keywords:
    - keyword: "order"
      response: "To place an order, please visit: example.com/order"
      priority: 10  # Higher = checked first
      
    - keyword: "complaint"
      response: "I'm sorry to hear that. Please share more details."
      priority: 5
```

### Dynamic Responses

```python
def get_dynamic_response(keyword, context):
    responses = {
        "hours": f"We're open {get_current_hours()}",
        "price": f"Current prices: {get_prices()}",
        "location": f"We're at: {get_address()}"
    }
    return responses.get(keyword, "Please contact us for more info.")
```

---

## 📚 Advanced Code Examples

### Custom AI Response Handler

```python
class CustomAIHandler:
    def __init__(self, router):
        self.router = router
        
    def generate_smart_response(self, message, sender):
        # Add custom logic
        if self.is_urgent(message):
            return self.handle_urgent(message, sender)
        
        if self.is_order(message):
            return self.handle_order(message, sender)
            
        # Fallback to AI
        return self.router.generate_response(message, sender=sender)
        
    def is_urgent(self, message):
        urgent_keywords = ["emergency", "asap", "urgent", "immediately"]
        return any(kw in message.lower() for kw in urgent_keywords)
        
    def handle_urgent(self, message, sender):
        # Alert the human
        self.send_alert(f"URGENT from {sender}: {message}")
        return "I'll alert the team immediately! Someone will contact you soon."
```

### Adding New AI Provider

```python
# In src/ai/providers.py

class CustomAIProvider(BaseProvider):
    """Custom AI provider integration"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'custom-model')
        
    def check_connection(self):
        # Test API connection
        return True
        
    def generate(self, message, context=None, sender=None, **kwargs):
        # Implement API call
        response = self.call_api(message, context)
        return response
        
    def call_api(self, message, context):
        # Your API integration logic
        pass
```

---

## 🎯 Quick Start: Advanced Features

1. **Start with basics**: Keyword auto-reply
2. **Add AI**: Setup Ollama for smart responses
3. **Personalize**: Create bot personalities
4. **Automate**: Add scheduled messages
5. **Scale**: Use multiple providers

---

**Need help with any advanced feature? Just ask! 🚀**
