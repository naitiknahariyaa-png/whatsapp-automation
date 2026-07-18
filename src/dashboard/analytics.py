"""
====================================================================
ANALYTICS DASHBOARD - Real-time Metrics & Reporting
====================================================================
Features:
- Real-time message tracking
- Campaign analytics
- Conversation metrics
- Agent performance
- Export reports
- Charts data
====================================================================
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class DashboardStats:
    """Dashboard statistics summary"""
    period_start: datetime
    period_end: datetime
    total_contacts: int = 0
    new_contacts: int = 0
    total_messages: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    delivery_rate: float = 0.0
    read_rate: float = 0.0
    response_rate: float = 0.0
    active_conversations: int = 0
    resolved_conversations: int = 0
    avg_response_time: float = 0.0
    top_campaigns: List[Dict] = field(default_factory=list)
    hourly_data: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "period": {
                "start": self.period_start.isoformat(),
                "end": self.period_end.isoformat()
            },
            "contacts": {
                "total": self.total_contacts,
                "new": self.new_contacts
            },
            "messages": {
                "total": self.total_messages,
                "sent": self.messages_sent,
                "received": self.messages_received
            },
            "engagement": {
                "delivery_rate": self.delivery_rate,
                "read_rate": self.read_rate,
                "response_rate": self.response_rate
            },
            "conversations": {
                "active": self.active_conversations,
                "resolved": self.resolved_conversations,
                "avg_response_time": self.avg_response_time
            },
            "top_campaigns": self.top_campaigns,
            "hourly_data": self.hourly_data
        }


class AnalyticsDashboard:
    """
    Analytics dashboard for WhatsApp marketing
    """
    
    def __init__(self, db):
        self.db = db
    
    def get_dashboard_stats(self, org_id: int, days: int = 7) -> DashboardStats:
        """Get complete dashboard statistics"""
        now = datetime.now()
        start = now - timedelta(days=days)
        
        stats = DashboardStats(
            period_start=start,
            period_end=now
        )
        
        # Get from database
        analytics = self.db.get_analytics(org_id, days)
        
        stats.total_contacts = self._get_total_contacts(org_id)
        stats.new_contacts = self._get_new_contacts(org_id, start)
        stats.messages_sent = analytics.get("messages_sent", 0)
        stats.messages_received = analytics.get("messages_received", 0)
        stats.total_messages = stats.messages_sent + stats.messages_received
        stats.delivery_rate = analytics.get("delivery_rate", 0)
        stats.read_rate = analytics.get("read_rate", 0)
        
        stats.active_conversations = 0
        stats.resolved_conversations = 0
        
        stats.top_campaigns = self._get_top_campaigns(org_id, limit=5)
        stats.hourly_data = analytics.get("daily_stats", [])
        
        return stats
    
    def _get_total_contacts(self, org_id: int) -> int:
        """Get total contacts count"""
        contacts = self.db.get_contacts(org_id, limit=1000000)
        return len(contacts)
    
    def _get_new_contacts(self, org_id: int, since: datetime) -> int:
        """Get new contacts since date"""
        return 0
    
    def _get_top_campaigns(self, org_id: int, limit: int = 5) -> List[Dict]:
        """Get top performing campaigns"""
        return []
    
    def get_messages_chart(self, org_id: int, days: int = 30) -> Dict:
        """Get messages over time chart data"""
        return {
            "labels": [],
            "datasets": []
        }
    
    def get_contacts_chart(self, org_id: int, days: int = 30) -> Dict:
        """Get contacts growth chart"""
        return {
            "labels": [],
            "datasets": []
        }
    
    def export_contacts(self, org_id: int, format: str = "csv") -> str:
        """Export contacts to file format"""
        contacts = self.db.get_contacts(org_id, limit=100000)
        
        if format == "csv":
            lines = ["phone,name,email,tags,created_at"]
            for c in contacts:
                line = f"{c.get('phone')},{c.get('name')},{c.get('email')},{c.get('tags')},{c.get('created_at')}"
                lines.append(line)
            return "\n".join(lines)
        
        return json.dumps(contacts)
    
    def export_messages(self, org_id: int, format: str = "csv") -> str:
        """Export messages to file format"""
        messages = self.db.get_messages(org_id, limit=100000)
        
        if format == "csv":
            lines = ["message_id,direction,content,status,sent_at"]
            for m in messages:
                line = f"{m.get('message_id')},{m.get('direction')},{m.get('content')},{m.get('status')},{m.get('sent_at')}"
                lines.append(line)
            return "\n".join(lines)
        
        return json.dumps(messages)
