"""
Web Dashboard Module
FastAPI/Gradio dashboard for monitoring and control
"""

import gradio as gr
from datetime import datetime


def create_dashboard(config):
    """Create the web dashboard using Gradio"""
    
    # Dashboard CSS
    css = """
    .dashboard-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #25D366, #128C7E);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stats-card {
        background: #f0f2f5;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    """
    
    # Load database
    try:
        from .database import Database
        db = Database(config.get('database', {}))
        stats = db.get_statistics()
    except:
        stats = {
            'total_messages': 0,
            'auto_replied': 0,
            'unique_contacts': 0,
            'today_messages': 0
        }
    
    # Get contacts
    try:
        contacts = db.get_contacts()
    except:
        contacts = []
    
    # Get recent messages
    try:
        messages = db.get_messages(limit=20)
    except:
        messages = []
    
    with gr.Blocks(title="WhatsApp Bot Dashboard", css=css) as dashboard:
        gr.Markdown("""
        # 🤖 WhatsApp AI Bot Dashboard
        
        Monitor and control your WhatsApp automation bot.
        """)
        
        # Status Section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📊 Bot Status")
                status_box = gr.Textbox(
                    value="🟢 Online" if stats.get('total_messages', 0) > 0 else "⚪ Offline",
                    interactive=False,
                    show_label=False
                )
                
            with gr.Column():
                gr.Markdown("### 🤖 AI Provider")
                ai_status = gr.Textbox(
                    value=config.get('ai', {}).get('provider', 'Not configured'),
                    interactive=False,
                    show_label=False
                )
        
        # Statistics
        gr.Markdown("### 📈 Statistics")
        with gr.Row():
            stats_box = gr.JSON(value=stats)
        
        # Controls
        gr.Markdown("### 🎮 Controls")
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh", variant="primary")
            settings_btn = gr.Button("⚙️ Settings")
        
        # Contacts
        gr.Markdown("### 👥 Recent Contacts")
        if contacts:
            contact_list = "\n".join([
                f"• {c['name']} ({c.get('message_count', 0)} messages)"
                for c in contacts[:10]
            ])
        else:
            contact_list = "No contacts yet"
        contacts_box = gr.Textbox(value=contact_list, interactive=False, lines=10)
        
        # Recent Messages
        gr.Markdown("### 💬 Recent Messages")
        if messages:
            msg_list = "\n".join([
                f"[{m.get('timestamp', '')[:19]}] {m['sender']}: {m['content'][:50]}..."
                for m in messages[:10]
            ])
        else:
            msg_list = "No messages yet"
        messages_box = gr.Textbox(value=msg_list, interactive=False, lines=15)
        
        # Event handlers
        refresh_btn.click(
            fn=lambda: (
                db.get_statistics() if 'db' in dir() else {},
                "Refreshed!"
            ),
            outputs=[stats_box, status_box]
        )
        
    return dashboard


# Alternative FastAPI dashboard
def create_fastapi_dashboard(config):
    """Create FastAPI-based dashboard (alternative)"""
    try:
        from fastapi import FastAPI, Request
        from fastapi.responses import HTMLResponse
        import uvicorn
        
        app = FastAPI(title="WhatsApp Bot Dashboard")
        
        @app.get("/", response_class=HTMLResponse)
        async def home():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>WhatsApp Bot Dashboard</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    .card { background: #f0f2f5; padding: 20px; border-radius: 10px; margin: 10px 0; }
                    .online { color: green; }
                    h1 { color: #25D366; }
                </style>
            </head>
            <body>
                <h1>🤖 WhatsApp Bot Dashboard</h1>
                <div class="card">
                    <h2>Status: <span class="online">🟢 Online</span></h2>
                </div>
                <div class="card">
                    <h3>Quick Stats</h3>
                    <p>Total Messages: Loading...</p>
                </div>
            </body>
            </html>
            """
        
        @app.get("/api/stats")
        async def get_stats():
            try:
                from .database import Database
                db = Database(config.get('database', {}))
                return db.get_statistics()
            except:
                return {"error": "Database not available"}
        
        @app.get("/api/contacts")
        async def get_contacts():
            try:
                from .database import Database
                db = Database(config.get('database', {}))
                return db.get_contacts()
            except:
                return []
        
        return app
        
    except ImportError:
        print("FastAPI not installed. Install with: pip install fastapi uvicorn")
        return None
