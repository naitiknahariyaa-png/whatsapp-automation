"""
Qdrant Integration - FREE Vector Database
==========================================
AI-powered similarity search

Based on: https://github.com/qdrant/qdrant

Features:
- Vector storage & search
- Semantic similarity
- AI/ML embeddings
- RAG support
- 100% FREE!

Setup:
    docker run -d -p 6333:6333 qdrant/qdrant
"""

import os
import logging
import requests
import json
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class QdrantClient:
    """
    Qdrant Vector Database Client
    
    Use Cases:
    - Store AI embeddings
    - Semantic search
    - RAG (Retrieval Augmented Generation)
    - Similarity search
    - Product recommendations
    
    Setup:
    1. Docker (FREE):
       docker run -d -p 6333:6333 qdrant/qdrant
    
    Environment:
    - QDRANT_URL=http://localhost:6333
    - QDRANT_API_KEY=key
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY", "")
        self.enabled = self._check_connection()
        
        self.headers = {"Content-Type": "application/json"}
        if self.api_key:
            self.headers["api-key"] = self.api_key
        
        if self.enabled:
            logger.info(f"✅ Qdrant configured: {self.url}")
        else:
            logger.warning("⚠️ Qdrant not configured")
    
    def _check_connection(self) -> bool:
        try:
            r = requests.get(f"{self.url}/collections", headers=self.headers, timeout=5)
            return r.status_code == 200
        except:
            return False
    
    def create_collection(
        self,
        name: str,
        vector_size: int = 768,
        distance: str = "Cosine"
    ) -> bool:
        """Create collection (table)"""
        payload = {
            "name": name,
            "vectors": {
                "size": vector_size,
                "distance": distance
            }
        }
        
        try:
            response = requests.put(
                f"{self.url}/collections/{name}",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Qdrant create collection error: {e}")
            return False
    
    def add_point(
        self,
        collection_name: str,
        vector: List[float],
        payload: Dict,
        point_id: Optional[str] = None
    ) -> bool:
        """Add a point (document)"""
        import uuid
        point_id = point_id or str(uuid.uuid4())
        
        payload_data = {
            "points": [{
                "id": point_id,
                "vector": vector,
                "payload": payload
            }]
        }
        
        try:
            response = requests.put(
                f"{self.url}/collections/{collection_name}/points",
                headers=self.headers,
                json=payload_data,
                timeout=10
            )
            return response.status_code in [200, 202]
        except Exception as e:
            logger.error(f"Qdrant add point error: {e}")
            return False
    
    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """Search similar vectors"""
        payload = {
            "vector": query_vector,
            "limit": limit,
            "with_payload": True
        }
        if score_threshold:
            payload["score_threshold"] = score_threshold
        
        try:
            response = requests.post(
                f"{self.url}/collections/{collection_name}/points/search",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("result", [])
            return []
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            return []
    
    def delete_point(self, collection_name: str, point_id: str) -> bool:
        """Delete a point"""
        try:
            response = requests.delete(
                f"{self.url}/collections/{collection_name}/points/{point_id}",
                headers=self.headers,
                timeout=10
            )
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Qdrant delete error: {e}")
            return False
    
    def get_collections(self) -> List[str]:
        """List all collections"""
        try:
            response = requests.get(
                f"{self.url}/collections",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return [c["name"] for c in data.get("result", {}).get("collections", [])]
            return []
        except Exception as e:
            logger.error(f"Qdrant list error: {e}")
            return []


def setup_qdrant():
    """Setup guide for Qdrant"""
    print("\n" + "="*50)
    print("🧠 Qdrant Vector DB Setup")
    print("="*50 + "\n")
    
    print("Run with Docker (FREE):")
    print("-" * 40)
    print("docker run -d -p 6333:6333 \\")
    print("  -v $(pwd)/qdrant_storage:/qdrant/storage \\")
    print("  qdrant/qdrant")
    print("\nDefault URL: http://localhost:6333\n")
    
    url = input("Qdrant URL (press Enter for default): ").strip()
    if not url:
        url = "http://localhost:6333"
    
    key = input("API Key (optional): ").strip()
    
    with open(".env", "a") as f:
        f.write(f"\n# Qdrant (Vector Database)\n")
        f.write(f"QDRANT_URL={url}\n")
        if key:
            f.write(f"QDRANT_API_KEY={key}\n")
    print("✅ Saved to .env!")


if __name__ == "__main__":
    setup_qdrant()
