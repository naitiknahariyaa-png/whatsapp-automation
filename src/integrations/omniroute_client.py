"""
OmniRoute Integration - Universal AI Gateway
Connect to 250+ AI providers, 90+ FREE, auto-fallback, save 15-95% tokens!

Website: https://omniroute.onl
GitHub: https://github.com/diegosouzapw/OmniRoute

Features:
- 250+ AI providers
- 90+ FREE providers
- ~1.6B free tokens/month
- Auto-fallback (never hit limits)
- Token compression (RTK + Caveman)
- 18 routing strategies

Setup:
1. npm install -g omniroute
2. omniroute start
3. Configure providers
4. Connect to http://localhost:20128
"""

import os
import logging
import requests
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class OmniRouteClient:
    """
    OmniRoute AI Gateway Client
    
    OmniRoute is the FREE AI gateway that connects to 250+ providers.
    - 90+ providers with FREE tiers
    - Auto-fallback (never hit limits)
    - Token compression (15-95% savings)
    - Works with Claude, GPT, Gemini, and more
    
    Setup:
    1. Install OmniRoute: npm install -g omniroute
    2. Start: omniroute start
    3. Configure providers: omniroute config add openrouter KEY
    4. Access dashboard: http://localhost:20128
    
    Environment:
    - OMNIROUTE_URL=http://localhost:20128
    - OMNIROUTE_API_KEY= (optional, for local)
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.url = url or os.getenv("OMNIROUTE_URL", "http://localhost:20128")
        self.api_key = api_key or os.getenv("OMNIROUTE_API_KEY", "")
        self.api_v1 = f"{self.url}/v1"
        
        self.enabled = self.is_available()
        
        if self.enabled:
            logger.info(f"✅ OmniRoute connected: {self.url}")
            self._log_providers()
        else:
            logger.warning("⚠️ OmniRoute not running")
            logger.info("   Install: npm install -g omniroute")
            logger.info("   Start: omniroute start")
    
    def is_available(self) -> bool:
        """Check if OmniRoute server is running"""
        try:
            response = requests.get(f"{self.url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _log_providers(self):
        """Log available providers"""
        try:
            providers = self.get_providers()
            if providers:
                free_count = sum(1 for p in providers if p.get("is_free", False))
                logger.info(f"   📡 {len(providers)} providers available, {free_count} FREE")
        except:
            pass
    
    def get_providers(self) -> List[Dict]:
        """Get list of configured providers"""
        try:
            response = requests.get(
                f"{self.api_v1}/providers",
                headers=self._get_headers(),
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("providers", [])
            return []
        except:
            return []
    
    def get_free_providers(self) -> List[Dict]:
        """Get list of FREE providers only"""
        try:
            response = requests.get(
                f"{self.api_v1}/providers?free=true",
                headers=self._get_headers(),
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("providers", [])
            return []
        except:
            return []
    
    def _get_headers(self) -> Dict:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def get_response(
        self,
        message: str,
        model: str = "auto",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 256
    ) -> Optional[str]:
        """
        Get AI response through OmniRoute
        
        Args:
            message: User's message
            model: Model ID (default: "auto" - uses best available)
            system_prompt: System instructions
            temperature: Creativity (0.0-1.0)
            max_tokens: Max response length
        
        Returns:
            AI response string or None on error
        """
        if not self.enabled:
            return None
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        try:
            response = requests.post(
                f"{self.api_v1}/chat/completions",
                headers=self._get_headers(),
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
            else:
                logger.error(f"OmniRoute error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error("OmniRoute timeout")
        except Exception as e:
            logger.error(f"OmniRoute error: {e}")
        
        return None
    
    def get_status(self) -> Dict:
        """Get OmniRoute status"""
        providers = self.get_providers()
        free_providers = self.get_free_providers()
        
        return {
            "available": self.enabled,
            "url": self.url,
            "total_providers": len(providers),
            "free_providers": len(free_providers),
        }
    
    def test_connection(self) -> bool:
        """Test OmniRoute connection"""
        if not self.enabled:
            return False
        
        result = self.get_response("Hello!")
        return result is not None


# Pre-built model shortcuts
FREE_MODELS = {
    "auto": "auto",
    "fast": "auto/fast",
    "cheap": "auto/cheap",
    "coding": "auto/coding",
    "claude": "anthropic/claude-3-haiku",
    "gpt4": "openai/gpt-4o-mini",
    "gemini": "google/gemini-2.0-flash",
    "deepseek": "deepseek/deepseek-r1",
    "llama": "meta-llama/llama-3.1-8b-instruct",
}


def setup_omniroute():
    """Guide user to setup OmniRoute"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           OmniRoute AI Gateway Setup (FREE!)               ║
╠══════════════════════════════════════════════════════════════╣
║  🚀 250+ AI Providers  |  90+ FREE  |  ~1.6B Free Tokens  ║
╚══════════════════════════════════════════════════════════════╝

QUICK SETUP:

1. Install OmniRoute:
   npm install -g omniroute

2. Start OmniRoute:
   omniroute start

3. Access Dashboard:
   http://localhost:20128

4. Add Providers (FREE):
   omniroute config add openrouter YOUR_KEY
   omniroute config add groq YOUR_KEY

5. Add to .env:
   OMNIROUTE_URL=http://localhost:20128

USAGE:
   from src.integrations import OmniRouteClient
   
   client = OmniRouteClient()
   response = client.get_response("Hello!")

DOCS: https://github.com/diegosouzapw/OmniRoute
""")


if __name__ == "__main__":
    setup_omniroute()
