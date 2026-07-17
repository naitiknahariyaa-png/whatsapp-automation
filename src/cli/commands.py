"""
====================================================================
COMMANDS - All Menu Command Implementations
====================================================================

Each function corresponds to a menu option in the CLI.
Organized by category for easy maintenance.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from .colors import C

# Get logger
logger = logging.getLogger(__name__)

# Type hints for services (avoid circular imports)
if TYPE_CHECKING:
    from src.core.config import BotConfig
    from src.core.database import Database
    from src.ai.providers import AIManager
    from src.core.whatsapp_client import WhatsAppClient, MockWhatsAppClient
    from src.core.reply_engine import ReplyEngine


# ========================
# GLOBAL SERVICE REFERENCES
# ========================
# These are set by main.py during init
config: 'BotConfig' = None
db: 'Database' = None
ai_manager: 'AIManager' = None
whatsapp_client: 'WhatsAppClient | MockWhatsAppClient' = None
reply_engine: 'ReplyEngine' = None


def set_services(
    cfg: 'BotConfig',
    database: 'Database',
    ai: 'AIManager',
    wa_client,
    engine: 'ReplyEngine'
):
    """Set global service references (called by main.py)"""
    global config, db, ai_manager, whatsapp_client, reply_engine
    config = cfg
    db = database
    ai_manager = ai
    whatsapp_client = wa_client
    reply_engine = engine


# ========================
# AI COMMANDS
# ========================

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
            from src.core.config import save_config
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
            from src.core.config import save_config
            save_config(config)
            ai_manager.configure("groq", api_key)
            print(f"{C.GREEN}✅ Groq configured!{C.END}")
    
    elif choice == "3":
        config.ai.provider = "keyword"
        from src.core.config import save_config
        save_config(config)
        print(f"{C.GREEN}✅ Keyword AI selected!{C.END}")


def test_reply():
    """Test auto-reply with sample message"""
    print(f"\n{C.CYAN}💬 Test Auto-Reply{C.END}\n")
    
    test_message = input(f"{C.GREEN}Enter test message: {C.END}").strip()
    
    if not test_message:
        print(f"{C.YELLOW}No message entered{C.END}")
        return
    
    print(f"\n{C.YELLOW}Processing...{C.END}\n")
    
    response = reply_engine.process_message("test_user", test_message)
    
    print(f"{C.GREEN}🤖 Bot Response:{C.END}\n{response}\n")


def view_cache_stats():
    """View AI response cache statistics"""
    print(f"\n{C.CYAN}⚡ Cache Statistics{C.END}\n")
    
    ai_status = ai_manager.get_status()
    cache_stats = ai_status.get('cache', {})
    
    print(f"{C.GREEN}Cache Size:{C.END} {cache_stats.get('size', 0)}")
    print(f"{C.GREEN}Cache Hits:{C.END} {cache_stats.get('hits', 0)}")
    print(f"{C.GREEN}Cache Misses:{C.END} {cache_stats.get('misses', 0)}")
    print(f"{C.GREEN}Hit Rate:{C.END} {cache_stats.get('hit_rate', '0%')}\n")


# ========================
# KEYWORD COMMANDS
# ========================

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


# ========================
# STATS COMMANDS
# ========================

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
  Keyword: ✅
""")


def clear_data():
    """Clear all data"""
    print(f"\n{C.YELLOW}⚠️ Clear All Data{C.END}\n")
    confirm = input(f"{C.RED}This will delete all messages, keywords, and stats. Are you sure? [y/N]: {C.END}").strip().lower()
    
    if confirm == 'y':
        db.clear_all_data()
        print(f"{C.GREEN}✅ All data cleared!{C.END}")
    else:
        print(f"{C.YELLOW}Cancelled{C.END}")


# ========================
# WHATSAPP COMMANDS
# ========================

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
            from src.core.whatsapp_client import WhatsAppClient
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
        from src.core.whatsapp_client import MockWhatsAppClient
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


# ========================
# SERVER COMMANDS
# ========================

def start_api_server():
    """Start FastAPI server"""
    print(f"\n{C.CYAN}🌐 Starting API Server{C.END}\n")
    print(f"{C.YELLOW}Server will start on http://0.0.0.0:8000{C.END}")
    print(f"{C.YELLOW}Press Ctrl+C to stop{C.END}\n")
    
    try:
        from src.api.webhook import run_server
        run_server(host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Server stopped{C.END}")


# ========================
# TEST COMMANDS
# ========================

def run_tests():
    """Run pytest tests"""
    print(f"\n{C.CYAN}🧪 Running Tests{C.END}\n")
    
    import pytest
    result = pytest.main(["-v", "tests/"])
    
    if result == 0:
        print(f"\n{C.GREEN}✅ All tests passed!{C.END}")
    else:
        print(f"\n{C.RED}❌ Some tests failed{C.END}")


# ========================
# LANGCHAIN COMMANDS
# ========================

def show_langchain_stack():
    """Show LangChain AI stack information"""
    print(f"""
{C.CYAN}🧠 LangChain AI Stack{C.END}

LangChain adds production-grade AI capabilities:

{C.GREEN}Features:{C.END}
  ✅ Chain multiple AI calls together
  ✅ RAG (Retrieval Augmented Generation)
  ✅ Memory and conversation history
  ✅ Tool use and function calling
  ✅ LangSmith: See every message the AI processes
  ✅ Debug when something goes wrong
  ✅ Track response quality over time
  ✅ Measure latency and performance
  ✅ Free tier: 10,000 traces/month
""")
    
    try:
        from src.ai.langchain_integration import demo_langchain, demo_langgraph, demo_langsmith
        print(f"""
{C.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.END}
{C.CYAN}DEMOS AVAILABLE:{C.END}

  To see LangChain demos:
  python -c "from src.ai.langchain_integration import demo_langchain, demo_langgraph, demo_langsmith; demo_langchain(); demo_langgraph(); demo_langsmith()"
""")
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
    
    print(f"""
{C.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.END}
{C.GREEN}Setup LangSmith (Observability):{C.END}

  python -c "from src.cli.commands import setup_langsmith; setup_langsmith()"
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


# ========================
# CAFE COMMANDS
# ========================

def load_cafe_menu():
    """Load cafe menu"""
    print(f"\n{C.CYAN}🏪 Cafe Menu Setup{C.END}\n")
    
    print(f"{C.GREEN}This feature helps restaurants/cafes set up their menu.{C.END}")
    print(f"Place your menu file in the project root:")
    print(f"  • cafe_menu.csv - CSV format menu")
    print(f"  • cafe_menu.xlsx - Excel format menu\n")
    
    # Check if create_cafe_menu.py exists
    if Path("create_cafe_menu.py").exists():
        print(f"{C.YELLOW}Run: python create_cafe_menu.py to generate a sample menu{C.END}")
