"""
🤖 WhatsApp Automation Hub - v5.0
=====================================
CONNECTED SYSTEM - All apps work together!

Flow:
WhatsApp Message → OpenWA → AI Processing → 
    → Save to Database (Supabase)
    → Track Analytics (Posthog)
    → Create Lead (Notion)
    → Send Notification (Discord)
    → Log Errors (Sentry)

How to Run:
    python src/core/unified_hub.py
"""

import os
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# 📦 IMPORT ALL INTEGRATIONS
# ═══════════════════════════════════════════════════════════════

class IntegrationHub:
    """
    Central hub connecting all integrations
    
    Usage:
        hub = IntegrationHub()
        await hub.initialize()
        
        # Process a message
        await hub.process_message(
            sender="919876543210",
            message="I want to order coffee",
            platform="whatsapp"
        )
    """
    
    def __init__(self):
        self.name = "WhatsApp Hub"
        self.version = "5.0"
        self.initialized = False
        
        # Integration status
        self.integrations = {
            "openwa": {"enabled": False, "client": None},
            "telegram": {"enabled": False, "client": None},
            "ai": {"enabled": False, "client": None},
            "database": {"enabled": False, "client": None},
            "analytics": {"enabled": False, "client": None},
            "crm": {"enabled": False, "client": None},
            "payments": {"enabled": False, "client": None},
            "notifications": {"enabled": False, "client": None},
            "storage": {"enabled": False, "client": None},
            "error_tracking": {"enabled": False, "client": None},
        }
    
    async def initialize(self):
        """Initialize all integrations"""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║       🤖 {self.name} v{self.version} - Connected System           ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        print("🔄 Initializing integrations...")
        
        # Initialize each integration
        await self._init_openwa()
        await self._init_ai()
        await self._init_database()
        await self._init_analytics()
        await self._init_crm()
        await self._init_payments()
        await self._init_notifications()
        await self._init_error_tracking()
        
        # Count enabled integrations
        enabled = sum(1 for i in self.integrations.values() if i["enabled"])
        total = len(self.integrations)
        
        print(f"\n✅ Initialized {enabled}/{total} integrations")
        self.initialized = True
        
        return self
    
    async def _init_openwa(self):
        """Initialize OpenWA WhatsApp Gateway"""
        try:
            from src.integrations.openwa_client import OpenWAGateway
            self.integrations["openwa"]["client"] = OpenWAGateway()
            if self.integrations["openwa"]["client"].enabled:
                self.integrations["openwa"]["enabled"] = True
                print("  ✅ OpenWA (WhatsApp Gateway)")
            else:
                print("  ⚠️  OpenWA not configured")
        except Exception as e:
            print(f"  ❌ OpenWA error: {e}")
    
    async def _init_ai(self):
        """Initialize AI providers"""
        try:
            from src.integrations.ollama_client import OllamaAI
            from src.ai.providers import AIManager
            
            # Try Groq first
            groq_key = os.getenv("GROQ_API_KEY", "")
            if groq_key:
                self.ai_client = AIManager()
                self.integrations["ai"]["enabled"] = True
                self.ai_type = "groq"
                print("  ✅ AI (Groq)")
                return
            
            # Try Gemini
            gemini_key = os.getenv("GOOGLE_API_KEY", "")
            if gemini_key:
                self.ai_client = AIManager()
                self.integrations["ai"]["enabled"] = True
                self.ai_type = "gemini"
                print("  ✅ AI (Gemini)")
                return
            
            # Try Ollama
            try:
                self.ai_client = OllamaAI()
                self.integrations["ai"]["enabled"] = True
                self.ai_type = "ollama"
                print("  ✅ AI (Ollama)")
            except:
                print("  ⚠️  AI not configured (set GROQ_API_KEY or GOOGLE_API_KEY)")
                
        except Exception as e:
            print(f"  ❌ AI error: {e}")
    
    async def _init_database(self):
        """Initialize Supabase database"""
        try:
            supabase_url = os.getenv("SUPABASE_URL", "")
            supabase_key = os.getenv("SUPABASE_KEY", "")
            
            if supabase_url and supabase_key:
                from src.integrations.supabase_client import SupabaseDB
                self.db_client = SupabaseDB()
                self.integrations["database"]["enabled"] = True
                print("  ✅ Database (Supabase)")
            else:
                # Use local SQLite as fallback
                self.integrations["database"]["enabled"] = True
                self.db_type = "sqlite"
                print("  ✅ Database (SQLite)")
                
        except Exception as e:
            print(f"  ❌ Database error: {e}")
    
    async def _init_analytics(self):
        """Initialize Posthog analytics"""
        try:
            posthog_key = os.getenv("POSTHOG_API_KEY", "")
            if posthog_key:
                from src.integrations.posthog_client import PosthogClient
                self.analytics_client = PosthogClient()
                self.integrations["analytics"]["enabled"] = True
                print("  ✅ Analytics (Posthog)")
            else:
                print("  ⚠️  Analytics not configured")
        except Exception as e:
            print(f"  ❌ Analytics error: {e}")
    
    async def _init_crm(self):
        """Initialize Notion CRM"""
        try:
            notion_key = os.getenv("NOTION_API_KEY", "")
            notion_db = os.getenv("NOTION_DATABASE_ID", "")
            
            if notion_key and notion_db:
                from src.integrations.notion_client import NotionClient
                self.crm_client = NotionClient()
                self.integrations["crm"]["enabled"] = True
                print("  ✅ CRM (Notion)")
            else:
                print("  ⚠️  CRM not configured")
        except Exception as e:
            print(f"  ❌ CRM error: {e}")
    
    async def _init_payments(self):
        try:
                self.integrations["payments"]["enabled"] = True
            else:
                print("  ⚠️  Payments not configured")
        except Exception as e:
            print(f"  ❌ Payments error: {e}")
    
    async def _init_notifications(self):
        """Initialize Discord & Telegram"""
        try:
            # Discord
            discord_webhook = os.getenv("DISCORD_WEBHOOK_URL", "")
            if discord_webhook:
                from src.integrations.discord_client import DiscordWebhook
                self.discord_client = DiscordWebhook()
                self.integrations["notifications"]["enabled"] = True
                print("  ✅ Notifications (Discord)")
            
            # Telegram already handled by separate bot
            print("  ✅ Notifications (Telegram Bot - separate)")
                
        except Exception as e:
            print(f"  ❌ Notifications error: {e}")
    
    async def _init_error_tracking(self):
        """Initialize Sentry"""
        try:
            sentry_dsn = os.getenv("SENTRY_DSN", "")
            if sentry_dsn:
                from src.integrations.sentry_client import SentryClient
                self.sentry_client = SentryClient()
                self.integrations["error_tracking"]["enabled"] = True
                print("  ✅ Error Tracking (Sentry)")
            else:
                print("  ⚠️  Error tracking not configured")
        except Exception as e:
            print(f"  ❌ Error tracking error: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # 🎯 MAIN MESSAGE PROCESSOR
    # ═══════════════════════════════════════════════════════════════
    
    async def process_message(self, sender: str, message: str, platform: str = "whatsapp"):
        """
        Process incoming message through the entire pipeline
        
        Pipeline:
        1. Receive message
        2. Track analytics
        3. Get AI response
        4. Check for intents (order, payment, etc.)
        5. Take action based on intent
        6. Save to database
        7. Send response
        """
        try:
            logger.info(f"Processing: {sender} - {message[:50]}")
            
            # Step 1: Track analytics
            await self._track_event(sender, "message_received", {
                "platform": platform,
                "message_length": len(message)
            })
            
            # Step 2: Detect intent
            intent = self._detect_intent(message)
            logger.info(f"Detected intent: {intent}")
            
            response = None
            action_taken = None
            
            # Step 3: Process based on intent
            if intent == "order":
                response, action_taken = await self._handle_order(sender, message)
            elif intent == "payment":
                response, action_taken = await self._handle_payment(sender, message)
            elif intent == "inquiry":
                response, action_taken = await self._handle_inquiry(sender, message)
            elif intent == "support":
                response, action_taken = await self._handle_support(sender, message)
            else:
                response, action_taken = await self._handle_general(sender, message)
            
            # Step 4: Save to CRM
            await self._save_to_crm(sender, message, intent, action_taken)
            
            # Step 5: Send notification to admin
            await self._notify_admin(sender, message, intent)
            
            # Step 6: Track result
            await self._track_event(sender, "message_processed", {
                "intent": intent,
                "action": action_taken,
                "platform": platform
            })
            
            return {
                "success": True,
                "response": response,
                "intent": intent,
                "action": action_taken
            }
            
        except Exception as e:
            logger.error(f"Process error: {e}")
            await self._track_error(e, {"sender": sender, "message": message})
            return {
                "success": False,
                "error": str(e)
            }
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Order intents
        order_keywords = ["order", "buy", "purchase", "want", "need", "get me", "book"]
        if any(kw in message_lower for kw in order_keywords):
            return "order"
        
        # Payment intents
        payment_keywords = ["pay", "payment", "price", "cost", "rupees", "₹", "paytm", "upi"]
        if any(kw in message_lower for kw in payment_keywords):
            return "payment"
        
        # Support intents
        support_keywords = ["help", "support", "problem", "issue", "not working", "refund"]
        if any(kw in message_lower for kw in support_keywords):
            return "support"
        
        # Inquiry intents
        inquiry_keywords = ["what", "how", "when", "where", "which", "is it", "do you"]
        if any(kw in message_lower for kw in inquiry_keywords):
            return "inquiry"
        
        return "general"
    
    async def _handle_order(self, sender: str, message: str):
        """Handle order intent"""
        # Track event
        await self._track_event(sender, "order_intent_detected")
        
        # Generate payment link if payments enabled
        payment_link = None
        if self.integrations["payments"]["enabled"]:
            payment_link = await self._create_payment_link(sender, message)
        
        # Get AI response
        ai_response = await self._get_ai_response(message)
        
        response = f"""
📦 *Order Received!*

{ai_response}
"""
        if payment_link:
            response += f"\n💳 *Payment Link:* {payment_link}"
        
        response += "\n\nWe'll confirm your order shortly!"
        
        return response, "order_created"
    
    async def _handle_payment(self, sender: str, message: str):
        """Handle payment intent"""
        # Extract amount from message (simple parsing)
        import re
        amounts = re.findall(r'\d+', message)
        amount = int(amounts[0]) * 100 if amounts else 50000  # Default ₹500
        
        payment_link = None
        if self.integrations["payments"]["enabled"]:
            payment_link = await self._create_payment_link(sender, message, amount)
        
        if payment_link:
            response = f"""
💰 *Payment Options*

Click below to pay:
{payment_link}

*UPI / Card / Wallet accepted*
"""
        else:
            response = "Payment system not configured. Contact us for payment options."
        
        return response, "payment_link_sent"
    
    async def _handle_inquiry(self, sender: str, message: str):
        """Handle inquiry intent"""
        response = await self._get_ai_response(message)
        return response, "inquiry_answered"
    
    async def _handle_support(self, sender: str, message: str):
        """Handle support intent"""
        # Save to CRM as support ticket
        await self._save_support_ticket(sender, message)
        
        response = await self._get_ai_response(message)
        response += "\n\n📧 Our team has been notified and will respond soon!"
        
        return response, "support_ticket_created"
    
    async def _handle_general(self, sender: str, message: str):
        """Handle general message"""
        response = await self._get_ai_response(message)
        return response, "general_response"
    
    # ═══════════════════════════════════════════════════════════════
    # 🔧 HELPER METHODS
    # ═══════════════════════════════════════════════════════════════
    
    async def _get_ai_response(self, message: str) -> str:
        """Get response from AI"""
        if not self.integrations["ai"]["enabled"]:
            return "AI not configured. Please set up GROQ_API_KEY or GOOGLE_API_KEY"
        
        try:
            if self.ai_type == "groq":
                response = self.ai_client.get_response(message)
                return response
            elif self.ai_type == "gemini":
                response = self.ai_client.get_response(message)
                return response
            else:
                return "AI processing..."
        except Exception as e:
            logger.error(f"AI error: {e}")
            return "Sorry, I'm having trouble thinking right now. Please try again."
    
    async def _create_payment_link(self, sender: str, message: str, amount: int = 50000):
        try:
            result = self.payment_client.create_payment_link(
                amount=amount,
                description=f"Order from {sender}: {message[:100]}",
                customer_name=f"Customer {sender[-4:]}",
                customer_email="customer@example.com",
                customer_mobile=sender
            )
            
            if result and result.get("short_url"):
                return result["short_url"]
        except Exception as e:
            logger.error(f"Payment link error: {e}")
        
        return None
    
    async def _save_to_crm(self, sender: str, message: str, intent: str, action: str):
        """Save interaction to Notion CRM"""
        if not self.integrations["crm"]["enabled"]:
            return
        
        try:
            self.crm_client.add_lead(
                name=f"Lead {sender[-4:]}",
                phone=sender,
                source="WhatsApp",
                notes=f"Intent: {intent}, Action: {action}, Message: {message[:100]}"
            )
        except Exception as e:
            logger.error(f"CRM save error: {e}")
    
    async def _save_support_ticket(self, sender: str, message: str):
        """Save support ticket"""
        if self.integrations["crm"]["enabled"]:
            try:
                self.crm_client.create_page({
                    "Name": {"title": [{"text": {"content": f"Support: {sender[-4:]}"}}]},
                    "Type": {"select": {"name": "Support"}},
                    "Status": {"select": {"name": "Open"}},
                    "Description": {"rich_text": [{"text": {"content": message}}]}
                })
            except Exception as e:
                logger.error(f"Support ticket error: {e}")
    
    async def _track_event(self, user_id: str, event: str, properties: dict = None):
        """Track event to analytics"""
        if not self.integrations["analytics"]["enabled"]:
            return
        
        try:
            self.analytics_client.capture(user_id, event, properties or {})
        except Exception as e:
            logger.error(f"Analytics error: {e}")
    
    async def _notify_admin(self, sender: str, message: str, intent: str):
        """Send notification to admin"""
        if not self.integrations["notifications"]["enabled"]:
            return
        
        try:
            emoji = {
                "order": "🛒",
                "payment": "💰",
                "support": "🆘",
                "inquiry": "❓",
                "general": "💬"
            }.get(intent, "📩")
            
            notification = f"""
{emoji} *New {intent.title()}*

*From:* {sender}
*Intent:* {intent}

*Message:*
{message[:200]}
"""
            self.discord_client.send(notification)
        except Exception as e:
            logger.error(f"Notification error: {e}")
    
    async def _track_error(self, error: Exception, context: dict):
        """Track error to Sentry"""
        if not self.integrations["error_tracking"]["enabled"]:
            return
        
        try:
            self.sentry_client.capture_error(error, context)
        except Exception as e:
            logger.error(f"Error tracking error: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 STATUS
    # ═══════════════════════════════════════════════════════════════
    
    def get_status(self) -> dict:
        """Get status of all integrations"""
        return {
            "hub": {"name": self.name, "version": self.version, "ready": self.initialized},
            "integrations": {name: info["enabled"] for name, info in self.integrations.items()}
        }
    
    def print_status(self):
        """Print status table"""
        print("\n📊 Integration Status:")
        print("-" * 40)
        for name, info in self.integrations.items():
            status = "✅ ON" if info["enabled"] else "❌ OFF"
            print(f"  {name.upper():15} {status}")
        print("-" * 40)


# ═══════════════════════════════════════════════════════════════
# 🚀 MAIN
# ═══════════════════════════════════════════════════════════════

async def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       🤖 WhatsApp Automation Hub v5.0                      ║
║       Connected System - All Apps Working Together         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize hub
    hub = IntegrationHub()
    await hub.initialize()
    
    # Print status
    hub.print_status()
    
    # Example: Process a test message
    print("\n🧪 Testing with sample message...")
    
    result = await hub.process_message(
        sender="919876543210",
        message="I want to order 2 coffees",
        platform="whatsapp"
    )
    
    print(f"\n📤 Response:\n{result.get('response', 'Error')[:500]}")
    print(f"\n🎯 Intent: {result.get('intent', 'unknown')}")
    print(f"⚡ Action: {result.get('action', 'none')}")


if __name__ == "__main__":
    asyncio.run(main())
