"""
====================================================================
WHATSAPP BUSINESS API CLIENT - Official WhatsApp Integration
====================================================================
Features:
- Webhook handling for incoming messages
- Template message sending
- Status webhook processing (delivered, read)
- Multi-account support
- Proper error handling

This replaces WhatsApp Web (Selenium) with Official API
====================================================================
"""

import os
import hmac
import hashlib
import time
import logging
import json
import asyncio
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import threading
from functools import wraps

import requests

logger = logging.getLogger(__name__)


class MessageStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACTS = "contacts"
    TEMPLATE = "template"
    INTERACTIVE = "interactive"


@dataclass
class WhatsAppMessage:
    """Represents a WhatsApp message"""
    message_id: str
    from_phone: str
    to_phone: str = None
    content: str = None
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = None
    media_url: str = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class WebhookPayload:
    """Incoming webhook payload from Meta"""
    object_type: str
    entry_id: str
    changes: List[Dict]
    raw_data: Dict


class CircuitBreaker:
    """
    Circuit Breaker Pattern - Prevents cascading failures
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise e


class RateLimiter:
    """
    WhatsApp API Rate Limiting
    - Respects Meta's rate limits
    - Implements token bucket algorithm
    """
    
    def __init__(self, max_requests: int = 50, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
        self._lock = threading.Lock()
    
    def acquire(self) -> bool:
        """Acquire rate limit token"""
        with self._lock:
            now = time.time()
            
            # Remove expired timestamps
            self.requests = [t for t in self.requests if now - t < self.window_seconds]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def wait_time(self) -> float:
        """Calculate wait time in seconds"""
        if not self.requests:
            return 0
        
        now = time.time()
        oldest = min(self.requests)
        return max(0, self.window_seconds - (now - oldest))


class WhatsAppBusinessAPI:
    """
    WhatsApp Business Cloud API Client
    
    Features:
    - Send text, media, template messages
    - Receive webhooks (messages, status updates)
    - Verify webhooks (security)
    - Multi-account support
    """
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self, phone_number_id: str, access_token: str, 
                 app_secret: str = None, verify_token: str = None):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.app_secret = app_secret
        self.verify_token = verify_token
        
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter(max_requests=50, window_seconds=60)
        
        self._message_callback: Optional[Callable] = None
        self._status_callback: Optional[Callable] = None
        self._webhook_callbacks: Dict[str, Callable] = {}
        
        logger.info(f"WhatsApp Business API initialized for {phone_number_id}")
    
    def set_message_callback(self, callback: Callable[[WhatsAppMessage], Any]):
        """Set callback for incoming messages"""
        self._message_callback = callback
    
    def set_status_callback(self, callback: Callable[[str, str, Dict], Any]):
        """Set callback for status updates (delivered, read, etc.)"""
        self._status_callback = callback
    
    # =====================================
    # WEBHOOK VERIFICATION
    # =====================================
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verify webhook subscription with Meta
        
        Args:
            mode: 'subscribe' from Meta
            token: Your verify token
            challenge: String to return if verified
        
        Returns:
            challenge string if verified, None otherwise
        """
        if mode == "subscribe" and token == self.verify_token:
            logger.info("Webhook verified successfully")
            return challenge
        
        logger.warning(f"Webhook verification failed: mode={mode}, token={token}")
        return None
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from Meta
        
        Args:
            payload: Raw request body
            signature: X-Hub-Signature-256 header
        
        Returns:
            True if signature is valid
        """
        if not self.app_secret or not signature:
            return True  # Skip verification if not configured
        
        expected = "sha256=" + hmac.new(
            self.app_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    
    # =====================================
    # PROCESS WEBHOOK
    # =====================================
    
    def process_webhook(self, data: Dict) -> List[Dict]:
        """
        Process incoming webhook from Meta
        
        Args:
            data: Webhook payload
        
        Returns:
            List of processed events
        """
        results = []
        
        try:
            if data.get("object") != "whatsapp_business_account":
                logger.debug(f"Ignoring non-WhatsApp webhook: {data.get('object')}")
                return results
            
            for entry in data.get("entry", []):
                org_id = entry.get("id")
                
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    # Process messages
                    for message in value.get("messages", []):
                        result = self._process_incoming_message(message, value)
                        if result:
                            results.append(result)
                    
                    # Process status updates
                    for status in value.get("statuses", []):
                        result = self._process_status_update(status)
                        if result:
                            results.append(result)
                    
                    # Process reactions
                    for reaction in value.get("reactions", []):
                        result = self._process_reaction(reaction)
                        if result:
                            results.append(result)
        
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
        
        return results
    
    def _process_incoming_message(self, message: Dict, value: Dict) -> Optional[Dict]:
        """Process incoming message"""
        try:
            msg = WhatsAppMessage(
                message_id=message.get("id"),
                from_phone=message.get("from"),
                content=message.get("text", {}).get("body") if message.get("type") == "text" else None,
                message_type=MessageType(message.get("type", "text")),
                timestamp=datetime.fromtimestamp(int(message.get("timestamp", 0))),
                metadata={
                    "reply_to": message.get("context", {}).get("id"),
                    "org_id": value.get("id")
                }
            )
            
            # Extract media if present
            if message.get("image"):
                msg.media_url = message["image"].get("id")
                msg.metadata["mime_type"] = message["image"].get("mime_type")
            
            # Call message callback
            if self._message_callback:
                response = self._message_callback(msg)
                return {"type": "message", "processed": True, "response": response}
            
            return {"type": "message", "processed": False}
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return None
    
    def _process_status_update(self, status: Dict) -> Optional[Dict]:
        """Process message status update"""
        try:
            message_id = status.get("id")
            new_status = status.get("status")
            
            # Call status callback
            if self._status_callback:
                self._status_callback(message_id, new_status, status)
            
            return {
                "type": "status",
                "message_id": message_id,
                "status": new_status,
                "processed": True
            }
        
        except Exception as e:
            logger.error(f"Error processing status: {e}")
            return None
    
    def _process_reaction(self, reaction: Dict) -> Optional[Dict]:
        """Process message reaction"""
        return {"type": "reaction", "processed": True}
    
    # =====================================
    # SEND MESSAGES
    # =====================================
    
    def _ensure_rate_limit(self):
        """Wait for rate limit token"""
        while not self.rate_limiter.acquire():
            wait = self.rate_limiter.wait_time()
            if wait > 0:
                time.sleep(wait)
    
    def send_text_message(self, to: str, message: str, 
                          reply_to: str = None,
                          preview_url: bool = False) -> Optional[Dict]:
        """
        Send text message
        
        Args:
            to: Recipient phone number (with country code)
            message: Message text
            reply_to: Message ID to reply to
            preview_url: Show link preview
        
        Returns:
            Response with message_id
        """
        self._ensure_rate_limit()
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message
            }
        }
        
        if reply_to:
            payload["context"] = {"message_id": reply_to}
        
        return self._send_request(payload)
    
    def send_media_message(self, to: str, media_type: str, media_id: str = None,
                           url: str = None, caption: str = None,
                           filename: str = None) -> Optional[Dict]:
        """
        Send media message (image, video, document, audio)
        
        Args:
            to: Recipient phone
            media_type: 'image', 'video', 'document', 'audio'
            media_id: WhatsApp media ID (if uploaded)
            url: Public URL to media
            caption: Media caption
            filename: Filename for documents
        """
        self._ensure_rate_limit()
        
        media_payload = {"type": media_type}
        
        if media_id:
            media_payload[media_type] = {"id": media_id}
        elif url:
            media_payload[media_type] = {"link": url}
            if caption:
                media_payload[media_type]["caption"] = caption
            if filename:
                media_payload[media_type]["filename"] = filename
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            **media_payload
        }
        
        return self._send_request(payload)
    
    def send_interactive_message(self, to: str, buttons: List[Dict] = None,
                                list_rows: List[Dict] = None) -> Optional[Dict]:
        """
        Send interactive message (buttons or list)
        
        Args:
            to: Recipient phone
            buttons: List of buttons [{id, title}]
            list_rows: List of rows for list message
        """
        self._ensure_rate_limit()
        
        if buttons:
            interactive = {
                "type": "buttons",
                "body": {"text": "Please select an option:"},
                "action": {"buttons": [{"type": "reply", "reply": btn} for btn in buttons]}
            }
        elif list_rows:
            interactive = {
                "type": "list",
                "header": {"type": "text", "text": "Select an option"},
                "body": {"text": "Please choose:"},
                "action": {"button": "View Options", "sections": [{"rows": list_rows}]}
            }
        else:
            return None
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": interactive
        }
        
        return self._send_request(payload)
    
    def send_template_message(self, to: str, template_name: str,
                             language_code: str = "en_US",
                             components: List[Dict] = None) -> Optional[Dict]:
        """
        Send template message
        
        Args:
            to: Recipient phone
            template_name: Template name (must be approved)
            language_code: Language code (default: en_US)
            components: Template components (header, body, buttons)
        """
        self._ensure_rate_limit()
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        return self._send_request(payload)
    
    def send_reaction(self, to: str, message_id: str, emoji: str) -> Optional[Dict]:
        """Send reaction to a message"""
        self._ensure_rate_limit()
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "reaction",
            "reaction": {
                "message_id": message_id,
                "emoji": emoji
            }
        }
        
        return self._send_request(payload)
    
    def mark_as_read(self, message_id: str) -> Optional[Dict]:
        """Mark message as read"""
        payload = {
            "messaging_product": "whatsapp",
            "message_id": message_id
        }
        
        return self._send_request(payload)
    
    # =====================================
    # MEDIA MANAGEMENT
    # =====================================
    
    def upload_media(self, file_path: str, media_type: str) -> Optional[str]:
        """
        Upload media to WhatsApp servers
        
        Args:
            file_path: Path to media file
            media_type: 'image', 'video', 'audio', 'document'
        
        Returns:
            Media ID for use in messages
        """
        url = f"{self.BASE_URL}/{self.phone_number_id}/media"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        mime_types = {
            "image": "image/jpeg",
            "video": "video/mp4",
            "audio": "audio/mpeg",
            "document": "application/pdf"
        }
        
        with open(file_path, "rb") as f:
            files = {
                "file": (Path(file_path).name, f, mime_types.get(media_type, "application/octet-stream"))
            }
            data = {"messaging_product": "whatsapp"}
            
            response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            return response.json().get("id")
        
        logger.error(f"Media upload failed: {response.text}")
        return None
    
    def download_media(self, media_id: str) -> Optional[bytes]:
        """Download media content"""
        # First get media URL
        url = f"{self.BASE_URL}/{media_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            media_url = response.json().get("url")
            
            # Download media content
            media_response = requests.get(media_url, headers=headers)
            
            if media_response.status_code == 200:
                return media_response.content
        
        return None
    
    # =====================================
    # INTERNAL METHODS
    # =====================================
    
    def _send_request(self, payload: Dict, retry_count: int = 3) -> Optional[Dict]:
        """
        Send API request with retry and circuit breaker
        """
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(retry_count):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"Message sent: {result.get('messages', [{}])[0].get('id')}")
                    return result
                
                # Rate limited
                if response.status_code == 429:
                    wait = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited, waiting {wait}s")
                    time.sleep(wait)
                    continue
                
                # Circuit breaker trigger
                if response.status_code >= 500:
                    self.circuit_breaker.call(lambda: None)  # Record failure
                
                logger.error(f"API Error: {response.status_code} - {response.text}")
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Request error: {e}")
        
        return None
    
    def get_account_info(self) -> Optional[Dict]:
        """Get WhatsApp Business Account info"""
        url = f"{self.BASE_URL}/{self.phone_number_id}"
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        
        return None
    
    def get_message_info(self, message_id: str) -> Optional[Dict]:
        """Get message status info"""
        url = f"{self.BASE_URL}/{message_id}"
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        
        return None


# =====================================
# FLASK WEBHOOK HANDLER EXAMPLE
# =====================================

def create_webhook_routes(app, whatsapp_api: WhatsAppBusinessAPI, db):
    """
    Create Flask routes for WhatsApp webhook
    
    Args:
        app: Flask app instance
        whatsapp_api: WhatsAppBusinessAPI instance
        db: Database instance
    """
    from flask import request, jsonify
    
    @app.route("/webhook", methods=["GET"])
    def webhook_verify():
        """Webhook verification endpoint"""
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        result = whatsapp_api.verify_webhook(mode, token, challenge)
        
        if result:
            return result, 200
        return "Verification failed", 403
    
    @app.route("/webhook", methods=["POST"])
    def webhook_receive():
        """Receive webhook from Meta"""
        data = request.get_json()
        
        # Verify signature
        signature = request.headers.get("X-Hub-Signature-256", "")
        
        if not whatsapp_api.verify_signature(request.data, signature):
            logger.warning("Invalid webhook signature")
            return "Invalid signature", 401
        
        # Process webhook
        events = whatsapp_api.process_webhook(data)
        
        for event in events:
            if event.get("type") == "message":
                msg = event.get("processed")
                if msg:
                    # Track in database
                    db.track_event(
                        org_id=msg.get("org_id"),
                        metric_type="messages_received",
                        value=1
                    )
        
        return "OK", 200


# =====================================
# TWILIO COMPATIBILITY LAYER
# =====================================

class TwilioWhatsApp:
    """
    Twilio WhatsApp Integration
    Alternative to Meta's API if using Twilio
    """
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.client = None
        
        try:
            from twilio.rest import Client
            self.client = Client(account_sid, auth_token)
        except ImportError:
            logger.warning("Twilio not installed")
    
    def send_message(self, to: str, body: str) -> Optional[str]:
        """Send WhatsApp message via Twilio"""
        if not self.client:
            return None
        
        message = self.client.messages.create(
            body=body,
            from_=f"whatsapp:{self.from_number}",
            to=f"whatsapp:{to}"
        )
        
        return message.sid
    
    def process_webhook(self, form_data: Dict) -> WhatsAppMessage:
        """Process Twilio webhook"""
        return WhatsAppMessage(
            message_id=form_data.get("MessageSid"),
            from_phone=form_data.get("From", "").replace("whatsapp:", ""),
            content=form_data.get("Body"),
            message_type=MessageType.TEXT
        )
