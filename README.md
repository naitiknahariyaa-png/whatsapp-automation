# 🤖 WhatsApp AI Business Bot

<div align="center">

![WhatsApp](https://img.shields.io/badge/WhatsApp-Business-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AI](https://img.shields.io/badge/AI-Powered-FF6B6B?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-4CAF50?style=for-the-badge)

### 🚀 The #1 WhatsApp Automation Solution for Indian Businesses

*Respond to customers 24/7 with AI. Save ₹15,000/month. Setup in 10 minutes.*

[Features](#-features) • [Quick Start](#-quick-start) • [Advanced Features](ADVANCED_FEATURES.md) • [For Investors](BUSINESS_PLAN.md)

</div>

---

## 💡 What Is This?

**WhatsApp AI Business Bot** is an intelligent automation platform that:

- ✅ **Responds instantly** to WhatsApp messages 24/7
- ✅ **AI-powered** - understands and answers questions naturally
- ✅ **Multi-language** - supports English, Hindi, and regional languages
- ✅ **Easy setup** - scan QR code, done in 10 minutes
- ✅ **Affordable** - starts at ₹999/month (90% cheaper than hiring staff)

---

## 🎯 Why This Matters

| Problem | Solution |
|---------|----------|
| Can't reply 24/7? | AI replies instantly, always |
| Hiring staff costs ₹15,000+? | Bot does it for ₹999/month |
| Slow responses = lost customers? | Responds in <2 seconds |
| Complex enterprise tools? | Simple QR code setup |

**Perfect for**: Restaurants, Shops, Salons, Clinics, Tuitions, Real Estate, and more!

---

## ✨ Features

### 🤖 Smart AI Responses
- Powered by OpenRouter (100+ free models)
- Natural language understanding
- Context-aware conversations
- Continuous learning

### 📱 WhatsApp Integration
- Works with existing WhatsApp Business
- QR code setup (no technical skills)
- Session persistence
- Real-time message handling

### 📊 Business Tools
- **Dashboard** - Message stats, analytics
- **Knowledge Base** - Add products, prices, FAQs
- **Multi-language** - Hindi + regional support
- **API Ready** - Connect to your systems

### 🛠️ Developer-Friendly
- **Open Source** - Full source code available
- **FastAPI** - Professional webhook API
- **pytest** - Industry-grade testing
- **CI/CD** - GitHub Actions included

---

## 🛡️ Three-Layer Auto-Recovery System

The bot includes a robust auto-recovery system to keep it running 24/7:

| Layer | Problem | Solution | Recovery Time |
|-------|---------|----------|---------------|
| **Layer 1** | Process crashes | systemd auto-restarts | ~5 seconds |
| **Layer 2** | Process freezes | Watchdog force-restarts | ~5 minutes |
| **Layer 3** | Single request fails | Auto-retry before giving up | Immediate |

Plus: Telegram alerts notify you the moment anything breaks.

### Systemd Service (Layer 1)

The `whatsapp-bot.service` file handles process crashes:

```ini
[Unit]
Description=WhatsApp AI Business Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=%i
WorkingDirectory=/home/%i/whatsapp-automation
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=/home/%i/whatsapp-automation/.env

ExecStart=/home/%i/whatsapp-automation/venv/bin/python -m uvicorn src.api.webhook:app --host 0.0.0.0 --port 8000

Restart=always
RestartSec=5
StartLimitBurst=10
StartLimitWindow=60
WatchdogSec=90

StandardOutput=append:/home/%i/whatsapp-automation/logs/bot.log
StandardError=append:/home/%i/whatsapp-automation/logs/bot-error.log

[Install]
WantedBy=multi-user.target
```

Install it:
```bash
sudo cp whatsapp-bot.service /etc/systemd/system/whatsapp-bot@yourusername.service
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-bot@yourusername
sudo systemctl start whatsapp-bot@yourusername
```

### Watchdog Script (Layer 2)

The `watchdog.py` script catches frozen processes that systemd misses. It runs every 5 minutes via cron:

```bash
# Set up cron job
crontab -e
# Add this line:
*/5 * * * * /home/yourusername/whatsapp-automation/venv/bin/python /home/yourusername/whatsapp-automation/watchdog.py >> logs/watchdog.log 2>&1

# Allow passwordless sudo for restart
sudo visudo
# Add: yourusername ALL=(ALL) NOPASSWD: /bin/systemctl restart whatsapp-bot@yourusername
```

### Telegram Alerts (Notifications)

Get instant notifications when something goes wrong:

1. Open Telegram → **@BotFather** → `/newbot` → copy the token
2. Message your new bot once
3. Visit `https://api.telegram.org/bot<TOKEN>/getUpdates` to get your chat ID
4. Add to `.env`:
```
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

The alerts module (`src/core/alerts.py`) includes:
- Rate limiting (max 1 alert per 5 minutes per error type)
- Retry decorator for automatic request retries

### What This Protects Against

| Scenario | Protection |
|----------|------------|
| Python crash | systemd restarts in 5 seconds |
| Bot frozen (infinite loop) | Watchdog restarts in ~5 minutes |
| AI API timeout | Auto-retry 3 times with backoff |
| Network blip | Automatic retry before giving up |
| Any failure | Telegram alert sent |

### What It Doesn't Fix

- WhatsApp session expiring (still needs QR re-scan)
- Account bans (architecture limitation)

---

## 🚀 Quick Start

### 1. Clone & Install (2 minutes)

```bash
# Clone the repository
git clone https://github.com/naitiknahariyaa-png/whatsapp-automation.git
cd whatsapp-automation

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure (2 minutes)

```bash
# Copy environment file
cp .env.example .env

# Add your OpenRouter API key (FREE)
# Get it from: https://openrouter.ai/keys
echo "OPENROUTER_API_KEY=sk-or-your-key" >> .env
```

### 3. Run (30 seconds)

```bash
python main.py
```

### 4. Connect WhatsApp (2 minutes)

```text
Menu → Setup WhatsApp → Scan QR Code → Done!
```

---

## 📱 How It Works

```text
Customer sends message
        ↓
WhatsApp receives it
        ↓
AI Bot analyzes message
        ↓
Instant smart response
        ↓
Customer happy! 🎉
```

---

## 💰 Pricing

| Plan | Price | Best For |
|------|-------|----------|
| **Starter** | ₹999/month | Small shops, startups |
| **Business** | ₹2,499/month | Growing businesses |
| **Enterprise** | ₹5,999/month | Large operations |

**Or buy once, use forever:**
- Lifetime License: ₹29,999
- Source Code: ₹49,999

---

## 🏆 Why Choose Us?

| Feature | Others | Us |
|---------|--------|-----|
| Setup Time | Days | 10 minutes |
| Monthly Cost | ₹10,000+ | ₹999 |
| Languages | English only | Hindi + Regional |
| Support | Email only | WhatsApp priority |

---

## 📂 Project Structure

```
whatsapp-automation/
├── main.py                 # Main entry point (simplified)
├── watchdog.py             # Auto-restart if bot freezes
├── whatsapp-bot.service    # systemd service file
├── config.yaml             # Configuration file
├── requirements.txt        # Dependencies
│
├── src/
│   ├── cli/                # Command-line interface
│   │   ├── __init__.py
│   │   ├── colors.py      # Terminal colors & formatting
│   │   ├── menu.py        # Menu structure definition
│   │   └── commands.py    # All menu command implementations
│   │
│   ├── core/
│   │   ├── config.py      # Pydantic configuration
│   │   ├── database.py    # SQLite database
│   │   ├── whatsapp_client.py  # WhatsApp Web client
│   │   └── reply_engine.py     # Auto-reply logic
│   │
│   ├── ai/
│   │   ├── providers.py   # AI providers (OpenRouter, Groq)
│   │   └── langchain_integration.py
│   │
│   ├── api/
│   │   └── webhook.py     # FastAPI webhook server
│   │
│   └── utils/
│       └── alerts.py       # Telegram alerts + retry decorator
│
├── tests/
│   ├── test_bot.py        # Main tests
│   ├── test_alerts.py     # Alert module tests
│   └── test_watchdog.py   # Watchdog tests
│
├── BUSINESS_PLAN.md        # For investors
├── PROJECT_PROPOSAL.md     # Detailed proposal
└── PITCH_DECK.md          # One-page pitch
```

---

## 🛠️ For Developers

### Run Tests
```bash
pytest tests/ -v
```

### Start API Server
```bash
python -m uvicorn src.api.webhook:app --port 8000
```

### Using the Alerts Module

Import the retry decorator for automatic retry on failures:

```python
from src.core.alerts import with_retry

@with_retry(max_attempts=3, delay_seconds=2)
def get_ai_response(prompt: str) -> str:
    # Your code here - will auto-retry on failure
    ...
```

Send Telegram alerts manually:

```python
from src.core.alerts import send_alert

send_alert("Something went wrong!", level="ERROR")
send_alert("Heads up - minor issue", level="WARNING")
```

### API Endpoints

```text
GET  /health            - Health check (used by watchdog)
POST /webhook/message   - Handle incoming messages
GET  /stats             - Get message statistics
POST /webhook/keyword   - Add custom keywords
GET  /keywords          - List all keywords
```

---

## 📈 Roadmap

| Feature | Status |
|---------|--------|
| ✅ WhatsApp Web integration | Complete |
| ✅ AI responses (OpenRouter) | Complete |
| ✅ Keyword matching | Complete |
| ✅ Multi-language support | Complete |
| 🔜 Telegram integration | Q2 |
| 🔜 Voice messages | Q3 |
| 🔜 White-label | Q4 |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 📞 Contact

**For Business Inquiries**: [your-email@domain.com]
**For Support**: [support@domain.com]
**WhatsApp**: [Your Business WhatsApp]

---

<div align="center">

### ⭐ Star this repo if it helps you!

*Built with ❤️ for Indian Businesses*

</div>
