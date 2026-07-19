"""
ActivePieces Integration - FREE Automation Builder
==================================================
Zapier alternative, open source

Based on: https://github.com/activepieces/activepieces

Features:
- Visual workflow builder
- 100+ integrations
- Trigger actions
- Code snippets
- 100% FREE!

Setup:
    docker run -d -p 8080:80 activepieces/activepieces
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class ActivePiecesClient:
    """
    ActivePieces Automation Client
    
    Use Cases:
    - Workflow automation
    - Connect apps
    - Trigger actions
    - Data sync
    - Business automation
    
    Setup:
    1. Docker (FREE):
       docker run -d -p 8080:80 activepieces/activepieces
    
    2. Cloud (Free tier):
       https://activepieces.com
    
    Environment:
    - ACTIVEPIECES_URL=http://localhost:8080
    - ACTIVEPIECES_API_KEY=xxx
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("ACTIVEPIECES_API_KEY", "")
        self.url = url or os.getenv("ACTIVEPIECES_URL", "http://localhost:8080")
        self.enabled = bool(self.api_key)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.enabled:
            logger.info(f"✅ ActivePieces configured")
        else:
            logger.warning("⚠️ ActivePieces not configured")
    
    def trigger_webhook(self, webhook_url: str, data: Dict) -> bool:
        """
        Trigger a webhook flow
        
        Use this to trigger any ActivePieces flow that has a webhook trigger
        """
        try:
            response = requests.post(webhook_url, json=data, timeout=30)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            logger.error(f"ActivePieces webhook error: {e}")
            return False
    
    def create_flow_run(
        self,
        flow_id: str,
        data: Dict
    ) -> Optional[Dict]:
        """Create a new flow run"""
        payload = {
            "flowId": flow_id,
            "collectionVariant": {},
            "searchQuery": "",
            "payload": data
        }
        
        try:
            response = requests.post(
                f"{self.url}/v1/flows/{flow_id}/runs",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"ActivePieces flow run error: {e}")
            return None
    
    def get_flows(self) -> List[Dict]:
        """Get all flows"""
        try:
            response = requests.get(
                f"{self.url}/v1/flows",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("flows", [])
            return []
        except Exception as e:
            logger.error(f"ActivePieces get flows error: {e}")
            return []
    
    def get_flow_runs(self, flow_id: str) -> List[Dict]:
        """Get runs for a flow"""
        try:
            response = requests.get(
                f"{self.url}/v1/flows/{flow_id}/runs",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("runs", [])
            return []
        except Exception as e:
            logger.error(f"ActivePieces get runs error: {e}")
            return []
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> bool:
        """Send email via ActivePieces"""
        payload = {
            "to": to,
            "subject": subject,
            "body": body,
            "from": from_email or "noreply@example.com"
        }
        
        try:
            response = requests.post(
                f"{self.url}/v1/pieces/send-email",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"ActivePieces email error: {e}")
            return False
    
    def create_spreadsheet_row(
        self,
        spreadsheet_id: str,
        values: List[Any]
    ) -> bool:
        """Add row to spreadsheet (Google Sheets, etc.)"""
        payload = {
            "spreadsheetId": spreadsheet_id,
            "values": values
        }
        
        try:
            response = requests.post(
                f"{self.url}/v1/pieces/google-sheets/add-row",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"ActivePieces spreadsheet error: {e}")
            return False
    
    def create_crm_contact(
        self,
        name: str,
        email: str,
        phone: str = ""
    ) -> bool:
        """Add contact to CRM"""
        payload = {
            "name": name,
            "email": email,
            "phone": phone
        }
        
        try:
            response = requests.post(
                f"{self.url}/v1/pieces/hubspot/create-contact",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"ActivePieces CRM error: {e}")
            return False
    
    def create_task(
        self,
        title: str,
        project: str = "Default"
    ) -> bool:
        """Create a task (Asana, Todoist, etc.)"""
        payload = {
            "title": title,
            "project": project
        }
        
        try:
            response = requests.post(
                f"{self.url}/v1/pieces/tasks/create",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"ActivePieces task error: {e}")
            return False


def setup_activepieces():
    """Setup guide for ActivePieces"""
    print("\n" + "="*50)
    print("⚡ ActivePieces Automation Setup")
    print("="*50 + "\n")
    
    print("OPTION 1: Self-hosted (FREE)")
    print("-" * 40)
    print("docker run -d -p 8080:80 \\")
    print("  -v activepieces_data:/data \\")
    print("  activepieces/activepieces")
    print("\nVisit http://localhost:8080\n")
    
    print("OPTION 2: Cloud (Free tier)")
    print("-" * 40)
    print("1. Go to https://activepieces.com")
    print("2. Sign up free")
    print("3. Create workflows")
    print("4. Get API key from Settings\n")
    
    url = input("ActivePieces URL (press Enter for localhost): ").strip()
    if not url:
        url = "http://localhost:8080"
    
    key = input("API Key: ").strip()
    
    if key:
        with open(".env", "a") as f:
            f.write(f"\n# ActivePieces (Automation)\n")
            f.write(f"ACTIVEPIECES_URL={url}\n")
            f.write(f"ACTIVEPIECES_API_KEY={key}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ API Key required!")


if __name__ == "__main__":
    setup_activepieces()
