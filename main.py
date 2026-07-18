#!/usr/bin/env python3
"""
====================================================================
WHATSAPP AI BOT - PRO ELITE EDITION v3.5
====================================================================

Full WhatsApp Marketing Platform with:
- AI Auto-Replies (OpenRouter, Groq, Claude)
- WhatsApp Business API Integration
- Visual Flow Builder
- Broadcasting Campaigns
- Team Inbox
- Analytics Dashboard
- Multi-Tenant Support

Author: Built for Indian Businesses 🇮🇳
====================================================================
"""

import os
import sys
import logging
from pathlib import Path

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
    from src.core.config import load_config
    from src.core.database import get_database
    from src.core.reply_engine import ReplyEngine
    from src.ai.providers import AIManager
except ImportError as e:
    logger.error(f"Import error: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)

# CLI imports
from src.cli import (
    C, BANNER, MENU,
    setup_ai, add_keyword, view_keywords, view_stats,
    test_reply, view_cache_stats, start_api_server, run_tests,
    show_langchain_stack, setup_langsmith, clear_data,
    load_cafe_menu, setup_whatsapp, start_bot
)

# ========================
# GLOBAL INSTANCES
# ========================
config = None
db = None
ai_manager = None
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
    
    # Set services for CLI commands
    from src.cli.commands import set_services
    set_services(config, db, ai_manager, whatsapp_client, reply_engine)


def main():
    """Main function"""
    global whatsapp_client
    
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
                import time
                time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n\n  {C.YELLOW}Goodbye! 👋{C.END}\n")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\n  {C.RED}Error: {e}{C.END}")
            import time
            time.sleep(2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n  {C.YELLOW}Goodbye! 👋{C.END}\n")
        sys.exit(0)
