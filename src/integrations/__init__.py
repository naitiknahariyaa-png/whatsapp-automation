"""
WhatsApp Bot Integrations - 50+ External Services

Quick Setup:
    python src/integrations/setup_all.py

Available Integrations (ALL FREE or FREE-tier):
- AI: Groq, Gemini, Ollama, HuggingFace, Dify, Stable Diffusion
- WhatsApp: OpenWA Gateway
- Payments: Razorpay, Medusa
- Database: Supabase, Redis, MongoDB
- Search: Meilisearch, Qdrant (vectors)
- CRM: Notion, Linear
- Scheduling: Cal.com, Google Calendar
- Analytics: Posthog, Sentry, Plausible, Netdata
- Storage: Cloudflare R2, MinIO
- Notifications: Ntfy, Discord, Telegram
- Automation: n8n, ActivePieces, Celery
- Chatbots: Botpress, Typebot
- Communication: Chatwoot
"""

from .chatwoot_client import ChatwootClient
from .supabase_client import SupabaseClient
from .redis_client import RedisCache
from .ollama_client import OllamaAI
from .omniroute_client import OmniRouteClient, FREE_MODELS, setup_omniroute
from .celery_tasks import (
    celery_app, process_whatsapp_message, send_bulk_messages,
    cleanup_old_messages, send_daily_summary, send_scheduled_message, health_check
)
from .n8n_client import N8NClient, setup_n8n
from .botpress_client import BotpressClient, BotpressAI, setup_botpress
from .typebot_client import TypebotClient, WhatsAppFormHandler, setup_typebot
from .openwa_client import OpenWAGateway, setup_openwa
from .openwa_memory import OpenWAMemory, setup_openwa_memory

# AI & ML
from .huggingface_client import HuggingFaceClient, setup_huggingface
from .stable_diffusion_client import StableDiffusionClient, setup_stable_diffusion
from .dify_client import DifyClient, setup_dify

# Payments & Commerce
from .razorpay_client import RazorpayClient, setup_razorpay
from .medusa_client import MedusaClient, setup_medusa

# CRM & Productivity
from .notion_client import NotionClient, setup_notion
from .linear_client import LinearClient, setup_linear
from .cal_client import CalClient, setup_cal
from .google_calendar_client import GoogleCalendarClient, setup_google_calendar

# Monitoring & Analytics
from .sentry_client import SentryClient, setup_sentry
from .posthog_client import PosthogClient, setup_posthog
from .plausible_client import PlausibleAnalytics, setup_plausible
from .netdata_client import NetdataClient, setup_netdata
from .discord_client import DiscordWebhook, setup_discord

# Database & Search
from .cloudflare_r2_client import CloudflareR2Client, setup_cloudflare_r2
from .minio_client import MinIOClient, setup_minio
from .mongodb_client import MongoDBClient, setup_mongodb
from .meilisearch_client import MeilisearchClient, setup_meilisearch
from .qdrant_client import QdrantClient, setup_qdrant

# Notifications & Automation
from .ntfy_client import NtfyClient, setup_ntfy
from .activepieces_client import ActivePiecesClient, setup_activepieces

__all__ = [
    # WhatsApp Gateway
    "OpenWAGateway", "OpenWAMemory", "setup_openwa", "setup_openwa_memory",
    
    # AI & ML (FREE)
    "OllamaAI", "OmniRouteClient", "HuggingFaceClient", "StableDiffusionClient", "DifyClient",
    "setup_omniroute", "setup_huggingface", "setup_stable_diffusion", "setup_dify",
    
    # Database & Cache
    "SupabaseClient", "RedisCache", "MongoDBClient",
    "setup_mongodb",
    
    # Search & Vectors
    "MeilisearchClient", "QdrantClient",
    "setup_meilisearch", "setup_qdrant",
    
    # Payments (India)
    "RazorpayClient", "MedusaClient",
    "setup_razorpay", "setup_medusa",
    
    # CRM & Productivity
    "NotionClient", "LinearClient", "CalClient", "GoogleCalendarClient",
    "setup_notion", "setup_linear", "setup_cal", "setup_google_calendar",
    
    # Monitoring & Analytics
    "SentryClient", "PosthogClient", "PlausibleAnalytics", "NetdataClient",
    "setup_sentry", "setup_posthog", "setup_plausible", "setup_netdata",
    "DiscordWebhook", "setup_discord",
    
    # Storage
    "CloudflareR2Client", "MinIOClient",
    "setup_cloudflare_r2", "setup_minio",
    
    # Notifications
    "NtfyClient", "setup_ntfy",
    
    # Automation
    "N8NClient", "ActivePiecesClient", "celery_app",
    "setup_n8n", "setup_activepieces",
    "process_whatsapp_message", "send_bulk_messages", "health_check",
    
    # Chatbot builders
    "BotpressClient", "BotpressAI", "setup_botpress",
    "TypebotClient", "WhatsAppFormHandler", "setup_typebot",
    
    # Communication
    "ChatwootClient",
    
    # Utilities
    "FREE_MODELS",
]
