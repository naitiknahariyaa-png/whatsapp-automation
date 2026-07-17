# 🔗 GitHub Integration Guide

## WhatsApp AI Bot GitHub Setup

Your project is ready for GitHub integration with AI tools like Claude Code, GitHub Copilot, and more.

---

## 📁 Project Structure on GitHub

```
naitiknahariyaa-png/whatsapp-automation
├── 📄 README.md
├── 📄 .env.example
├── 📄 requirements.txt
├── 📄 main.py
├── 📄 webhook.py
├── 📄 watchdog.py
├── 📁 src/
│   ├── 📁 cli/           # CLI menu commands
│   ├── 📁 core/          # WhatsApp client, DB, config
│   ├── 📁 ai/            # AI providers (OpenRouter, Groq)
│   ├── 📁 api/           # FastAPI web server
│   └── 📁 utils/         # Alerts, helpers
├── 📁 tests/             # pytest tests
├── 📁 .github/           # GitHub Actions
└── 📄 config.yaml        # Configuration
```

---

## 🤖 Connect to AI Coding Assistants

### 1. Claude Code (claude.ai/code)

1. Go to [claude.ai/code](https://claude.ai/code)
2. Click **Connect to GitHub**
3. Authorize the GitHub App
4. Search for: `naitiknahariyaa-png/whatsapp-automation`
5. Select branch: `refactored-structure`
6. Click **Add Project**

**What you can do:**
- Ask: "Fix the auto-reply bug"
- Ask: "Add Telegram webhook support"
- Ask: "Explain how WhatsApp monitoring works"

---

### 2. GitHub Copilot (VS Code)

1. Install **GitHub Copilot** extension in VS Code
2. Sign in with GitHub
3. Open your project folder
4. Start coding with AI suggestions

**Commands:**
- `Ctrl+Shift+P` → "Copilot: Open Chat"
- `Ctrl+I` → Inline AI suggestions

---

### 3. Cursor IDE

1. Download [Cursor](https://cursor.sh)
2. Connect GitHub account
3. Open project: `naitiknahariyaa-png/whatsapp-automation`
4. AI will understand your codebase

---

### 4. GitHub Actions (CI/CD)

Your project has automatic CI/CD configured:

```yaml
# Runs on every push:
✅ Install dependencies
✅ Run pytest tests
✅ Lint code with flake8
✅ Build package
✅ Deploy (on main branch)
```

**View CI Status:**
```
https://github.com/naitiknahariyaa-png/whatsapp-automation/actions
```

---

## 🔄 Sync Updates

When you push new code, AI tools will see the changes automatically.

### To Force Sync in Claude Code:
1. Click the **Sync** icon
2. Or press `Ctrl+R` to refresh

---

## 🌿 Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable release |
| `refactored-structure` | Latest features (recommended) |

---

## 📋 Files to Share with AI

When asking AI to help, share these key files:

| File | Description |
|------|-------------|
| `main.py` | Entry point, menu system |
| `src/core/whatsapp_client.py` | WhatsApp Web automation |
| `src/ai/providers.py` | AI response logic |
| `src/core/reply_engine.py` | Auto-reply engine |
| `README.md` | Project overview |

---

## ⚙️ Project Settings

### Recommended Settings for AI Tools:

```markdown
# Project Instructions (add to Claude Code)

## Coding Style
- Python 3.11+
- Type hints on functions
- docstrings for classes

## Architecture
- Modular structure (src/cli, src/core, src/ai)
- CLI commands in src/cli/commands.py
- WhatsApp logic in src/core/whatsapp_client.py

## Don't Change
- src/utils/alerts.py (Telegram integration)
- Database schema in src/core/database.py
```

---

## 🚀 Quick Commands

```bash
# Clone the project
git clone https://github.com/naitiknahariyaa-png/whatsapp-automation.git
cd whatsapp-automation
git checkout refactored-structure

# Install & run
pip install -r requirements.txt
python main.py
```

---

## 📞 Support

- **GitHub Issues:** Report bugs
- **Pull Requests:** Submit improvements
- **AI Assistants:** Get instant help

---

**Happy Coding! 🎉**
