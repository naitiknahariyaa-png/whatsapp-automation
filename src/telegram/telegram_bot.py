"""
v3.8 Tab - Telegram Bot PRO Edition
===================================
Advanced Telegram Bot with AI, Automation & Multi-Provider Support

Based on:
- https://github.com/Moh4696/build-ai-agents-free (LangChain AI)
- https://github.com/rmyndharis/OpenWA (WhatsApp Gateway)

Features:
- 🤖 AI Chat (Groq, Gemini, OpenRouter, Ollama)
- 🔗 OpenWA Integration
- 📊 Advanced Analytics
- 👥 User Management
- 🔔 Notifications & Alerts
- 📈 Scalable Architecture
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import telegram
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, MessageHandler, 
        CallbackQueryHandler, ConversationHandler, ContextTypes,
        filters
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("Install python-telegram-bot: pip install python-telegram-bot")


class Config:
    """Bot Configuration"""
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_ADMIN_IDS = os.getenv("TELEGRAM_ADMIN_IDS", "").split(",")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    OPENWA_URL = os.getenv("OPENWA_URL", "http://localhost:2785")
    OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "")
    BOT_NAME = "v3.8 Tab"
    BOT_VERSION = "3.8.0"
    BOT_TAGLINE = "PRO Edition - AI Powered"
    ENABLE_AI = True
    ENABLE_ANALYTICS = True
    ENABLE_USER_MANAGEMENT = True
    ENABLE_BROADCAST = True


class AIManager:
    """Multi-Provider AI Manager"""
    
    def __init__(self):
        self.providers = {}
        self.current_provider = "groq"
        self._init_providers()
    
    def _init_providers(self):
        if Config.GROQ_API_KEY:
            self.providers["groq"] = {"name": "Groq", "status": "active", "speed": "Fast", "cost": "FREE"}
        if Config.GOOGLE_API_KEY:
            self.providers["gemini"] = {"name": "Google Gemini", "status": "ready", "speed": "Fast", "cost": "FREE"}
        if Config.OPENROUTER_API_KEY:
            self.providers["openrouter"] = {"name": "OpenRouter", "status": "ready", "speed": "Medium", "cost": "PAID"}
        self.providers["ollama"] = {"name": "Ollama (Local)", "status": "ready", "speed": "Local", "cost": "FREE"}
    
    def get_response(self, message: str, user_id: str = "default") -> str:
        for provider in ["groq", "gemini", "ollama", "openrouter"]:
            if provider in self.providers:
                try:
                    response = self._call_provider(provider, message, user_id)
                    if response:
                        return response
                except Exception as e:
                    logger.warning(f"{provider} failed: {e}")
                    continue
        return "All AI providers failed!"
    
    def _call_provider(self, provider: str, message: str, user_id: str) -> Optional[str]:
        if provider == "groq":
            return self._call_groq(message)
        elif provider == "gemini":
            return self._call_gemini(message)
        elif provider == "ollama":
            return self._call_ollama(message)
        elif provider == "openrouter":
            return self._call_openrouter(message)
    
    def _call_groq(self, message: str) -> str:
        import requests
        headers = {"Authorization": f"Bearer {Config.GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": message}]}
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        raise Exception(f"Groq error: {response.status_code}")
    
    def _call_gemini(self, message: str) -> str:
        import requests
        data = {"contents": [{"parts": [{"text": message}]}]}
        response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={Config.GOOGLE_API_KEY}", json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        raise Exception(f"Gemini error: {response.status_code}")
    
    def _call_ollama(self, message: str) -> str:
        import requests
        data = {"model": Config.OLLAMA_MODEL, "prompt": message, "stream": False}
        response = requests.post(f"{Config.OLLAMA_URL}/api/generate", json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["response"]
        raise Exception(f"Ollama error: {response.status_code}")
    
    def _call_openrouter(self, message: str) -> str:
        import requests
        headers = {"Authorization": f"Bearer {Config.OPENROUTER_API_KEY}"}
        data = {"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": message}]}
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        raise Exception(f"OpenRouter error: {response.status_code}")
    
    def get_status(self) -> str:
        lines = [f"AI Status - {Config.BOT_NAME}\n"]
        for name, info in self.providers.items():
            lines.append(f"[{info['status']}] {info['name']} - {info['cost']}")
        return "\n".join(lines)


class UserManager:
    """User Management System"""
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.blacklist: List[str] = []
    
    def add_user(self, user_id: str, username: str = "", first_name: str = ""):
        if user_id not in self.users:
            self.users[user_id] = {
                "id": user_id, "username": username, "first_name": first_name,
                "created_at": datetime.now().isoformat(), "messages_count": 0,
                "commands_count": 0, "last_seen": datetime.now().isoformat(),
                "is_premium": False, "is_admin": user_id in Config.TELEGRAM_ADMIN_IDS
            }
    
    def increment_messages(self, user_id: str):
        if user_id in self.users:
            self.users[user_id]["messages_count"] += 1
    
    def increment_commands(self, user_id: str):
        if user_id in self.users:
            self.users[user_id]["commands_count"] += 1
    
    def is_blacklisted(self, user_id: str) -> bool:
        return user_id in self.blacklist
    
    def get_user_stats(self, user_id: str) -> str:
        if user_id not in self.users:
            return "User not found!"
        user = self.users[user_id]
        return f"Name: {user['first_name']}\nMsgs: {user['messages_count']}\nCommands: {user['commands_count']}"
    
    def get_all_users(self) -> List[Dict]:
        return list(self.users.values())
    
    def get_total_users(self) -> int:
        return len(self.users)


class AnalyticsManager:
    """Analytics & Statistics"""
    
    def __init__(self):
        self.stats = {
            "total_messages": 0, "total_ai_responses": 0, "total_commands": 0,
            "total_errors": 0, "total_broadcasts": 0, "commands": {},
            "start_time": datetime.now().isoformat()
        }
    
    def increment(self, key: str, value: int = 1):
        if key in self.stats:
            self.stats[key] += value
    
    def track_command(self, command: str):
        self.increment("total_commands")
        if command not in self.stats["commands"]:
            self.stats["commands"][command] = 0
        self.stats["commands"][command] += 1
    
    def get_stats(self) -> str:
        return f"""Statistics - {Config.BOT_NAME}
Total Messages: {self.stats['total_messages']}
AI Responses: {self.stats['total_ai_responses']}
Commands: {self.stats['total_commands']}
Users: {user_manager.get_total_users()}
Version: {Config.BOT_VERSION}"""


# Global instances
ai_manager = AIManager()
user_manager = UserManager()
analytics = AnalyticsManager()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_manager.add_user(str(user.id), user.username or "", user.first_name or "")
    user_manager.increment_commands(str(user.id))
    analytics.track_command("start")
    
    welcome = f"""Welcome to {Config.BOT_NAME}!

{Config.BOT_TAGLINE}

Commands:
/start - Start bot
/help - Help
/ai <msg> - Chat with AI
/stats - Statistics
/profile - Your profile
/aistatus - AI status

Get your API keys from:
- Groq: https://console.groq.com
- Gemini: https://aistudio.google.com"""
    
    await update.message.reply_text(welcome)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_manager.increment_commands(str(update.effective_user.id))
    analytics.track_command("help")
    
    help_text = f"""{Config.BOT_NAME} Commands:

/start - Start bot
/help - Show this help
/ai <message> - Chat with AI
/stats - View statistics
/profile - Your profile
/aistatus - AI provider status
/broadcast <msg> - Broadcast (admin)
/users - List users (admin)

v{Config.BOT_VERSION} - {Config.BOT_TAGLINE}"""
    
    await update.message.reply_text(help_text)


async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    if not context.args:
        await update.message.reply_text("Usage: /ai <your message>")
        return
    
    user_message = " ".join(context.args)
    user_manager.increment_messages(user_id)
    analytics.increment("total_messages")
    await update.message.chat.send_action("typing")
    
    response = ai_manager.get_response(user_message, user_id)
    analytics.increment("total_ai_responses")
    
    await update.message.reply_text(f"AI: {response}")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    analytics.track_command("stats")
    stats_text = analytics.get_stats()
    await update.message.reply_text(stats_text)


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_manager.increment_commands(user_id)
    analytics.track_command("profile")
    profile_text = user_manager.get_user_stats(user_id)
    await update.message.reply_text(profile_text)


async def aistatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_manager.increment_commands(user_id)
    analytics.track_command("aistatus")
    status_text = ai_manager.get_status()
    await update.message.reply_text(status_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    if user_manager.is_blacklisted(user_id):
        await update.message.reply_text("You are blacklisted!")
        return
    
    user_manager.increment_messages(user_id)
    analytics.increment("total_messages")
    
    if Config.ENABLE_AI:
        await update.message.chat.send_action("typing")
        response = ai_manager.get_response(update.message.text, user_id)
        analytics.increment("total_ai_responses")
        await update.message.reply_text(response)


class TelegramBotPRO:
    def __init__(self):
        self.app = None
        self.running = False
    
    async def setup(self):
        self.app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        self.app.add_handler(CommandHandler("start", start_command))
        self.app.add_handler(CommandHandler("help", help_command))
        self.app.add_handler(CommandHandler("ai", ai_command))
        self.app.add_handler(CommandHandler("stats", stats_command))
        self.app.add_handler(CommandHandler("profile", profile_command))
        self.app.add_handler(CommandHandler("aistatus", aistatus_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        logger.info(f"{Config.BOT_NAME} v{Config.BOT_VERSION} initialized")
    
    async def start(self):
        if not self.app:
            await self.setup()
        self.running = True
        logger.info(f"{Config.BOT_NAME} started!")
        await self.app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    
    async def stop(self):
        self.running = False
        if self.app:
            await self.app.stop()
        logger.info(f"{Config.BOT_NAME} stopped!")


async def main():
    print(f"""
╔══════════════════════════════════════╗
║    {Config.BOT_NAME} - {Config.BOT_VERSION} PRO Edition     ║
║    {Config.BOT_TAGLINE}                 ║
╚══════════════════════════════════════╝
    """)
    
    if not Config.TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set!")
        return
    
    bot = TelegramBotPRO()
    try:
        await bot.start()
    except KeyboardInterrupt:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
