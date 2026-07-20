"""
🤖 Enhanced AI Engine v2.0
=========================
Multi-provider AI engine with fallbacks, caching, and analytics.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Available AI providers."""
    GROQ = "groq"
    OPENROUTER = "openrouter"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    KEYWORD = "keyword"  # Fallback - no API needed


@dataclass
class AIResponse:
    """Response from AI engine."""
    text: str
    provider: str
    model: str
    latency_ms: float
    cached: bool = False
    tokens_used: Optional[int] = None


@dataclass
class ProviderConfig:
    """Configuration for AI provider."""
    provider: AIProvider
    api_key: Optional[str] = None
    model: str = "llama-3.1-8b-instant"
    base_url: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    timeout: int = 30


class CacheManager:
    """Simple file-based cache for AI responses."""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "ai_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            self.cache_file.write_text(json.dumps(self.cache, indent=2))
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def get(self, key: str) -> Optional[str]:
        """Get cached response."""
        entry = self.cache.get(key)
        if entry and time.time() - entry.get('timestamp', 0) < 3600:  # 1 hour TTL
            return entry.get('response')
        return None
    
    def set(self, key: str, response: str):
        """Cache response."""
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
        self._save_cache()
    
    def clear(self):
        """Clear cache."""
        self.cache = {}
        self._save_cache()


class AnalyticsTracker:
    """Track AI usage analytics."""
    
    def __init__(self, stats_file: str = "data/ai_stats.json"):
        self.stats_file = Path(stats_file)
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """Load stats from disk."""
        if self.stats_file.exists():
            try:
                return json.loads(self.stats_file.read_text())
            except:
                return self._default_stats()
        return self._default_stats()
    
    def _default_stats(self) -> Dict:
        """Default stats structure."""
        return {
            'total_requests': 0,
            'cache_hits': 0,
            'providers_used': {},
            'total_tokens': 0,
            'avg_latency_ms': 0,
            'errors': 0
        }
    
    def _save_stats(self):
        """Save stats to disk."""
        try:
            self.stats_file.write_text(json.dumps(self.stats, indent=2))
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")
    
    def track(self, provider: str, latency_ms: float, cached: bool = False, tokens: int = 0):
        """Track a request."""
        self.stats['total_requests'] += 1
        if cached:
            self.stats['cache_hits'] += 1
        
        if provider not in self.stats['providers_used']:
            self.stats['providers_used'][provider] = 0
        self.stats['providers_used'][provider] += 1
        
        self.stats['total_tokens'] += tokens
        
        # Update average latency
        n = self.stats['total_requests']
        current_avg = self.stats['avg_latency_ms']
        self.stats['avg_latency_ms'] = (current_avg * (n - 1) + latency_ms) / n
    
    def track_error(self):
        """Track an error."""
        self.stats['errors'] += 1
    
    def get_stats(self) -> Dict:
        """Get current stats."""
        return {
            **self.stats,
            'cache_hit_rate': (
                self.stats['cache_hits'] / self.stats['total_requests'] * 100
                if self.stats['total_requests'] > 0 else 0
            )
        }


class AIEngine:
    """
    Enhanced AI Engine with multi-provider support.
    
    Usage:
        engine = AIEngine()
        response = engine.generate("Hello, how can you help me?")
        print(response.text)
    """
    
    # Default templates for keyword fallback
    DEFAULT_TEMPLATES = {
        "hi": "Hello! 👋 Welcome! How can I help you today?",
        "hello": "Hi there! 😊 How may I assist you?",
        "price": "Our prices are very competitive! What product are you interested in?",
        "order": "Great! To place an order, please tell us:\n1. Your Name\n2. What items you want\n3. Your delivery address",
        "delivery": "Yes! We deliver all over India. Delivery takes 2-5 business days.",
        "hours": "We're open 9 AM - 9 PM, all days! 🌟",
        "contact": "You can reach us at our WhatsApp or email us anytime!",
        "thanks": "You're welcome! 😊 Is there anything else I can help with?",
        "bye": "Goodbye! Have a great day! 👋"
    }
    
    def __init__(
        self,
        providers: Optional[List[ProviderConfig]] = None,
        cache_enabled: bool = True,
        analytics_enabled: bool = True
    ):
        self.providers = providers or []
        self.cache = CacheManager() if cache_enabled else None
        self.analytics = AnalyticsTracker() if analytics_enabled else None
        self.current_provider = None
        self._init_providers()
    
    def _init_providers(self):
        """Initialize configured providers."""
        # Auto-detect from environment
        if not self.providers:
            # Groq
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key:
                self.providers.append(ProviderConfig(
                    provider=AIProvider.GROQ,
                    api_key=groq_key,
                    model="llama-3.1-8b-instant"
                ))
            
            # OpenRouter
            openrouter_key = os.getenv("OPENROUTER_API_KEY")
            if openrouter_key:
                self.providers.append(ProviderConfig(
                    provider=AIProvider.OPENROUTER,
                    api_key=openrouter_key,
                    model="anthropic/claude-3-haiku"
                ))
            
            # Gemini
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                self.providers.append(ProviderConfig(
                    provider=AIProvider.GEMINI,
                    api_key=gemini_key,
                    model="gemini-pro"
                ))
        
        # Set first available as current
        if self.providers:
            self.current_provider = self.providers[0]
        else:
            logger.info("No AI providers configured, using keyword fallback")
    
    def _get_cache_key(self, prompt: str, context: str = "") -> str:
        """Generate cache key."""
        return f"{prompt}:{context}".lower().strip()
    
    def _generate_keyword_response(self, message: str) -> AIResponse:
        """Generate response using keyword matching."""
        message_lower = message.lower().strip()
        
        # Check templates
        for keyword, response in self.DEFAULT_TEMPLATES.items():
            if keyword in message_lower:
                return AIResponse(
                    text=response,
                    provider="keyword",
                    model="templates",
                    latency_ms=0,
                    cached=False
                )
        
        # Default response
        return AIResponse(
            text="Thanks for your message! We'll get back to you shortly. 🙏",
            provider="keyword",
            model="templates",
            latency_ms=0,
            cached=False
        )
    
    async def _generate_groq(self, message: str, config: ProviderConfig, context: str = "") -> AIResponse:
        """Generate response using Groq."""
        start_time = time.time()
        
        try:
            from groq import Groq
            client = Groq(api_key=config.api_key)
            
            chat = client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant. Keep responses SHORT (1-2 sentences)."},
                    {"role": "user", "content": message}
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            latency = (time.time() - start_time) * 1000
            
            return AIResponse(
                text=chat.choices[0].message.content,
                provider="groq",
                model=config.model,
                latency_ms=latency,
                tokens_used=chat.usage.total_tokens if hasattr(chat, 'usage') else None
            )
        except Exception as e:
            logger.error(f"Groq error: {e}")
            raise
    
    async def generate(
        self,
        message: str,
        context: str = "",
        force_provider: Optional[AIProvider] = None
    ) -> AIResponse:
        """
        Generate AI response.
        
        Args:
            message: User message
            context: Additional context
            force_provider: Force specific provider
            
        Returns:
            AIResponse with text and metadata
        """
        # Check cache
        if self.cache:
            cache_key = self._get_cache_key(message, context)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                if self.analytics:
                    self.analytics.track("cache", 0, cached=True)
                return AIResponse(
                    text=cached_response,
                    provider="cache",
                    model="cached",
                    latency_ms=0,
                    cached=True
                )
        
        # Try providers in order
        providers_to_try = (
            [p for p in self.providers if p.provider == force_provider]
            if force_provider
            else self.providers
        )
        
        for config in providers_to_try:
            try:
                if config.provider == AIProvider.GROQ:
                    response = await self._generate_groq(message, config, context)
                    
                    # Cache the response
                    if self.cache:
                        self.cache.set(cache_key, response.text)
                    
                    # Track analytics
                    if self.analytics:
                        self.analytics.track(
                            config.provider.value,
                            response.latency_ms,
                            tokens=response.tokens_used or 0
                        )
                    
                    return response
            
            except Exception as e:
                logger.warning(f"Provider {config.provider} failed: {e}")
                if self.analytics:
                    self.analytics.track_error()
                continue
        
        # Fallback to keyword matching
        return self._generate_keyword_response(message)
    
    def get_stats(self) -> Dict:
        """Get AI usage statistics."""
        if self.analytics:
            return self.analytics.get_stats()
        return {}
    
    def clear_cache(self):
        """Clear response cache."""
        if self.cache:
            self.cache.clear()


# Backwards compatibility alias
class AIManager(AIEngine):
    """Alias for backwards compatibility."""
    pass
