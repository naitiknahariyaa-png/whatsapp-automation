# WhatsAutomation API - Implementation Plan

## 1. OBJECTIVE

Create a comprehensive FastAPI application called **whatsautomation** that exposes all 50+ WhatsApp automation functions as REST API endpoints. This will be a test/production-ready model that can be used to build automated applications with all integrations working out of the box.

## 2. CONTEXT SUMMARY

**Current Project:** WhatsApp AI Bot v3.0 with 50+ integrations including:
- **AI Providers:** Groq, OpenRouter, Ollama, HuggingFace, Stable Diffusion, Dify
- **WhatsApp:** OpenWA Gateway, Selenium Web
- **Databases:** Supabase, Redis, MongoDB, Meilisearch, Qdrant
- **CRM:** Notion, Linear, Cal.com, Google Calendar
- **Analytics:** Posthog, Sentry, Plausible, Netdata
- **Storage:** Cloudflare R2, MinIO
- **Notifications:** Discord, Ntfy, Telegram
- **Automation:** n8n, ActivePieces, Celery
- **Chatbots:** Botpress, Typebot, Chatwoot

**Key Files in Repository:**
- `src/ai/providers.py` - AI provider management
- `src/core/database.py` - SQLite database
- `src/core/reply_engine.py` - Auto-reply logic
- `src/integrations/` - 50+ integration clients
- `src/api/webhook.py` - Existing API endpoints

## 3. APPROACH OVERVIEW

Create a new FastAPI application with:
1. All-in-one API endpoints for every function
2. Environment configuration wizard (.env generator)
3. API key validation and health checks
4. Swagger/OpenAPI documentation (auto-generated)
5. Comprehensive test endpoints
6. GitHub-ready structure with CI/CD

## 4. IMPLEMENTATION STEPS

### Step 1: Create API App Structure
- **Goal:** Create the main FastAPI application
- **Method:** Create `whatsautomation/app.py` with all endpoints organized by category
- **File:** `whatsautomation/app.py`

### Step 2: Create Configuration Manager
- **Goal:** Auto-generate .env file with all required API keys
- **Method:** Create `whatsautomation/config_manager.py` that guides users through setup
- **File:** `whatsautomation/config_manager.py`

### Step 3: Create API Endpoints by Category

#### A. AI Endpoints
- `POST /ai/generate` - Generate AI response
- `GET /ai/status` - Get AI provider status
- `POST /ai/configure` - Configure AI provider
- `GET /ai/models` - List available models
- **Files:** `whatsautomation/endpoints/ai.py`

#### B. WhatsApp Endpoints
- `POST /whatsapp/send` - Send message
- `POST /whatsapp/send-image` - Send image
- `GET /whatsapp/status` - Get connection status
- `POST /whatsapp/connect` - Connect/reconnect
- **Files:** `whatsautomation/endpoints/whatsapp.py`

#### C. Database Endpoints
- `GET /db/messages` - Get messages
- `POST /db/keywords` - Add keyword
- `GET /db/stats` - Get statistics
- `POST /db/backup` - Backup database
- **Files:** `whatsautomation/endpoints/database.py`

#### D. Integration Endpoints (All 50+)
- `POST /integrations/{name}/test` - Test integration
- `GET /integrations/list` - List all integrations
- `POST /integrations/configure` - Configure integration
- **Files:** `whatsautomation/endpoints/integrations.py`

### Step 4: Create Environment Setup
- **Goal:** Generate complete .env with all keys
- **Method:** Interactive CLI or API endpoint to configure all keys
- **File:** `whatsautomation/.env.example`

### Step 5: Create Docker Configuration
- **Goal:** Containerized deployment
- **Method:** Create Dockerfile and docker-compose.yml
- **Files:** `whatsautomation/Dockerfile`, `whatsautomation/docker-compose.yml`

### Step 6: Create README and Documentation
- **Goal:** Clear documentation for all endpoints
- **Method:** Auto-generate from FastAPI docs + custom README
- **Files:** `whatsautomation/README.md`

### Step 7: GitHub Setup
- **Goal:** Push to GitHub with proper structure
- **Method:** 
  - Create new repo `whatsautomation-api`
  - Add .gitignore, LICENSE
  - Push with proper branch structure
- **Command:** `git push` to new repository

## 5. TESTING AND VALIDATION

### API Health Check
```bash
curl http://localhost:8000/health
```

### Test AI Generation
```bash
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "context": ""}'
```

### Validate All Integrations
```bash
curl http://localhost:8000/integrations/list
curl -X POST http://localhost:8000/integrations/{name}/test
```

### Swagger Documentation
- Open http://localhost:8000/docs for interactive API docs
- Open http://localhost:8000/redoc for ReDoc documentation

---

## API Keys Required (Complete List)

### FREE Services (No Credit Card)
| Service | Key Variable | Signup URL |
|---------|-------------|------------|
| Groq | `GROQ_API_KEY` | https://console.groq.com/keys |
| OpenRouter | `OPENROUTER_API_KEY` | https://openrouter.ai/keys |
| Ollama | `OLLAMA_URL` | https://ollama.com |
| HuggingFace | `HUGGINGFACE_API_KEY` | https://huggingface.co/settings/tokens |
| Meilisearch | `MEILISEARCH_HOST` | https://www.meilisearch.com |
| Qdrant | `QDRANT_URL` | https://cloud.qdrant.io |
| Supabase | `SUPABASE_URL`, `SUPABASE_KEY` | https://supabase.com |
| Redis | `REDIS_URL` | https://redis.io |
| MongoDB | `MONGODB_URI` | https://mongodb.com |
| Notion | `NOTION_API_KEY` | https://www.notion.so/my-integrations |
| Linear | `LINEAR_API_KEY` | https://linear.app/settings/api |
| Cal.com | `CAL_API_KEY` | https://cal.com/settings/developer/api |
| Posthog | `POSTHOG_API_KEY` | https://app.posthog.com/settings/project |
| Sentry | `SENTRY_DSN` | https://sentry.io |
| Plausible | `PLAUSIBLE_URL` | https://plausible.io |
| Discord | `DISCORD_WEBHOOK` | Discord channel settings |
| Ntfy | `NTFY_URL` | https://ntfy.sh |
| n8n | `N8N_WEBHOOK_URL` | https://n8n.io |
| ActivePieces | `ACTIVPIECES_URL` | https://www.activepieces.com |
| Botpress | `BOTPRESS_URL` | https://botpress.com |
| Typebot | `TYPEBOT_URL` | https://typebot.io |
| Chatwoot | `CHATWOOT_URL` | https://www.chatwoot.com |

### PAID/India Specific
| Service | Key Variable | Signup URL |
|---------|-------------|------------|
| OpenWA Gateway | `OPENWA_URL`, `OPENWA_API_KEY` | https://openwa.io |
| Telegram | `TELEGRAM_BOT_TOKEN` | @BotFather |
| Google Calendar | `GOOGLE_CREDENTIALS_PATH` | Google Cloud Console |
| Cloudflare R2 | `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID` | https://dash.cloudflare.com |
| MinIO | `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY` | Self-hosted |
