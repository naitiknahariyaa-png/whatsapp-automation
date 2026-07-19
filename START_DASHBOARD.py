#!/usr/bin/env python3
"""
🚀 WhatsApp Automation - Web Dashboard Launcher
===============================================

Double-click this file to:
1. Install dependencies
2. Start the web dashboard
3. Open Chrome automatically

Author: Built with ❤️
"""

import os
import sys
import webbrowser
import subprocess
import time

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🤖 WhatsApp Automation - Web Dashboard                  ║
║                                                               ║
║     🌐 Opening in Chrome automatically...                    ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Install dependencies
    print("📦 Installing dependencies...")
    deps = ["fastapi", "uvicorn", "jinja2", "python-telegram-bot", "groq", "requests"]
    for dep in deps:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep, "-q"], 
                         capture_output=True, check=True)
        except:
            pass
    print("✅ Dependencies ready!")
    
    # Start server in background
    print("\n🌐 Starting Dashboard...")
    print("-" * 50)
    
    server_process = subprocess.Popen(
        [sys.executable, "web_dashboard.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    # Wait for server to start
    time.sleep(3)
    
    # Open browser
    url = "http://localhost:8500"
    print(f"\n🔗 Opening: {url}")
    webbrowser.open(url)
    
    print("\n" + "=" * 50)
    print("✅ Dashboard is running!")
    print(f"   🌐 http://localhost:8500")
    print("\n   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Wait for server
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("\n\n👋 Stopping server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped!")

if __name__ == "__main__":
    main()
