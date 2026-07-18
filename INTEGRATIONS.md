# WhatsApp Bot - Complete Integration Guide

All available integrations and features for the WhatsApp AI Bot.

## 📦 Available Integrations

### AI Providers

| Provider | Cost | Speed | Quality | Setup |
|----------|------|-------|---------|-------|
| [OpenRouter](https://openrouter.ai) | FREE | Medium | Good | API key |
| [Groq](https://console.groq.com) | FREE | Fast | Good | API key |
| [Ollama](https://ollama.com) | FREE | Medium | Good | Local install |
| [OmniRoute](https://omniroute.onl) | FREE | Fast | Good | npm install |

### Caching & Queue

| Feature | Purpose | Setup |
|---------|---------|-------|
| Redis | Cache AI responses, rate limiting | `docker run -d -p 6379:6379 redis` |
| Celery | Async processing, bulk messages | Start workers |

### Workflow Automation

| Integration | Purpose | Setup |
|-------------|---------|-------|
| N8N | 400+ automations | `docker run -d -p 5678:5678 n8nio/n8n` |
| Chatwoot | Unified inbox, CRM | `docker run -d -p 3000:3000 chatwoot/chatwoot` |
| Botpress | Visual chatbot flows | `docker run -d -p 3000:3000 botpress/server` |
| Typebot | Interactive forms | `docker run -d -p 3000:3000 botpress/typebot` |

### Monitoring

| Tool | Purpose | Setup |
|------|---------|-------|
| Healthchecks | Uptime monitoring | Create account at healthchecks.io |
| Netdata | Real-time metrics | Install via kickstart script |
| Prometheus | Metrics export | Built-in `/metrics` endpoint |

### Database

| Database | Purpose | Setup |
|----------|---------|-------|
| SQLite | Local storage | Built-in |
| Supabase | Cloud PostgreSQL | Create account at supabase.com |

## 🚀 Quick Setup

### 1. Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f whatsapp-bot
```

### 2. Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis
docker run -d -p 6379:6379 redis

# Run bot
python main.py
```

## 📖 Detailed Guides

### Redis Caching

```python
from src.integrations import RedisCache

# Initialize
cache = RedisCache()

# Cache AI responses
cached = cache.get_cached_ai_response("Hello!")
if not cached:
    cached = ai.get_response("Hello!")
    cache.cache_ai_response("Hello!", cached)

# Rate limiting
if not cache.check_rate_limit(user_id, limit=10, window=60):
    return "Please wait before sending more messages"

# Duplicate prevention
if cache.is_message_processed(message_id):
    return  # Already replied
cache.mark_message_processed(message_id)
```

### Celery Task Queue

```python
from src.integrations import process_whatsapp_message, send_bulk_messages

# Process message in background
task = process_whatsapp_message.delay(sender, message, message_id)

# Send bulk messages
result = send_bulk_messages.delay(
    numbers=["+91-1234567890", "+91-0987654321"],
    message="Your order is ready!"
)

# Check result
print(result.get(timeout=60))
```

### N8N Workflow

```python
from src.integrations import N8NClient

n8n = N8NClient()

# Trigger on new message
n8n.on_new_message(sender, message)

# Trigger on order
n8n.on_order(sender, items=["Pizza", "Coke"], total=299)

# Trigger on lead capture
n8n.on_lead_capture(sender, name="John", email="john@example.com", interest="Product")
```

### Chatwoot Integration

```python
from src.integrations import ChatwootClient

chatwoot = ChatwootClient()

# Create contact
contact_id = chatwoot.create_contact(name="John", phone="+91-1234567890")

# Send message to conversation
chatwoot.send_message(conversation_id=1, message="Thanks for your order!")

# Add label
chatwoot.add_label(conversation_id=1, label="hot-lead")
```

### Botpress Flows

```python
from src.integrations import BotpressClient

botpress = BotpressClient()

# Send message for processing
response = botpress.get_response(user_id, "I want to order pizza")
print(response)

# Trigger specific flow
botpress.trigger_flow(user_id, "order-flow")

# Set user variable
botpress.set_variable(user_id, "plan", "premium")
```

### Typebot Forms

```python
from src.integrations import TypebotClient, WhatsAppFormHandler

typebot = TypebotClient()

# Start form
form = typebot.start_form(user_id)
send_whatsapp(form["question"]["text"])

# Process answer
result = typebot.process_form_step(session_id, user_answer)

# Or use handler
handler = WhatsAppFormHandler(user_id="1234567890")
form = handler.start_form("lead-collection")
send_whatsapp(handler.format_for_whatsapp(form["question"]))
```

### Healthchecks Monitoring

```python
from src.monitoring import HealthchecksMonitor, HeartbeatThread

# Simple ping
monitor = HealthchecksMonitor()
monitor.ping("✅ Bot is running!")

# Background heartbeat
monitor = HealthchecksMonitor()
heartbeat = HeartbeatThread(monitor, interval=300)  # 5 minutes
heartbeat.start()

# Ping on events
monitor.ping_start()
try:
    process_message()
    monitor.ping_success()
except Exception as e:
    monitor.ping_fail(str(e))
```

### Prometheus Metrics

```python
from src.monitoring import PrometheusMetrics

metrics = PrometheusMetrics()

# Get metrics in Prometheus format
output = metrics.get_prometheus_output()

# Save to file for scraping
metrics.save_to_file("/var/www/html/metrics.txt")

# In FastAPI:
@app.get("/metrics")
async def metrics():
    return Response(content=PrometheusMetrics().get_prometheus_output(), media_type="text/plain")
```

## 🐳 Docker Compose Services

All services can be started with:

```bash
docker-compose up -d
```

Services:
- `whatsapp-bot` - Main bot application
- `redis` - Cache and message broker
- `celery-worker` - Background task worker
- `celery-beat` - Scheduled tasks
- `nginx` - Reverse proxy
- `chatwoot` - Unified inbox (optional)
- `n8n` - Workflow automation (optional)
- `postgres` - Database for Chatwoot

## 🔒 Environment Variables

See `.env.example` for all configuration options.

Required:
- `OPENROUTER_API_KEY` - AI provider
- `TELEGRAM_BOT_TOKEN` - Alerts
- `TELEGRAM_CHAT_ID` - Alerts

Optional:
- `REDIS_URL` - Cache backend
- `CHATWOOT_API_URL` - CRM integration
- `N8N_WEBHOOK_URL` - Workflow trigger
- `HEALTHCHECKS_PING_URL` - Uptime monitoring

## 📊 Monitoring Endpoints

| Endpoint | Format | Purpose |
|----------|--------|---------|
| `/health` | JSON | Health check |
| `/metrics` | Prometheus | Metrics export |

## 🚀 Scaling

### Single Instance
```bash
python main.py
```

### Multiple Instances with Load Balancer
```bash
# Start 3 bot instances
docker-compose up -d --scale whatsapp-bot=3
```

### With Celery Workers
```bash
# Start 4 Celery workers
celery -A src.integrations.celery_tasks worker --loglevel=info --concurrency=10
```

## 🛠️ Troubleshooting

### Redis Not Connecting
```bash
# Check Redis is running
docker ps | grep redis

# Start Redis
docker run -d -p 6379:6379 redis
```

### Celery Workers Not Processing
```bash
# Check worker logs
docker-compose logs celery-worker

# Restart workers
docker-compose restart celery-worker
```

### N8N Webhook Not Triggering
1. Check webhook URL in `.env`
2. Verify N8N is running: `docker-compose ps n8n`
3. Test webhook in N8N dashboard

### Chatwoot Not Receiving Messages
1. Verify Chatwoot URL and API token
2. Check inbox is configured for WhatsApp
3. Test with: `curl -X POST http://localhost:3000/api/v1/conversations`
