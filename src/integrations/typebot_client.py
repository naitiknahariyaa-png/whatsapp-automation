"""
Typebot Integration - Interactive Forms and Chatbot Flows
Add interactive forms, quizzes, and lead collection to WhatsApp.
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class TypebotClient:
    """
    Typebot API Client
    
    Features:
    - Visual form builder (drag and drop)
    - Conditional logic (branch flows)
    - Calculate (math in forms)
    - File upload (collect documents)
    - Payments (Stripe integration)
    
    Setup:
    1. Install Typebot: docker run -d -p 3000:3000 botpress/typebot
    2. Create form/quiz in Typebot Studio
    3. Publish and get Public ID
    4. Get API key for advanced features
    
    Environment:
    - TYPEBOT_URL=https://your-typebot.com
    - TYPEBOT_PUBLIC_ID=abc123
    - TYPEBOT_API_KEY=xxx (optional)
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        public_id: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.url = url or os.getenv("TYPEBOT_URL", "http://localhost:3000")
        self.public_id = public_id or os.getenv("TYPEBOT_PUBLIC_ID", "")
        self.api_key = api_key or os.getenv("TYPEBOT_API_KEY", "")
        
        self.enabled = bool(self.public_id)
        
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        if self.enabled:
            logger.info(f"✅ Typebot configured: {self.url}/public/{self.public_id}")
        else:
            logger.warning("⚠️ Typebot not configured (set TYPEBOT_PUBLIC_ID)")
    
    def create_session(self, user_id: str) -> Optional[str]:
        """
        Create new Typebot session
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Session ID
        """
        if not self.enabled:
            return None
        
        try:
            response = requests.post(
                f"{self.url}/api/v1/sessions",
                headers=self.headers,
                json={
                    "typebot": self.public_id,
                    "userId": user_id
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return response.json().get("id")
                
        except Exception as e:
            logger.error(f"Typebot create_session error: {e}")
            return None
    
    def get_next_question(
        self,
        session_id: str,
        user_answer: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get next question from Typebot flow
        
        Args:
            session_id: Typebot session ID
            user_answer: User's previous answer
            
        Returns:
            Question data with buttons/options
        """
        if not self.enabled:
            return None
        
        try:
            payload = {}
            if user_answer:
                payload["message"] = user_answer
                payload["type"] = "text"
            
            response = requests.post(
                f"{self.url}/api/v1/sessions/{session_id}/continue",
                headers=self.headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            logger.error(f"Typebot get_next_question error: {e}")
            return None
    
    def get_form_response(self, session_id: str) -> Dict[str, Any]:
        """
        Get collected form data
        
        Args:
            session_id: Typebot session ID
            
        Returns:
            Form responses
        """
        if not self.enabled:
            return {}
        
        try:
            response = requests.get(
                f"{self.url}/api/v1/sessions/{session_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "answers": data.get("answers", []),
                    "variables": data.get("variables", {}),
                    "status": data.get("status", "")
                }
                
        except Exception as e:
            logger.error(f"Typebot get_form_response error: {e}")
            return {}
    
    def start_form(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Start a new form/quiz with user
        
        Args:
            user_id: User identifier
            
        Returns:
            First question from form
        """
        session_id = self.create_session(user_id)
        
        if session_id:
            question = self.get_next_question(session_id)
            return {
                "session_id": session_id,
                "question": question
            }
        
        return None
    
    def process_form_step(
        self,
        session_id: str,
        user_answer: str
    ) -> Dict[str, Any]:
        """
        Process user's answer to form question
        
        Args:
            session_id: Typebot session ID
            user_answer: User's answer
            
        Returns:
            Next question or completion status
        """
        question = self.get_next_question(session_id, user_answer)
        
        if question:
            # Check if form is complete
            if question.get("status") == "finished":
                return {
                    "complete": True,
                    "answers": self.get_form_response(session_id)
                }
            
            return {
                "complete": False,
                "question": question
            }
        
        return {"complete": True, "error": "Could not get response"}


class WhatsAppFormHandler:
    """
    Handle Typebot forms in WhatsApp
    
    Example usage:
    
    handler = WhatsAppFormHandler(user_id="123456789")
    
    # Start form
    form = handler.start_form("lead-collection")
    if form:
        # Send first question
        send_whatsapp_message(user_id, form["question"])
    
    # Process answer
    handler.process_answer("John Doe")
    
    # Get final responses
    responses = handler.get_responses()
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client = TypebotClient()
        self.sessions = {}  # user_id -> session_id
        self.forms = {}  # session_id -> form_name
        self.responses = {}  # session_id -> collected responses
    
    def start_form(self, form_name: str) -> Optional[Dict[str, Any]]:
        """Start a form for user"""
        if not self.client.enabled:
            return None
        
        session = self.client.start_form(self.user_id)
        
        if session:
            session_id = session["session_id"]
            self.sessions[self.user_id] = session_id
            self.forms[session_id] = form_name
            return session
        
        return None
    
    def process_answer(self, answer: str) -> Optional[Dict[str, Any]]:
        """Process user's answer"""
        session_id = self.sessions.get(self.user_id)
        
        if not session_id:
            return None
        
        result = self.client.process_form_step(session_id, answer)
        
        # Store responses
        if result.get("complete"):
            self.responses[session_id] = result.get("answers", {})
        
        return result
    
    def get_responses(self) -> Dict[str, Any]:
        """Get collected form responses"""
        session_id = self.sessions.get(self.user_id)
        
        if session_id and session_id in self.responses:
            return self.responses[session_id]
        
        return {}
    
    def format_for_whatsapp(self, question: Dict[str, Any]) -> str:
        """
        Format Typebot question for WhatsApp
        
        Args:
            question: Typebot question data
            
        Returns:
            Formatted message text
        """
        text = question.get("text", "")
        buttons = question.get("buttons", [])
        
        message = text
        
        if buttons:
            message += "\n\n"
            for i, button in enumerate(buttons):
                message += f"\n{i+1}. {button.get('label', '')}"
        
        return message


# Quick setup function
def setup_typebot():
    """Guide user to setup Typebot"""
    print("""
╔══════════════════════════════════════════════════════════╗
║           Typebot Integration Setup                     ║
╚══════════════════════════════════════════════════════════╝

1. Install Typebot:
   docker run -d -p 3000:3000 \\
     -e DATABASE_URL=file:///db \\
     -v typebot_data:/db \\
     botpress/typebot

2. Open: http://localhost:3000

3. Create Account:
   • Sign up for free
   • Create new workspace

4. Create Form/Quiz:
   • Click "Create typebot"
   • Add questions:
     - Text input
     - Multiple choice
     - Email/Phone
     - File upload
   • Add logic:
     - Conditional branching
     - Calculate prices
     - Save to database

5. Publish:
   • Click "Preview"
   • Click "Share" → "Publish"
   • Copy Public ID

6. Add to .env:
   TYPEBOT_URL=http://localhost:3000
   TYPEBOT_PUBLIC_ID=abc123

Use Cases:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Lead Collection:
   "Hi! Please enter your details:"
   - Name
   - Email
   - Interest

🛒 Order Taking:
   "What would you like to order?"
   - Select items
   - Enter address
   - Confirm order

📅 Appointment Booking:
   "Book your appointment"
   - Select service
   - Choose date
   - Enter phone

🏠 Real Estate:
   "Tell us about your requirements"
   - Budget range
   - Location
   - Property type

Example:
   # Start form in WhatsApp
   form = TypebotClient()
   session = form.start_form(user_id="123456789")
   send_whatsapp(session["question"])
""")


# Example forms
def example_lead_collection():
    """Example: Lead collection form"""
    return {
        "name": "Lead Collection",
        "questions": [
            {
                "id": "q1",
                "type": "text",
                "question": "What's your name?",
                "variable": "name"
            },
            {
                "id": "q2",
                "type": "email",
                "question": "What's your email?",
                "variable": "email"
            },
            {
                "id": "q3",
                "type": "choice",
                "question": "What are you interested in?",
                "options": ["Product A", "Product B", "Service C"],
                "variable": "interest"
            }
        ]
    }


def example_order_form():
    """Example: Simple order form"""
    return {
        "name": "Order Form",
        "questions": [
            {
                "id": "q1",
                "type": "text",
                "question": "What would you like to order?",
                "variable": "item"
            },
            {
                "id": "q2",
                "type": "number",
                "question": "How many?",
                "variable": "quantity"
            },
            {
                "id": "q3",
                "type": "text",
                "question": "Your delivery address?",
                "variable": "address"
            }
        ]
    }


if __name__ == "__main__":
    setup_typebot()
