#!/usr/bin/env python3
"""
Master Setup Script - Configure ALL 50+ Integrations
Run this to set up all integrations one by one
"""

import os
import sys


def print_banner():
    print("\n" + "="*70)
    print("🚀 WhatsApp Automation Hub - Integration Setup (50+ FREE)")
    print("="*70)
    print("\nSelect an integration category:")
    print()


def show_menu():
    print_banner()
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║ 🤖 AI & MACHINE LEARNING                                  ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 1.  🤖 Groq AI (configure GROQ_API_KEY in .env)            ║")
    print("║ 2.  🤖 HuggingFace (FREE models)                          ║")
    print("║ 3.  🎨 Stable Diffusion (Image generation)                 ║")
    print("║ 4.  🧠 Dify (Visual AI workflow builder)                   ║")
    print("║ 5.  🐱 Ollama (Local AI - no API cost)                      ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 📱 WHATSAPP & COMMUNICATION                                ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 6.  💬 OpenWA WhatsApp Gateway                             ║")
    print("║ 7.  ✈️  Telegram Bot                                       ║")
    print("║ 8.  💬 Chatwoot (Unified inbox)                           ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 💰 PAYMENTS & COMMERCE                                     ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 9.  💰 Razorpay (India - UPI, Cards)                       ║")
    print("║ 10. 🛒 Medusa (E-commerce engine)                          ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 🗄️ DATABASE & STORAGE                                       ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 11. 🗄️  Supabase (Cloud PostgreSQL)                        ║")
    print("║ 12. 🔴 Redis (Fast caching)                               ║")
    print("║ 13. 🍃 MongoDB (NoSQL database)                           ║")
    print("║ 14. ☁️  Cloudflare R2 (10GB FREE)                          ║")
    print("║ 15. 🗳️  MinIO (S3-compatible storage)                       ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 🔍 SEARCH & VECTORS                                        ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 16. 🔍 Meilisearch (Lightning search)                     ║")
    print("║ 17. 🧠 Qdrant (Vector database)                            ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 📋 CRM & BUSINESS                                         ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 18. 📝 Notion (CRM & Knowledge base)                       ║")
    print("║ 19. 📋 Linear (Issue tracking)                            ║")
    print("║ 20. 📅 Cal.com (Appointment booking)                       ║")
    print("║ 21. 📅 Google Calendar                                     ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 📊 ANALYTICS & MONITORING                                  ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 22. 📊 Posthog (Product analytics)                        ║")
    print("║ 23. 🔍 Sentry (Error tracking)                           ║")
    print("║ 24. 📈 Plausible (Privacy analytics)                      ║")
    print("║ 25. 📊 Netdata (Real-time monitoring)                     ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 🔔 NOTIFICATIONS & AUTOMATION                              ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 26. 📱 Discord Webhooks                                    ║")
    print("║ 27. 🔔 Ntfy (Push notifications)                          ║")
    print("║ 28. ⬡ n8n (Workflow automation)                          ║")
    print("║ 29. ⚡ ActivePieces (FREE automation)                      ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 🤖 CHATBOT BUILDERS                                        ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 30. 🤖 Botpress (Visual chatbot builder)                   ║")
    print("║ 31. 📝 Typebot (Interactive forms)                         ║")
    print("╠═══════════════════════════════════════════════════════════════════╣")
    print("║ 0.  Exit                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print()


def run_setup(module_name: str):
    """Run setup for a specific integration"""
    try:
        module = __import__(f"src.integrations.{module_name}", fromlist=["setup"])
        if hasattr(module, "setup"):
            print("\n" + "="*60)
            module.setup()
        else:
            print(f"❌ No setup function found")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    setups = {
        "1": ("skip", "Configure GROQ_API_KEY in .env manually"),
        "2": ("huggingface_client", "HuggingFace Setup"),
        "3": ("stable_diffusion_client", "Stable Diffusion Setup"),
        "4": ("dify_client", "Dify AI Setup"),
        "5": ("skip", "Configure OLLAMA_URL in .env manually"),
        "6": ("openwa_memory", "OpenWA Setup"),
        "7": ("skip", "Configure TELEGRAM_BOT_TOKEN in .env manually"),
        "8": ("skip", "Configure CHATWOOT_URL in .env manually"),
        "9": ("razorpay_client", "Razorpay Setup"),
        "10": ("medusa_client", "Medusa Setup"),
        "11": ("skip", "Configure SUPABASE_URL in .env manually"),
        "12": ("skip", "Configure REDIS_URL in .env manually"),
        "13": ("mongodb_client", "MongoDB Setup"),
        "14": ("cloudflare_r2_client", "Cloudflare R2 Setup"),
        "15": ("minio_client", "MinIO Setup"),
        "16": ("meilisearch_client", "Meilisearch Setup"),
        "17": ("qdrant_client", "Qdrant Setup"),
        "18": ("notion_client", "Notion Setup"),
        "19": ("linear_client", "Linear Setup"),
        "20": ("cal_client", "Cal.com Setup"),
        "21": ("google_calendar_client", "Google Calendar Setup"),
        "22": ("posthog_client", "Posthog Setup"),
        "23": ("sentry_client", "Sentry Setup"),
        "24": ("plausible_client", "Plausible Setup"),
        "25": ("netdata_client", "Netdata Setup"),
        "26": ("discord_client", "Discord Setup"),
        "27": ("ntfy_client", "Ntfy Setup"),
        "28": ("n8n_client", "n8n Setup"),
        "29": ("activepieces_client", "ActivePieces Setup"),
        "30": ("skip", "Configure BOTPRESS_URL in .env manually"),
        "31": ("skip", "Configure TYPEBOT_URL in .env manually"),
    }
    
    while True:
        show_menu()
        choice = input("Enter your choice (0-31): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye! Your bot is ready to use.")
            print("\nRun with: python main_hub.py")
            break
        
        elif choice in setups:
            module, name = setups[choice]
            if module == "skip":
                print(f"\n⚠️  {name}")
            else:
                print(f"\n🔧 {name}...")
                run_setup(module)
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
