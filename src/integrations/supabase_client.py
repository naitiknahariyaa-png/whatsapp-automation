"""
Supabase Database - Cloud PostgreSQL for WhatsApp bot
Store messages, customers, keywords in the cloud
"""

import os
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Try to import supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None


class SupabaseClient:
    """
    Supabase Database Client
    
    Features:
    - Cloud PostgreSQL database
    - User authentication
    - File storage
    - Real-time subscriptions
    
    Setup:
    1. Go to https://supabase.com
    2. Create new project
    3. Get Project URL and API Key from Settings
    
    Environment:
    - SUPABASE_URL=https://xxx.supabase.co
    - SUPABASE_KEY=your-anon-key
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None
    ):
        self.url = url or os.getenv("SUPABASE_URL", "")
        self.key = key or os.getenv("SUPABASE_KEY", "")
        self.client: Optional[Client] = None
        self.enabled = False
        
        if SUPABASE_AVAILABLE and self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                self.enabled = True
                logger.info(f"✅ Supabase connected")
            except Exception as e:
                logger.warning(f"⚠️ Supabase error: {e}")
                self.enabled = False
        else:
            if not SUPABASE_AVAILABLE:
                logger.warning("⚠️ Supabase not installed (pip install supabase)")
            else:
                logger.warning("⚠️ Supabase not configured")
    
    # ========================
    # Messages
    # ========================
    
    def add_message(
        self,
        sender: str,
        message: str,
        response: str = "",
        message_type: str = "incoming"
    ) -> Optional[Dict]:
        """Store message in database"""
        if not self.enabled:
            return None
        
        try:
            data = {
                "sender": sender,
                "message": message,
                "response": response,
                "message_type": message_type
            }
            return self.client.table("messages").insert(data).execute()
        except Exception as e:
            logger.error(f"Supabase add_message error: {e}")
            return None
    
    def get_messages(
        self,
        sender: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get messages from database"""
        if not self.enabled:
            return []
        
        try:
            query = self.client.table("messages").select("*")
            
            if sender:
                query = query.eq("sender", sender)
            
            return query.order("created_at", desc=True).limit(limit).execute().data
        except Exception as e:
            logger.error(f"Supabase get_messages error: {e}")
            return []
    
    # ========================
    # Customers
    # ========================
    
    def add_customer(
        self,
        phone: str,
        name: str = "",
        tags: List[str] = None
    ) -> Optional[Dict]:
        """Add or update customer"""
        if not self.enabled:
            return None
        
        try:
            # Check if exists
            existing = self.client.table("customers").select("*").eq(
                "phone", phone
            ).execute().data
            
            if existing:
                # Update
                return self.client.table("customers").update({
                    "name": name,
                    "tags": tags or []
                }).eq("phone", phone).execute()
            else:
                # Insert
                return self.client.table("customers").insert({
                    "phone": phone,
                    "name": name,
                    "tags": tags or []
                }).execute()
        except Exception as e:
            logger.error(f"Supabase add_customer error: {e}")
            return None
    
    def get_customer(self, phone: str) -> Optional[Dict]:
        """Get customer by phone"""
        if not self.enabled:
            return None
        
        try:
            data = self.client.table("customers").select("*").eq(
                "phone", phone
            ).execute().data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Supabase get_customer error: {e}")
            return None
    
    def update_customer_tags(self, phone: str, tags: List[str]) -> bool:
        """Update customer tags"""
        if not self.enabled:
            return False
        
        try:
            self.client.table("customers").update({
                "tags": tags
            }).eq("phone", phone).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase update_customer_tags error: {e}")
            return False
    
    # ========================
    # Keywords
    # ========================
    
    def add_keyword(self, keyword: str, response: str) -> Optional[Dict]:
        """Add keyword response"""
        if not self.enabled:
            return None
        
        try:
            return self.client.table("keywords").insert({
                "keyword": keyword,
                "response": response
            }).execute()
        except Exception as e:
            # Probably duplicate
            logger.error(f"Supabase add_keyword error: {e}")
            return None
    
    def get_keywords(self) -> List[Dict]:
        """Get all keywords"""
        if not self.enabled:
            return []
        
        try:
            return self.client.table("keywords").select("*").execute().data
        except Exception as e:
            logger.error(f"Supabase get_keywords error: {e}")
            return []
    
    def find_keyword(self, message: str) -> Optional[str]:
        """Find matching keyword response"""
        keywords = self.get_keywords()
        message_lower = message.lower()
        
        for kw in keywords:
            if kw.get("keyword", "").lower() in message_lower:
                return kw.get("response")
        
        return None
    
    # ========================
    # Stats
    # ========================
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            messages = self.client.table("messages").select("id", count="exact").execute()
            customers = self.client.table("customers").select("id", count="exact").execute()
            keywords = self.client.table("keywords").select("id", count="exact").execute()
            
            return {
                "enabled": True,
                "total_messages": messages.count,
                "total_customers": customers.count,
                "total_keywords": keywords.count
            }
        except Exception as e:
            logger.error(f"Supabase get_stats error: {e}")
            return {"enabled": True, "error": str(e)}


# SQL Schema for Supabase
SCHEMA_SQL = """
-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender VARCHAR(255),
    message TEXT,
    response TEXT DEFAULT '',
    message_type VARCHAR(50) DEFAULT 'incoming',
    created_at TIMESTAMP DEFAULT now()
);

-- Customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(50) UNIQUE,
    name VARCHAR(255),
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT now()
);

-- Keywords table
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(255) UNIQUE,
    response TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Enable Row Level Security (RLS)
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE keywords ENABLE ROW LEVEL SECURITY;

-- Public access policies (adjust for production)
CREATE POLICY "Enable public access" ON messages FOR SELECT USING (true);
CREATE POLICY "Enable public insert" ON messages FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable public access" ON customers FOR SELECT USING (true);
CREATE POLICY "Enable public insert" ON customers FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable public access" ON keywords FOR SELECT USING (true);
CREATE POLICY "Enable public insert" ON keywords FOR INSERT WITH CHECK (true);
"""


def setup_supabase():
    """Guide user to setup Supabase"""
    print("""
╔══════════════════════════════════════════════════════════╗
║           Supabase Database Setup                       ║
╚══════════════════════════════════════════════════════════╝

1. Create Supabase Account:
   Go to: https://supabase.com

2. Create New Project:
   - Name: whatsapp-bot
   - Database Password: (save this!)
   - Region: Choose nearest

3. Get API Keys:
   - Go to Settings → API
   - Copy Project URL
   - Copy anon/public key

4. Add to .env:
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=your-anon-key

5. Run SQL Schema:
   - Go to SQL Editor
   - Paste the schema from supabase_client.py
   - Click Run

Install Python package:
   pip install supabase

Benefits:
✅ Free tier: 500MB database
✅ Automatic backups
✅ Real-time subscriptions
✅ User authentication
""")


if __name__ == "__main__":
    setup_supabase()
    print("\n=== SQL Schema ===")
    print(SCHEMA_SQL)
