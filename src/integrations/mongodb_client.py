"""
MongoDB Integration - FREE NoSQL Database
=========================================
Flexible document database

Based on: https://github.com/mongodb/mongo

Features:
- NoSQL document storage
- Flexible schema
- JSON-like documents
- Horizontal scaling
- 100% FREE (self-hosted)!

Setup:
    docker run -d -p 27017:27017 mongo
"""

import os
import logging
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)


class MongoDBClient:
    """
    MongoDB Client - NoSQL Database
    
    Use Cases:
    - Store WhatsApp messages
    - User profiles
    - Flexible data storage
    - Real-time feeds
    - Chat history
    
    Setup:
    1. Docker (FREE):
       docker run -d -p 27017:27017 mongo
       docker run -d -p 27017:27017 -v mongo_data:/data/db mongo
    
    2. Cloud (MongoDB Atlas):
       https://mongodb.com/atlas (500MB free)
    
    Environment:
    - MONGODB_URL=mongodb://localhost:27017
    - MONGODB_DB=whatsapp_bot
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        database: Optional[str] = None
    ):
        self.url = url or os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.database = database or os.getenv("MONGODB_DB", "whatsapp_bot")
        self.enabled = False
        self.client = None
        self.db = None
        
        try:
            from pymongo import MongoClient
            self.client = MongoClient(self.url, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database]
            self.enabled = True
            logger.info(f"✅ MongoDB configured: {self.database}")
        except ImportError:
            logger.warning("Install pymongo: pip install pymongo")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB not configured: {e}")
    
    def insert_one(self, collection: str, document: Dict) -> Optional[str]:
        """Insert single document"""
        if not self.enabled:
            return None
        
        try:
            result = self.db[collection].insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"MongoDB insert error: {e}")
            return None
    
    def insert_many(self, collection: str, documents: List[Dict]) -> List[str]:
        """Insert multiple documents"""
        if not self.enabled:
            return []
        
        try:
            result = self.db[collection].insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"MongoDB insert many error: {e}")
            return []
    
    def find_one(
        self,
        collection: str,
        query: Dict,
        projection: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Find single document"""
        if not self.enabled:
            return None
        
        try:
            return self.db[collection].find_one(query, projection)
        except Exception as e:
            logger.error(f"MongoDB find error: {e}")
            return None
    
    def find_many(
        self,
        collection: str,
        query: Dict,
        limit: int = 100,
        sort: Optional[List] = None
    ) -> List[Dict]:
        """Find multiple documents"""
        if not self.enabled:
            return []
        
        try:
            cursor = self.db[collection].find(query)
            if sort:
                cursor = cursor.sort(sort)
            return list(cursor.limit(limit))
        except Exception as e:
            logger.error(f"MongoDB find many error: {e}")
            return []
    
    def update_one(
        self,
        collection: str,
        query: Dict,
        update: Dict
    ) -> bool:
        """Update single document"""
        if not self.enabled:
            return False
        
        try:
            result = self.db[collection].update_one(query, {"$set": update})
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"MongoDB update error: {e}")
            return False
    
    def delete_one(self, collection: str, query: Dict) -> bool:
        """Delete single document"""
        if not self.enabled:
            return False
        
        try:
            result = self.db[collection].delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"MongoDB delete error: {e}")
            return False
    
    def count(self, collection: str, query: Dict = None) -> int:
        """Count documents"""
        if not self.enabled:
            return 0
        
        try:
            query = query or {}
            return self.db[collection].count_documents(query)
        except Exception as e:
            logger.error(f"MongoDB count error: {e}")
            return 0
    
    def aggregate(self, collection: str, pipeline: List) -> List[Dict]:
        """Run aggregation pipeline"""
        if not self.enabled:
            return []
        
        try:
            return list(self.db[collection].aggregate(pipeline))
        except Exception as e:
            logger.error(f"MongoDB aggregate error: {e}")
            return []
    
    def save_message(self, sender: str, message: str, direction: str) -> Optional[str]:
        """Save WhatsApp message"""
        doc = {
            "sender": sender,
            "message": message,
            "direction": direction,  # incoming/outgoing
            "timestamp": {"$date": {"$numberLong": str(int(__import__("time").time() * 1000))}}
        }
        return self.insert_one("messages", doc)
    
    def get_user_messages(
        self,
        sender: str,
        limit: int = 50
    ) -> List[Dict]:
        """Get chat history for user"""
        return self.find_many(
            "messages",
            {"sender": sender},
            limit=limit,
            sort=[("timestamp", -1)]
        )
    
    def save_lead(self, name: str, phone: str, source: str = "whatsapp") -> Optional[str]:
        """Save lead/customer"""
        doc = {
            "name": name,
            "phone": phone,
            "source": source,
            "created_at": {"$date": {"$numberLong": str(int(__import__("time").time() * 1000))}},
            "status": "new"
        }
        return self.insert_one("leads", doc)
    
    def get_stats(self, collection: str) -> Dict:
        """Get collection statistics"""
        if not self.enabled:
            return {}
        
        try:
            count = self.count(collection)
            return {"collection": collection, "count": count}
        except:
            return {}


def setup_mongodb():
    """Setup guide for MongoDB"""
    print("\n" + "="*50)
    print("🗄️ MongoDB Setup")
    print("="*50 + "\n")
    
    print("OPTION 1: Self-hosted (FREE)")
    print("-" * 40)
    print("docker run -d -p 27017:27017 \\")
    print("  -v mongo_data:/data/db \\")
    print("  mongo")
    print("\nConnection: mongodb://localhost:27017\n")
    
    print("OPTION 2: MongoDB Atlas (Cloud - 500MB FREE)")
    print("-" * 40)
    print("1. Go to https://mongodb.com/atlas")
    print("2. Sign up free")
    print("3. Create cluster")
    print("4. Get connection string\n")
    
    url = input("MongoDB URL (press Enter for default): ").strip()
    if not url:
        url = "mongodb://localhost:27017"
    
    db = input("Database name: ").strip()
    if not db:
        db = "whatsapp_bot"
    
    with open(".env", "a") as f:
        f.write(f"\n# MongoDB (NoSQL Database)\n")
        f.write(f"MONGODB_URL={url}\n")
        f.write(f"MONGODB_DB={db}\n")
    
    # Install pymongo
    print("\nInstalling pymongo...")
    os.system("pip install pymongo")
    print("✅ Saved to .env!")


if __name__ == "__main__":
    setup_mongodb()
