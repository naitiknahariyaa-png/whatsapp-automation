"""
====================================================================
OpenRouter AI Client - FREE Models (Kimi, GLM, and 100+ more!)
====================================================================

FREE AI Models available:
- Kimi (Moonshot AI)
- GLM-5.2
- OpenChat
- And 100+ more!

Get your free API key: https://openrouter.ai/keys

Author: Built for Indian Businesses 🇮🇳
====================================================================
"""

import time
import json
from pathlib import Path


class OpenRouterAI:
    """
    OpenRouter - Access 100+ AI models for FREE!
    
    How to get API key:
    1. Go to: https://openrouter.ai/keys
    2. Sign up (FREE)
    3. Get your API key
    4. Paste it in the bot!
    
    FREE Models:
    - openchat/openchat-7b
    - nousresearch/hermes-3-llama-3.1-8b
    - meta-llama/llama-3.2-3b-instruct
    - mistralai/mistral-7b-instruct
    - And many more...
    """
    
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    # Best FREE models (fastest first)
    FREE_MODELS = [
        "openchat/openchat-7b",           # Very fast, good quality
        "nousresearch/hermes-3-llama-3.1-8b",  # Great quality
        "meta-llama/llama-3.2-3b-instruct",     # Meta's best
        "mistralai/mistral-7b-instruct",        # Fast and capable
        "google/gemma-2-2b-it",                 # Google's model
        "anthropic/claude-3-haiku",             # Claude's budget option
    ]
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.model = self.FREE_MODELS[0]  # Default to fastest
        self.cache = {}  # Response cache
        self.cache_enabled = True
        self.cache_max_size = 1000
        
    def set_api_key(self, api_key):
        """Set API key and save to config"""
        self.api_key = api_key
        self._save_config()
        
    def _save_config(self):
        """Save config to file"""
        config = {}
        config_path = Path("config.yaml")
        
        if config_path.exists():
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        
        config['ai'] = config.get('ai', {})
        config['ai']['openrouter_api_key'] = self.api_key
        config['ai']['ai_type'] = 'openrouter'
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
    
    def _load_config(self):
        """Load config from file"""
        import yaml
        config_path = Path("config.yaml")
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
            self.api_key = config.get('ai', {}).get('openrouter_api_key')
            return config.get('ai', {})
        return {}
    
    def is_configured(self):
        """Check if API key is set"""
        return bool(self.api_key)
    
    def set_model(self, model_name):
        """Change AI model"""
        if model_name in self.FREE_MODELS:
            self.model = model_name
            return True
        return False
    
    def get_available_models(self):
        """Get list of available free models"""
        return self.FREE_MODELS
    
    def generate(self, message, context=""):
        """Generate AI response with caching"""
        
        # Create cache key
        cache_key = self._get_cache_key(message, context)
        
        # Check cache first
        if self.cache_enabled and cache_key in self.cache:
            return self.cache[cache_key]
        
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
Be helpful, polite, and professional.
Use emojis sparingly."""
            
            if context:
                system_prompt += f"\n\nPrevious conversation:\n{context}"
            
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
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                
                # Cache the response
                self._cache_response(cache_key, ai_response)
                
                return ai_response
            else:
                print(f"OpenRouter Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except ImportError:
            print("Please install requests: pip install requests")
            return None
        except Exception as e:
            print(f"AI Error: {e}")
            return None
    
    def _get_cache_key(self, message, context):
        """Generate cache key for message"""
        import hashlib
        text = f"{message}|{context}"
        return hashlib.md5(text.encode()).hexdigest()
    
    def _cache_response(self, key, response):
        """Cache a response"""
        if len(self.cache) >= self.cache_max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = response
    
    def clear_cache(self):
        """Clear response cache"""
        self.cache = {}
        print("Cache cleared!")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.cache_max_size,
            "enabled": self.cache_enabled
        }
    
    def test_connection(self):
        """Test if API key works"""
        if not self.api_key:
            return False, "No API key set"
        
        try:
            test = self.generate("Say 'Hello' in one word")
            if test:
                return True, f"Working! Model: {self.model}"
            else:
                return False, "API key may be invalid"
        except Exception as e:
            return False, str(e)


class MultiProviderRouter:
    """
    Router that can switch between different AI providers
    Priority: OpenRouter (free) > Groq (fast) > Keyword (offline)
    """
    
    def __init__(self):
        self.openrouter = OpenRouterAI()
        self.groq = None
        self.keyword_ai = None
        self.current_provider = "keyword"
        
    def setup_openrouter(self, api_key):
        """Setup OpenRouter"""
        self.openrouter.set_api_key(api_key)
        self.current_provider = "openrouter"
        
    def setup_groq(self, api_key):
        """Setup Groq (faster but needs account)"""
        from main import GroqAI  # Lazy import
        self.groq = GroqAI(api_key)
        self.current_provider = "groq"
        
    def generate(self, message, context=""):
        """Generate response using best available provider"""
        
        # Try OpenRouter first (free)
        if self.openrouter.is_configured():
            response = self.openrouter.generate(message, context)
            if response:
                return response, "openrouter"
        
        # Try Groq second (fast)
        if self.groq and self.groq.is_configured():
            response = self.groq.generate(message)
            if response:
                return response, "groq"
        
        # Fall back to keyword AI
        if self.keyword_ai:
            response = self.keyword_ai.generate(message)
            return response, "keyword"
        
        return None, "none"
    
    def get_status(self):
        """Get status of all providers"""
        return {
            "openrouter": self.openrouter.is_configured(),
            "groq": self.groq.is_configured() if self.groq else False,
            "keyword": self.keyword_ai is not None,
            "current": self.current_provider
        }
