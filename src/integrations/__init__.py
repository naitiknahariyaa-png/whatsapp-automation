"""
WhatsApp Bot Integrations - External Services

Quick Setup:
    python src/integrations/setup_all.py

Available Integrations:
- AI: Groq, Gemini, Ollama, OmniRoute
- WhatsApp: OpenWA Gateway
- Payments: Razorpay (India)
- CRM: Notion, Linear
- Storage: Cloudflare R2 (FREE), Supabase
- Analytics: Posthog, Sentry
- Calendar: Google Calendar
- Automation: n8n, Celery
- Chatbots: Botpress, Typebot
- Communication: Chatwoot, Discord
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
from .openwa_client import OpenWAGateway, setup_openwa
from .openwa_memory import OpenWAMemory, setup_openwa_memory

# NEW: Payment & Commerce
from .razorpay_client import RazorpayClient, setup_razorpay

# NEW: CRM & Productivity
from .notion_client import NotionClient, setup_notion
from .linear_client import LinearClient, setup_linear
from .google_calendar_client import GoogleCalendarClient, setup_google_calendar

# NEW: Monitoring & Analytics
from .sentry_client import SentryClient, setup_sentry
from .posthog_client import PosthogClient, setup_posthog
from .discord_client import DiscordWebhook, setup_discord

# NEW: Storage
from .cloudflare_r2_client import CloudflareR2Client, setup_cloudflare_r2

__all__ = [
    # WhatsApp Gateway
    "OpenWAGateway",
    "OpenWAMemory",
    "setup_openwa",
    "setup_openwa_memory",
    
    # AI
    "OllamaAI",
    "OmniRouteClient",
    "FREE_MODELS",
    "setup_omniroute",
    
    # Database & Cache
    "SupabaseClient",
    "RedisCache",
    
    # Payments (India)
    "RazorpayClient",
    "setup_razorpay",
    
    # CRM & Productivity
    "NotionClient",
    "setup_notion",
    "LinearClient",
    "setup_linear",
    "GoogleCalendarClient",
    "setup_google_calendar",
    
    # Monitoring & Analytics
    "SentryClient",
    "setup_sentry",
    "PosthogClient",
    "setup_posthog",
    "DiscordWebhook",
    "setup_discord",
    
    # Storage
    "CloudflareR2Client",
    "setup_cloudflare_r2",
    
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
    
    # Communication
    "ChatwootClient",
]
