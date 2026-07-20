---
name: whatsapp-automation-hub
description: Complete WhatsApp automation system for Indian businesses with AI auto-replies, broadcast messaging, lead capture, and Telegram control. Use when building WhatsApp bots, managing customer communications, or automating sales workflows.
trigger phrases: ["whatsapp bot", "whatsapp automation", "auto reply", "broadcast", "lead capture", "telegram control"]
tags: [whatsapp, automation, bot, ai, business, india]
complexity: medium
cost: free
self-hosted: true
---

# WhatsApp Automation Hub Skill

## Overview

**WhatsApp Automation Hub** is a comprehensive Python-based automation system for Indian businesses.

### Features

- 🤖 **AI Auto-Reply** - Intelligent responses using Groq/Gemini
- 📢 **Broadcast** - Send to all customers at once
- 👥 **Lead Capture** - Auto-capture leads from messages
- 📱 **Telegram Control** - Control from Telegram bot
- 🌐 **Web Dashboard** - Visual management interface
- 🔒 **Rate Limiting** - Prevent spam/abuse
- 📊 **Analytics** - Track messages and leads

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:
```env
OPENWA_URL=http://localhost:3000
OPENWA_API_KEY=your-api-key
OPENWA_SESSION=default
GROQ_API_KEY=your-groq-key  # Optional
TELEGRAM_BOT_TOKEN=your-token  # Optional
```

### 3. Run Web Dashboard

```bash
python web_dashboard.py
```

Open: http://localhost:8000

### 4. Set Webhook

In OpenWA settings, set:
```
http://YOUR_IP:8000/webhook
```

## Available Scripts

| Script | Purpose |
|--------|---------|
| `web_dashboard.py` | Web UI + API server |
| `complete_bot.py` | Telegram bot control |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | System status |
| `/api/send` | POST | Send single message |
| `/api/broadcast` | POST | Broadcast to all |
| `/api/customers` | GET | List customers |
| `/api/leads` | GET | List captured leads |
| `/api/templates` | GET | View templates |
| `/webhook` | POST | Receive messages |

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Show menu |
| `/broadcast MSG` | Send to all |
| `/send PHONE MSG` | Send single |
| `/leads` | View leads |
| `/addcustomer PHONE` | Add customer |

## Architecture

```
WhatsApp → OpenWA → Webhook → Hub → AI/Templates
                              ↓
                         Dashboard/DB
```

## Templates

Templates auto-reply when keywords match:

```python
"hello" → "Hi there!"
"price" → "Our prices are..."
"order" → "To order, tell me..."
```

Add templates via dashboard or code.

## Lead Flow

1. Customer sends WhatsApp message
2. Webhook receives → logs → captures lead
3. AI/tempLate generates response
4. Auto-reply sent to customer

## Docker Deployment

```bash
docker build -t whatsapp-hub .
docker run -d -p 8000:8000 \
  -e OPENWA_URL=http://openwa:3000 \
  -e OPENWA_API_KEY=$KEY \
  whatsapp-hub
```
