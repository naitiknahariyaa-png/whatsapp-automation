# 💬 WhatsApp Automation Hub v5.1

> 🤖 AI-Powered WhatsApp Automation with Telegram Control

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Auto-Reply** | Multi-provider AI (Groq, OpenRouter, Gemini) with fallbacks |
| 💬 **Telegram Control** | Control everything from Telegram bot |
| 📊 **Web Dashboard** | Modern glassmorphism dashboard |
| 🔒 **Security** | Input validation, rate limiting, XSS protection |
| ☁️ **Docker Ready** | Production-ready Docker setup |
| 📈 **Monitoring** | Real-time metrics and health checks |
| 🧪 **Tested** | Comprehensive test suite |
| 💾 **Caching** | In-memory cache with TTL |
| ⚡ **Performance** | Thread-safe SQLite database |

## 🚀 Quick Start

### Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/naitiknahariyaa-png/whatsapp-automation.git
cd whatsapp-automation

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Start with Docker Compose
docker-compose up -d
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env

# Run
python complete_bot.py
```

## 🔑 Required Environment Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather |
| `GROQ_API_KEY` | Free from console.groq.com |
| `OPENWA_API_KEY` | WAHA/OpenWA API key |

## 📁 Project Structure

```
whatsapp-automation/
├── src/
│   ├── ai/              # AI engine with multi-provider support
│   ├── api/             # FastAPI endpoints
│   ├── core/            # Core database & config
│   ├── monitoring/      # Metrics & health checks
│   ├── security/        # Input validation & sanitization
│   └── rate_limiter/    # Rate limiting
├── website/             # Web dashboard (Tailwind CSS)
├── tests/               # Test suite
├── Dockerfile           # Multi-stage production build
├── docker-compose.yml   # Full stack deployment
└── .env.example         # Environment template
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/status` | GET | Connection status |
| `/api/v1/stats` | GET | Dashboard statistics |
| `/api/v1/send` | POST | Send WhatsApp message |
| `/api/v1/broadcast` | POST | Broadcast to all customers |
| `/api/v1/health` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |

## 🛡️ Security Features

- **Input Validation** - Phone numbers, messages, API keys
- **XSS Protection** - HTML/script tag sanitization
- **SQL Injection Prevention** - Pattern detection
- **Rate Limiting** - Per-user request limits
- **Non-root Docker** - Runs as unprivileged user

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_security.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## 📊 Monitoring

Access metrics at `/metrics` for Prometheus scraping:

- System: CPU, Memory, Disk, Network
- Application: Requests, Messages, Cache hit rate
- AI: Provider usage, Latency, Errors

## 🤖 AI Providers

| Provider | Free Tier | Speed |
|----------|-----------|-------|
| Groq | 14,400 req/day | ~300 tokens/sec |
| Gemini | 1,500 req/day | Fast |
| OpenRouter | Varies | Varies |
| Keyword | Unlimited | Instant |

## 🐳 Deployment

### Docker Compose (Full Stack)
```bash
docker-compose up -d
```

### Docker (Single)
```bash
docker build -t whatsapp-hub .
docker run -d -p 8000:8000 --env-file .env whatsapp-hub
```

### Production with Nginx
```bash
# Build
docker-compose build

# Start services
docker-compose up -d nginx
```

## 📝 Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message & help |
| `/status` | Check connection status |
| `/stats` | View statistics |
| `/broadcast` | Send message to all |
| `/test` | Test WhatsApp message |
| `/template` | Manage templates |

## 🔧 Configuration

### Rate Limiting
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

### Security
```env
MAX_MESSAGE_LENGTH=4096
MAX_BROADCAST_RECIPIENTS=100
```

## 📈 Performance

- **Database**: Thread-safe SQLite with indexes
- **Caching**: In-memory cache with TTL
- **AI**: Response caching, multi-provider fallback
- **Rate Limiting**: Token bucket algorithm

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Credits

- [Groq](https://console.groq.com) - Free AI inference
- [LangChain](https://langchain.com) - AI framework
- [WAHA](https://waha.dev/) - WhatsApp HTTP API
- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram bot framework

---

**Built with ❤️ for Indian Businesses 🇮🇳**
