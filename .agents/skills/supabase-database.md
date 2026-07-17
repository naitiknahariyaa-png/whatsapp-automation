# Supabase Database Skill

## Purpose
Use Supabase (PostgreSQL + Auth + Storage) instead of local SQLite.

## What is Supabase?
Open-source Firebase alternative - Postgres + Auth + Storage + Realtime.

## Setup

### 1. Create Supabase Project
1. Go to https://supabase.com
2. Create new project
3. Get Project URL and API Key from Settings

### 2. Install Client
```bash
pip install supabase
```

### 3. Connect to WhatsApp Bot
```python
# In database.py
from supabase import create_client, Client

SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseDatabase:
    """Cloud database using Supabase"""
    
    def add_message(self, sender, message, response):
        """Store message"""
        return supabase.table("messages").insert({
            "sender": sender,
            "message": message,
            "response": response,
            "timestamp": "now()"
        }).execute()
    
    def get_messages(self, sender, limit=50):
        """Get message history"""
        return supabase.table("messages").select("*").eq(
            "sender", sender
        ).order("timestamp", desc=True).limit(limit).execute()
    
    def add_keyword(self, keyword, response):
        """Add keyword"""
        return supabase.table("keywords").insert({
            "keyword": keyword,
            "response": response
        }).execute()
    
    def get_keywords(self):
        """Get all keywords"""
        return supabase.table("keywords").select("*").execute()
```

## Tables Setup

```sql
-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender VARCHAR(255),
    message TEXT,
    response TEXT,
    timestamp TIMESTAMP DEFAULT now()
);

-- Keywords table
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(255) UNIQUE,
    response TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(50) UNIQUE,
    name VARCHAR(255),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT now()
);

-- Enable realtime
ALTER PUBLICATION supabase_realtime ADD TABLE messages;
```

## Features

| Feature | Description |
|---------|-------------|
| PostgreSQL | Full SQL power |
| Auth | User authentication |
| Storage | File uploads |
| Realtime | Live updates |
| Edge Functions | Serverless code |

## Environment Variables
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
```

## Code: Customer Tracking
```python
def track_customer(sender, message):
    """Track customer and their interests"""
    
    # Check if customer exists
    existing = supabase.table("customers").select("*").eq(
        "phone", sender
    ).execute()
    
    if not existing.data:
        # New customer - create record
        supabase.table("customers").insert({
            "phone": sender,
            "name": extract_name(message),
            "tags": ["whatsapp"]
        }).execute()
    else:
        # Update tags based on message
        tags = existing.data[0].get("tags", [])
        if "prices" in message.lower():
            tags.append("price_inquiry")
        if "order" in message.lower():
            tags.append("ready_to_buy")
```

## More Info
- Website: https://supabase.com
- GitHub: https://github.com/supabase/supabase
