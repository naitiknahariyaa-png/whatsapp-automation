# 🤖 WhatsApp AI Business Bot

<div align="center">

![WhatsApp](https://img.shields.io/badge/WhatsApp-Business-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AI](https://img.shields.io/badge/AI-Powered-FF6B6B?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-4CAF50?style=for-the-badge)

### 🚀 The #1 WhatsApp Automation Solution for Indian Businesses

*Respond to customers 24/7 with AI. Save ₹15,000/month. Setup in 10 minutes.*

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](docs/) • [For Investors](BUSINESS_PLAN.md)

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

```
Menu → Setup WhatsApp → Scan QR Code → Done!
```

---

## 📱 How It Works

```
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
├── main.py                 # Main bot interface
├── requirements.txt        # Dependencies
├── config.yaml            # Configuration
│
├── src/
│   ├── core/
│   │   ├── config.py      # Pydantic validation
│   │   ├── database.py    # SQLite database
│   │   ├── whatsapp_client.py
│   │   └── reply_engine.py
│   │
│   ├── ai/
│   │   └── providers.py    # AI providers
│   │
│   └── api/
│       └── webhook.py      # FastAPI server
│
├── tests/
│   └── test_bot.py        # pytest tests
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

### API Endpoints
```
POST /webhook/message - Handle messages
GET  /stats           - Get statistics
POST /webhook/keyword - Add keywords
GET  /keywords        - List keywords
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

MIT License - see [LICENSE](LICENSE) for details.

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
