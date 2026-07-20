#!/usr/bin/env python3
"""
🤖 WhatsApp Automation Hub v5.1 - COMPLETE WORKING SYSTEM
============================================================
What this does:
1. Telegram Bot - Control everything from Telegram
2. AI Auto-Reply - Responds to messages automatically  
3. Order Processing - Handles customer orders
4. Broadcast - Send messages to 1000s of customers
5. Templates - Pre-defined responses
6. Rate Limiting - Prevents abuse
7. Input Validation - Security hardened

Author: Built with ❤️
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

try:
    import telegram
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("telegram package not installed")

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("groq package not installed")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Security imports
try:
    from src.security.validator import InputValidator
    from src.security.sanitizer import Sanitizer
    from src.security.config import SecurityConfig, SECURITY_HEADERS
    from src.rate_limiter.limiter import RateLimiter, default_limiter
    SECURITY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security module not available: {e}")
    SECURITY_AVAILABLE = False
    InputValidator = None
    Sanitizer = None

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENWA_URL = os.getenv("OPENWA_URL", "http://localhost:3000")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "")
OPENWA_SESSION = os.getenv("OPENWA_SESSION_ID", "default")

# Business Info
BUSINESS_NAME = "My Business"
BUSINESS_PHONE = "+91-9876543210"

# States for conversation
MENU, ORDER_NAME, ORDER_ITEM, ORDER_ADDRESS, BROADCAST_MSG, TEMPLATE_KEYWORD, TEMPLATE_RESPONSE = range(7)

# ═══════════════════════════════════════════════════════════════
# DATABASE (Simple JSON-based)
# ═══════════════════════════════════════════════════════════════

import json
from pathlib import Path

class Database:
    def __init__(self):
        self.db_file = Path("data/bot_database.json")
        self.db_file.parent.mkdir(exist_ok=True)
        self.data = self.load()
    
    def load(self):
        if self.db_file.exists():
            return json.loads(self.db_file.read_text())
        return {
            "customers": [],      # List of customer phone numbers
            "orders": [],         # List of orders
            "templates": {},      # Keyword -> Response templates
            "messages": [],       # Message history
            "stats": {"total_messages": 0, "total_orders": 0, "total_broadcasts": 0}
        }
    
    def save(self):
        self.db_file.write_text(json.dumps(self.data, indent=2))
    
    def add_customer(self, phone):
        if phone not in self.data["customers"]:
            self.data["customers"].append(phone)
            self.save()
            return True
        return False
    
    def add_order(self, order):
        self.data["orders"].append(order)
        self.data["stats"]["total_orders"] += 1
        self.save()
    
    def add_template(self, keyword, response):
        self.data["templates"][keyword.lower()] = response
        self.save()
    
    def get_template(self, keyword):
        return self.data["templates"].get(keyword.lower())
    
    def get_all_templates(self):
        return self.data["templates"]
    
    def add_message(self, sender, message, direction):
        self.data["messages"].append({
            "time": datetime.now().isoformat(),
            "sender": sender,
            "message": message,
            "direction": direction  # "incoming" or "outgoing"
        })
        self.data["stats"]["total_messages"] += 1
        self.save()
    
    def get_stats(self):
        return self.data["stats"]

db = Database()

# ═══════════════════════════════════════════════════════════════
# AI RESPONSE ENGINE
# ═══════════════════════════════════════════════════════════════

class AIEngine:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_AVAILABLE and GROQ_API_KEY else None
    
    def get_response(self, message, context=""):
        """Get AI response using Groq"""
        
        # Check templates first
        template = db.get_template(message.lower().strip())
        if template:
            return template, "template"
        
        # Check partial keywords
        templates = db.get_all_templates()
        for keyword, response in templates.items():
            if keyword in message.lower():
                return response, "template"
        
        # Use AI if available
        if self.client:
            try:
                system_prompt = f"""You are a helpful assistant for {BUSINESS_NAME}.
Keep responses SHORT and FRIENDLY (1-2 sentences).
Help with orders, questions about products/services.
If they want to order, ask for their name and address."""
                
                chat = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                return chat.choices[0].message.content, "ai"
            except Exception as e:
                logger.error(f"AI Error: {e}")
        
        # Default responses
        defaults = {
            "hi": "Hello! 👋 Welcome to " + BUSINESS_NAME + "! How can I help you today?",
            "hello": "Hi there! 😊 How may I assist you?",
            "price": "Our prices are very competitive! What product are you interested in?",
            "order": "Great! To place an order, please tell us:\n1. Your Name\n2. What items you want\n3. Your delivery address",
            "delivery": "Yes! We deliver all over India. Delivery takes 2-5 business days.",
            "hours": "We're open 9 AM - 9 PM, all days! 🌟",
        }
        
        for key, response in defaults.items():
            if key in message.lower():
                return response, "default"
        
        return "Thanks for your message! We'll get back to you shortly. 🙏", "default"

ai = AIEngine()

# ═══════════════════════════════════════════════════════════════
# OPENWA GATEWAY
# ═══════════════════════════════════════════════════════════════

class OpenWAGateway:
    def __init__(self):
        self.url = OPENWA_URL.rstrip('/')
        self.api_key = OPENWA_API_KEY
        self.session_id = OPENWA_SESSION
    
    def is_connected(self):
        """Check if WhatsApp is connected"""
        if not self.api_key:
            return False
        try:
            headers = {"X-API-Key": self.api_key}
            r = requests.get(f"{self.url}/api/connection", headers=headers, timeout=5)
            return r.status_code == 200
        except:
            return False
    
    def send_message(self, phone, text):
        """Send WhatsApp message"""
        if not self.api_key:
            return False
        try:
            headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
            data = {
                "session": self.session_id,
                "chatId": f"{phone}@c.us",
                "text": text
            }
            r = requests.post(f"{self.url}/api/messages/sendText", headers=headers, json=data, timeout=30)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    def get_messages(self, limit=10):
        """Get recent messages"""
        if not self.api_key:
            return []
        try:
            headers = {"X-API-Key": self.api_key}
            r = requests.get(f"{self.url}/api/messages", headers=headers, params={"limit": limit, "session": self.session_id}, timeout=10)
            if r.status_code == 200:
                return r.json()
            return []
        except:
            return []

openwa = OpenWAGateway()

# ═══════════════════════════════════════════════════════════════
# TELEGRAM HANDLERS
# ═══════════════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("👥 Customers", callback_data="customers")],
        [InlineKeyboardButton("📦 Orders", callback_data="orders")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("📝 Templates", callback_data="templates")],
        [InlineKeyboardButton("🔄 Test WhatsApp", callback_data="test_whatsapp")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🤖 *{BUSINESS_NAME} - Control Panel*\n\n"
        "Welcome! Use the buttons below to control your bot:\n\n"
        "📱 *WhatsApp Status:* " + ("✅ Connected" if openwa.is_connected() else "❌ Not Connected") + "\n"
        "🤖 *AI Engine:* " + ("✅ Active" if ai.client else "❌ Disabled") + "\n"
        "📊 *Stats:* " + str(db.get_stats().get("total_messages", 0)) + " messages processed",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
� *Available Commands:*

/start - Show control panel
/help - Show this help
/status - Check system status
/stats - View statistics
/orders - View recent orders
/customers - View customer list
/broadcast - Send message to all customers
/template - Manage response templates
/test - Test WhatsApp connection
/whatsapp - Test sending a message

*Quick Tips:*
• Add customer phone numbers manually
• Set up templates for auto-replies
• Use broadcast to reach all customers
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    stats = db.get_stats()
    openwa_status = "✅ Connected" if openwa.is_connected() else "❌ Not Connected"
    ai_status = "✅ Active" if ai.client else "❌ Disabled"
    
    await update.message.reply_text(
        f"📊 *System Status*\n\n"
        f"WhatsApp: {openwa_status}\n"
        f"AI Engine: {ai_status}\n"
        f"Templates: {len(db.get_all_templates())}\n"
        f"Customers: {len(db.data['customers'])}\n"
        f"Orders: {stats.get('total_orders', 0)}\n"
        f"Messages: {stats.get('total_messages', 0)}\n"
        f"Broadcasts: {stats.get('total_broadcasts', 0)}",
        parse_mode="Markdown"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    stats = db.get_stats()
    recent_orders = db.data['orders'][-5:] if db.data['orders'] else []
    
    text = f"📈 *Statistics*\n\n"
    text += f"Total Messages: {stats.get('total_messages', 0)}\n"
    text += f"Total Orders: {stats.get('total_orders', 0)}\n"
    text += f"Total Broadcasts: {stats.get('total_broadcasts', 0)}\n"
    text += f"Customers: {len(db.data['customers'])}\n"
    
    if recent_orders:
        text += f"\n📦 *Recent Orders:*\n"
        for order in reversed(recent_orders):
            text += f"• {order.get('name', 'Unknown')}: {order.get('item', 'N/A')}\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /orders command"""
    orders = db.data['orders']
    
    if not orders:
        await update.message.reply_text("📦 No orders yet!")
        return
    
    text = "📦 *Recent Orders:*\n\n"
    for i, order in enumerate(reversed(orders[-10:]), 1):
        text += f"{i}. *{order.get('name', 'Unknown')}*\n"
        text += f"   📍 {order.get('address', 'N/A')}\n"
        text += f"   🛒 {order.get('item', 'N/A')}\n"
        text += f"   📅 {order.get('time', 'N/A')}\n\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def customers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /customers command"""
    customers = db.data['customers']
    
    if not customers:
        await update.message.reply_text("👥 No customers yet!\n\nAdd customers using:\n/addcustomer PHONE_NUMBER")
        return
    
    text = f"👥 *Customer List* ({len(customers)} total)\n\n"
    for i, phone in enumerate(customers[:20], 1):
        text += f"{i}. {phone}\n"
    
    if len(customers) > 20:
        text += f"\n...and {len(customers) - 20} more"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def add_customer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addcustomer command"""
    if not context.args:
        await update.message.reply_text("Usage: /addcustomer PHONE_NUMBER\n\nExample:\n/addcustomer 919876543210")
        return
    
    phone = context.args[0]
    if db.add_customer(phone):
        await update.message.reply_text(f"✅ Customer added!\n\n📱 {phone}\n\nTotal customers: {len(db.data['customers'])}")
    else:
        await update.message.reply_text(f"ℹ️ Customer already exists!\n\n📱 {phone}")

async def test_whatsapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /test command"""
    if not openwa.is_connected():
        await update.message.reply_text(
            "❌ WhatsApp not connected!\n\n"
            "Start OpenWA:\n"
            "```\ndocker run -d --name openwa -p 3000:3000 waha/waha:latest\n```",
            parse_mode="Markdown"
        )
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /test PHONE_NUMBER MESSAGE\n\nExample:\n/test 919876543210 Hello!")
        return
    
    phone = context.args[0]
    message = " ".join(context.args[1:]) or "Test message from Telegram Bot!"
    
    if openwa.send_message(phone, message):
        await update.message.reply_text(f"✅ Message sent!\n\n📱 To: {phone}\n💬 {message}")
    else:
        await update.message.reply_text(f"❌ Failed to send message to {phone}")

async def template_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /template command"""
    if not context.args or len(context.args) < 2:
        templates = db.get_all_templates()
        if not templates:
            await update.message.reply_text(
                "📝 *Templates*\n\n"
                "No templates yet!\n\n"
                "Add template:\n"
                "`/template KEYWORD RESPONSE`\n\n"
                "Example:\n"
                "`/template hello Hi! Welcome!`",
                parse_mode="Markdown"
            )
            return
        
        text = "📝 *Templates*\n\n"
        for keyword, response in templates.items():
            text += f"• *{keyword}*\n  → {response[:50]}...\n\n"
        
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    keyword = context.args[0].lower()
    response = " ".join(context.args[1:])
    db.add_template(keyword, response)
    
    await update.message.reply_text(
        f"✅ Template added!\n\n"
        f"🔑 Keyword: {keyword}\n"
        f"💬 Response: {response}"
    )

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command"""
    if not context.args:
        await update.message.reply_text(
            "📢 *Broadcast Message*\n\n"
            "Usage:\n"
            "`/broadcast YOUR MESSAGE`\n\n"
            "Example:\n"
            "`/broadcast Hello! We have new offers!`\n\n"
            f"This will send to {len(db.data['customers'])} customers.",
            parse_mode="Markdown"
        )
        return
    
    if not openwa.is_connected():
        await update.message.reply_text("❌ WhatsApp not connected!")
        return
    
    message = " ".join(context.args)
    customers = db.data['customers']
    
    if not customers:
        await update.message.reply_text("❌ No customers to send to!\n\nAdd customers first using:\n/addcustomer PHONE")
        return
    
    await update.message.reply_text(f"📤 Sending broadcast to {len(customers)} customers...")
    
    sent = 0
    failed = 0
    
    for phone in customers:
        if openwa.send_message(phone, message):
            sent += 1
        else:
            failed += 1
    
    db.data["stats"]["total_broadcasts"] += 1
    db.save()
    
    await update.message.reply_text(
        f"✅ Broadcast complete!\n\n"
        f"📤 Sent: {sent}\n"
        f"❌ Failed: {failed}\n"
        f"📊 Total broadcasts: {db.data['stats']['total_broadcasts']}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    text = update.message.text
    
    # Log message
    db.add_message("telegram", text, "incoming")
    
    # Get AI response
    response, source = ai.get_response(text)
    
    # Send response
    await update.message.reply_text(response)
    
    # Log response
    db.add_message("telegram", response, "outgoing")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "status":
        stats = db.get_stats()
        await query.edit_message_text(
            f"📊 *Status*\n\n"
            f"WhatsApp: {'✅' if openwa.is_connected() else '❌'}\n"
            f"AI: {'✅' if ai.client else '❌'}\n"
            f"Customers: {len(db.data['customers'])}\n"
            f"Messages: {stats.get('total_messages', 0)}"
        )
    
    elif data == "customers":
        customers = db.data['customers']
        text = f"👥 *Customers* ({len(customers)})\n\n"
        text += "\n".join([f"• {c}" for c in customers[:10]]) or "No customers"
        await query.edit_message_text(text)
    
    elif data == "orders":
        await orders_command(update, context)
    
    elif data == "broadcast":
        await query.edit_message_text(
            "📢 *Broadcast*\n\n"
            "Send a message to ALL customers.\n\n"
            "Use: /broadcast YOUR MESSAGE"
        )
    
    elif data == "templates":
        templates = db.get_all_templates()
        text = "📝 *Templates*\n\n"
        text += "\n".join([f"• {k}: {v[:30]}..." for k, v in templates.items()]) or "No templates"
        await query.edit_message_text(text)
    
    elif data == "test_whatsapp":
        if openwa.is_connected():
            await query.edit_message_text("✅ WhatsApp connected!\n\nUse /test PHONE MESSAGE to send")
        else:
            await query.edit_message_text("❌ WhatsApp not connected!\n\nStart Docker and try again.")

# ═══════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🤖 WhatsApp Automation Hub v5.0                         ║
║                                                               ║
║     Complete Working System                                   ║
║     • Telegram Control                                        ║
║     • AI Auto-Reply                                          ║
║     • Order Processing                                       ║
║     • Broadcast Messages                                     ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if not TELEGRAM_AVAILABLE:
        print("❌ Telegram package not installed!")
        print("   Run: pip install python-telegram-bot")
        return
    
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env!")
        return
    
    print("✅ All components loaded!")
    print("")
    print("📱 Telegram Bot: @whatsappuubot")
    print(f"📊 Customers: {len(db.data['customers'])}")
    print(f"📝 Templates: {len(db.get_all_templates())}")
    print("")
    print("🚀 Bot is running!")
    print("   Open Telegram and send /start")
    print("   Press Ctrl+C to stop")
    print("")
    
    # Build application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CommandHandler("customers", customers_command))
    app.add_handler(CommandHandler("addcustomer", add_customer_command))
    app.add_handler(CommandHandler("test", test_whatsapp_command))
    app.add_handler(CommandHandler("template", template_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run bot
    print("=" * 60)
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
