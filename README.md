# 🚀 WhatsApp AI Automation Tool

An advanced WhatsApp automation system with AI-powered replies, multi-personality bots, scheduled messages, and more.

## Features

### Core Features
- ✅ **Auto-Reply System** - Keyword-based and AI-powered responses
- ✅ **Multi-Session Support** - Run multiple WhatsApp accounts
- ✅ **Contact Management** - Whitelist, blacklist, group-specific rules
- ✅ **Message Logging** - SQLite database for all conversations
- ✅ **Scheduled Messages** - Send messages at specific times

### AI Features
- 🤖 **Local AI (Ollama)** - Privacy-focused, no API costs
- 🤖 **OpenAI Integration** - GPT-4 powered responses
- 🤖 **Claude Integration** - Anthropic Claude powered
- 🤖 **Gemini Integration** - Google Gemini powered
- 🤖 **DeepSeek Integration** - Budget-friendly AI

### Advanced Features
- 🎭 **Multi-Personality Bots** - Different personalities for different contacts
- 🧠 **Conversation Memory** - Remember context across messages
- 📊 **Analytics Dashboard** - Track replies, engagement, stats
- 🔄 **Auto-Restart** - Recover from crashes automatically
- 🌐 **Web Dashboard** - Monitor and control via browser
- 📱 **Mobile App Ready** - API for mobile integration

## Quick Start

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/whatsapp-automation.git
cd whatsapp-automation

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py

# Start the bot
python main.py
```

## Configuration

Edit `config.yaml` to customize:
- AI provider settings
- Auto-reply rules
- Scheduled messages
- Contact preferences

## Project Structure

```
whatsapp-automation/
├── main.py                 # Main entry point
├── config.yaml            # Configuration
├── src/
│   ├── core/             # Core automation logic
│   │   ├── whatsapp_client.py
│   │   ├── message_handler.py
│   │   ├── reply_engine.py
│   │   ├── scheduler.py
│   │   └── database.py
│   ├── ai/              # AI integrations
│   │   ├── providers.py
│   │   ├── ollama_client.py
│   │   ├── openai_client.py
│   │   └── claude_client.py
│   └── utils/           # Utilities
│       ├── logger.py
│       └── helpers.py
└── skills/              # OpenHands skills
    └── whatsapp-auto-reply/
```

## License

MIT License - Free for personal and commercial use

---

**Made with ❤️ for Indian Businesses**
