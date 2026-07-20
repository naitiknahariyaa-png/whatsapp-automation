#!/usr/bin/env python3
"""
WhatsApp Automation Hub v5.2 - Web Dashboard
All functions: Auto-reply, Broadcast, Lead Generation
"""

import os
import json
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OPENWA_URL = os.getenv("OPENWA_URL", "http://localhost:3000")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "")
OPENWA_SESSION = os.getenv("OPENWA_SESSION_ID", "default")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "WhatsApp Bot")
PORT = int(os.getenv("PORT", "8000"))

class Database:
    def __init__(self, db_file="data/bot_database.json"):
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.data = self._load()
    
    def _load(self):
        if self.db_file.exists():
            try: return json.loads(self.db_file.read_text())
            except: pass
        return {
            "customers": [], "leads": [], "orders": [],
            "templates": {
                "hi": "Hello! Welcome to {b}! How can I help?",
                "hello": "Hi there! How may I assist you?",
                "price": "Our prices are competitive!",
                "order": "Great! Tell me: 1) Name, 2) Items, 3) Address",
                "delivery": "Yes! We deliver all over India. 2-5 days.",
                "hours": "Open 9 AM - 9 PM, all days!",
            },
            "messages": [],
            "stats": {"total_messages": 0, "total_leads": 0, "total_broadcasts": 0}
        }
    
    def save(self):
        with self._lock: self.db_file.write_text(json.dumps(self.data, indent=2))
    
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
        if len(self.data["messages"]) > 1000: self.data["messages"] = self.data["messages"][-1000:]
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
                    messages=[{"role": "system", "content": f"Helpful for {BUSINESS_NAME}. SHORT responses."}, {"role": "user", "content": message}],
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

app = FastAPI(title="WhatsApp Hub")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()
        payload = body.get("payload", {})
        msg = payload.get("message", {})
        conversation = msg.get("conversation") or msg.get("extendedTextMessage", {}).get("text", "") or str(msg)
        from_id = payload.get("from", "")
        if not conversation or not from_id: return {"status": "ignored"}
        sender = db._clean(from_id)
        db.add_message(sender, conversation.strip(), "incoming")
        db.add_lead(sender, message=conversation.strip())
        response, _ = ai.get_response(conversation.strip())
        db.add_message(sender, response, "outgoing")
        wa.send(sender, response)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error"}

@app.get("/api/status")
async def status(): return {"connected": wa.is_connected(), "ai": ai.client is not None, "stats": db.get_stats()}

@app.get("/api/stats")
async def stats(): return db.get_stats()

@app.get("/api/customers")
async def customers(): return db.data["customers"]

@app.post("/api/customers/add")
async def add_customer(request: Request):
    data = await request.json()
    if db.add_customer(data.get("phone", ""), data.get("name", "")): return {"success": True}
    return {"success": False, "message": "Exists"}

@app.get("/api/leads")
async def leads(): return db.data["leads"]

@app.get("/api/messages")
async def messages(limit=100): return list(reversed(db.data["messages"][-limit:]))

@app.get("/api/templates")
async def templates(): return db.get_all_templates()

@app.post("/api/templates/add")
async def add_template(request: Request):
    data = await request.json()
    db.add_template(data.get("keyword", ""), data.get("response", ""))
    return {"success": True}

@app.post("/api/send")
async def send(request: Request):
    data = await request.json()
    phone, message = data.get("phone", ""), data.get("message", "")
    if wa.send(phone, message):
        db.add_message(phone, message, "outgoing")
        return {"success": True}
    return {"success": False}

@app.post("/api/broadcast")
async def broadcast(request: Request):
    data = await request.json()
    if not wa.is_connected(): return {"success": False, "message": "Not connected"}
    sent, failed = wa.broadcast(data.get("message", ""))
    db.data["stats"]["total_broadcasts"] += 1
    db.save()
    return {"success": True, "message": f"Sent: {sent}, Failed: {failed}", "sent": sent, "failed": failed}

@app.post("/api/test-ai")
async def test_ai(request: Request):
    data = await request.json()
    r, s = ai.get_response(data.get("message", ""))
    return {"response": r, "source": s}

@app.get("/health")
async def health(): return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = Path("website/index.html")
    if html_path.exists(): return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<h1>WhatsApp Hub</h1><p>Dashboard not found</p>")

def main():
    print(f"WhatsApp Hub v5.2 - WhatsApp: {'Connected' if wa.is_connected() else 'Not Connected'} - AI: {'Active' if ai.client else 'Disabled'} - Customers: {len(db.data['customers'])} - Dashboard: http://localhost:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")

if __name__ == "__main__": main()
