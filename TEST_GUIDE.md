# WhatsApp Bot v3.8 - Testing Guide (PowerShell)

Complete step-by-step guide to test all new features in v3.8

---

## 🚀 Quick Start - Test Everything in 10 Minutes

### Step 1: Clone the Repository

```powershell
# Clone the repo
git clone https://github.com/naitiknahariyaa-png/whatsapp-automation.git
cd whatsapp-automation

# Checkout v3.8
git checkout v3.8
```

### Step 2: Install Dependencies

```powershell
# Install Python (if not installed)
# Download from: https://www.python.org/downloads/

# Install dependencies
pip install -r requirements.txt

# Install Redis (for caching)
docker run -d -p 6379:6379 redis
```

### Step 3: Configure Environment

```powershell
# Copy example env file
copy .env.example .env

# Edit .env with your API keys
notepad .env
```

Add these keys to `.env`:
```env
OPENROUTER_API_KEY=sk-or-your-key-here
TELEGRAM_BOT_TOKEN=your-telegram-token
TELEGRAM_CHAT_ID=your-chat-id
REDIS_URL=redis://localhost:6379
```

---

## 🧪 Test Each Feature

### Test 1: Redis Cache ✅

```powershell
# Start Redis container
docker run -d -p 6379:6379 redis

# Test Redis connection in Python
python -c "
from src.integrations import RedisCache
cache = RedisCache()
print('Redis Status:', 'Enabled' if cache.enabled else 'Disabled')

# Test caching
cache.cache_ai_response('Hello', 'Hi there!')
result = cache.get_cached_ai_response('Hello')
print('Cache Test:', 'Passed' if result else 'Failed')
"
```

**Expected Output:**
```
Redis Status: Enabled
Cache Test: Passed
```

---

### Test 2: Celery Task Queue ✅

```powershell
# Start Redis (if not running)
docker run -d -p 6379:6379 redis

# In Terminal 1: Start Celery worker
celery -A src.integrations.celery_tasks worker --loglevel=info

# In Terminal 2: Test tasks
python -c "
from src.integrations import send_bulk_messages, health_check

# Test health check task
result = health_check.delay()
print('Health Check Result:', result.get(timeout=10))
"
```

**Expected Output:**
```
[INFO] Ready
[INFO] Task completed: src.integrations.celery_tasks.health_check
```

---

### Test 3: Healthchecks Monitoring ✅

```powershell
# Set environment variable (optional - test without real ping URL)
$env:HEALTHCHECKS_PING_URL = "https://hc-ping.com/test-123"

# Test in Python
python -c "
from src.monitoring import HealthchecksMonitor

monitor = HealthchecksMonitor()
print('Healthchecks Status:', 'Enabled' if monitor.enabled else 'Disabled (no URL)')

# Note: Without real URL, it won't actually ping
# To get a real URL: https://healthchecks.io
"
```

---

### Test 4: N8N Integration ✅

```powershell
# Start N8N (optional - just for testing code)
docker run -d -p 5678:5678 n8nio/n8n

# Test N8N client
python -c "
from src.integrations import N8NClient

# Without real webhook URL, it shows disabled
n8n = N8NClient()
print('N8N Status:', 'Enabled' if n8n.enabled else 'Disabled')
print('Webhook URL:', n8n.webhook_url or 'Not configured')
"
```

**Expected Output:**
```
N8N Status: Disabled
Webhook URL: Not configured
```

---

### Test 5: Chatwoot Integration ✅

```powershell
# Start Chatwoot (optional)
docker run -d -p 3000:3000 chatwoot/chatwoot

# Test Chatwoot client
python -c "
from src.integrations import ChatwootClient

chatwoot = ChatwootClient()
print('Chatwoot Status:', 'Enabled' if chatwoot.enabled else 'Disabled')
"
```

---

### Test 6: Botpress Integration ✅

```powershell
# Test Botpress client
python -c "
from src.integrations import BotpressClient

botpress = BotpressClient()
print('Botpress Status:', 'Enabled' if botpress.enabled else 'Disabled')
print('Bot ID:', botpress.bot_id or 'Not configured')
"
```

---

### Test 7: Typebot Forms ✅

```powershell
# Test Typebot client
python -c "
from src.integrations import TypebotClient

typebot = TypebotClient()
print('Typebot Status:', 'Enabled' if typebot.enabled else 'Disabled')

# Test form handler
from src.integrations import WhatsAppFormHandler
handler = WhatsAppFormHandler(user_id='test-user')
print('Form Handler: Initialized')
"
```

---

### Test 8: Prometheus Metrics ✅

```powershell
# Test metrics export
python -c "
from src.monitoring import PrometheusMetrics

metrics = PrometheusMetrics()
output = metrics.get_prometheus_output()
print('=== Prometheus Metrics ===')
Write-Host output
"
```

**Expected Output:**
```
# HELP whatsapp_messages_processed_total Total messages processed
# TYPE whatsapp_messages_processed_total counter
whatsapp_messages_processed_total 0
...
```

---

### Test 9: Docker Compose ✅

```powershell
# Test docker-compose configuration
docker-compose config

# Should show the full configuration without errors
```

**Expected Output:**
```
name: whatsapp-automation
services:
  celery-beat:
    ...
  celery-worker:
    ...
  chatwoot:
    ...
  ...
```

---

### Test 10: PM2 Configuration ✅

```powershell
# Install PM2
npm install -g pm2

# Test ecosystem file
node -e "
const config = require('./deploy/pm2_ecosystem.js');
console.log('PM2 Apps:', config.apps.map(a => a.name));
"
```

---

## 🐳 Full Docker Test

### Start Everything with Docker Compose

```powershell
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f whatsapp-bot

# Stop all services
docker-compose down
```

### Start Individual Services

```powershell
# Start only Redis
docker-compose up -d redis

# Start Redis + Bot
docker-compose up -d redis whatsapp-bot

# Start with Celery workers
docker-compose up -d redis celery-worker celery-beat
```

---

## 📊 Run All Tests

```powershell
# Run the test suite
pytest tests/ -v

# Run specific tests
pytest tests/test_alerts.py -v
pytest tests/test_bot.py -v
```

---

## 🔧 Troubleshooting

### Redis Not Connecting?

```powershell
# Check if Redis is running
docker ps | findstr redis

# Restart Redis
docker restart redis

# Or start fresh
docker stop redis; docker rm redis
docker run -d -p 6379:6379 redis
```

### Celery Worker Not Starting?

```powershell
# Check Redis is running
docker ps | findstr redis

# Start worker with more info
celery -A src.integrations.celery_tasks worker --loglevel=debug
```

### Docker Compose Errors?

```powershell
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check for port conflicts
netstat -ano | findstr "6379"  # Redis
netstat -ano | findstr "5678"  # N8N
```

### Import Errors?

```powershell
# Reinstall dependencies
pip uninstall -y -r requirements.txt
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.10+
```

---

## 📋 Testing Checklist

| Feature | Test Command | Status |
|---------|--------------|--------|
| Redis Cache | `python -c "from src.integrations import RedisCache; c=RedisCache(); print(c.enabled)"` | ⬜ |
| Celery Tasks | `celery -A src.integrations.celery_tasks worker --loglevel=info` | ⬜ |
| Healthchecks | `python -c "from src.monitoring import HealthchecksMonitor; print(HealthchecksMonitor().enabled)"` | ⬜ |
| N8N Client | `python -c "from src.integrations import N8NClient; print(N8NClient().enabled)"` | ⬜ |
| Chatwoot | `python -c "from src.integrations import ChatwootClient; print(ChatwootClient().enabled)"` | ⬜ |
| Botpress | `python -c "from src.integrations import BotpressClient; print(BotpressClient().enabled)"` | ⬜ |
| Typebot | `python -c "from src.integrations import TypebotClient; print(TypebotClient().enabled)"` | ⬜ |
| Prometheus | `python -c "from src.monitoring import PrometheusMetrics; print('OK')"` | ⬜ |
| Docker | `docker-compose config` | ⬜ |
| PM2 | `node -e "require('./deploy/pm2_ecosystem.js'); console.log('OK')"` | ⬜ |

---

## 🎯 Next Steps

After testing, you can:

1. **Set up real API keys** for production use
2. **Configure N8N webhooks** for automations
3. **Set up Healthchecks** for monitoring
4. **Deploy with Docker Compose** for production
5. **Scale with multiple instances** using PM2/Nginx

---

## 📞 Need Help?

- **Documentation**: See `INTEGRATIONS.md`
- **Issues**: https://github.com/naitiknahariyaa-png/whatsapp-automation/issues
- **Discussions**: https://github.com/naitiknahariyaa-png/whatsapp-automation/discussions
