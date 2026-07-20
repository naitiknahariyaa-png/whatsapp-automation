"""
⚙️ Security Configuration
========================
Centralized security settings for the application.
"""

from dataclasses import dataclass
from typing import List
import os


@dataclass
class SecurityConfig:
    """
    Security configuration settings.
    
    Usage:
        config = SecurityConfig.from_env()
        if config.rate_limit_enabled:
            print(f"Rate limit: {config.rate_limit_per_minute} req/min")
    """
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # Input Validation
    max_message_length: int = 4096
    max_broadcast_recipients: int = 100
    
    # Session Security
    session_timeout_minutes: int = 30
    max_login_attempts: int = 5
    
    # API Security
    api_key_required: bool = True
    cors_enabled: bool = False
    allowed_origins: List[str] = None
    
    # WhatsApp Specific
    max_contacts_per_request: int = 50
    message_cooldown_seconds: int = 5
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Load configuration from environment variables."""
        return cls(
            rate_limit_enabled=os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true',
            rate_limit_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', '60')),
            rate_limit_per_hour=int(os.getenv('RATE_LIMIT_PER_HOUR', '1000')),
            max_message_length=int(os.getenv('MAX_MESSAGE_LENGTH', '4096')),
            max_broadcast_recipients=int(os.getenv('MAX_BROADCAST_RECIPIENTS', '100')),
            session_timeout_minutes=int(os.getenv('SESSION_TIMEOUT_MINUTES', '30')),
            max_login_attempts=int(os.getenv('MAX_LOGIN_ATTEMPTS', '5')),
            api_key_required=os.getenv('API_KEY_REQUIRED', 'true').lower() == 'true',
            cors_enabled=os.getenv('CORS_ENABLED', 'false').lower() == 'true',
            allowed_origins=os.getenv('ALLOWED_ORIGINS', '').split(',') if os.getenv('ALLOWED_ORIGINS') else [],
            max_contacts_per_request=int(os.getenv('MAX_CONTACTS_PER_REQUEST', '50')),
            message_cooldown_seconds=int(os.getenv('MESSAGE_COOLDOWN_SECONDS', '5')),
        )


# Security headers for HTTP responses
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
}


# Default singleton instance
config = SecurityConfig.from_env()
