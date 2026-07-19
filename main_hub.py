#!/usr/bin/env python3
"""
🚀 WhatsApp Automation Hub - Main Launcher
==========================================
Connect all apps in one place!

Menu:
1. Start Unified Hub (all connected)
2. Start WhatsApp Bot (Selenium)
3. Start Telegram Bot
4. Start OpenWA Server
5. Setup Integrations
6. Test Integrations
"""

import os
import sys
import asyncio
import subprocess

# Load .env file safely
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🤖 WhatsApp Automation Hub v5.0                         ║
║                                                               ║
║     🔗 All Apps Connected Together!                          ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
    """)


def show_menu():
    print("\n📋 MAIN MENU:")
    print("-" * 50)
    print("  1. 🚀  Start Unified Hub (ALL CONNECTED)")
    print("  2. 📱  Start WhatsApp Bot (Selenium)")
    print("  3. ✈️   Start Telegram Bot")
    print("  4. 🌐  Start OpenWA Server")
    print("  5. ⚙️   Setup Integrations")
    print("  6. 🧪  Test All Integrations")
    print("  7. 📊  View Status")
    print("  0. ❌  Exit")
    print("-" * 50)


def run_command(script: str, wait: bool = True):
    """Run a Python script"""
    try:
        if wait:
            subprocess.run([sys.executable, script], check=True)
        else:
            subprocess.Popen([sys.executable, script])
            print(f"✅ Started {script}")
    except Exception as e:
        print(f"❌ Error running {script}: {e}")


def setup_integrations():
    """Run setup for all integrations"""
    print("\n⚙️ Setting up integrations...")
    print("-" * 40)
    
    try:
        subprocess.run([sys.executable, "-m", "src.integrations.setup_all"])
    except:
        print("Run: python src/integrations/setup_all.py")


def test_integrations():
    """Test all integrations"""
    print("\n🧪 Testing Integrations...")
    print("-" * 40)
    
    # Test imports
    integrations = [
        ("OpenWA", "src.integrations.openwa_client"),
        ("Razorpay", "src.integrations.razorpay_client"),
        ("Notion", "src.integrations.notion_client"),
        ("Posthog", "src.integrations.posthog_client"),
        ("Sentry", "src.integrations.sentry_client"),
        ("Discord", "src.integrations.discord_client"),
        ("Linear", "src.integrations.linear_client"),
    ]
    
    for name, module in integrations:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
        except Exception as e:
            print(f"  ⚠️  {name}: {e}")


def view_status():
    """View status of all integrations"""
    print("\n📊 Integration Status")
    print("=" * 50)
    
    env_checks = [
        ("GROQ_API_KEY", "AI (Groq)", False),
        ("GOOGLE_API_KEY", "AI (Gemini)", False),
        ("OPENWA_URL", "OpenWA Gateway", False),
        ("OPENWA_API_KEY", "OpenWA API", False),
        ("TELEGRAM_BOT_TOKEN", "Telegram Bot", False),
        ("SUPABASE_URL", "Supabase DB", False),
        ("RAZORPAY_KEY_ID", "Razorpay", False),
        ("NOTION_API_KEY", "Notion CRM", False),
        ("POSTHOG_API_KEY", "Posthog Analytics", False),
        ("SENTRY_DSN", "Sentry", False),
        ("DISCORD_WEBHOOK_URL", "Discord", False),
        ("LINEAR_API_KEY", "Linear", False),
        ("R2_ACCOUNT_ID", "Cloudflare R2", False),
    ]
    
    for var, name, _ in env_checks:
        value = os.getenv(var, "")
        status = "✅" if value else "❌"
        print(f"  {status} {name:20} {'(configured)' if value else '(not set)'}")
    
    print("=" * 50)


async def start_unified_hub():
    """Start the unified hub"""
    print("\n🚀 Starting Unified Hub...")
    print("This connects all integrations!\n")
    
    from src.core.unified_hub import IntegrationHub
    
    hub = IntegrationHub()
    await hub.initialize()
    hub.print_status()
    
    # Run a test
    print("\n🧪 Testing with sample message...")
    result = await hub.process_message(
        sender="919876543210",
        message="I want to order coffee",
        platform="whatsapp"
    )
    
    print(f"\n✅ Test Result:")
    print(f"   Intent: {result.get('intent')}")
    print(f"   Action: {result.get('action')}")
    print(f"   Response: {result.get('response', '')[:200]}...")
    
    return hub


def main():
    print_banner()
    
    while True:
        show_menu()
        choice = input("\n🎯 Enter choice (0-7): ").strip()
        
        if choice == "1":
            # Start unified hub
            asyncio.run(start_unified_hub())
        
        elif choice == "2":
            # Start WhatsApp bot
            print("\n📱 Starting WhatsApp Bot...")
            run_command("main.py")
        
        elif choice == "3":
            # Start Telegram bot
            print("\n✈️ Starting Telegram Bot...")
            run_command("src/telegram/custom_bot.py")
        
        elif choice == "4":
            # Start OpenWA
            print("\n🌐 Starting OpenWA Server...")
            print("Run in C:\\OpenWA folder:")
            print("  docker compose -f docker-compose.dev.yml up -d")
            print("  OR: npm run dev")
        
        elif choice == "5":
            # Setup integrations
            setup_integrations()
        
        elif choice == "6":
            # Test integrations
            test_integrations()
        
        elif choice == "7":
            # View status
            view_status()
        
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice!")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
