# WhatsApp Automation Hub - Agent Context

## Project Overview

**WhatsApp Automation Hub** is a Python-based automation system for Indian businesses featuring:
- AI auto-replies via Groq/Gemini
- Broadcast messaging to customers
- Lead capture from incoming messages
- Telegram bot control
- Web dashboard

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run web dashboard
python web_dashboard.py

# OR run Telegram bot
python complete_bot.py
```

## Required Configuration

```env
# OpenWA Gateway (Required)
OPENWA_URL=http://localhost:3000
OPENWA_API_KEY=your-api-key
OPENWA_SESSION=default

# Optional: AI (for smart auto-replies)
GROQ_API_KEY=your-groq-key

# Optional: Telegram control
TELEGRAM_BOT_TOKEN=your-token
```

## Key Files

| File | Purpose |
|------|---------|
| `web_dashboard.py` | Web UI + API server with webhook |
| `complete_bot.py` | Telegram bot for command control |
| `src/` | Core modules (AI, security, rate limiting) |
| `website/` | Web dashboard HTML |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | System status |
| `/api/send` | POST | Send WhatsApp message |
| `/api/broadcast` | POST | Broadcast to all customers |
| `/api/customers` | GET | List customers |
| `/api/leads` | GET | List captured leads |
| `/api/templates` | GET | View auto-reply templates |
| `/webhook` | POST | Receive WhatsApp messages |
| `/health` | GET | Health check |

## Webhook Setup

1. Start OpenWA: `docker run -d --name openwa -p 3000:3000 waha/waha:latest`
2. Start hub: `python web_dashboard.py`
3. In OpenWA dashboard, set webhook: `http://YOUR_IP:8000/webhook`

## Telegram Commands

- `/start` - Show menu
- `/status` - Check status
- `/broadcast MSG` - Send to all customers
- `/send PHONE MSG` - Send single message
- `/leads` - View captured leads
- `/addlead PHONE MSG` - Add lead manually
- `/addcustomer PHONE` - Add customer
- `/template KEYWORD RESPONSE` - Add template

## Development

### Add New Feature

1. Edit `web_dashboard.py` for API routes
2. Update `Database` class for data storage
3. Update `AI` class for AI integration
4. Update `WA` class for WhatsApp sending

### Testing

```bash
# Test webhook locally
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"event":"message","payload":{"from":"919876543210@c.us","message":{"conversation":"Hello"}}}'
```

## Docker Deployment

```bash
docker build -t whatsapp-hub .
docker run -d -p 8000:8000 \
  -e OPENWA_URL=http://openwa:3000 \
  -e OPENWA_API_KEY=$KEY \
  whatsapp-hub
```

## Skills Available

When working with this project, these skills are relevant:

- **openwa-gateway** - OpenWA setup and API usage
- **waha-gateway** - Alternative WhatsApp gateway
- **groq-ai** - Free fast AI for auto-replies
- **docker-deployment** - Container deployment
- **healthchecks-monitoring** - Uptime monitoring

## Common Issues

| Issue | Solution |
|-------|----------|
| WhatsApp not connected | Check OPENWA_URL and API key |
| Auto-reply not working | Verify webhook URL in OpenWA |
| AI not responding | Add GROQ_API_KEY to .env |
| Port 8000 in use | Change PORT=8001 in .env |
