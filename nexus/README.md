# 🤖 NEXUS Platform v3.0

> **Unified AI Automation Platform** — One app, infinite possibilities.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-20+-blue.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue.svg)](https://www.typescriptlang.org/)

## 🎯 What is NEXUS?

NEXUS is a **single unified AI automation platform** that connects:

- 📱 **WhatsApp** — Self-hosted automation using Baileys (no API costs!)
- 💬 **Telegram** — Bot management & team control
- 🐙 **GitHub** — Code analysis, PR automation, repo monitoring
- 🌐 **Web** — Research, scraping, data collection
- 🤖 **AI Agents** — Intelligent automation powered by LangGraph

**Not 5 different apps. ONE Super App.**

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Channel AI** | Unified AI processing across all channels |
| 📱 **WhatsApp Automation** | Self-hosted, no Meta API costs |
| 💬 **Telegram Control** | Admin bot with full command system |
| 🐙 **GitHub Integration** | PR reviews, issue management, monitoring |
| 🌐 **Web Research** | Playwright-powered scraping & data extraction |
| 📊 **Unified Dashboard** | Control everything from one place |
| 🔒 **Secure** | Auth, rate limiting, XSS protection |
| 🐳 **Docker Ready** | One-command deployment |

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

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/status` | GET | Platform status |
| `/api/whatsapp/connect` | POST | Connect WhatsApp |
| `/api/whatsapp/send` | POST | Send WhatsApp message |
| `/api/github/prs` | GET | Get GitHub PRs |
| `/api/github/issues` | GET | Get GitHub issues |
| `/api/web/scrape` | POST | Scrape web page |
| `/api/chat` | POST | Chat with AI agent |
| `/api/webhook` | POST | Webhook for messages |

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
│   ├── agents/          # AI Agent core
│   ├── connectors/       # Channel integrations
│   │   ├── whatsapp.ts   # WhatsApp (Baileys)
│   │   ├── telegram.ts   # Telegram (Telegraf)
│   │   ├── github.ts     # GitHub (Octokit)
│   │   └── web.ts        # Web (Playwright)
│   ├── core/             # Core utilities
│   ├── types/            # TypeScript types
│   ├── config/           # Configuration
│   └── index.ts          # Main entry point
├── tests/                # Test files
├── deploy/               # Deployment configs
├── package.json
├── tsconfig.json
├── Dockerfile
└── docker-compose.yml
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Credits

Built with:
- [Baileys](https://github.com/adiwajshing/Baileys) - WhatsApp protocol
- [Telegraf](https://github.com/telegraf/telegraf) - Telegram bot SDK
- [Octokit](https://github.com/octokit/rest.js) - GitHub API
- [Playwright](https://github.com/microsoft/playwright) - Web automation
- [LangChain](https://github.com/langchain-ai/langchain) - AI orchestration

---

**ONE APP. INFINITE POSSIBILITIES.**

🤖 **NEXUS** - Your Universal Automation Platform
