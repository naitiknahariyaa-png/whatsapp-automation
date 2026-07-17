"""
WhatsApp Bot Integrations - External Services

Available:
- ChatwootClient: Unified customer inbox (CRM)
- SupabaseClient: Cloud PostgreSQL database
- RedisCache: Fast in-memory cache
- OllamaAI: FREE local AI (no costs)
- OmniRouteClient: 250+ AI providers, 90+ FREE
"""

from .chatwoot_client import ChatwootClient
from .supabase_client import SupabaseClient
from .redis_client import RedisCache
from .ollama_client import OllamaAI
from .omniroute_client import OmniRouteClient, FREE_MODELS, setup_omniroute

__all__ = [
    "ChatwootClient",
    "SupabaseClient", 
    "RedisCache",
    "OllamaAI",
    "OmniRouteClient",
    "FREE_MODELS",
    "setup_omniroute"
]
