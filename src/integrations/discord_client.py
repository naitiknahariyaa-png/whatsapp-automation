"""
Discord Webhook Integration
Send notifications and alerts to Discord channels
"""

import os
import logging
import requests
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class DiscordWebhook:
    """
    Discord Webhook Client for sending messages
    
    Setup:
    1. In Discord, go to Channel Settings → Integrations → Webhooks
    2. Create new webhook or copy existing one
    3. Add WEBHOOK_URL to .env
    
    Environment:
    - DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL", "")
        self.enabled = bool(self.webhook_url)
        
        if self.enabled:
            logger.info("✅ Discord webhook configured")
        else:
            logger.warning("⚠️ Discord webhook not configured (set DISCORD_WEBHOOK_URL)")
    
    def send(
        self,
        message: str,
        username: str = "WhatsApp Bot",
        embed: Optional[Dict] = None
    ) -> bool:
        """Send message to Discord channel"""
        if not self.enabled:
            return False
        
        try:
            data = {
                "content": message,
                "username": username,
                "allowed_mentions": {"parse": []}  # Prevent accidental pings
            }
            
            if embed:
                data["embeds"] = [embed]
            
            response = requests.post(self.webhook_url, json=data, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Discord send error: {e}")
            return False
    
    def send_embed(
        self,
        title: str,
        description: str,
        color: int = 0x00FF00,
        fields: Optional[List[Dict]] = None,
        footer: Optional[str] = None
    ) -> bool:
        """Send rich embed message"""
        if not self.enabled:
            return False
        
        embed = {
            "title": title,
            "description": description,
            "color": color
        }
        
        if fields:
            embed["fields"] = fields
        
        if footer:
            embed["footer"] = {"text": footer}
        
        return self.send(embed=embed)
    
    def alert(self, title: str, message: str, level: str = "info") -> bool:
        """Send alert with color coding"""
        colors = {
            "success": 0x00FF00,   # Green
            "info": 0x0099FF,     # Blue
            "warning": 0xFFAA00,  # Orange
            "error": 0xFF0000     # Red
        }
        
        return self.send_embed(
            title=f"🔔 {title}",
            description=message,
            color=colors.get(level, 0x0099FF),
            footer="WhatsApp Automation Bot"
        )


def setup_discord():
    """Interactive setup for Discord webhook"""
    print("\n" + "="*50)
    print("📱 Discord Webhook Setup")
    print("="*50 + "\n")
    
    print("How to get Discord Webhook URL:")
    print("1. Open Discord → Right-click channel → Edit Channel")
    print("2. Go to Integrations → Webhooks")
    print("3. Create Webhook or Copy URL")
    print("4. Paste the URL below\n")
    
    webhook_url = input("Discord Webhook URL: ").strip()
    
    if webhook_url:
        # Save to .env
        with open(".env", "a") as f:
            f.write(f"\n# Discord Webhook\n")
            f.write(f"DISCORD_WEBHOOK_URL={webhook_url}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ Webhook URL required!")


if __name__ == "__main__":
    setup_discord()
