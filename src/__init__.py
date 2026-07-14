"""
WhatsApp Automation Skill for OpenHands
Use this skill to build, deploy, and manage WhatsApp automation tools
"""

# Skill metadata
SKILL_NAME = "whatsapp-automation"
SKILL_VERSION = "1.0.0"
SKILL_DESCRIPTION = """
WhatsApp AI Automation Tool - Build intelligent auto-reply bots

## Features
- 🤖 AI-powered responses (Ollama, OpenAI, Claude, Gemini, DeepSeek)
- 📝 Keyword-based auto-replies
- ⏰ Scheduled messages
- 👥 Contact management
- 📊 Statistics dashboard
- 🎭 Multi-personality bots

## Usage
1. Install: pip install -r requirements.txt
2. Configure: Edit config.yaml
3. Run: python main.py

## Commands
- Start bot: python main.py
- Dashboard: python main.py --dashboard
- Status: python main.py --status
"""

# Environment variables needed
REQUIRED_ENV_VARS = {
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OPENAI_API_KEY": "Optional - for OpenAI GPT-4",
    "ANTHROPIC_API_KEY": "Optional - for Claude",
    "GEMINI_API_KEY": "Optional - for Google Gemini",
    "DEEPSEEK_API_KEY": "Optional - for DeepSeek"
}

# Installation guide
INSTALL_GUIDE = """
# WhatsApp Automation Tool - Installation Guide

## Quick Install
```bash
git clone <repo-url>
cd whatsapp-automation
pip install -r requirements.txt
python setup.py
```

## Configuration
1. Copy config.yaml.example to config.yaml
2. Edit config.yaml with your settings
3. For AI features, install Ollama:
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Pull a model
   ollama pull llama3.2
   ```

## Usage
```bash
# Start interactive menu
python main.py

# Start directly
python main.py --dashboard  # Web dashboard
python main.py --status     # Show stats
```

## For Developers
```python
from src.core.whatsapp_client import WhatsAppClient
from src.core.reply_engine import ReplyEngine
from src.ai.providers import AIProviderRouter

# Initialize
whatsapp = WhatsAppClient()
ai = AIProviderRouter(config)
reply_engine = ReplyEngine(config)

# Connect
whatsapp.connect()

# Auto-reply loop
while True:
    messages = whatsapp.get_new_messages()
    for msg in messages:
        response = reply_engine.get_reply(msg['content'], ai)
        whatsapp.send_message(response)
```
"""
