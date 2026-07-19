"""
v4.0 - Fully Customizable Telegram Bot
=====================================
EASY TO MODIFY - Just change the text below!

Features:
- 🤖 AI Chat with Groq/Gemini
- 💬 Auto-reply to messages
- 📊 Statistics & Analytics
- 👥 User Management
- 🔔 Admin Controls
- ⚙️ Easy to customize

MODIFY THESE:
- BOT_NAME, BOT_TAGLINE
- COMMANDS_LIST
- WELCOME_MESSAGE
- HELP_MESSAGE
- CUSTOM_COMMANDS
"""

import os
import logging
import asyncio
from typing import Optional, Dict, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import telegram
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, MessageHandler, 
        CallbackQueryHandler, ContextTypes, filters
    )
except ImportError:
    logger.error("Install: pip install python-telegram-bot")

# ═══════════════════════════════════════════════════════════════
# 🎯 CUSTOMIZE YOUR BOT HERE - CHANGE THESE VALUES!
# ═══════════════════════════════════════════════════════════════

# Bot Identity
BOT_NAME = "🚀 My WhatsApp Bot"
BOT_VERSION = "4.0"
BOT_TAGLINE = "Your Business Assistant"

# Bot Owner (shown in about)
BOT_OWNER = "Your Name"
BOT_CONTACT = "@your_username"

# Welcome Message (when /start is sent)
WELCOME_MESSAGE = """
👋 *Welcome to {bot_name}!*

_{bot_tagline}_

I can help you with:
• 💬 Chat with AI
• 📊 View statistics  
• 📋 Manage your business
• 🔔 Get notifications

*Available Commands:*
/help - See all commands
/ai <message> - Chat with AI
/stats - View statistics
/menu - Open menu

_Start chatting or tap a button below!_
""".strip()

# Help Message
HELP_MESSAGE = """
📖 *Help & Commands*

*User Commands:*
/start - Start the bot
/help - Show this help
/menu - Open menu
/ai <message> - Chat with AI
/stats - View statistics
/profile - Your profile

*Quick Actions:*
/order - Place an order
/price - View prices
/contact - Contact us
/about - About the bot

*Admin Commands:*
/broadcast <msg> - Send to all
/users - List users
/panel - Admin panel

_Version: {version}_
""".strip()

# About Message
ABOUT_MESSAGE = """
🤖 *About {bot_name}*

_{bot_tagline}_

Version: {version}

Built with ❤️ for Indian businesses

Features:
• AI-powered responses
• WhatsApp integration
• Payment gateway ready
• 100% FREE to use

Made by: {owner}
Contact: {contact}
""".strip()

# ═══════════════════════════════════════════════════════════════
# ⚙️ CONFIGURATION - Don't change unless you know what you're doing!
# ═══════════════════════════════════════════════════════════════

class Config:
    """Bot Settings"""
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_ADMIN_IDS = os.getenv("TELEGRAM_ADMIN_IDS", "").split(",")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    OPENWA_URL = os.getenv("OPENWA_URL", "http://localhost:2785")
    OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "")
    ENABLE_AI = True

# ═══════════════════════════════════════════════════════════════
# 🧠 AI MANAGER - Handles AI responses
# ═══════════════════════════════════════════════════════════════

class AIManager:
    """Multi-Provider AI"""
    
    def __init__(self):
        self.providers = {}
        self._init_providers()
    
    def _init_providers(self):
        if Config.GROQ_API_KEY:
            self.providers["groq"] = "Groq ⚡"
        if Config.GOOGLE_API_KEY:
            self.providers["gemini"] = "Gemini ✨"
    
    def get_response(self, message: str) -> str:
        # Try Groq first (fastest)
        if "groq" in self.providers:
            try:
                return self._call_groq(message)
            except Exception as e:
                logger.error(f"Groq error: {e}")
        
        # Try Gemini
        if "gemini" in self.providers:
            try:
                return self._call_gemini(message)
            except Exception as e:
                logger.error(f"Gemini error: {e}")
        
        return "AI not configured! Set GROQ_API_KEY in .env"
    
    def _call_groq(self, message: str) -> str:
        import requests
        headers = {"Authorization": f"Bearer {Config.GROQ_API_KEY}"}
        data = {"model": "llama-3.3-70b-versatile", 
                "messages": [{"role": "user", "content": message}]}
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=data, timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        raise Exception(f"Groq error: {response.status_code}")
    
    def _call_gemini(self, message: str) -> str:
        import requests
        data = {"contents": [{"parts": [{"text": message}]}]}
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={Config.GOOGLE_API_KEY}",
            json=data, timeout=30
        )
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        raise Exception(f"Gemini error: {response.status_code}")

# ═══════════════════════════════════════════════════════════════
# 👥 USER MANAGER
# ═══════════════════════════════════════════════════════════════

class UserManager:
    """Track users and their activity"""
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}
    
    def add_user(self, user_id: str, username: str = "", first_name: str = ""):
        if user_id not in self.users:
            self.users[user_id] = {
                "id": user_id,
                "username": username,
                "first_name": first_name,
                "created_at": datetime.now().isoformat(),
                "messages_count": 0,
                "commands_count": 0,
                "is_admin": user_id in Config.TELEGRAM_ADMIN_IDS
            }
    
    def get_user(self, user_id: str) -> Dict:
        if user_id not in self.users:
            self.add_user(user_id)
        return self.users[user_id]
    
    def increment(self, user_id: str, key: str):
        user = self.get_user(user_id)
        user[key] = user.get(key, 0) + 1

# ═══════════════════════════════════════════════════════════════
# 📊 ANALYTICS
# ═══════════════════════════════════════════════════════════════

class Analytics:
    """Track bot statistics"""
    
    def __init__(self):
        self.stats = {
            "total_messages": 0,
            "total_commands": 0,
            "total_ai_calls": 0,
            "start_time": datetime.now()
        }
    
    def increment(self, key: str):
        self.stats[key] = self.stats.get(key, 0) + 1
    
    def get_report(self) -> str:
        uptime = datetime.now() - self.stats["start_time"]
        return f"""
📊 *Statistics*

💬 Messages: {self.stats['total_messages']}
⚡ Commands: {self.stats['total_commands']}
🤖 AI Calls: {self.stats['total_ai_calls']}
👥 Users: {len(user_manager.users)}
⏱️ Uptime: {uptime.days}d {uptime.seconds//3600}h
""".strip()

# Global instances
ai_manager = AIManager()
user_manager = UserManager()
analytics = Analytics()

# ═══════════════════════════════════════════════════════════════
# 🎛️ MENU KEYBOARDS
# ═══════════════════════════════════════════════════════════════

def main_menu_keyboard():
    """Main menu buttons"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Chat AI", callback_data="menu_ai")],
        [InlineKeyboardButton("📊 Statistics", callback_data="menu_stats")],
        [InlineKeyboardButton("👤 My Profile", callback_data="menu_profile")],
        [InlineKeyboardButton("📋 Orders", callback_data="menu_orders")],
        [InlineKeyboardButton("💰 Prices", callback_data="menu_prices")],
        [InlineKeyboardButton("📞 Contact", callback_data="menu_contact")],
    ])

def admin_menu_keyboard():
    """Admin menu buttons"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")],
    ])

def back_keyboard():
    """Back button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]
    ])

# ═══════════════════════════════════════════════════════════════
# 📱 COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_manager.add_user(str(user.id), user.username or "", user.first_name or "")
    
    message = WELCOME_MESSAGE.format(
        bot_name=BOT_NAME,
        bot_tagline=BOT_TAGLINE
    )
    
    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = update.effective_user
    user_manager.increment(str(user.id), "commands_count")
    analytics.increment("total_commands")
    
    message = HELP_MESSAGE.format(version=BOT_VERSION)
    
    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=back_keyboard()
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /menu command"""
    await update.message.reply_text(
        "📋 *Main Menu*\n\nChoose an option:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    message = ABOUT_MESSAGE.format(
        bot_name=BOT_NAME,
        bot_tagline=BOT_TAGLINE,
        version=BOT_VERSION,
        owner=BOT_OWNER,
        contact=BOT_CONTACT
    )
    
    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=back_keyboard()
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    await update.message.reply_text(
        analytics.get_report(),
        parse_mode="Markdown"
    )

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /profile command"""
    user_id = str(update.effective_user.id)
    user = user_manager.get_user(user_id)
    
    message = f"""
👤 *Your Profile*

Name: {user.get('first_name', 'Unknown')}
Username: @{user.get('username', 'N/A')}
Messages: {user.get('messages_count', 0)}
Commands: {user.get('commands_count', 0)}
Status: {'👑 Admin' if user.get('is_admin') else '👤 User'}
""".strip()
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ai command"""
    user_id = str(update.effective_user.id)
    user_manager.increment(user_id, "messages_count")
    analytics.increment("total_commands")
    
    if not context.args:
        await update.message.reply_text(
            "🤖 *AI Chat*\n\nUsage: /ai <your message>\n\nExample:\n`/ai What is WhatsApp?`",
            parse_mode="Markdown"
        )
        return
    
    user_message = " ".join(context.args)
    await update.message.chat.send_action("typing")
    
    response = ai_manager.get_response(user_message)
    analytics.increment("total_ai_calls")
    
    await update.message.reply_text(f"🤖 *AI Response:*\n\n{response}", parse_mode="Markdown")

async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /order command"""
    message = """
📦 *Place Order*

To place an order, just send:
• Product name
• Quantity
• Your address

We'll respond with price and delivery info!

Example:
"I want 2 kg rice, deliver to Mumbai"
"""
    await update.message.reply_text(message, parse_mode="Markdown")

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command"""
    message = """
💰 *Price List*

| Product | Price |
|---------|-------|
| Item 1 | ₹100 |
| Item 2 | ₹200 |
| Item 3 | ₹300 |

_Contact us for bulk orders!_
"""
    await update.message.reply_text(message, parse_mode="Markdown")

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /contact command"""
    message = f"""
📞 *Contact Us*

{BOT_OWNER}
{BOT_CONTACT}

We reply within 24 hours!
"""
    await update.message.reply_text(message, parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════════
# 👑 ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════

async def admin_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /panel command"""
    user_id = str(update.effective_user.id)
    
    if user_id not in Config.TELEGRAM_ADMIN_IDS:
        await update.message.reply_text("⛔ Admin only!")
        return
    
    await update.message.reply_text(
        "👑 *Admin Panel*\n\nChoose an action:",
        parse_mode="Markdown",
        reply_markup=admin_menu_keyboard()
    )

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command"""
    user_id = str(update.effective_user.id)
    
    if user_id not in Config.TELEGRAM_ADMIN_IDS:
        await update.message.reply_text("⛔ Admin only!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    
    message = " ".join(context.args)
    success = 0
    failed = 0
    
    for uid, user in user_manager.users.items():
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 *Broadcast:*\n\n{message}", parse_mode="Markdown")
            success += 1
        except:
            failed += 1
    
    await update.message.reply_text(f"✅ Sent to {success} users\n❌ Failed: {failed}")

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /users command"""
    user_id = str(update.effective_user.id)
    
    if user_id not in Config.TELEGRAM_ADMIN_IDS:
        await update.message.reply_text("⛔ Admin only!")
        return
    
    all_users = list(user_manager.users.values())
    
    if not all_users:
        await update.message.reply_text("No users yet!")
        return
    
    message = f"👥 *Users ({len(all_users)}):*\n\n"
    for i, user in enumerate(all_users[:20], 1):
        name = user.get('first_name', 'Unknown')
        msgs = user.get('messages_count', 0)
        message += f"{i}. {name} ({msgs} msgs)\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════════
# 💬 MESSAGE HANDLER
# ═══════════════════════════════════════════════════════════════

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    user_id = str(update.effective_user.id)
    user_manager.add_user(user_id, update.effective_user.username or "", update.effective_user.first_name or "")
    user_manager.increment(user_id, "messages_count")
    analytics.increment("total_messages")
    
    if Config.ENABLE_AI:
        await update.message.chat.send_action("typing")
        response = ai_manager.get_response(update.message.text)
        analytics.increment("total_ai_calls")
        await update.message.reply_text(f"🤖: {response}")

# ═══════════════════════════════════════════════════════════════
# 🔘 CALLBACK HANDLER (Button Clicks)
# ═══════════════════════════════════════════════════════════════

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    data = query.data
    
    # Menu callbacks
    if data == "menu_main":
        await query.edit_message_text(
            "📋 *Main Menu*\n\nChoose an option:",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    
    elif data == "menu_ai":
        await query.edit_message_text(
            "🤖 *Chat with AI*\n\nSend any message and I'll respond!\n\nOr use /ai <message>",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
    
    elif data == "menu_stats":
        await query.edit_message_text(
            analytics.get_report(),
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
    
    elif data == "menu_profile":
        user = user_manager.get_user(user_id)
        message = f"👤 *Your Profile*\n\nName: {user.get('first_name')}\nMessages: {user.get('messages_count', 0)}\nCommands: {user.get('commands_count', 0)}"
        await query.edit_message_text(message, parse_mode="Markdown", reply_markup=back_keyboard())
    
    elif data == "menu_orders":
        await query.edit_message_text(
            "📦 *Orders*\n\nUse /order to place an order!",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
    
    elif data == "menu_prices":
        await query.edit_message_text(
            "💰 *Prices*\n\nUse /price to view prices!",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
    
    elif data == "menu_contact":
        await query.edit_message_text(
            f"📞 *Contact*\n\n{BOT_OWNER}\n{BOT_CONTACT}",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
    
    # Admin callbacks
    elif data == "admin_broadcast":
        if user_id not in Config.TELEGRAM_ADMIN_IDS:
            await query.edit_message_text("⛔ Admin only!", reply_markup=back_keyboard())
        else:
            await query.edit_message_text(
                "📢 *Broadcast*\n\nUse /broadcast <message>",
                parse_mode="Markdown",
                reply_markup=back_keyboard()
            )
    
    elif data == "admin_users":
        if user_id not in Config.TELEGRAM_ADMIN_IDS:
            await query.edit_message_text("⛔ Admin only!", reply_markup=back_keyboard())
        else:
            all_users = list(user_manager.users.values())
            message = f"👥 *Users ({len(all_users)}):*\n\n"
            for i, user in enumerate(all_users[:10], 1):
                message += f"{i}. {user.get('first_name', 'Unknown')}\n"
            await query.edit_message_text(message, parse_mode="Markdown", reply_markup=back_keyboard())

# ═══════════════════════════════════════════════════════════════
# 🤖 BOT SETUP
# ═══════════════════════════════════════════════════════════════

class CustomTelegramBot:
    """Main bot class"""
    
    def __init__(self):
        self.app = None
    
    async def setup(self):
        self.app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # User commands
        self.app.add_handler(CommandHandler("start", start_command))
        self.app.add_handler(CommandHandler("help", help_command))
        self.app.add_handler(CommandHandler("menu", menu_command))
        self.app.add_handler(CommandHandler("about", about_command))
        self.app.add_handler(CommandHandler("stats", stats_command))
        self.app.add_handler(CommandHandler("profile", profile_command))
        self.app.add_handler(CommandHandler("ai", ai_command))
        self.app.add_handler(CommandHandler("order", order_command))
        self.app.add_handler(CommandHandler("price", price_command))
        self.app.add_handler(CommandHandler("contact", contact_command))
        
        # Admin commands
        self.app.add_handler(CommandHandler("panel", admin_panel_command))
        self.app.add_handler(CommandHandler("broadcast", broadcast_command))
        self.app.add_handler(CommandHandler("users", users_command))
        
        # Message & callback handlers
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        self.app.add_handler(CallbackQueryHandler(callback_handler))
        
        logger.info(f"{BOT_NAME} v{BOT_VERSION} ready!")
    
    async def start(self):
        await self.setup()
        logger.info(f"Starting {BOT_NAME}...")
        await self.app.run_polling(drop_pending_updates=True)
    
    async def stop(self):
        if self.app:
            await self.app.stop()

# ═══════════════════════════════════════════════════════════════
# 🚀 MAIN
# ═══════════════════════════════════════════════════════════════

async def main():
    print(f"""
╔══════════════════════════════════════════╗
║         {BOT_NAME} v{BOT_VERSION}             ║
║    {BOT_TAGLINE}        ║
╚══════════════════════════════════════════╝
    """)
    
    if not Config.TELEGRAM_BOT_TOKEN:
        print("❌ Set TELEGRAM_BOT_TOKEN in .env")
        return
    
    bot = CustomTelegramBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
