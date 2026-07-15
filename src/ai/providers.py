"""
====================================================================
AI PROVIDERS - OpenRouter, Groq, Keyword (Multi-Provider)
====================================================================
"""

import hashlib
import time
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AICache:
    """Simple in-memory cache for AI responses"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.max_size = max_size
        self.ttl = ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[str]:
        """Get cached response if not expired"""
        if key in self.cache:
            response, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.hits += 1
                return response
            else:
                del self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: str):
        """Cache a response"""
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = (value, time.time())
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%"
        }
    
    def clear(self):
        """Clear the cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0


class AIBase(ABC):
    """Base class for AI providers"""
    
    @abstractmethod
    def generate(self, message: str, context: str = "") -> Optional[str]:
        """Generate AI response"""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider is configured"""
        pass


class KeywordAI(AIBase):
    """Simple keyword-based AI - No API needed!"""
    
    def __init__(self):
        self.defaults = {
            "hi": "Hello! 👋 Welcome! How can I help you?",
            "hello": "Hi there! 😊 How may I assist you?",
            "hey": "Hey! What's up? 😄",
            "price": "For our best prices, please tell me which product you're interested in!",
            "cost": "Our prices are very competitive!",
            "available": "Yes, we're available! 🕐 We're open 9 AM to 9 PM.",
            "hours": "We're open 9 AM to 9 PM, all days! 🌟",
            "thank": "You're welcome! 😊",
            "thanks": "Happy to help! 🙌",
            "bye": "Goodbye! Have a great day! 👋",
            "help": "I can help with: Product info, Prices, Orders, Hours, Location. Just ask! 😊",
            "order": "Great choice! To place an order, please tell us what you'd like. 🛒",
            "contact": "You can reach us at [Your Phone]! 📞",
            "delivery": "Yes! We deliver all over India! 🚚 Delivery takes 3-5 business days.",
            "location": "We're located at [Your Address]. 📍",
            "menu": "📋 Our Menu:\n☕ Coffee\n🍔 Burgers\n🍕 Pizza\n🍝 Pasta\n🍰 Desserts\n\nWhat would you like?",
        }
    
    def generate(self, message: str, context: str = "") -> Optional[str]:
        """Generate response based on keywords"""
        message_lower = message.lower().strip()
        
        for keyword, response in self.defaults.items():
            if keyword in message_lower:
                return response
        
        return "Thanks for your message! We'll get back to you shortly. 🙏"
    
    def is_configured(self) -> bool:
        return True


class OpenRouterAI(AIBase):
    """
    OpenRouter - FREE AI Models
    Get API key: https://openrouter.ai/keys
    """
    
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    FREE_MODELS = [
        "openrouter/free",
        "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "google/gemma-4-26b-a4b-it:free",
    ]
    
    def __init__(self, api_key: Optional[str] = None, model: str = "openrouter/free"):
        self.api_key = api_key
        self.model = model
        self.cache = AICache()
    
    def set_api_key(self, api_key: str):
        """Set API key"""
        self.api_key = api_key
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    def generate(self, message: str, context: str = "") -> Optional[str]:
        """Generate AI response"""
        cache_key = hashlib.md5(f"{message}|{context}".encode()).hexdigest()
        
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
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
Be helpful, polite, and professional."""
            
            if context:
                system_prompt += f"\n\nConversation history:\n{context}"
            
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
                self.cache.set(cache_key, ai_response)
                return ai_response
            else:
                logger.error(f"OpenRouter Error: {response.status_code}")
                return None
                
        except ImportError:
            logger.error("requests library not installed")
            return None
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return None


class GroqAI(AIBase):
    """Groq AI - Fast and Free"""
    
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key
        self.model = model
        self.cache = AICache()
    
    def set_api_key(self, api_key: str):
        """Set API key"""
        self.api_key = api_key
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    def generate(self, message: str, context: str = "") -> Optional[str]:
        """Generate AI response"""
        cache_key = hashlib.md5(f"{message}|{context}".encode()).hexdigest()
        
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        if not self.api_key:
            return None
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            system_prompt = """You are a helpful WhatsApp assistant for a small Indian business.
Keep responses SHORT and FRIENDLY (1-2 sentences max).
Respond in the same language as the user.
Be helpful, polite, and professional."""
            
            if context:
                system_prompt += f"\n\nConversation history:\n{context}"
            
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
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                self.cache.set(cache_key, ai_response)
                return ai_response
            else:
                logger.error(f"Groq Error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return None


class AIManager:
    """
    Multi-provider AI Router
    Tries providers in order: OpenRouter > Groq > Keyword
    """
    
    def __init__(self):
        self.keyword = KeywordAI()
        self.openrouter = OpenRouterAI()
        self.groq = GroqAI()
        self.current_provider = "keyword"
    
    def configure(self, provider: str, api_key: Optional[str] = None, model: Optional[str] = None):
        """Configure AI provider"""
        if provider == "openrouter" and api_key:
            self.openrouter.set_api_key(api_key)
            if model:
                self.openrouter.model = model
            self.current_provider = "openrouter"
        elif provider == "groq" and api_key:
            self.groq.set_api_key(api_key)
            if model:
                self.groq.model = model
            self.current_provider = "groq"
        else:
            self.current_provider = "keyword"
    
    def generate(self, message: str, context: str = "") -> tuple[Optional[str], str]:
        """Generate response using best available provider"""
        # Try OpenRouter first (free models)
        if self.openrouter.is_configured():
            response = self.openrouter.generate(message, context)
            if response:
                return response, "openrouter"
        
        # Try Groq second (fast)
        if self.groq.is_configured():
            response = self.groq.generate(message, context)
            if response:
                return response, "groq"
        
        # Fall back to keyword AI
        response = self.keyword.generate(message, context)
        return response, "keyword"
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {
            "current": self.current_provider,
            "openrouter": self.openrouter.is_configured(),
            "groq": self.groq.is_configured(),
            "keyword": True,
            "cache": self.openrouter.cache.stats()
        }
