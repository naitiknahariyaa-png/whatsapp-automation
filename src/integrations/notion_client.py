"""
Notion Integration - Knowledge Base & Database
Connect WhatsApp leads to Notion for CRM
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class NotionClient:
    """
    Notion API Client for CRM and Knowledge Base
    
    Perfect for:
    - Lead capture from WhatsApp
    - Customer database
    - Order tracking
    - Knowledge base
    
    Setup:
    1. Go to https://www.notion.so/my-integrations
    2. Create new integration
    3. Copy the API key
    4. Share your database with the integration
    5. Add to .env
    
    Environment:
    - NOTION_API_KEY=secret_xxx
    - NOTION_DATABASE_ID=xxx
    """
    
    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        database_id: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("NOTION_API_KEY", "")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID", "")
        self.enabled = bool(self.api_key)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": self.NOTION_VERSION,
            "Content-Type": "application/json"
        }
        
        if self.enabled:
            logger.info("✅ Notion configured")
        else:
            logger.warning("⚠️ Notion not configured (set NOTION_API_KEY)")
    
    def create_page(
        self,
        properties: Dict[str, Any],
        children: Optional[List[Dict]] = None
    ) -> Optional[Dict]:
        """
        Create a new page in database
        
        Args:
            properties: Database properties (Title, Name, Email, etc.)
            children: Page content blocks
            
        Example:
            client.create_page({
                "Name": {"title": [{"text": {"content": "John"}}]},
                "Phone": {"phone_number": "+919876543210"},
                "Status": {"select": {"name": "New Lead"}}
            })
        """
        if not self.enabled:
            return None
        
        data = {
            "parent": {"database_id": self.database_id},
            "properties": properties
        }
        
        if children:
            data["children"] = children
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/pages",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Notion error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Notion request error: {e}")
            return None
    
    def query_database(
        self,
        filter_props: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Query database for pages
        
        Args:
            filter_props: Filter properties
            sorts: Sort order
            page_size: Results per page
        """
        if not self.enabled:
            return []
        
        data = {"page_size": page_size}
        
        if filter_props:
            data["filter"] = filter_props
        
        if sorts:
            data["sorts"] = sorts
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/databases/{self.database_id}/query",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            return []
            
        except Exception as e:
            logger.error(f"Query error: {e}")
            return []
    
    def add_lead(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        source: str = "WhatsApp",
        notes: Optional[str] = None
    ) -> bool:
        """
        Quick add a lead from WhatsApp
        
        Your Notion database should have:
        - Name (title)
        - Phone (phone_number)
        - Email (email)
        - Source (select)
        - Notes (rich_text)
        """
        if not self.enabled:
            return False
        
        properties = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Phone": {"phone_number": phone},
            "Source": {"select": {"name": source}}
        }
        
        if email:
            properties["Email"] = {"email": email}
        
        if notes:
            properties["Notes"] = {"rich_text": [{"text": {"content": notes}}]}
        
        result = self.create_page(properties)
        return result is not None
    
    def update_page(self, page_id: str, properties: Dict) -> bool:
        """Update page properties"""
        if not self.enabled:
            return False
        
        try:
            response = requests.patch(
                f"{self.BASE_URL}/pages/{page_id}",
                headers=self.headers,
                json={"properties": properties},
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Update page error: {e}")
            return False
    
    def search_pages(self, query: str, page_size: int = 10) -> List[Dict]:
        """Search for pages"""
        if not self.enabled:
            return []
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/search",
                headers=self.headers,
                json={"query": query, "page_size": page_size},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            return []
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []


def setup_notion():
    """Interactive setup for Notion"""
    print("\n" + "="*50)
    print("📝 Notion Setup")
    print("="*50 + "\n")
    
    print("How to setup Notion Integration:")
    print("1. Go to https://www.notion.so/my-integrations")
    print("2. Click 'New integration'")
    print("3. Name it 'WhatsApp Bot'")
    print("4. Copy the API Key")
    print("5. Create a database with columns: Name, Phone, Email, Source")
    print("6. Share the database with your integration")
    print("7. Copy the Database ID from the URL\n")
    
    api_key = input("Notion API Key (secret_xxx): ").strip()
    database_id = input("Database ID: ").strip()
    
    if api_key and database_id:
        with open(".env", "a") as f:
            f.write(f"\n# Notion CRM\n")
            f.write(f"NOTION_API_KEY={api_key}\n")
            f.write(f"NOTION_DATABASE_ID={database_id}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ Both API Key and Database ID required!")


if __name__ == "__main__":
    setup_notion()
