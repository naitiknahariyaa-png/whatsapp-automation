#!/usr/bin/env python3
"""
Master Setup Script - Configure All Integrations
Run this to set up all integrations one by one
"""

import os
import sys


def print_banner():
    print("\n" + "="*60)
    print("🚀 WhatsApp Automation - Integration Setup")
    print("="*60)
    print("\nSelect an integration to set up:")
    print()


def show_menu():
    print_banner()
    print("1.  🤖 Groq AI (Already configured if GROQ_API_KEY in .env)")
    print("2.  📱 Google Gemini AI (Already configured if GOOGLE_API_KEY)")
    print("3.  🐱 Ollama Local AI (Already configured if OLLAMA_URL)")
    print("4.  ✈️  Telegram Bot (Already configured if TELEGRAM_BOT_TOKEN)")
    print("5.  💬 OpenWA WhatsApp Gateway")
    print("6.  📱 Discord Webhooks")
    print("7.  💰 Razorpay Payment Gateway")
    print("8.  📝 Notion CRM")
    print("9.  🔍 Sentry Error Tracking")
    print("10. 📊 Posthog Analytics")
    print("11. 📋 Linear Issue Tracker")
    print("12. 📅 Google Calendar")
    print("13. ☁️  Cloudflare R2 Storage")
    print("14. 🗄️  Supabase Database")
    print("15. 🔴 Redis Cache")
    print("16. ⬡ n8n Automation")
    print("0.  Exit")
    print()


def run_setup(module_name: str):
    """Run setup for a specific integration"""
    try:
        module = __import__(f"src.integrations.{module_name}", fromlist=["setup"])
        if hasattr(module, "setup"):
            print("\n" + "="*50)
            module.setup()
        else:
            print(f"❌ No setup function found in {module_name}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    while True:
        show_menu()
        choice = input("Enter your choice (0-16): ").strip()
        
        setups = {
            "1": ("groq", "Skipping - configure GROQ_API_KEY in .env manually"),
            "2": ("gemini", "Skipping - configure GOOGLE_API_KEY in .env manually"),
            "3": ("ollama", "Skipping - configure OLLAMA_URL in .env manually"),
            "4": ("telegram", "Skipping - configure TELEGRAM_BOT_TOKEN in .env manually"),
            "5": ("openwa_memory", "OpenWA Memory Setup"),
            "6": ("discord_client", "Discord Webhook Setup"),
            "7": ("razorpay_client", "Razorpay Setup"),
            "8": ("notion_client", "Notion Setup"),
            "9": ("sentry_client", "Sentry Setup"),
            "10": ("posthog_client", "Posthog Setup"),
            "11": ("linear_client", "Linear Setup"),
            "12": ("google_calendar_client", "Google Calendar Setup"),
            "13": ("cloudflare_r2_client", "Cloudflare R2 Setup"),
            "14": ("supabase_client", "Supabase Setup"),
            "15": ("redis_client", "Redis Setup"),
            "16": ("n8n_client", "n8n Setup"),
        }
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        
        elif choice in setups:
            module, name = setups[choice]
            print(f"\n🔧 Starting {name}...")
            run_setup(module)
        
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
