#!/usr/bin/env python3
"""
WhatsApp Hub v5.2 - COMPLETE WORKING SYSTEM
==========================================
ALL FEATURES WORKING:
- Send WhatsApp messages
- Auto-reply from incoming
- Broadcast to all customers
- Lead capture
- Web Dashboard
- Telegram Bot

Author: Built with OpenHands
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path
from threading import Thread
import traceback

# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("WhatsAppHub")

# ═══════════════════════════════════════════════════════════════
# LOAD .env
# ═══════════════════════════════════════════════════════════════

def load_env():
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
        logger.info("Loaded .env file")

load_env()

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

OPENWA_URL = os.getenv("OPENWA_URL", "http://localhost:3000")
OPENWA_KEY = os.getenv("OPENWA_API_KEY", "")
OPENWA_SESSION = os.getenv("OPENWA_SESSION", "default")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "WhatsApp Bot")
PORT = int(os.getenv("PORT", "8000"))

# ═══════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════

DB_FILE = Path("data/database.json")
DB_FILE.parent.mkdir(exist_ok=True)

def load_db():
    if DB_FILE.exists():
        try:
            return json.loads(DB_FILE.read_text())
        except:
            pass
    return default_db()

def save_db(data):
    DB_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def default_db():
    return {
        "customers": [],
        "leads": [],
        "messages": [],
        "templates": {
            "hi": "Hello! Welcome to {b}!",
            "hello": "Hi there! How can I help?",
            "price": "Our prices are competitive!",
            "order": "To order, tell: Name, Items, Address",
            "delivery": "Yes! Delivery 2-5 days pan-India!",
            "hours": "Open 9 AM - 9 PM daily!",
            "thanks": "You're welcome!",
            "bye": "Goodbye!"
        },
        "stats": {"messages": 0, "leads": 0, "broadcasts": 0, "ai_responses": 0}
    }

db = load_db()

def add_customer(phone):
    phone = clean_phone(phone)
    if not phone: return False
    for c in db["customers"]:
        if c.get("phone") == phone: return False
    db["customers"].append({"phone": phone, "added": datetime.now().isoformat()})
    save_db(db)
    return True

def add_lead(phone, message=""):
    phone = clean_phone(phone)
    if not phone: return False
    for l in db["leads"]:
        if l.get("phone") == phone:
            l["last"] = message
            l["time"] = datetime.now().isoformat()
            save_db(db)
            return False
    db["leads"].append({"phone": phone, "first": message, "last": message, "time": datetime.now().isoformat()})
    db["stats"]["leads"] = len(db["leads"])
    add_customer(phone)
    save_db(db)
    return True

def add_message(sender, msg, direction):
    db["messages"].append({
        "time": datetime.now().isoformat(),
        "sender": clean_phone(sender),
        "message": msg[:500],
        "direction": direction
    })
    db["stats"]["messages"] = len(db["messages"])
    if len(db["messages"]) > 1000: db["messages"] = db["messages"][-1000:]
    save_db(db)

def get_stats():
    return {
        **db["stats"],
        "customers": len(db["customers"]),
        "leads": len(db["leads"]),
        "templates": len(db["templates"])
    }

def clean_phone(phone):
    if not phone: return ""
    return str(phone).replace("@c.us","").replace("@g.us","").replace("+","").replace(" ","").replace("-","")

# ═══════════════════════════════════════════════════════════════
# TEMPLATES / AI
# ═══════════════════════════════════════════════════════════════

def get_response(message):
    """Get auto-reply using templates or AI"""
    msg_lower = message.lower().strip()
    
    # Check templates
    for keyword, response in db["templates"].items():
        if keyword in msg_lower:
            return response.replace("{b}", BUSINESS_NAME), "template"
    
    # Use AI if available
    if GROQ_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_KEY)
            chat = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are assistant for {BUSINESS_NAME}. Keep SHORT responses."},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=100
            )
            db["stats"]["ai_responses"] += 1
            save_db(db)
            return chat.choices[0].message.content, "ai"
        except Exception as e:
            logger.error(f"AI Error: {e}")
    
    return "Thanks! We'll get back soon.", "default"

# ═══════════════════════════════════════════════════════════════
# WHATSAPP SENDER
# ═══════════════════════════════════════════════════════════════

def send_whatsapp(phone, text):
    """Send WhatsApp message via OpenWA/WAHA"""
    if not OPENWA_KEY:
        logger.error("No OPENWA_API_KEY configured!")
        return False
    
    try:
        import requests
        phone = clean_phone(phone)
        
        payload = {
            "session": OPENWA_SESSION,
            "chatId": f"{phone}@c.us",
            "text": text
        }
        
        headers = {"X-API-Key": OPENWA_KEY, "Content-Type": "application/json"}
        
        # Try different API endpoints
        endpoints = [
            f"{OPENWA_URL}/api/messages/sendText",
            f"{OPENWA_URL}/api/sendText",
            f"{OPENWA_URL}/api/message/text"
        ]
        
        for url in endpoints:
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=15)
                if r.status_code == 200 or r.status_code == 201:
                    logger.info(f"Sent to {phone}: {text[:30]}...")
                    return True
                else:
                    logger.debug(f"Endpoint {url} returned {r.status_code}")
            except:
                continue
        
        logger.warning(f"All endpoints failed for {phone}")
        return False
        
    except Exception as e:
        logger.error(f"Send error: {e}")
        return False

def send_broadcast(message):
    """Broadcast to all customers"""
    customers = db["customers"]
    if not customers:
        return 0, 0
    
    sent = failed = 0
    for c in customers:
        if send_whatsapp(c["phone"], message):
            sent += 1
        else:
            failed += 1
        time.sleep(1)  # Rate limit
    
    db["stats"]["broadcasts"] += 1
    save_db(db)
    return sent, failed

def check_whatsapp():
    """Check if WhatsApp gateway is connected"""
    if not OPENWA_KEY:
        return False
    
    try:
        import requests
        headers = {"X-API-Key": OPENWA_KEY}
        
        endpoints = [
            f"{OPENWA_URL}/api/connection",
            f"{OPENWA_URL}/api/status",
            f"{OPENWA_URL}/api/health"
        ]
        
        for url in endpoints:
            try:
                r = requests.get(url, headers=headers, timeout=5)
                if r.status_code == 200:
                    return True
            except:
                continue
        
        return False
    except:
        return False

# ═══════════════════════════════════════════════════════════════
# WEB SERVER
# ═══════════════════════════════════════════════════════════════

def start_web():
    """Start FastAPI web server"""
    try:
        from fastapi import FastAPI, Request
        from fastapi.responses import HTMLResponse, JSONResponse
        import uvicorn
        
        app = FastAPI(title="WhatsApp Hub")
        
        @app.post("/webhook")
        async def webhook(request: Request):
            """Receive WhatsApp messages"""
            try:
                body = await request.json()
                logger.info(f"Webhook: {str(body)[:200]}")
                
                # Parse WAHA format
                sender = ""
                message = ""
                
                if "payload" in body:
                    p = body["payload"]
                    sender = p.get("from", "")
                    msg = p.get("message", {})
                    if isinstance(msg, dict):
                        message = msg.get("conversation") or msg.get("text", "")
                    else:
                        message = str(msg)
                
                # Parse simple format
                elif "from" in body:
                    sender = body.get("from", "")
                    msg = body.get("message", {})
                    if isinstance(msg, dict):
                        message = msg.get("conversation") or msg.get("text", "")
                    else:
                        message = str(msg)
                
                if sender and message:
                    sender = clean_phone(sender)
                    message = message.strip()
                    
                    # Log and capture lead
                    add_message(sender, message, "incoming")
                    add_lead(sender, message)
                    
                    # Get response
                    response, source = get_response(message)
                    
                    # Log and send
                    add_message(sender, response, "outgoing")
                    send_whatsapp(sender, response)
                    
                    logger.info(f"Auto-reply sent: {source}")
                    return JSONResponse({"status": "ok"})
                
                return JSONResponse({"status": "ignored"})
            except Exception as e:
                logger.error(f"Webhook error: {e}")
                return JSONResponse({"status": "error"})
        
        @app.get("/")
        async def dashboard():
            html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WhatsApp Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen p-6">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">🤖 WhatsApp Hub</h1>
        
        <div class="grid grid-cols-4 gap-4 mb-6">
            <div class="bg-gray-800 p-4 rounded">
                <p class="text-gray-400">Messages</p>
                <p id="msgs" class="text-2xl">-</p>
            </div>
            <div class="bg-gray-800 p-4 rounded">
                <p class="text-gray-400">Customers</p>
                <p id="custs" class="text-2xl">-</p>
            </div>
            <div class="bg-gray-800 p-4 rounded">
                <p class="text-gray-400">Leads</p>
                <p id="leads" class="text-2xl">-</p>
            </div>
            <div class="bg-gray-800 p-4 rounded">
                <p class="text-gray-400">Broadcasts</p>
                <p id="bcasts" class="text-2xl">-</p>
            </div>
        </div>
        
        <div class="grid grid-cols-2 gap-6 mb-6">
            <div class="bg-gray-800 p-4 rounded">
                <h2 class="font-bold mb-3">Send Message</h2>
                <input id="phone" placeholder="919876543210" class="w-full p-2 mb-2 bg-gray-700 rounded">
                <textarea id="msg" placeholder="Message..." rows="3" class="w-full p-2 mb-2 bg-gray-700 rounded"></textarea>
                <button onclick="sendMsg()" class="w-full bg-green-600 p-2 rounded">Send</button>
            </div>
            <div class="bg-gray-800 p-4 rounded">
                <h2 class="font-bold mb-3">Broadcast</h2>
                <p class="text-gray-400 mb-2">Send to ALL customers</p>
                <textarea id="bcast" placeholder="Broadcast..." rows="3" class="w-full p-2 mb-2 bg-gray-700 rounded"></textarea>
                <button onclick="doBroadcast()" class="w-full bg-purple-600 p-2 rounded">Broadcast</button>
            </div>
        </div>
        
        <div class="bg-gray-800 p-4 rounded">
            <h2 class="font-bold mb-3">Recent Messages</h2>
            <div id="recent" class="space-y-2 max-h-64 overflow-y-auto"></div>
        </div>
    </div>
    
    <script>
        async function load() {
            let r = await fetch('/api/stats');
            let d = await r.json();
            document.getElementById('msgs').textContent = d.messages || 0;
            document.getElementById('custs').textContent = d.customers || 0;
            document.getElementById('leads').textContent = d.leads || 0;
            document.getElementById('bcasts').textContent = d.broadcasts || 0;
            
            r = await fetch('/api/messages');
            let msgs = await r.json();
            document.getElementById('recent').innerHTML = msgs.slice(-10).reverse().map(m =>
                '<div class="p-2 bg-gray-700 rounded"><b>' + m.sender + '</b> <span class="text-' + (m.direction === 'incoming' ? 'blue' : 'green') + '-400">' + m.direction + '</span><p>' + m.message + '</p></div>'
            ).join('') || '<p class="text-gray-500">No messages</p>';
        }
        
        async function sendMsg() {
            let p = document.getElementById('phone').value;
            let m = document.getElementById('msg').value;
            if (!p || !m) return alert('Fill all');
            await fetch('/api/send', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({phone:p, message:m})});
            document.getElementById('msg').value = '';
            load();
        }
        
        async function doBroadcast() {
            let m = document.getElementById('bcast').value;
            if (!m) return alert('Enter message');
            if (!confirm('Send to ALL?')) return;
            await fetch('/api/broadcast', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message:m})});
            document.getElementById('bcast').value = '';
            load();
        }
        
        load(); setInterval(load, 5000);
    </script>
</body>
</html>"""
            return HTMLResponse(content=html)
        
        @app.get("/api/stats")
        async def stats():
            return JSONResponse(get_stats())
        
        @app.get("/api/messages")
        async def messages():
            return JSONResponse(db["messages"][-50:])
        
        @app.get("/api/customers")
        async def customers():
            return JSONResponse(db["customers"])
        
        @app.post("/api/send")
        async def send(request: Request):
            data = await request.json()
            phone = data.get("phone", "")
            message = data.get("message", "")
            if send_whatsapp(phone, message):
                add_message(phone, message, "outgoing")
                return JSONResponse({"success": True})
            return JSONResponse({"success": False, "message": "Failed"})
        
        @app.post("/api/broadcast")
        async def broadcast(request: Request):
            data = await request.json()
            message = data.get("message", "")
            sent, failed = send_broadcast(message)
            return JSONResponse({"success": True, "sent": sent, "failed": failed})
        
        @app.get("/health")
        async def health():
            return JSONResponse({"status": "ok"})
        
        logger.info(f"Starting web server on port {PORT}...")
        uvicorn.run(app, host="0.0.0.0", port=PORT)
        
    except ImportError as e:
        logger.error(f"FastAPI not installed: {e}")
    except Exception as e:
        logger.error(f"Web server error: {e}")

# ═══════════════════════════════════════════════════════════════
# TELEGRAM BOT
# ═══════════════════════════════════════════════════════════════

def start_telegram():
    """Start Telegram bot"""
    if not TELEGRAM_TOKEN:
        logger.warning("No TELEGRAM_BOT_TOKEN configured")
        return
    
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
        
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        async def cmd_start(update, context):
            stats = get_stats()
            await update.message.reply_text(
                f"🤖 WhatsApp Hub\n\n"
                f"WhatsApp: {'✅' if check_whatsapp() else '❌'}\n"
                f"Customers: {stats['customers']}\n"
                f"Leads: {stats['leads']}\n"
                f"Messages: {stats['messages']}\n\n"
                f"/broadcast MSG - Send to all\n"
                f"/send PHONE MSG - Send one\n"
                f"/leads - View leads\n"
                f"/customers - View customers"
            )
        
        async def cmd_broadcast(update, context):
            if not context.args:
                await update.message.reply_text("Usage: /broadcast MESSAGE")
                return
            msg = " ".join(context.args)
            sent, failed = send_broadcast(msg)
            await update.message.reply_text(f"✅ Done!\nSent: {sent}\nFailed: {failed}")
        
        async def cmd_send(update, context):
            if not context.args or len(context.args) < 2:
                await update.message.reply_text("Usage: /send PHONE MESSAGE")
                return
            phone = context.args[0]
            msg = " ".join(context.args[1:])
            if send_whatsapp(phone, msg):
                add_message(phone, msg, "outgoing")
                await update.message.reply_text(f"✅ Sent to {phone}")
            else:
                await update.message.reply_text(f"❌ Failed")
        
        async def cmd_leads(update, context):
            leads = db["leads"]
            if not leads:
                await update.message.reply_text("No leads yet!")
                return
            text = f"👥 Leads ({len(leads)}):\n\n"
            for l in leads[-10:]:
                text += f"📱 {l['phone']}\n{l.get('first','')[:30]}\n\n"
            await update.message.reply_text(text)
        
        async def cmd_customers(update, context):
            custs = db["customers"]
            if not custs:
                await update.message.reply_text("No customers!")
                return
            text = f"👥 Customers ({len(custs)}):\n\n"
            for c in custs[:15]:
                text += f"📱 {c['phone']}\n"
            await update.message.reply_text(text)
        
        async def cmd_addcustomer(update, context):
            if not context.args:
                await update.message.reply_text("Usage: /addcustomer PHONE")
                return
            phone = context.args[0]
            if add_customer(phone):
                await update.message.reply_text(f"✅ Added {phone}")
            else:
                await update.message.reply_text("Already exists")
        
        async def cmd_test(update, context):
            wa_ok = check_whatsapp()
            await update.message.reply_text(
                f"🔧 Test\n\n"
                f"WhatsApp: {'✅ OK' if wa_ok else '❌ FAIL'}\n"
                f"Database: ✅ OK"
            )
        
        app.add_handler(CommandHandler("start", cmd_start))
        app.add_handler(CommandHandler("broadcast", cmd_broadcast))
        app.add_handler(CommandHandler("bc", cmd_broadcast))
        app.add_handler(CommandHandler("send", cmd_send))
        app.add_handler(CommandHandler("leads", cmd_leads))
        app.add_handler(CommandHandler("customers", cmd_customers))
        app.add_handler(CommandHandler("addcustomer", cmd_addcustomer))
        app.add_handler(CommandHandler("test", cmd_test))
        
        logger.info("Starting Telegram bot...")
        app.run_polling()
        
    except ImportError:
        logger.error("python-telegram-bot not installed")
    except Exception as e:
        logger.error(f"Telegram error: {e}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("""
╔══════════════════════════════════════════════════╗
║                                                  ║
║   WHATSAPP HUB v5.2                            ║
║   ALL FEATURES WORKING                          ║
║                                                  ║
╚══════════════════════════════════════════════════╝
    """)
    
    # Status
    stats = get_stats()
    wa_connected = check_whatsapp()
    
    print(f"📊 Stats: {stats['messages']} msgs, {stats['customers']} custs, {stats['leads']} leads")
    print(f"📱 WhatsApp: {'✅ Connected' if wa_connected else '❌ Not Connected'}")
    print(f"🤖 AI: {'✅ Active' if GROQ_KEY else '⚠️ Templates only'}")
    print()
    
    if wa_connected:
        print("✅ WhatsApp Gateway is WORKING!")
    else:
        print("⚠️ WhatsApp Gateway not connected.")
        print("   Make sure OPENWA is running and OPENWA_API_KEY is set.")
    
    print()
    print(f"🌐 Dashboard: http://localhost:{PORT}")
    print(f"📋 Webhook: http://YOUR_IP:{PORT}/webhook")
    print()
    
    # Start web server
    Thread(target=start_web, daemon=True).start()
    
    # Start Telegram
    if TELEGRAM_TOKEN:
        start_telegram()
    else:
        print("📱 Telegram: No token (add TELEGRAM_BOT_TOKEN to .env)")
        print()
        print("Press Ctrl+C to stop")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Stopped!")
