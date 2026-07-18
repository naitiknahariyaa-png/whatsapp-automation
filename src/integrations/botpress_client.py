"""
Botpress Integration - Visual Chatbot Flow Builder
Connect to Botpress for advanced conversational AI flows.
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class BotpressClient:
    """
    Botpress API Client
    
    Features:
    - Visual flow builder (no-code chatbot design)
    - AI NLU (understand user intent)
    - Multi-channel (WhatsApp, Web, Slack)
    - Knowledge Base (AI-powered FAQ)
    - Analytics (conversation insights)
    
    Setup:
    1. Install Botpress: docker run -d -p 3000:3000 botpress/server
    2. Create bot in Botpress Studio
    3. Add WhatsApp channel
    4. Get bot ID and API key
    
    Environment:
    - BOTPRESS_URL=https://your-botpress.com
    - BOTPRESS_BOT_ID=your-bot-id
    - BOTPRESS_API_KEY=xxx
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        bot_id: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.url = url or os.getenv("BOTPRESS_URL", "http://localhost:3000")
        self.bot_id = bot_id or os.getenv("BOTPRESS_BOT_ID", "")
        self.api_key = api_key or os.getenv("BOTPRESS_API_KEY", "")
        
        self.enabled = bool(self.bot_id)
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        } if self.api_key else {"Content-Type": "application/json"}
        
        if self.enabled:
            logger.info(f"✅ Botpress configured: {self.url}/bots/{self.bot_id}")
        else:
            logger.warning("⚠️ Botpress not configured (set BOTPRESS_BOT_ID)")
    
    def send_message(
        self,
        user_id: str,
        message: str,
        message_type: str = "text"
    ) -> Optional[Dict[str, Any]]:
        """
        Send message to Botpress for processing
        
        Args:
            user_id: Unique user identifier (phone number)
            message: Message to process
            message_type: Type of message ('text', 'image', etc.)
            
        Returns:
            Botpress response
        """
        if not self.enabled:
            return None
        
        try:
            response = requests.post(
                f"{self.url}/api/bots/{self.bot_id}/messages",
                headers=self.headers,
                json={
                    "userId": user_id,
                    "message": message,
                    "type": message_type
                },
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Botpress error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Botpress send_message error: {e}")
            return None
    
    def get_response(self, user_id: str, message: str) -> str:
        """
        Get response from Botpress
        
        Args:
            user_id: User identifier
            message: User message
            
        Returns:
            Bot response text
        """
        result = self.send_message(user_id, message)
        
        if result:
            # Parse Botpress response
            responses = result.get("responses", [])
            if responses:
                return responses[0].get("text", "")
        
        return ""
    
    def create_conversation(self, user_id: str) -> Optional[str]:
        """
        Create new conversation in Botpress
        
        Args:
            user_id: User identifier
            
        Returns:
            Conversation ID
        """
        if not self.enabled:
            return None
        
        try:
            response = requests.post(
                f"{self.url}/api/bots/{self.bot_id}/conversations",
                headers=self.headers,
                json={"userId": user_id},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return data.get("conversationId")
                
        except Exception as e:
            logger.error(f"Botpress create_conversation error: {e}")
            return None
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history from Botpress
        
        Args:
            conversation_id: Conversation ID
            limit: Number of messages to retrieve
            
        Returns:
            List of messages
        """
        if not self.enabled:
            return []
        
        try:
            response = requests.get(
                f"{self.url}/api/bots/{self.bot_id}/conversations/{conversation_id}/messages",
                headers=self.headers,
                params={"limit": limit},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("messages", [])
                
        except Exception as e:
            logger.error(f"Botpress history error: {e}")
            return []
    
    def trigger_flow(self, user_id: str, flow_name: str) -> bool:
        """
        Trigger specific flow in Botpress
        
        Args:
            user_id: User identifier
            flow_name: Name of the flow to trigger
            
        Returns:
            Success status
        """
        if not self.enabled:
            return False
        
        try:
            response = requests.post(
                f"{self.url}/api/bots/{self.bot_id}/flows/{flow_name}/trigger",
                headers=self.headers,
                json={"userId": user_id},
                timeout=10
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            logger.error(f"Botpress trigger_flow error: {e}")
            return False
    
    def set_variable(self, user_id: str, variable: str, value: Any) -> bool:
        """
        Set user variable in Botpress
        
        Args:
            user_id: User identifier
            variable: Variable name
            value: Variable value
            
        Returns:
            Success status
        """
        if not self.enabled:
            return False
        
        try:
            response = requests.post(
                f"{self.url}/api/bots/{self.bot_id}/users/{user_id}/variables",
                headers=self.headers,
                json={
                    "name": variable,
                    "value": value
                },
                timeout=10
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            logger.error(f"Botpress set_variable error: {e}")
            return False
    
    def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data from Botpress
        
        Args:
            user_id: User identifier
            
        Returns:
            User data dictionary
        """
        if not self.enabled:
            return None
        
        try:
            response = requests.get(
                f"{self.url}/api/bots/{self.bot_id}/users/{user_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            logger.error(f"Botpress get_user_data error: {e}")
            return None


class BotpressAI:
    """
    Botpress as AI Brain
    Use Botpress as the main AI engine instead of OpenRouter/Groq
    """
    
    def __init__(self, bot_id: Optional[str] = None):
        self.client = BotpressClient(bot_id=bot_id)
    
    def think(self, prompt: str, context: str = "") -> str:
        """
        Process prompt through Botpress
        
        Args:
            prompt: User message
            context: Conversation context
            
        Returns:
            AI response
        """
        # Create temporary user ID
        import hashlib
        user_id = hashlib.md5(prompt.encode()).hexdigest()[:16]
        
        return self.client.get_response(user_id, prompt)
    
    def get_status(self) -> Dict[str, Any]:
        """Check Botpress status"""
        return {
            "configured": self.client.enabled,
            "bot_id": self.client.bot_id,
            "url": self.client.url
        }


# Quick setup function
def setup_botpress():
    """Guide user to setup Botpress"""
    print("""
╔══════════════════════════════════════════════════════════╗
║           Botpress Integration Setup                     ║
╚══════════════════════════════════════════════════════════╝

1. Install Botpress:
   docker run -d -p 3000:3000 -v botpress_data:/botpress/data botpress/server

2. Open: http://localhost:3000

3. Create Account:
   • Sign up for free
   • Create your first bot

4. Create Flow:
   • Click "Flows" → "New"
   • Add nodes:
     - Start (trigger)
     - Send Message (AI response)
     - Execute Code (custom logic)
     - And more!

5. Add WhatsApp Channel:
   • Settings → Channels → WhatsApp
   • Follow setup instructions

6. Get Bot ID:
   • Settings → General → Bot ID

7. Add to .env:
   BOTPRESS_URL=http://localhost:3000
   BOTPRESS_BOT_ID=your-bot-id
   BOTPRESS_API_KEY=xxx

Botpress Features:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 Visual Builder - Drag and drop chatbot flows
🧠 AI NLU - Understand user intent
📚 Knowledge Base - AI-powered FAQ
📊 Analytics - Track conversations
🔗 Multi-channel - WhatsApp, Web, Slack
💬 Live Chat - Human handoff

Example Flow:
   User → WhatsApp → Botpress → AI → Response
                          ↓
                      CRM Update
                          ↓
                    Email Alert
""")


# Example: Use Botpress as AI in reply engine
def use_botpress_as_ai():
    """Example of using Botpress as the main AI"""
    from src.core.reply_engine import ReplyEngine
    
    # Create Botpress AI
    botpress = BotpressAI()
    
    # Override the get_response method
    def botpress_response(prompt, context=""):
        return botpress.think(prompt, context)
    
    # Use in reply engine
    engine = ReplyEngine()
    # engine.ai.get_response = botpress_response  # Override AI method


if __name__ == "__main__":
    setup_botpress()
