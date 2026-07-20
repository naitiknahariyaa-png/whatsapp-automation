---
name: groq-ai
description: Groq provides free, ultra-fast AI inference with models like Llama-3.1. Use for AI auto-replies, smart responses, and natural language processing in WhatsApp automation.
trigger phrases: ["groq", "free ai", "fast ai", "llama", "ai inference"]
tags: [ai, llm, free, fast, inference]
complexity: low
cost: free
self-hosted: false
---

# Groq AI Skill

## Overview

**Groq** provides free, extremely fast AI inference - perfect for WhatsApp auto-replies.

### Why Groq?

- ✅ **14,400 requests/day FREE**
- ✅ **~300 tokens/second** - Instant responses
- ✅ **No credit card required**
- ✅ **Llama 3.1 models** - High quality

## Setup

### 1. Get API Key

1. Go to https://console.groq.com
2. Sign up (free)
3. Create API key
4. Add to `.env`:
   ```
   GROQ_API_KEY=gsk_xxxx
   ```

### 2. Install Client

```bash
pip install groq
```

### 3. Python Usage

```python
from groq import Groq

client = Groq(api_key="your-key")

chat = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Keep responses SHORT."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    max_tokens=150
)

print(chat.choices[0].message.content)
```

## Available Models

| Model | Speed | Best For |
|-------|-------|----------|
| `llama-3.1-8b-instant` | Fastest | Auto-replies |
| `llama-3.1-70b-versatile` | Fast | Complex queries |
| `mixtral-8x7b-32768` | Fast | Balanced |

## In WhatsApp Hub

```python
GROQ_API_KEY=your-key  # In .env

# Auto-enabled in AIEngine
response, source = ai.get_response("Hello!")
# source = "ai" if using Groq
```

## Rate Limits

| Plan | Requests | Tokens/min |
|------|----------|------------|
| Free | 14,400/day | 30/min |
| Paid | Unlimited | 600/min |

## Tips

- Keep prompts SHORT for faster responses
- Use templates for common queries first
- Groq fallback to templates if rate limited

## Alternatives

If Groq unavailable:
- **OpenAI** - Paid, more models
- **Gemini** - Free tier available
- **Ollama** - Run locally, free
