"""
Meilisearch Integration - FREE Lightning-Fast Search
===================================================
Self-hosted search engine

Based on: https://github.com/meilisearch/meilisearch

Features:
- Instant search results
- Typo tolerance
- Faceted search
- 100% FREE!

Setup:
    docker run -d -p 7700:7700 getmeili/meilisearch
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class MeilisearchClient:
    """
    Meilisearch Client - Lightning Fast Search
    
    Use Cases:
    - Product search
    - Knowledge base search
    - Real-time search
    - Autocomplete
    
    Setup:
    1. Docker (FREE):
       docker run -d -p 7700:7700 getmeili/meilisearch
    
    Environment:
    - MEILISEARCH_URL=http://localhost:7700
    - MEILISEARCH_KEY=master-key
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.url = url or os.getenv("MEILISEARCH_URL", "http://localhost:7700")
        self.api_key = api_key or os.getenv("MEILISEARCH_KEY", "")
        self.enabled = self._check_connection()
        
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        if self.enabled:
            logger.info(f"✅ Meilisearch configured: {self.url}")
        else:
            logger.warning("⚠️ Meilisearch not configured")
    
    def _check_connection(self) -> bool:
        try:
            r = requests.get(f"{self.url}/health", timeout=5)
            return r.status_code == 200
        except:
            return False
    
    def create_index(
        self,
        name: str,
        primary_key: str = "id"
    ) -> Optional[Dict]:
        """Create a new index"""
        payload = {
            "uid": name.lower().replace(" ", "_"),
            "primaryKey": primary_key
        }
        
        try:
            response = requests.post(
                f"{self.url}/indexes",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Meilisearch create index error: {e}")
            return None
    
    def add_documents(
        self,
        index_name: str,
        documents: List[Dict]
    ) -> Optional[Dict]:
        """Add documents to index"""
        try:
            # Get index UID
            uid = index_name.lower().replace(" ", "_")
            
            response = requests.post(
                f"{self.url}/indexes/{uid}/documents",
                headers=self.headers,
                json=documents,
                timeout=30
            )
            if response.status_code in [200, 202]:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Meilisearch add docs error: {e}")
            return None
    
    def search(
        self,
        index_name: str,
        query: str,
        limit: int = 20,
        attributes_to_retrieve: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Search documents"""
        try:
            uid = index_name.lower().replace(" ", "_")
            
            payload = {
                "q": query,
                "limit": limit
            }
            if attributes_to_retrieve:
                payload["attributesToRetrieve"] = attributes_to_retrieve
            
            response = requests.post(
                f"{self.url}/indexes/{uid}/search",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Meilisearch search error: {e}")
            return None
    
    def delete_document(self, index_name: str, doc_id: str) -> bool:
        """Delete a document"""
        try:
            uid = index_name.lower().replace(" ", "_")
            response = requests.delete(
                f"{self.url}/indexes/{uid}/documents/{doc_id}",
                headers=self.headers,
                timeout=10
            )
            return response.status_code in [200, 202, 204]
        except Exception as e:
            logger.error(f"Meilisearch delete error: {e}")
            return False
    
    def update_settings(
        self,
        index_name: str,
        searchable_attributes: Optional[List[str]] = None,
        filterable_attributes: Optional[List[str]] = None,
        sortable_attributes: Optional[List[str]] = None
    ) -> bool:
        """Update index settings"""
        try:
            uid = index_name.lower().replace(" ", "_")
            
            settings = {}
            if searchable_attributes:
                settings["searchableAttributes"] = searchable_attributes
            if filterable_attributes:
                settings["filterableAttributes"] = filterable_attributes
            if sortable_attributes:
                settings["sortableAttributes"] = sortable_attributes
            
            response = requests.patch(
                f"{self.url}/indexes/{uid}/settings",
                headers=self.headers,
                json=settings,
                timeout=10
            )
            return response.status_code in [200, 202]
        except Exception as e:
            logger.error(f"Meilisearch settings error: {e}")
            return False


def setup_meilisearch():
    """Setup guide for Meilisearch"""
    print("\n" + "="*50)
    print("🔍 Meilisearch Setup")
    print("="*50 + "\n")
    
    print("Run with Docker (FREE):")
    print("-" * 40)
    print("docker run -d -p 7700:7700 \\")
    print("  -v $(pwd)/meili_data:/meili_data \\")
    print("  getmeili/meilisearch")
    print("\nDefault URL: http://localhost:7700")
    print("Default Key: (no key required for dev)\n")
    
    url = input("Meilisearch URL (press Enter for default): ").strip()
    if not url:
        url = "http://localhost:7700"
    
    key = input("Master Key (optional): ").strip()
    
    with open(".env", "a") as f:
        f.write(f"\n# Meilisearch (Lightning Fast Search)\n")
        f.write(f"MEILISEARCH_URL={url}\n")
        if key:
            f.write(f"MEILISEARCH_KEY={key}\n")
    print("✅ Saved to .env!")


if __name__ == "__main__":
    setup_meilisearch()
