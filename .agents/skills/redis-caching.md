# Redis Caching Skill

## Purpose
Use Redis for fast caching and session storage.

## What is Redis?
In-memory database - super fast caching + queue backend.

## Setup

### 1. Install Redis
**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis
```

### 2. Install Client
```bash
pip install redis
```

### 3. Connect to WhatsApp Bot
```python
# In cache.py
import redis
import json

REDIS_URL = "redis://localhost:6379"

redis_client = redis.from_url(REDIS_URL)

class RedisCache:
    """Fast caching with Redis"""
    
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL)
    
    def cache_ai_response(self, prompt, response, ttl=3600):
        """Cache AI response for 1 hour"""
        key = f"ai:response:{hash(prompt)}"
        self.redis.setex(key, ttl, response)
    
    def get_cached_response(self, prompt):
        """Get cached AI response"""
        key = f"ai:response:{hash(prompt)}"
        return self.redis.get(key)
    
    def mark_seen_message(self, message_id):
        """Prevent duplicate replies"""
        key = f"seen:{message_id}"
        return self.redis.set(key, "1", ex=86400)  # 24 hours
    
    def is_message_seen(self, message_id):
        """Check if already replied"""
        key = f"seen:{message_id}"
        return self.redis.exists(key)
    
    def rate_limit(self, user_id, limit=10, window=60):
        """Rate limit user requests"""
        key = f"ratelimit:{user_id}"
        count = self.redis.get(key)
        
        if count and int(count) >= limit:
            return False  # Rate limited
        
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        pipe.execute()
        
        return True  # Allowed
    
    def store_session(self, session_id, data, ttl=86400):
        """Store WhatsApp session"""
        key = f"session:{session_id}"
        self.redis.setex(key, ttl, json.dumps(data))
    
    def get_session(self, session_id):
        """Get stored session"""
        key = f"session:{session_id}"
        data = self.redis.get(key)
        return json.loads(data) if data else None
```

## Features

| Feature | Description |
|---------|-------------|
| Cache | Speed up repeated queries |
| Rate Limiting | Prevent spam |
| Session Store | Fast session access |
| Pub/Sub | Real-time messaging |
| Queue | Background jobs |

## Use Cases

### 1. AI Response Cache
```python
# Cache AI responses
cache = RedisCache()

# Check cache first
cached = cache.get_cached_response(user_message)
if cached:
    return cached  # Skip AI call

# Not cached - call AI
response = ai.get_response(user_message)
cache.cache_ai_response(user_message, response)
```

### 2. Duplicate Prevention
```python
def on_message(message_id, text):
    if cache.is_message_seen(message_id):
        return  # Already replied
    
    cache.mark_seen_message(message_id)
    # Process message...
```

### 3. Rate Limiting
```python
def on_message(user_id, text):
    if not cache.rate_limit(user_id, limit=10, window=60):
        return "Please wait before sending more messages"
```

## Environment Variables
```
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=xxx  # If auth enabled
```

## Docker Compose Setup
```yaml
# docker-compose.yml
version: '3'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  bot:
    build: .
    depends_on:
      - redis
```

## More Info
- Website: https://redis.io
- GitHub: https://github.com/redis/redis
