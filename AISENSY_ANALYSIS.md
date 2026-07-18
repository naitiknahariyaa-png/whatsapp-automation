# Aisensy Platform Analysis & Implementation Guide

This document provides a deep analysis of [Aisensy](https://www.app.aisensy.com/) and explains how to build similar features for your WhatsApp automation platform.

---

## 📊 Aisensy Platform Overview

**Aisensy** is a no-code WhatsApp marketing and engagement platform that helps businesses:
- Deploy AI chatbots for 24/7 customer support
- Run broadcast campaigns with segmentation
- Capture leads through multiple channels
- Automate conversations with visual flow builder
- Process payments within WhatsApp
- Manage team inbox with multiple agents

### Key Statistics
- Trusted by **210,000+ businesses** across 68+ countries
- Handles **200M+ API requests daily**
- Official WhatsApp Business Solution Provider (BSP)
- Used by major brands: PhysicsWallah, Vivo, Bajaj Finance, Tata, Wipro

---

## 🎯 Core Features to Build

### 1. **AI Agents (Smart Chatbots)**

**What Aisensy Does:**
- AI agents with natural language processing (NLP)
- Context-aware, multi-turn conversations
- 24/7 availability
- Human handoff when needed
- Lead qualification and product recommendations

**How to Implement:**

```python
# src/ai/agent.py - AI Agent Framework
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List
import json

class AgentState(Enum):
    IDLE = "idle"
    WAITING_INPUT = "waiting_input"
    QUALIFYING = "qualifying"
    RECOMMENDING = "recommending"
    ESCALATING = "escalating"
    COMPLETED = "completed"

@dataclass
class ConversationContext:
    user_id: str
    state: AgentState
    intent: Optional[str] = None
    entities: Dict = None
    history: List[Dict] = None
    metadata: Dict = None

class WhatsAppAIAgent:
    """
    AI Agent for WhatsApp conversations
    - Understands user intent using NLP
    - Maintains conversation context
    - Escalates to humans when needed
    """
    
    def __init__(self, nlp_model=None, escalation_handler=None):
        self.nlp = nlp_model or self._load_nlp_model()
        self.contexts: Dict[str, ConversationContext] = {}
        self.escalation_handler = escalation_handler
        self.intent_handlers = self._register_intent_handlers()
    
    def process_message(self, user_id: str, message: str) -> Dict:
        """Process incoming message and generate response"""
        context = self._get_or_create_context(user_id)
        
        # Step 1: Intent Detection
        intent = self.nlp.detect_intent(message, context)
        context.intent = intent
        
        # Step 2: Extract Entities
        entities = self.nlp.extract_entities(message, intent)
        context.entities.update(entities)
        
        # Step 3: Generate Response
        handler = self.intent_handlers.get(intent, self._fallback_handler)
        response = handler(context, message)
        
        # Step 4: Update Context
        context.history.append({
            "role": "user",
            "message": message,
            "intent": intent
        })
        context.history.append({
            "role": "agent",
            "message": response["message"]
        })
        
        return response
    
    def _handle_lead_qualification(self, context, message) -> Dict:
        """Qualify leads based on conversation"""
        qualification_score = self._calculate_qualification(context)
        
        if qualification_score >= 0.8:
            return {
                "message": "You're a great fit! Let me connect you with our sales team.",
                "action": "escalate",
                "state": AgentState.COMPLETED
            }
        elif qualification_score >= 0.5:
            return {
                "message": "I need a bit more info. What's your budget range?",
                "action": "continue",
                "state": AgentState.QUALIFYING
            }
        else:
            return {
                "message": "Thanks for your interest! Here's some general info.",
                "action": "continue",
                "state": AgentState.IDLE
            }
    
    def _calculate_qualification(self, context) -> float:
        """Calculate lead qualification score (0-1)"""
        score = 0.0
        required_fields = ["name", "email", "phone", "interest"]
        for field in required_fields:
            if context.entities.get(field):
                score += 0.25
        return min(score, 1.0)
```

**Tech Stack for AI Agents:**
- OpenAI GPT-4 / Claude for NLP
- LangChain for conversation management
- Weights & Biases for training (optional)

---

### 2. **Visual Flow Builder (Drag & Drop)**

**What Aisensy Does:**
- No-code flow builder
- Pre-built templates
- Conditional logic and branching
- Multi-channel triggers
- API/webhook integrations

**How to Implement:**

```python
# src/core/flow_builder.py - Visual Flow Builder Core

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
import json

class NodeType(Enum):
    TRIGGER = "trigger"
    MESSAGE = "message"
    CONDITION = "condition"
    ACTION = "action"
    API_CALL = "api_call"
    DELAY = "delay"
    RANDOMIZER = "randomizer"
    SPEAK_TO_HUMAN = "speak_to_human"
    END = "end"

@dataclass
class FlowNode:
    id: str
    type: NodeType
    config: Dict = field(default_factory=dict)
    position: Dict = field(default_factory=lambda: {"x": 0, "y": 0})
    connections: List[str] = field(default_factory=list)

@dataclass 
class FlowCondition:
    field: str
    operator: str  # equals, contains, greater_than, etc.
    value: any
    next_node_id: str

class FlowBuilder:
    """
    Visual Flow Builder - Core Engine
    Supports: Triggers, Messages, Conditions, Actions, API calls
    """
    
    def __init__(self):
        self.nodes: Dict[str, FlowNode] = {}
        self.flows: Dict[str, Dict] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
    
    def create_flow(self, flow_id: str, name: str) -> Dict:
        """Create a new flow"""
        flow = {
            "id": flow_id,
            "name": name,
            "nodes": {},
            "connections": [],
            "trigger_types": ["keyword", "schedule", "event", "click"]
        }
        self.flows[flow_id] = flow
        return flow
    
    def add_node(self, flow_id: str, node: FlowNode) -> None:
        """Add a node to the flow"""
        self.flows[flow_id]["nodes"][node.id] = node
        self.nodes[node.id] = node
    
    def connect_nodes(self, flow_id: str, from_node: str, to_node: str) -> None:
        """Connect two nodes"""
        self.flows[flow_id]["connections"].append({
            "from": from_node,
            "to": to_node
        })
    
    def evaluate_condition(self, condition: FlowCondition, context: Dict) -> bool:
        """Evaluate a condition against context"""
        value = context.get(condition.field)
        
        if condition.operator == "equals":
            return value == condition.value
        elif condition.operator == "contains":
            return condition.value in str(value)
        elif condition.operator == "greater_than":
            return float(value) > float(condition.value)
        elif condition.operator == "exists":
            return value is not None
        
        return False
    
    def execute_flow(self, flow_id: str, trigger_data: Dict) -> List[Dict]:
        """Execute a flow and return actions to perform"""
        flow = self.flows.get(flow_id)
        if not flow:
            return []
        
        actions = []
        current_node_id = self._find_start_node(flow)
        context = self._build_context(trigger_data)
        
        while current_node_id:
            node = flow["nodes"].get(current_node_id)
            if not node:
                break
            
            result = self._execute_node(node, context)
            if result:
                actions.extend(result.get("actions", []))
            
            # Determine next node
            current_node_id = self._get_next_node(node, context, flow)
        
        return actions
    
    def _execute_node(self, node: FlowNode, context: Dict) -> Optional[Dict]:
        """Execute a single node"""
        if node.type == NodeType.MESSAGE:
            return {"actions": [{"type": "send_message", "content": node.config.get("content")}]}
        
        elif node.type == NodeType.CONDITION:
            conditions = node.config.get("conditions", [])
            for cond in conditions:
                if self.evaluate_condition(FlowCondition(**cond), context):
                    return {"next_node_id": cond["next_node_id"]}
            return {"next_node_id": node.config.get("default_next")}
        
        elif node.type == NodeType.API_CALL:
            return self._execute_api_call(node, context)
        
        elif node.type == NodeType.SPEAK_TO_HUMAN:
            return {"actions": [{"type": "escalate", "agent_id": "human"}]}
        
        return None
    
    def export_flow_json(self, flow_id: str) -> str:
        """Export flow as JSON (for frontend visualization)"""
        flow = self.flows.get(flow_id, {})
        return json.dumps(flow, indent=2)
    
    def import_flow_json(self, flow_json: str) -> str:
        """Import flow from JSON"""
        data = json.loads(flow_json)
        flow_id = data["id"]
        self.flows[flow_id] = data
        return flow_id


# Pre-built Flow Templates
FLOW_TEMPLATES = {
    "lead_qualification": {
        "name": "Lead Qualification",
        "nodes": [
            {"id": "start", "type": "trigger", "config": {"trigger": "keyword", "value": "hi"}},
            {"id": "greet", "type": "message", "config": {"content": "Hi! I'm here to help. What's your name?"}},
            {"id": "ask_email", "type": "condition", "config": {"conditions": []}},
            {"id": "qualify", "type": "action", "config": {"action": "score_lead"}},
            {"id": "end", "type": "end"}
        ]
    },
    "order_tracking": {
        "name": "Order Tracking",
        "nodes": [
            {"id": "start", "type": "trigger", "config": {"trigger": "keyword", "value": "track"}},
            {"id": "ask_order", "type": "message", "config": {"content": "Please enter your order ID"}},
            {"id": "fetch_order", "type": "api_call", "config": {"endpoint": "/api/orders/{order_id}"}},
            {"id": "send_status", "type": "message", "config": {"content": "Your order is {{status}}"}}
        ]
    },
    "appointment_booking": {
        "name": "Appointment Booking",
        "nodes": [
            {"id": "start", "type": "trigger", "config": {"trigger": "keyword", "value": "book"}},
            {"id": "show_slots", "type": "api_call", "config": {"endpoint": "/api/slots"}},
            {"id": "select_slot", "type": "message", "config": {"content": "Available slots: {{slots}}"}},
            {"id": "confirm", "type": "action", "config": {"action": "book_appointment"}},
            {"id": "send_confirmation", "type": "message", "config": {"content": "Booked! See you on {{date}}"}}
        ]
    }
}
```

---

### 3. **Broadcasting & Campaigns**

**What Aisensy Does:**
- Segment contacts by tags, behavior, attributes
- Schedule broadcasts
- A/B test messages
- Personalization with tokens
- Real-time analytics

**How to Implement:**

```python
# src/core/broadcast.py - Broadcasting Engine

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio

class CampaignStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"

class SegmentType(Enum):
    ALL = "all"
    TAG = "tag"
    BEHAVIOR = "behavior"
    ATTRIBUTE = "attribute"
    CUSTOM = "custom"

@dataclass
class Segment:
    id: str
    name: str
    segment_type: SegmentType
    criteria: Dict  # Filter criteria
    count: int = 0  # Number of contacts in segment

@dataclass
class Campaign:
    id: str
    name: str
    template_id: str
    segment: Segment
    scheduled_at: Optional[datetime]
    status: CampaignStatus
    stats: Dict = None  # delivery, opens, clicks, responses

@dataclass
class BroadcastStats:
    total_recipients: int
    delivered: int
    read: int
    replied: int
    failed: int
    
    @property
    def delivery_rate(self) -> float:
        return (self.delivered / self.total_recipients * 100) if self.total_recipients else 0
    
    @property
    def engagement_rate(self) -> float:
        return (self.replied / self.delivered * 100) if self.delivered else 0

class BroadcastingEngine:
    """
    Handles broadcast campaigns with segmentation and scheduling
    """
    
    def __init__(self, whatsapp_client, database):
        self.whatsapp = whatsapp_client
        self.db = database
        self.campaigns: Dict[str, Campaign] = {}
        self.rate_limiter = RateLimiter()
    
    def create_segment(self, segment_data: Dict) -> Segment:
        """Create a contact segment based on criteria"""
        segment = Segment(
            id=self._generate_id(),
            name=segment_data["name"],
            segment_type=SegmentType(segment_data["type"]),
            criteria=segment_data["criteria"]
        )
        segment.count = self._count_segment_contacts(segment)
        return segment
    
    def _count_segment_contacts(self, segment: Segment) -> int:
        """Count contacts matching segment criteria"""
        if segment.segment_type == SegmentType.ALL:
            return self.db.count_contacts()
        
        elif segment.segment_type == SegmentType.TAG:
            return self.db.count_contacts_by_tag(segment.criteria["tag"])
        
        elif segment.segment_type == SegmentType.BEHAVIOR:
            return self.db.count_contacts_by_behavior(
                segment.criteria["action"],
                segment.criteria.get("days", 7)
            )
        
        elif segment.segment_type == SegmentType.ATTRIBUTE:
            return self.db.count_contacts_by_attribute(
                segment.criteria["field"],
                segment.criteria["value"]
            )
        
        return 0
    
    def create_campaign(self, campaign_data: Dict) -> Campaign:
        """Create a new broadcast campaign"""
        segment = self.create_segment(campaign_data["segment"])
        
        campaign = Campaign(
            id=self._generate_id(),
            name=campaign_data["name"],
            template_id=campaign_data["template_id"],
            segment=segment,
            scheduled_at=campaign_data.get("scheduled_at"),
            status=CampaignStatus.DRAFT,
            stats={
                "total": segment.count,
                "delivered": 0,
                "read": 0,
                "replied": 0,
                "failed": 0
            }
        )
        
        self.campaigns[campaign.id] = campaign
        return campaign
    
    def schedule_campaign(self, campaign_id: str, scheduled_at: datetime) -> None:
        """Schedule a campaign for future execution"""
        campaign = self.campaigns.get(campaign_id)
        if campaign:
            campaign.scheduled_at = scheduled_at
            campaign.status = CampaignStatus.SCHEDULED
            self._schedule_task(campaign_id, scheduled_at)
    
    async def execute_campaign(self, campaign_id: str) -> BroadcastStats:
        """Execute a broadcast campaign"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        campaign.status = CampaignStatus.RUNNING
        
        # Get template content
        template = self.db.get_template(campaign.template_id)
        
        # Get segment contacts
        contacts = self._get_segment_contacts(campaign.segment)
        
        # Execute in batches (respecting rate limits)
        stats = BroadcastStats(
            total_recipients=len(contacts),
            delivered=0,
            read=0,
            replied=0,
            failed=0
        )
        
        batch_size = 50
        for i in range(0, len(contacts), batch_size):
            batch = contacts[i:i + batch_size]
            
            for contact in batch:
                try:
                    # Personalize message
                    content = self._personalize_template(
                        template["content"], 
                        contact
                    )
                    
                    # Send message
                    result = await self.whatsapp.send_message(
                        contact["phone"],
                        content
                    )
                    
                    if result["success"]:
                        stats.delivered += 1
                    else:
                        stats.failed += 1
                    
                    # Rate limiting
                    await self.rate_limiter.wait()
                    
                except Exception as e:
                    stats.failed += 1
                    self.db.log_error(campaign_id, contact["phone"], str(e))
            
            # Update campaign stats
            campaign.stats = {
                "delivered": stats.delivered,
                "read": stats.read,
                "replied": stats.replied,
                "failed": stats.failed
            }
        
        campaign.status = CampaignStatus.COMPLETED
        return stats
    
    def _personalize_template(self, template: str, contact: Dict) -> str:
        """Replace tokens with contact data"""
        tokens = {
            "{{first_name}}": contact.get("first_name", ""),
            "{{last_name}}": contact.get("last_name", ""),
            "{{name}}": contact.get("name", ""),
            "{{phone}}": contact.get("phone", ""),
            "{{email}}": contact.get("email", ""),
        }
        
        content = template
        for token, value in tokens.items():
            content = content.replace(token, value)
        
        return content
    
    def _get_segment_contacts(self, segment: Segment) -> List[Dict]:
        """Get all contacts matching segment criteria"""
        if segment.segment_type == SegmentType.ALL:
            return self.db.get_all_contacts()
        elif segment.segment_type == SegmentType.TAG:
            return self.db.get_contacts_by_tag(segment.criteria["tag"])
        elif segment.segment_type == SegmentType.BEHAVIOR:
            return self.db.get_contacts_by_behavior(
                segment.criteria["action"],
                segment.criteria.get("days", 7)
            )
        elif segment.segment_type == SegmentType.ATTRIBUTE:
            return self.db.get_contacts_by_attribute(
                segment.criteria["field"],
                segment.criteria["value"]
            )
        return []


class RateLimiter:
    """
    WhatsApp rate limiting to prevent blocks
    Meta WABA limits: ~60 messages/minute sustained
    """
    
    def __init__(self):
        self.messages_sent = 0
        self.window_start = datetime.now()
        self.max_per_minute = 50  # Conservative limit
        self.max_per_day = 10000
    
    async def wait(self) -> None:
        """Wait if rate limit would be exceeded"""
        now = datetime.now()
        
        # Reset window every minute
        if (now - self.window_start).total_seconds() >= 60:
            self.messages_sent = 0
            self.window_start = now
        
        if self.messages_sent >= self.max_per_minute:
            wait_time = 60 - (now - self.window_start).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.messages_sent += 1
```

---

### 4. **Lead Capture & Forms**

**What Aisensy Does:**
- Click-to-WhatsApp links
- QR codes
- Native WhatsApp Forms
- Chat widgets for websites
- Lead qualification flows

**How to Implement:**

```python
# src/core/lead_capture.py - Lead Capture System

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import secrets

@dataclass
class ClickToWhatsAppLink:
    phone_number_id: str
    phone: str
    prefilled_message: str
    short_url: str
    qr_code_url: str
    analytics: Dict = None

@dataclass
class WhatsAppForm:
    id: str
    title: str
    fields: List[Dict]  # [{name, type, required, options}]
    success_message: str
    webhook_url: Optional[str]
    responses: List[Dict] = None

class LeadCapture:
    """
    Lead capture through multiple channels
    """
    
    def __init__(self, database):
        self.db = database
    
    def generate_cta_link(self, phone: str, message: str = "Hi!") -> ClickToWhatsAppLink:
        """Generate Click-to-WhatsApp link and QR code"""
        # Format phone number (remove + and spaces)
        clean_phone = phone.replace("+", "").replace(" ", "")
        
        # Generate unique short URL
        short_code = secrets.token_urlsafe(6)
        
        # Create WhatsApp deep link
        wa_link = f"https://wa.me/{clean_phone}?text={self._url_encode(message)}"
        
        # Generate QR code
        qr_url = self._generate_qr_code(wa_link)
        
        return ClickToWhatsAppLink(
            phone_number_id=clean_phone,
            phone=phone,
            prefilled_message=message,
            short_url=f"https://wa.me/{clean_phone}",
            qr_code_url=qr_url
        )
    
    def create_whatsapp_form(self, form_data: Dict) -> WhatsAppForm:
        """Create native WhatsApp form"""
        form = WhatsAppForm(
            id=self._generate_id(),
            title=form_data["title"],
            fields=form_data["fields"],
            success_message=form_data.get("success_message", "Thank you!"),
            webhook_url=form_data.get("webhook_url")
        )
        
        # Save form
        self.db.save_form(form)
        
        # Generate form URL for sharing
        form.url = f"https://app.yourplatform.com/forms/{form.id}"
        
        return form
    
    def process_form_response(self, form_id: str, responses: Dict) -> Dict:
        """Process form submission and create lead"""
        form = self.db.get_form(form_id)
        if not form:
            raise ValueError("Form not found")
        
        # Validate required fields
        for field in form.fields:
            if field.get("required") and not responses.get(field["name"]):
                return {"success": False, "error": f"{field['name']} is required"}
        
        # Create lead
        lead = {
            "id": self._generate_id(),
            "form_id": form_id,
            "responses": responses,
            "created_at": datetime.now().isoformat(),
            "tags": ["form_capture"]
        }
        
        # Add to database
        self.db.save_lead(lead)
        
        # Trigger webhook if configured
        if form.webhook_url:
            self._send_webhook(form.webhook_url, lead)
        
        return {"success": True, "lead_id": lead["id"]}
    
    def generate_website_widget(self, config: Dict) -> str:
        """Generate chat widget code for websites"""
        return f'''
        <!-- WhatsApp Chat Widget -->
        <script>
          window.waConfig = {{
            phone: "{config['phone']}",
            position: "{config.get('position', 'right')}",
            prefill: "{config.get('prefill_message', 'Hi!')}",
            theme: "{config.get('theme', 'green')}"
          }};
        </script>
        <script src="https://cdn.yourplatform.com/widget.js"></script>
        '''
```

---

### 5. **Team Inbox & Multi-Agent**

**What Aisensy Does:**
- Shared inbox for teams
- Assign conversations to agents
- Role-based access
- Online/offline status
- Chat history

**How to Implement:**

```python
# src/core/team_inbox.py - Team Collaboration

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class AgentStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"

class ConversationStatus(Enum):
    UNASSIGNED = "unassigned"
    OPEN = "open"
    PENDING = "pending"
    RESOLVED = "resolved"

@dataclass
class Agent:
    id: str
    name: str
    email: str
    role: str  # admin, agent, supervisor
    status: AgentStatus
    assigned_conversations: int = 0
    max_conversations: int = 50

@dataclass
class Conversation:
    id: str
    customer_id: str
    customer_name: str
    customer_phone: str
    status: ConversationStatus
    assigned_agent_id: Optional[str]
    priority: int = 0  # 1 = highest
    tags: List[str] = None
    messages: List[Dict] = None
    created_at: datetime = None
    updated_at: datetime = None

class TeamInbox:
    """
    Team inbox for managing WhatsApp conversations
    """
    
    def __init__(self, database):
        self.db = database
        self.agents: Dict[str, Agent] = {}
        self.conversations: Dict[str, Conversation] = {}
        self.assignment_strategy = "round_robin"  # or "load_balance"
    
    def add_agent(self, agent_data: Dict) -> Agent:
        """Add a new agent to the team"""
        agent = Agent(
            id=agent_data["id"],
            name=agent_data["name"],
            email=agent_data["email"],
            role=agent_data.get("role", "agent"),
            status=AgentStatus.OFFLINE
        )
        self.agents[agent.id] = agent
        return agent
    
    def set_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update agent availability status"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
    
    def create_conversation(self, customer_data: Dict) -> Conversation:
        """Create new conversation from incoming message"""
        conversation = Conversation(
            id=self._generate_id(),
            customer_id=customer_data["customer_id"],
            customer_name=customer_data["customer_name"],
            customer_phone=customer_data["customer_phone"],
            status=ConversationStatus.UNASSIGNED,
            assigned_agent_id=None,
            priority=customer_data.get("priority", 5),
            tags=customer_data.get("tags", []),
            messages=[],
            created_at=datetime.now()
        )
        
        self.conversations[conversation.id] = conversation
        self.db.save_conversation(conversation)
        
        return conversation
    
    def assign_conversation(self, conversation_id: str, agent_id: str = None) -> bool:
        """Assign conversation to an agent"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return False
        
        if not agent_id:
            # Auto-assign based on strategy
            agent_id = self._auto_assign()
        
        if agent_id in self.agents:
            conversation.assigned_agent_id = agent_id
            conversation.status = ConversationStatus.OPEN
            conversation.updated_at = datetime.now()
            
            # Update agent's load
            self.agents[agent_id].assigned_conversations += 1
            
            self.db.update_conversation(conversation)
            return True
        
        return False
    
    def _auto_assign(self) -> Optional[str]:
        """Auto-assign based on strategy"""
        available_agents = [
            a for a in self.agents.values()
            if a.status == AgentStatus.ONLINE 
            and a.assigned_conversations < a.max_conversations
        ]
        
        if not available_agents:
            return None
        
        if self.assignment_strategy == "round_robin":
            return available_agents[0].id
        elif self.assignment_strategy == "load_balance":
            return min(available_agents, key=lambda a: a.assigned_conversations).id
        
        return None
    
    def escalate_to_human(self, conversation_id: str, context: Dict) -> bool:
        """Escalate AI conversation to human agent"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return False
        
        # Add priority for human handling
        conversation.priority = 1
        
        # Find available agent
        assigned = self.assign_conversation(conversation_id)
        
        if assigned:
            # Send notification to agent
            agent = self.agents.get(conversation.assigned_agent_id)
            self._notify_agent(agent, conversation, context)
        
        return assigned
    
    def get_agent_dashboard(self, agent_id: str) -> Dict:
        """Get dashboard data for an agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {}
        
        # Get assigned conversations
        my_convs = [
            c for c in self.conversations.values()
            if c.assigned_agent_id == agent_id
        ]
        
        return {
            "agent": {
                "name": agent.name,
                "status": agent.status.value,
                "active_conversations": len(my_convs)
            },
            "conversations": [
                {
                    "id": c.id,
                    "customer": c.customer_name,
                    "status": c.status.value,
                    "priority": c.priority,
                    "last_message": c.messages[-1] if c.messages else None
                }
                for c in my_convs
            ],
            "stats": self._calculate_agent_stats(agent_id)
        }
```

---

### 6. **Integrations (Shopify, CRM, etc.)**

**What Aisensy Does:**
- Native Shopify integration (abandoned cart, order status)
- Razorpay payment notifications
- HubSpot/Salesforce CRM sync
- Webhooks for custom integrations
- Zapier/Integrately for 25,000+ apps

**How to Implement:**

```python
# src/integrations/shopify.py - Shopify Integration

from dataclasses import dataclass
from typing import Dict, List, Optional
import shopify
from datetime import datetime

@dataclass
class AbandonedCart:
    order_id: str
    customer_id: str
    customer_phone: str
    items: List[Dict]
    total: float
    checkout_url: str
    abandoned_at: datetime

class ShopifyIntegration:
    """
    Shopify integration for e-commerce automation
    """
    
    def __init__(self, shop_url: str, access_token: str):
        self.shop_url = shop_url
        shopify.ShopifyResource.set_site(f"https://{shop_url}")
        shopify.ShopifyResource.set_headers({
            "X-Shopify-Access-Token": access_token
        })
    
    def get_abandoned_carts(self, hours: int = 1) -> List[AbandonedCart]:
        """Get recently abandoned carts"""
        since = datetime.now() - timedelta(hours=hours)
        
        checkouts = shopify.Checkout.find(
            created_at_min=since.isoformat(),
            limit=250
        )
        
        carts = []
        for checkout in checkouts:
            if checkout.abandoned_checkout_url:
                carts.append(AbandonedCart(
                    order_id=checkout.id,
                    customer_id=checkout.customer.id,
                    customer_phone=checkout.phone or "",
                    items=[{"title": item.title, "quantity": item.quantity} 
                           for item in checkout.line_items],
                    total=float(checkout.subtotal_price or 0),
                    checkout_url=checkout.abandoned_checkout_url,
                    abandoned_at=checkout.created_at
                ))
        
        return carts
    
    def send_cart_recovery(self, cart: AbandonedCart, wa_client) -> bool:
        """Send abandoned cart recovery message"""
        items_text = ", ".join([f"{i['title']}" for i in cart.items[:3]])
        
        message = f"""
🛒 Hi! You left some items in your cart:
• {items_text}
💰 Total: ₹{cart.total}

Complete your purchase: {cart.checkout_url}

Reply STOP to unsubscribe
        """.strip()
        
        return wa_client.send_message(cart.customer_phone, message)
    
    def sync_orders(self, order_id: str, wa_client) -> Dict:
        """Sync order status and notify customer"""
        order = shopify.Order.find(order_id)
        
        status_messages = {
            "pending": "📦 Your order #{id} is being processed!",
            "confirmed": "✅ Order #{id} confirmed! We're preparing it.",
            "shipped": "🚚 Your order #{id} has been shipped!",
            "delivered": "🎉 Your order #{id} has been delivered!",
        }
        
        message = status_messages.get(
            order.financial_status,
            f"📦 Order #{order.id} update: {order.financial_status}"
        )
        
        wa_client.send_message(order.phone, message)
        
        return {"success": True, "order_id": order_id}
```

---

## 🏗️ Architecture Recommendations

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │Dashboard │  │Flow      │  │Campaign  │  │Lead      │          │
│  │          │  │Builder   │  │Builder   │  │Manager   │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
└───────┼─────────────┼─────────────┼─────────────┼────────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │ REST API / GraphQL
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND SERVICES                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │Message   │  │AI Agent  │  │Campaign  │  │Integration│          │
│  │Processor │  │Engine    │  │Engine    │  │Engine    │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       │            │             │             │                  │
│       └────────────┴─────────────┴─────────────┘                  │
│                         │ Message Queue (Redis/RabbitMQ)          │
└─────────────────────────┼────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     WHATSAPP LAYER                               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              WhatsApp Business API (WABA)                    │ │
│  │              - Webhooks for incoming messages               │ │
│  │              - Template message sending                      │ │
│  │              - Media handling                                │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │PostgreSQL│  │Redis     │  │S3/Blob   │  │Elastic   │          │
│  │(Primary) │  │(Cache/Q) │  │(Media)   │  │Search    │          │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Database Schema (PostgreSQL)

```sql
-- Contacts/Customers
CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    phone VARCHAR(20) UNIQUE,
    name VARCHAR(255),
    email VARCHAR(255),
    tags TEXT[],
    attributes JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    contact_id UUID REFERENCES contacts(id),
    status VARCHAR(50),
    assigned_agent_id UUID,
    priority INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    direction VARCHAR(10), -- 'inbound' or 'outbound'
    content TEXT,
    media_url VARCHAR(500),
    status VARCHAR(50),
    sent_at TIMESTAMP DEFAULT NOW()
);

-- Flows
CREATE TABLE flows (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    definition JSONB, -- Flow nodes and connections
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Campaigns
CREATE TABLE campaigns (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    flow_id UUID REFERENCES flows(id),
    segment_criteria JSONB,
    scheduled_at TIMESTAMP,
    status VARCHAR(50),
    stats JSONB
);

-- Templates (for broadcasting)
CREATE TABLE templates (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(100),
    content TEXT,
    variables TEXT[],
    approved BOOLEAN DEFAULT FALSE,
    meta_template_id VARCHAR(255)
);
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up WhatsApp Business API integration
- [ ] Build basic message sending/receiving
- [ ] Create contact database
- [ ] Implement simple keyword-based auto-replies

### Phase 2: AI Capabilities (Week 3-4)
- [ ] Integrate OpenAI/Claude for NLP
- [ ] Build conversation context management
- [ ] Implement intent detection
- [ ] Add human handoff logic

### Phase 3: Flow Builder (Week 5-6)
- [ ] Design flow builder UI
- [ ] Build flow execution engine
- [ ] Add conditions and branching
- [ ] Create pre-built templates

### Phase 4: Broadcasting (Week 7-8)
- [ ] Build contact segmentation
- [ ] Create campaign management
- [ ] Implement scheduling
- [ ] Add analytics dashboard

### Phase 5: Integrations (Week 9-10)
- [ ] Shopify integration
- [ ] CRM webhooks
- [ ] Payment gateway notifications
- [ ] Zapier/Integrately support

### Phase 6: Team Features (Week 11-12)
- [ ] Team inbox
- [ ] Agent management
- [ ] Assignment logic
- [ ] Reporting dashboard

---

## 📚 Tech Stack Recommendations

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React + TypeScript | Dashboard, Flow Builder |
| **Backend** | Node.js / Python FastAPI | API, Business Logic |
| **Database** | PostgreSQL | Primary data |
| **Cache/Queue** | Redis | Caching, Message queue |
| **AI** | OpenAI GPT-4 / Claude | NLP, Intent detection |
| **WhatsApp** | Official WABA API | Messaging |
| **File Storage** | S3 / Blob Storage | Media files |
| **Hosting** | AWS / GCP / Vercel | Cloud infrastructure |

---

## 🔑 Key Takeaways

1. **Start Simple**: Begin with basic auto-replies and keyword triggers before adding AI
2. **Use Official API**: WhatsApp Business API (not WhatsApp Web) for reliability and scale
3. **Rate Limiting**: Always respect WhatsApp's message limits to avoid blocks
4. **Template Approval**: Plan for Meta's template approval process in your workflow
5. **Human Handoff**: Always have a path for conversations to reach humans
6. **Data Privacy**: Comply with local regulations (GDPR, DPDP) for customer data
7. **Analytics**: Track everything - delivery rates, engagement, conversion funnels

---

## 📖 Additional Resources

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Aisensy Platform](https://www.app.aisensy.com/)
- [Meta Business Partner Directory](https://www.facebook.com/business/partners/search)

---

*This document was created by analyzing Aisensy's public features and website. Some implementation details are based on common patterns in WhatsApp marketing platforms.*
