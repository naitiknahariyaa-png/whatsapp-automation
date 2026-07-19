"""
OpenWA Integration - Open Source WhatsApp API Gateway
Based on: https://github.com/rmyndharis/OpenWA

OpenWA is a free, open-source WhatsApp API Gateway with:
- 11.4k GitHub stars
- REST API for WhatsApp
- Multi-session support
- Web Dashboard
- Webhook support
- Docker native
- MCP Server for AI agents

Features:
- Persistent memory (saves API key automatically)
- Auto-loads saved credentials
- Easy setup via CLI
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenWAGateway:
    """
    OpenWA API Gateway Client with Persistent Memory
    
    Features:
    - REST API for WhatsApp messaging
    - Multi-session (multiple WhatsApp accounts)
    - Webhook support
    - Dashboard UI
    - MCP Server for AI agents
    - Persistent memory (saves API key automatically)
    
    Setup:
    1. Docker (Recommended):
       git clone https://github.com/rmyndharis/OpenWA.git
       cd OpenWA
       docker compose -f docker-compose.dev.yml up -d
    
    2. Local Development:
       npm install
       npm run dev
    
    3. Access:
       - Dashboard: http://localhost:2785
       - API: http://localhost:2785/api
       - Swagger: http://localhost:2785/api/docs
    
    4. Save credentials:
       python -m src.integrations.openwa_memory
    
    Environment:
    - OPENWA_URL=http://localhost:2785
    - OPENWA_API_KEY=your-api-key
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        # Try to load from memory first
        memory_key = self._load_from_memory()
        
        self.url = url or os.getenv("OPENWA_URL", memory_key.get("url", "http://localhost:2785"))
        self.api_key = api_key or os.getenv("OPENWA_API_KEY", memory_key.get("api_key", ""))
        self.session_id = session_id or memory_key.get("session_id", "default")
        
        self.enabled = bool(self.api_key)
        
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        
        if self.enabled:
            logger.info(f"✅ OpenWA Gateway configured: {self.url}")
            logger.info(f"   Memory: Loaded saved credentials")
        else:
            logger.warning("⚠️ OpenWA not configured")
            logger.info("   Run: python -m src.integrations.openwa_memory")
    
    def _load_from_memory(self) -> dict:
        """Load credentials from persistent memory"""
        try:
            from pathlib import Path
            config_file = Path(__file__).parent.parent.parent / "config" / "openwa_config.json"
            if config_file.exists():
                import json
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    if data.get("openwa_api_key"):
                        logger.info("📋 Loaded OpenWA credentials from memory")
                        return data
        except Exception as e:
            logger.debug(f"Could not load memory: {e}")
        return {}
    
    def save_to_memory(self):
        """Save current credentials to persistent memory"""
        try:
            from pathlib import Path
            import json
            config_file = Path(__file__).parent.parent.parent / "config" / "openwa_config.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                "openwa_url": self.url,
                "openwa_api_key": self.api_key,
                "openwa_session_id": self.session_id,
                "whatsapp_connected": True,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("💾 Saved OpenWA credentials to memory")
        except Exception as e:
            logger.error(f"Failed to save to memory: {e}")
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make API request"""
        try:
            url = f"{self.url}{endpoint}"
            response = requests.request(
                method,
                url,
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"OpenWA error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"OpenWA request error: {e}")
            return None
    
    # ═══════════════════════════════════════════════════════════════
    # Session Management
    # ═══════════════════════════════════════════════════════════════
    
    def create_session(self, name: str = "default") -> Optional[Dict]:
        """Create a new session"""
        return self._request("POST", "/api/sessions", {"name": name})
    
    def start_session(self, session_id: str = None) -> Optional[Dict]:
        """Start a session"""
        sid = session_id or self.session_id
        return self._request("POST", f"/api/sessions/{sid}/start")
    
    def stop_session(self, session_id: str = None) -> Optional[Dict]:
        """Stop a session"""
        sid = session_id or self.session_id
        return self._request("POST", f"/api/sessions/{sid}/stop")
    
    def get_session_status(self, session_id: str = None) -> Optional[Dict]:
        """Get session status"""
        sid = session_id or self.session_id
        return self._request("GET", f"/api/sessions/{sid}")
    
    def get_qr_code(self, session_id: str = None) -> Optional[str]:
        """Get QR code for session (base64)"""
        sid = session_id or self.session_id
        try:
            response = requests.get(
                f"{self.url}/api/sessions/{sid}/qr",
                headers={"X-API-Key": self.api_key},
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("qr")
        except Exception as e:
            logger.error(f"Get QR error: {e}")
        return None
    
    def list_sessions(self) -> List[Dict]:
        """List all sessions"""
        result = self._request("GET", "/api/sessions")
        return result.get("data", []) if result else []
    
    # ═══════════════════════════════════════════════════════════════
    # Messaging
    # ═══════════════════════════════════════════════════════════════
    
    def send_text(
        self,
        chat_id: str,
        text: str,
        session_id: str = None
    ) -> Optional[Dict]:
        """
        Send text message
        
        Args:
            chat_id: Recipient phone number (e.g., "628123456789@c.us")
            text: Message text
            session_id: Session to use
            
        Returns:
            Message response
        """
        sid = session_id or self.session_id
        return self._request(
            "POST",
            f"/api/sessions/{sid}/messages/send-text",
            {"chatId": chat_id, "text": text}
        )
    
    def send_image(
        self,
        chat_id: str,
        image_url: str,
        caption: str = "",
        session_id: str = None
    ) -> Optional[Dict]:
        """Send image message"""
        sid = session_id or self.session_id
        return self._request(
            "POST",
            f"/api/sessions/{sid}/messages/send-image",
            {"chatId": chat_id, "image": image_url, "caption": caption}
        )
    
    def send_bulk_messages(
        self,
        numbers: List[str],
        message: str,
        session_id: str = None
    ) -> List[Dict]:
        """Send message to multiple recipients"""
        sid = session_id or self.session_id
        results = []
        
        for number in numbers:
            # Format number
            chat_id = number if "@c.us" in number else f"{number}@c.us"
            
            result = self.send_text(chat_id, message, sid)
            results.append({
                "number": number,
                "status": "sent" if result else "failed"
            })
        
        return results
    
    # ═══════════════════════════════════════════════════════════════
    # Webhooks
    # ═══════════════════════════════════════════════════════════════
    
    def setup_webhook(
        self,
        url: str,
        events: List[str],
        secret: str = "",
        session_id: str = None
    ) -> Optional[Dict]:
        """
        Setup webhook for session
        
        Args:
            url: Webhook URL
            events: Events to receive (e.g., ["message.received", "session.status"])
            secret: HMAC secret for verification
            session_id: Session ID
            
        Returns:
            Webhook response
        """
        sid = session_id or self.session_id
        return self._request(
            "POST",
            f"/api/sessions/{sid}/webhooks",
            {
                "url": url,
                "events": events,
                "secret": secret
            }
        )
    
    # ═══════════════════════════════════════════════════════════════
    # Groups
    # ═══════════════════════════════════════════════════════════════
    
    def create_group(
        self,
        name: str,
        participants: List[str],
        session_id: str = None
    ) -> Optional[Dict]:
        """Create a group"""
        sid = session_id or self.session_id
        return self._request(
            "POST",
            f"/api/sessions/{sid}/groups",
            {"name": name, "participants": participants}
        )
    
    # ═══════════════════════════════════════════════════════════════
    # Contacts
    # ═══════════════════════════════════════════════════════════════
    
    def get_contact(self, chat_id: str, session_id: str = None) -> Optional[Dict]:
        """Get contact info"""
        sid = session_id or self.session_id
        return self._request("GET", f"/api/sessions/{sid}/contacts/{chat_id}")
    
    def get_chats(self, session_id: str = None) -> List[Dict]:
        """Get all chats"""
        sid = session_id or self.session_id
        result = self._request("GET", f"/api/sessions/{sid}/chats")
        return result.get("data", []) if result else []


# ═══════════════════════════════════════════════════════════════
# Quick Setup Guide
# ═══════════════════════════════════════════════════════════════

def setup_openwa():
    """Guide to setup OpenWA"""
    print("""
╔══════════════════════════════════════════════════════════╗
║       OpenWA - Open Source WhatsApp API Gateway         ║
║       https://github.com/rmyndharis/OpenWA              ║
╚══════════════════════════════════════════════════════════╝

Option 1: Docker (Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
git clone https://github.com/rmyndharis/OpenWA.git
cd OpenWA
docker compose -f docker-compose.dev.yml up -d

Access:
• Dashboard: http://localhost:2785
• API: http://localhost:2785/api
• Swagger: http://localhost:2785/api/docs

Option 2: Local Development
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
git clone https://github.com/rmyndharis/OpenWA.git
cd OpenWA
npm install
npm run dev

Add to .env:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OPENWA_URL=http://localhost:2785
OPENWA_API_KEY=your-api-key

Get API Key:
1. Open Dashboard: http://localhost:2785
2. Go to Settings → API Keys
3. Create new key
4. Copy the key

Features:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ REST API
✅ Multi-Session
✅ Web Dashboard
✅ Webhooks
✅ MCP Server (AI Agents)
✅ Groups API
✅ Media Messages
✅ Rate Limiting

MCP Server for AI Agents:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Set MCP_ENABLED=true to enable MCP server

Add to .mcp.json:
{
  "mcpServers": {
    "openwa": {
      "type": "http",
      "url": "http://localhost:2785/mcp",
      "headers": { "Authorization": "Bearer YOUR_API_KEY" }
    }
  }
}
""")


if __name__ == "__main__":
    setup_openwa()
