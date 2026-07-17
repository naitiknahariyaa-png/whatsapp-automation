# Cursor IDE - Project Setup

## Quick Start

1. Open Cursor IDE
2. Open folder: `naitiknahariyaa-png/whatsapp-automation`
3. AI will automatically read `CLAUDE.md` for context

---

## 🤖 Using AI in Cursor

### Chat (Ctrl+L)
Ask questions about the code:
- "How does WhatsApp monitoring work?"
- "Fix the auto-reply bug"
- "Add Telegram webhook support"

### Code Generation (Tab)
Accept AI suggestions while typing code.

### Inline Chat (Ctrl+I)
Edit specific parts of code with AI help.

---

## 📁 Key Files for AI Context

When asking AI to help, reference these files:

```
src/core/whatsapp_client.py  ← WhatsApp automation
src/core/reply_engine.py      ← Auto-reply logic  
src/ai/providers.py           ← AI integration
src/cli/commands.py           ← Menu commands
```

---

## 🔧 Development Workflow

1. **Clone & Setup**
```bash
git clone https://github.com/naitiknahariyaa-png/whatsapp-automation.git
cd whatsapp-automation
pip install -r requirements.txt
```

2. **Run Locally**
```bash
python main.py
```

3. **Test Changes**
```bash
python -m pytest tests/
```

4. **Push Changes**
```bash
git checkout -b feature-name
git add .
git commit -m "feat: your feature"
git push origin feature-name
```

---

## ⚠️ Important Notes

- WhatsApp Web HTML changes frequently - keep fallback selectors
- Chrome session files can get corrupted - delete `data/chrome-profile-*`
- Keep `.env` private - never commit API keys

---

## 🐛 Debugging Tips

### WhatsApp not connecting?
- Delete `data/chrome-profile-*` folders
- Re-scan QR code

### AI not responding?
- Check `OPENROUTER_API_KEY` in `.env`
- Test API key at openrouter.ai

### Telegram alerts not working?
- Check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- Test bot at t.me/your_bot

---

**Happy coding with Cursor! 🚀**
