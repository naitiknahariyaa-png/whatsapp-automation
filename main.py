#!/usr/bin/env python3
"""
====================================================================
WHATSAPP AI BOT v3.0 - ADVANCED VERSION
====================================================================

Advanced Features:
✅ Pydantic Config Validation
✅ SQLite with Proper Error Handling
✅ Multi-Provider AI (OpenRouter/Groq/Keyword)
✅ Response Caching
✅ FastAPI Webhook Endpoint
✅ Async Support
✅ GitHub Actions CI/CD
✅ pytest Unit Tests

Author: Built for Indian Businesses 🇮🇳
====================================================================
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# ========================
# LOGGING SETUP
# ========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========================
# IMPORTS
# ========================
try:
    from src.core.config import load_config, save_config, BotConfig
    from src.core.database import get_database, DatabaseError
    from src.core.whatsapp_client import WhatsAppClient, MockWhatsAppClient
    from src.core.reply_engine import ReplyEngine
    from src.ai.providers import AIManager, KeywordAI, OpenRouterAI, GroqAI
except ImportError as e:
    logger.error(f"Import error: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)

# ========================
# COLORS
# ========================
class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

# ========================
# BANNER
# ========================
BANNER = f"""
{C.CYAN}{C.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║       🤖 WHATSAPP AI BOT v3.0 🤖                           ║
║       ADVANCED VERSION - PRODUCTION READY!                  ║
║                                                               ║
║     ✅ Pydantic Validation  ✅ FastAPI Webhook               ║
║     ✅ Multi-Provider AI   ✅ GitHub Actions CI/CD         ║
║     ✅ SQLite (Safe)      ✅ pytest Tests                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{C.END}
"""

MENU = f"""
{C.CYAN}═══════════════════════════════════════════════════════════{C.END}

  {C.BOLD}📱 WhatsApp AI Bot v3.0 - Production Ready{C.END}

{C.GREEN}[1]{C.END}  🚀 Start Auto-Reply Bot
{C.GREEN}[2]{C.END}  📱 Setup WhatsApp Session
{C.GREEN}[3]{C.END}  🤖 Setup AI Provider
{C.GREEN}[4]{C.END}  📝 Add Keywords
{C.GREEN}[5]{C.END}  📊 View Statistics
{C.GREEN}[6]{C.END}  💬 Test Auto-Reply
{C.GREEN}[7]{C.END}  📜 View Keywords
{C.GREEN}[8]{C.END}  🏪 Cafe Menu Options
{C.GREEN}[9]{C.END}  ⚡ View Cache Stats
{C.GREEN}[10]{C.END} 🌐 Start API Server (FastAPI)
{C.GREEN}[11]{C.END} 🧪 Run Tests
{C.GREEN}[12]{C.END} 🧠 LangChain AI Stack
{C.GREEN}[13]{C.END} 🗑️  Clear All Data

{C.GREEN}[0]{C.END}   {C.RED}Exit{C.END}

{C.CYAN}═══════════════════════════════════════════════════════════{C.END}
"""

# ========================
# GLOBAL INSTANCES
# ========================
config: Optional[BotConfig] = None
db = None
ai_manager: Optional[AIManager] = None
whatsapp_client = None
reply_engine = None


def init_services():
    """Initialize all services"""
    global config, db, ai_manager, reply_engine
    
    logger.info("Initializing services...")
    
    # Load config
    config = load_config()
    logger.info(f"Config loaded: {config.ai.provider} AI provider")
    
    # Initialize database
    db = get_database(config.database.path)
    logger.info("Database initialized")
    
    # Initialize AI
    ai_manager = AIManager()
    
    if config.ai.openrouter_api_key:
        ai_manager.configure("openrouter", config.ai.openrouter_api_key, config.ai.model)
        logger.info("OpenRouter AI configured")
    elif config.ai.groq_api_key:
        ai_manager.configure("groq", config.ai.groq_api_key, config.ai.model)
        logger.info("Groq AI configured")
    else:
        logger.info("Using Keyword AI")
    
    # Initialize Reply Engine
    reply_engine = ReplyEngine(
        db=db,
        ai_manager=ai_manager,
        business_name=config.business.name,
        business_hours=config.business.hours,
        business_phone=config.business.phone
    )
    logger.info("Reply Engine initialized")


def setup_ai():
    """Setup AI provider"""
    print(f"\n{C.CYAN}{C.BOLD}🤖 AI Setup{C.END}\n")
    
    print(f"""{C.GREEN}
╔═══════════════════════════════════════════════════════════════╗
║  Choose AI Provider:                                       ║
╠═══════════════════════════════════════════════════════════════╣
║  [1] OpenRouter - 100+ FREE models (RECOMMENDED)           ║
║  [2] Groq - Fast AI                                      ║
║  [3] Keyword AI - No API needed                           ║
╚═══════════════════════════════════════════════════════════════╝
{C.END}""")
    
    choice = input(f"{C.CYAN}Choice [1/2/3]: {C.END}").strip()
    
    if choice == "1":
        print(f"\n{C.CYAN}OpenRouter Setup{C.END}")
        print(f"Get free API key: https://openrouter.ai/keys")
        api_key = input("Paste API key: ").strip()
        
        if api_key:
            config.ai.openrouter_api_key = api_key
            config.ai.provider = "openrouter"
            config.ai.model = "openrouter/free"
            save_config(config)
            ai_manager.configure("openrouter", api_key, "openrouter/free")
            print(f"{C.GREEN}✅ OpenRouter configured!{C.END}")
    
    elif choice == "2":
        print(f"\n{C.CYAN}Groq Setup{C.END}")
        print(f"Get free API key: https://console.groq.com/keys")
        api_key = input("Paste API key: ").strip()
        
        if api_key:
            config.ai.groq_api_key = api_key
            config.ai.provider = "groq"
            save_config(config)
            ai_manager.configure("groq", api_key)
            print(f"{C.GREEN}✅ Groq configured!{C.END}")
    
    elif choice == "3":
        config.ai.provider = "keyword"
        save_config(config)
        print(f"{C.GREEN}✅ Keyword AI selected!{C.END}")


def add_keyword():
    """Add keyword"""
    print(f"\n{C.CYAN}Add Keyword{C.END}\n")
    
    keyword = input(f"{C.GREEN}Keyword: {C.END}").strip().lower()
    if not keyword:
        print(f"{C.RED}Keyword cannot be empty!{C.END}")
        return
    
    response = input(f"{C.GREEN}Response: {C.END}").strip()
    if not response:
        print(f"{C.RED}Response cannot be empty!{C.END}")
        return
    
    if db.add_keyword(keyword, response):
        print(f"{C.GREEN}✅ Keyword added!{C.END}")
    else:
        print(f"{C.RED}❌ Failed to add keyword{C.END}")


def view_keywords():
    """View all keywords"""
    keywords = db.get_all_keywords()
    
    if not keywords:
        print(f"{C.YELLOW}No keywords yet!{C.END}")
        return
    
    print(f"\n{C.CYAN}Keywords ({len(keywords)}):{C.END}\n")
    for kw in keywords:
        print(f"  • {kw['keyword']} → {kw['response'][:40]}...")


def view_stats():
    """View statistics"""
    stats = db.get_stats()
    keywords = db.get_all_keywords()
    ai_status = ai_manager.get_status()
    
    print(f"""
{C.CYAN}📊 Statistics{C.END}

{C.GREEN}Messages:{C.END} {stats.get('total_messages', 0)}
{C.GREEN}Replies:{C.END} {stats.get('total_replies', 0)}
{C.GREEN}AI Responses:{C.END} {stats.get('total_ai_responses', 0)}
{C.GREEN}Keywords:{C.END} {len(keywords)}

{C.CYAN}AI Status:{C.END}
  Provider: {ai_status['current']}
  OpenRouter: {'✅' if ai_status['openrouter'] else '❌'}
  Groq: {'✅' if ai_status['groq'] else '❌'}
  Keyword: {'✅' if ai_status['keyword'] else '❌'}

{C.CYAN}Cache:{C.END}
  {ai_status['cache']['hit_rate']} hit rate
  {ai_status['cache']['hits']} hits, {ai_status['cache']['misses']} misses
""")


def test_reply():
    """Test auto-reply"""
    print(f"\n{C.CYAN}Test Auto-Reply{C.END}")
    print(f"Current AI: {ai_manager.get_status()['current']}\n")
    
    while True:
        msg = input(f"{C.CYAN}You: {C.END}").strip()
        if msg.lower() in ('exit', 'quit', 'q'):
            break
        
        if not msg:
            continue
        
        print(f"{C.YELLOW}Thinking...{C.END}")
        
        # Use Reply Engine for smart responses
        response = reply_engine.process_message("test_user", msg)
        
        if response:
            print(f"{C.GREEN}Bot: {C.END}{response}\n")
        else:
            print(f"{C.RED}No response{C.END}\n")


def load_cafe_menu():
    """Load cafe menu"""
    print(f"\n{C.CYAN}Cafe Menu Options{C.END}\n")
    print(f"{C.GREEN}[1]{C.END} Load Pre-made Cafe Keywords")
    print(f"{C.GREEN}[2]{C.END} Load from CSV file")
    print(f"{C.GREEN}[3]{C.END} Back\n")
    
    choice = input(f"{C.CYAN}Choice: {C.END}").strip()
    
    if choice == "1":
        load_premade_keywords()
    elif choice == "2":
        load_csv_menu()


def load_premade_keywords():
    """Load pre-made cafe keywords"""
    keywords = [
        ("hi", "Hello! 👋 Welcome! How can I help you?"),
        ("hello", "Hi there! 😊 How may I assist you?"),
        ("menu", "📋 Our Menu:\n☕ Coffee\n🍔 Burgers\n🍕 Pizza\n🍝 Pasta\n🍰 Desserts\n\nWhat would you like?"),
        ("coffee", "☕ Coffee Menu:\n• Espresso - ₹99\n• Cappuccino - ₹129\n• Latte - ₹149\n• Cold Coffee - ₹179"),
        ("burger", "🍔 Burgers:\n• Veg Burger - ₹149\n• Chicken Burger - ₹189\n• Zinger Burger - ₹229"),
        ("pizza", "🍕 Pizza:\n• Margherita - ₹199\n• Farmhouse - ₹249\n• Chicken Supreme - ₹349"),
        ("price", "💰 Our prices are affordable!\n• Coffee: ₹99-179\n• Burgers: ₹149-299\n• Pizza: ₹199-499"),
        ("hours", "🕐 Open:\nMon-Fri: 9 AM - 11 PM\nSat-Sun: 10 AM - 12 AM"),
        ("delivery", "🚚 Yes! We deliver!\nWithin city limits.\nCall to order!"),
        ("order", "🛒 To order:\n• Call us\n• WhatsApp us\n• Or visit directly!"),
        ("thank", "You're welcome! 😊"),
        ("thanks", "Happy to help! 🙌"),
        ("bye", "Goodbye! 👋 See you soon!"),
        ("help", "I can help with: Menu, Prices, Orders, Hours, Location! 😊"),
    ]
    
    count = 0
    for keyword, response in keywords:
        if db.add_keyword(keyword, response):
            count += 1
    
    print(f"{C.GREEN}✅ Loaded {count} cafe keywords!{C.END}")


def load_csv_menu():
    """Load menu from CSV"""
    print(f"\n{C.YELLOW}CSV Format:{C.END}")
    print(f"  Category,Item,Price,Keywords\n")
    
    file_path = input(f"{C.GREEN}Enter CSV file path (or press Enter for sample): {C.END}").strip()
    
    if not file_path:
        print(f"{C.YELLOW}No file specified.{C.END}")
        return
    
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        
        count = 0
        for _, row in df.iterrows():
            item = str(row.get('Item', ''))
            price = str(row.get('Price', ''))
            keywords = str(row.get('Keywords', ''))
            
            if item and item != 'nan':
                response = f"{item}"
                if price and price != 'nan':
                    response = f"{item} - ₹{price}"
                
                for kw in keywords.split(','):
                    kw = kw.strip().lower()
                    if kw and db.add_keyword(kw, response):
                        count += 1
        
        print(f"{C.GREEN}✅ Loaded {count} keywords from CSV!{C.END}")
    except Exception as e:
        print(f"{C.RED}Error: {e}{C.END}")


def view_cache_stats():
    """View cache statistics"""
    stats = ai_manager.get_status()['cache']
    
    print(f"""
{C.CYAN}⚡ Cache Statistics{C.END}

Cached: {stats['size']}
Hits: {stats['hits']}
Misses: {stats['misses']}
Hit Rate: {stats['hit_rate']}
""")


def start_api_server():
    """Start FastAPI webhook server"""
    print(f"""
{C.CYAN}🌐 Starting API Server{C.END}

The API server provides webhook endpoints:

  • POST /webhook/message - Handle messages
  • GET /stats - Get statistics
  • POST /webhook/keyword - Add keywords
  • GET /keywords - List keywords

Starting on http://0.0.0.0:8000
Press Ctrl+C to stop.
""")
    
    try:
        from src.api.webhook import run_server
        run_server()
    except ImportError:
        print(f"{C.RED}FastAPI not installed. Run: pip install fastapi uvicorn{C.END}")
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Server stopped.{C.END}")


def run_tests():
    """Run pytest tests"""
    print(f"\n{C.CYAN}🧪 Running Tests{C.END}\n")
    
    try:
        import pytest
        pytest.main(["tests/", "-v", "--tb=short"])
    except ImportError:
        print(f"{C.RED}pytest not installed. Run: pip install pytest{C.END}")


def clear_data():
    """Clear all data"""
    print(f"\n{C.RED}⚠️ Clear All Data{C.END}\n")
    
    confirm = input(f"{C.RED}Type 'yes' to confirm: {C.END}")
    
    if confirm.lower() == 'yes':
        try:
            db.clear_all_data()
            ai_manager.keyword = KeywordAI()  # Reset keyword defaults
            print(f"{C.GREEN}✅ All data cleared!{C.END}")
        except DatabaseError as e:
            print(f"{C.RED}Error: {e}{C.END}")
    else:
        print(f"{C.YELLOW}Cancelled.{C.END}")


def show_langchain_stack():
    """Show LangChain AI Stack information and demos"""
    print(f"""
{C.CYAN}╔═══════════════════════════════════════════════════════════════╗
║  🧠 LangChain AI Stack - Production Ready                    ║
╚═══════════════════════════════════════════════════════════════╝{C.END}

{C.YELLOW}What is LangChain Stack?{C.END}

🧩 LangChain — builds the components
   The Lego blocks: models, prompts, tools, memory
   → Gives you the pieces

🔵 LangGraph — orchestrates the workflow
   State management, loops, branching, decisions
   → Runs the workflow

🟡 LangSmith — observes everything
   Traces every step, debug what broke, evaluate quality
   → Watches what happens

{C.GREEN}{C.BOLD}One-liner:{C.END}
  📦 LangChain builds. 🔵 LangGraph orchestrates. 🟡 LangSmith observes.{C.END}


{C.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.END}
{C.CYAN}STATUS CHECK:{C.END}
""")
    
    # Try to import and check
    try:
        from src.ai.langchain_integration import (
            LANGCHAIN_AVAILABLE,
            LANGSMITH_AVAILABLE,
            ProductionAIManager
        )
        
        print(f"  LangChain: {'✅ Installed' if LANGCHAIN_AVAILABLE else '❌ Not installed'}")
        print(f"  LangSmith: {'✅ Installed' if LANGSMITH_AVAILABLE else '❌ Not installed'}")
        
        if not LANGCHAIN_AVAILABLE:
            print(f"""
{C.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.END}
{C.GREEN}To enable LangChain (Production AI), run:{C.END}

  pip install langchain langchain-openai langsmith

{C.CYAN}Benefits of LangChain Stack:{C.END}
  ✅ Better AI understanding
  ✅ Tool use (search, calculate, etc.)
  ✅ Conversation memory
  ✅ Intent classification
  ✅ Workflow orchestration
  ✅ Full observability with traces
""")
        
        if LANGCHAIN_AVAILABLE:
            print(f"""
{C.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.END}
{C.CYAN}LANGSMITH SETUP (Free Tier):{C.END}

  1. Go to: https://smith.langchain.com/settings
  2. Create free account
  3. Get API key
  4. Add to .env:
     LANGSMITH_API_KEY=your-key-here

{C.CYAN}What you get with LangSmith:{C.END}
  ✅ See every message the AI processes
  ✅ Debug when something goes wrong
  ✅ Track response quality over time
  ✅ Measure latency and performance
  ✅ Free tier: 10,000 traces/month
""")
    
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
    
    print(f"""
{C.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.END}
{C.CYAN}DEMOS AVAILABLE:{C.END}

  To see LangChain demos:
  python -c "from src.ai.langchain_integration import demo_langchain, demo_langgraph, demo_langsmith; demo_langchain(); demo_langgraph(); demo_langsmith()"
""")


def setup_langsmith():
    """Setup LangSmith observability"""
    print(f"""
{C.CYAN}🟡 LangSmith Setup - AI Observability{C.END}

LangSmith helps you:
  ✅ Trace every AI decision
  ✅ Debug when responses are wrong
  ✅ Evaluate AI quality over time
  ✅ Monitor performance metrics

{C.YELLOW}Steps:{C.END}

  1. Go to: https://smith.langchain.com
  2. Sign up (free)
  3. Create project: "whatsapp-business-bot"
  4. Copy API key

  Then paste your API key below:
""")
    
    api_key = input(f"{C.GREEN}LangSmith API Key: {C.END}").strip()
    
    if api_key:
        # Save to .env
        env_file = Path(".env")
        env_content = f"\nLANGSMITH_API_KEY={api_key}\n"
        
        with open(env_file, "a") as f:
            f.write(env_content)
        
        print(f"""
{C.GREEN}✅ LangSmith API key saved!{C.END}

{C.CYAN}To activate, you need to install LangChain packages:{C.END}

  pip install langchain langchain-openai langsmith

{C.YELLOW}Then restart the bot.{C.END}
""")


def setup_whatsapp():
    """Setup WhatsApp connection"""
    global whatsapp_client
    
    print(f"""
{C.CYAN}📱 WhatsApp Setup{C.END}

{C.YELLOW}Options:{C.END}

{C.GREEN}[1]{C.END} Connect with WhatsApp Web (QR Code)
{C.GREEN}[2]{C.END} Use Mock Mode (Testing Only)
{C.GREEN}[3]{C.END} Setup WhatsApp Business Cloud API

{C.YELLOW}Note:{C.END} WhatsApp Web uses Selenium - you'll need to scan QR code.
{C.YELLOW}Cloud API requires Meta Business account setup.{C.END}
""")
    
    choice = input(f"{C.CYAN}Choice [1/2/3]: {C.END}").strip()
    
    if choice == "1":
        print(f"\n{C.GREEN}Connecting to WhatsApp Web...{C.END}")
        print(f"{C.YELLOW}This will open a browser window.{C.END}")
        print(f"{C.YELLOW}Scan the QR code within 20 seconds.{C.END}\n")
        
        try:
            whatsapp_client = WhatsAppClient(
                session_dir="data/session",
                headless=False,
                verbose=True
            )
            
            if whatsapp_client.connect():
                print(f"{C.GREEN}✅ Connected to WhatsApp!{C.END}")
            else:
                print(f"{C.RED}❌ Failed to connect{C.END}")
                
        except Exception as e:
            print(f"{C.RED}Error: {e}{C.END}")
            print(f"\n{C.YELLOW}Make sure Chrome is installed and Selenium is set up.{C.END}")
    
    elif choice == "2":
        print(f"\n{C.GREEN}Using Mock Mode (for testing){C.END}")
        whatsapp_client = MockWhatsAppClient()
        whatsapp_client.connect()
        print(f"{C.GREEN}✅ Mock mode enabled!{C.END}")
    
    elif choice == "3":
        print(f"\n{C.YELLOW}WhatsApp Business Cloud API Setup{C.END}")
        print(f"Get setup guide: https://developers.facebook.com/docs/whatsapp")
        
        phone_id = input(f"{C.GREEN}Phone Number ID: {C.END}").strip()
        token = input(f"{C.GREEN}Access Token: {C.END}").strip()
        
        if phone_id and token:
            print(f"{C.GREEN}✅ Cloud API configured!{C.END}")
            print(f"{C.YELLOW}Note: Cloud API integration coming soon!{C.END}")
        else:
            print(f"{C.RED}❌ Both fields required{C.END}")


def start_bot():
    """Start the auto-reply bot"""
    global whatsapp_client
    
    print(f"""
{C.CYAN}🚀 Start Auto-Reply Bot{C.END}

Bot Status:
  • AI: {ai_manager.get_status()['current']}
  • WhatsApp: {'Connected' if whatsapp_client and whatsapp_client.is_connected else 'Not Connected'}
  • Keywords: {len(db.get_all_keywords())}
""")
    
    # Check if WhatsApp is connected
    if not whatsapp_client or not whatsapp_client.is_connected:
        print(f"{C.YELLOW}WhatsApp not connected!{C.END}")
        connect = input("Connect now? [y/N]: ").strip().lower()
        
        if connect == 'y':
            setup_whatsapp()
        else:
            print(f"\n{C.YELLOW}Starting in TEST mode (no actual WhatsApp messages){C.END}")
            test_reply()
            return
    
    # Define message handler
    def handle_message(sender: str, message: str) -> str:
        return reply_engine.process_message(sender, message)
    
    # Start monitoring
    print(f"\n{C.GREEN}✅ Bot is running!{C.END}")
    print(f"{C.YELLOW}Monitoring for messages...{C.END}")
    print(f"{C.YELLOW}Press Ctrl+C to stop.{C.END}\n")
    
    try:
        whatsapp_client.start_monitoring(handle_message)
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Stopping bot...{C.END}")
        whatsapp_client.stop_monitoring()


def main():
    """Main function"""
    global config
    
    # Initialize
    try:
        init_services()
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        print(f"{C.RED}Failed to initialize: {e}{C.END}")
        return
    
    # Main loop
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        print(MENU)
        
        choice = input(f"{C.BOLD}Enter choice: {C.END}").strip()
        
        try:
            if choice == "1":
                start_bot()
            
            elif choice == "2":
                setup_whatsapp()
            
            elif choice == "3":
                setup_ai()
                input(f"\n{C.GREEN}Press Enter to continue...{C.END}")
            
            elif choice == "4":
                add_keyword()
                input(f"\n{C.GREEN}Press Enter to continue...{C.END}")
            
            elif choice == "5":
                view_stats()
                input(f"\n{C.GREEN}Press Enter to continue...{C.END}")
            
            elif choice == "6":
                test_reply()
            
            elif choice == "7":
                view_keywords()
                input(f"\n{C.GREEN}Press Enter to continue...{C.END}")
            
            elif choice == "8":
                load_cafe_menu()
                input(f"\n{C.GREEN}Press Enter to continue...{C.END}")
            
            elif choice == "9":
                view_cache_stats()
                input(f"\n{C.GREEN}Press Enter to continue...{C.END}")
            
            elif choice == "10":
                start_api_server()
            
            elif choice == "11":
                run_tests()
                input(f"\n{C.GREEN}Press Enter to continue...{C.END}")
            
            elif choice == "12":
                show_langchain_stack()
                input(f"\n{C.GREEN}Press Enter to continue...{C.END}")
            
            elif choice == "13":
                clear_data()
                input(f"\n{C.GREEN}Press Enter to continue...{C.END}")
            
            elif choice == "0":
                print(f"\n  {C.YELLOW}Goodbye! 👋{C.END}\n")
                break
            
            else:
                print(f"\n  {C.RED}Invalid choice!{C.END}")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n\n  {C.YELLOW}Goodbye! 👋{C.END}\n")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\n  {C.RED}Error: {e}{C.END}")
            time.sleep(2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n  {C.YELLOW}Goodbye! 👋{C.END}\n")
        sys.exit(0)
