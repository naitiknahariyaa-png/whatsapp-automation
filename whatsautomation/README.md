# 🤖 WhatsAutomation API

A comprehensive WhatsApp automation REST API with 50+ integrations.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your API keys

# Start everything
docker-compose up -d

# Open API docs
open http://localhost:8000/docs
```

### Option 2: Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn whatsautomation.app:app --reload --port 8000

# Open docs
open http://localhost:8000/docs
```

---

## 📚 API Documentation

| URL | Description |
|-----|-------------|
| `/docs` | Swagger UI (Interactive) |
| `/redoc` | ReDoc (Alternative) |
| `/health` | Health check |

---

## 🔌 API Endpoints

### 🤖 AI
```
GET  /api/v1/ai/status        - Get AI status
POST /api/v1/ai/chat         - Generate AI response
POST /api/v1/ai/configure    - Configure AI provider
GET  /api/v1/ai/models       - List available models
POST /api/v1/ai/test         - Test AI
```

### 📱 WhatsApp
```
GET  /api/v1/whatsapp/status      - Get WhatsApp status
POST /api/v1/whatsapp/send        - Send message
POST /api/v1/whatsapp/send-image  - Send image
GET  /api/v1/whatsapp/chats       - List chats
POST /api/v1/whatsapp/broadcast   - Broadcast message
```

### 💾 Database
```
GET  /api/v1/db/stats          - Get statistics
GET  /api/v1/db/messages       - Get messages
POST /api/v1/db/messages       - Add message
GET  /api/v1/db/keywords       - Get keywords
POST /api/v1/db/keywords       - Add keyword
POST /api/v1/db/backup         - Backup database
```

### 🔗 Integrations
```
GET  /api/v1/integrations/list           - List all integrations
GET  /api/v1/integrations/{name}         - Get integration info
POST /api/v1/integrations/{name}/test    - Test integration
POST /api/v1/integrations/discord/send   - Send Discord message
POST /api/v1/integrations/telegram/send  - Send Telegram message
POST /api/v1/integrations/ntfy/send     - Send Ntfy notification
```

---

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Test AI
```bash
curl -X POST http://localhost:8000/api/v1/ai/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### Send WhatsApp Message
```bash
curl -X POST http://localhost:8000/api/v1/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{"phone": "919876543210", "message": "Hello from API!"}'
```

### Send Discord Message
```bash
curl -X POST http://localhost:8000/api/v1/integrations/discord/send \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from WhatsAutomation API!"}'
```

---

## 🔑 Required API Keys

### FREE Services (No Credit Card)
| Service | Variable | Signup |
|---------|----------|--------|
| Groq | `GROQ_API_KEY` | https://console.groq.com |
| OpenRouter | `OPENROUTER_API_KEY` | https://openrouter.ai |
| Ollama | `OLLAMA_URL` | https://ollama.com |
| Telegram | `TELEGRAM_BOT_TOKEN` | @BotFather |
| Discord | `DISCORD_WEBHOOK` | Channel Settings |
| Ntfy | `NTFY_URL` | https://ntfy.sh |

---

## 🐳 Docker Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build

# View logs
docker-compose logs -f api

# Shell into container
docker exec -it whatsautomation-api sh
```

---

## 📁 Project Structure

```
whatsautomation/
├── app.py                    # Main FastAPI app
├── requirements.txt          # Dependencies
├── Dockerfile               # Container build
├── docker-compose.yml       # Multi-container setup
├── .env.example            # Environment template
├── endpoints/
│   ├── __init__.py
│   ├── ai.py              # AI endpoints
│   ├── whatsapp.py        # WhatsApp endpoints
│   ├── database.py        # Database endpoints
│   └── integrations.py    # Integration endpoints
└── README.md
```

---

## 🌟 Features

- **50+ Integrations** - AI, Database, CRM, Analytics, Notifications
- **Auto-generated Docs** - Swagger & ReDoc
- **Docker Ready** - One command deployment
- **RESTful API** - Easy to integrate
- **Type-safe** - Pydantic models
- **CORS Enabled** - Cross-origin requests

---

## 📜 License

MIT License - Use freely for personal and commercial projects.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Built with ❤️ for WhatsApp automation**
