# WhatsApp AI Bot - Skills Index

## Available Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [whatsapp-debug.md](whatsapp-debug.md) | Debug WhatsApp issues | Bot not working |
| [telegram-setup.md](telegram-setup.md) | Setup Telegram alerts | Alerts not working |
| [ai-setup.md](ai-setup.md) | Configure AI providers | AI not responding |
| [deployment.md](deployment.md) | Deploy to production | Ready to go live |

---

## Quick Start

### 1. First Time Setup
```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your API keys to .env

# Run
python main.py
```

### 2. Connect WhatsApp
1. Choose menu option **2** (Setup WhatsApp)
2. Scan QR code with your phone
3. Wait for "Connected"

### 3. Start Bot
1. Choose menu option **1** (Start Auto-Reply)
2. Bot will scan all chats
3. Auto-replies will start

---

## AI Setup

### Get OpenRouter API Key (FREE)
1. Go to https://openrouter.ai/keys
2. Sign up free
3. Create API key
4. Add to `.env`:
```
OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

---

## Telegram Setup

### Get Your Chat ID
1. Message @BotFather → Create bot
2. Get bot token
3. Message your bot
4. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Copy your `chat_id`

Add to `.env`:
```
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
```

---

## Common Issues

| Problem | Solution |
|---------|----------|
| WhatsApp not connecting | Delete `data/chrome-profile-*` |
| AI not responding | Check `OPENROUTER_API_KEY` |
| Telegram alerts not working | Verify `TELEGRAM_BOT_TOKEN` |
| Bot crashes | Check `watchdog.py` logs |

---

## Development

### Run Tests
```bash
python -m pytest tests/
```

### Run Bot
```bash
python main.py
```

### Debug Mode
```python
# In main.py, set:
verbose=True
```

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point |
| `src/core/whatsapp_client.py` | WhatsApp automation |
| `src/ai/providers.py` | AI integration |
| `src/utils/alerts.py` | Telegram alerts |
| `src/core/database.py` | SQLite database |

---

## Support

- GitHub Issues: Report bugs
- Telegram: Get alerts on your phone
- GitHub Discussions: Ask questions

---

## License

MIT License - Use freely for your business!
