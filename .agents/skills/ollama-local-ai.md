# Ollama Local AI Skill

## Purpose
Run free AI models locally - no API costs!

## What is Ollama?
Run AI models on your own computer - 100% free, private.

## Setup

### 1. Install Ollama
**Mac/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from: https://ollama.com/download

### 2. Download Models
```bash
# Download a model (first time takes a while)
ollama pull llama3.2           # ~2GB
ollama pull codellama         # Coding assistant
ollama pull mistral           # Fast & good
ollama pull phi               # Small & fast
ollama pull deepseek-r1       # Reasoning
```

### 3. Start Ollama Server
```bash
# Server runs automatically
ollama serve

# Or run a specific model
ollama run llama3.2
```

### 4. Connect to WhatsApp Bot
```python
# In providers.py
import requests

OLLAMA_URL = "http://localhost:11434"

class OllamaAI:
    """Local AI using Ollama"""
    
    def __init__(self, model="llama3.2"):
        self.model = model
        self.url = f"{OLLAMA_URL}/api/generate"
    
    def get_response(self, message, context=""):
        """Get AI response from local model"""
        prompt = f"""You are a helpful WhatsApp bot assistant.
Context: {context}
Customer: {message}
Response:"""
        
        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        
        return response.json()["response"]
    
    def get_status(self):
        """Check if Ollama is running"""
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags")
            return {
                "available": True,
                "models": r.json().get("models", [])
            }
        except:
            return {"available": False}

# Usage
ollama = OllamaAI(model="llama3.2")
response = ollama.get_response("Hi, what are your prices?")
```

## Models Comparison

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| llama3.2 | 2GB | Fast | Good |
| mistral | 4GB | Medium | Very Good |
| phi | 1GB | Very Fast | Good |
| deepseek-r1 | 7GB | Slow | Excellent |
| codellama | 4GB | Medium | Great for code |

## Free Models Available
```bash
# List all available
ollama list

# Pull specific model
ollama pull llama3.2
ollama pull mistral
ollama pull mixtral
ollama pull deepseek-r1
```

## Features

| Feature | Description |
|---------|-------------|
| 100% Free | No API costs |
| Private | Data stays local |
| Fast | On your hardware |
| Offline | Works without internet |

## Environment Variables
```
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Hardware Requirements
- **Minimum:** 8GB RAM, 10GB storage
- **Recommended:** 16GB RAM, 20GB storage
- **GPU:** Much faster with NVIDIA GPU

## More Info
- Website: https://ollama.com
- GitHub: https://github.com/ollama/ollama
