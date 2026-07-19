# v3.8 Tab - Telegram Bot PRO Edition

## What is v3.8 Tab?

**v3.8 Tab** is a powerful Telegram bot with AI capabilities, built from:
- [Moh4696/build-ai-agents-free](https://github.com/Moh4696/build-ai-agents-free) - Free AI Agents
- [rmyndharis/OpenWA](https://github.com/rmyndharis/OpenWA) - WhatsApp Gateway

---

## Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Chat** | Groq, Gemini, OpenRouter, Ollama support |
| ⚡ **Fast Response** | Groq at ~300 tokens/sec |
| 💬 **Multi-User** | User management & tracking |
| 📊 **Analytics** | Full statistics & reporting |
| 🔔 **Broadcast** | Send to all users at once |
| 🛡️ **Admin Controls** | Blacklist, user management |
| 📈 **Scalable** | Works for 1 to 10,000+ users |

---

## Quick Setup

### 1. Get Telegram Bot Token

1. Open Telegram
2. Search for **@BotFather**
3. Send `/newbot`
4. Follow prompts (name, username)
5. **Copy the token** (format: `123456789:ABCdef...`)

### 2. Get Free AI Keys

**Groq** (Recommended - Fastest, FREE):
1. Go to: https://console.groq.com
2. Sign up with Google/GitHub
3. Create API Key
4. Copy the key

**Google Gemini** (Free Backup):
1. Go to: https://aistudio.google.com
2. Sign in with Google
3. Get API Key

### 3. Install Dependencies

```powershell
cd C:\Users\PC\whatsapp-automation
pip install -r requirements.txt
```

### 4. Configure .env

Edit `C:\Users\PC\whatsapp-automation\.env`:

```env
# Telegram Bot (Required)
TELEGRAM_BOT_TOKEN=123456789:ABCdef...

# Admin IDs (your Telegram user ID)
TELEGRAM_ADMIN_IDS=123456789

# AI Providers (FREE)
GROQ_API_KEY=gsk_xxxxxxxxxxxx
GOOGLE_API_KEY=xxxxxxxxxxxx

# OpenWA (Optional)
OPENWA_URL=http://localhost:2785
OPENWA_API_KEY=your-key
```

### 5. Run the Bot

```powershell
python src/telegram/telegram_bot.py
```

---

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show all commands |
| `/ai <message>` | Chat with AI |
| `/stats` | View statistics |
| `/profile` | Your profile |
| `/aistatus` | AI provider status |

### Admin Commands

| Command | Description |
|---------|-------------|
| `/broadcast <msg>` | Send to all users |
| `/users` | List all users |

---

## Find Your Telegram User ID

1. Search for **@userinfobot** on Telegram
2. Send `/start`
3. Copy your **ID** (number like `123456789`)

Add it to `.env`:
```env
TELEGRAM_ADMIN_IDS=123456789
```

---

## v3.8 Tab vs WhatsApp Bot

| Feature | WhatsApp Bot | v3.8 Tab |
|---------|-------------|----------|
| Platform | WhatsApp | Telegram |
| Setup | Complex (needs phone) | Simple |
| AI Chat | ✅ | ✅ |
| Multi-User | ✅ | ✅ |
| Analytics | ✅ | ✅ |
| Broadcast | ✅ | ✅ |
| No Phone Needed | ❌ | ✅ |

---

## Architecture

```
v3.8 Tab Architecture
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────┐
│          Telegram Users                  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Telegram Bot (v3.8 Tab)          │
│  • Command Handler                       │
│  • Message Handler                       │
│  • Callback Handler                      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            AI Manager                    │
│  • Groq (Primary - FAST)                │
│  • Gemini (Fallback - FREE)              │
│  • Ollama (Local - FREE)                │
│  • OpenRouter (100+ models)              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Analytics & User DB              │
│  • User tracking                         │
│  • Stats                                 │
│  • Command history                       │
└─────────────────────────────────────────┘
```

---

## Files Changed

| File | Description |
|------|-------------|
| `src/telegram/telegram_bot.py` | NEW - Main Telegram bot |
| `requirements.txt` | Updated - Added python-telegram-bot |
| `OPENWA_SETUP.md` | OpenWA Gateway guide |
| `TELEGRAM_SETUP.md` | This file |

---

## Cost: $0

All features are FREE:
- Telegram Bot: FREE
- Groq AI: FREE (14,400 req/day)
- Gemini AI: FREE (1,500 req/day)
- Ollama (Local): FREE

---

## Links

| Resource | URL |
|----------|-----|
| Bot Repo | https://github.com/naitiknahariyaa-png/whatsapp-automation |
| LangChain AI | https://github.com/Moh4696/build-ai-agents-free |
| OpenWA Gateway | https://github.com/rmyndharis/OpenWA |
| Groq API | https://console.groq.com |
| Gemini AI | https://aistudio.google.com |
| BotFather | https://t.me/botfather |

---

## Support

Need help? Open an issue on GitHub:
https://github.com/naitiknahariyaa-png/whatsapp-automation/issues

---

**v3.8 Tab** - AI Powered Telegram Bot - 100% FREE
