"""
====================================================================
SELF-HEALING UTILITIES
====================================================================

1. send_alert()      -> pings you on Telegram when something breaks
2. @with_retry        -> auto-retries transient failures (AI timeout, network blip)
                         before giving up

Setup:
1. Message @BotFather on Telegram -> /newbot -> get a bot token
2. Message your new bot once, then visit:
   https://api.telegram.org/bot<TOKEN>/getUpdates
   -> find your "chat":{"id": ...} value
3. Add to .env:
   TELEGRAM_BOT_TOKEN=xxxx
   TELEGRAM_CHAT_ID=xxxx
"""

import os
import time
import logging
import functools
import requests


logger = logging.getLogger("whatsapp_bot")


TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


_last_alert_time: dict[str, float] = {}
ALERT_COOLDOWN_SECONDS = 300  # don't spam you more than once per 5 min per error type


def send_alert(message: str, level: str = "ERROR") -> None:
    """Send a message to your Telegram. Falls back to just logging if not configured."""
    logger.log(logging.ERROR if level == "ERROR" else logging.WARNING, message)

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return  # alerts not configured yet — logging above still happens

    # Cooldown so a crash-loop doesn't send you 500 messages
    key = message[:50]
    now = time.time()
    if now - _last_alert_time.get(key, 0) < ALERT_COOLDOWN_SECONDS:
        return
    _last_alert_time[key] = now

    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"🤖 WhatsApp Bot [{level}]\n{message}",
            },
            timeout=5,
        )
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")


def with_retry(max_attempts: int = 3, delay_seconds: float = 2.0, alert_on_final_failure: bool = True):
    """
    Decorator: retries a function on failure before giving up.
    Use on anything that can transiently fail — AI calls, WhatsApp sends, DB writes.

    Example:
        @with_retry(max_attempts=3)
        def call_ai_provider(prompt):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}"
                    )
                    if attempt < max_attempts:
                        time.sleep(delay_seconds * attempt)  # backoff: 2s, 4s, 6s...

            if alert_on_final_failure:
                send_alert(
                    f"{func.__name__} failed after {max_attempts} attempts: {last_exception}"
                )
            raise last_exception

        return wrapper
    return decorator
