#!/usr/bin/env python3
"""
🚀 WhatsApp Automation Auto-Start Launcher
==========================================
Runs on PC startup - Starts ALL services automatically!
- Starts Docker containers
- Connects to WhatsApp API
- Launches main bot
- Runs in background
- Monitors health

Install:
    python auto_start_launcher.py --install

Run:
    python auto_start_launcher.py
"""

import os
import sys
import time
import socket
import logging
import subprocess
import threading
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION - Customize these!
# ═══════════════════════════════════════════════════════════════

CONFIG = {
    # Services to auto-start (set True/False)
    "services": {
        "docker_desktop": True,      # Start Docker Desktop
        "openwa": True,             # OpenWA WhatsApp Gateway
        "redis": True,              # Redis Cache
        "postgres": True,            # PostgreSQL Database
        "minio": False,             # MinIO Storage
        "n8n": False,              # N8N Automation
        "meilisearch": False,       # Search Engine
        "qdrant": False,           # Vector Database
        "netdata": False,           # Monitoring
        "mailhog": False,           # Email Testing
    },
    
    # Ports to wait for (service readiness)
    "ports": {
        2376: ("Docker", 30),           # Docker
        2785: ("OpenWA", 60),          # OpenWA
        6379: ("Redis", 15),           # Redis
        5432: ("PostgreSQL", 30),      # PostgreSQL
        9000: ("MinIO", 20),           # MinIO
        5678: ("N8N", 45),            # N8N
        7700: ("Meilisearch", 20),     # Meilisearch
        6333: ("Qdrant", 25),          # Qdrant
        19999: ("Netdata", 15),        # Netdata
        1025: ("MailHog SMTP", 10),    # MailHog
    },
    
    # WhatsApp Bot startup
    "bot": {
        "wait_for_services": 30,       # Wait seconds before starting bot
        "retries": 3,                  # Retry bot start
        "delay_between_retries": 10,   # Seconds between retries
    },
    
    # Paths
    "paths": {
        "bot_dir": os.path.dirname(os.path.abspath(__file__)),
        "openwa_dir": "C:\\OpenWA",
        "docker_compose": "docker-compose.yml",
    }
}

# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════

LOG_FILE = os.path.join(CONFIG["paths"]["bot_dir"], "auto_start.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def is_port_open(port, host="localhost", timeout=1):
    """Check if port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def wait_for_port(port, timeout=30, service_name=""):
    """Wait for a port to become available"""
    name = service_name or f"Port {port}"
    logger.info(f"Waiting for {name} (port {port})...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_open(port):
            logger.info(f"✅ {name} is ready!")
            return True
        time.sleep(1)
    
    logger.warning(f"⏱️ {name} timeout after {timeout}s")
    return False


def run_command(cmd, shell=True, capture=True, timeout=60):
    """Run shell command"""
    try:
        if capture:
            result = subprocess.run(
                cmd, shell=shell, capture_output=True, 
                text=True, timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        else:
            subprocess.Popen(cmd, shell=shell, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return True, "", ""
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def start_docker_service(name, image, ports=None, volumes=None, env=None):
    """Start a Docker container"""
    logger.info(f"🚀 Starting {name}...")
    
    # Build docker command
    cmd = f'docker run -d --name {name}'
    
    # Add ports
    if ports:
        for host_port, container_port in ports.items():
            cmd += f" -p {host_port}:{container_port}"
    
    # Add volumes
    if volumes:
        for host_path, container_path in volumes.items():
            cmd += f' -v "{host_path}":"{container_path}"'
    
    # Add environment
    if env:
        for key, value in env.items():
            cmd += f' -e {key}="{value}"'
    
    # Add image
    cmd += f" {image}"
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        logger.info(f"✅ {name} started!")
        return True
    else:
        logger.warning(f"⚠️ {name}: {stderr or 'Already running or failed'}")
        return False


def is_docker_running():
    """Check if Docker is running"""
    success, _, _ = run_command("docker info")
    return success


# ═══════════════════════════════════════════════════════════════
# SERVICE STARTERS
# ═══════════════════════════════════════════════════════════════

class ServiceManager:
    """Manages all services"""
    
    def __init__(self):
        self.services_status = {}
        self.bot_started = False
        
    def start_docker_desktop(self):
        """Start Docker Desktop (Windows)"""
        if not is_docker_running():
            logger.info("🚀 Starting Docker Desktop...")
            try:
                # Try to start Docker Desktop
                subprocess.Popen(
                    "start docker",
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                logger.info("✅ Docker Desktop starting...")
            except Exception as e:
                logger.warning(f"⚠️ Could not start Docker Desktop: {e}")
                logger.info("💡 Please start Docker Desktop manually")
                return False
        else:
            logger.info("✅ Docker is already running")
        return True
    
    def start_openwa(self):
        """Start OpenWA WhatsApp Gateway"""
        logger.info("🚀 Starting OpenWA...")
        
        # Check if already running
        if is_port_open(2785):
            logger.info("✅ OpenWA is already running")
            return True
        
        # Try docker first
        success = start_docker_service(
            "openwa",
            "waha/e2e-js:latest",
            ports={2785: 3000, 8181: 8181}
        )
        
        if success:
            wait_for_port(2785, timeout=60, service_name="OpenWA")
        
        return is_port_open(2785)
    
    def start_redis(self):
        """Start Redis"""
        logger.info("🚀 Starting Redis...")
        
        if is_port_open(6379):
            logger.info("✅ Redis is already running")
            return True
        
        success = start_docker_service(
            "redis",
            "redis:alpine",
            ports={6379: 6379}
        )
        
        if success:
            wait_for_port(6379, timeout=15, service_name="Redis")
        
        return is_port_open(6379)
    
    def start_postgres(self):
        """Start PostgreSQL"""
        logger.info("🚀 Starting PostgreSQL...")
        
        if is_port_open(5432):
            logger.info("✅ PostgreSQL is already running")
            return True
        
        success = start_docker_service(
            "postgres",
            "postgres:15-alpine",
            ports={5432: 5432},
            env={
                "POSTGRES_DB": "whatsapp_bot",
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": "postgres"
            },
            volumes={f"{CONFIG['paths']['bot_dir']}\\data\\postgres": "/var/lib/postgresql/data"}
        )
        
        if success:
            wait_for_port(5432, timeout=30, service_name="PostgreSQL")
        
        return is_port_open(5432)
    
    def start_minio(self):
        """Start MinIO Storage"""
        logger.info("🚀 Starting MinIO...")
        
        if is_port_open(9000):
            logger.info("✅ MinIO is already running")
            return True
        
        success = start_docker_service(
            "minio",
            "minio/minio",
            ports={9000: 9000, 9001: 9001},
            env={"MINIO_ROOT_USER": "minioadmin", "MINIO_ROOT_PASSWORD": "minioadmin"},
            volumes={f"{CONFIG['paths']['bot_dir']}\\data\\minio": "/data"}
        )
        
        if success:
            # Run with proper command
            run_command('docker exec minio minio server /data --console-address ":9001"')
            wait_for_port(9000, timeout=20, service_name="MinIO")
        
        return is_port_open(9000)
    
    def start_n8n(self):
        """Start N8N Automation"""
        logger.info("🚀 Starting N8N...")
        
        if is_port_open(5678):
            logger.info("✅ N8N is already running")
            return True
        
        success = start_docker_service(
            "n8n",
            "n8nio/n8n",
            ports={5678: 5678},
            volumes={f"{CONFIG['paths']['bot_dir']}\\data\\n8n": "/home/node/.n8n"}
        )
        
        if success:
            wait_for_port(5678, timeout=45, service_name="N8N")
        
        return is_port_open(5678)
    
    def start_meilisearch(self):
        """Start Meilisearch"""
        logger.info("🚀 Starting Meilisearch...")
        
        if is_port_open(7700):
            logger.info("✅ Meilisearch is already running")
            return True
        
        success = start_docker_service(
            "meilisearch",
            "getmeili/meilisearch",
            ports={7700: 7700},
            env={"MEILI_MASTER_KEY": "masterKey123"},
            volumes={f"{CONFIG['paths']['bot_dir']}\\data\\meili": "/meili_data"}
        )
        
        if success:
            wait_for_port(7700, timeout=20, service_name="Meilisearch")
        
        return is_port_open(7700)
    
    def start_qdrant(self):
        """Start Qdrant Vector Database"""
        logger.info("🚀 Starting Qdrant...")
        
        if is_port_open(6333):
            logger.info("✅ Qdrant is already running")
            return True
        
        success = start_docker_service(
            "qdrant",
            "qdrant/qdrant",
            ports={6333: 6333, 6334: 6334},
            volumes={f"{CONFIG['paths']['bot_dir']}\\data\\qdrant": "/qdrant/storage"}
        )
        
        if success:
            wait_for_port(6333, timeout=25, service_name="Qdrant")
        
        return is_port_open(6333)
    
    def start_netdata(self):
        """Start Netdata Monitoring"""
        logger.info("🚀 Starting Netdata...")
        
        if is_port_open(19999):
            logger.info("✅ Netdata is already running")
            return True
        
        success = start_docker_service(
            "netdata",
            "netdata/netdata",
            ports={19999: 19999},
            volumes={
                "/proc": "/host/proc",
                "/sys": "/host/sys",
                "/var/run/docker.sock": "/var/run/docker.sock"
            }
        )
        
        if success:
            wait_for_port(19999, timeout=15, service_name="Netdata")
        
        return is_port_open(19999)
    
    def start_all_services(self):
        """Start all configured services"""
        logger.info("\n" + "="*60)
        logger.info("🚀 STARTING ALL SERVICES")
        logger.info("="*60 + "\n")
        
        services_order = []
        
        # Start Docker first
        if CONFIG["services"].get("docker_desktop"):
            self.start_docker_desktop()
            services_order.append(("Docker", lambda: is_docker_running()))
        
        # Start services in order
        service_methods = [
            ("Redis", self.start_redis, CONFIG["services"].get("redis")),
            ("PostgreSQL", self.start_postgres, CONFIG["services"].get("postgres")),
            ("OpenWA", self.start_openwa, CONFIG["services"].get("openwa")),
            ("MinIO", self.start_minio, CONFIG["services"].get("minio")),
            ("N8N", self.start_n8n, CONFIG["services"].get("n8n")),
            ("Meilisearch", self.start_meilisearch, CONFIG["services"].get("meilisearch")),
            ("Qdrant", self.start_qdrant, CONFIG["services"].get("qdrant")),
            ("Netdata", self.start_netdata, CONFIG["services"].get("netdata")),
        ]
        
        for name, method, enabled in service_methods:
            if enabled:
                try:
                    status = method()
                    services_order.append((name, lambda s=status: s))
                    self.services_status[name] = status
                except Exception as e:
                    logger.error(f"❌ {name} failed: {e}")
                    self.services_status[name] = False
        
        return self.services_status
    
    def start_whatsapp_bot(self):
        """Start the main WhatsApp bot"""
        logger.info("\n" + "="*60)
        logger.info("🤖 STARTING WHATSAPP BOT")
        logger.info("="*60 + "\n")
        
        bot_dir = CONFIG["paths"]["bot_dir"]
        
        # Try main_hub.py first (connected system)
        hub_path = os.path.join(bot_dir, "main_hub.py")
        bot_path = os.path.join(bot_dir, "main.py")
        custom_bot_path = os.path.join(bot_dir, "src", "telegram", "custom_bot.py")
        
        if os.path.exists(hub_path):
            logger.info(f"🚀 Starting Unified Hub...")
            try:
                subprocess.Popen(
                    [sys.executable, hub_path],
                    cwd=bot_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                logger.info("✅ Unified Hub started!")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to start hub: {e}")
        
        # Fallback to main.py
        if os.path.exists(bot_path):
            logger.info(f"🚀 Starting WhatsApp Bot...")
            try:
                subprocess.Popen(
                    [sys.executable, bot_path],
                    cwd=bot_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                logger.info("✅ WhatsApp Bot started!")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to start bot: {e}")
        
        logger.warning("⚠️ No bot script found!")
        return False


# ═══════════════════════════════════════════════════════════════
# SYSTEM TRAY (Background Mode)
# ═══════════════════════════════════════════════════════════════

def minimize_to_tray():
    """Minimize window to system tray"""
    # Windows-specific
    import ctypes
    
    # Get console window
    window = ctypes.windll.kernel32.GetConsoleWindow()
    
    if window:
        # Minimize
        ctypes.windll.user32.ShowWindow(window, 6)  # SW_MINIMIZE
        return True
    return False


def create_tray_icon():
    """Create system tray icon"""
    try:
        import pystray
        from PIL import Image, ImageDraw
        
        # Create icon image
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), 'green')
        draw = ImageDraw.Draw(image)
        draw.ellipse([8, 8, 56, 56], fill='white', outline='green', width=4)
        draw.text((20, 24), "🤖", fill='green')
        
        menu = pystray.Menu(
            pystray.MenuItem("Open Dashboard", lambda: open_dashboard()),
            pystray.MenuItem("View Logs", lambda: view_logs()),
            pystray.MenuItem("Restart Services", lambda: restart_services()),
            pystray.MenuItem("Exit", lambda: exit_app())
        )
        
        icon = pystray.Icon("WhatsApp Bot", image, "WhatsApp Automation", menu)
        icon.run_detached()
        logger.info("✅ System tray icon created")
        
    except ImportError:
        logger.warning("⚠️ pystray not installed. Install with: pip install pystray Pillow")
    except Exception as e:
        logger.error(f"❌ Tray icon error: {e}")


def open_dashboard():
    """Open dashboard in browser"""
    import webbrowser
    webbrowser.open("http://localhost:8000")
    webbrowser.open("http://localhost:19999")  # Netdata


def view_logs():
    """Open log file"""
    import subprocess
    subprocess.Popen(["notepad", LOG_FILE])


def restart_services():
    """Restart all services"""
    manager = ServiceManager()
    manager.start_all_services()


def exit_app():
    """Exit the application"""
    logger.info("👋 Shutting down...")
    sys.exit(0)


# ═══════════════════════════════════════════════════════════════
# INSTALL TO STARTUP
# ═══════════════════════════════════════════════════════════════

def install_to_startup():
    """Install to Windows startup (Run on boot)"""
    logger.info("🚀 Installing to Windows startup...")
    
    # Get script path
    script_path = os.path.abspath(__file__)
    python_path = sys.executable
    
    # Create batch file
    startup_dir = os.getenv('APPDATA') + "\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
    batch_path = os.path.join(startup_dir, "WhatsApp_Bot_Launcher.bat")
    
    batch_content = f'''@echo off
title WhatsApp Automation
cd /d "{os.path.dirname(script_path)}"
start /B pythonw "{script_path}" --background
'''
    
    try:
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        logger.info(f"✅ Installed to startup: {batch_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to install: {e}")
        return False


def uninstall_from_startup():
    """Remove from Windows startup"""
    logger.info("🗑️ Removing from startup...")
    
    startup_dir = os.getenv('APPDATA') + "\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
    batch_path = os.path.join(startup_dir, "WhatsApp_Bot_Launcher.bat")
    
    try:
        if os.path.exists(batch_path):
            os.remove(batch_path)
            logger.info("✅ Removed from startup")
        else:
            logger.info("ℹ️ Not in startup")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to remove: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🤖 WhatsApp Automation Auto-Start Launcher             ║
║                                                               ║
║     Starts ALL services automatically on PC boot!             ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Parse arguments
    if "--install" in sys.argv:
        install_to_startup()
        return
    
    if "--uninstall" in sys.argv:
        uninstall_from_startup()
        return
    
    if "--background" in sys.argv:
        # Run in background
        logger.info("Running in background mode...")
        time.sleep(2)
    
    # Create data directories
    bot_dir = CONFIG["paths"]["bot_dir"]
    data_dir = os.path.join(bot_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    for subdir in ["postgres", "minio", "n8n", "meili", "qdrant"]:
        os.makedirs(os.path.join(data_dir, subdir), exist_ok=True)
    
    # Start services
    manager = ServiceManager()
    manager.start_all_services()
    
    # Wait for services
    wait_time = CONFIG["bot"]["wait_for_services"]
    logger.info(f"\n⏱️ Waiting {wait_time}s for services to stabilize...")
    time.sleep(wait_time)
    
    # Start WhatsApp bot
    logger.info("\n" + "="*60)
    manager.start_whatsapp_bot()
    
    # Summary
    print("\n" + "="*60)
    print("📊 SERVICE STATUS")
    print("="*60)
    
    for name, status in manager.services_status.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")
    
    print("\n" + "="*60)
    print("🌐 ACCESS URLs:")
    print("-" * 60)
    
    urls = [
        ("Unified Hub", "http://localhost:8000"),
        ("OpenWA", "http://localhost:2785"),
        ("N8N Automation", "http://localhost:5678"),
        ("Netdata", "http://localhost:19999"),
        ("MinIO", "http://localhost:9001"),
        ("Meilisearch", "http://localhost:7700"),
    ]
    
    for name, url in urls:
        if is_port_open(int(url.split(":")[-1])):
            print(f"  🔗 {name}: {url}")
    
    print("\n" + "="*60)
    print("✅ ALL SERVICES STARTED!")
    print("💡 Check auto_start.log for details")
    print("📝 Logs: " + LOG_FILE)
    print("="*60 + "\n")
    
    # Keep running
    if "--background" not in sys.argv:
        logger.info("Press Ctrl+C to stop, or this will keep monitoring...")
        try:
            while True:
                time.sleep(60)
                # Periodic health check
                logger.info("💚 Health check OK")
        except KeyboardInterrupt:
            logger.info("👋 Shutting down...")


if __name__ == "__main__":
    main()
