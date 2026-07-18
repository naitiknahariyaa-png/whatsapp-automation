"""
Healthchecks Monitoring - Cron Job and Uptime Monitoring
Monitor bot health and get alerts when checks miss.
"""

import os
import logging
import requests
import time
import threading
from typing import Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthchecksMonitor:
    """
    Healthchecks.io Client
    
    Features:
    - Heartbeat monitoring (regular "I'm alive" pings)
    - Cron monitoring (track scheduled tasks)
    - Failure alerts (Email, Slack, Telegram, PagerDuty)
    - Uptime reports (monthly uptime %)
    
    Setup:
    1. Create account at https://healthchecks.io
    2. Create new check: "whatsapp-bot-heartbeat"
    3. Copy the ping URL
    
    Environment:
    - HEALTHCHECKS_PING_URL=https://hc-ping.com/xxx
    - HEALTHCHECKS_API_KEY=xxx
    """
    
    def __init__(
        self,
        ping_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.ping_url = ping_url or os.getenv("HEALTHCHECKS_PING_URL", "")
        self.api_key = api_key or os.getenv("HEALTHCHECKS_API_KEY", "")
        self.enabled = bool(self.ping_url)
        
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        if self.enabled:
            logger.info(f"✅ Healthchecks configured")
        else:
            logger.warning("⚠️ Healthchecks not configured (set HEALTHCHECKS_PING_URL)")
    
    def ping(self, message: str = "") -> bool:
        """
        Send success ping to Healthchecks
        
        Args:
            message: Optional message (e.g., "✅ Bot running")
            
        Returns:
            Success status
        """
        if not self.enabled:
            return False
        
        try:
            url = self.ping_url
            if message:
                url = f"{self.ping_url}/{requests.utils.quote(message)}"
            
            response = requests.get(url, timeout=10)
            return response.status_code in [200, 202]
            
        except Exception as e:
            logger.error(f"Healthchecks ping error: {e}")
            return False
    
    def ping_start(self) -> bool:
        """Ping that job started"""
        return self.ping("started")
    
    def ping_success(self) -> bool:
        """Ping that job succeeded"""
        return self.ping("success")
    
    def ping_fail(self, message: str = "failed") -> bool:
        """
        Ping that job failed
        
        Args:
            message: Failure message
            
        Returns:
            Success status
        """
        if not self.enabled:
            return False
        
        try:
            url = f"{self.ping_url}/fail"
            if message:
                url = f"{url}/{requests.utils.quote(message)}"
            
            response = requests.get(url, timeout=10)
            return response.status_code in [200, 202]
            
        except Exception as e:
            logger.error(f"Healthchecks ping_fail error: {e}")
            return False
    
    def ping_custom(self, exit_code: int) -> bool:
        """
        Ping with custom exit code
        
        Args:
            exit_code: Exit code (0 = success, non-zero = fail)
            
        Returns:
            Success status
        """
        if not self.enabled:
            return False
        
        try:
            if exit_code == 0:
                return self.ping_success()
            else:
                return self.ping_fail(f"exit_code_{exit_code}")
        except:
            return False


class HeartbeatThread:
    """
    Background thread that sends heartbeats to Healthchecks
    
    Usage:
        monitor = HealthchecksMonitor()
        heartbeat = HeartbeatThread(monitor, interval=300)  # 5 minutes
        heartbeat.start()
    """
    
    def __init__(self, monitor: HealthchecksMonitor, interval: int = 300):
        """
        Args:
            monitor: HealthchecksMonitor instance
            interval: Seconds between heartbeats (default 5 minutes)
        """
        self.monitor = monitor
        self.interval = interval
        self.running = False
        self.thread = None
    
    def _loop(self):
        """Heartbeat loop"""
        while self.running:
            try:
                self.monitor.ping("❤️ heartbeat")
                logger.debug(f"Heartbeat sent (interval={self.interval}s)")
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
            
            # Sleep in small increments to allow stopping
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def start(self):
        """Start heartbeat thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        logger.info(f"Heartbeat thread started (interval={self.interval}s)")
    
    def stop(self):
        """Stop heartbeat thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Heartbeat thread stopped")


def setup_healthchecks():
    """Guide user to setup Healthchecks"""
    print("""
╔══════════════════════════════════════════════════════════╗
║           Healthchecks Monitoring Setup                  ║
╚══════════════════════════════════════════════════════════╝

Option 1: Cloud (Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Go to: https://healthchecks.io
2. Create free account
3. Click "Create Check"
4. Name: "whatsapp-bot-heartbeat"
5. Copy the ping URL

Option 2: Self-Hosted
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docker run -d -p 8000:8000 \\
  -v hc_data:/data \\
  healthchecks/checks

Then create checks in the web UI.

Add to .env:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HEALTHCHECKS_PING_URL=https://hc-ping.com/xxx
HEALTHCHECKS_API_KEY=xxx

Usage Examples:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Simple heartbeat
monitor = HealthchecksMonitor()
monitor.ping()

# With message
monitor.ping("✅ Processed 100 messages")

# Start/Success/Fail pattern
monitor.ping_start()
try:
    do_work()
    monitor.ping_success()
except:
    monitor.ping_fail("Error occurred")

# Background heartbeat thread
monitor = HealthchecksMonitor()
heartbeat = HeartbeatThread(monitor, interval=300)  # 5 min
heartbeat.start()

Alert Channels:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Email
• Slack
• Discord
• Telegram (like your bot!)
• PagerDuty
• Webhooks
• And more...

All configured in Healthchecks dashboard.
""")


# Decorator for automatic Healthchecks
def with_healthchecks(monitor: Optional[HealthchecksMonitor] = None):
    """
    Decorator to automatically ping Healthchecks
    
    Usage:
        monitor = HealthchecksMonitor()
        
        @with_healthchecks(monitor)
        def my_task():
            # Your codehere
            pass
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            if monitor and monitor.enabled:
                monitor.ping_start()
            
            try:
                result = func(*args, **kwargs)
                
                if monitor and monitor.enabled:
                    monitor.ping_success()
                
                return result
                
            except Exception as e:
                if monitor and monitor.enabled:
                    monitor.ping_fail(str(e))
                raise
        
        return wrapper
    return decorator


if __name__ == "__main__":
    setup_healthchecks()
