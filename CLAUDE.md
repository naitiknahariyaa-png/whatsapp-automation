# Claude Project Instructions

## WhatsApp AI Bot - Project Context

### What This Project Does
A WhatsApp auto-reply bot powered by AI for Indian businesses. It:
- Monitors all WhatsApp chats
- Skips group chats
- Responds to messages using AI (OpenRouter/Groq)
- Sends Telegram alerts on errors
- Has a CLI menu interface

### Key Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point, CLI menu |
| `src/core/whatsapp_client.py` | WhatsApp Web automation (Selenium) |
| `src/core/reply_engine.py` | Auto-reply logic |
| `src/ai/providers.py` | AI providers (OpenRouter, Groq, Keyword) |
| `src/utils/alerts.py` | Telegram alerts |
| `src/core/database.py` | SQLite database |

### Important Rules

1. **Don't break WhatsApp selectors** - WhatsApp changes HTML often. Keep multiple fallback selectors.

2. **Keep session handling** - WhatsApp sessions are saved to `data/session/session.json`

3. **Telegram alerts are critical** - `send_alert()` function must work for production use

4. **Database is SQLite** - File: `data/whatsapp.db`

### Running the Bot

```bash
pip install -r requirements.txt
python main.py
```

### Menu Options
- 1: Start Auto-Reply
- 2: Setup WhatsApp (scan QR)
- 3: Setup AI
- 4: Add Keywords
- 5: View Stats

### API Keys Needed
- OpenRouter API key (for AI)
- Telegram Bot Token + Chat ID (for alerts)

### Common Issues
- WhatsApp Web selectors change frequently - use fallback selectors
- Chrome profile issues - delete `data/chrome-profile-*` folders
- Session expired - scan QR code again

### Environment Variables
```
OPENROUTER_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```
