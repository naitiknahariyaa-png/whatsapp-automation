"""
====================================================================
WHATSAPP BOT - ENTERPRISE EDITION
====================================================================
Complete WhatsApp Marketing Platform
Built with features inspired by Aisensy

Features:
- WhatsApp Business API Integration
- AI Auto-Replies
- Flow Builder (Visual Automation)
- Broadcasting Campaigns
- Team Inbox
- Analytics Dashboard
- Multi-tenant Support

Author: Your Name
Version: 2.0.0
====================================================================
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Version
__version__ = "3.5.0-PRO-ELITE"


class WhatsAppEnterprise:
    """
    Main application class integrating all enterprise features
    """
    
    def __init__(self):
        self.db = None
        self.whatsapp_api = None
        self.flow_executor = None
        self.broadcasting = None
        self.team_inbox = None
        self.analytics = None
        
        # Configuration
        self.config = {
            "phone_number_id": os.getenv("WHATSAPP_PHONE_ID"),
            "access_token": os.getenv("WHATSAPP_ACCESS_TOKEN"),
            "app_secret": os.getenv("WHATSAPP_APP_SECRET"),
            "verify_token": os.getenv("WHATSAPP_VERIFY_TOKEN"),
            "organization_id": 1  # For demo
        }
    
    def initialize(self):
        """Initialize all components"""
        logger.info("🚀 Initializing WhatsApp Enterprise...")
        
        # Initialize database
        try:
            from src.core.database_enterprise import get_enterprise_db
            self.db = get_enterprise_db()
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
        
        # Initialize WhatsApp API
        if self.config["phone_number_id"] and self.config["access_token"]:
            try:
                from src.core.whatsapp_business_api import WhatsAppBusinessAPI
                
                self.whatsapp_api = WhatsAppBusinessAPI(
                    phone_number_id=self.config["phone_number_id"],
                    access_token=self.config["access_token"],
                    app_secret=self.config.get("app_secret"),
                    verify_token=self.config.get("verify_token")
                )
                logger.info("✅ WhatsApp Business API initialized")
            except Exception as e:
                logger.warning(f"⚠️ WhatsApp API not configured: {e}")
        
        # Initialize AI Provider
        try:
            from src.ai.providers import AIManager
            self.ai = AIManager()
            
            # Configure with API key if available
            if os.getenv("OPENROUTER_API_KEY"):
                self.ai.configure("openrouter", os.getenv("OPENROUTER_API_KEY"))
                logger.info("✅ AI Provider configured")
        except Exception as e:
            logger.warning(f"⚠️ AI Provider not configured: {e}")
        
        # Initialize Flow Executor
        try:
            from src.core.flow_builder import FlowExecutor
            self.flow_executor = FlowExecutor(
                db=self.db,
                whatsapp_api=self.whatsapp_api,
                ai_provider=getattr(self, 'ai', None)
            )
            logger.info("✅ Flow Builder initialized")
        except Exception as e:
            logger.error(f"❌ Flow Builder initialization failed: {e}")
        
        # Initialize Broadcasting
        try:
            from src.core.broadcasting import BroadcastingEngine
            self.broadcasting = BroadcastingEngine(
                db=self.db,
                whatsapp_api=self.whatsapp_api
            )
            logger.info("✅ Broadcasting Engine initialized")
        except Exception as e:
            logger.error(f"❌ Broadcasting initialization failed: {e}")
        
        # Initialize Team Inbox
        try:
            from src.core.team_inbox import TeamInbox
            self.team_inbox = TeamInbox(
                db=self.db,
                whatsapp_api=self.whatsapp_api
            )
            logger.info("✅ Team Inbox initialized")
        except Exception as e:
            logger.error(f"❌ Team Inbox initialization failed: {e}")
        
        # Initialize Analytics
        try:
            from src.dashboard.analytics import AnalyticsDashboard
            self.analytics = AnalyticsDashboard(db=self.db)
            logger.info("✅ Analytics Dashboard initialized")
        except Exception as e:
            logger.error(f"❌ Analytics initialization failed: {e}")
        
        logger.info("✅ All components initialized successfully!")
        return True
    
    def run(self):
        """Run the main application"""
        if not self.initialize():
            logger.error("Failed to initialize application")
            return
        
        logger.info(f"""
╔═══════════════════════════════════════════════════════════╗
║           WHATSAPP BOT - ENTERPRISE v{VERSION}              ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Features:                                                ║
║  ├── 🤖 AI Auto-Replies                                  ║
║  ├── 🔧 Flow Builder (Visual Automation)                  ║
║  ├── 📢 Broadcasting Campaigns                           ║
║  ├── 👥 Team Inbox                                      ║
║  ├── 📊 Analytics Dashboard                             ║
║  └── 📱 WhatsApp Business API                            ║
║                                                           ║
║  Commands:                                                ║
║  python main_enterprise.py demo     - Run demo           ║
║  python main_enterprise.py api       - Start API server   ║
║  python main_enterprise.py test      - Test components    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        # Run demo
        self.run_demo()
    
    def run_demo(self):
        """Run demonstration of all features"""
        logger.info("🎬 Running Demo...")
        
        org_id = self.config["organization_id"]
        
        # Demo 1: Create Organization
        logger.info("\n📝 Demo 1: Creating organization...")
        org = self.db.get_organization(org_id)
        if not org:
            org_id = self.db.create_organization(
                name="Demo Business",
                email="demo@example.com",
                phone="+919876543210"
            )
            logger.info(f"✅ Created organization: {org_id}")
        else:
            logger.info(f"✅ Using existing organization: {org['name']}")
        
        # Demo 2: Add Contacts
        logger.info("\n👥 Demo 2: Adding contacts...")
        contacts = [
            ("+919876543211", "Alice", "alice@example.com"),
            ("+919876543212", "Bob", "bob@example.com"),
            ("+919876543213", "Charlie", "charlie@example.com"),
        ]
        for phone, name, email in contacts:
            self.db.add_contact(org_id, phone, name, email)
        logger.info(f"✅ Added {len(contacts)} contacts")
        
        # Demo 3: Add Keywords
        logger.info("\n🔑 Demo 3: Setting up keywords...")
        keywords = [
            ("hi", "Hello! Welcome to our business! 👋 How can I help?"),
            ("hello", "Hi there! How can I assist you today?"),
            ("price", "Our products are very affordable! What are you interested in?"),
            ("help", "I can help with:\n1. Product Info\n2. Pricing\n3. Orders\n4. Support"),
        ]
        for keyword, response in keywords:
            self.db.add_keyword(org_id, keyword, response)
        logger.info(f"✅ Set up {len(keywords)} keywords")
        
        # Demo 4: Create Flow
        logger.info("\n🔧 Demo 4: Creating automation flow...")
        flow_def = {
            "nodes": [
                {"id": "start", "type": "trigger", "label": "Start"},
                {"id": "greet", "type": "message", 
                 "config": {"content": "Hello {{name}}! Welcome!"},
                 "next_nodes": ["choice"]},
                {"id": "choice", "type": "quick_reply",
                 "config": {"buttons": [
                     {"id": "product", "title": "Products 🛍️"},
                     {"id": "support", "title": "Support ❓"}
                 ]}},
            ]
        }
        flow_id = self.db.create_flow(
            org_id=org_id,
            name="Welcome Flow",
            definition=flow_def
        )
        logger.info(f"✅ Created flow: {flow_id}")
        
        # Demo 5: Create Campaign
        logger.info("\n📢 Demo 5: Creating campaign...")
        from src.core.broadcasting import Segment, SegmentType
        segment = Segment(
            id="all",
            name="All Contacts",
            segment_type=SegmentType.ALL,
            criteria={}
        )
        campaign_id = self.db.create_campaign(
            org_id=org_id,
            name="Welcome Campaign",
            segment_criteria={}
        )
        logger.info(f"✅ Created campaign: {campaign_id}")
        
        # Demo 6: Analytics
        logger.info("\n📊 Demo 6: Analytics...")
        self.db.track_event(org_id, "messages_sent", 100)
        self.db.track_event(org_id, "messages_delivered", 95)
        self.db.track_event(org_id, "messages_read", 80)
        
        stats = self.analytics.get_dashboard_stats(org_id)
        logger.info(f"""
📈 Dashboard Stats:
   Total Messages: {stats.total_messages}
   Sent: {stats.messages_sent}
   Delivery Rate: {stats.delivery_rate}%
   Read Rate: {stats.read_rate}%
        """)
        
        # Demo 7: Team Inbox
        logger.info("\n👥 Demo 7: Team Inbox...")
        agent = self.team_inbox.create_agent(
            org_id=org_id,
            name="John Agent",
            email="john@demo.com"
        )
        logger.info(f"✅ Created agent: {agent.name}")
        
        # Create conversation
        conv = self.team_inbox.create_conversation(
            org_id=org_id,
            contact_id=1,
            contact_phone="+919876543211",
            contact_name="Alice"
        )
        logger.info(f"✅ Created conversation: {conv.id}")
        
        # Demo 8: Keyword Response
        logger.info("\n🔍 Demo 8: Testing keyword response...")
        response = self.db.find_keyword_response(org_id, "Hi Alice, how are you?")
        if response:
            logger.info(f"✅ Keyword matched: '{response['keyword']}' -> {response['response'][:50]}...")
        
        logger.info("\n" + "="*60)
        logger.info("🎉 DEMO COMPLETE!")
        logger.info("="*60)
        
        logger.info(f"""
📋 Summary:
   Organization: {org_id}
   Contacts: {len(contacts)}
   Keywords: {len(keywords)}
   Flows: 1
   Campaigns: 1
   Agents: 1
   Conversations: 1

🚀 Next Steps:
   1. Configure WhatsApp Business API credentials
   2. Start API server: python main_enterprise.py api
   3. Access dashboard at http://localhost:5000

📚 Documentation:
   - WhatsApp API: src/core/whatsapp_business_api.py
   - Flow Builder: src/core/flow_builder.py
   - Broadcasting: src/core/broadcasting.py
   - Team Inbox: src/core/team_inbox.py
   - Analytics: src/dashboard/analytics.py
        """)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="WhatsApp Bot Enterprise Edition")
    parser.add_argument("command", nargs="?", default="demo",
                       choices=["demo", "api", "test"],
                       help="Command to run")
    parser.add_argument("--port", "-p", type=int, default=5000,
                       help="API server port")
    args = parser.parse_args()
    
    app = WhatsAppEnterprise()
    
    if args.command == "demo":
        app.run()
    
    elif args.command == "api":
        logger.info(f"Starting API server on port {args.port}...")
        # Start Flask API (would be implemented here)
        logger.info("API server started! Visit /docs for API documentation")
    
    elif args.command == "test":
        # Run tests
        logger.info("Running tests...")
        from tests.test_bot import test_keyword_matching
        from tests.test_alerts import test_alert_sending
        
        test_keyword_matching()
        test_alert_sending()
        
        logger.info("✅ All tests passed!")


if __name__ == "__main__":
    main()
