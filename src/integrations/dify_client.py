"""
Dify Integration - Open Source AI App Builder
==============================================
Build AI workflows without coding

Based on: https://github.com/langgenius/dify

Features:
- Visual workflow builder
- RAG (Retrieval Augmented Generation)
- Agentic AI
- Multiple LLM support
- 100% FREE (self-hosted)

Setup:
    1. Docker: docker run -d -p 80:80 -v ~/dify-data:/data difycommunity/dify-api
    2. Or use cloud: https://dify.ai
    3. Get API Key from Settings
    
Environment:
    DIFY_API_KEY=app-xxx
    DIFY_URL=http://localhost:80
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class DifyClient:
    """
    Dify AI Workflow Client
    
    Use Cases:
    - Build chatbots with workflows
    - RAG-powered knowledge bases
    - Multi-step AI agents
    - Custom AI applications
    
    Setup:
    1. Self-hosted (FREE):
       docker run -d -p 80:80 -v ~/dify-data:/data difycommunity/dify-api
    
    2. Cloud:
       https://dify.ai
    
    3. Get API key from Settings → API Keys
    
    Environment:
    - DIFY_API_KEY=app-xxx
    - DIFY_URL=http://localhost:80
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("DIFY_API_KEY", "")
        self.url = url or os.getenv("DIFY_URL", "http://localhost:80")
        self.enabled = bool(self.api_key)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.enabled:
            logger.info(f"✅ Dify configured: {self.url}")
        else:
            logger.warning("⚠️ Dify not configured (set DIFY_API_KEY)")
    
    def chat(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        user: str = "whatsapp-user",
        response_mode: str = "blocking"
    ) -> Optional[Dict]:
        """
        Send chat message to Dify app
        
        Args:
            query: User message
            conversation_id: Continue conversation
            user: User identifier
            response_mode: "blocking" or "streaming"
        """
        if not self.enabled:
            return None
        
        payload = {
            "query": query,
            "user": user,
            "response_mode": response_mode,
            "conversation_id": conversation_id or ""
        }
        
        try:
            response = requests.post(
                f"{self.url}/v1/chat-messages",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Dify chat error: {e}")
            return None
    
    def completion(
        self,
        query: str,
        user: str = "whatsapp-user"
    ) -> Optional[str]:
        """
        Text completion (non-chat)
        """
        if not self.enabled:
            return None
        
        payload = {
            "inputs": {},
            "query": query,
            "response_mode": "blocking",
            "user": user
        }
        
        try:
            response = requests.post(
                f"{self.url}/v1/completion-messages",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("answer", "")
            return None
        except Exception as e:
            logger.error(f"Dify completion error: {e}")
            return None
    
    def create_app(
        self,
        name: str,
        description: str,
        app_type: str = "agent-app"
    ) -> Optional[Dict]:
        """
        Create new Dify application
        
        app_type options:
        - agent-app (Agent)
        - chat-app (Chatbot)
        - completion-app (Text generation)
        - agent-workflow (Workflow)
        """
        if not self.enabled:
            return None
        
        payload = {
            "name": name,
            "description": description,
            "icon": "🤖",
            "app_type": app_type,
            "mode": "advanced-chat"
        }
        
        try:
            response = requests.post(
                f"{self.url}/v1/apps",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Dify create app error: {e}")
            return None
    
    def get_app_info(self, app_id: str) -> Optional[Dict]:
        """Get application details"""
        if not self.enabled:
            return None
        
        try:
            response = requests.get(
                f"{self.url}/v1/apps/{app_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Dify get app error: {e}")
            return None
    
    def list_datasets(self) -> List[Dict]:
        """List knowledge bases"""
        if not self.enabled:
            return []
        
        try:
            response = requests.get(
                f"{self.url}/v1/datasets",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []
        except Exception as e:
            logger.error(f"Dify list datasets error: {e}")
            return []
    
    def add_document(
        self,
        dataset_id: str,
        text: str,
        name: str = "document"
    ) -> Optional[Dict]:
        """
        Add document to knowledge base
        """
        if not self.enabled:
            return None
        
        payload = {
            "indexing_technique": "high_quality",
            "process_rule": {
                "mode": "custom",
                "rules": {
                    "pre_processing_rules": [
                        {"id": "remove_extra_spaces", "enabled": True},
                        {"id": "remove_urls_emails", "enabled": False}
                    ],
                    "segmentation": {
                        "separator": "\n",
                        "max_tokens": 500
                    }
                }
            },
            "documents": [
                {
                    "input_form": "text",
                    "input": text,
                    "name": name
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.url}/v1/datasets/{dataset_id}/documents",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Dify add document error: {e}")
            return None
    
    def rag_chat(
        self,
        query: str,
        dataset_id: str,
        user: str = "whatsapp-user"
    ) -> Optional[str]:
        """
        Chat with knowledge base (RAG)
        """
        if not self.enabled:
            return None
        
        payload = {
            "query": query,
            "user": user,
            "retrieval_model": {
                "search_method": "semantic_search",
                "reranking_enable": False,
                "top_k": 3,
                "score_threshold_enabled": False
            }
        }
        
        try:
            response = requests.post(
                f"{self.url}/v1/datasets/{dataset_id}/retrieve",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Return retrieved context
                records = result.get("data", [])
                if records:
                    context = "\n".join([r.get("content", "") for r in records])
                    return context
            return None
        except Exception as e:
            logger.error(f"Dify RAG error: {e}")
            return None
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload file and get file_id
        """
        if not self.enabled:
            return None
        
        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = requests.post(
                    f"{self.url}/v1/file-upload",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                return response.json().get("id")
            return None
        except Exception as e:
            logger.error(f"Dify upload error: {e}")
            return None


def setup_dify():
    """Interactive setup for Dify"""
    print("\n" + "="*50)
    print("🧠 Dify AI Setup")
    print("="*50 + "\n")
    
    print("OPTION 1: Self-hosted (FREE)")
    print("-" * 40)
    print("1. Run Docker:")
    print("   docker run -d -p 80:80 -v ~/dify-data:/data \\")
    print("      difycommunity/dify-api")
    print("2. Wait 2-3 minutes for startup")
    print("3. Visit http://localhost")
    print("4. Create account and get API key\n")
    
    print("OPTION 2: Cloud (Has free tier)")
    print("-" * 40)
    print("1. Go to https://dify.ai")
    print("2. Sign up for free")
    print("3. Create an app")
    print("4. Get API key from Settings\n")
    
    api_key = input("Dify API Key (app-xxx): ").strip()
    url = input("Dify URL (press Enter for localhost): ").strip()
    
    if not url:
        url = "http://localhost"
    
    if api_key:
        with open(".env", "a") as f:
            f.write(f"\n# Dify AI (Visual Workflow Builder)\n")
            f.write(f"DIFY_API_KEY={api_key}\n")
            f.write(f"DIFY_URL={url}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ API Key required!")


if __name__ == "__main__":
    setup_dify()
