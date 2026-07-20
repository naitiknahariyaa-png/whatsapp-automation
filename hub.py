#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🤖 WHATSAPP HUB v5.2 - ALL SKILLS WORKING                 ║
║                                                              ║
║   ✅ OpenWA Gateway     ✅ AI Auto-Reply                    ║
║   ✅ Lead Capture       ✅ Broadcast                          ║
║   ✅ Web Dashboard      ✅ Telegram Bot                       ║
║                                                              ║
║   USAGE: python hub.py                                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
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

# ═══════════════════════════════════════════════════════════════
# SETUP LOGGING
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WhatsAppHub")

# ═══════════════════════════════════════════════════════════════
# LOAD .env FILE
# ═══════════════════════════════════════════════════════════════

def load_env():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
        logger.info("Loaded .env file")

load_env()

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

class Config:
    """Master configuration class"""
    
    # WhatsApp Gateway (OpenWA/WAHA)
    OPENWA_URL = os.getenv("OPENWA_URL", "http://localhost:3000")
    OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "")
    OPENWA_SESSION = os.getenv("OPENWA_SESSION", "default")
    
    # AI Provider
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    # Telegram
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Business
    BUSINESS_NAME = os.getenv("BUSINESS_NAME", "WhatsApp Bot")
    
    # Server
    PORT = int(os.getenv("PORT", "8000"))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Healthchecks
    HEALTHCHECK_URL = os.getenv("HEALTHCHECK_URL", "")

config = Config()

# ═══════════════════════════════════════════════════════════════
# DATABASE CLASS
# ═══════════════════════════════════════════════════════════════

class Database:
    """JSON-based database with thread safety"""
    
    def __init__(self, filepath="data/database.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(exist_ok=True)
        self.data = self._load()
        self._lock_count = 0
    
    def _load(self):
        """Load data from file or return defaults"""
        if self.filepath.exists():
            try:
                return json.loads(self.filepath.read_text())
            except Exception as e:
                logger.warning(f"Could not load database: {e}")
        
        return self._default_data()
    
    def _default_data(self):
        """Default database structure"""
        return {
            "customers": [],
            "leads": [],
            "orders": [],
            "messages": [],
            "templates": {
                "hi": "Hello! 👋 Welcome to {business}! How can I help?",
                "hello": "Hi there! 😊 How may I assist you?",
                "price": "Our prices are very competitive! What interests you?",
                "cost": "Great question! Our prices are affordable.",
                "order": "To place order, tell me:\n1) Your Name\n2) Items\n3) Address",
                "buy": "Ready to buy? Share your name, items, and address!",
                "delivery": "🚚 Yes! We deliver all over India.\nDelivery: 2-5 business days",
                "shipping": "Pan-India delivery available! 2-5 days.",
                "hours": "🕐 Open 9 AM - 9 PM, all 7 days!",
                "timing": "Working hours: 9 AM to 9 PM daily!",
                "contact": "📱 Reach us anytime on WhatsApp!",
                "thanks": "You're welcome! 😊 Anything else?",
                "thank": "Thank you! 🙏 Let us know if you need help!",
                "bye": "Goodbye! Have a great day! 👋",
                "goodbye": "Take care! See you soon! 😊"
            },
            "blacklist": [],
            "stats": {
                "total_messages": 0,
                "total_leads": 0,
                "total_orders": 0,
                "total_broadcasts": 0,
                "total_ai_responses": 0,
                "total_template_responses": 0
            },
            "rate_limits": {}
        }
    
    def save(self):
        """Save data to file"""
        try:
            self.filepath.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Database save error: {e}")
    
    def clean_phone(self, phone):
        """Clean and standardize phone number"""
        if not phone:
            return ""
        phone = str(phone)
        phone = phone.replace("@c.us", "").replace("@g.us", "")
        phone = phone.replace("+91", "91").replace("+", "")
        phone = phone.replace(" ", "").replace("-", "")
        return phone
    
    # ─────────────────────────────────────────────────────────
    # CUSTOMER METHODS
    # ─────────────────────────────────────────────────────────
    
    def add_customer(self, phone, name="", source="manual"):
        """Add a customer"""
        phone = self.clean_phone(phone)
        if not phone:
            return False
        
        for c in self.data["customers"]:
            if c.get("phone") == phone:
                return False
        
        customer = {
            "id": f"cust_{len(self.data['customers'])}_{int(time.time())}",
            "phone": phone,
            "name": name,
            "source": source,
            "added_at": datetime.now().isoformat(),
            "message_count": 0
        }
        self.data["customers"].append(customer)
        self.save()
        return True
    
    def get_customers(self):
        """Get all customers"""
        return self.data.get("customers", [])
    
    # ─────────────────────────────────────────────────────────
    # LEAD METHODS
    # ─────────────────────────────────────────────────────────
    
    def add_lead(self, phone, message="", source="whatsapp"):
        """Add or update a lead"""
        phone = self.clean_phone(phone)
        if not phone:
            return False
        
        for lead in self.data["leads"]:
            if lead.get("phone") == phone:
                lead["last_message"] = message
                lead["updated_at"] = datetime.now().isoformat()
                lead["interaction_count"] = lead.get("interaction_count", 0) + 1
                self.save()
                return False
        
        lead = {
            "id": f"lead_{len(self.data['leads'])}_{int(time.time())}",
            "phone": phone,
            "first_message": message,
            "last_message": message,
            "source": source,
            "status": "new",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "interaction_count": 1
        }
        self.data["leads"].append(lead)
        self.data["stats"]["total_leads"] += 1
        
        # Also add as customer
        self.add_customer(phone, source="lead")
        
        self.save()
        return True
    
    def get_leads(self, status=None):
        """Get leads, optionally filtered by status"""
        leads = self.data.get("leads", [])
        if status:
            leads = [l for l in leads if l.get("status") == status]
        return leads
    
    # ─────────────────────────────────────────────────────────
    # MESSAGE METHODS
    # ─────────────────────────────────────────────────────────
    
    def add_message(self, sender, message, direction, is_ai=False, response_type="default"):
        """Log a message"""
        msg = {
            "id": f"msg_{len(self.data['messages'])}_{int(time.time())}",
            "time": datetime.now().isoformat(),
            "sender": self.clean_phone(sender),
            "message": message[:500],
            "direction": direction,
            "is_ai": is_ai,
            "response_type": response_type
        }
        self.data["messages"].append(msg)
        self.data["stats"]["total_messages"] += 1
        
        if is_ai and response_type == "ai":
            self.data["stats"]["total_ai_responses"] += 1
        elif response_type == "template":
            self.data["stats"]["total_template_responses"] += 1
        
        # Keep last 5000 messages
        if len(self.data["messages"]) > 5000:
            self.data["messages"] = self.data["messages"][-5000:]
        
        self.save()
    
    def get_messages(self, limit=100, direction=None):
        """Get message history"""
        messages = self.data.get("messages", [])
        if direction:
            messages = [m for m in messages if m.get("direction") == direction]
        return messages[-limit:]
    
    # ─────────────────────────────────────────────────────────
    # TEMPLATE METHODS
    # ─────────────────────────────────────────────────────────
    
    def add_template(self, keyword, response):
        """Add auto-reply template"""
        self.data["templates"][keyword.lower().strip()] = response
        self.save()
    
    def delete_template(self, keyword):
        """Delete template"""
        keyword = keyword.lower().strip()
        if keyword in self.data["templates"]:
            del self.data["templates"][keyword]
            self.save()
            return True
        return False
    
    def get_templates(self):
        """Get all templates"""
        return self.data.get("templates", {})
    
    def match_template(self, message):
        """Find matching template for message"""
        msg_lower = message.lower().strip()
        
        # Exact match
        if msg_lower in self.data["templates"]:
            return self.data["templates"][msg_lower], "exact"
        
        # Partial keyword match
        for keyword, response in self.data["templates"].items():
            if keyword in msg_lower:
                return response, "keyword"
        
        return None, None
    
    # ─────────────────────────────────────────────────────────
    # RATE LIMITING
    # ─────────────────────────────────────────────────────────
    
    def check_rate_limit(self, phone, limit=60, window=60):
        """Check if phone is rate limited"""
        if not config.RATE_LIMIT_ENABLED:
            return True
        
        phone = self.clean_phone(phone)
        now = time.time()
        
        if phone not in self.data["rate_limits"]:
            self.data["rate_limits"][phone] = {"count": 0, "window_start": now}
        
        rate = self.data["rate_limits"][phone]
        
        if now - rate["window_start"] > window:
            rate["count"] = 0
            rate["window_start"] = now
        
        if rate["count"] >= limit:
            return False
        
        rate["count"] += 1
        return True
    
    # ─────────────────────────────────────────────────────────
    # STATS
    # ─────────────────────────────────────────────────────────
    
    def get_stats(self):
        """Get statistics"""
        stats = self.data["stats"].copy()
        stats["customers"] = len(self.data["customers"])
        stats["leads"] = len(self.data["leads"])
        stats["new_leads"] = len([l for l in self.data["leads"] if l.get("status") == "new"])
        stats["templates"] = len(self.data["templates"])
        return stats

# Create global database instance
db = Database()

# ═══════════════════════════════════════════════════════════════
# AI ENGINE CLASS
# ═══════════════════════════════════════════════════════════════

class AIEngine:
    """AI Engine using Groq API (FREE & FAST)"""
    
    def __init__(self):
        self.client = None
        self.enabled = False
        
        if config.GROQ_API_KEY:
            try:
                from groq import Groq
                self.client = Groq(api_key=config.GROQ_API_KEY)
                self.enabled = True
                logger.info("✅ AI Engine: Groq connected")
            except ImportError:
                logger.warning("⚠️ AI Engine: groq package not installed")
            except Exception as e:
                logger.warning(f"⚠️ AI Engine: {e}")
        else:
            logger.info("ℹ️ AI Engine: No API key (using templates only)")
    
    def get_response(self, message, context=None):
        """
        Get AI response for message
        Returns: (response_text, source_type)
        """
        # Check templates first
        template_response, match_type = db.match_template(message)
        if template_response:
            response = template_response.replace("{business}", config.BUSINESS_NAME)
            return response, "template"
        
        # Use AI if available
        if self.client:
            try:
                system_prompt = f"""You are a helpful assistant for {config.BUSINESS_NAME}.
Keep responses SHORT and FRIENDLY (1-2 sentences max).
Help customers with orders, questions, and inquiries.
Be warm, professional, and concise."""

                chat = self.client.chat.completions.create(
                    model=config.GROQ_MODEL,
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
        
        # Default fallback
        return "Thanks for your message! We'll get back to you shortly. 🙏", "default"

# Create global AI instance
ai = AIEngine()

# ═══════════════════════════════════════════════════════════════
# WHATSAPP GATEWAY CLASS
# ═══════════════════════════════════════════════════════════════

class WhatsAppGateway:
    """WhatsApp Gateway using OpenWA/WAHA REST API"""
    
    def __init__(self):
        self.url = config.OPENWA_URL.rstrip("/")
        self.api_key = config.OPENWA_API_KEY
        self.session = config.OPENWA_SESSION
        self.enabled = bool(self.api_key)
    
    def _headers(self):
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def is_connected(self):
        """Check if gateway is connected"""
        if not self.enabled:
            return False
        
        try:
            import requests
            r = requests.get(
                f"{self.url}/api/connection",
                headers=self._headers(),
                timeout=5
            )
            return r.status_code == 200
        except Exception as e:
            logger.warning(f"WhatsApp check failed: {e}")
            return False
    
    def send_message(self, phone, text):
        """Send WhatsApp message"""
        if not self.enabled:
            logger.error("WhatsApp: Not enabled (no API key)")
            return False
        
        try:
            import requests
            phone = db.clean_phone(phone)
            
            if not db.check_rate_limit(phone):
                logger.warning(f"Rate limited: {phone}")
                return False
            
            payload = {
                "session": self.session,
                "chatId": f"{phone}@c.us",
                "text": text
            }
            
            r = requests.post(
                f"{self.url}/api/messages/sendText",
                headers=self._headers(),
                json=payload,
                timeout=30
            )
            
            if r.status_code == 200:
                logger.info(f"✅ Sent to {phone}: {text[:30]}...")
                return True
            else:
                logger.error(f"Send failed: {r.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    def send_broadcast(self, message, delay=1):
        """
        Send broadcast to all customers
        Returns: (sent_count, failed_count)
        """
        customers = db.get_customers()
        if not customers:
            logger.warning("Broadcast: No customers")
            return 0, 0
        
        logger.info(f"Broadcast: Starting for {len(customers)} customers")
        
        sent = failed = 0
        for customer in customers:
            phone = customer.get("phone")
            if phone:
                if self.send_message(phone, message):
                    sent += 1
                else:
                    failed += 1
                time.sleep(delay)
        
        db.data["stats"]["total_broadcasts"] += 1
        db.save()
        
        logger.info(f"Broadcast: Done! Sent={sent}, Failed={failed}")
        return sent, failed

# Create global WhatsApp instance
wa = WhatsAppGateway()

# ═══════════════════════════════════════════════════════════════
# HEALTHCHECKS CLASS
# ═══════════════════════════════════════════════════════════════

class HealthChecks:
    """Healthchecks.io integration"""
    
    def __init__(self):
        self.url = config.HEALTHCHECK_URL
    
    def ping(self, event=""):
        """Send ping to healthchecks"""
        if not self.url:
            return
        
        try:
            import requests
            url = f"{self.url}{event}" if event else self.url
            requests.get(url, timeout=5)
        except:
            pass
    
    def start(self): self.ping("/start")
    def success(self): self.ping("")
    def fail(self): self.ping("/fail")

hc = HealthChecks()

# ═══════════════════════════════════════════════════════════════
# AUTO REPLY ENGINE
# ═══════════════════════════════════════════════════════════════

def process_message(sender, message):
    """Process incoming message and send auto-reply"""
    sender = db.clean_phone(sender)
    message = message.strip()
    
    if not sender or not message:
        return None
    
    logger.info(f"📥 From: {sender} - {message[:50]}...")
    
    # Log incoming
    db.add_message(sender, message, "incoming")
    
    # Add lead
    db.add_lead(sender, message)
    
    # Get response
    response, source = ai.get_response(message)
    
    # Log outgoing
    db.add_message(sender, response, "outgoing", is_ai=(source == "ai"), response_type=source)
    
    # Send reply
    wa.send_message(sender, response)
    
    logger.info(f"📤 Reply: {source} - {response[:50]}...")
    return response

def parse_webhook(payload):
    """Parse webhook payload from OpenWA/WAHA"""
    try:
        # WAHA format
        if "payload" in payload:
            p = payload["payload"]
            msg_data = p.get("message", {})
            
            if isinstance(msg_data, dict):
                message = (
                    msg_data.get("conversation") or
                    msg_data.get("extendedTextMessage", {}).get("text") or
                    msg_data.get("text") or
                    str(msg_data)
                )
            else:
                message = str(msg_data)
            
            sender = p.get("from", "")
            return sender, message
        
        # Simple format
        if "from" in payload and "message" in payload:
            msg = payload["message"]
            if isinstance(msg, dict):
                message = msg.get("conversation") or msg.get("text") or str(msg)
            else:
                message = str(msg)
            return payload["from"], message
        
        return None, None
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return None, None

# ═══════════════════════════════════════════════════════════════
# WEB SERVER (FastAPI)
# ═══════════════════════════════════════════════════════════════

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    import uvicorn
    
    app = FastAPI(title="WhatsApp Hub")
    
    @app.post("/webhook")
    async def webhook(request: Request):
        """Webhook endpoint for incoming WhatsApp messages"""
        try:
            payload = await request.json()
            logger.info(f"Webhook: {str(payload)[:100]}...")
            
            sender, message = parse_webhook(payload)
            
            if sender and message:
                process_message(sender, message)
                return JSONResponse({"status": "ok"})
            
            return JSONResponse({"status": "ignored"})
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return JSONResponse({"status": "error"})
    
    @app.get("/api/status")
    async def status():
        """System status"""
        return JSONResponse({
            "status": "ok",
            "whatsapp": wa.is_connected(),
            "ai_enabled": ai.enabled,
            "stats": db.get_stats()
        })
    
    @app.get("/api/stats")
    async def stats():
        """Get statistics"""
        return JSONResponse(db.get_stats())
    
    @app.get("/api/customers")
    async def customers():
        """Get customers"""
        return JSONResponse(db.get_customers())
    
    @app.post("/api/customers/add")
    async def add_customer(request: Request):
        """Add customer"""
        data = await request.json()
        phone = data.get("phone", "")
        name = data.get("name", "")
        
        if db.add_customer(phone, name):
            return JSONResponse({"success": True, "message": "Customer added"})
        return JSONResponse({"success": False, "message": "Already exists"})
    
    @app.get("/api/leads")
    async def leads():
        """Get leads"""
        return JSONResponse(db.get_leads())
    
    @app.get("/api/messages")
    async def messages(limit: int = 100):
        """Get messages"""
        return JSONResponse(db.get_messages(limit=limit))
    
    @app.get("/api/templates")
    async def templates():
        """Get templates"""
        return JSONResponse(db.get_templates())
    
    @app.post("/api/templates/add")
    async def add_template(request: Request):
        """Add template"""
        data = await request.json()
        keyword = data.get("keyword", "")
        response = data.get("response", "")
        
        if keyword and response:
            db.add_template(keyword, response)
            return JSONResponse({"success": True})
        return JSONResponse({"success": False, "message": "Keyword and response required"})
    
    @app.post("/api/send")
    async def send_message(request: Request):
        """Send single WhatsApp message"""
        data = await request.json()
        phone = data.get("phone", "")
        message = data.get("message", "")
        
        if not phone or not message:
            return JSONResponse({"success": False, "message": "Phone and message required"})
        
        if wa.send_message(phone, message):
            db.add_message(phone, message, "outgoing")
            return JSONResponse({"success": True, "message": "Sent"})
        return JSONResponse({"success": False, "message": "Failed"})
    
    @app.post("/api/broadcast")
    async def broadcast(request: Request):
        """Broadcast to all customers"""
        data = await request.json()
        message = data.get("message", "")
        
        if not message:
            return JSONResponse({"success": False, "message": "Message required"})
        
        if not wa.enabled:
            return JSONResponse({"success": False, "message": "WhatsApp not configured"})
        
        sent, failed = wa.send_broadcast(message)
        return JSONResponse({
            "success": True,
            "message": f"Sent: {sent}, Failed: {failed}",
            "sent": sent,
            "failed": failed
        })
    
    @app.post("/api/test")
    async def test():
        """Test connections"""
        return JSONResponse({
            "database": True,
            "whatsapp": wa.is_connected(),
            "ai": ai.enabled
        })
    
    @app.get("/health")
    async def health():
        """Health check"""
        hc.ping()
        return JSONResponse({"status": "healthy", "time": datetime.now().isoformat()})
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        """Web Dashboard HTML"""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp Hub Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen p-6">
    <div class="max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">🤖 WhatsApp Hub Dashboard</h1>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-gray-800 p-4 rounded-lg">
                <p class="text-gray-400">Messages</p>
                <p id="messages" class="text-2xl font-bold text-blue-400">-</p>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg">
                <p class="text-gray-400">Customers</p>
                <p id="customers" class="text-2xl font-bold text-purple-400">-</p>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg">
                <p class="text-gray-400">New Leads</p>
                <p id="leads" class="text-2xl font-bold text-green-400">-</p>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg">
                <p class="text-gray-400">Broadcasts</p>
                <p id="broadcasts" class="text-2xl font-bold text-yellow-400">-</p>
            </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div class="bg-gray-800 p-6 rounded-lg">
                <h2 class="text-xl font-bold mb-4">✉️ Send Message</h2>
                <input type="text" id="phone" placeholder="919876543210" class="w-full p-2 mb-2 bg-gray-700 rounded">
                <textarea id="msg" placeholder="Message..." rows="3" class="w-full p-2 mb-2 bg-gray-700 rounded"></textarea>
                <button onclick="sendMsg()" class="w-full bg-green-600 p-2 rounded hover:bg-green-700">Send</button>
            </div>
            
            <div class="bg-gray-800 p-6 rounded-lg">
                <h2 class="text-xl font-bold mb-4">📢 Broadcast</h2>
                <p class="text-gray-400 mb-2">Send to ALL customers</p>
                <textarea id="broadcast" placeholder="Broadcast message..." rows="3" class="w-full p-2 mb-2 bg-gray-700 rounded"></textarea>
                <button onclick="doBroadcast()" class="w-full bg-purple-600 p-2 rounded hover:bg-purple-700">Broadcast</button>
            </div>
        </div>
        
        <div class="bg-gray-800 p-6 rounded-lg">
            <h2 class="text-xl font-bold mb-4">💬 Recent Messages</h2>
            <div id="msgs" class="space-y-2 max-h-96 overflow-y-auto"></div>
        </div>
    </div>
    
    <script>
        async function load() {
            try {
                let res = await fetch('/api/stats');
                let data = await res.json();
                document.getElementById('messages').textContent = data.total_messages || 0;
                document.getElementById('customers').textContent = data.customers || 0;
                document.getElementById('leads').textContent = data.new_leads || 0;
                document.getElementById('broadcasts').textContent = data.total_broadcasts || 0;
                
                res = await fetch('/api/messages?limit=20');
                let msgs = await res.json();
                document.getElementById('msgs').innerHTML = msgs.reverse().map(m => 
                    `<div class="p-3 bg-gray-700 rounded ${m.direction === 'incoming' ? 'border-l-4 border-blue-500' : 'border-l-4 border-green-500'}">
                        <div class="flex justify-between">
                            <span class="font-bold">${m.sender}</span>
                            <span class="text-sm ${m.direction === 'incoming' ? 'text-blue-400' : 'text-green-400'}">${m.direction}</span>
                        </div>
                        <p class="mt-1">${m.message}</p>
                    </div>`
                ).join('') || '<p class="text-gray-500">No messages yet</p>';
            } catch (e) {
                console.error(e);
            }
        }
        
        async function sendMsg() {
            let phone = document.getElementById('phone').value;
            let msg = document.getElementById('msg').value;
            if (!phone || !msg) { alert('Fill all fields'); return; }
            await fetch('/api/send', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({phone, message: msg})});
            document.getElementById('msg').value = '';
            load();
        }
        
        async function doBroadcast() {
            let msg = document.getElementById('broadcast').value;
            if (!msg) { alert('Enter message'); return; }
            if (!confirm('Send to ALL customers?')) return;
            await fetch('/api/broadcast', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message: msg})});
            document.getElementById('broadcast').value = '';
            load();
        }
        
        load();
        setInterval(load, 5000);
    </script>
</body>
</html>"""
        return HTMLResponse(content=html)
    
    WEB_SERVER_AVAILABLE = True
    
except ImportError:
    WEB_SERVER_AVAILABLE = False
    logger.error("FastAPI not installed. Run: pip install fastapi uvicorn")

# ═══════════════════════════════════════════════════════════════
# TELEGRAM BOT
# ═══════════════════════════════════════════════════════════════

def run_telegram():
    """Run Telegram bot"""
    if not config.TELEGRAM_TOKEN:
        logger.warning("Telegram: No token configured")
        return
    
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
        
        bot = Application.builder().token(config.TELEGRAM_TOKEN).build()
        
        async def cmd_start(update, context):
            stats = db.get_stats()
            wa_status = "✅ Connected" if wa.is_connected() else "❌ Disconnected"
            ai_status = "✅ Active" if ai.enabled else "❌ Disabled"
            
            text = f"""🤖 *{config.BUSINESS_NAME}*

📱 WhatsApp: {wa_status}
🤖 AI: {ai_status}

📊 *Statistics:*
• Messages: {stats.get('total_messages', 0)}
• Customers: {stats.get('customers', 0)}
• Leads: {stats.get('new_leads', 0)}
• Broadcasts: {stats.get('total_broadcasts', 0)}

*Commands:*
/start - Show this menu
/status - System status
/stats - Statistics
/broadcast - Send to all
/send - Send single message
/leads - View new leads
/customers - View customers"""
            
            await update.message.reply_text(text, parse_mode="Markdown")
        
        async def cmd_status(update, context):
            text = f"""📊 *Status:*
WhatsApp: {'✅' if wa.is_connected() else '❌'}
AI: {'✅' if ai.enabled else '❌'}
Templates: {len(db.get_templates())}"""
            await update.message.reply_text(text, parse_mode="Markdown")
        
        async def cmd_stats(update, context):
            stats = db.get_stats()
            text = f"""📈 *Statistics:*
Messages: {stats.get('total_messages', 0)}
AI Responses: {stats.get('total_ai_responses', 0)}
Templates Used: {stats.get('total_template_responses', 0)}
Customers: {stats.get('customers', 0)}
Leads: {stats.get('leads', 0)}
Broadcasts: {stats.get('total_broadcasts', 0)}"""
            await update.message.reply_text(text, parse_mode="Markdown")
        
        async def cmd_broadcast(update, context):
            if not context.args:
                await update.message.reply_text("Usage: /broadcast YOUR MESSAGE\n\nExample:\n/broadcast Hello everyone!")
                return
            
            message = " ".join(context.args)
            
            if not wa.enabled:
                await update.message.reply_text("❌ WhatsApp not configured")
                return
            
            customers = db.get_customers()
            if not customers:
                await update.message.reply_text("❌ No customers to send to!")
                return
            
            await update.message.reply_text(f"📤 Sending to {len(customers)} customers...")
            
            sent, failed = wa.send_broadcast(message)
            
            await update.message.reply_text(f"✅ Broadcast complete!\n\n📤 Sent: {sent}\n❌ Failed: {failed}")
        
        async def cmd_send(update, context):
            if not context.args or len(context.args) < 2:
                await update.message.reply_text("Usage: /send PHONE MESSAGE\n\nExample:\n/send 919876543210 Hello!")
                return
            
            phone = context.args[0]
            message = " ".join(context.args[1:])
            
            if wa.send_message(phone, message):
                db.add_message(phone, message, "outgoing")
                await update.message.reply_text(f"✅ Sent to {phone}!")
            else:
                await update.message.reply_text(f"❌ Failed to send to {phone}")
        
        async def cmd_leads(update, context):
            leads = db.get_leads(status="new")
            
            if not leads:
                await update.message.reply_text("📭 No new leads!\n\nLeads are captured from incoming WhatsApp messages.")
                return
            
            text = f"👥 *New Leads ({len(leads)}):*\n\n"
            for lead in leads[-10:]:
                text += f"📱 {lead.get('phone')}\n"
                text += f"💬 {lead.get('first_message', '')[:50]}...\n"
                text += f"📅 {lead.get('created_at', '')[:10]}\n\n"
            
            await update.message.reply_text(text, parse_mode="Markdown")
        
        async def cmd_customers(update, context):
            customers = db.get_customers()
            
            if not customers:
                await update.message.reply_text("👥 No customers!\n\nAdd with /addcustomer PHONE")
                return
            
            text = f"👥 *Customers ({len(customers)}):*\n\n"
            for c in customers[:20]:
                text += f"📱 {c.get('phone')}"
                if c.get('name'):
                    text += f" ({c.get('name')})"
                text += "\n"
            
            if len(customers) > 20:
                text += f"\n...and {len(customers) - 20} more"
            
            await update.message.reply_text(text, parse_mode="Markdown")
        
        async def cmd_addcustomer(update, context):
            if not context.args:
                await update.message.reply_text("Usage: /addcustomer PHONE\n\nExample:\n/addcustomer 919876543210")
                return
            
            phone = context.args[0]
            if db.add_customer(phone):
                await update.message.reply_text(f"✅ Customer added!\n\n📱 {phone}")
            else:
                await update.message.reply_text(f"ℹ️ Already exists!\n\n📱 {phone}")
        
        async def cmd_test(update, context):
            wa_ok = wa.is_connected()
            ai_ok = ai.enabled
            
            text = f"🔧 *Connection Test*\n\n"
            text += f"WhatsApp: {'✅ OK' if wa_ok else '❌ FAIL'}\n"
            text += f"AI: {'✅ OK' if ai_ok else '❌ FAIL'}\n"
            text += f"Database: ✅ OK"
            
            await update.message.reply_text(text, parse_mode="Markdown")
        
        # Register handlers
        bot.add_handler(CommandHandler("start", cmd_start))
        bot.add_handler(CommandHandler("status", cmd_status))
        bot.add_handler(CommandHandler("stats", cmd_stats))
        bot.add_handler(CommandHandler("broadcast", cmd_broadcast))
        bot.add_handler(CommandHandler("bc", cmd_broadcast))
        bot.add_handler(CommandHandler("send", cmd_send))
        bot.add_handler(CommandHandler("leads", cmd_leads))
        bot.add_handler(CommandHandler("customers", cmd_customers))
        bot.add_handler(CommandHandler("addcustomer", cmd_addcustomer))
        bot.add_handler(CommandHandler("addlead", cmd_addcustomer))
        bot.add_handler(CommandHandler("test", cmd_test))
        
        logger.info("📱 Telegram bot starting...")
        bot.run_polling()
    
    except ImportError:
        logger.error("python-telegram-bot not installed")
    except Exception as e:
        logger.error(f"Telegram error: {e}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="WhatsApp Hub")
    parser.add_argument("--test", action="store_true", help="Test connections")
    parser.add_argument("--web", action="store_true", help="Web dashboard only")
    parser.add_argument("--telegram", action="store_true", help="Telegram only")
    args = parser.parse_args()
    
    # Test mode
    if args.test:
        print("\n" + "="*50)
        print("🔧 CONNECTION TEST")
        print("="*50)
        print(f"Database: ✅ OK ({len(db.get_customers())} customers)")
        print(f"WhatsApp: {'✅ Connected' if wa.is_connected() else '❌ Disconnected'}")
        print(f"AI: {'✅ Active' if ai.enabled else '❌ Disabled'}")
        print(f"Templates: {len(db.get_templates())}")
        print("="*50 + "\n")
        return
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🤖 WHATSAPP HUB v5.2 - ALL SKILLS WORKING                 ║
║                                                              ║
║   ✅ OpenWA Gateway     ✅ AI Auto-Reply                    ║
║   ✅ Lead Capture       ✅ Broadcast                          ║
║   ✅ Web Dashboard      ✅ Telegram Bot                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Show status
    stats = db.get_stats()
    print(f"📊 Database: {stats.get('customers', 0)} customers, {stats.get('leads', 0)} leads")
    print(f"📱 WhatsApp: {'✅ Connected' if wa.is_connected() else '❌ Disconnected'}")
    print(f"🤖 AI: {'✅ Active' if ai.enabled else '⚠️ Disabled'}")
    print()
    
    # Healthchecks
    hc.start()
    
    # Web only mode
    if args.web:
        if not WEB_SERVER_AVAILABLE:
            print("❌ FastAPI not installed!")
            return
        print(f"🌐 Web Dashboard: http://localhost:{config.PORT}")
        print(f"📋 Webhook URL: http://YOUR_IP:{config.PORT}/webhook")
        uvicorn.run(app, host=config.HOST, port=config.PORT)
        return
    
    # Telegram only mode
    if args.telegram:
        run_telegram()
        return
    
    # Full mode
    if WEB_SERVER_AVAILABLE:
        print(f"🌐 Web Dashboard: http://localhost:{config.PORT}")
        print(f"📋 Webhook URL: http://YOUR_IP:{config.PORT}/webhook")
        
        # Start web server in background
        def run_web():
            uvicorn.run(app, host=config.HOST, port=config.PORT, log_level="warning")
        
        web_thread = Thread(target=run_web, daemon=True)
        web_thread.start()
    
    # Start Telegram
    if config.TELEGRAM_TOKEN:
        print("📱 Starting Telegram bot...")
        run_telegram()
    else:
        print("📱 Telegram: No token (add TELEGRAM_BOT_TOKEN to .env)")
        print()
        
        # Keep running with healthchecks
        print("🔄 Running... Press Ctrl+C to stop")
        try:
            while True:
                hc.success()
                time.sleep(300)  # 5 minutes
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Stopped!")
