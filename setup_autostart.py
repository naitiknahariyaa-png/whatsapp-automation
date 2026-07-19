#!/usr/bin/env python3
"""
⚙️ WhatsApp Automation Setup & Auto-Start Installer
=================================================
Installs all dependencies and sets up auto-start on PC boot

Usage:
    python setup_autostart.py          # Full setup
    python setup_autostart.py --help  # Show help
"""

import os
import sys
import subprocess
import platform

# ═══════════════════════════════════════════════════════════════
# ANSI Colors
# ═══════════════════════════════════════════════════════════════

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(msg, status="info"):
    icons = {"info": "🔄", "ok": "✅", "warn": "⚠️", "error": "❌", "skip": "⏭️"}
    icon = icons.get(status, "•")
    color = {
        "info": Colors.CYAN,
        "ok": Colors.GREEN,
        "warn": Colors.YELLOW,
        "error": Colors.RED,
        "skip": Colors.YELLOW
    }.get(status, "")
    print(f"{color}{icon} {msg}{Colors.END}")


# ═══════════════════════════════════════════════════════════════
# SYSTEM CHECKS
# ═══════════════════════════════════════════════════════════════

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_step(f"Python {version.major}.{version.minor}.{version.micro} ✓", "ok")
        return True
    else:
        print_step(f"Python {version.major}.{version.minor} - Need 3.8+", "error")
        return False


def check_docker():
    """Check if Docker is installed"""
    try:
        result = subprocess.run("docker --version", capture_output=True, text=True)
        if result.returncode == 0:
            print_step(f"Docker: {result.stdout.strip()} ✓", "ok")
            
            # Check if running
            result = subprocess.run("docker info", capture_output=True, text=True)
            if result.returncode == 0:
                print_step("Docker is running ✓", "ok")
                return True
            else:
                print_step("Docker is installed but not running", "warn")
                print_step("Start Docker Desktop manually", "info")
                return False
    except FileNotFoundError:
        print_step("Docker not found - Install from https://docker.com", "error")
        return False


def check_git():
    """Check if Git is installed"""
    try:
        result = subprocess.run("git --version", capture_output=True, text=True)
        if result.returncode == 0:
            print_step(f"Git: {result.stdout.strip()} ✓", "ok")
            return True
    except:
        pass
    print_step("Git not found - Optional", "warn")
    return False


# ═══════════════════════════════════════════════════════════════
# INSTALLATION
# ═══════════════════════════════════════════════════════════════

def install_dependencies():
    """Install Python dependencies"""
    print_step("\n📦 Installing Python dependencies...", "info")
    
    packages = [
        "python-dotenv",
        "requests",
        "python-telegram-bot",
        "selenium",
        "webdriver-manager",
        "groq",
        "boto3",
        "pymongo",
        "redis",
        "posthog",
        "sentry-sdk",
    ]
    
    for package in packages:
        try:
            print_step(f"Installing {package}...", "info")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package, "-q"],
                check=True
            )
        except:
            print_step(f"Failed to install {package}", "warn")
    
    print_step("Dependencies installed ✓", "ok")


def create_data_folders():
    """Create required data folders"""
    print_step("\n📁 Creating data folders...", "info")
    
    folders = [
        "data",
        "data/logs",
        "data/session",
        "data/chrome-profile",
        "data/postgres",
        "data/redis",
        "data/minio",
        "data/n8n",
        "data/meili",
        "data/qdrant",
        "generated_images",
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print_step(f"  Created: {folder}", "ok")
    
    print_step("Data folders created ✓", "ok")


def setup_env_file():
    """Create .env file from example"""
    print_step("\n📝 Setting up environment file...", "info")
    
    env_file = ".env"
    env_example = ".env.example"
    
    if os.path.exists(env_file):
        print_step(".env already exists - Skipping", "skip")
        return
    
    if os.path.exists(env_example):
        with open(env_example, 'r') as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print_step("Created .env from .env.example", "ok")
        print_step("⚠️  Edit .env with your API keys!", "warn")
    else:
        # Create basic .env
        with open(env_file, 'w') as f:
            f.write("# WhatsApp Automation\n")
            f.write("# Add your API keys below\n\n")
        print_step("Created empty .env file", "ok")


def install_to_startup():
    """Install to Windows startup"""
    if platform.system() != "Windows":
        print_step("Auto-startup only works on Windows", "skip")
        return
    
    print_step("\n🚀 Installing to Windows startup...", "info")
    
    script_path = os.path.abspath("auto_start_launcher.py")
    startup_dir = os.getenv('APPDATA') + "\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
    batch_path = os.path.join(startup_dir, "WhatsApp_Bot_Launcher.bat")
    
    batch_content = f'''@echo off
cd /d "{os.path.dirname(script_path)}"
start /B pythonw "{script_path}" --background
'''
    
    try:
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        print_step("Installed to Windows startup ✓", "ok")
        print_step("Bot will start automatically on PC boot!", "ok")
    except Exception as e:
        print_step(f"Failed: {e}", "error")


def start_docker_containers():
    """Try to start essential Docker containers"""
    print_step("\n🐳 Starting Docker containers...", "info")
    
    containers = [
        ("redis", "redis:alpine", "-p 6379:6379"),
        ("openwa", "waha/e2e-js:latest", "-p 2785:3000 -p 8181:8181"),
    ]
    
    for name, image, ports in containers:
        print_step(f"Checking {name}...", "info")
        
        # Check if running
        result = subprocess.run(
            f'docker ps --filter "name={name}" --format "{{{{.Names}}}}"',
            capture_output=True, text=True
        )
        
        if name in result.stdout:
            print_step(f"{name} is already running ✓", "ok")
            continue
        
        # Check if stopped
        result = subprocess.run(
            f'docker ps -a --filter "name={name}" --format "{{{{.Names}}}}"',
            capture_output=True, text=True
        )
        
        if name in result.stdout:
            print_step(f"Starting existing {name}...", "info")
            subprocess.run(f"docker start {name}", shell=True)
        else:
            print_step(f"Creating new {name}...", "info")
            subprocess.run(
                f"docker run -d --name {name} {ports} {image}",
                shell=True
            )
        
        print_step(f"{name} started ✓", "ok")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ⚙️ WhatsApp Automation Setup & Auto-Start             ║
║                                                               ║
║     Installs dependencies and sets up auto-start            ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # System checks
    print("\n📋 System Checks:")
    print("-" * 40)
    check_python()
    check_docker()
    check_git()
    
    # Installation steps
    install_dependencies()
    create_data_folders()
    setup_env_file()
    
    # Ask about auto-start
    if platform.system() == "Windows":
        print()
        response = input("🚀 Install auto-start on PC boot? (y/n): ").strip().lower()
        if response == 'y':
            install_to_startup()
    
    # Ask to start now
    print()
    response = input("▶️  Start services now? (y/n): ").strip().lower()
    if response == 'y':
        start_docker_containers()
        print_step("\n✅ Setup complete!", "ok")
        print_step("\nRun START.bat or python auto_start_launcher.py to start!", "ok")
    else:
        print_step("\n✅ Setup complete! Run START.bat when ready.", "ok")
    
    print("\n" + "="*60)
    print("📋 Next Steps:")
    print("-" * 60)
    print("1. Edit .env and add your API keys")
    print("2. Run START.bat to launch everything")
    print("3. Access services at localhost ports")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
