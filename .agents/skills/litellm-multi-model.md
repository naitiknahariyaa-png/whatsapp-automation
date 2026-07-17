# LiteLLM Multi-Model Router Skill

## Purpose
Use 100+ AI models through single API - OpenRouter, OpenAI, Azure, local models.

## What is LiteLLM?
Proxy server that routes to any LLM - unified API for all models.

## Setup

### 1. Install LiteLLM
```bash
pip install litellm
```

### 2. Configure Models
```bash
# Create config.yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: gpt-4
      api_key: os.environ/openai-api-key

  - model_name: claude-3
    litellm_params:
      model: claude-3-haiku-20240307
      api_key: os.environ/anthropic-api-key

  - model_name: local-llama
    litellm_params:
      model: ollama/llama3.2
      api_base: http://localhost:11434

  - model_name: openrouter-free
    litellm_params:
      model: openrouter/google/gemini-2.0-flash-thinking-exp-01-21
      api_key: os.environ/openrouter-api-key
```

### 3. Start Proxy
```bash
litellm --config config.yaml --port 8000
```

### 4. Connect to WhatsApp Bot
```python
# In providers.py
import requests

LITELLM_URL = "http://localhost:8000"

class LiteLLMAI:
    """Multi-model AI router"""
    
    def __init__(self, api_base=LITELLM_URL):
        self.api_base = api_base
    
    def get_response(self, message, model="openrouter-free"):
        """Get response from any model"""
        response = requests.post(
            f"{self.api_base}/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": message}
                ]
            },
            timeout=60
        )
        
        return response.json()["choices"][0]["message"]["content"]
    
    def get_models(self):
        """List available models"""
        r = requests.get(f"{self.api_base}/models")
        return r.json()

# Usage
ai = LiteLLMAI()

# Use OpenRouter free model
response = ai.get_response("Hello!", model="openrouter-free")

# Use local Ollama
response = ai.get_response("Hello!", model="local-llama")

# Use Claude
response = ai.get_response("Hello!", model="claude-3")
```

## Supported Providers

| Provider | Models | API Key |
|----------|--------|---------|
| OpenAI | GPT-4, GPT-3.5 | openai.com/api |
| Anthropic | Claude 3, Claude 2 | console.anthropic.com |
| OpenRouter | 100+ free models | openrouter.ai |
| Azure | Azure OpenAI | Azure portal |
| Ollama | Local models | localhost |
| Groq | Fast free models | console.groq.com |

## Features

| Feature | Description |
|---------|-------------|
| Unified API | One endpoint for all models |
| Fallback | Try next model if one fails |
| Budget Tracking | Monitor spending |
| Rate Limiting | Prevent overuse |
| Caching | Speed up repeated queries |

## Environment Variables
```
# OpenAI
OPENAI_API_KEY=sk-xxx

# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxx

# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-xxx

# LiteLLM
LITELLM_MASTER_KEY=xxx
```

## Code: Auto-Fallback
```python
def get_response_with_fallback(message):
    models = ["openrouter-free", "claude-3", "gpt-4"]
    
    for model in models:
        try:
            return ai.get_response(message, model)
        except Exception as e:
            print(f"{model} failed: {e}")
            continue
    
    return "Sorry, all AI models failed!"
```

## More Info
- Website: https://docs.litellm.ai
- GitHub: https://github.com/BerriAI/litellm
