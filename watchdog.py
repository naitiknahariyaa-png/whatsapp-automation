"""
====================================================================
WATCHDOG - Auto-restart if bot freezes
====================================================================

Watchdog — runs as its own tiny cron job, separate from the bot.
Purpose: systemd's Restart=always only catches CRASHES. If the bot is
alive but frozen (stuck in an infinite loop, deadlocked, etc.), systemd
won't notice. This script catches that case.

Setup (Linux):
    crontab -e
    */5 * * * * /path/to/venv/bin/python /path/to/watchdog.py >> /path/to/logs/watchdog.log 2>&1

Requires main.py to expose a GET /health endpoint that returns 200 OK
when it's genuinely working (not just "process is running").
"""

import os
import subprocess
import requests
from datetime import datetime


HEALTH_URL = os.getenv("HEALTH_CHECK_URL", "http://localhost:8000/health")
SERVICE_NAME = os.getenv("SYSTEMD_SERVICE_NAME", "whatsapp-bot")
TIMEOUT_SECONDS = 10


def check_and_recover():
    try:
        resp = requests.get(HEALTH_URL, timeout=TIMEOUT_SECONDS)
        if resp.status_code == 200:
            print(f"[{datetime.now()}] Healthy.")
            return
        raise Exception(f"Health check returned {resp.status_code}")
    except Exception as e:
        print(f"[{datetime.now()}] UNHEALTHY: {e}. Restarting service...")
        try:
            subprocess.run(["sudo", "systemctl", "restart", SERVICE_NAME], check=True)
            print(f"[{datetime.now()}] Restart command issued.")
        except Exception as restart_error:
            print(f"[{datetime.now()}] FAILED to restart: {restart_error}")

        # Also alert, using the same alerts module as the bot
        try:
            from src.utils.alerts import send_alert
            send_alert(f"Bot was unresponsive and has been auto-restarted. Reason: {e}", level="WARNING")
        except ImportError:
            pass  # alerts module not on path when run standalone — that's fine


if __name__ == "__main__":
    check_and_recover()
