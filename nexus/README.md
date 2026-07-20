# 🤖 NEXUS Platform v3.0

> **The Ultimate Unified AI Automation Platform** — ONE APP. INFINITE POSSIBILITIES.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-20+-blue.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue.svg)](https://www.typescriptlang.org/)

## 🎯 What is NEXUS?

NEXUS is a **single unified AI automation platform** that connects:

- 📱 **WhatsApp** — 3 libraries: Baileys, whatsapp-web.js, open-wa
- 💬 **Telegram** — Bot management & team control
- 🐙 **GitHub** — Code analysis, PR automation, repo monitoring
- 🌐 **Web** — Research, scraping, data collection
- 🤖 **AI Agents** — LangChain + GPT-4 Turbo with memory
- 🔮 **Vector DB** — Qdrant/Chroma for semantic search
- ⚡ **Job Queue** — BullMQ for background tasks
- 📅 **Calendar** — Cal.com for bookings & appointments
- 👥 **CRM** — Twenty for contacts, deals, tasks
- 📄 **Documents** — PDF parsing & intake forms

**Not 12 different apps. ONE Super App.**

## ✨ Features

| Module | Features |
|--------|----------|
| 📱 **WhatsApp** | Baileys, whatsapp-web.js, open-wa - QR connect, multi-device, auto-replies |
| 💬 **Telegram** | Telegraf bot - Commands, broadcasts, alerts, admin panel |
| 🐙 **GitHub** | Octokit - PR reviews, issues, repo monitoring, auto-assign |
| 🌐 **Web** | Playwright - Scraping, research, screenshots, form filling |
| 🤖 **AI Agent** | LangChain + GPT-4 - Intent detection, RAG, memory |
| 🔮 **Vector DB** | Qdrant/Chroma - Semantic search, chat memory |
| ⚡ **Job Queue** | BullMQ - Scheduled messages, reminders, background tasks |
| 📅 **Calendar** | Cal.com - Bookings, appointments, availability |
| 👥 **CRM** | Twenty - Contacts, deals, lead qualification |
| 📄 **Documents** | PDF parsing, intake forms, form field extraction |

## 🚀 Quick Start

### Prerequisites

- Node.js 20+
- Docker & Docker Compose (optional)
- WhatsApp device for connection
- Telegram Bot Token (from @BotFather)
- GitHub Personal Access Token
- OpenAI API Key (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/naitiknahariyaa-png/whatsapp-automation.git
cd whatsapp-automation/nexus

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Start development
npm run dev

# Or use Docker
docker-compose up -d
```

### Configuration

Edit `.env` with your credentials:

```env
PORT=3000
TELEGRAM_BOT_TOKEN=your_telegram_token
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_key
DATABASE_URL=postgresql://user:pass@localhost:5432/nexus
REDIS_URL=redis://localhost:6379
```

## 📚 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      🤖 NEXUS CORE                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   AI Agent  │  │   Message   │  │   Storage   │        │
│  │   (GPT-4)   │  │     Bus     │  │   (Redis)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                         CONNECTORS                           │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────┐  │
│  │ WhatsApp  │  │ Telegram  │  │  GitHub   │  │   Web   │  │
│  │ (Baileys) │  │ (Telegraf)│  │ (Octokit) │  │(Playwright)│ │
│  └───────────┘  └───────────┘  └───────────┘  └─────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      📊 DASHBOARD                            │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ API Endpoints

### Core
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/status` | GET | Platform status |
| `/api/webhook` | POST | Webhook for messages |

### WhatsApp
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/whatsapp/connect` | POST | Connect WhatsApp |
| `/api/whatsapp/send` | POST | Send message |
| `/api/whatsapp/multi/connect` | POST | Connect with specific library |

### GitHub
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/github/prs` | GET | List PRs |
| `/api/github/issues` | GET | List issues |

### AI & Vector
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai/chat` | POST | Chat with AI |
| `/api/ai/memory/add` | POST | Add to memory |
| `/api/ai/memory/search` | GET | Search memory |
| `/api/vector/add` | POST | Add document |
| `/api/vector/search` | GET | Semantic search |

### Jobs & Queue
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/queue/add` | POST | Add job |
| `/api/queue/stats` | GET | Queue stats |

### Calendar
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/calendar/booking` | POST | Create booking |
| `/api/calendar/events` | GET | List events |

### CRM
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/crm/contact` | POST | Create contact |
| `/api/crm/contacts` | GET | List contacts |
| `/api/crm/deal` | POST | Create deal |
| `/api/crm/stats` | GET | CRM stats |

### Documents
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/document/parse` | POST | Parse PDF/document |
| `/api/document/intake-form` | POST | Parse intake form |

## 💬 Telegram Commands

- `/start` - Start the bot
- `/help` - Show all commands
- `/devices` - List WhatsApp devices
- `/status` - System status
- `/stats` - View analytics
- `/github` - GitHub actions
- `/research` - Web research

## 🐙 GitHub Features

- **PR Management**: List, review, merge, label PRs
- **Issue Tracking**: Create, update, search issues
- **Repo Monitoring**: Watch repos for activity
- **Auto-assign**: Automatically assign PRs/Issues

## 📱 WhatsApp Features

- **Multi-device**: Connect multiple WhatsApp accounts
- **Auto-replies**: AI-powered responses
- **Broadcast**: Send to multiple contacts
- **Media support**: Images, documents, voice
- **No API costs**: Uses Baileys protocol

## 🌐 Web Features

- **Scraping**: Extract data from any website
- **Research**: AI-powered topic research
- **Screenshots**: Capture full page screenshots
- **Form filling**: Automate web forms

## 🐳 Docker

```bash
# Build image
docker build -t nexus-platform .

# Run container
docker run -d -p 3000:3000 --env-file .env nexus-platform

# Or use docker-compose
docker-compose up -d
```

## 📦 Project Structure

```
nexus/
├── src/
│   ├── agents/              # AI Agent core
│   │   ├── core.ts         # Basic AI agent
│   │   └── langchain.ts    # LangChain integration
│   ├── connectors/         # Channel integrations
│   │   ├── whatsapp.ts      # WhatsApp (Baileys)
│   │   ├── whatsapp-multi.ts # Multi-library WA support
│   │   ├── telegram.ts     # Telegram (Telegraf)
│   │   ├── github.ts       # GitHub (Octokit)
│   │   └── web.ts          # Web (Playwright)
│   ├── core/               # Core utilities
│   │   ├── vector-store.ts  # Qdrant/Chroma
│   │   ├── job-queue.ts     # BullMQ
│   │   ├── calendar.ts       # Cal.com
│   │   ├── crm.ts           # Twenty CRM
│   │   └── document-parser.ts # PDF parsing
│   ├── types/              # TypeScript types
│   ├── config/            # Configuration
│   └── index.ts            # Main entry point
├── tests/                  # Test files
├── deploy/                 # Deployment configs
├── package.json
├── tsconfig.json
├── Dockerfile
└── docker-compose.yml
```

## 🔮 Vector Store (RAG)

```typescript
// Add knowledge to vector store
await nexus.vectorStore.addDocument({
  id: 'doc-1',
  content: 'Our product pricing is $99/month...',
  metadata: { source: 'pricing-page' }
});

// Search knowledge
const results = await nexus.vectorStore.search('pricing');
```

## ⚡ Job Queue (BullMQ)

```typescript
// Schedule a message
await nexus.jobQueue.addJob('notifications', {
  name: 'send-reminder',
  data: { userId: '123', message: 'Meeting in 5 min' },
  options: { delay: 300000 } // 5 minutes
});
```

## 📅 Calendar (Cal.com)

```typescript
// Create booking
const booking = await nexus.calendar.createBooking({
  eventTypeSlug: 'consultation',
  startTime: '2024-01-15T10:00:00Z',
  name: 'John Doe',
  email: 'john@example.com'
});
```

## 👥 CRM (Twenty)

```typescript
// Create contact
const contact = await nexus.crm.createContact({
  name: 'Jane Smith',
  email: 'jane@company.com',
  company: 'Acme Corp',
  tags: ['hot-lead', 'enterprise']
});

// Create deal
await nexus.crm.createDeal({
  title: 'Enterprise License',
  value: 50000,
  stage: 'proposal',
  contactId: contact.id
});
```

## 📄 Document Parser

```typescript
// Parse intake form
const intake = await documentParser.parseIntakeForm(document);
// Returns: { clientName, email, phone, caseType, ... }
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Credits & Inspiration

Built with inspiration from these amazing open-source projects:

### WhatsApp
- [Baileys](https://github.com/WhiskeySockets/Baileys) - WhatsApp Web Protocol
- [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js) - WhatsApp Web API
- [open-wa](https://github.com/open-wa/wa-automate-nodejs) - WA Automation

### AI & Orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - AI framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration

### Vector Databases
- [Qdrant](https://github.com/qdrant/qdrant) - Vector search engine
- [Chroma](https://github.com/chroma-core/chroma) - Embeddings database

### Queue & Jobs
- [BullMQ](https://github.com/taskforcesh/bullmq) - Redis queue
- [Celery](https://github.com/celery/celery) - Task queue

### Business Tools
- [Cal.com](https://github.com/calcom/cal.com) - Scheduling platform
- [Twenty](https://github.com/twentyhq/twenty) - CRM platform
- [n8n](https://github.com/n8n-io/n8n) - Workflow automation

### Other Integrations
- [Telegraf](https://github.com/telegraf/telegraf) - Telegram SDK
- [Octokit](https://github.com/octokit/rest.js) - GitHub API
- [Playwright](https://github.com/microsoft/playwright) - Browser automation
- [PyMuPDF](https://github.com/PyMuPDF/PyMuPDF) - PDF processing

---

**ONE APP. INFINITE POSSIBILITIES.**

🤖 **NEXUS** - Your Ultimate Universal Automation Platform v3.0
