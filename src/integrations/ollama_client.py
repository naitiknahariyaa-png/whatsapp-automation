"""
Ollama Local AI - FREE AI models on your computer
No API costs, fully private, works offline!
"""

import os
import logging
import requests
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class OllamaAI:
    """
    Ollama Local AI Client
    
    FREE models you can run:
    - llama3.2 (2GB) - Fast, good quality
    - mistral (4GB) - Very good quality
    - phi (1GB) - Small, very fast
    - deepseek-r1 (7GB) - Excellent reasoning
    
    Setup:
    1. Install: https://ollama.com/download
    2. Download model: ollama pull llama3.2
    3. Start server: ollama serve
    
    Environment:
    - OLLAMA_URL=http://localhost:11434
    - OLLAMA_MODEL=llama3.2
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.url = url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
        self.api_generate = f"{self.url}/api/generate"
        self.api_tags = f"{self.url}/api/tags"
        
        self.enabled = self.is_available()
        
        if self.enabled:
            logger.info(f"✅ Ollama AI connected: {self.model}")
        else:
            logger.warning("⚠️ Ollama not running (start with: ollama serve)")
    
    def is_available(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(self.api_tags, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_models(self) -> List[Dict]:
        """Get list of available models"""
        try:
            response = requests.get(self.api_tags, timeout=5)
            if response.status_code == 200:
                return response.json().get("models", [])
            return []
        except:
            return []
    
    def get_response(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        context: str = ""
    ) -> Optional[str]:
        """
        Get AI response
        
        Args:
            message: User's message
            system_prompt: System instructions
            context: Previous conversation context
        """
        if not self.enabled:
            return None
        
        prompt = self._build_prompt(message, system_prompt, context)
        
        try:
            response = requests.post(
                self.api_generate,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 256  # Max tokens
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Ollama timeout - try smaller model")
            return None
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return None
    
    def _build_prompt(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        context: str = ""
    ) -> str:
        """Build prompt with system instructions"""
        if system_prompt:
            return f"""System: {system_prompt}

Context: {context}

User: {message}

Assistant:"""
        
        return f"""You are a helpful WhatsApp bot assistant for a business.
Be friendly, concise, and helpful.
Respond in the same language as the user.

User: {message}

Assistant:"""
    
    def get_status(self) -> Dict:
        """Get Ollama status"""
        models = self.get_models()
        return {
            "available": self.enabled,
            "model": self.model,
            "url": self.url,
            "models": [m.get("name") for m in models]
        }


# Quick setup function
def setup_ollama():
    """Guide user to setup Ollama"""
    print("""
╔══════════════════════════════════════════════════════════╗
║           Ollama Local AI Setup (FREE!)                 ║
╚══════════════════════════════════════════════════════════╝

1. Install Ollama:
   Mac/Linux: curl -fsSL https://ollama.com/install.sh | sh
   Windows: Download from https://ollama.com/download

2. Download a model (FREE, no API costs):
   ollama pull llama3.2        # 2GB - Fast, good
   ollama pull mistral         # 4GB - Very good quality
   ollama pull phi             # 1GB - Very fast
   ollama pull deepseek-r1     # 7GB - Best reasoning

3. Start Ollama:
   ollama serve

4. Add to .env:
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2

Benefits:
✅ 100% FREE
✅ No internet needed
✅ Super private
✅ No API limits

RAM Requirements:
- 8GB RAM: phi, llama3.2
- 16GB RAM: mistral
- 32GB RAM: deepseek-r1
""")


def install_models():
    """List commands to install models"""
    print("""
╔════════════════════════════════════════╗
║         Install Ollama Models         ║
╚════════════════════════════════════════╝

Run these commands:

ollama pull llama3.2
ollama pull mistral  
ollama pull phi
ollama pull deepseek-r1

Check installed:
ollama list

Start server:
ollama serve
""")


if __name__ == "__main__":
    setup_ollama()
