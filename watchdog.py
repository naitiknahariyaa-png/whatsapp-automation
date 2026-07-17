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

Allow passwordless sudo for systemctl restart:
    sudo visudo
    # Add: yourusername ALL=(ALL) NOPASSWD: /bin/systemctl restart whatsapp-bot

Requires the API server to expose a GET /health endpoint that returns 200 OK
when it's genuinely working (not just "process is running").
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import requests
except ImportError:
    print("requests library required: pip install requests")
    sys.exit(1)

HEALTH_URL = os.getenv("HEALTH_CHECK_URL", "http://localhost:8000/health")
SERVICE_NAME = os.getenv("SYSTEMD_SERVICE_NAME", "whatsapp-bot")
TIMEOUT_SECONDS = 10


def check_and_recover():
    """Check bot health and restart if unresponsive."""
    try:
        resp = requests.get(HEALTH_URL, timeout=TIMEOUT_SECONDS)
        if resp.status_code == 200:
            print(f"[{datetime.now()}] ✓ Healthy")
            return
        raise Exception(f"Health check returned {resp.status_code}")
    except requests.exceptions.Timeout:
        reason = f"Connection timed out after {TIMEOUT_SECONDS}s"
    except requests.exceptions.ConnectionError as e:
        reason = f"Connection refused: {e}"
    except Exception as e:
        reason = str(e)
    
    print(f"[{datetime.now()}] ✗ UNHEALTHY: {reason}")
    print(f"[{datetime.now()}] → Restarting service {SERVICE_NAME}...")
    
    # Try to restart the service
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "restart", SERVICE_NAME],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"[{datetime.now()}] ✓ Restart command issued successfully")
        
        # Alert via Telegram
        try:
            from src.utils.alerts import send_alert
            send_alert(
                f"🔄 Bot was unresponsive and has been auto-restarted.\n"
                f"Reason: {reason}",
                level="WARNING"
            )
        except ImportError:
            pass  # Module may not be on path when run standalone
    
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to restart service: {e.stderr}"
        print(f"[{datetime.now()}] ✗ {error_msg}")
        
        try:
            from src.utils.alerts import send_alert
            send_alert(
                f"⚠️ Bot is unhealthy AND restart failed!\n"
                f"Reason: {reason}\n"
                f"Error: {error_msg}",
                level="ERROR"
            )
        except ImportError:
            pass


if __name__ == "__main__":
    check_and_recover()
