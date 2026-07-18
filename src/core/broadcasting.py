"""
====================================================================
BROADCASTING ENGINE - Campaign Management System
====================================================================
Features:
- Contact segmentation
- Scheduled campaigns
- A/B testing
- Template personalization
- Rate limiting (WhatsApp compliant)
- Real-time statistics

This is how Aisensy sends messages to thousands of contacts
====================================================================
"""

import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import secrets
import hashlib

logger = logging.getLogger(__name__)


class CampaignStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SegmentType(Enum):
    ALL = "all"
    TAG = "tag"
    OPTED_IN = "opted_in"
    DATE_RANGE = "date_range"
    CUSTOM = "custom"


@dataclass
class Segment:
    """Contact segment definition"""
    id: str
    name: str
    segment_type: SegmentType
    criteria: Dict[str, Any]
    estimated_count: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Segment':
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            segment_type=SegmentType(data.get("type", "all")),
            criteria=data.get("criteria", {}),
            estimated_count=data.get("estimated_count", 0)
        )


@dataclass
class CampaignStats:
    """Campaign statistics"""
    total: int = 0
    sent: int = 0
    delivered: int = 0
    read: int = 0
    replied: int = 0
    failed: int = 0
    pending: int = 0
    
    @property
    def delivery_rate(self) -> float:
        return round(self.delivered / self.sent * 100, 1) if self.sent else 0
    
    @property
    def read_rate(self) -> float:
        return round(self.read / self.delivered * 100, 1) if self.delivered else 0
    
    @property
    def response_rate(self) -> float:
        return round(self.replied / self.delivered * 100, 1) if self.delivered else 0
    
    def to_dict(self) -> Dict:
        return {
            "total": self.total,
            "sent": self.sent,
            "delivered": self.delivered,
            "read": self.read,
            "replied": self.replied,
            "failed": self.failed,
            "pending": self.pending,
            "delivery_rate": self.delivery_rate,
            "read_rate": self.read_rate,
            "response_rate": self.response_rate
        }


@dataclass
class MessageItem:
    """Individual message in campaign"""
    contact_id: int
    phone: str
    content: str
    idempotency_key: str
    status: str = "pending"
    sent_at: datetime = None
    delivered_at: datetime = None
    error: str = None


class WhatsAppRateLimiter:
    """
    WhatsApp-compliant rate limiter
    
    Meta WhatsApp Business API limits:
    - 50 requests/minute sustained
    - Burst up to 100 requests
    - Per-conversation limits
    
    This ensures we stay within limits and avoid bans
    """
    
    def __init__(self, requests_per_minute: int = 50, burst_limit: int = 100):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        
        self.minute_requests = []
        self.burst_tokens = burst_limit
        self.last_refill = time.time()
        self._lock = threading.Lock()
    
    def acquire(self) -> bool:
        """Acquire permission to send"""
        with self._lock:
            now = time.time()
            
            # Refill tokens every second
            elapsed = now - self.last_refill
            if elapsed >= 1:
                tokens_to_add = int(elapsed * self.requests_per_minute / 60)
                self.burst_tokens = min(self.burst_limit, self.burst_tokens + tokens_to_add)
                self.last_refill = now
            
            # Wait for token
            if self.burst_tokens > 0:
                self.burst_tokens -= 1
                return True
            
            return False
    
    def wait_time(self) -> float:
        """Calculate wait time for next available token"""
        with self._lock:
            if self.burst_tokens > 0:
                return 0
            return 60 / self.requests_per_minute


class BroadcastingEngine:
    """
    Campaign broadcasting engine
    
    Features:
    - Multi-contact broadcasting
    - Personalization with variables
    - Rate limiting
    - Progress tracking
    - Error handling
    """
    
    def __init__(self, db, whatsapp_api, config: Dict = None):
        self.db = db
        self.whatsapp_api = whatsapp_api
        self.config = config or {}
        
        # Rate limiter
        self.rate_limiter = WhatsAppRateLimiter(
            requests_per_minute=self.config.get("requests_per_minute", 50),
            burst_limit=self.config.get("burst_limit", 100)
        )
        
        # Active campaigns
        self.active_campaigns: Dict[int, Dict] = {}
        
        # Callbacks
        self.on_progress: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        logger.info("Broadcasting engine initialized")
    
    def create_campaign(self, org_id: int, name: str, 
                       content: str, segment: Segment,
                       scheduled_at: datetime = None) -> int:
        """
        Create new broadcast campaign
        
        Args:
            org_id: Organization ID
            name: Campaign name
            content: Message template
            segment: Contact segment to target
            scheduled_at: Optional scheduled time
        
        Returns:
            Campaign ID
        """
        # Estimate contact count
        estimated_count = self.db.get_contact_count(org_id, segment.criteria)
        
        # Create campaign
        campaign_id = self.db.create_campaign(
            org_id=org_id,
            name=name,
            segment_criteria=segment.criteria,
            scheduled_at=scheduled_at
        )
        
        # Store template
        template_id = self.db.create_template(
            org_id=org_id,
            name=f"Campaign: {name}",
            content=content,
            category="broadcast"
        )
        
        logger.info(f"Created campaign {campaign_id}: {name} ({estimated_count} contacts)")
        
        return campaign_id
    
    def prepare_messages(self, campaign_id: int, org_id: int,
                         content: str, segment: Segment) -> List[MessageItem]:
        """
        Prepare messages for all segment contacts
        
        Returns:
            List of MessageItem objects
        """
        messages = []
        contacts = self.db.get_contacts(org_id, limit=100000)
        
        # Apply segment filters
        filtered_contacts = self._filter_contacts(contacts, segment)
        
        for contact in filtered_contacts:
            # Personalize message
            personalized = self._personalize_message(content, contact)
            
            # Generate idempotency key
            idempotency_key = self._generate_idempotency_key(
                campaign_id, contact['id']
            )
            
            messages.append(MessageItem(
                contact_id=contact['id'],
                phone=contact['phone'],
                content=personalized,
                idempotency_key=idempotency_key
            ))
        
        logger.info(f"Prepared {len(messages)} messages for campaign {campaign_id}")
        
        return messages
    
    def _filter_contacts(self, contacts: List[Dict], segment: Segment) -> List[Dict]:
        """Apply segment filters to contacts"""
        filtered = contacts
        
        if segment.segment_type == SegmentType.OPTED_IN:
            filtered = [c for c in filtered if c.get('opted_in')]
        elif segment.segment_type == SegmentType.TAG:
            required_tags = segment.criteria.get('tags', [])
            filtered = []
            for c in contacts:
                contact_tags = json.loads(c.get('tags', '[]'))
                if any(tag in contact_tags for tag in required_tags):
                    filtered.append(c)
        elif segment.segment_type == SegmentType.DATE_RANGE:
            start_date = segment.criteria.get('start_date')
            end_date = segment.criteria.get('end_date')
            filtered = []
            for c in contacts:
                created = c.get('created_at', '')
                if start_date and created < start_date:
                    continue
                if end_date and created > end_date:
                    continue
                filtered.append(c)
        
        return filtered
    
    def _personalize_message(self, content: str, contact: Dict) -> str:
        """Replace {{variables}} with contact data"""
        import re
        pattern = r'\{\{(\w+)\}\}'
        
        def replacer(match):
            field = match.group(1)
            value = contact.get(field, match.group(0))
            return str(value) if value else match.group(0)
        
        return re.sub(pattern, replacer, content)
    
    def _generate_idempotency_key(self, campaign_id: int, contact_id: int) -> str:
        """Generate unique idempotency key"""
        raw = f"{campaign_id}-{contact_id}-{secrets.token_hex(8)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]
    
    def execute_campaign(self, campaign_id: int, batch_size: int = 50,
                        delay_between_batches: float = 1.0) -> CampaignStats:
        """
        Execute broadcast campaign
        
        Args:
            campaign_id: Campaign to execute
            batch_size: Messages per batch
            delay_between_batches: Delay between batches
        
        Returns:
            Campaign statistics
        """
        # Get campaign details
        campaign = self.db.get_campaign(campaign_id)
        if not campaign:
            return CampaignStats()
        
        org_id = campaign['organization_id']
        content = campaign.get('content', '')
        segment = Segment(
            id=str(campaign_id),
            name=campaign.get('name', ''),
            segment_type=SegmentType.ALL,
            criteria=json.loads(campaign.get('segment_criteria', '{}'))
        )
        
        # Prepare messages
        messages = self.prepare_messages(campaign_id, org_id, content, segment)
        
        stats = CampaignStats(total=len(messages))
        self.active_campaigns[campaign_id] = {"stats": stats, "running": True}
        
        # Update campaign status
        self.db.update_campaign_status(campaign_id, CampaignStatus.RUNNING.value)
        
        # Process in batches
        for i in range(0, len(messages), batch_size):
            if not self.active_campaigns.get(campaign_id, {}).get("running"):
                logger.info(f"Campaign {campaign_id} paused")
                break
            
            batch = messages[i:i + batch_size]
            
            for msg in batch:
                # Acquire rate limit token
                while not self.rate_limiter.acquire():
                    time.sleep(self.rate_limiter.wait_time())
                
                # Send message
                result = self._send_campaign_message(campaign_id, msg)
                
                if result["success"]:
                    stats.sent += 1
                else:
                    stats.failed += 1
                    stats.error = result.get("error")
            
            # Update progress
            stats.pending = len(messages) - stats.sent - stats.failed
            self._update_campaign_stats(campaign_id, stats)
            
            if self.on_progress:
                self.on_progress(campaign_id, stats)
            
            # Delay between batches
            if delay_between_batches > 0:
                time.sleep(delay_between_batches)
        
        # Mark complete
        stats.pending = 0
        self._complete_campaign(campaign_id, stats)
        
        return stats
    
    def _send_campaign_message(self, campaign_id: int, msg: MessageItem) -> Dict:
        """Send single campaign message"""
        try:
            # Create message record
            message_id = self.db.create_message(
                org_id=0,  # Will be set from campaign
                direction="outbound",
                content=msg.content,
                to_phone=msg.phone,
                idempotency_key=msg.idempotency_key
            )
            
            # Send via WhatsApp API
            if self.whatsapp_api:
                result = self.whatsapp_api.send_text_message(
                    to=msg.phone,
                    message=msg.content
                )
                
                if result and result.get("messages"):
                    msg_id = result["messages"][0]["id"]
                    self.db.update_message_idempotency_key(msg.idempotency_key, msg_id)
                    return {"success": True, "message_id": msg_id}
            
            return {"success": True}
        
        except Exception as e:
            logger.error(f"Failed to send campaign message: {e}")
            return {"success": False, "error": str(e)}
    
    def _update_campaign_stats(self, campaign_id: int, stats: CampaignStats):
        """Update campaign statistics in database"""
        self.db.update_campaign_stats(campaign_id, stats.to_dict())
    
    def _complete_campaign(self, campaign_id: int, stats: CampaignStats):
        """Mark campaign as completed"""
        self.db.update_campaign_status(campaign_id, CampaignStatus.COMPLETED.value)
        self.db.complete_campaign(campaign_id)
        
        self.active_campaigns[campaign_id] = {"stats": stats, "running": False}
        
        if self.on_complete:
            self.on_complete(campaign_id, stats)
        
        logger.info(f"Campaign {campaign_id} completed: {stats.sent} sent, {stats.delivered} delivered")
    
    def pause_campaign(self, campaign_id: int):
        """Pause running campaign"""
        if campaign_id in self.active_campaigns:
            self.active_campaigns[campaign_id]["running"] = False
            self.db.update_campaign_status(campaign_id, CampaignStatus.PAUSED.value)
            logger.info(f"Campaign {campaign_id} paused")
    
    def get_campaign_stats(self, campaign_id: int) -> Optional[CampaignStats]:
        """Get current campaign statistics"""
        if campaign_id in self.active_campaigns:
            return self.active_campaigns[campaign_id]["stats"]
        return None


class ABTestingEngine:
    """
    A/B Testing for campaigns
    
    Test different message variations and optimize based on results
    """
    
    def __init__(self, broadcasting_engine: BroadcastingEngine):
        self.engine = broadcasting_engine
        self.variants: Dict[str, Dict] = {}
    
    def create_ab_test(self, org_id: int, base_content: str,
                       variants: List[Dict], segment: Segment,
                       test_percentage: float = 10) -> Dict:
        """
        Create A/B test campaign
        
        Args:
            base_content: Control message
            variants: [{id, content, description}]
            segment: Target segment
            test_percentage: % of contacts for testing
        
        Returns:
            Test configuration with variant IDs
        """
        test_id = secrets.token_urlsafe(8)
        
        self.variants[test_id] = {
            "control": {
                "id": "control",
                "content": base_content,
                "stats": CampaignStats()
            },
            "variants": [
                {**v, "stats": CampaignStats()}
                for v in variants
            ],
            "test_percentage": test_percentage,
            "segment": segment,
            "status": "running"
        }
        
        return {"test_id": test_id, "variants": len(variants) + 1}
    
    def assign_variant(self, test_id: str, contact_id: int) -> str:
        """Assign contact to test variant"""
        import random
        test = self.variants.get(test_id)
        
        if not test:
            return "control"
        
        percentage = test["test_percentage"]
        random_value = random.random() * 100
        
        if random_value < percentage:
            # Assign to variant testing
            variant_index = random.randint(0, len(test["variants"]) - 1)
            return f"variant_{variant_index}"
        else:
            return "control"
    
    def track_variant_result(self, test_id: str, variant_id: str, 
                           message_id: str, status: str):
        """Track result for variant"""
        test = self.variants.get(test_id)
        
        if not test:
            return
        
        if variant_id == "control":
            variant = test["control"]
        elif variant_id.startswith("variant_"):
            idx = int(variant_id.replace("variant_", ""))
            variant = test["variants"][idx]
        else:
            return
        
        stats = variant["stats"]
        
        if status == "sent":
            stats.sent += 1
        elif status == "delivered":
            stats.delivered += 1
        elif status == "read":
            stats.read += 1
        elif status == "replied":
            stats.replied += 1
        elif status == "failed":
            stats.failed += 1
    
    def get_ab_test_results(self, test_id: str) -> Dict:
        """Get A/B test results"""
        test = self.variants.get(test_id)
        
        if not test:
            return {}
        
        results = {
            "test_id": test_id,
            "status": test["status"],
            "control": {
                **test["control"],
                "stats": test["control"]["stats"].to_dict()
            },
            "variants": [
                {**v, "stats": v["stats"].to_dict()}
                for v in test["variants"]
            ],
            "recommendation": self._calculate_recommendation(test)
        }
        
        return results
    
    def _calculate_recommendation(self, test: Dict) -> str:
        """Calculate best performing variant"""
        control_rate = test["control"]["stats"].response_rate
        
        best_variant = None
        best_rate = control_rate
        
        for v in test["variants"]:
            rate = v["stats"].response_rate
            if rate > best_rate:
                best_rate = rate
                best_variant = v.get("id")
        
        if best_variant:
            return f"Variant '{best_variant}' performs {round((best_rate - control_rate) / max(control_rate, 1) * 100, 1)}% better than control"
        
        return "More data needed for recommendation"


# =====================================
# CAMPAIGN SCHEDULER
# =====================================

class CampaignScheduler:
    """
    Schedule campaigns for future execution
    """
    
    def __init__(self, broadcasting_engine: BroadcastingEngine):
        self.engine = broadcasting_engine
        self.scheduled: Dict[int, Dict] = {}
        self._running = False
        self._thread = None
    
    def schedule(self, campaign_id: int, scheduled_at: datetime):
        """Schedule campaign for execution"""
        self.scheduled[campaign_id] = {
            "scheduled_at": scheduled_at,
            "status": "scheduled"
        }
        
        logger.info(f"Campaign {campaign_id} scheduled for {scheduled_at}")
    
    def cancel(self, campaign_id: int):
        """Cancel scheduled campaign"""
        if campaign_id in self.scheduled:
            del self.scheduled[campaign_id]
            logger.info(f"Campaign {campaign_id} cancelled")
    
    def start(self):
        """Start scheduler background thread"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop scheduler"""
        self._running = False
        if self._thread:
            self._thread.join()
    
    def _run_scheduler(self):
        """Run scheduler loop"""
        while self._running:
            now = datetime.now()
            
            for campaign_id, schedule in list(self.scheduled.items()):
                if now >= schedule["scheduled_at"]:
                    # Execute campaign
                    self.engine.execute_campaign(campaign_id)
                    del self.scheduled[campaign_id]
            
            time.sleep(10)  # Check every 10 seconds
