# AI Setup Skill

## Purpose
Configure AI providers for smart auto-replies.

## Available AI Providers

| Provider | Cost | Speed | Quality |
|----------|------|-------|---------|
| OpenRouter | FREE | Medium | Good |
| Groq | FREE | Fast | Good |
| Keyword | FREE | Instant | Basic |

---

## OpenRouter Setup (RECOMMENDED)

### Get API Key
1. Go to: https://openrouter.ai/keys
2. Sign up (free)
3. Click "Create Key"
4. Copy the key

### Configure
```bash
# Add to .env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
```

### Free Models Available
```
- google/gemini-2.0-flash-thinking-exp-01-21
- anthropic/claude-3-haiku
- openai/chatgpt-4o-mini
- meta-llama/llama-3.1-8b-instruct
```

### Test
```python
from src.ai.providers import AIManager

ai = AIManager()
ai.configure("openrouter", "your-key", "openrouter/free")
response = ai.get_response("Hello!")
print(response)
```

---

## Groq Setup

### Get API Key
1. Go to: https://console.groq.com/keys
2. Sign up (free)
3. Click "Create API Key"
4. Copy the key

### Configure
```bash
# Add to .env
GROQ_API_KEY=gsk_xxxxxxxxxxxx
```

### Free Models
```
- llama-3.1-8b-instant
- llama-3.2-1b-preview
- mixtral-8x7b-32768
```

### Test
```python
from src.ai.providers import AIManager

ai = AIManager()
ai.configure("groq", "your-key", "llama-3.1-8b-instant")
response = ai.get_response("Hello!")
print(response)
```

---

## Keyword AI (No API Needed)

Works without any API key - matches keywords to responses.

### Add Keywords
```python
from src.core.database import get_database

db = get_database()
db.add_keyword("hello", "Hi! How can I help?")
db.add_keyword("price", "Our prices are very competitive!")
db.add_keyword("hours", "We are open 9 AM - 9 PM")
```

### Configure
```bash
# No API key needed
# Just set in main.py menu option 3
```

---

## AI Provider Priority

The bot checks providers in this order:
1. OpenRouter (if key provided)
2. Groq (if key provided)
3. Keyword (fallback, no key needed)

---

## Change AI Model

### Via Code
```python
ai.configure("openrouter", "key", "openai/chatgpt-4o-mini")
```

### Via .env
```python
# In config
ai:
  model: openai/chatgpt-4o-mini
```

---

## Troubleshooting

### AI Not Responding
```
1. Check API key is correct
2. Check API key has credits
3. Check internet connection
4. Try different model
```

### Slow Responses
```
1. Use Groq (fastest)
2. Use smaller models
3. Check network latency
```

### "Invalid API Key"
```
1. Get new key from provider
2. Make sure no spaces in key
3. Check key hasn't expired
```

---

## Environment Variables

| Variable | For Provider |
|----------|--------------|
| OPENROUTER_API_KEY | OpenRouter AI |
| GROQ_API_KEY | Groq AI |

---

## Test All Providers

```python
from src.ai.providers import AIManager

ai = AIManager()
print(ai.get_status())

# Test each provider
ai.configure("keyword")
print(ai.get_response("hello"))

ai.configure("openrouter", "key", "openrouter/free")
print(ai.get_response("hello"))
```
