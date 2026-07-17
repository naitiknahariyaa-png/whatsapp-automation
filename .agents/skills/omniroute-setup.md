# OmniRoute AI Gateway Skill

## Purpose
Connect WhatsApp bot to 250+ AI providers through OmniRoute.

## What is OmniRoute?
Universal AI gateway - connects to 250+ providers, 90+ FREE!

## Quick Stats
| Feature | Value |
|---------|-------|
| Total Providers | 250+ |
| FREE Providers | 90+ |
| Free Tokens/Month | ~1.6B |
| Token Savings | 15-95% |
| Routing Strategies | 18 |

---

## Setup

### 1. Install OmniRoute
```bash
npm install -g omniroute
```

### 2. Start Server
```bash
omniroute start
```

### 3. Access Dashboard
```
http://localhost:20128
```

### 4. Add FREE Providers
```bash
# OpenRouter (100+ free models)
omniroute config add openrouter YOUR_KEY

# Groq (Fast & Free)
omniroute config add groq YOUR_KEY

# Get free keys:
# OpenRouter: https://openrouter.ai/keys
# Groq: https://console.groq.com/keys
```

### 5. Connect to WhatsApp Bot
```python
# In .env
OMNIROUTE_URL=http://localhost:20128

# In code
from src.integrations import OmniRouteClient

client = OmniRouteClient()
response = client.get_response("Hello!")
```

---

## FREE Providers (No Credit Card)

| Provider | Models | Website |
|----------|--------|---------|
| OpenRouter | 100+ | openrouter.ai |
| Groq | Llama, Mixtral | console.groq.com |
| Kiro AI | Multiple | kiro.ai |
| Pollinations | Multiple | pollinations.ai |
| Qoder | Multiple | qoder.ai |
| LongCat | Multiple | longcat.ai |

---

## Model Options

### Auto Modes (Recommended)
```python
# Best available model
response = client.get_response(msg, model="auto")

# Fastest response
response = client.get_response(msg, model="auto/fast")

# Cheapest tokens
response = client.get_response(msg, model="auto/cheap")

# Best for coding
response = client.get_response(msg, model="auto/coding")
```

### Specific Models
```python
# Claude
response = client.get_response(msg, model="anthropic/claude-3-haiku")

# GPT-4
response = client.get_response(msg, model="openai/gpt-4o-mini")

# Gemini
response = client.get_response(msg, model="google/gemini-2.0-flash")

# DeepSeek
response = client.get_response(msg, model="deepseek/deepseek-r1")

# Llama
response = client.get_response(msg, model="meta-llama/llama-3.1-8b-instruct")
```

---

## Routing Strategies (18 Total)

| Strategy | Description |
|----------|-------------|
| `auto` | Smart routing (recommended) |
| `priority` | Use first provider fully |
| `round-robin` | Cycle through providers |
| `cost-optimized` | Cheapest first |
| `headroom` | Most quota remaining |
| `weighted` | Random by weight |

---

## Streaming Responses

```python
# Get streaming response
for chunk in client.get_response_stream("Tell me a story"):
    print(chunk, end="", flush=True)
```

---

## Code Examples

### Basic Usage
```python
from src.integrations import OmniRouteClient

client = OmniRouteClient()

# Simple response
response = client.get_response("Hello!")
print(response)
```

### With System Prompt
```python
response = client.get_response(
    message="What are your prices?",
    model="auto",
    system_prompt="You are a helpful sales assistant for a shop."
)
```

### Batch Processing
```python
# Process multiple messages
messages = ["Hi", "Price?", "Order"]
for msg in messages:
    response = client.get_response(msg)
    print(f"{msg} -> {response}")
```

---

## Benefits for WhatsApp Bot

| Benefit | How it Helps |
|---------|-------------|
| Never hit limits | Auto-fallback to next provider |
| Save tokens | RTK + Caveman compression |
| FREE options | 90+ free providers |
| Fast responses | Groq is milliseconds |
| Multiple models | Claude, GPT, Gemini, etc. |

---

## Environment Variables

```bash
OMNIROUTE_URL=http://localhost:20128
OMNIROUTE_API_KEY= (optional)
```

---

## Troubleshooting

### OmniRoute not running?
```bash
npm install -g omniroute
omniroute start
```

### No providers configured?
```bash
omniroute config add openrouter YOUR_KEY
omniroute config add groq YOUR_KEY
```

### Check status
```python
client = OmniRouteClient()
print(client.get_status())
```

---

## More Info

- Website: https://omniroute.onl
- GitHub: https://github.com/diegosouzapw/OmniRoute
- Dashboard: http://localhost:20128
- Discord: https://discord.gg/omniroute

---

## Complete Flow

```
User Message → WhatsApp Bot → OmniRoute Client
                                    ↓
                           250+ Providers
                                    ↓
                           Auto-select best
                                    ↓
                           Return response
```

---

**OmniRoute = Never worry about AI limits again! 🚀**
