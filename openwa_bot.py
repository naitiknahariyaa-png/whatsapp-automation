#!/usr/bin/env python3
"""
🤖 WhatsApp Bot with OpenWA API
================================
Simple auto-reply bot using OpenWA API

Setup:
1. Start OpenWA: docker run -d --name openwa -p 3000:3000 waha/waha:latest
2. Run: pip install -r requirements.txt
3. Run: python openwa_bot.py
"""

import os
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

OPENWA_URL = os.getenv("OPENWA_URL", "http://localhost:3000")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


# ═══════════════════════════════════════════════════════════════
# OPENWA CLASS
# ═══════════════════════════════════════════════════════════════

class OpenWABot:
    """Simple OpenWA Bot"""
    
    def __init__(self):
        self.url = OPENWA_URL.rstrip('/')
        self.api_key = OPENWA_API_KEY
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"x-api-key": self.api_key})
    
    def is_connected(self):
        """Check if WhatsApp is connected"""
        try:
            r = self.session.get(f"{self.url}/api/connection", timeout=5)
            return r.status_code == 200
        except:
            return False
    
    def send_message(self, phone, text):
        """Send message"""
        try:
            data = {"phone": phone, "message": text}
            r = self.session.post(f"{self.url}/api/sendText", json=data, timeout=30)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    def get_messages(self, limit=10):
        """Get recent messages"""
        try:
            r = self.session.get(f"{self.url}/api/messages", params={"limit": limit}, timeout=10)
            if r.status_code == 200:
                return r.json()
            return []
        except:
            return []


# ═══════════════════════════════════════════════════════════════
# AI RESPONSE
# ═══════════════════════════════════════════════════════════════

def get_ai_response(message):
    """Get AI response using Groq"""
    if not GROQ_API_KEY:
        return "AI not configured. Set GROQ_API_KEY in .env"
    
    try:
        import requests
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": message}]
        }
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=data, timeout=30
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return "AI error"
    except Exception as e:
        logger.error(f"AI error: {e}")
        return "AI error"


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🤖 WhatsApp Bot (OpenWA)                             ║
║                                                               ║
║     Auto-reply using AI                                    ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize bot
    bot = OpenWABot()
    
    # Check connection
    print("\n🔍 Checking OpenWA connection...")
    
    if not bot.is_connected():
        print("❌ OpenWA not connected!")
        print("""
📱 SETUP STEPS:

1. Start OpenWA container:
   docker run -d --name openwa -p 3000:3000 waha/waha:latest

2. Wait 2-5 minutes for download

3. Open browser: http://localhost:3000

4. Click "Connect" and scan QR code

5. Get API key from Settings

6. Add to .env:
   OPENWA_URL=http://localhost:3000
   OPENWA_API_KEY=your-key
   GROQ_API_KEY=your-groq-key
        """)
        return
    
    print("✅ OpenWA connected!")
    
    # Check AI
    if GROQ_API_KEY:
        print("✅ AI (Groq) configured!")
    else:
        print("⚠️ AI not configured. Add GROQ_API_KEY to .env")
    
    print("\n🚀 Bot is running!")
    print("📱 Listening for messages...")
    print("(Press Ctrl+C to stop)\n")
    
    last_msg_id = None
    
    while True:
        try:
            messages = bot.get_messages(limit=5)
            
            for msg in messages:
                msg_id = msg.get("id", "")
                
                if msg_id == last_msg_id:
                    continue
                
                last_msg_id = msg_id
                
                # Skip outgoing
                if msg.get("fromMe"):
                    continue
                
                # Get message
                text = msg.get("body", "")
                chat = msg.get("chat", {})
                sender = chat.get("id", {}).get("remote", "unknown")
                
                if not text:
                    continue
                
                print(f"\n📩 From: {sender}")
                print(f"   Message: {text[:50]}")
                
                # Get AI response
                response = get_ai_response(text)
                
                # Send reply
                if bot.send_message(sender, response):
                    print(f"   ✅ Replied: {response[:50]}")
                else:
                    print(f"   ❌ Failed to send")
            
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n\n👋 Bot stopped!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
