"""
Sentry Integration - Error Tracking
Monitor and fix errors in production
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SentryClient:
    """
    Sentry Error Tracking Client
    
    Perfect for:
    - Track errors from WhatsApp bot
    - Get alerts when something breaks
    - Debug issues in production
    
    Setup:
    1. Sign up at https://sentry.io
    2. Create a new project
    3. Copy the DSN URL
    4. Add to .env
    
    Environment:
    - SENTRY_DSN=https://xxx@sentry.io/xxx
    """
    
    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or os.getenv("SENTRY_DSN", "")
        self.enabled = bool(self.dsn)
        self._client = None
        
        if self.enabled:
            self._init_sentry()
            logger.info("✅ Sentry configured")
        else:
            logger.warning("⚠️ Sentry not configured (set SENTRY_DSN)")
    
    def _init_sentry(self):
        """Initialize Sentry SDK"""
        try:
            import sentry_sdk
            from sentry_sdk import capture_message, capture_exception
            
            sentry_sdk.init(
                dsn=self.dsn,
                traces_sample_rate=1.0,
                send_default_pii=False
            )
            self._client = sentry_sdk
            self.capture_message = capture_message
            self.capture_exception = capture_exception
            
        except ImportError:
            logger.warning("Install sentry-sdk: pip install sentry-sdk")
        except Exception as e:
            logger.error(f"Sentry init error: {e}")
    
    def capture_error(self, error: Exception, extra: Optional[Dict] = None):
        """Capture an error with optional context"""
        if not self.enabled:
            return
        
        try:
            with self._client.configure_scope() as scope:
                if extra:
                    for key, value in extra.items():
                        scope.set_extra(key, value)
                self._client.capture_exception(error)
        except Exception as e:
            logger.error(f"Capture error failed: {e}")
    
    def capture_message_event(self, message: str, level: str = "info"):
        """Capture a message event"""
        if not self.enabled:
            return
        
        try:
            self._client.capture_message(message, level=level)
        except Exception as e:
            logger.error(f"Capture message failed: {e}")
    
    def set_context(self, name: str, data: Dict):
        """Set context for all future events"""
        if not self.enabled:
            return
        
        try:
            self._client.set_context(name, data)
        except Exception as e:
            logger.error(f"Set context failed: {e}")
    
    def add_tag(self, key: str, value: str):
        """Add tag to events"""
        if not self.enabled:
            return
        
        try:
            self._client.set_tag(key, value)
        except Exception as e:
            logger.error(f"Add tag failed: {e}")


def setup_sentry():
    """Interactive setup for Sentry"""
    print("\n" + "="*50)
    print("🔍 Sentry Error Tracking Setup")
    print("="*50 + "\n")
    
    print("How to get Sentry DSN:")
    print("1. Sign up at https://sentry.io (free tier available)")
    print("2. Create a new project")
    print("3. Go to Project Settings → Client Keys (DSN)")
    print("4. Copy the DSN URL\n")
    
    dsn = input("Sentry DSN URL: ").strip()
    
    if dsn:
        with open(".env", "a") as f:
            f.write(f"\n# Sentry Error Tracking\n")
            f.write(f"SENTRY_DSN={dsn}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ DSN URL required!")


if __name__ == "__main__":
    setup_sentry()
