# WhatsApp Automation Skill for OpenHands

## Overview
This skill enables OpenHands to build, deploy, and manage WhatsApp automation tools with AI-powered features.

## Features
- ✅ WhatsApp Web automation via Selenium
- ✅ AI-powered responses (Ollama, OpenAI, Claude, Gemini, DeepSeek)
- ✅ Keyword-based auto-replies
- ✅ Multi-personality bots
- ✅ Scheduled messages
- ✅ Contact management (whitelist/blacklist)
- ✅ Conversation memory
- ✅ Web dashboard
- ✅ SQLite database for logging

## Installation

### Option 1: Use add-skill Command
```
/add-skill https://github.com/YOUR_USERNAME/whatsapp-automation/tree/main
```

### Option 2: Manual Installation
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/whatsapp-automation.git
cd whatsapp-automation

# Install dependencies
pip install -r requirements.txt

# Configure
cp config.yaml.example config.yaml
# Edit config.yaml with your settings
```

## Configuration

### AI Providers Setup

#### Ollama (Recommended - Free & Local)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2:latest
# or
ollama pull qwen2.5:7b
# or
ollama pull mistral:latest

# Start Ollama service
ollama serve
```

#### OpenAI (Cloud - Requires API Key)
```yaml
# In config.yaml
ai:
  provider: openai
  openai:
    api_key: "sk-your-api-key-here"
    model: "gpt-4"
```

#### Claude (Cloud - Requires API Key)
```yaml
ai:
  provider: claude
  claude:
    api_key: "sk-ant-your-api-key-here"
    model: "claude-3-haiku-20240307"
```

## Usage

### Start the Bot
```bash
python main.py
```

### Interactive Menu
```
╔═══════════════════════════════════════════════════════════════╗
║                    WhatsApp AI Automation                       ║
╚═══════════════════════════════════════════════════════════════╝

[1] Start WhatsApp Bot
[2] Start Web Dashboard
[3] View Statistics
[4] AI Settings
[5] Manage Auto-Reply Rules
[6] Contact Management
[7] Scheduled Messages
[8] Test AI Response
[9] View Logs
[0] Exit
```

### CLI Options
```bash
python main.py --dashboard  # Start web dashboard
python main.py --status     # Show bot statistics
python main.py --ai         # Test AI responses
```

## Auto-Reply Rules

### Keyword-Based Rules
Edit `config.yaml`:
```yaml
auto_reply:
  keywords:
    - keyword: "hi"
      response: "Hello! 👋 How can I help?"
    - keyword: "price"
      response: "For prices, please visit our website."
    - keyword: "hours"
      response: "We're open 9 AM to 9 PM!"
```

### AI-Powered Responses
When no keyword matches, AI generates contextual responses based on:
- Conversation history
- System prompt (customizable)
- Sender context

## Personalities

### Pre-built Personalities
```yaml
personalities:
  default:
    name: "Assistant"
    greeting: "Hello! I'm your AI assistant."
    tone: "friendly"
    
  formal:
    name: "Business Bot"
    greeting: "Good day. How may I assist you?"
    tone: "formal"
    
  casual:
    name: "Buddy"
    greeting: "Hey! What's up? 😄"
    tone: "casual"
```

## Scheduled Messages

### Setup in config.yaml
```yaml
scheduled_messages:
  - time: "09:00"
    message: "Good morning! We're now open! 🌟"
    enabled: true
  - time: "21:00"
    message: "We're closing. See you tomorrow! 👋"
    enabled: true
```

## Database

Messages and contacts are stored in SQLite:
- Location: `data/whatsapp.db`
- Tables: messages, contacts, conversations, statistics

### Query Examples
```python
from src.core.database import Database

db = Database()
stats = db.get_statistics()
messages = db.get_messages(limit=100)
contacts = db.get_contacts()
```

## Advanced Features

### Conversation Memory
The bot remembers context from recent conversations:
```python
# Enable in config.yaml
advanced:
  memory_enabled: true
  memory_limit: 10  # last N messages
```

### Sentiment Analysis
Automatically detects sentiment and adjusts responses:
```python
# Enable in config.yaml
advanced:
  sentiment_analysis: true
```

### Multi-Language Support
Works with messages in any language:
```yaml
ai:
  ollama:
    model: "qwen2.5:7b"  # Good for multilingual
```

## Troubleshooting

### WhatsApp Web Won't Load
```bash
# Update ChromeDriver
pip install --upgrade webdriver-manager
```

### AI Not Responding
```bash
# Check Ollama is running
ollama list  # Shows installed models
ollama run llama3.2:latest  # Test manually
```

### Session Expires
The bot will prompt for QR code scan again if session expires.

## API Reference

### WhatsAppClient
```python
from src.core.whatsapp_client import WhatsAppClient

client = WhatsAppClient(config)
client.connect()           # Connect to WhatsApp Web
client.send_message(msg)  # Send a message
client.get_new_messages() # Get unread messages
```

### ReplyEngine
```python
from src.core.reply_engine import ReplyEngine

engine = ReplyEngine(config)
response = engine.get_reply(message, ai_router, sender)
engine.add_keyword("hello", "Hi there!")
```

### AIProviderRouter
```python
from src.ai.providers import AIProviderRouter

router = AIProviderRouter(ai_config)
response = router.generate_response(message)
status = router.check_status()
router.set_provider("openai")
```

## License
MIT License - Free for personal and commercial use.

## Support
For issues and feature requests, please open an issue on GitHub.
