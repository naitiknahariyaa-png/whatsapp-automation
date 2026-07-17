"""
Redis Caching - Fast in-memory cache for WhatsApp bot
Prevents duplicate replies, speeds up AI responses, rate limiting
"""

import os
import json
import logging
import hashlib
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Try to import redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class RedisCache:
    """
    Redis Cache Client
    
    Features:
    - AI response caching (speed up repeated queries)
    - Duplicate message prevention (don't reply twice)
    - Rate limiting (prevent spam)
    - Session storage
    
    Setup:
    1. Install Redis: docker run -d -p 6379:6379 redis
    2. Or: sudo apt install redis-server
    
    Environment:
    - REDIS_URL=redis://localhost:6379
    """
    
    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = None
        self.enabled = False
        
        if REDIS_AVAILABLE:
            try:
                self.client = redis.from_url(self.url)
                self.client.ping()
                self.enabled = True
                logger.info(f"✅ Redis connected: {self.url}")
            except Exception as e:
                logger.warning(f"⚠️ Redis not available: {e}")
                self.enabled = False
        else:
            logger.warning("⚠️ Redis not installed (pip install redis)")
    
    def _hash_key(self, text: str) -> str:
        """Create hash for text"""
        return hashlib.md5(text.lower().encode()).hexdigest()
    
    # ========================
    # AI Response Caching
    # ========================
    
    def get_cached_ai_response(self, message: str) -> Optional[str]:
        """Get cached AI response (same message = same response)"""
        if not self.enabled:
            return None
        
        try:
            key = f"ai:cache:{self._hash_key(message)}"
            return self.client.get(key)
        except:
            return None
    
    def cache_ai_response(self, message: str, response: str, ttl: int = 3600):
        """
        Cache AI response
        
        Args:
            message: User's message
            response: AI's response
            ttl: Time to live in seconds (default 1 hour)
        """
        if not self.enabled:
            return
        
        try:
            key = f"ai:cache:{self._hash_key(message)}"
            self.client.setex(key, ttl, response)
            logger.debug(f"Cached AI response for: {message[:50]}...")
        except:
            pass
    
    # ========================
    # Duplicate Prevention
    # ========================
    
    def is_message_processed(self, message_id: str) -> bool:
        """Check if message was already processed"""
        if not self.enabled:
            return False
        
        try:
            key = f"processed:{message_id}"
            return bool(self.client.exists(key))
        except:
            return False
    
    def mark_message_processed(self, message_id: str, ttl: int = 86400):
        """
        Mark message as processed
        
        Args:
            message_id: Unique message ID
            ttl: Keep for 24 hours
        """
        if not self.enabled:
            return
        
        try:
            key = f"processed:{message_id}"
            self.client.setex(key, ttl, "1")
        except:
            pass
    
    # ========================
    # Rate Limiting
    # ========================
    
    def check_rate_limit(
        self,
        user_id: str,
        limit: int = 10,
        window: int = 60
    ) -> bool:
        """
        Check if user is rate limited
        
        Args:
            user_id: User's phone number or ID
            limit: Max messages per window
            window: Time window in seconds
            
        Returns:
            True if allowed, False if rate limited
        """
        if not self.enabled:
            return True  # Allow if no Redis
        
        try:
            key = f"ratelimit:{user_id}"
            
            # Get current count
            count = self.client.get(key)
            
            if count and int(count) >= limit:
                return False  # Rate limited
            
            # Increment counter
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            pipe.execute()
            
            return True
            
        except:
            return True  # Allow on error
    
    def get_rate_limit_remaining(self, user_id: str, limit: int = 10) -> int:
        """Get remaining messages in current window"""
        if not self.enabled:
            return limit
        
        try:
            key = f"ratelimit:{user_id}"
            count = self.client.get(key)
            if count:
                return max(0, limit - int(count))
            return limit
        except:
            return limit
    
    # ========================
    # Session Storage
    # ========================
    
    def save_session(self, session_id: str, data: dict, ttl: int = 86400):
        """Save WhatsApp session data"""
        if not self.enabled:
            return
        
        try:
            key = f"session:{session_id}"
            self.client.setex(key, ttl, json.dumps(data))
        except:
            pass
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get WhatsApp session data"""
        if not self.enabled:
            return None
        
        try:
            key = f"session:{session_id}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except:
            return None
    
    # ========================
    # Utility
    # ========================
    
    def clear_cache(self):
        """Clear all cache (for testing)"""
        if not self.enabled:
            return
        
        try:
            self.client.flushdb()
            logger.info("Redis cache cleared")
        except:
            pass
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            info = self.client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0"),
                "total_keys": self.client.dbsize()
            }
        except:
            return {"enabled": True, "error": "Could not get stats"}


# Quick setup function
def setup_redis():
    """Guide user to setup Redis"""
    print("""
╔══════════════════════════════════════════════════════════╗
║           Redis Cache Setup                             ║
╚══════════════════════════════════════════════════════════╝

Option 1: Docker (Recommended)
   docker run -d -p 6379:6379 redis

Option 2: Install directly
   Ubuntu/Debian: sudo apt install redis-server
   Mac: brew install redis
   Windows: Use Docker

Option 3: Cloud Redis
   https://redis.com/cloud
   Free tier available

Add to .env:
   REDIS_URL=redis://localhost:6379

Install Python package:
   pip install redis

Test connection:
   redis-cli ping
   # Should return: PONG
""")


if __name__ == "__main__":
    setup_redis()
