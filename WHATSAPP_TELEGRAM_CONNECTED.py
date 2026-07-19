#!/usr/bin/env python3
"""
🤖 WhatsApp ↔ Telegram Connected Bot v5.0
===========================================
This bot connects WhatsApp to Telegram

Flow:
WhatsApp Message → Bot → AI → Reply to WhatsApp
                    ↓
              Telegram Admin Alert

Admin can send commands via Telegram to:
- View messages
- Send broadcasts
- Manage customers
- Test WhatsApp
"""

import os
import time
import json
import logging
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_telegram.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.error("pip install python-telegram-bot")

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.error("pip install groq")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENWA_URL = os.getenv("OPENWA_URL", "http://localhost:3000")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "")
OPENWA_SESSION = os.getenv("OPENWA_SESSION_ID", "default")

# Admin Telegram ID (get from @userinfobot)
ADMIN_TELEGRAM_ID = ""  # Optional - set your Telegram ID to receive alerts

BUSINESS_NAME = "My Business"

# ═══════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════

import json
from pathlib import Path

class Database:
    def __init__(self):
        self.db_file = Path("data/connected_bot_db.json")
        self.db_file.parent.mkdir(exist_ok=True)
        self.data = self.load()
    
    def load(self):
        if self.db_file.exists():
            return json.loads(self.db_file.read_text())
        return {
            "customers": [],
            "orders": [],
            "templates": {
                "hello": "Hello! 👋 Welcome to " + BUSINESS_NAME + "! How can I help you?",
                "hi": "Hi there! 😊 How may I assist you today?",
                "price": "Our prices are very competitive! What product interests you?",
                "order": "Great! Please tell me:\n1. Your Name\n2. What items you want\n3. Delivery address",
                "delivery": "Yes! We deliver all over India! 🚚 2-5 business days.",
                "hours": "We're open 9 AM - 9 PM, all days! 🌟",
                "thanks": "You're welcome! 😊 Happy to help!",
                "bye": "Goodbye! Have a great day! 👋",
            },
            "messages": [],
            "stats": {"total_whatsapp": 0, "total_orders": 0, "broadcasts": 0}
        }
    
    def save(self):
        self.db_file.write_text(json.dumps(self.data, indent=2))
    
    def add_customer(self, phone):
        phone = str(phone).replace("@c.us", "").replace("+", "")
        if phone not in self.data["customers"]:
            self.data["customers"].append(phone)
            self.save()
            return True
        return False
    
    def add_message(self, sender, message, direction, platform="whatsapp"):
        self.data["messages"].append({
            "time": datetime.now().isoformat(),
            "sender": sender,
            "message": message[:500],
            "direction": direction,
            "platform": platform
        })
        self.data["stats"]["total_whatsapp"] += 1
        self.save()
    
    def add_order(self, order):
        self.data["orders"].append(order)
        self.data["stats"]["total_orders"] += 1
        self.save()
    
    def add_template(self, keyword, response):
        self.data["templates"][keyword.lower()] = response
        self.save()
    
    def get_template_response(self, message):
        msg_lower = message.lower().strip()
        for keyword, response in self.data["templates"].items():
            if keyword in msg_lower:
                return response, "template"
        return None, None
    
    def get_all_templates(self):
        return self.data["templates"]
    
    def get_stats(self):
        return self.data["stats"]

db = Database()

# ═══════════════════════════════════════════════════════════════
# AI ENGINE
# ═══════════════════════════════════════════════════════════════

class AIEngine:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_AVAILABLE and GROQ_API_KEY else None
    
    def get_response(self, message):
        # Check templates first
        response, source = db.get_template_response(message)
        if response:
            return response, source
        
        # Use AI
        if self.client:
            try:
                system_prompt = f"""You are a helpful assistant for {BUSINESS_NAME}.
Keep responses SHORT (1-2 sentences).
Be friendly and professional.
Help with orders, questions, and inquiries."""
                
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
        
        return "Thanks for your message! We'll get back to you soon. 🙏", "default"

ai = AIEngine()

# ═══════════════════════════════════════════════════════════════
# WHATSAPP GATEWAY
# ═══════════════════════════════════════════════════════════════

class WhatsAppGateway:
    def __init__(self):
        self.url = OPENWA_URL.rstrip('/')
        self.api_key = OPENWA_API_KEY
        self.session = OPENWA_SESSION
    
    def is_connected(self):
        if not self.api_key:
            return False
        try:
            headers = {"X-API-Key": self.api_key}
            r = requests.get(f"{self.url}/api/connection", headers=headers, timeout=5)
            return r.status_code == 200
        except:
            return False
    
    def send_message(self, phone, text):
        if not self.api_key:
            return False
        try:
            headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
            data = {
                "session": self.session,
                "chatId": f"{phone}@c.us",
                "text": text
            }
            r = requests.post(f"{self.url}/api/messages/sendText", headers=headers, json=data, timeout=30)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
            return False
    
    def get_new_messages(self):
        if not self.api_key:
            return []
        try:
            headers = {"X-API-Key": self.api_key}
            r = requests.get(
                f"{self.url}/api/messages",
                headers=headers,
                params={"limit": 20, "session": self.session},
                timeout=10
            )
            if r.status_code == 200:
                return r.json()
            return []
        except:
            return []

wa = WhatsAppGateway()

# ═══════════════════════════════════════════════════════════════
# TELEGRAM HANDLERS
# ═══════════════════════════════════════════════════════════════

# Global for sending WhatsApp messages from Telegram
whatsapp_to_telegram_queue = []
telegram_app = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("📦 Orders", callback_data="orders")],
        [InlineKeyboardButton("👥 Customers", callback_data="customers")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("🧪 Test WhatsApp", callback_data="test_wa")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status = "✅ Connected" if wa.is_connected() else "❌ Not Connected"
    
    await update.message.reply_text(
        f"🤖 *{BUSINESS_NAME} - Control Panel*\n\n"
        f"WhatsApp: {status}\n"
        f"AI: {'✅ Active' if ai.client else '❌ Disabled'}\n\n"
        "Use buttons below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🆘 *Commands:*

/start - Control panel
/status - System status
/stats - Statistics
/orders - View orders
/customers - View customers
/addcustomer PHONE - Add customer
/broadcast MESSAGE - Send to all
/template KEY RESPONSE - Add auto-reply
/whois 919876543210 - Check customer
/testwa PHONE MSG - Test WhatsApp
/whatsapp - WhatsApp status
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = db.get_stats()
    connected = "✅ Connected" if wa.is_connected() else "❌ Not Connected"
    
    text = f"""
📊 *Status*

WhatsApp: {connected}
AI: {'✅ Active' if ai.client else '❌ Disabled'}
Templates: {len(db.get_all_templates())}
Customers: {len(db.data['customers'])}
WhatsApp Msgs: {stats.get('total_whatsapp', 0)}
Orders: {stats.get('total_orders', 0)}
Broadcasts: {stats.get('broadcasts', 0)}
    """
    await update.message.reply_text(text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = db.get_stats()
    recent_msgs = db.data['messages'][-5:]
    
    text = f"📈 *Statistics*\n\n"
    text += f"WhatsApp Messages: {stats.get('total_whatsapp', 0)}\n"
    text += f"Orders: {stats.get('total_orders', 0)}\n"
    text += f"Broadcasts Sent: {stats.get('broadcasts', 0)}\n"
    text += f"Customers: {len(db.data['customers'])}\n"
    
    if recent_msgs:
        text += f"\n📱 *Recent Messages:*\n"
        for msg in reversed(recent_msgs):
            arrow = "→" if msg['direction'] == 'outgoing' else "←"
            text += f"{arrow} {msg.get('sender', '?')[:15]}: {msg.get('message', '')[:30]}...\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = db.data['orders']
    
    if not orders:
        await update.message.reply_text("📦 No orders yet!")
        return
    
    text = "📦 *Recent Orders:*\n\n"
    for i, order in enumerate(reversed(orders[-10:]), 1):
        text += f"{i}. *{order.get('name', 'Unknown')}*\n"
        text += f"   📍 {order.get('address', 'N/A')}\n"
        text += f"   🛒 {order.get('item', 'N/A')}\n\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def customers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    customers = db.data['customers']
    
    if not customers:
        await update.message.reply_text("👥 No customers!\n\n/addcustomer PHONE")
        return
    
    text = f"👥 *Customers* ({len(customers)})\n\n"
    for i, phone in enumerate(customers[:20], 1):
        text += f"{i}. `{phone}`\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def addcustomer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /addcustomer PHONE\n\n/addcustomer 919876543210")
        return
    
    phone = context.args[0].replace("+", "")
    if db.add_customer(phone):
        await update.message.reply_text(f"✅ Added!\n\n📱 {phone}\nTotal: {len(db.data['customers'])}")
    else:
        await update.message.reply_text(f"ℹ️ Already exists!\n\n📱 {phone}")

async def template_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        templates = db.get_all_templates()
        text = "📝 *Templates*\n\n"
        for k, v in templates.items():
            text += f"• `{k}` → {v[:40]}...\n"
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    keyword = context.args[0].lower()
    response = " ".join(context.args[1:])
    db.add_template(keyword, response)
    await update.message.reply_text(f"✅ Template added!\n\n🔑 {keyword}\n💬 {response}")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(f"📢 Broadcast\n\nUsage:\n/broadcast YOUR MESSAGE\n\nWill send to {len(db.data['customers'])} customers.")
        return
    
    if not wa.is_connected():
        await update.message.reply_text("❌ WhatsApp not connected!")
        return
    
    message = " ".join(context.args)
    customers = db.data['customers']
    
    if not customers:
        await update.message.reply_text("❌ No customers! Add customers first.")
        return
    
    await update.message.reply_text(f"📤 Sending to {len(customers)} customers...")
    
    sent = failed = 0
    for phone in customers:
        if wa.send_message(phone, message):
            sent += 1
        else:
            failed += 1
    
    db.data["stats"]["broadcasts"] += 1
    db.save()
    
    await update.message.reply_text(f"✅ Done!\n\n📤 Sent: {sent}\n❌ Failed: {failed}")

async def whois_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /whois PHONE")
        return
    
    phone = context.args[0].replace("+", "")
    is_customer = phone in db.data['customers']
    
    # Find messages from this number
    msgs = [m for m in db.data['messages'] if phone in str(m.get('sender', ''))]
    
    text = f"🔍 *Info for {phone}*\n\n"
    text += f"Customer: {'✅ Yes' if is_customer else '❌ No'}\n"
    text += f"Messages: {len(msgs)}\n"
    
    if msgs:
        text += f"\nRecent:\n"
        for msg in reversed(msgs[-3:]):
            text += f"• {msg['direction']}: {msg['message'][:50]}...\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def testwa_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage:\n/testwa PHONE MESSAGE\n\n/testwa 919876543210 Hello!")
        return
    
    phone = context.args[0].replace("+", "")
    message = " ".join(context.args[1:])
    
    if not wa.is_connected():
        await update.message.reply_text("❌ WhatsApp not connected!")
        return
    
    if wa.send_message(phone, message):
        await update.message.reply_text(f"✅ Sent!\n\n📱 To: {phone}\n💬 {message}")
    else:
        await update.message.reply_text(f"❌ Failed to send to {phone}")

async def whatsapp_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if wa.is_connected():
        await update.message.reply_text("✅ WhatsApp is connected and ready!")
    else:
        await update.message.reply_text(
            "❌ WhatsApp not connected!\n\n"
            "Start OpenWA:\n"
            "```\ndocker run -d --name openwa -p 3000:3000 waha/waha:latest\n```"
            "\nThen scan QR code at http://localhost:3000",
            parse_mode="Markdown"
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "status":
        await status_command(update, context)
    elif data == "orders":
        await orders_command(update, context)
    elif data == "customers":
        await customers_command(update, context)
    elif data == "broadcast":
        await query.edit_message_text(
            f"📢 *Broadcast*\n\n"
            f"Send a message to ALL {len(db.data['customers'])} customers.\n\n"
            "Use: /broadcast YOUR MESSAGE"
        )
    elif data == "test_wa":
        await query.edit_message_text(
            "🧪 *Test WhatsApp*\n\n"
            "Usage:\n"
            "```\n/testwa PHONE MESSAGE\n```\n\n"
            "Example:\n"
            "```\n/testwa 919876543210 Hello!\n```"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Process command
    response, source = ai.get_response(text)
    await update.message.reply_text(response)

# ═══════════════════════════════════════════════════════════════
# WHATSAPP MONITOR (Background Thread)
# ═══════════════════════════════════════════════════════════════

class WhatsAppMonitor:
    def __init__(self):
        self.running = False
        self.last_message_id = None
        self.admin_chat_id = None
    
    def set_admin(self, chat_id):
        self.admin_chat_id = chat_id
    
    def start(self):
        self.running = True
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()
        logger.info("WhatsApp monitor started")
    
    def stop(self):
        self.running = False
    
    def _monitor_loop(self):
        while self.running:
            try:
                messages = wa.get_new_messages()
                
                for msg in messages:
                    msg_id = msg.get("id", "")
                    
                    if msg_id == self.last_message_id:
                        continue
                    self.last_message_id = msg_id
                    
                    # Skip outgoing
                    if msg.get("fromMe"):
                        continue
                    
                    # Get message details
                    text = msg.get("body", "")
                    chat = msg.get("chat", {})
                    sender = str(chat.get("id", {}).get("remote", "")).replace("@c.us", "")
                    
                    if not text or not sender:
                        continue
                    
                    # Log message
                    db.add_message(sender, text, "incoming")
                    
                    # Add customer
                    db.add_customer(sender)
                    
                    # Get AI response
                    response, source = ai.get_response(text)
                    
                    # Send reply to WhatsApp
                    wa.send_message(sender, response)
                    
                    # Log outgoing
                    db.add_message(sender, response, "outgoing")
                    
                    # Alert admin on Telegram
                    if self.admin_chat_id and telegram_app:
                        try:
                            import asyncio
                            async def send_alert():
                                text = f"📱 *New WhatsApp Message*\n\n👤 From: `{sender}`\n💬 {text}\n\n🤖 Auto-replied: {response[:100]}..."
                                await telegram_app.bot.send_message(
                                    chat_id=self.admin_chat_id,
                                    text=text,
                                    parse_mode="Markdown"
                                )
                            asyncio.run(send_alert())
                        except:
                            pass
                    
                    logger.info(f"WhatsApp: {sender} -> {text[:30]}...")
            
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            
            time.sleep(3)
    
    def send_to_admin(self, message):
        """Send message to Telegram admin"""
        if self.admin_chat_id and telegram_app:
            try:
                import asyncio
                async def send():
                    await telegram_app.bot.send_message(
                        chat_id=self.admin_chat_id,
                        text=message,
                        parse_mode="Markdown"
                    )
                asyncio.run(send())
            except:
                pass

monitor = WhatsAppMonitor()

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    global telegram_app
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🤖 WhatsApp ↔ Telegram Connected Bot                     ║
║                                                               ║
║     🔗 WhatsApp + Telegram = Complete System                 ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if not TELEGRAM_AVAILABLE:
        print("❌ Install: pip install python-telegram-bot")
        return
    
    if not TELEGRAM_TOKEN:
        print("❌ Set TELEGRAM_BOT_TOKEN in .env")
        return
    
    print("✅ Components loaded!")
    print(f"📱 WhatsApp: {'✅ Connected' if wa.is_connected() else '❌ Not Connected'}")
    print(f"🤖 AI: {'✅ Active' if ai.client else '❌ Disabled'}")
    print(f"👥 Customers: {len(db.data['customers'])}")
    print(f"📝 Templates: {len(db.get_all_templates())}")
    print("")
    
    # Start WhatsApp monitor if connected
    if wa.is_connected():
        monitor.start()
        print("🔄 WhatsApp monitor running...")
    
    print("🚀 Bot is running!")
    print("📱 Telegram: @whatsappuubot")
    print("=" * 60)
    
    # Build app
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    telegram_app = app
    
    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CommandHandler("customers", customers_command))
    app.add_handler(CommandHandler("addcustomer", addcustomer_command))
    app.add_handler(CommandHandler("template", template_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("whois", whois_command))
    app.add_handler(CommandHandler("testwa", testwa_command))
    app.add_handler(CommandHandler("whatsapp", whatsapp_status_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
