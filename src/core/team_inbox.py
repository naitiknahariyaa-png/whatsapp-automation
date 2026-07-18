"""
====================================================================
TEAM INBOX - Multi-Agent Conversation Management
====================================================================
Features:
- Assign conversations to agents
- Agent status management
- Load balancing
- Priority queuing
- Real-time updates

This is how Aisensy handles team conversations
====================================================================
"""

import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    AWAY = "away"


class AgentRole(Enum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    AGENT = "agent"


class ConversationStatus(Enum):
    UNASSIGNED = "unassigned"
    OPEN = "open"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AssignmentStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCE = "load_balance"
    PRIORITY = "priority"
    SKILLS = "skills"


@dataclass
class Agent:
    """Team agent"""
    id: int
    organization_id: int
    name: str
    email: str
    role: AgentRole
    status: AgentStatus
    max_conversations: int = 50
    skills: List[str] = field(default_factory=list)
    current_conversations: int = 0
    last_activity: datetime = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Agent':
        return cls(
            id=data.get("id"),
            organization_id=data.get("organization_id"),
            name=data.get("name"),
            email=data.get("email"),
            role=AgentRole(data.get("role", "agent")),
            status=AgentStatus(data.get("status", "offline")),
            max_conversations=data.get("max_conversations", 50),
            skills=data.get("skills", []),
            current_conversations=data.get("current_conversations", 0),
            last_activity=data.get("last_activity")
        )
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "status": self.status.value,
            "max_conversations": self.max_conversations,
            "skills": self.skills,
            "current_conversations": self.current_conversations,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
    
    @property
    def is_available(self) -> bool:
        """Check if agent can take new conversations"""
        return (
            self.status == AgentStatus.ONLINE and 
            self.current_conversations < self.max_conversations
        )


@dataclass
class Conversation:
    """Support conversation"""
    id: int
    organization_id: int
    contact_id: int
    contact_phone: str
    contact_name: str
    status: ConversationStatus
    priority: int = 5  # 1 = highest, 5 = lowest
    assigned_agent_id: int = None
    tags: List[str] = field(default_factory=list)
    unread_count: int = 0
    last_message_at: datetime = None
    first_response_at: datetime = None
    resolved_at: datetime = None
    source: str = "whatsapp"
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Conversation':
        return cls(
            id=data.get("id"),
            organization_id=data.get("organization_id"),
            contact_id=data.get("contact_id"),
            contact_phone=data.get("contact_phone"),
            contact_name=data.get("contact_name", ""),
            status=ConversationStatus(data.get("status", "open")),
            priority=data.get("priority", 5),
            assigned_agent_id=data.get("assigned_agent_id"),
            tags=json.loads(data.get("tags', '[]')),
            unread_count=data.get("unread_count", 0),
            last_message_at=data.get("last_message_at"),
            first_response_at=data.get("first_response_at"),
            resolved_at=data.get("resolved_at"),
            source=data.get("source", "whatsapp"),
            created_at=data.get("created_at", datetime.now())
        )
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "contact_id": self.contact_id,
            "contact_phone": self.contact_phone,
            "contact_name": self.contact_name,
            "status": self.status.value,
            "priority": self.priority,
            "assigned_agent_id": self.assigned_agent_id,
            "tags": self.tags,
            "unread_count": self.unread_count,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "first_response_at": self.first_response_at.isoformat() if self.first_response_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class Message:
    """Chat message"""
    id: int
    conversation_id: int
    sender_type: str  # 'contact', 'agent', 'system'
    sender_id: int = None
    sender_name: str = None
    content: str
    message_type: str = "text"
    is_internal: bool = False  # Internal notes (not visible to customer)
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        return cls(
            id=data.get("id"),
            conversation_id=data.get("conversation_id"),
            sender_type=data.get("sender_type"),
            sender_id=data.get("sender_id"),
            sender_name=data.get("sender_name"),
            content=data.get("content"),
            message_type=data.get("message_type", "text"),
            is_internal=data.get("is_internal", False),
            created_at=data.get("created_at", datetime.now())
        )


class TeamInbox:
    """
    Team inbox for managing WhatsApp conversations
    
    Features:
    - Multi-agent support
    - Auto-assignment with strategies
    - Priority queuing
    - Real-time updates
    - Canned responses
    """
    
    def __init__(self, db, whatsapp_api=None):
        self.db = db
        self.whatsapp_api = whatsapp_api
        
        # In-memory agent cache
        self.agents: Dict[int, Agent] = {}
        self.conversations: Dict[int, Conversation] = {}
        
        # Assignment tracking
        self._round_robin_index: Dict[int, int] = defaultdict(int)
        self._last_assignment: Dict[int, datetime] = {}
        
        # Callbacks
        self.on_new_conversation: Optional[Callable] = None
        self.on_conversation_assigned: Optional[Callable] = None
        self.on_conversation_updated: Optional[Callable] = None
        
        logger.info("Team inbox initialized")
    
    # =====================================
    # AGENT MANAGEMENT
    # =====================================
    
    def create_agent(self, org_id: int, name: str, email: str,
                     role: AgentRole = AgentRole.AGENT,
                     max_conversations: int = 50,
                     skills: List[str] = None) -> Agent:
        """Create new team agent"""
        agent_id = self.db.create_agent(
            org_id=org_id,
            name=name,
            email=email,
            role=role.value,
            max_conversations=max_conversations
        )
        
        agent = Agent(
            id=agent_id,
            organization_id=org_id,
            name=name,
            email=email,
            role=role,
            status=AgentStatus.OFFLINE,
            max_conversations=max_conversations,
            skills=skills or []
        )
        
        self.agents[agent_id] = agent
        
        logger.info(f"Created agent: {name} ({email})")
        
        return agent
    
    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Get agent by ID"""
        if agent_id in self.agents:
            return self.agents[agent_id]
        
        # Load from database
        agent_data = self.db.get_agent(agent_id)
        if agent_data:
            agent = Agent.from_dict(agent_data)
            self.agents[agent_id] = agent
            return agent
        
        return None
    
    def get_agents(self, org_id: int, status: AgentStatus = None) -> List[Agent]:
        """Get all agents for organization"""
        agents_data = self.db.get_agents(org_id, status.value if status else None)
        
        agents = []
        for data in agents_data:
            agent = Agent.from_dict(data)
            self.agents[agent.id] = agent
            agents.append(agent)
        
        return agents
    
    def update_agent_status(self, agent_id: int, status: AgentStatus) -> bool:
        """Update agent availability status"""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        agent.status = status
        agent.last_activity = datetime.now()
        
        self.db.update_agent_status(agent_id, status.value)
        
        logger.info(f"Agent {agent.name} status: {status.value}")
        
        return True
    
    def get_available_agents(self, org_id: int) -> List[Agent]:
        """Get available agents who can take conversations"""
        agents = self.get_agents(org_id, AgentStatus.ONLINE)
        return [a for a in agents if a.is_available]
    
    # =====================================
    # CONVERSATION MANAGEMENT
    # =====================================
    
    def create_conversation(self, org_id: int, contact_id: int,
                           contact_phone: str, contact_name: str = None,
                           source: str = "whatsapp",
                           auto_assign: bool = True) -> Conversation:
        """Create new conversation from incoming message"""
        conversation_id = self.db.create_conversation(
            org_id=org_id,
            contact_id=contact_id,
            contact_phone=contact_phone,
            contact_name=contact_name,
            source=source
        )
        
        conversation = Conversation(
            id=conversation_id,
            organization_id=org_id,
            contact_id=contact_id,
            contact_phone=contact_phone,
            contact_name=contact_name or "",
            status=ConversationStatus.UNASSIGNED,
            source=source
        )
        
        self.conversations[conversation_id] = conversation
        
        # Auto-assign if enabled
        if auto_assign:
            self.assign_conversation(conversation_id)
        
        if self.on_new_conversation:
            self.on_new_conversation(conversation)
        
        logger.info(f"New conversation {conversation_id} from {contact_phone}")
        
        return conversation
    
    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID"""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]
        
        # Load from database
        data = self.db.get_conversation(conversation_id)
        if data:
            conversation = Conversation.from_dict(data)
            self.conversations[conversation_id] = conversation
            return conversation
        
        return None
    
    def get_conversations(self, org_id: int, status: ConversationStatus = None,
                         agent_id: int = None,
                         limit: int = 100) -> List[Conversation]:
        """Get conversations with filters"""
        data_list = self.db.get_conversations(
            org_id=org_id,
            status=status.value if status else None,
            agent_id=agent_id,
            limit=limit
        )
        
        conversations = []
        for data in data_list:
            conv = Conversation.from_dict(data)
            self.conversations[conv.id] = conv
            conversations.append(conv)
        
        return conversations
    
    def assign_conversation(self, conversation_id: int,
                           agent_id: int = None,
                           strategy: AssignmentStrategy = AssignmentStrategy.LOAD_BALANCE) -> bool:
        """Assign conversation to agent"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        # Auto-assign if no agent specified
        if not agent_id:
            agent_id = self._select_agent(conversation, strategy)
        
        if not agent_id:
            logger.warning(f"No available agent for conversation {conversation_id}")
            return False
        
        agent = self.get_agent(agent_id)
        if not agent or not agent.is_available:
            return False
        
        # Update conversation
        conversation.assigned_agent_id = agent_id
        conversation.status = ConversationStatus.OPEN
        conversation.unread_count = 0
        
        # Update agent load
        agent.current_conversations += 1
        agent.last_activity = datetime.now()
        
        # Save to database
        self.db.assign_conversation(conversation_id, agent_id)
        self.db.update_agent_conversation_count(agent_id, agent.current_conversations)
        
        if self.on_conversation_assigned:
            self.on_conversation_assigned(conversation, agent)
        
        logger.info(f"Conversation {conversation_id} assigned to {agent.name}")
        
        return True
    
    def _select_agent(self, conversation: Conversation,
                     strategy: AssignmentStrategy) -> Optional[int]:
        """Select best agent based on strategy"""
        available = self.get_available_agents(conversation.organization_id)
        
        if not available:
            return None
        
        if strategy == AssignmentStrategy.ROUND_ROBIN:
            # Round-robin assignment
            org_id = conversation.organization_id
            start_idx = self._round_robin_index[org_id]
            
            for i in range(len(available)):
                idx = (start_idx + i) % len(available)
                self._round_robin_index[org_id] = (idx + 1) % len(available)
                return available[idx].id
        
        elif strategy == AssignmentStrategy.LOAD_BALANCE:
            # Assign to agent with least conversations
            return min(available, key=lambda a: a.current_conversations).id
        
        elif strategy == AssignmentStrategy.PRIORITY:
            # First check for high priority
            if conversation.priority <= 2:
                # High priority - assign to supervisor
                supervisors = [a for a in available if a.role == AgentRole.SUPERVISOR]
                if supervisors:
                    return supervisors[0].id
            
            # Normal priority - load balance
            return min(available, key=lambda a: a.current_conversations).id
        
        return available[0].id if available else None
    
    def escalate_conversation(self, conversation_id: int, priority: int = 1) -> bool:
        """Escalate conversation priority"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation.priority = priority
        self.db.update_conversation_priority(conversation_id, priority)
        
        # Re-assign to higher priority
        if conversation.assigned_agent_id:
            # Reassign based on new priority
            self.assign_conversation(conversation_id, strategy=AssignmentStrategy.PRIORITY)
        
        logger.info(f"Conversation {conversation_id} escalated to priority {priority}")
        
        return True
    
    def resolve_conversation(self, conversation_id: int) -> bool:
        """Mark conversation as resolved"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation.status = ConversationStatus.RESOLVED
        conversation.resolved_at = datetime.now()
        
        # Free up agent
        if conversation.assigned_agent_id:
            agent = self.get_agent(conversation.assigned_agent_id)
            if agent and agent.current_conversations > 0:
                agent.current_conversations -= 1
                self.db.update_agent_conversation_count(
                    conversation.assigned_agent_id, 
                    agent.current_conversations
                )
        
        self.db.resolve_conversation(conversation_id)
        
        logger.info(f"Conversation {conversation_id} resolved")
        
        return True
    
    def close_conversation(self, conversation_id: int) -> bool:
        """Close conversation permanently"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation.status = ConversationStatus.CLOSED
        
        self.db.close_conversation(conversation_id)
        
        return True
    
    # =====================================
    # MESSAGES
    # =====================================
    
    def add_message(self, conversation_id: int, sender_type: str,
                   content: str, sender_id: int = None,
                   sender_name: str = None,
                   is_internal: bool = False) -> Message:
        """Add message to conversation"""
        message_id = self.db.add_conversation_message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            sender_id=sender_id,
            sender_name=sender_name,
            content=content,
            is_internal=is_internal
        )
        
        message = Message(
            id=message_id,
            conversation_id=conversation_id,
            sender_type=sender_type,
            sender_id=sender_id,
            sender_name=sender_name,
            content=content,
            is_internal=is_internal
        )
        
        # Update conversation
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.last_message_at = datetime.now()
            
            if sender_type == "contact":
                conversation.unread_count += 1
                
                # Mark first response time
                if not conversation.first_response_at:
                    conversation.first_response_at = datetime.now()
            
            self.db.update_conversation_activity(conversation_id)
        
        logger.debug(f"Message added to conversation {conversation_id}")
        
        return message
    
    def get_messages(self, conversation_id: int, limit: int = 50) -> List[Message]:
        """Get conversation messages"""
        data_list = self.db.get_conversation_messages(conversation_id, limit)
        
        return [Message.from_dict(data) for data in data_list]
    
    def mark_as_read(self, conversation_id: int, agent_id: int) -> bool:
        """Mark conversation as read by agent"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        if conversation.assigned_agent_id != agent_id:
            return False
        
        conversation.unread_count = 0
        self.db.mark_conversation_read(conversation_id)
        
        return True
    
    # =====================================
    # INTERNAL NOTES
    # =====================================
    
    def add_note(self, conversation_id: int, agent_id: int,
                agent_name: str, content: str) -> Message:
        """Add internal note (not visible to customer)"""
        return self.add_message(
            conversation_id=conversation_id,
            sender_type="agent",
            sender_id=agent_id,
            sender_name=agent_name,
            content=content,
            is_internal=True
        )
    
    # =====================================
    # TAGS
    # =====================================
    
    def add_tag(self, conversation_id: int, tag: str) -> bool:
        """Add tag to conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        if tag not in conversation.tags:
            conversation.tags.append(tag)
            self.db.update_conversation_tags(conversation_id, conversation.tags)
        
        return True
    
    def remove_tag(self, conversation_id: int, tag: str) -> bool:
        """Remove tag from conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        if tag in conversation.tags:
            conversation.tags.remove(tag)
            self.db.update_conversation_tags(conversation_id, conversation.tags)
        
        return True
    
    # =====================================
    # STATISTICS
    # =====================================
    
    def get_inbox_stats(self, org_id: int) -> Dict:
        """Get inbox statistics"""
        conversations = self.get_conversations(org_id, limit=10000)
        
        stats = {
            "total": len(conversations),
            "unassigned": len([c for c in conversations if c.status == ConversationStatus.UNASSIGNED]),
            "open": len([c for c in conversations if c.status == ConversationStatus.OPEN]),
            "pending": len([c for c in conversations if c.status == ConversationStatus.PENDING]),
            "resolved": len([c for c in conversations if c.status == ConversationStatus.RESOLVED]),
            "high_priority": len([c for c in conversations if c.priority <= 2]),
            "with_unread": len([c for c in conversations if c.unread_count > 0])
        }
        
        # Agent stats
        agents = self.get_agents(org_id)
        agent_stats = []
        
        for agent in agents:
            agent_convs = [c for c in conversations if c.assigned_agent_id == agent.id]
            agent_stats.append({
                "id": agent.id,
                "name": agent.name,
                "status": agent.status.value,
                "conversations": len(agent_convs),
                "unread": sum(c.unread_count for c in agent_convs)
            })
        
        stats["agents"] = agent_stats
        
        return stats
    
    def get_response_time_stats(self, org_id: int, days: int = 7) -> Dict:
        """Get response time statistics"""
        conversations = self.get_conversations(org_id, status=ConversationStatus.RESOLVED, limit=1000)
        
        response_times = []
        
        for conv in conversations:
            if conv.first_response_at and conv.created_at:
                response_time = (conv.first_response_at - conv.created_at).total_seconds()
                response_times.append(response_time)
        
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            return {
                "avg_response_time_seconds": round(avg_response, 1),
                "avg_response_time_minutes": round(avg_response / 60, 1),
                "total_resolved": len(response_times)
            }
        
        return {"avg_response_time_seconds": 0, "total_resolved": 0}


# =====================================
# CANNED RESPONSES
# =====================================

class CannedResponses:
    """Canned response templates for quick replies"""
    
    def __init__(self, db):
        self.db = db
    
    def create(self, org_id: int, shortcut: str, content: str,
              category: str = "general") -> int:
        """Create canned response"""
        return self.db.create_canned_response(
            org_id=org_id,
            shortcut=shortcut,
            content=content,
            category=category
        )
    
    def search(self, org_id: int, query: str) -> List[Dict]:
        """Search canned responses"""
        return self.db.search_canned_responses(org_id, query)
    
    def get_by_shortcut(self, org_id: int, shortcut: str) -> Optional[str]:
        """Get content by shortcut"""
        responses = self.db.get_canned_responses(org_id)
        
        for resp in responses:
            if resp.get("shortcut") == shortcut:
                return resp.get("content")
        
        return None
