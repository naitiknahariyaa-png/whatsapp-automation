# Telegram Alerts Skill

## Purpose
Set up and troubleshoot Telegram notifications.

## Setup Steps

### 1. Create Telegram Bot
1. Open Telegram
2. Search: @BotFather
3. Send: /newbot
4. Give bot a name
5. Give bot a username
6. Copy the **Bot Token** (format: `123456789:ABCdef...`)

### 2. Get Your Chat ID
1. Open your new bot
2. Send any message (e.g., "Hello")
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find your chat ID: Look for `"chat":{"id":123456789}`

### 3. Add to .env
```
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=123456789
```

## Test Alerts

```python
from src.utils.alerts import send_alert

# Test basic alert
send_alert("Hello from bot!", "INFO")

# Test error alert
send_alert("Something went wrong!", "ERROR")

# Test warning alert
send_alert("Check this!", "WARNING")
```

## Alert Levels

| Level | When Used |
|-------|-----------|
| INFO | Normal events (bot started, connected) |
| WARNING | Recoverable issues (retry needed) |
| ERROR | Serious problems (bot crashed) |

## Troubleshooting

### Bot Not Responding
```
1. Check bot token is correct
2. Send /start to your bot
3. Visit: https://api.telegram.org/bot<TOKEN>/getUpdates
4. Verify chat_id matches
```

### No Messages Received
```
1. Bot might be blocked - unblock it
2. Chat ID might be wrong
3. Token might be expired (get new one)
```

### Rate Limiting
```
- Alerts are rate-limited (5 min cooldown)
- Check _last_alert_time dict
- Clear if needed
```

## Code Example

```python
from src.utils.alerts import send_alert, with_retry

# Send alert
send_alert("Bot started successfully!", "INFO")

# Use retry decorator
@with_retry(max_attempts=3, alert_on_final_failure=True)
def risky_operation():
    # Your code here
    pass
```

## Alert Message Format

Messages are sent with emoji prefix:
```
🤖 WhatsApp Bot [ERROR]
Your message here
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| TELEGRAM_BOT_TOKEN | Yes | Bot token from @BotFather |
| TELEGRAM_CHAT_ID | Yes | Your Telegram user ID |

## Get Updates URL
```
https://api.telegram.org/bot{TOKEN}/getUpdates
```
