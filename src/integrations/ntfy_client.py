"""
Ntfy Integration - FREE Push Notifications
==========================================
Self-hosted notification service

Based on: https://github.com/binwiederhier/ntfy

Features:
- Real-time push notifications
- Web browser support
- Android/iOS apps
- No registration needed
- 100% FREE!

Setup:
    docker run -d -p 80:80 binwiederhier/ntfy
"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class NtfyClient:
    """
    Ntfy Push Notification Client
    
    Use Cases:
    - Admin alerts
    - Order notifications
    - System monitoring
    - Custom alerts
    - WhatsApp bot notifications
    
    Setup:
    1. Self-hosted (FREE):
       docker run -d -p 80:80 binwiederhier/ntfy
       OR
       docker run -d -p 80:80 \\
         -v $(pwd)/ntfy_data:/var/cache/ntfy \\
         -e NTFY_TOPIC_DEFAULT="mydefaulttopic" \\
         binwiederhier/ntfy serve
    
    2. Or use public server:
       https://ntfy.sh (no setup needed)
    
    Environment:
    - NTFY_URL=http://localhost:80
    - NTFY_TOPIC=my-topic
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        topic: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.url = url or os.getenv("NTFY_URL", "https://ntfy.sh")
        self.topic = topic or os.getenv("NTFY_TOPIC", "whatsapp-alerts")
        self.username = username or os.getenv("NTFY_USERNAME", "")
        self.password = password or os.getenv("NTFY_PASSWORD", "")
        self.enabled = bool(self.url)
        
        self.session = requests.Session()
        if self.username and self.password:
            self.session.auth = (self.username, self.password)
        
        logger.info(f"✅ Ntfy configured: {self.url}")
    
    def send(
        self,
        message: str,
        title: Optional[str] = None,
        priority: int = 3,
        tags: Optional[str] = None,
        topic: Optional[str] = None
    ) -> bool:
        """
        Send push notification
        
        Args:
            message: Notification message
            title: Optional title
            priority: 1-5 (1=min, 5=max)
            tags: Comma-separated emojis/tags (e.g., "warning,🔔")
            topic: Override default topic
        """
        target_topic = topic or self.topic
        
        # Build URL
        url = f"{self.url}/{target_topic}"
        
        # Build headers
        headers = {
            "Content-Type": "text/plain",
            "Priority": str(priority)
        }
        if title:
            headers["Title"] = title
        if tags:
            headers["Tags"] = tags
        
        try:
            response = self.session.post(
                url,
                data=message.encode("utf-8"),
                headers=headers,
                timeout=10
            )
            return response.status_code in [200, 201, 204]
        except Exception as e:
            logger.error(f"Ntfy send error: {e}")
            return False
    
    def alert(
        self,
        message: str,
        level: str = "info"
    ) -> bool:
        """
        Send alert with level
        
        levels: info, success, warning, error
        """
        tag_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        return self.send(
            message=message,
            title=f"{tag_map.get(level, '📢')} WhatsApp Bot",
            priority={"info": 3, "success": 3, "warning": 4, "error": 5}[level],
            tags=tag_map.get(level, "📢")
        )
    
    def order_notification(
        self,
        customer_name: str,
        order_details: str,
        amount: str = ""
    ) -> bool:
        """Send order notification"""
        message = f"📦 New Order!\n\n👤 {customer_name}\n💰 Amount: {amount}\n📋 {order_details}"
        return self.alert(message, "success")
    
    def error_alert(self, error_message: str, context: str = "") -> bool:
        """Send error alert"""
        message = f"❌ Error: {error_message}\n\n{context}"
        return self.alert(message, "error")
    
    def payment_received(
        self,
        customer: str,
        amount: str,
        payment_id: str
    ) -> bool:
        """Send payment notification"""
        message = f"💰 Payment Received!\n\n👤 {customer}\n💵 Amount: {amount}\n🔢 ID: {payment_id}"
        return self.alert(message, "success")
    
    def system_status(
        self,
        status: str,
        uptime: str,
        messages_today: int
    ) -> bool:
        """Send system status"""
        message = f"🤖 System: {status}\n⏱️ Uptime: {uptime}\n💬 Messages Today: {messages_today}"
        return self.send(message, "System Status", tags="🤖,📊")
    
    def subscribe(self, topic: Optional[str] = None, callback=None):
        """
        Subscribe to topic (for receiving notifications)
        
        This is a simple polling implementation.
        For real-time, use websockets.
        """
        import threading
        import time
        
        target_topic = topic or self.topic
        url = f"{self.url}/{target_topic}/json"
        
        def poll():
            last_id = None
            while True:
                try:
                    params = {"since": 1}
                    if last_id:
                        params["poll"] = 1
                    
                    response = requests.get(url, params=params, timeout=35)
                    if response.status_code == 200:
                        for line in response.text.split("\n"):
                            if line.strip():
                                try:
                                    data = __import__("json").loads(line)
                                    last_id = data.get("id")
                                    if callback:
                                        callback(data)
                                except:
                                    pass
                except:
                    pass
                time.sleep(5)
        
        thread = threading.Thread(target=poll, daemon=True)
        thread.start()
        return thread


def setup_ntfy():
    """Setup guide for Ntfy"""
    print("\n" + "="*50)
    print("🔔 Ntfy Notifications Setup")
    print("="*50 + "\n")
    
    print("OPTION 1: Self-hosted (FREE)")
    print("-" * 40)
    print("docker run -d -p 80:80 \\")
    print("  -v $(pwd)/ntfy_data:/var/cache/ntfy \\")
    print("  binwiederhier/ntfy serve")
    print("\nConsole: http://localhost:80\n")
    
    print("OPTION 2: Use Public Server (Easiest)")
    print("-" * 40)
    print("No setup needed! Just use https://ntfy.sh")
    print("Topics are public but temporary.\n")
    
    url = input("Ntfy URL (press Enter for ntfy.sh): ").strip()
    if not url:
        url = "https://ntfy.sh"
    
    topic = input("Default topic name: ").strip()
    if not topic:
        topic = "whatsapp-alerts"
    
    user = input("Username (optional): ").strip()
    pwd = input("Password (optional): ").strip()
    
    with open(".env", "a") as f:
        f.write(f"\n# Ntfy (Push Notifications)\n")
        f.write(f"NTFY_URL={url}\n")
        f.write(f"NTFY_TOPIC={topic}\n")
        if user:
            f.write(f"NTFY_USERNAME={user}\n")
        if pwd:
            f.write(f"NTFY_PASSWORD={pwd}\n")
    print("✅ Saved to .env!")


if __name__ == "__main__":
    setup_ntfy()
