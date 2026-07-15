"""
====================================================================
CONFIGURATION MANAGEMENT - Pydantic Validation
====================================================================
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class AIConfig(BaseModel):
    """AI Provider Configuration"""
    provider: str = Field(default="keyword", description="AI provider: openrouter, groq, keyword")
    openrouter_api_key: Optional[str] = Field(default=None, description="OpenRouter API key")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    model: str = Field(default="openrouter/free", description="AI model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=150, ge=10, le=1000)

    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v):
        allowed = ['openrouter', 'groq', 'keyword']
        if v not in allowed:
            raise ValueError(f"Provider must be one of: {allowed}")
        return v


class WhatsAppConfig(BaseModel):
    """WhatsApp Configuration"""
    session_dir: str = Field(default="data/session")
    reconnect_delay: int = Field(default=5, ge=1, le=60)
    max_retries: int = Field(default=3, ge=1, le=10)
    qr_timeout: int = Field(default=120, ge=30, le=300)


class DatabaseConfig(BaseModel):
    """Database Configuration"""
    path: str = Field(default="data/whatsapp.db")
    max_connections: int = Field(default=5, ge=1, le=20)
    timeout: float = Field(default=30.0, ge=1.0, le=60.0)


class CacheConfig(BaseModel):
    """Cache Configuration"""
    enabled: bool = True
    max_size: int = Field(default=1000, ge=100, le=10000)
    ttl: int = Field(default=3600, ge=60, le=86400)


class BusinessConfig(BaseModel):
    """Business Information"""
    name: str = Field(default="My Business")
    address: str = Field(default="")
    phone: str = Field(default="")
    whatsapp: str = Field(default="")
    email: str = Field(default="")
    website: str = Field(default="")
    hours: str = Field(default="9 AM - 9 PM")


class BotConfig(BaseModel):
    """Main Bot Configuration"""
    ai: AIConfig = Field(default_factory=AIConfig)
    whatsapp: WhatsAppConfig = Field(default_factory=WhatsAppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    business: BusinessConfig = Field(default_factory=BusinessConfig)
    debug: bool = False
    log_level: str = Field(default="INFO")

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()


def load_config(config_path: str = "config.yaml") -> BotConfig:
    """Load configuration from YAML file with validation"""
    import yaml
    config_file = Path(config_path)
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f) or {}
        return BotConfig(**data)
    
    return BotConfig()


def save_config(config: BotConfig, config_path: str = "config.yaml"):
    """Save configuration to YAML file"""
    import yaml
    config_file = Path(config_path)
    
    data = {
        'ai': config.ai.model_dump(),
        'whatsapp': config.whatsapp.model_dump(),
        'database': config.database.model_dump(),
        'cache': config.cache.model_dump(),
        'business': config.business.model_dump(),
        'debug': config.debug,
        'log_level': config.log_level
    }
    
    with open(config_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
