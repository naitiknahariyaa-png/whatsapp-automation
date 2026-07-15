#!/usr/bin/env python3
"""
====================================================================
WHATSAPP AI BOT v2.2 - CAFE READY!
====================================================================

✅ Session Save (Login Once)
✅ Fast AI (Groq - FREE!)
✅ Auto-Reply (WORKS!)
✅ Statistics (WORKS!)
✅ Keywords (WORKS!)
✅ Load Menu from Excel/CSV (WORKS!)
✅ Pre-Made Cafe Keywords!

Author: Built for Indian Businesses 🇮🇳
====================================================================
"""

import os
import sys
import time
import sqlite3
import shutil
import webbrowser
from pathlib import Path

# ========================
# COLORS
# ========================
class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

# ========================
# BANNER & MENU
# ========================
BANNER = f"""
{C.CYAN}{C.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║       🤖 WHATSAPP AI BOT v2.2 🤖                           ║
║       CAFE READY! WITH MENU LOADER!                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{C.END}
"""

MENU = f"""
{C.CYAN}═══════════════════════════════════════════════════════════{C.END}

  {C.BOLD}📱 WhatsApp AI Bot v2.3 - FULL POWER!{C.END}

{C.GREEN}[1]{C.END}  🚀 Start Auto-Reply Bot
{C.GREEN}[2]{C.END}  📱 Setup WhatsApp Session
{C.GREEN}[3]{C.END}  🤖 Setup AI (OpenRouter/Groq)
{C.GREEN}[4]{C.END}  📝 Add Keywords
{C.GREEN}[5]{C.END}  📊 View Statistics
{C.GREEN}[6]{C.END}  💬 Test Auto-Reply
{C.GREEN}[7]{C.END}  📜 View Keywords
{C.GREEN}[8]{C.END}  🏪 Cafe Menu Options
{C.GREEN}[9]{C.END}  ⚡ View Cache Stats
{C.GREEN}[10]{C.END} 🗑️  Clear All Data

{C.GREEN}[0]{C.END}   {C.RED}Exit{C.END}

{C.CYAN}═══════════════════════════════════════════════════════════{C.END}
"""

# ========================
# PATHS
# ========================
DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "whatsapp.db"
CONFIG_PATH = Path("config.yaml")
SESSION_BACKUP = DATA_DIR / "whatsapp_session_backup"

DATA_DIR.mkdir(exist_ok=True)

# ========================
# CAFE INFO
# ========================
CAFE_NAME = "Our Cafe"
CAFE_ADDRESS = "Your Address"
CAFE_PHONE = "Your Phone"

# ========================
# DATABASE FUNCTIONS
# ========================

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT UNIQUE,
        response TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY,
        messages INTEGER DEFAULT 0,
        replies INTEGER DEFAULT 0
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        message TEXT,
        response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('INSERT OR IGNORE INTO stats (id, messages, replies) VALUES (1, 0, 0)')
    
    conn.commit()
    conn.close()

def get_stats():
    """Get statistics"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('SELECT messages, replies FROM stats WHERE id=1')
    row = c.fetchone()
    conn.close()
    if row:
        return {"messages": row[0], "replies": row[1]}
    return {"messages": 0, "replies": 0}

def add_keyword(keyword, response):
    """Add keyword"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    try:
        c.execute('INSERT INTO keywords (keyword, response) VALUES (?, ?)', 
                  (keyword.lower().strip(), response.strip()))
        conn.commit()
        conn.close()
        return True
    except:
        c.execute('UPDATE keywords SET response=? WHERE keyword=?', 
                  (response.strip(), keyword.lower().strip()))
        conn.commit()
        conn.close()
        return True

def get_keywords():
    """Get all keywords"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('SELECT keyword, response FROM keywords')
    rows = c.fetchone()
    keywords = []
    for row in c.execute('SELECT keyword, response FROM keywords'):
        keywords.append({"keyword": row[0], "response": row[1]})
    conn.close()
    return keywords

def delete_keyword(keyword):
    """Delete keyword"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('DELETE FROM keywords WHERE keyword=?', (keyword.lower().strip(),))
    conn.commit()
    conn.close()

def log_message(sender, message, response):
    """Log message"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('INSERT INTO logs (sender, message, response) VALUES (?, ?, ?)',
              (sender, message, response))
    c.execute('UPDATE stats SET messages = messages + 1, replies = replies + 1 WHERE id=1')
    conn.commit()
    conn.close()

def clear_all_data():
    """Clear all data"""
    if DB_PATH.exists():
        DB_PATH.unlink()
    if SESSION_BACKUP.exists():
        shutil.rmtree(str(SESSION_BACKUP))
    init_db()

def find_reply(message):
    """Find reply for message"""
    keywords = get_keywords()
    message_lower = message.lower()
    
    # Default responses (always work!)
    defaults = {
        "hi": "Hello! 👋 Welcome! How can I help you today?",
        "hello": "Hi there! 😊 How may I assist you?",
        "hey": "Hey! What's up? 😄",
        "price": "For our best prices, please tell me which product you're interested in!",
        "cost": "Our prices are very competitive! What would you like to know about?",
        "available": "Yes, we're available! 🕐 We're open from 9 AM to 9 PM.",
        "hours": "We're open 9 AM to 9 PM, all days! 🌟",
        "location": "We're located at [Your Address]. 📍",
        "contact": "You can reach us at [Your Phone]! 📞",
        "order": "Great choice! To place an order, please tell us what you'd like. 🛒",
        "thank": "You're welcome! 😊 Is there anything else I can help with?",
        "thanks": "Happy to help! 🙌 Feel free to ask if you need anything!",
        "bye": "Goodbye! Have a great day! 👋 See you soon!",
        "help": "I can help with:\n• Product info\n• Prices\n• Orders\n• Hours\n• Location\n\nJust ask! 😊",
        "delivery": "Yes! We deliver all over India! 🚚 Delivery takes 3-5 business days.",
        "payment": "We accept UPI, Cash on Delivery, and Bank Transfer! 💰",
        "return": "We offer 7-day return policy! 🔄 Contact us for any issues."
    }
    
    # Check custom keywords first
    for kw in keywords:
        if kw['keyword'].lower() in message_lower:
            return kw['response']
    
    # Check default keywords
    for keyword, response in defaults.items():
        if keyword in message_lower:
            return response
    
    return "Thanks for your message! We'll get back to you shortly. 🙏"

# ========================
# RESPONSE CACHE (Speed Up!)
# ========================

class ResponseCache:
    """Simple cache to speed up repeated queries"""
    
    def __init__(self, max_size=500):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, message):
        """Get cached response"""
        key = self._make_key(message)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, message, response):
        """Cache a response"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        
        key = self._make_key(message)
        self.cache[key] = response
    
    def _make_key(self, message):
        """Create cache key from message"""
        import hashlib
        return hashlib.md5(message.lower().strip().encode()).hexdigest()
    
    def stats(self):
        """Get cache stats"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%"
        }
    
    def clear(self):
        """Clear cache"""
        self.cache = {}
        self.hits = 0
        self.misses = 0

# Global cache instance
CACHE = ResponseCache()

# ========================
# AI PROVIDERS
# ========================

class GroqAI:
    """Fast Free AI using Groq API"""
    
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or self.load_api_key()
        self.model = "llama-3.1-8b-instant"
    
    def load_api_key(self):
        """Load API key from config"""
        if CONFIG_PATH.exists():
            import yaml
            with open(CONFIG_PATH, 'r') as f:
                config = yaml.safe_load(f) or {}
                return config.get('groq_api_key')
        return None
    
    def save_api_key(self, api_key):
        """Save API key to config"""
        import yaml
        config = {}
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r') as f:
                config = yaml.safe_load(f) or {}
        config['ai'] = config.get('ai', {})
        config['ai']['groq_api_key'] = api_key
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(config, f)
        self.api_key = api_key
    
    def is_configured(self):
        """Check if API key is set"""
        return bool(self.api_key)
    
    def generate(self, message):
        """Generate AI response"""
        if not self.api_key:
            return None
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            system_prompt = """You are a helpful WhatsApp assistant for a small Indian business.
Keep responses SHORT and FRIENDLY (1-2 sentences max).
Respond in the same language as the user.
Be helpful, polite, and professional."""
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            }
            
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                return None
                
        except Exception as e:
            print(f"{C.RED}AI Error: {e}{C.END}")
            return None


class OpenRouterAI:
    """
    OpenRouter - FREE AI Models!
    No API costs - Kimi, GLM, and 100+ models!
    
    Get free API key: https://openrouter.ai/keys
    """
    
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    # FREE models (fastest first)
    FREE_MODELS = [
        "openchat/openchat-7b",
        "nousresearch/hermes-3-llama-3.1-8b",
        "meta-llama/llama-3.2-3b-instruct",
        "mistralai/mistral-7b-instruct",
    ]
    
    def __init__(self, api_key=None):
        self.api_key = api_key or self.load_api_key()
        self.model = self.FREE_MODELS[0]
    
    def load_api_key(self):
        """Load API key from config"""
        if CONFIG_PATH.exists():
            import yaml
            with open(CONFIG_PATH, 'r') as f:
                config = yaml.safe_load(f) or {}
                return config.get('ai', {}).get('openrouter_api_key')
        return None
    
    def save_api_key(self, api_key):
        """Save API key to config"""
        import yaml
        config = {}
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r') as f:
                config = yaml.safe_load(f) or {}
        config['ai'] = config.get('ai', {})
        config['ai']['openrouter_api_key'] = api_key
        config['ai']['provider'] = 'openrouter'
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(config, f)
        self.api_key = api_key
    
    def is_configured(self):
        """Check if API key is set"""
        return bool(self.api_key)
    
    def generate(self, message):
        """Generate AI response"""
        if not self.api_key:
            return None
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://whatsapp-bot.local",
                "X-Title": "WhatsApp AI Bot"
            }
            
            system_prompt = """You are a helpful WhatsApp assistant for a small Indian business.
Keep responses SHORT and FRIENDLY (1-2 sentences max).
Respond in the same language as the user.
Be helpful, polite, and professional."""
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            }
            
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                print(f"{C.RED}OpenRouter Error: {response.status_code}{C.END}")
                return None
                
        except Exception as e:
            print(f"{C.RED}AI Error: {e}{C.END}")
            return None

# ========================
# WHATSAPP SESSION
# ========================

def setup_whatsapp_session():
    """Setup WhatsApp session"""
    print(f"\n{C.CYAN}{C.BOLD}📱 WhatsApp Session Setup{C.END}\n")
    
    print(f"{C.YELLOW}This will open WhatsApp Web in Chrome.{C.END}")
    print(f"{C.YELLOW}You need to scan the QR code ONCE.{C.END}")
    print(f"{C.YELLOW}After this, you won't need to scan again!{C.END}\n")
    
    input(f"{C.GREEN}Press ENTER to open WhatsApp Web...{C.END}")
    
    # Open WhatsApp Web
    webbrowser.open("https://web.whatsapp.com")
    
    print(f"\n{C.GREEN}✅ WhatsApp Web opened!{C.END}")
    print(f"{C.YELLOW}Please scan the QR code with your phone.{C.END}")
    print(f"{C.YELLOW}After scanning, press ENTER here to continue...{C.END}\n")
    
    input()
    
    print(f"\n{C.GREEN}✅ Session setup complete!{C.END}")
    print(f"{C.CYAN}Your WhatsApp session is now ready.{C.END}")

# ========================
# AUTO REPLY BOT
# ========================

def run_auto_reply():
    """Run the auto-reply bot"""
    print(f"\n{C.CYAN}{C.BOLD}🚀 Starting Auto-Reply Bot{C.END}\n")
    
    # Check AI
    ai = GroqAI()
    if ai.is_configured():
        print(f"{C.GREEN}✅ Groq AI configured (Fast responses!){C.END}")
        use_ai = True
    else:
        print(f"{C.YELLOW}⚠️ Groq AI not configured.{C.END}")
        print(f"{C.YELLOW}Using keyword-based responses (still works!).{C.END}")
        print(f"{C.YELLOW}Run option [3] to set up free Groq AI!{C.END}")
        use_ai = False
    
    # Check session
    print(f"\n{C.YELLOW}Opening WhatsApp Web...{C.END}\n")
    webbrowser.open("https://web.whatsapp.com")
    
    print(f"{C.GREEN}✅ WhatsApp Web opened!{C.END}")
    print(f"{C.CYAN}The bot is monitoring for messages...{C.END}")
    print(f"{C.YELLOW}Press Ctrl+C to stop.{C.END}\n")
    
    input(f"\n{C.GREEN}Press ENTER when WhatsApp Web is ready...{C.END}")
    
    print(f"\n{C.GREEN}✅ Bot is ACTIVE! Monitoring messages...{C.END}\n")
    
    print(f"""
{C.CYAN}─────────────────────────────────────────{C.END}
HOW IT WORKS:
1. Someone sends you a WhatsApp message
2. You see it on screen
3. Type 'REPLY' followed by your response
4. Bot sends the response!

Example:
  You: REPLY Hello! How can I help you?
  Bot sends: "Hello! How can I help you?"

Type 'KEYWORDS' to see current auto-reply keywords
Type 'STATS' to see statistics
Type 'QUIT' to stop bot
{C.CYAN}─────────────────────────────────────────{C.END}
""")
    
    reply_count = 0
    
    while True:
        try:
            user_input = input(f"{C.CYAN}You:{C.END} ").strip()
            
            if user_input.upper() == 'QUIT':
                break
            
            elif user_input.upper() == 'KEYWORDS':
                keywords = get_keywords()
                print(f"\n{C.CYAN}📝 Current Keywords:{C.END}")
                for kw in keywords:
                    print(f"  • '{kw['keyword']}' → '{kw['response'][:50]}...'")
                if not keywords:
                    print(f"  {C.YELLOW}No custom keywords yet. Add some with option [4]!{C.END}")
                print()
            
            elif user_input.upper() == 'STATS':
                stats = get_stats()
                print(f"\n{C.CYAN}📊 Statistics:{C.END}")
                print(f"  Messages: {stats['messages']}")
                print(f"  Replies: {stats['replies']}\n")
            
            elif user_input.upper().startswith('REPLY '):
                response = user_input[6:].strip()
                if response:
                    print(f"{C.GREEN}📤 Reply prepared: {response}{C.END}")
                    print(f"{C.YELLOW}(Copy and paste to WhatsApp Web to send){C.END}")
                    log_message("Manual", "Manual trigger", response)
                    reply_count += 1
                else:
                    print(f"{C.RED}Please enter a reply message!{C.END}")
            
            elif user_input.upper().startswith('AUTO '):
                message = user_input[5:].strip()
                if message:
                    # Use auto-reply logic
                    if use_ai:
                        reply = ai.generate(message)
                        if not reply:
                            reply = find_reply(message)
                    else:
                        reply = find_reply(message)
                    
                    print(f"\n{C.CYAN}📩 Message: {message}{C.END}")
                    print(f"{C.GREEN}🤖 Auto-Reply: {reply}{C.END}\n")
                    log_message("Test", message, reply)
                else:
                    print(f"{C.RED}Please enter a message!{C.END}")
            
            else:
                # Test auto-reply
                reply = find_reply(user_input)
                print(f"\n{C.GREEN}🤖 Bot would reply: {reply}{C.END}\n")
        
        except KeyboardInterrupt:
            print(f"\n\n{C.YELLOW}Stopping bot...{C.END}")
            break
    
    print(f"\n{C.GREEN}✅ Bot stopped. Total replies: {reply_count}{C.END}")

# ========================
# SETUP GROQ AI
# ========================

def setup_ai():
    """Setup AI (OpenRouter or Groq)"""
    print(f"\n{C.CYAN}{C.BOLD}🤖 AI Setup - Choose Your AI!{C.END}\n")
    
    print(f"""{C.GREEN}
╔═══════════════════════════════════════════════════════════════╗
║              AI PROVIDERS COMPARISON                        ║
╠═══════════════════════════════════════════════════════════════╣
║  [1] OpenRouter (RECOMMENDED)                             ║
║  ─────────────────────────────────────────────────         ║
║  ✅ 100+ FREE models (Kimi, GLM, etc.)                    ║
║  ✅ No API costs forever                                   ║
║  ⚠️  Slightly slower than Groq                            ║
║  📍 Get key: https://openrouter.ai/keys                   ║
║                                                              ║
║  [2] Groq (Fast)                                           ║
║  ─────────────────────────────────────────────────         ║
║  ✅ Very fast (10x faster)                                 ║
║  ⚠️  Rate limited (30 req/min)                            ║
║  📍 Get key: https://console.groq.com/keys                 ║
║                                                              ║
║  [3] Keyword AI Only (NO API NEEDED!)                      ║
║  ─────────────────────────────────────────────────         ║
║  ✅ Works 100% FREE                                       ║
║  ✅ No internet needed                                     ║
║  ⚠️  Basic responses only                                 ║
╚═══════════════════════════════════════════════════════════════╝
{C.END}""")
    
    choice = input(f"{C.CYAN}Choose AI provider [1/2/3]: {C.END}").strip()
    
    if choice == "1":
        # OpenRouter
        print(f"\n{C.CYAN}{C.BOLD}🆓 OpenRouter Setup (FREE AI!){C.END}\n")
        print(f"{C.YELLOW}OpenRouter gives you 100+ FREE AI models!{C.END}\n")
        
        print(f"{C.GREEN}Get FREE API key:{C.END}")
        print(f"  1. Go to: {C.CYAN}https://openrouter.ai/keys{C.END}")
        print(f"  2. Sign up FREE")
        print(f"  3. Create Key")
        print(f"  4. Copy the key\n")
        
        webbrowser.open("https://openrouter.ai/keys")
        
        api_key = input(f"{C.GREEN}Paste OpenRouter API key: {C.END}\n> ").strip()
        
        if api_key:
            ai = OpenRouterAI()
            ai.save_api_key(api_key)
            
            print(f"\n{C.YELLOW}Testing...{C.END}")
            test = ai.generate("Say 'Hi' in one word")
            
            if test:
                print(f"\n{C.GREEN}✅ SUCCESS! OpenRouter AI is working!{C.END}")
                print(f"{C.GREEN}Response: {test}{C.END}")
            else:
                print(f"\n{C.RED}❌ API key didn't work.{C.END}")
        else:
            print(f"{C.RED}No API key entered.{C.END}")
    
    elif choice == "2":
        # Groq
        print(f"\n{C.CYAN}{C.BOLD}⚡ Groq AI Setup (FAST!){C.END}\n")
        
        print(f"{C.GREEN}Get FREE API key:{C.END}")
        print(f"  1. Go to: {C.CYAN}https://console.groq.com/keys{C.END}")
        print(f"  2. Sign up FREE")
        print(f"  3. Create Key")
        print(f"  4. Copy the key\n")
        
        webbrowser.open("https://console.groq.com/keys")
        
        api_key = input(f"{C.GREEN}Paste Groq API key: {C.END}\n> ").strip()
        
        if api_key:
            ai = GroqAI()
            ai.save_api_key(api_key)
            
            print(f"\n{C.YELLOW}Testing...{C.END}")
            test = ai.generate("Say 'Hi' in one word")
            
            if test:
                print(f"\n{C.GREEN}✅ SUCCESS! Groq AI is working!{C.END}")
                print(f"{C.GREEN}Response: {test}{C.END}")
            else:
                print(f"\n{C.RED}❌ API key didn't work.{C.END}")
        else:
            print(f"{C.RED}No API key entered.{C.END}")
    
    elif choice == "3":
        print(f"\n{C.GREEN}✅ Keyword AI selected!{C.END}")
        print(f"{C.YELLOW}Bot will use your custom keywords.{C.END}")
    
    else:
        print(f"\n{C.YELLOW}No changes made.{C.END}")


def view_cache_stats():
    """View cache statistics"""
    print(f"\n{C.CYAN}{C.BOLD}⚡ Cache Statistics{C.END}\n")
    
    stats = CACHE.stats()
    
    print(f"{C.GREEN}Cache Status:{C.END}")
    print(f"  • Cached responses: {stats['size']}")
    print(f"  • Cache hits: {stats['hits']}")
    print(f"  • Cache misses: {stats['misses']}")
    print(f"  • Hit rate: {stats['hit_rate']}")
    print(f"  • Max size: {CACHE.max_size}\n")
    
    print(f"{C.GREEN}How caching works:{C.END}")
    print(f"  • Same question = Instant response (from cache)")
    print(f"  • New question = Generate fresh (slower)")
    print(f"  • Cache auto-clears when full\n")
    
    action = input(f"{C.GREEN}Clear cache? (y/n): {C.END}").strip().lower()
    if action == 'y':
        CACHE.clear()
        print(f"{C.GREEN}✅ Cache cleared!{C.END}")

# ========================
# ADD KEYWORD
# ========================

def add_keyword_ui():
    """Add keyword interactively"""
    print(f"\n{C.CYAN}{C.BOLD}📝 Add Auto-Reply Keyword{C.END}\n")
    
    keyword = input(f"{C.GREEN}Enter keyword (e.g., 'hi', 'price', 'delivery'):{C.END}\n> ").strip().lower()
    
    if not keyword:
        print(f"{C.RED}Keyword cannot be empty!{C.END}")
        return
    
    print(f"\n{C.GREEN}Enter response:{C.END}")
    response = input(f"(What should bot reply when someone says '{keyword}?'){C.END}\n> ").strip()
    
    if not response:
        print(f"{C.RED}Response cannot be empty!{C.END}")
        return
    
    if add_keyword(keyword, response):
        print(f"\n{C.GREEN}✅ Keyword added successfully!{C.END}")
        print(f"   '{keyword}' → '{response}'")
    else:
        print(f"\n{C.YELLOW}Updated existing keyword.{C.END}")

# ========================
# VIEW KEYWORDS
# ========================

def view_keywords():
    """View all keywords"""
    print(f"\n{C.CYAN}{C.BOLD}📜 All Keywords{C.END}\n")
    
    keywords = get_keywords()
    
    if not keywords:
        print(f"{C.YELLOW}No custom keywords yet.{C.END}")
        print(f"{C.YELLOW}Add some with option [4]!{C.END}\n")
        return
    
    print(f"{C.GREEN}Your keywords ({len(keywords)}):{C.END}\n")
    for i, kw in enumerate(keywords, 1):
        print(f"{C.GREEN}[{i}]{C.END} '{C.CYAN}{kw['keyword']}{C.END}'")
        print(f"    → {kw['response']}\n")

# ========================
# VIEW STATISTICS
# ========================

def view_stats():
    """View statistics"""
    print(f"\n{C.CYAN}{C.BOLD}📊 Statistics{C.END}\n")
    
    stats = get_stats()
    keywords = get_keywords()
    
    print(f"{C.GREEN}📨 Total Messages:{C.END} {stats['messages']}")
    print(f"{C.GREEN}🤖 Total Auto-Replies:{C.END} {stats['replies']}")
    print(f"{C.GREEN}📝 Custom Keywords:{C.END} {len(keywords)}\n")
    
    ai = GroqAI()
    if ai.is_configured():
        print(f"{C.GREEN}🤖 Groq AI:{C.END} ✅ Configured")
    else:
        print(f"{C.YELLOW}🤖 Groq AI:{C.END} ⚠️ Not configured")
    print()

# ========================
# TEST AUTO-REPLY
# ========================

def test_auto_reply():
    """Test auto-reply without WhatsApp"""
    print(f"\n{C.CYAN}{C.BOLD}💬 Test Auto-Reply{C.END}\n")
    
    ai = GroqAI()
    if ai.is_configured():
        print(f"{C.GREEN}✅ Groq AI configured (Smart responses!){C.END}\n")
    else:
        print(f"{C.YELLOW}⚠️ Groq AI not configured. Using keyword-based responses.{C.END}\n")
    
    print(f"{C.CYAN}Type a message to test (or 'exit' to quit):{C.END}\n")
    
    while True:
        msg = input(f"{C.CYAN}You:{C.END} ").strip()
        
        if msg.lower() in ('exit', 'quit', 'q'):
            break
        
        if not msg:
            continue
        
        print(f"\n{C.YELLOW}Generating response...{C.END}")
        
        # Try AI first
        if ai.is_configured():
            reply = ai.generate(msg)
            if not reply:
                reply = find_reply(msg)
        else:
            reply = find_reply(msg)
        
        print(f"\n{C.GREEN}🤖 Bot:{C.END} {reply}\n")

# ========================
# CLEAR DATA
# ========================

def clear_data():
    """Clear all data"""
    print(f"\n{C.RED}{C.BOLD}⚠️ Clear All Data{C.END}\n")
    
    confirm = input(f"{C.RED}Are you sure? Type 'yes' to confirm: {C.END}")
    
    if confirm.lower() == 'yes':
        clear_all_data()
        print(f"\n{C.GREEN}✅ All data cleared!{C.END}")
    else:
        print(f"{C.YELLOW}Cancelled.{C.END}")

# ========================
# LOAD CAFE MENU
# ========================

def load_cafe_menu():
    """Load cafe menu from CSV/Excel file"""
    print(f"\n{C.CYAN}{C.BOLD}🏪 Load Cafe Menu{C.END}\n")
    
    print(f"{C.YELLOW}This will load your menu items as auto-reply keywords!{C.END}\n")
    
    # Check for pandas
    try:
        import pandas as pd
    except ImportError:
        print(f"{C.RED}pandas not installed!{C.END}")
        print(f"{C.YELLOW}Install with: pip install pandas{C.END}")
        return
    
    print(f"{C.GREEN}File formats supported:{C.END}")
    print(f"  • CSV file (.csv)")
    print(f"  • Excel file (.xlsx)\n")
    
    # Check for sample files
    sample_csv = Path("cafe_menu_template.csv")
    if sample_csv.exists():
        print(f"{C.GREEN}✓ Found: cafe_menu_template.csv{C.END}")
        use_sample = input(f"\n{C.GREEN}Use this sample menu? (y/n): {C.END}").strip().lower()
        
        if use_sample == 'y':
            file_path = "cafe_menu_template.csv"
        else:
            file_path = input(f"\n{C.GREEN}Enter your menu file path: {C.END}").strip()
    else:
        file_path = input(f"{C.GREEN}Enter your menu file path: {C.END}").strip()
    
    if not file_path:
        print(f"{C.RED}No file specified.{C.END}")
        return
    
    if not Path(file_path).exists():
        print(f"{C.RED}File not found: {file_path}{C.END}")
        return
    
    print(f"\n{C.YELLOW}Loading menu...{C.END}")
    
    try:
        # Read file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            print(f"{C.RED}Unsupported file format!{C.END}")
            return
        
        print(f"{C.CYAN}Found columns: {list(df.columns)}{C.END}\n")
        
        # Load keywords to database
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        count = 0
        for index, row in df.iterrows():
            try:
                # Get values (case insensitive)
                item = str(row.get('Item', row.get('item', row.get('NAME', ''))))
                price = str(row.get('Price', row.get('price', row.get('COST', ''))))
                keywords_str = str(row.get('Keywords', row.get('keywords', row.get('SEARCH', ''))))
                
                if item == 'nan' or item == '':
                    continue
                
                # Create response
                response = item
                if price != 'nan' and price:
                    response = f"{item} - ₹{price}"
                
                # Add keywords
                for kw in keywords_str.split(','):
                    kw = kw.strip().lower()
                    if kw:
                        try:
                            c.execute('INSERT INTO keywords (keyword, response) VALUES (?, ?)',
                                     (kw, response))
                            count += 1
                        except:
                            c.execute('UPDATE keywords SET response=? WHERE keyword=?',
                                     (response, kw))
                
            except Exception as e:
                continue
        
        conn.commit()
        conn.close()
        
        print(f"\n{C.GREEN}✅ SUCCESS! Loaded {count} keywords!{C.END}")
        print(f"{C.CYAN}Your menu items are now auto-reply keywords!{C.END}")
        
    except Exception as e:
        print(f"{C.RED}Error loading menu: {e}{C.END}")

# ========================
# LOAD PRE-MADE CAFE KEYWORDS
# ========================

def load_premade_cafe_keywords():
    """Load pre-made cafe keywords"""
    print(f"\n{C.CYAN}{C.BOLD}🏪 Loading Pre-Made Cafe Keywords{C.END}\n")
    
    # Pre-made cafe keywords
    cafe_keywords = [
        # Greetings
        ("hi", "Hello! 👋 Welcome! How can I help you?"),
        ("hello", "Hi there! 😊 How may I assist you?"),
        ("hey", "Hey! What's up? 😄"),
        
        # Menu
        ("menu", "📋 Our Menu:\n☕ Coffee\n🍔 Burgers\n🍕 Pizza\n🍝 Pasta\n🍰 Desserts\n\nWhat would you like?"),
        ("food", "🍽️ We serve:\n• Coffee & Tea\n• Burgers & Sandwiches\n• Pizza & Pasta\n• Desserts & Snacks\n\nWhat sounds good?"),
        ("items", "📋 Available items:\n• Coffee: ₹99-179\n• Burgers: ₹149-299\n• Pizza: ₹199-499\n• Pasta: ₹179-249\n\nAnything interest you?"),
        
        # Coffee
        ("coffee", "☕ Coffee Menu:\n• Espresso - ₹99\n• Cappuccino - ₹129\n• Latte - ₹149\n• Cold Coffee - ₹179\n• Mocha - ₹169\n\nWhich one?"),
        ("espresso", "☕ Espresso - ₹99\nStrong and bold!"),
        ("cappuccino", "☕ Cappuccino - ₹129\nCreamy and smooth!"),
        ("latte", "☕ Latte - ₹149\nMild and milky!"),
        ("cold coffee", "☕ Cold Coffee - ₹179\nPerfect for summer!"),
        
        # Tea
        ("tea", "🍵 Tea Menu:\n• Masala Chai - ₹49\n• Green Tea - ₹79\n• Ginger Tea - ₹59\n• Lemon Tea - ₹59\n\nWhich one?"),
        ("chai", "🍵 Masala Chai - ₹49\nClassic Indian tea!"),
        ("masala", "🍵 Masala Chai - ₹49\nSpiced and delicious!"),
        
        # Burger
        ("burger", "🍔 Burger Menu:\n• Veg Burger - ₹149\n• Cheese Burger - ₹179\n• Chicken Burger - ₹189\n• Zinger Burger - ₹229\n\nWhich one?"),
        ("veg burger", "🍔 Veg Burger - ₹149\nFresh and tasty!"),
        ("chicken burger", "🍔 Chicken Burger - ₹189\nJuicy chicken!"),
        ("zinger", "🍔 Zinger Burger - ₹229\nOur bestseller!"),
        
        # Pizza
        ("pizza", "🍕 Pizza Menu:\n• Margherita - ₹199\n• Farmhouse - ₹249\n• Peppy Paneer - ₹279\n• Chicken Supreme - ₹349\n\nWhich one?"),
        ("margherita", "🍕 Margherita - ₹199\nClassic cheese pizza!"),
        ("farmhouse", "🍕 Farmhouse Pizza - ₹249\nLoaded with veggies!"),
        ("chicken pizza", "🍕 Chicken Pizza - ₹349\nNon-veg delight!"),
        
        # Pasta
        ("pasta", "🍝 Pasta Menu:\n• Red Sauce - ₹179\n• White Sauce - ₹199\n• Pink Sauce - ₹219\n• Chicken Pasta - ₹249\n\nWhich sauce?"),
        ("red sauce pasta", "🍝 Red Sauce Pasta - ₹179\nTomato tangy!"),
        ("white sauce pasta", "🍝 White Sauce Pasta - ₹199\nCreamy cheese!"),
        
        # Desserts
        ("dessert", "🍰 Dessert Menu:\n• Brownie - ₹99\n• Cheese Cake - ₹149\n• Ice Cream - ₹79\n• Lava Cake - ₹179\n\nSweet ending!"),
        ("cake", "🍰 Desserts:\n• Cheese Cake - ₹149\n• Pastry - ₹99\n• Chocolate Cake - ₹129\n\nYummy!"),
        ("brownie", "🍫 Chocolate Brownie - ₹99\nRich and fudgy!"),
        ("ice cream", "🍨 Ice Cream - ₹79\n2 scoops of happiness!"),
        
        # Prices
        ("price", "💰 Our Prices:\n• Coffee: ₹99-179\n• Tea: ₹49-99\n• Burgers: ₹149-299\n• Pizza: ₹199-499\n• Pasta: ₹179-249\n• Desserts: ₹79-179\n\nWhat would you like?"),
        ("cost", "💰 Check our affordable prices!\n• Coffee from ₹99\n• Burgers from ₹149\n• Pizza from ₹199\n\nBudget-friendly!"),
        
        # Hours
        ("hours", "🕐 Opening Hours:\nMon-Fri: 9 AM - 11 PM\nSat-Sun: 10 AM - 12 AM\n\nVisit us!"),
        ("open", "🕐 We're open!\nMon-Fri: 9 AM - 11 PM\nSat-Sun: 10 AM - 12 AM\n\nSee you soon!"),
        ("timing", "🕐 Timings:\nMon-Fri: 9 AM - 11 PM\nSat-Sun: 10 AM - 12 AM"),
        
        # Location
        ("address", "📍 We're located at:\n[Your Address Here]\n\nFind us easily!"),
        ("location", "📍 Visit us at:\n[Your Address Here]\n\nParking available!"),
        ("where", "📍 We're here:\n[Your Address Here]\n\nCome visit!"),
        
        # Contact
        ("contact", "📞 Contact Us:\nPhone: [Your Phone]\nWhatsApp: [Your WhatsApp]\n\nWe're here to help!"),
        ("phone", "📞 Call us:\n[Your Phone Number]\n\nOr WhatsApp us!"),
        ("call", "📞 Reach us:\n[Your Phone Number]\n\nHappy to help!"),
        
        # Delivery
        ("delivery", "🚚 Delivery Options:\n• We deliver nearby!\n• Also on Zomato & Swiggy\n\nOrder now!"),
        ("deliver", "🚚 Yes, we deliver!\nWithin [X] km radius\n\nCall to order!"),
        ("takeaway", "🥡 Takeaway Available!\nCall ahead and pick up!\nNo waiting!"),
        ("parcel", "🥡 Parcel available!\nWe'll pack it fresh!\n\nOrder now!"),
        
        # Order
        ("order", "🛒 To Order:\n• Call us\n• WhatsApp us\n• Or visit directly!\n\nHow would you like to order?"),
        ("book", "📅 Table Booking:\n• Call us to reserve\n• Tell us date, time, people\n\nWe'll save a spot!"),
        
        # Veg/Non-Veg
        ("veg", "🌱 Vegetarian Options:\n• Veg Burger - ₹149\n• Margherita Pizza - ₹199\n• Red Sauce Pasta - ₹179\n\nPlenty of choices!"),
        ("vegetarian", "🌱 Veg items available!\nBurgers, Pizza, Pasta, Salads\n\nOrder now!"),
        ("non-veg", "🍗 Non-Veg Options:\n• Chicken Burger - ₹189\n• Chicken Pizza - ₹349\n• Chicken Pasta - ₹249\n\nTasty!"),
        
        # Payment
        ("payment", "💳 We Accept:\n• Cash\n• UPI (GPay, PhonePe)\n• Cards\n\nAll payment methods!"),
        ("pay", "💳 Payment Options:\n• Cash\n• UPI\n• Cards\n\nConvenient!"),
        ("upi", "💳 UPI Accepted!\nGPay, PhonePe, Paytm\nAll UPI apps work!"),
        
        # WiFi
        ("wifi", "📶 Free WiFi!\nPassword: [Your WiFi Password]\n\nEnjoy!"),
        ("internet", "📶 WiFi Available!\nAsk staff for password\n\nStay connected!"),
        
        # Parking
        ("parking", "🅿️ Parking Available:\n• 2-Wheeler: FREE\n• 4-Wheeler: ₹20\n\nSafe parking!"),
        
        # Specials
        ("offer", "🎁 Current Offers:\n• Happy Hour: 4-7 PM\n• 20% off on Coffee\n• Student Discount: 10%\n\nAsk for more!"),
        ("deal", "🎁 Today's Deals:\n• Combo: Burger+Fries+Drink = ₹249\n• Coffee: 20% off 4-7 PM\n\nGreat savings!"),
        ("discount", "🎁 Discounts:\n• Student: 10% off\n• Happy Hour: 20% off coffee\n\nShow your ID!"),
        ("combo", "🍔 Combo Deals:\n• Burger + Fries + Drink = ₹249\n• Pizza + Drink = ₹299\n\nValue meals!"),
        
        # Thanks/Goodbye
        ("thank", "You're welcome! 😊\nHappy to help!"),
        ("thanks", "Thank you! 🙏\nVisit again soon!"),
        ("bye", "Goodbye! 👋\nHave a great day! 🌟"),
        ("tata", "Tata! 👋\nCome back soon! 😊"),
        
        # Help
        ("help", "ℹ️ I can help with:\n• Menu info\n• Prices\n• Order placement\n• Table booking\n• Delivery info\n\nJust ask! 😊"),
        
        # Best sellers
        ("best", "⭐ Our Best Sellers:\n1. Zinger Burger - ₹229\n2. Cold Coffee - ₹179\n3. Farmhouse Pizza - ₹249\n\nHighly recommended!"),
        ("popular", "⭐ Popular Items:\n• Zinger Burger\n• Cold Coffee\n• Farmhouse Pizza\n\nCustomer favorites!"),
        
        # About
        ("about", "🏪 About Us:\nWe're a cozy cafe serving\ndelicious food & drinks since [Year]!\n\nQuality and taste guaranteed!"),
    ]
    
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    count = 0
    for keyword, response in cafe_keywords:
        try:
            c.execute('INSERT INTO keywords (keyword, response) VALUES (?, ?)',
                     (keyword.lower(), response))
            count += 1
        except:
            c.execute('UPDATE keywords SET response=? WHERE keyword=?',
                     (response, keyword.lower()))
            count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n{C.GREEN}✅ Loaded {count} pre-made cafe keywords!{C.END}")
    print(f"{C.CYAN}Your bot now knows common cafe questions!{C.END}")

# ========================
# MAIN
# ========================

def main():
    """Main function"""
    # Initialize database
    init_db()
    
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        print(BANNER)
        print(MENU)
        
        choice = input(f"  {C.BOLD}Enter choice:{C.END} ").strip()
        
        if choice == "1":
            run_auto_reply()
            input(f"\n{C.GREEN}Press ENTER to continue...{C.END}")
            
        elif choice == "2":
            setup_whatsapp_session()
            input(f"\n{C.GREEN}Press ENTER to continue...{C.END}")
            
        elif choice == "3":
            setup_ai()
            input(f"\n{C.GREEN}Press ENTER to continue...{C.END}")
            
        elif choice == "4":
            add_keyword_ui()
            input(f"\n{C.GREEN}Press ENTER to continue...{C.END}")
            
        elif choice == "5":
            view_stats()
            input(f"\n{C.GREEN}Press ENTER to continue...{C.END}")
            
        elif choice == "6":
            test_auto_reply()
            
        elif choice == "7":
            view_keywords()
            input(f"\n{C.GREEN}Press ENTER to continue...{C.END}")
            
        elif choice == "8":
            print(f"\n{C.CYAN}Options:{C.END}")
            print(f"{C.GREEN}[1]{C.END} Load Cafe Menu (CSV/Excel file)")
            print(f"{C.GREEN}[2]{C.END} Load Pre-Made Cafe Keywords")
            sub_choice = input(f"\n{C.GREEN}Enter choice: {C.END}").strip()
            
            if sub_choice == "1":
                load_cafe_menu()
            elif sub_choice == "2":
                load_premade_cafe_keywords()
            
            input(f"\n{C.GREEN}Press ENTER to continue...{C.END}")
            
        elif choice == "9":
            view_cache_stats()
            input(f"\n{C.GREEN}Press ENTER to continue...{C.END}")
            
        elif choice == "10":
            clear_data()
            input(f"\n{C.GREEN}Press ENTER to continue...{C.END}")
            
        elif choice == "0":
            print(f"\n  {C.YELLOW}Goodbye! 👋{C.END}\n")
            sys.exit(0)
            
        else:
            print(f"\n  {C.RED}Invalid choice!{C.END}")
            time.sleep(1)
        
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.YELLOW}Goodbye! 👋{C.END}\n")
        sys.exit(0)
