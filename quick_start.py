#!/usr/bin/env python3
"""
⚡ Quick Start - Simple Auto-Launcher
=====================================
Starts only if containers exist. No auto-pull.

USE THIS IF:
- Docker images are already downloaded
- You want fast startup

FOR FIRST TIME SETUP:
- Run manually: docker run -d --name redis -p 6379:6379 redis:alpine
- Then use this script for quick start
"""

import os
import sys
import time
import socket
import subprocess

# ═══════════════════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════════════════

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BOLD = '\033[1m'
END = '\033[0m'

def log(msg, color=""):
    print(f"{color}{msg}{END}")

# ═══════════════════════════════════════════════════════════════
# CHECK FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def is_port_open(port, host="localhost"):
    """Check if port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def is_docker_running():
    """Check if Docker is running"""
    try:
        result = subprocess.run("docker info", capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def is_container_running(name):
    """Check if container is running"""
    try:
        result = subprocess.run(
            f'docker ps --filter "name={name}" --format "{{{{.Names}}}}"',
            capture_output=True, text=True, timeout=5
        )
        return name in result.stdout
    except:
        return False

def start_container(name):
    """Start existing container"""
    try:
        # Check if exists
        result = subprocess.run(
            f'docker ps -a --filter "name={name}" --format "{{{{.Names}}}}"',
            capture_output=True, text=True, timeout=5
        )
        
        if name not in result.stdout:
            return False, f"Container '{name}' does not exist. Run the setup command first."
        
        # Start it
        result = subprocess.run(f"docker start {name}", capture_output=True, timeout=30)
        
        if result.returncode == 0:
            return True, f"Container '{name}' started"
        else:
            return False, result.stderr.decode()
    except Exception as e:
        return False, str(e)

# ═══════════════════════════════════════════════════════════════
# SERVICES
# ═══════════════════════════════════════════════════════════════

SERVICES = [
    {
        "name": "Redis",
        "container": "redis",
        "port": 6379,
        "url": "http://localhost:6379"
    },
    {
        "name": "OpenWA",
        "container": "openwa",
        "port": 2785,
        "url": "http://localhost:2785"
    },
    {
        "name": "PostgreSQL",
        "container": "postgres",
        "port": 5432,
        "url": "PostgreSQL://localhost:5432"
    },
    {
        "name": "MinIO",
        "container": "minio",
        "port": 9000,
        "url": "http://localhost:9001"
    },
    {
        "name": "N8N",
        "container": "n8n",
        "port": 5678,
        "url": "http://localhost:5678"
    },
]

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"""
{BOLD}{CYAN}
╔══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ⚡ WhatsApp Automation - Quick Start                 ║
║                                                               ║
║     Fast startup (no Docker pulls)                          ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝{END}
    """)
    
    # Check Docker
    print(f"{CYAN}🔍 Checking Docker...{END}")
    if not is_docker_running():
        log("❌ Docker is not running!", RED)
        log("   Start Docker Desktop first", YELLOW)
        input("\nPress Enter to exit...")
        return
    
    log("✅ Docker is running", GREEN)
    print()
    
    # Check services
    running = []
    not_running = []
    missing = []
    
    for svc in SERVICES:
        print(f"{CYAN}Checking {svc['name']}...{END}", end=" ")
        
        if is_port_open(svc['port']):
            log("✅ Running", GREEN)
            running.append(svc)
        elif is_container_running(svc['container']):
            log("⚠️  Container exists but stopped", YELLOW)
            not_running.append(svc)
        else:
            log("❌ Not found", RED)
            missing.append(svc)
    
    print()
    
    # Start stopped containers
    if not_running:
        print(f"{YELLOW}▶️  Starting stopped containers...{END}")
        for svc in not_running:
            success, msg = start_container(svc['container'])
            if success:
                log(f"   ✅ {svc['name']}: {msg}", GREEN)
                running.append(svc)
            else:
                log(f"   ❌ {svc['name']}: {msg}", RED)
        print()
    
    # Summary
    print(f"{BOLD}📊 SERVICE STATUS{END}")
    print("-" * 50)
    
    if running:
        log(f"\n✅ RUNNING ({len(running)}/{len(SERVICES)}):", GREEN)
        for svc in running:
            print(f"   • {svc['name']}: {svc['url']}")
    
    if not_running:
        log(f"\n⚠️  STOPPED ({len(not_running)}):", YELLOW)
        for svc in not_running:
            print(f"   • {svc['name']}")
    
    if missing:
        log(f"\n❌ MISSING ({len(missing)}):", RED)
        for svc in missing:
            print(f"   • {svc['name']}")
    
    # Instructions for missing
    if missing:
        print(f"""
{CYAN}
📝 FIRST TIME SETUP (Run these once):

docker run -d --name redis -p 6379:6379 redis:alpine
docker run -d --name openwa -p 2785:3000 -p 8181:8181 waha/e2e-js:latest
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15
{CYAN}{END}
        """)
    
    # Start bot
    print(f"\n{BOLD}🚀 STARTING WHATSAPP BOT{END}")
    print("-" * 50)
    
    bot_dir = os.path.dirname(os.path.abspath(__file__))
    bot_script = os.path.join(bot_dir, "main_hub.py")
    
    if os.path.exists(bot_script):
        log(f"✅ Found main_hub.py", GREEN)
        print(f"\n{CYAN}Starting bot in new window...{END}\n")
        
        # Open in new terminal window
        try:
            if sys.platform == "win32":
                subprocess.Popen(
                    f'start cmd /k "cd /d {bot_dir} && python main_hub.py"',
                    shell=True
                )
            else:
                subprocess.Popen(["python", bot_script], cwd=bot_dir)
        except:
            print(f"Run manually: python {bot_script}")
    else:
        log("❌ main_hub.py not found!", RED)
    
    print(f"""
{BOLD}{GREEN}
╔══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ✅ QUICK START COMPLETE!                               ║
║                                                               ║
║     Bot is running. Check the new window for status.        ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝{END}
    """)
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
