#!/usr/bin/env python3
"""
WhatsApp Automation Hub v5.2 - Telegram Bot
All functions: Auto-reply, Broadcast, Lead Generation
"""

import os, sys, logging, json, time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENWA_URL = os.getenv("OPENWA_URL", "http://localhost:3000")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "")
OPENWA_SESSION = os.getenv("OPENWA_SESSION_ID", "default")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "WhatsApp Bot")

class Database:
    def __init__(self, db_file="data/bot_database.json"):
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()
    
    def _load(self):
        if self.db_file.exists():
            try: return json.loads(self.db_file.read_text())
            except: pass
        return {
            "customers": [], "leads": [], "orders": [],
            "templates": {
                "hi": "Hello! Welcome to {b}!",
                "hello": "Hi there!",
                "price": "Our prices are competitive!",
                "order": "Great! Tell me your Name, Items, Address",
                "delivery": "Yes! Delivery 2-5 days.",
                "hours": "Open 9 AM - 9 PM!",
            },
            "messages": [],
            "stats": {"total_messages": 0, "total_leads": 0, "total_broadcasts": 0}
        }
    
    def save(self): self.db_file.write_text(json.dumps(self.data, indent=2))
    def _clean(self, phone):
        if not phone: return ""
        return str(phone).replace("@c.us", "").replace("@g.us", "").replace("+", "").replace(" ", "").replace("-", "")
    
    def add_customer(self, phone, name=None):
        phone = self._clean(phone)
        for c in self.data["customers"]:
            if c["phone"] == phone: return False
        self.data["customers"].append({"phone": phone, "name": name or "", "added_at": datetime.now().isoformat()})
        self.save(); return True
    
    def add_lead(self, phone, message=None):
        phone = self._clean(phone)
        for lead in self.data["leads"]:
            if lead["phone"] == phone:
                lead["last_message"] = message or ""
                lead["updated_at"] = datetime.now().isoformat()
                self.save(); return False
        self.data["leads"].append({"phone": phone, "message": message or "", "created_at": datetime.now().isoformat(), "status": "new"})
        self.data["stats"]["total_leads"] += 1
        self.add_customer(phone)
        self.save(); return True
    
    def add_message(self, sender, msg, direction):
        self.data["messages"].append({"time": datetime.now().isoformat(), "sender": self._clean(sender), "message": msg[:500], "direction": direction})
        self.data["stats"]["total_messages"] += 1
        self.save()
    
    def add_template(self, k, v): self.data["templates"][k.lower()] = v; self.save()
    def get_template(self, k): return self.data["templates"].get(k.lower())
    def get_all_templates(self): return self.data["templates"]
    def get_stats(self): return {**self.data["stats"], "customers": len(self.data["customers"]), "templates": len(self.data["templates"])}

db = Database()

class AI:
    def __init__(self):
        self.client = None
        if GROQ_API_KEY:
            try:
                from groq import Groq
                self.client = Groq(api_key=GROQ_API_KEY)
            except: pass
    
    def get_response(self, message):
        msg_lower = message.lower().strip()
        t = db.get_template(msg_lower)
        if t: return t.replace("{b}", BUSINESS_NAME), "template"
        for k, v in db.get_all_templates().items():
            if k in msg_lower: return v.replace("{b}", BUSINESS_NAME), "template"
        if self.client:
            try:
                chat = self.client.chat.completions.create(model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": f"Helpful for {BUSINESS_NAME}. SHORT."}, {"role": "user", "content": message}],
                    temperature=0.7, max_tokens=150)
                return chat.choices[0].message.content, "ai"
            except: pass
        return "Thanks! We'll get back soon.", "default"

ai = AI()

class WA:
    def __init__(self):
        self.url = OPENWA_URL.rstrip("/")
        self.api_key = OPENWA_API_KEY
        self.session = OPENWA_SESSION
    
    def is_connected(self):
        if not self.api_key: return False
        try:
            import requests
            r = requests.get(f"{self.url}/api/connection", headers={"X-API-Key": self.api_key}, timeout=5)
            return r.status_code == 200
        except: return False
    
    def send(self, phone, text):
        if not self.api_key: return False
        try:
            import requests
            phone = db._clean(phone)
            r = requests.post(f"{self.url}/api/messages/sendText",
                headers={"X-API-Key": self.api_key, "Content-Type": "application/json"},
                json={"session": self.session, "chatId": f"{phone}@c.us", "text": text}, timeout=30)
            return r.status_code == 200
        except: return False
    
    def broadcast(self, message, delay=1):
        sent = failed = 0
        for c in db.data["customers"]:
            if self.send(c["phone"], message): sent += 1
            else: failed += 1
            time.sleep(delay)
        return sent, failed

wa = WA()

# Telegram
try:
    import telegram
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

async def start(update, context): await update.message.reply_text(f"WhatsApp Hub v5.2\nWhatsApp: {'Connected' if wa.is_connected() else 'Not Connected'}\nAI: {'Active' if ai.client else 'Disabled'}\n\nCommands:\n/status - Check status\n/broadcast - Send to all\n/send - Send message\n/leads - View leads")

async def status_cmd(update, context):
    stats = db.get_stats()
    await update.message.reply_text(f"WhatsApp: {'Connected' if wa.is_connected() else 'Not Connected'}\nAI: {'Active' if ai.client else 'Disabled'}\n\nStats:\nMessages: {stats.get('total_messages', 0)}\nCustomers: {stats.get('customers', 0)}\nLeads: {stats.get('total_leads', 0)}\nBroadcasts: {stats.get('total_broadcasts', 0)}")

async def broadcast_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /broadcast MESSAGE"); return
    if not wa.is_connected(): await update.message.reply_text("WhatsApp not connected!"); return
    msg = " ".join(context.args)
    sent, failed = wa.broadcast(msg)
    db.data["stats"]["total_broadcasts"] += 1
    db.save()
    await update.message.reply_text(f"Broadcast done!\nSent: {sent}\nFailed: {failed}")

async def send_cmd(update, context):
    if not context.args or len(context.args) < 2: await update.message.reply_text("Usage: /send PHONE MESSAGE"); return
    phone, msg = context.args[0], " ".join(context.args[1:])
    if wa.send(phone, msg):
        db.add_message(phone, msg, "outgoing")
        await update.message.reply_text(f"Sent to {phone}!")
    else: await update.message.reply_text("Failed!")

async def leads_cmd(update, context):
    leads = db.data["leads"]
    if not leads: await update.message.reply_text("No leads yet!"); return
    text = f"Leads ({len(leads)}):\n\n"
    for lead in leads[-10:]:
        text += f"{lead['phone']}\n{lead.get('message', '')[:30]}\n\n"
    await update.message.reply_text(text)

async def customers_cmd(update, context):
    customers = db.data["customers"]
    if not customers: await update.message.reply_text("No customers!"); return
    text = f"Customers ({len(customers)}):\n\n"
    for c in customers[:20]: text += f"{c['phone']}\n"
    await update.message.reply_text(text)

async def addcustomer_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /addcustomer PHONE"); return
    phone = context.args[0]
    if db.add_customer(phone): await update.message.reply_text(f"Added {phone}!")
    else: await update.message.reply_text("Already exists!")

async def addlead_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /addlead PHONE MESSAGE"); return
    phone = context.args[0]
    msg = " ".join(context.args[1:]) if len(context.args) > 1 else ""
    if db.add_lead(phone, msg): await update.message.reply_text(f"New lead: {phone}")
    else: await update.message.reply_text("Lead updated!")

async def template_cmd(update, context):
    if not context.args or len(context.args) < 2:
        templates = db.get_all_templates()
        text = f"Templates ({len(templates)}):\n\n"
        for k, v in templates.items(): text += f"{k}: {v[:30]}...\n"
        await update.message.reply_text(text); return
    db.add_template(context.args[0], " ".join(context.args[1:]))
    await update.message.reply_text("Template added!")

async def message_handler(update, context):
    response, source = ai.get_response(update.message.text)
    await update.message.reply_text(response)

def main():
    if not TELEGRAM_TOKEN: print("Set TELEGRAM_BOT_TOKEN!"); return
    if not TELEGRAM_AVAILABLE: print("pip install python-telegram-bot"); return
    
    print(f"Starting bot... WhatsApp: {'Connected' if wa.is_connected() else 'Not Connected'}")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    app.add_handler(CommandHandler("send", send_cmd))
    app.add_handler(CommandHandler("leads", leads_cmd))
    app.add_handler(CommandHandler("customers", customers_cmd))
    app.add_handler(CommandHandler("addcustomer", addcustomer_cmd))
    app.add_handler(CommandHandler("addlead", addlead_cmd))
    app.add_handler(CommandHandler("template", template_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot running! /start in Telegram")
    app.run_polling()

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("Stopped!")
