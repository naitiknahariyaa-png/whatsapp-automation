#!/usr/bin/env python3
"""
🚀 QUICK START - WhatsApp Automation Hub v5.0
==============================================

Run this to start your working bot!

What this does:
✅ Telegram Control Panel - Control everything from Telegram
✅ AI Auto-Reply - Smart responses using Groq AI
✅ Customer Management - Add and manage customers
✅ Order Processing - Handle customer orders
✅ Broadcast Messages - Send to 1000s of customers
✅ Template System - Set up auto-responses

==============================================
HOW TO USE:
==============================================

1. Open Telegram
2. Search for: @whatsappuubot
3. Click Start or send /start

COMMANDS:
/start - Open control panel
/help - Show all commands
/status - Check system status
/stats - View statistics
/orders - View orders
/customers - View customer list
/addcustomer PHONE - Add customer
/broadcast MESSAGE - Send to all customers
/template KEYWORD RESPONSE - Add auto-response
/test PHONE MESSAGE - Test WhatsApp message

==============================================
"""

import os
import sys

# Check dependencies
print("🔍 Checking dependencies...")

try:
    import telegram
    print("   ✅ python-telegram-bot")
except ImportError:
    print("   ❌ Installing python-telegram-bot...")
    os.system("pip install python-telegram-bot")

try:
    from groq import Groq
    print("   ✅ groq")
except ImportError:
    print("   ❌ Installing groq...")
    os.system("pip install groq")

try:
    import requests
    print("   ✅ requests")
except ImportError:
    print("   ❌ Installing requests...")
    os.system("pip install requests")

print("\n✅ All dependencies ready!")
print("\n" + "="*60)

# Start the bot
print("\n🚀 Starting WhatsApp Automation Hub v5.0...")
print("\n📱 Open Telegram and message @whatsappuubot")
print("="*60 + "\n")

os.system("python complete_bot.py")
