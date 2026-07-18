"""
WhatsApp Bot Integrations - External Services

Available:
- ChatwootClient: Unified customer inbox (CRM)
- SupabaseClient: Cloud PostgreSQL database
- RedisCache: Fast in-memory cache
- OllamaAI: FREE local AI (no costs)
- OmniRouteClient: 250+ AI providers, 90+ FREE
- CeleryTasks: Async task queue for 10k+ users
- N8NClient: Workflow automation (400+ integrations)
- BotpressClient: Visual chatbot flow builder
- TypebotClient: Interactive forms and quizzes
"""

from .chatwoot_client import ChatwootClient
from .supabase_client import SupabaseClient
from .redis_client import RedisCache
from .ollama_client import OllamaAI
from .omniroute_client import OmniRouteClient, FREE_MODELS, setup_omniroute
from .celery_tasks import (
    celery_app,
    process_whatsapp_message,
    send_bulk_messages,
    cleanup_old_messages,
    send_daily_summary,
    send_scheduled_message,
    health_check
)
from .n8n_client import N8NClient, setup_n8n
from .botpress_client import BotpressClient, BotpressAI, setup_botpress
from .typebot_client import TypebotClient, WhatsAppFormHandler, setup_typebot

__all__ = [
    # Core integrations
    "ChatwootClient",
    "SupabaseClient",
    "RedisCache",
    "OllamaAI",
    "OmniRouteClient",

    # Task queue
    "celery_app",
    "process_whatsapp_message",
    "send_bulk_messages",
    "cleanup_old_messages",
    "send_daily_summary",
    "send_scheduled_message",
    "health_check",

    # Workflow automation
    "N8NClient",
    "setup_n8n",

    # Chatbot builders
    "BotpressClient",
    "BotpressAI",
    "setup_botpress",
    "TypebotClient",
    "WhatsAppFormHandler",
    "setup_typebot",

    # Utilities
    "FREE_MODELS",
    "setup_omniroute"
]
