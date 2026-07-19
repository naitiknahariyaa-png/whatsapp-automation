#!/usr/bin/env python3
"""
🤖 WhatsApp Automation - Web Dashboard
=====================================
Open in Chrome - No CLI needed!

Features:
- Beautiful Web Dashboard
- Click-based controls
- Real-time monitoring
- Customer management
- Broadcast messages
- Order tracking
- AI auto-replies

Author: Built with ❤️
"""

import os
import json
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, RedirectResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.error("pip install fastapi uvicorn jinja2")

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

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

BUSINESS_NAME = "WhatsApp AI Bot"
PORT = 8500

# ═══════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════

class Database:
    def __init__(self):
        self.db_file = Path("data/web_dashboard.json")
        self.db_file.parent.mkdir(exist_ok=True)
        self.data = self.load()
    
    def load(self):
        if self.db_file.exists():
            return json.loads(self.db_file.read_text())
        return {
            "customers": [],
            "orders": [],
            "templates": {
                "hello": "Hello! 👋 Welcome! How can I help you?",
                "hi": "Hi there! 😊 How may I assist you?",
                "price": "Our prices are very competitive! What interests you?",
                "order": "Great! Please tell me your name, items, and address.",
                "delivery": "Yes! We deliver all over India! 🚚 2-5 days.",
                "hours": "We're open 9 AM - 9 PM, all days! 🌟",
                "thanks": "You're welcome! 😊",
                "bye": "Goodbye! Have a great day! 👋",
            },
            "messages": [],
            "stats": {"total": 0, "orders": 0, "broadcasts": 0}
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
    
    def add_message(self, sender, msg, direction):
        self.data["messages"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "sender": sender,
            "message": msg[:200],
            "direction": direction
        })
        self.data["stats"]["total"] += 1
        self.save()
    
    def add_order(self, order):
        self.data["orders"].append(order)
        self.data["stats"]["orders"] += 1
        self.save()
    
    def add_template(self, keyword, response):
        self.data["templates"][keyword.lower()] = response
        self.save()
    
    def delete_template(self, keyword):
        if keyword in self.data["templates"]:
            del self.data["templates"][keyword]
            self.save()
            return True
        return False
    
    def get_stats(self):
        return {
            **self.data["stats"],
            "customers": len(self.data["customers"]),
            "templates": len(self.data["templates"])
        }

db = Database()

# ═══════════════════════════════════════════════════════════════
# AI ENGINE
# ═══════════════════════════════════════════════════════════════

class AIEngine:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_AVAILABLE and GROQ_API_KEY else None
    
    def get_response(self, message):
        # Check templates
        msg_lower = message.lower().strip()
        for keyword, response in db.data["templates"].items():
            if keyword in msg_lower:
                return response, "template"
        
        # Use AI
        if self.client:
            try:
                chat = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": f"You are a helpful assistant for {BUSINESS_NAME}. Keep responses SHORT and FRIENDLY."},
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
            data = {"session": self.session, "chatId": f"{phone}@c.us", "text": text}
            r = requests.post(f"{self.url}/api/messages/sendText", headers=headers, json=data, timeout=30)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    def get_messages(self, limit=20):
        if not self.api_key:
            return []
        try:
            headers = {"X-API-Key": self.api_key}
            r = requests.get(f"{self.url}/api/messages", headers=headers, params={"limit": limit, "session": self.session}, timeout=10)
            if r.status_code == 200:
                return r.json()
            return []
        except:
            return []

wa = WhatsAppGateway()

# ═══════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════

app = FastAPI(title="WhatsApp Automation Dashboard")

# Templates
templates = Jinja2Templates(directory="templates")

# ═══════════════════════════════════════════════════════════════
# HTML DASHBOARD
# ═══════════════════════════════════════════════════════════════

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 WhatsApp Automation Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        .header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 20px 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .status-bar {
            display: flex;
            gap: 30px;
            padding: 20px 40px;
            background: rgba(255,255,255,0.05);
            flex-wrap: wrap;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }
        
        .status-item .icon {
            font-size: 24px;
        }
        
        .status-item .info {
            display: flex;
            flex-direction: column;
        }
        
        .status-item .label {
            font-size: 12px;
            opacity: 0.7;
        }
        
        .status-item .value {
            font-size: 18px;
            font-weight: bold;
        }
        
        .green { color: #4ade80; }
        .red { color: #f87171; }
        .yellow { color: #fbbf24; }
        
        .container {
            padding: 30px 40px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .card h2 {
            font-size: 18px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card h2 .icon {
            font-size: 24px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            opacity: 0.9;
        }
        
        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 12px 15px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .form-group input:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            background: rgba(255,255,255,0.15);
        }
        
        .form-group textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: #fff;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn-success {
            background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
            color: #fff;
        }
        
        .btn-danger {
            background: linear-gradient(90deg, #eb3349 0%, #f45c43 100%);
            color: #fff;
        }
        
        .btn-small {
            padding: 8px 15px;
            font-size: 12px;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .list-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 8px;
            transition: all 0.3s;
        }
        
        .list-item:hover {
            background: rgba(255,255,255,0.1);
        }
        
        .list-item .info {
            flex: 1;
        }
        
        .list-item .name {
            font-weight: bold;
            margin-bottom: 3px;
        }
        
        .list-item .detail {
            font-size: 12px;
            opacity: 0.7;
        }
        
        .badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
        }
        
        .badge-green {
            background: rgba(74, 222, 128, 0.2);
            color: #4ade80;
        }
        
        .badge-yellow {
            background: rgba(251, 191, 36, 0.2);
            color: #fbbf24;
        }
        
        .badge-red {
            background: rgba(248, 113, 113, 0.2);
            color: #f87171;
        }
        
        .empty {
            text-align: center;
            padding: 40px;
            opacity: 0.6;
        }
        
        .empty .icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        
        .alert {
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert-success {
            background: rgba(74, 222, 128, 0.2);
            border: 1px solid #4ade80;
            color: #4ade80;
        }
        
        .alert-error {
            background: rgba(248, 113, 113, 0.2);
            border: 1px solid #f87171;
            color: #f87171;
        }
        
        .actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .message-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .message {
            padding: 12px 15px;
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 13px;
        }
        
        .message-in {
            background: rgba(102, 126, 234, 0.2);
            border-left: 3px solid #667eea;
        }
        
        .message-out {
            background: rgba(74, 222, 128, 0.2);
            border-left: 3px solid #4ade80;
        }
        
        .message .time {
            font-size: 11px;
            opacity: 0.6;
            margin-bottom: 5px;
        }
        
        .message .sender {
            font-weight: bold;
            color: #667eea;
        }
        
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        
        .nav-tab {
            padding: 12px 25px;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }
        
        .nav-tab:hover, .nav-tab.active {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .flex {
            display: flex;
            gap: 15px;
        }
        
        .flex-1 {
            flex: 1;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
        
        .stat-card .icon {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-card .label {
            font-size: 12px;
            opacity: 0.7;
        }
        
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .header, .container, .status-bar {
                padding: 15px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 WhatsApp Automation Dashboard v5.0</h1>
        <p>Control your WhatsApp bot from here - No CLI needed!</p>
    </div>
    
    <div class="status-bar">
        <div class="status-item">
            <span class="icon">📱</span>
            <div class="info">
                <span class="label">WhatsApp</span>
                <span class="value" id="wa-status">Checking...</span>
            </div>
        </div>
        <div class="status-item">
            <span class="icon">🤖</span>
            <div class="info">
                <span class="label">AI Engine</span>
                <span class="value green" id="ai-status">Active</span>
            </div>
        </div>
        <div class="status-item">
            <span class="icon">👥</span>
            <div class="info">
                <span class="label">Customers</span>
                <span class="value" id="customers-count">0</span>
            </div>
        </div>
        <div class="status-item">
            <span class="icon">📊</span>
            <div class="info">
                <span class="label">Messages</span>
                <span class="value" id="messages-count">0</span>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="alert alert-success" id="alert-success"></div>
        <div class="alert alert-error" id="alert-error"></div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📱</div>
                <div class="value" id="stat-messages">0</div>
                <div class="label">Total Messages</div>
            </div>
            <div class="stat-card">
                <div class="icon">📦</div>
                <div class="value" id="stat-orders">0</div>
                <div class="label">Orders</div>
            </div>
            <div class="stat-card">
                <div class="icon">👥</div>
                <div class="value" id="stat-customers">0</div>
                <div class="label">Customers</div>
            </div>
            <div class="stat-card">
                <div class="icon">📢</div>
                <div class="value" id="stat-broadcasts">0</div>
                <div class="label">Broadcasts</div>
            </div>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('dashboard')">📊 Dashboard</button>
            <button class="nav-tab" onclick="showTab('customers')">👥 Customers</button>
            <button class="nav-tab" onclick="showTab('templates')">📝 Templates</button>
            <button class="nav-tab" onclick="showTab('broadcast')">📢 Broadcast</button>
            <button class="nav-tab" onclick="showTab('messages')">💬 Messages</button>
            <button class="nav-tab" onclick="showTab('test')">🧪 Test</button>
        </div>
        
        <!-- Dashboard Tab -->
        <div class="tab-content active" id="tab-dashboard">
            <div class="card">
                <h2><span class="icon">🚀</span> Quick Actions</h2>
                <div class="grid">
                    <div>
                        <div class="form-group">
                            <label>Test WhatsApp Message</label>
                            <div class="flex">
                                <input type="text" id="test-phone" placeholder="Phone (919876543210)" class="flex-1">
                                <input type="text" id="test-message" placeholder="Message" class="flex-1">
                                <button class="btn btn-success" onclick="testWhatsApp()">📤 Send</button>
                            </div>
                        </div>
                    </div>
                    <div>
                        <div class="form-group">
                            <label>Add Customer</label>
                            <div class="flex">
                                <input type="text" id="add-phone" placeholder="Phone (919876543210)" class="flex-1">
                                <button class="btn btn-primary" onclick="addCustomer()">➕ Add</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Customers Tab -->
        <div class="tab-content" id="tab-customers">
            <div class="card">
                <h2><span class="icon">👥</span> Customer Management</h2>
                <div class="form-group">
                    <label>Add New Customer</label>
                    <div class="flex">
                        <input type="text" id="new-customer-phone" placeholder="Phone Number" class="flex-1">
                        <button class="btn btn-primary" onclick="addCustomer()">➕ Add Customer</button>
                    </div>
                </div>
                <hr style="margin: 20px 0; opacity: 0.2;">
                <div class="list" id="customers-list">
                    <div class="empty">
                        <div class="icon">👥</div>
                        <p>No customers yet</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Templates Tab -->
        <div class="tab-content" id="tab-templates">
            <div class="card">
                <h2><span class="icon">📝</span> Auto-Reply Templates</h2>
                <div class="grid">
                    <div>
                        <div class="form-group">
                            <label>Keyword (what user types)</label>
                            <input type="text" id="template-keyword" placeholder="e.g., hello, price, order">
                        </div>
                    </div>
                    <div>
                        <div class="form-group">
                            <label>Response (what bot replies)</label>
                            <input type="text" id="template-response" placeholder="Your auto-reply message">
                        </div>
                    </div>
                </div>
                <button class="btn btn-primary" onclick="addTemplate()">➕ Add Template</button>
                
                <hr style="margin: 25px 0; opacity: 0.2;">
                
                <h3 style="margin-bottom: 15px;">Current Templates</h3>
                <div class="list" id="templates-list"></div>
            </div>
        </div>
        
        <!-- Broadcast Tab -->
        <div class="tab-content" id="tab-broadcast">
            <div class="card">
                <h2><span class="icon">📢</span> Broadcast Message</h2>
                <p style="margin-bottom: 20px; opacity: 0.8;">
                    Send a message to ALL <span id="broadcast-count">0</span> customers at once!
                </p>
                <div class="form-group">
                    <label>Message to Broadcast</label>
                    <textarea id="broadcast-message" placeholder="Type your broadcast message here..."></textarea>
                </div>
                <button class="btn btn-success" onclick="sendBroadcast()">📤 Send to All Customers</button>
            </div>
        </div>
        
        <!-- Messages Tab -->
        <div class="tab-content" id="tab-messages">
            <div class="card">
                <h2><span class="icon">💬</span> Message History</h2>
                <div class="message-list" id="messages-list">
                    <div class="empty">
                        <div class="icon">💬</div>
                        <p>No messages yet</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Test Tab -->
        <div class="tab-content" id="tab-test">
            <div class="card">
                <h2><span class="icon">🧪</span> Test AI Response</h2>
                <div class="form-group">
                    <label>Type a message to test AI</label>
                    <input type="text" id="test-ai-input" placeholder="Type message (e.g., hello, what are your prices?)">
                </div>
                <button class="btn btn-primary" onclick="testAI()">🧪 Test AI</button>
                <div id="ai-test-result" style="margin-top: 20px;"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab switching
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        // Load data on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboard();
            setInterval(loadDashboard, 5000); // Refresh every 5 seconds
        });
        
        function loadDashboard() {
            fetch('/api/stats')
                .then(res => res.json())
                .then(data => {
                    // Update status bar
                    document.getElementById('wa-status').innerHTML = data.wa_connected 
                        ? '<span class="green">✅ Connected</span>' 
                        : '<span class="red">❌ Not Connected</span>';
                    document.getElementById('customers-count').textContent = data.customers;
                    document.getElementById('messages-count').textContent = data.total;
                    document.getElementById('broadcast-count').textContent = data.customers;
                    
                    // Update stats
                    document.getElementById('stat-messages').textContent = data.total;
                    document.getElementById('stat-orders').textContent = data.orders;
                    document.getElementById('stat-customers').textContent = data.customers;
                    document.getElementById('stat-broadcasts').textContent = data.broadcasts;
                });
            
            loadCustomers();
            loadTemplates();
            loadMessages();
        }
        
        function loadCustomers() {
            fetch('/api/customers')
                .then(res => res.json())
                .then(data => {
                    const list = document.getElementById('customers-list');
                    if (data.length === 0) {
                        list.innerHTML = '<div class="empty"><div class="icon">👥</div><p>No customers yet</p></div>';
                    } else {
                        list.innerHTML = data.map(c => `
                            <div class="list-item">
                                <div class="info">
                                    <div class="name">📱 ${c}</div>
                                </div>
                                <button class="btn btn-small btn-danger" onclick="removeCustomer('${c}')">🗑️</button>
                            </div>
                        `).join('');
                    }
                });
        }
        
        function loadTemplates() {
            fetch('/api/templates')
                .then(res => res.json())
                .then(data => {
                    const list = document.getElementById('templates-list');
                    if (Object.keys(data).length === 0) {
                        list.innerHTML = '<div class="empty"><div class="icon">📝</div><p>No templates yet</p></div>';
                    } else {
                        list.innerHTML = Object.entries(data).map(([key, value]) => `
                            <div class="list-item">
                                <div class="info">
                                    <div class="name">🔑 ${key}</div>
                                    <div class="detail">💬 ${value}</div>
                                </div>
                                <button class="btn btn-small btn-danger" onclick="deleteTemplate('${key}')">🗑️</button>
                            </div>
                        `).join('');
                    }
                });
        }
        
        function loadMessages() {
            fetch('/api/messages')
                .then(res => res.json())
                .then(data => {
                    const list = document.getElementById('messages-list');
                    if (data.length === 0) {
                        list.innerHTML = '<div class="empty"><div class="icon">💬</div><p>No messages yet</p></div>';
                    } else {
                        list.innerHTML = data.reverse().slice(0, 50).map(m => `
                            <div class="message ${m.direction === 'incoming' ? 'message-in' : 'message-out'}">
                                <div class="time">${m.time} - ${m.direction === 'incoming' ? '📥' : '📤'}</div>
                                <div><span class="sender">${m.sender}:</span> ${m.message}</div>
                            </div>
                        `).join('');
                    }
                });
        }
        
        function showAlert(type, message) {
            const alert = document.getElementById(type === 'success' ? 'alert-success' : 'alert-error');
            alert.textContent = message;
            alert.style.display = 'block';
            setTimeout(() => alert.style.display = 'none', 3000);
        }
        
        function addCustomer() {
            const phone = document.getElementById('new-customer-phone').value || document.getElementById('add-phone').value;
            if (!phone) {
                showAlert('error', 'Please enter a phone number');
                return;
            }
            
            fetch('/api/customers/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone: phone})
            })
            .then(res => res.json())
            .then(data => {
                showAlert('success', data.message);
                document.getElementById('new-customer-phone').value = '';
                document.getElementById('add-phone').value = '';
                loadDashboard();
            });
        }
        
        function removeCustomer(phone) {
            if (confirm('Remove customer ' + phone + '?')) {
                fetch('/api/customers/remove', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phone: phone})
                })
                .then(res => res.json())
                .then(data => {
                    showAlert('success', data.message);
                    loadDashboard();
                });
            }
        }
        
        function addTemplate() {
            const keyword = document.getElementById('template-keyword').value;
            const response = document.getElementById('template-response').value;
            
            if (!keyword || !response) {
                showAlert('error', 'Please enter both keyword and response');
                return;
            }
            
            fetch('/api/templates/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({keyword, response})
            })
            .then(res => res.json())
            .then(data => {
                showAlert('success', data.message);
                document.getElementById('template-keyword').value = '';
                document.getElementById('template-response').value = '';
                loadDashboard();
            });
        }
        
        function deleteTemplate(keyword) {
            if (confirm('Delete template "' + keyword + '"?')) {
                fetch('/api/templates/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({keyword})
                })
                .then(res => res.json())
                .then(data => {
                    showAlert('success', data.message);
                    loadDashboard();
                });
            }
        }
        
        function sendBroadcast() {
            const message = document.getElementById('broadcast-message').value;
            if (!message) {
                showAlert('error', 'Please enter a message to broadcast');
                return;
            }
            
            if (!confirm('Send this message to ALL customers?')) return;
            
            fetch('/api/broadcast', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message})
            })
            .then(res => res.json())
            .then(data => {
                showAlert('success', data.message);
                document.getElementById('broadcast-message').value = '';
                loadDashboard();
            });
        }
        
        function testWhatsApp() {
            const phone = document.getElementById('test-phone').value;
            const message = document.getElementById('test-message').value;
            
            if (!phone || !message) {
                showAlert('error', 'Please enter phone and message');
                return;
            }
            
            fetch('/api/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone, message})
            })
            .then(res => res.json())
            .then(data => {
                showAlert(data.success ? 'success' : 'error', data.message);
                if (data.success) {
                    document.getElementById('test-phone').value = '';
                    document.getElementById('test-message').value = '';
                }
                loadDashboard();
            });
        }
        
        function testAI() {
            const input = document.getElementById('test-ai-input').value;
            if (!input) {
                showAlert('error', 'Please enter a message');
                return;
            }
            
            fetch('/api/test-ai', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: input})
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('ai-test-result').innerHTML = `
                    <div class="message message-in">
                        <div class="time">You</div>
                        <div>${input}</div>
                    </div>
                    <div class="message message-out">
                        <div class="time">AI (${data.source})</div>
                        <div>${data.response}</div>
                    </div>
                `;
            });
        }
    </script>
</body>
</html>
"""

# ═══════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the dashboard HTML"""
    return DASHBOARD_HTML

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    stats = db.get_stats()
    return {
        **stats,
        "wa_connected": wa.is_connected()
    }

@app.get("/api/customers")
async def get_customers():
    """Get customer list"""
    return db.data["customers"]

@app.post("/api/customers/add")
async def add_customer(request: Request):
    """Add a customer"""
    data = await request.json()
    phone = data.get("phone", "").replace("+", "").replace("@c.us", "")
    
    if db.add_customer(phone):
        return {"success": True, "message": f"✅ Customer {phone} added!"}
    return {"success": False, "message": "ℹ️ Customer already exists"}

@app.post("/api/customers/remove")
async def remove_customer(request: Request):
    """Remove a customer"""
    data = await request.json()
    phone = data.get("phone", "")
    
    if phone in db.data["customers"]:
        db.data["customers"].remove(phone)
        db.save()
        return {"success": True, "message": f"✅ Customer {phone} removed!"}
    return {"success": False, "message": "Customer not found"}

@app.get("/api/templates")
async def get_templates():
    """Get templates"""
    return db.data["templates"]

@app.post("/api/templates/add")
async def add_template(request: Request):
    """Add a template"""
    data = await request.json()
    keyword = data.get("keyword", "").lower()
    response = data.get("response", "")
    
    db.add_template(keyword, response)
    return {"success": True, "message": f"✅ Template '{keyword}' added!"}

@app.post("/api/templates/delete")
async def delete_template(request: Request):
    """Delete a template"""
    data = await request.json()
    keyword = data.get("keyword", "")
    
    if db.delete_template(keyword):
        return {"success": True, "message": f"✅ Template '{keyword}' deleted!"}
    return {"success": False, "message": "Template not found"}

@app.get("/api/messages")
async def get_messages():
    """Get message history"""
    return db.data["messages"]

@app.post("/api/broadcast")
async def broadcast(request: Request):
    """Send broadcast to all customers"""
    data = await request.json()
    message = data.get("message", "")
    
    if not wa.is_connected():
        return {"success": False, "message": "❌ WhatsApp not connected!"}
    
    customers = db.data["customers"]
    if not customers:
        return {"success": False, "message": "❌ No customers to send to!"}
    
    sent = failed = 0
    for phone in customers:
        if wa.send_message(phone, message):
            sent += 1
        else:
            failed += 1
    
    db.data["stats"]["broadcasts"] += 1
    db.save()
    
    return {
        "success": True, 
        "message": f"✅ Broadcast sent! 📤 Sent: {sent}, ❌ Failed: {failed}"
    }

@app.post("/api/send")
async def send_message(request: Request):
    """Send WhatsApp message"""
    data = await request.json()
    phone = data.get("phone", "").replace("+", "")
    message = data.get("message", "")
    
    if not wa.is_connected():
        return {"success": False, "message": "❌ WhatsApp not connected!"}
    
    if wa.send_message(phone, message):
        db.add_message(phone, message, "outgoing")
        return {"success": True, "message": f"✅ Message sent to {phone}!"}
    
    return {"success": False, "message": f"❌ Failed to send to {phone}"}

@app.post("/api/test-ai")
async def test_ai(request: Request):
    """Test AI response"""
    data = await request.json()
    message = data.get("message", "")
    
    response, source = ai.get_response(message)
    return {"response": response, "source": source}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🤖 WhatsApp Automation - Web Dashboard                  ║
║                                                               ║
║     🌐 Open in Chrome - No CLI Needed!                       ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if not FASTAPI_AVAILABLE:
        print("❌ Installing required packages...")
        os.system("pip install fastapi uvicorn jinja2")
    
    print(f"✅ All ready!")
    print(f"")
    print(f"🌐 Open your browser and go to:")
    print(f"")
    print(f"   👉 http://localhost:{PORT}")
    print(f"")
    print(f"📱 WhatsApp: {'✅ Connected' if wa.is_connected() else '❌ Not Connected'}")
    print(f"🤖 AI: {'✅ Active' if ai.client else '❌ Disabled'}")
    print(f"👥 Customers: {len(db.data['customers'])}")
    print(f"")
    print(f"⚠️  To connect WhatsApp, run this first:")
    print(f"    docker run -d --name openwa -p 3000:3000 waha/waha:latest")
    print(f"")
    print(f"=" * 60)
    
    # Start server
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")

if __name__ == "__main__":
    main()
