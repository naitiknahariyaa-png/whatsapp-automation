"""
OpenWA Memory - Persistent Configuration Storage
Saves and loads OpenWA API credentials automatically
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Config file path
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
CONFIG_FILE = CONFIG_DIR / "openwa_config.json"


class OpenWAMemory:
    """
    Persistent memory for OpenWA configuration
    Saves API key, URL, and session info
    """
    
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self._ensure_config_dir()
        self._ensure_config_file()
        self.config = self._load_config()
    
    def _ensure_config_dir(self):
        """Create config directory if not exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Config directory: {self.config_dir}")
    
    def _ensure_config_file(self):
        """Create config file with defaults if not exists"""
        if not self.config_file.exists():
            default_config = {
                "openwa_url": "http://localhost:2785",
                "openwa_api_key": "",
                "openwa_session_id": "default",
                "whatsapp_connected": False,
                "last_updated": ""
            }
            self._save_config(default_config)
            logger.info("Created new OpenWA config file")
    
    def _load_config(self) -> dict:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                logger.info("Loaded OpenWA config from memory")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _save_config(self, config: dict):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("Saved OpenWA config to memory")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def save_credentials(
        self,
        api_key: str,
        url: str = "http://localhost:2785",
        session_id: str = "default"
    ):
        """
        Save OpenWA credentials to memory
        
        Args:
            api_key: Your OpenWA API key
            url: OpenWA URL (default: http://localhost:2785)
            session_id: Session ID (default: default)
        """
        self.config = {
            "openwa_url": url,
            "openwa_api_key": api_key,
            "openwa_session_id": session_id,
            "whatsapp_connected": True,
            "last_updated": datetime.now().isoformat()
        }
        self._save_config(self.config)
        print(f"✅ Credentials saved!")
        print(f"   URL: {url}")
        print(f"   Session: {session_id}")
        print(f"   Key: {api_key[:10]}...{api_key[-5:]}")
    
    def load_credentials(self) -> dict:
        """Load saved credentials"""
        if self.config.get("openwa_api_key"):
            logger.info("Loaded credentials from memory")
            return {
                "url": self.config.get("openwa_url", "http://localhost:2785"),
                "api_key": self.config.get("openwa_api_key"),
                "session_id": self.config.get("openwa_session_id", "default"),
                "connected": self.config.get("whatsapp_connected", False)
            }
        return {}
    
    def is_configured(self) -> bool:
        """Check if OpenWA is configured"""
        return bool(self.config.get("openwa_api_key"))
    
    def get_api_key(self) -> str:
        """Get saved API key"""
        return self.config.get("openwa_api_key", "")
    
    def get_url(self) -> str:
        """Get saved URL"""
        return self.config.get("openwa_url", "http://localhost:2785")
    
    def get_session_id(self) -> str:
        """Get saved session ID"""
        return self.config.get("openwa_session_id", "default")
    
    def update_connection_status(self, connected: bool):
        """Update WhatsApp connection status"""
        self.config["whatsapp_connected"] = connected
        self.config["last_updated"] = datetime.now().isoformat()
        self._save_config(self.config)
    
    def clear_credentials(self):
        """Clear all saved credentials"""
        self.config = {
            "openwa_url": "http://localhost:2785",
            "openwa_api_key": "",
            "openwa_session_id": "default",
            "whatsapp_connected": False,
            "last_updated": ""
        }
        self._save_config(self.config)
        logger.info("Cleared OpenWA credentials")


def setup_openwa_memory():
    """Interactive setup for OpenWA memory"""
    print("\n" + "="*50)
    print("🔑 OpenWA Memory Setup")
    print("="*50 + "\n")
    
    memory = OpenWAMemory()
    
    # Check if already configured
    if memory.is_configured():
        print("📋 Current configuration:")
        creds = memory.load_credentials()
        print(f"   URL: {creds['url']}")
        print(f"   Session: {creds['session_id']}")
        print(f"   Connected: {creds['connected']}")
        print("")
        
        response = input("Update credentials? (y/n): ").strip().lower()
        if response != 'y':
            print("Keeping existing configuration.")
            return memory
    else:
        print("No saved credentials found.\n")
    
    # Get new credentials
    print("Enter your OpenWA credentials:\n")
    
    url = input("OpenWA URL (press Enter for default): ").strip()
    if not url:
        url = "http://localhost:2785"
    
    api_key = input("API Key: ").strip()
    if not api_key:
        print("❌ API key is required!")
        return None
    
    session_id = input("Session ID (press Enter for 'default'): ").strip()
    if not session_id:
        session_id = "default"
    
    # Save
    memory.save_credentials(api_key, url, session_id)
    print("\n✅ Configuration saved!")
    print("   Run your bot and it will auto-load these credentials.\n")
    
    return memory


if __name__ == "__main__":
    setup_openwa_memory()
