"""
Posthog Integration - Product Analytics
Track user behavior and events
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class PosthogClient:
    """
    Posthog Analytics Client
    
    Perfect for:
    - Track WhatsApp message events
    - Analyze user behavior
    - Funnels and retention
    - A/B testing
    
    Setup:
    1. Sign up at https://posthog.com
    2. Create a new project
    3. Copy the Project API Key
    4. Add to .env
    
    Environment:
    - POSTHOG_API_KEY=phc_xxx
    - POSTHOG_HOST=https://app.posthog.com
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        host: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("POSTHOG_API_KEY", "")
        self.host = host or os.getenv("POSTHOG_HOST", "https://app.posthog.com")
        self.enabled = bool(self.api_key)
        self._client = None
        
        if self.enabled:
            self._init_posthog()
            logger.info("✅ Posthog configured")
        else:
            logger.warning("⚠️ Posthog not configured (set POSTHOG_API_KEY)")
    
    def _init_posthog(self):
        """Initialize Posthog SDK"""
        try:
            from posthog import Posthog
            
            self._client = Posthog(
                project_api_key=self.api_key,
                host=self.host
            )
        except ImportError:
            logger.warning("Install posthog: pip install posthog")
        except Exception as e:
            logger.error(f"Posthog init error: {e}")
    
    def capture(
        self,
        distinct_id: str,
        event: str,
        properties: Optional[Dict] = None
    ):
        """
        Capture an event
        
        Args:
            distinct_id: Unique user identifier (phone number)
            event: Event name (e.g., "message_sent", "payment_completed")
            properties: Event properties
        """
        if not self.enabled:
            return
        
        try:
            self._client.capture(
                distinct_id=distinct_id,
                event=event,
                properties=properties or {}
            )
        except Exception as e:
            logger.error(f"Posthog capture error: {e}")
    
    def identify(
        self,
        distinct_id: str,
        properties: Optional[Dict] = None
    ):
        """
        Identify a user with properties
        
        Args:
            distinct_id: Unique user identifier
            properties: User properties (name, email, phone)
        """
        if not self.enabled:
            return
        
        try:
            self._client.identify(
                distinct_id=distinct_id,
                properties=properties or {}
            )
        except Exception as e:
            logger.error(f"Posthog identify error: {e}")
    
    def track_whatsapp_message(self, phone: str, direction: str, content: str):
        """Track WhatsApp message event"""
        self.capture(
            distinct_id=phone,
            event="whatsapp_message",
            properties={
                "direction": direction,  # "incoming" or "outgoing"
                "content_length": len(content)
            }
        )
    
    def track_payment(
        self,
        phone: str,
        amount: int,
        status: str,
        payment_id: Optional[str] = None
    ):
        """Track payment event"""
        self.capture(
            distinct_id=phone,
            event="payment",
            properties={
                "amount": amount,
                "status": status,
                "payment_id": payment_id
            }
        )
    
    def page(self, distinct_id: str, name: str, properties: Optional[Dict] = None):
        """Track page view"""
        if not self.enabled:
            return
        
        try:
            self._client.page(
                distinct_id=distinct_id,
                name=name,
                properties=properties or {}
            )
        except Exception as e:
            logger.error(f"Posthog page error: {e}")


def setup_posthog():
    """Interactive setup for Posthog"""
    print("\n" + "="*50)
    print("📊 Posthog Analytics Setup")
    print("="*50 + "\n")
    
    print("How to get Posthog API Key:")
    print("1. Sign up at https://posthog.com (free tier available)")
    print("2. Create a new project")
    print("3. Go to Project Settings → API Keys")
    print("4. Copy the Project API Key\n")
    
    api_key = input("Posthog API Key (phc_xxx): ").strip()
    host = input("Host (press Enter for default): ").strip()
    
    if not host:
        host = "https://app.posthog.com"
    
    if api_key:
        with open(".env", "a") as f:
            f.write(f"\n# Posthog Analytics\n")
            f.write(f"POSTHOG_API_KEY={api_key}\n")
            f.write(f"POSTHOG_HOST={host}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ API Key required!")


if __name__ == "__main__":
    setup_posthog()
