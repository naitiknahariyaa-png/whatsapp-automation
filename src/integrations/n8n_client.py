"""
N8N Workflow Integration - Connect to 400+ Automations
Trigger workflows, CRM updates, email automation, and more.
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class N8NClient:
    """
    N8N Webhook Client
    
    Features:
    - Trigger workflow automations
    - CRM integrations (HubSpot, Salesforce)
    - Email automation
    - Calendar booking
    - Order processing
    
    Setup:
    1. Install N8N: docker run -d -p 5678:5678 n8nio/n8n
    2. Create workflow with webhook trigger
    3. Copy webhook URL
    
    Environment:
    - N8N_WEBHOOK_URL=https://your-n8n.com/webhook/whatsapp
    - N8N_API_KEY=xxx (optional)
    """
    
    def __init__(
        self,
        webhook_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.webhook_url = webhook_url or os.getenv("N8N_WEBHOOK_URL", "")
        self.api_key = api_key or os.getenv("N8N_API_KEY", "")
        self.enabled = bool(self.webhook_url)
        
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers["X-N8N-API-KEY"] = self.api_key
        
        if self.enabled:
            logger.info(f"✅ N8N configured: {self.webhook_url}")
        else:
            logger.warning("⚠️ N8N not configured (set N8N_WEBHOOK_URL)")
    
    def trigger_workflow(
        self,
        event: str,
        data: Dict[str, Any],
        wait_for_response: bool = True,
        timeout: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Trigger N8N workflow
        
        Args:
            event: Event type (e.g., 'new_message', 'order', 'booking')
            data: Event data to send
            wait_for_response: Wait for workflow response
            timeout: Request timeout in seconds
            
        Returns:
            Workflow response or None
        """
        if not self.enabled:
            return None
        
        try:
            payload = {
                "event": event,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            if wait_for_response:
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=timeout
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    logger.error(f"N8N error: {response.status_code} - {response.text}")
                    return None
            else:
                # Fire and forget
                requests.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=5
                )
                return {"status": "triggered"}
                
        except requests.exceptions.Timeout:
            logger.error(f"N8N timeout after {timeout}s")
            return None
        except Exception as e:
            logger.error(f"N8N trigger error: {e}")
            return None
    
    def on_new_message(self, sender: str, message: str, name: str = "") -> Optional[Dict]:
        """
        Trigger workflow on new WhatsApp message
        
        Args:
            sender: Phone number
            message: Message text
            name: Contact name (optional)
            
        Returns:
            Workflow response
        """
        return self.trigger_workflow(
            event="new_message",
            data={
                "source": "whatsapp",
                "sender": sender,
                "name": name,
                "message": message
            }
        )
    
    def on_order(self, sender: str, items: List[str], total: float) -> Optional[Dict]:
        """
        Trigger workflow for new order
        
        Args:
            sender: Phone number
            items: List of order items
            total: Order total
            
        Returns:
            Workflow response
        """
        return self.trigger_workflow(
            event="new_order",
            data={
                "source": "whatsapp",
                "sender": sender,
                "items": items,
                "total": total
            }
        )
    
    def on_booking_request(
        self,
        sender: str,
        service: str,
        date: str,
        time: str
    ) -> Optional[Dict]:
        """
        Trigger workflow for booking request
        
        Args:
            sender: Phone number
            service: Service name
            date: Requested date
            time: Requested time
            
        Returns:
            Workflow response
        """
        return self.trigger_workflow(
            event="booking_request",
            data={
                "source": "whatsapp",
                "sender": sender,
                "service": service,
                "date": date,
                "time": time
            }
        )
    
    def on_lead_capture(
        self,
        sender: str,
        name: str,
        email: str,
        interest: str
    ) -> Optional[Dict]:
        """
        Trigger workflow for lead capture
        
        Args:
            sender: Phone number
            name: Person's name
            email: Email address
            interest: What they're interested in
            
        Returns:
            Workflow response
        """
        return self.trigger_workflow(
            event="lead_captured",
            data={
                "source": "whatsapp",
                "sender": sender,
                "name": name,
                "email": email,
                "interest": interest
            }
        )
    
    def get_workflow_response(self, default: str = "") -> str:
        """
        Get response from N8N workflow
        
        Use this after triggering a workflow to get the response
        """
        if not self.enabled:
            return default
        
        try:
            response = requests.get(
                self.webhook_url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", default)
                
        except:
            pass
        
        return default


# Quick setup function
def setup_n8n():
    """Guide user to setup N8N"""
    print("""
╔══════════════════════════════════════════════════════════╗
║           N8N Workflow Automation Setup                   ║
╚══════════════════════════════════════════════════════════╝

1. Install N8N:
   docker run -d --name n8n -p 5678:5678 n8nio/n8n

2. Open: http://localhost:5678

3. Create Workflow:
   • Click "Workflows" → "New"
   • Add "Webhook" node (start)
   • Connect to your desired actions:
     - HTTP Request (send to CRM)
     - Gmail (send email)
     - Google Sheets (save data)
     - And 400+ more!

4. Get Webhook URL:
   • Click on Webhook node
   • Set method to POST
   • Copy the webhook URL

5. Add to .env:
   N8N_WEBHOOK_URL=https://your-n8n.com/webhook/whatsapp

Popular Workflows:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Lead Collection:
   WhatsApp → N8N → HubSpot → Email confirmation

🛒 Order Processing:
   WhatsApp → N8N → WooCommerce → Invoice email

📅 Appointment Booking:
   WhatsApp → N8N → Google Calendar → Confirmation

📊 Auto-Reply:
   WhatsApp → N8N → AI → Response

🔗 Connect to 400+ services!
   https://n8n.io/integrations
""")


# Example: Create a simple CRM workflow
def create_crm_workflow_example():
    """Example N8N workflow JSON for CRM integration"""
    return {
        "name": "WhatsApp CRM Integration",
        "nodes": [
            {
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "position": [250, 300],
                "webhookId": "whatsapp-crm",
                "parameters": {
                    "httpMethod": "POST",
                    "path": "whatsapp-crm",
                    "responseMode": "onReceived",
                    "options": {}
                }
            },
            {
                "name": "Create HubSpot Contact",
                "type": "n8n-nodes-base.hubspot",
                "position": [500, 300],
                "parameters": {
                    "operation": "create",
                    "email": "={{ $json.body.data.sender }}@ whatsapp.com",
                    "additionalFields": {
                        "firstname": "={{ $json.body.data.name }}"
                    }
                }
            },
            {
                "name": "Send Email",
                "type": "n8n-nodes-base.emailSend",
                "position": [750, 300],
                "parameters": {
                    "to": "={{ $json.body.data.email }}",
                    "subject": "Thank you for contacting us!",
                    "text": "={{ $json.body.data.message }}"
                }
            }
        ],
        "connections": {
            "Webhook": {
                "main": [[{"node": "Create HubSpot Contact", "type": "main", "index": 0}]]
            },
            "Create HubSpot Contact": {
                "main": [[{"node": "Send Email", "type": "main", "index": 0}]]
            }
        }
    }


if __name__ == "__main__":
    setup_n8n()
