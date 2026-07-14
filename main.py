#!/usr/bin/env python3
"""
====================================================================
WHATSAPP AI AUTOMATION TOOL v1.0
Advanced WhatsApp auto-reply with AI-powered responses
====================================================================

Features:
- AI-powered replies (Ollama, OpenAI, Claude, Gemini, DeepSeek)
- Multi-personality bots
- Scheduled messages
- Contact management
- Conversation memory
- Web dashboard
- And more!

Author: Created with OpenHands
License: MIT
====================================================================
"""

import os
import sys
import time
import json
import yaml
import argparse
import signal
from datetime import datetime
from pathlib import Path

# Colors for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

BANNER = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ██╗  ██╗ ██████╗  ██████╗  ██████╗ ██╗  ██╗███████╗     ║
║     ██║ ██╔╝ ██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝██╔════╝     ║
║     █████╔╝  ██████╔╝██║   ██║██║   ██║█████╔╝ █████╗       ║
║     ██╔═██╗  ██╔══██╗██║   ██║██║   ██║██╔═██╗ ██╔══╝       ║
║     ██║  ██╗ ██║  ██║╚██████╔╝╚██████╔╝██║  ██╗███████╗     ║
║     ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝     ║
║                                                               ║
║              🤖 AI AUTOMATION TOOL v1.0 🤖                    ║
║                                                               ║
║     WhatsApp Auto-Reply • AI Responses • Scheduled Messages   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.END}
"""

MENU = f"""
{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}

  {Colors.BOLD}📱 WhatsApp Automation Menu{Colors.END}

{Colors.CYAN}── Core Features ──{Colors.END}
  {Colors.GREEN}[1]{Colors.END}  🚀 Start WhatsApp Bot
  {Colors.GREEN}[2]{Colors.END}  🖥️  Start Web Dashboard
  {Colors.GREEN}[3]{Colors.END}  📊 View Statistics

{Colors.CYAN}── Configuration ──{Colors.END}
  {Colors.GREEN}[4]{Colors.END}  ⚙️  AI Settings
  {Colors.GREEN}[5]{Colors.END}  📝 Manage Auto-Reply Rules
  {Colors.GREEN}[6]{Colors.END}  👥 Contact Management
  {Colors.GREEN}[7]{Colors.END}  ⏰ Scheduled Messages

{Colors.CYAN}── Tools ──{Colors.END}
  {Colors.GREEN}[8]{Colors.END}  🧪 Test AI Response
  {Colors.GREEN}[9]{Colors.END}  📜 View Logs
  {Colors.GREEN}[10]{Colors.END} 🗄️  Database Manager

{Colors.CYAN}── Advanced ──{Colors.END}
  {Colors.GREEN}[11]{Colors.END} 🎭 Bot Personalities
  {Colors.GREEN}[12]{Colors.END} 🧠 Conversation Memory
  {Colors.GREEN}[13]{Colors.END} 🌐 Multi-Language Support

{Colors.GREEN}[0]{Colors.END}   {Colors.RED}Exit{Colors.END}

{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}
"""


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            # Replace environment variables
            for section, values in config.items():
                if isinstance(values, dict):
                    for key, value in values.items():
                        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                            env_var = value[2:-1]
                            config[section][key] = os.getenv(env_var, "")
            return config
    return {}


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text):
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}  {text}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")


# ──────────────────────────────────────────────
# Core Functions
# ──────────────────────────────────────────────

def start_whatsapp_bot():
    """Start the WhatsApp automation bot"""
    print_header("🚀 Starting WhatsApp Bot")
    
    config = load_config()
    
    try:
        from src.core.whatsapp_client import WhatsAppClient
        from src.core.reply_engine import ReplyEngine
        from src.ai.providers import AIProviderRouter
        from src.core.database import Database
        
        print(f"{Colors.GREEN}✓ Loading configuration...{Colors.END}")
        
        # Initialize components
        db = Database(config.get('database', {}))
        ai_router = AIProviderRouter(config.get('ai', {}))
        reply_engine = ReplyEngine(config.get('auto_reply', {}))
        whatsapp = WhatsAppClient(config.get('whatsapp', {}))
        
        print(f"{Colors.GREEN}✓ Initializing AI provider: {config.get('ai', {}).get('provider', 'ollama')}{Colors.END}")
        
        # Check AI provider status
        ai_status = ai_router.check_status()
        print(f"{Colors.BLUE}AI Status:{Colors.END} {ai_status}")
        
        print(f"\n{Colors.GREEN}✓ Connecting to WhatsApp Web...{Colors.END}")
        print(f"{Colors.YELLOW}Please scan the QR code on the browser window!{Colors.END}\n")
        
        # Connect to WhatsApp
        whatsapp.connect()
        
        print(f"\n{Colors.GREEN}✅ WhatsApp Connected! Bot is now ACTIVE!{Colors.END}")
        print(f"{Colors.CYAN}Press Ctrl+C to stop the bot{Colors.END}\n")
        
        # Main loop
        last_message = ""
        while True:
            try:
                # Check for new messages
                messages = whatsapp.get_new_messages()
                
                for msg in messages:
                    if msg['content'] != last_message:
                        sender = msg['sender']
                        content = msg['content']
                        
                        print(f"{Colors.BLUE}📩 From {sender}:{Colors.END} {content}")
                        
                        # Generate response
                        response = reply_engine.get_reply(content, ai_router, sender)
                        
                        # Send response
                        whatsapp.send_message(response)
                        print(f"{Colors.GREEN}📤 Sent:{Colors.END} {response}")
                        
                        # Log to database
                        db.log_message(sender, content, response)
                        
                        last_message = content
                
                time.sleep(config.get('whatsapp', {}).get('check_interval', 3))
                
            except KeyboardInterrupt:
                break
    
    except ImportError as e:
        print(f"{Colors.RED}Error importing modules: {e}{Colors.END}")
        print(f"{Colors.YELLOW}Please run: pip install -r requirements.txt{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")


def start_dashboard():
    """Start the web dashboard"""
    print_header("🌐 Starting Web Dashboard")
    
    config = load_config()
    dashboard_config = config.get('dashboard', {})
    
    if not dashboard_config.get('enabled', True):
        print(f"{Colors.RED}Dashboard is disabled in config.yaml{Colors.END}")
        return
    
    host = dashboard_config.get('host', '0.0.0.0')
    port = dashboard_config.get('port', 5000)
    
    print(f"{Colors.GREEN}✓ Starting dashboard on http://{host}:{port}{Colors.END}")
    print(f"{Colors.CYAN}Open this URL in your browser!{Colors.END}\n")
    
    try:
        from src.core.dashboard import create_dashboard
        app = create_dashboard(config)
        app.run(host=host, port=port, debug=False)
    except ImportError:
        print(f"{Colors.RED}Dashboard module not found{Colors.END}")


def view_statistics():
    """Display bot statistics"""
    print_header("📊 Bot Statistics")
    
    try:
        from src.core.database import Database
        config = load_config()
        db = Database(config.get('database', {}))
        
        stats = db.get_statistics()
        
        print(f"""
{Colors.CYAN}📈 Statistics:{Colors.END}

  {Colors.GREEN}Total Messages:{Colors.END} {stats.get('total_messages', 0)}
  {Colors.GREEN}Total Replies:{Colors.END} {stats.get('total_replies', 0)}
  {Colors.GREEN}Unique Contacts:{Colors.END} {stats.get('unique_contacts', 0)}
  {Colors.GREEN}Auto-Replied:{Colors.END} {stats.get('auto_replied', 0)}
  
{Colors.CYAN}📅 Today:{Colors.END}
  {Colors.GREEN}Messages:{Colors.END} {stats.get('today_messages', 0)}
  {Colors.GREEN}Replies:{Colors.END} {stats.get('today_replies', 0)}
""")
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")


def ai_settings():
    """Configure AI settings"""
    print_header("⚙️ AI Settings")
    
    config = load_config()
    ai_config = config.get('ai', {})
    
    providers = {
        '1': ('ollama', 'Ollama (Local - Free)'),
        '2': ('openai', 'OpenAI (GPT-4)'),
        '3': ('claude', 'Claude (Anthropic)'),
        '4': ('gemini', 'Gemini (Google)'),
        '5': ('deepseek', 'DeepSeek (Budget)'),
    }
    
    print(f"""
{Colors.CYAN}Available AI Providers:{Colors.END}

  {Colors.GREEN}[1]{Colors.END} Ollama (Local - Free)
  {Colors.GREEN}[2]{Colors.END} OpenAI (GPT-4)
  {Colors.GREEN}[3]{Colors.END} Claude (Anthropic)
  {Colors.GREEN}[4]{Colors.END} Gemini (Google)
  {Colors.GREEN}[5]{Colors.END} DeepSeek (Budget)
  
{Colors.CYAN}Current Provider:{Colors.END} {ai_config.get('provider', 'ollama')}
""")
    
    choice = input(f"{Colors.CYAN}Select provider (1-5): {Colors.END}").strip()
    
    if choice in providers:
        new_provider = providers[choice][0]
        
        # Update config
        ai_config['provider'] = new_provider
        
        # Save config
        config['ai'] = ai_config
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f)
        
        print(f"{Colors.GREEN}✓ AI Provider set to: {providers[choice][1]}{Colors.END}")
        
        # Test connection
        try:
            from src.ai.providers import AIProviderRouter
            router = AIProviderRouter(ai_config)
            status = router.check_status()
            print(f"{Colors.BLUE}Status: {status}{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}Note: {e}{Colors.END}")


def manage_auto_reply_rules():
    """Manage auto-reply keyword rules"""
    print_header("📝 Auto-Reply Rules Manager")
    
    config = load_config()
    rules = config.get('auto_reply', {}).get('keywords', [])
    
    while True:
        print(f"""
{Colors.CYAN}Current Rules ({len(rules)}):{Colors.END}
""")
        for i, rule in enumerate(rules, 1):
            print(f"  {Colors.GREEN}[{i}]{Colors.END} '{rule.get('keyword', '')}' → '{rule.get('response', '')}'")
        
        print(f"""
{Colors.CYAN}Options:{Colors.END}
  {Colors.GREEN}[A]{Colors.END} Add new rule
  {Colors.GREEN}[D]{Colors.END} Delete rule
  {Colors.GREEN}[E]{Colors.END} Edit rule
  {Colors.GREEN}[0]{Colors.END} Back to menu
""")
        
        choice = input(f"{Colors.CYAN}Choice: {Colors.END}").strip().lower()
        
        if choice == 'a':
            keyword = input(f"{Colors.CYAN}Enter keyword: {Colors.END}").strip().lower()
            response = input(f"{Colors.CYAN}Enter response: {Colors.END}").strip()
            rules.append({'keyword': keyword, 'response': response})
            print(f"{Colors.GREEN}✓ Rule added!{Colors.END}")
            
        elif choice == 'd':
            try:
                num = int(input(f"{Colors.CYAN}Rule number to delete: {Colors.END}").strip())
                if 1 <= num <= len(rules):
                    rules.pop(num - 1)
                    print(f"{Colors.GREEN}✓ Rule deleted!{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Invalid number{Colors.END}")
                
        elif choice == 'e':
            try:
                num = int(input(f"{Colors.CYAN}Rule number to edit: {Colors.END}").strip())
                if 1 <= num <= len(rules):
                    keyword = input(f"{Colors.CYAN}New keyword (or Enter to skip): {Colors.END}").strip().lower()
                    response = input(f"{Colors.CYAN}New response (or Enter to skip): {Colors.END}").strip()
                    if keyword:
                        rules[num-1]['keyword'] = keyword
                    if response:
                        rules[num-1]['response'] = response
                    print(f"{Colors.GREEN}✓ Rule updated!{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Invalid number{Colors.END}")
                
        elif choice == '0':
            # Save changes
            config['auto_reply']['keywords'] = rules
            with open('config.yaml', 'w') as f:
                yaml.dump(config, f)
            break


def test_ai_response():
    """Test AI response generation"""
    print_header("🧪 Test AI Response")
    
    try:
        from src.ai.providers import AIProviderRouter
        config = load_config()
        router = AIProviderRouter(config.get('ai', {}))
        
        print(f"{Colors.GREEN}✓ AI Router initialized{Colors.END}\n")
        
        while True:
            message = input(f"{Colors.CYAN}Enter test message (or 'exit'): {Colors.END}").strip()
            
            if message.lower() in ('exit', 'quit', 'q'):
                break
            
            print(f"\n{Colors.YELLOW}Generating response...{Colors.END}\n")
            
            response = router.generate_response(message)
            print(f"{Colors.GREEN}AI Response:{Colors.END}\n{response}\n")
            
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")


def view_logs():
    """View bot logs"""
    print_header("📜 Bot Logs")
    
    log_file = Path(__file__).parent / "logs" / "whatsapp_bot.log"
    
    if log_file.exists():
        print(f"{Colors.CYAN}Showing last 50 lines from logs:{Colors.END}\n")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-50:]:
                print(line.rstrip())
    else:
        print(f"{Colors.YELLOW}No log file found{Colors.END}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="WhatsApp AI Automation Tool")
    parser.add_argument("--dashboard", "-d", action="store_true", help="Start web dashboard")
    parser.add_argument("--status", "-s", action="store_true", help="Show bot status")
    args = parser.parse_args()
    
    if args.dashboard:
        start_dashboard()
        return
    
    if args.status:
        view_statistics()
        return
    
    # Interactive menu
    clear_screen()
    print(BANNER)
    
    while True:
        print(MENU)
        choice = input(f"  {Colors.BOLD}Enter your choice:{Colors.END} ").strip()
        
        if choice == "1":
            clear_screen()
            start_whatsapp_bot()
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.END}")
            clear_screen()
            print(BANNER)
            
        elif choice == "2":
            clear_screen()
            start_dashboard()
            
        elif choice == "3":
            clear_screen()
            view_statistics()
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.END}")
            clear_screen()
            print(BANNER)
            
        elif choice == "4":
            clear_screen()
            ai_settings()
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.END}")
            clear_screen()
            print(BANNER)
            
        elif choice == "5":
            clear_screen()
            manage_auto_reply_rules()
            clear_screen()
            print(BANNER)
            
        elif choice == "6":
            print(f"\n{Colors.YELLOW}Contact Management coming soon!{Colors.END}\n")
            
        elif choice == "7":
            print(f"\n{Colors.YELLOW}Scheduled Messages coming soon!{Colors.END}\n")
            
        elif choice == "8":
            clear_screen()
            test_ai_response()
            clear_screen()
            print(BANNER)
            
        elif choice == "9":
            clear_screen()
            view_logs()
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.END}")
            clear_screen()
            print(BANNER)
            
        elif choice == "0":
            print(f"\n  {Colors.YELLOW}Goodbye! 👋{Colors.END}\n")
            sys.exit(0)
            
        else:
            print(f"\n  {Colors.RED}Invalid choice! Please try again.{Colors.END}\n")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Colors.YELLOW}Goodbye! 👋{Colors.END}\n")
        sys.exit(0)
