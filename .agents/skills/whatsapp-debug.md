# WhatsApp Debug Skill

## Purpose
Debug WhatsApp Web automation issues quickly.

## Common Problems & Solutions

### 1. WhatsApp Web Not Loading
```
Problem: Browser opens but WhatsApp doesn't load
Solution:
- Delete Chrome profile: rm -rf data/chrome-profile-*
- Check internet connection
- Try clearing cookies
```

### 2. QR Code Not Appearing
```
Problem: WhatsApp loads but no QR code
Solution:
- Delete session: rm data/session/session.json
- Clear cookies in browser
- Try different Chrome profile
```

### 3. Session Expired
```
Problem: "Phone not connected" error
Solution:
- Delete: data/session/session.json
- Delete: data/chrome-profile-*
- Re-scan QR code
```

### 4. WhatsApp Selectors Not Found
```
Problem: "Element not found" errors
Cause: WhatsApp updates HTML frequently
Solution:
- Use multiple fallback selectors
- Check CHAT_LIST_SELECTORS array
- Update selectors in whatsapp_client.py
```

### 5. Auto-Reply Not Working
```
Problem: Bot doesn't send replies
Debug Steps:
1. Check if AI is configured: AIManager.get_status()
2. Check keywords: db.get_all_keywords()
3. Check WhatsApp selectors
4. Check message callback
```

### 6. Browser Crashes
```
Problem: Chrome closes unexpectedly
Solution:
- Reduce memory: Use headless mode
- Clear old profiles: rm -rf data/chrome-profile-*
- Update Chrome/ChromeDriver
```

## Debug Commands

```bash
# Check if Selenium is installed
python -c "from selenium import webdriver; print('OK')"

# Check Chrome
google-chrome --version

# Clear all sessions
rm -rf data/chrome-profile-* data/session

# Test WhatsApp manually
python -c "
from src.core.whatsapp_client import WhatsAppClient
wc = WhatsAppClient(verbose=True)
wc.connect()
"
```

## Key Files to Check

| File | What to Check |
|------|---------------|
| `whatsapp_client.py` | Line ~270: start_monitoring() |
| `whatsapp_client.py` | Line ~100: Selectors |
| `reply_engine.py` | process_message() |
| `.env` | API keys configured |

## Selector Testing

```python
# Test selectors in browser console
document.querySelectorAll('[data-testid="chat-list-item"]')
document.querySelectorAll('[data-testid="msg-list"]')
document.querySelector('[data-testid="conversation-compose-box-input"]')
```

## Contact Debug Info

When reporting issues, include:
1. Python version: `python --version`
2. Selenium version: `pip show selenium`
3. Chrome version: `google-chrome --version`
4. Error message
5. Steps to reproduce
