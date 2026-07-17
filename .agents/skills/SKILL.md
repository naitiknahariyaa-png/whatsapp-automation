# WhatsApp AI Bot - Complete Skills Index

## 🎯 Available Skills (20+)

### Basic Skills
| Skill | Purpose |
|-------|---------|
| [SKILL.md](SKILL.md) | This index |
| [whatsapp-debug.md](whatsapp-debug.md) | Debug WhatsApp issues |
| [telegram-setup.md](telegram-setup.md) | Setup Telegram alerts |
| [ai-setup.md](ai-setup.md) | Configure AI providers |
| [deployment.md](deployment.md) | Deploy to production |

---

### 1. Communication + Marketing (Auto-Reply/Sales)
| Skill | Description |
|-------|-------------|
| [chatwoot-integration.md](chatwoot-integration.md) | Unified customer inbox |
| [botpress-integration.md](botpress-integration.md) | Visual chatbot flows |
| [typebot-integration.md](typebot-integration.md) | Interactive forms/quiz |
| [n8n-workflow.md](n8n-workflow.md) | Workflow automation |

---

### 2. Auto-Healing (Crash Recovery)
| Skill | Description |
|-------|-------------|
| [pm2-deployment.md](pm2-deployment.md) | Auto-restart processes |
| [healthchecks-monitoring.md](healthchecks-monitoring.md) | Uptime monitoring |
| [netdata-monitoring.md](netdata-monitoring.md) | Real-time metrics |
| [kubernetes/](kubernetes/) | Full self-healing infra |

---

### 3. AI Models (Free/Cheap)
| Skill | Description |
|-------|-------------|
| [ai-setup.md](ai-setup.md) | OpenRouter, Groq, Keyword |
| [ollama-local-ai.md](ollama-local-ai.md) | FREE local AI models |
| [litellm-multi-model.md](litellm-multi-model.md) | 100+ AI models unified |

---

### 4. Database
| Skill | Description |
|-------|-------------|
| [supabase-database.md](supabase-database.md) | Cloud PostgreSQL + Auth |
| (SQLite built-in) | Local database |

---

### 5. Scaling (10,000+ Users)
| Skill | Description |
|-------|-------------|
| [celery-scaling.md](celery-scaling.md) | Async task queue |
| [redis-caching.md](redis-caching.md) | Fast cache + queue backend |
| [nginx-load-balancer.md](nginx-load-balancer.md) | Load balancing |

---

## 🚀 Quick Start

```bash
git clone https://github.com/naitiknahariyaa-png/whatsapp-automation.git
cd whatsapp-automation
pip install -r requirements.txt
python main.py
```

---

## 📚 Skill Categories

### Marketing & Sales
- Chatwoot: Unified inbox
- Botpress: Visual bot builder
- Typebot: Forms & quizzes
- N8N: Automations

### Auto-Healing
- PM2: Process manager
- Healthchecks: Uptime alerts
- Netdata: Performance monitoring

### AI
- OpenRouter: 100+ free models
- Ollama: FREE local AI
- LiteLLM: Unified AI API

### Database
- Supabase: Cloud database
- SQLite: Built-in

### Scaling
- Celery: Task queue
- Redis: Caching
- Nginx: Load balancer

---

## 🔧 All Environment Variables

```bash
# WhatsApp
WHATSAPP_SESSION_DIR=data/session

# AI
OPENROUTER_API_KEY=sk-or-v1-xxx
GROQ_API_KEY=gsk_xxx

# Telegram
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx

# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx

# Queue/Cache
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379

# Monitoring
HEALTHCHECKS_PING_URL=https://hc-ping.com/xxx
```

---

## 📞 Support

- GitHub Issues: Report bugs
- Telegram Alerts: Get notified
- AI Assistants: Ask for help

---

## License

MIT License - Use freely for your business! 🇮🇳
