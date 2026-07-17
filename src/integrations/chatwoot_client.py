"""
Chatwoot Integration - Unified Customer Inbox
Connect WhatsApp to Chatwoot for CRM, team management, and analytics.
"""

import os
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ChatwootClient:
    """
    Chatwoot API Client
    
    Setup:
    1. Install Chatwoot: docker run -d -p 3000:3000 chatwoot/chatwoot
    2. Create WhatsApp inbox in Chatwoot dashboard
    3. Get your API access token from Profile → Settings
    
    Environment:
    - CHATWOOT_API_URL=https://your-chatwoot.com
    - CHATWOOT_API_TOKEN=your-access-token
    - CHATWOOT_INBOX_ID=1
    """
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        api_token: Optional[str] = None,
        inbox_id: Optional[int] = None
    ):
        self.api_url = api_url or os.getenv("CHATWOOT_API_URL", "")
        self.api_token = api_token or os.getenv("CHATWOOT_API_TOKEN", "")
        self.inbox_id = inbox_id or int(os.getenv("CHATWOOT_INBOX_ID", "1"))
        
        self.headers = {
            "api_access_token": self.api_token,
            "Content-Type": "application/json"
        }
        
        self.enabled = bool(self.api_url and self.api_token)
        
        if self.enabled:
            logger.info(f"✅ Chatwoot connected: {self.api_url}")
        else:
            logger.warning("⚠️ Chatwoot not configured (set CHATWOOT_API_URL and CHATWOOT_API_TOKEN)")
    
    def create_conversation(self, contact_id: int, message: str) -> Optional[Dict]:
        """Create new conversation"""
        if not self.enabled:
            return None
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/conversations",
                headers=self.headers,
                json={
                    "inbox_id": self.inbox_id,
                    "contact_id": contact_id,
                    "message": message
                },
                timeout=10
            )
            return response.json()
        except Exception as e:
            logger.error(f"Chatwoot create_conversation error: {e}")
            return None
    
    def send_message(self, conversation_id: int, message: str, message_type: str = "outgoing") -> Optional[Dict]:
        """
        Send message to conversation
        
        Args:
            conversation_id: Chatwoot conversation ID
            message: Message text
            message_type: 'outgoing' or 'incoming'
        """
        if not self.enabled:
            return None
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/conversations/{conversation_id}/messages",
                headers=self.headers,
                json={
                    "content": message,
                    "message_type": message_type
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Chatwoot message sent to conversation {conversation_id}")
                return response.json()
            else:
                logger.error(f"Chatwoot error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Chatwoot send_message error: {e}")
            return None
    
    def create_contact(self, name: str, phone: str, email: str = "") -> Optional[int]:
        """
        Create or get existing contact
        
        Returns: contact_id
        """
        if not self.enabled:
            return None
        
        try:
            # Try to find existing contact
            response = requests.get(
                f"{self.api_url}/api/v1/contacts",
                headers=selfHeaders,
                params={"search": phone},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get("data", [])
                
                if contacts:
                    return contacts[0]["id"]
            
            # Create new contact
            response = requests.post(
                f"{self.api_url}/api/v1/contacts",
                headers=self.headers,
                json={
                    "name": name or phone,
                    "phone_number": phone,
                    "email": email
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("id")
                
        except Exception as e:
            logger.error(f"Chatwoot create_contact error: {e}")
            return None
    
    def get_conversations(self, contact_id: int) -> list:
        """Get all conversations for a contact"""
        if not self.enabled:
            return []
        
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/contacts/{contact_id}/conversations",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("data", [])
            return []
                
        except Exception as e:
            logger.error(f"Chatwoot get_conversations error: {e}")
            return []
    
    def add_label(self, conversation_id: int, label: str) -> bool:
        """Add label to conversation"""
        if not self.enabled:
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/conversations/{conversation_id}/labels",
                headers=self.headers,
                json={"labels": [label]},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Chatwoot add_label error: {e}")
            return False


# Quick setup function
def setup_chatwoot():
    """Guide user to setup Chatwoot"""
    print("""
╔══════════════════════════════════════════════════════════╗
║           Chatwoot Integration Setup                     ║
╚══════════════════════════════════════════════════════════╝

1. Install Chatwoot:
   docker run -d -p 3000:3000 chatwoot/chatwoot

2. Open: http://localhost:3000

3. Create account and setup

4. Settings → Inboxes → Add Inbox → WhatsApp

5. Get API Token: Profile → Settings → Access Token

6. Add to .env:
   CHATWOOT_API_URL=http://localhost:3000
   CHATWOOT_API_TOKEN=your-token
   CHATWOOT_INBOX_ID=1

Quick Start:
   pip install requests
""")
