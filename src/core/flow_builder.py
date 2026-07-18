"""
====================================================================
FLOW BUILDER ENGINE - Visual Automation System
====================================================================
Features:
- Node-based flow execution
- Conditional branching
- AI integration
- API calls
- Delay actions
- Human handoff

This is how Aisensy builds chatbots without code
====================================================================
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Flow node types"""
    TRIGGER = "trigger"
    MESSAGE = "message"
    QUICK_REPLY = "quick_reply"
    BUTTONS = "buttons"
    LIST = "list"
    CONDITION = "condition"
    IF_ELSE = "if_else"
    AI_RESPONSE = "ai_response"
    KEYWORD_MATCH = "keyword_match"
    API_CALL = "api_call"
    SET_VARIABLE = "set_variable"
    DELAY = "delay"
    RANDOM = "random"
    GO_TO = "go_to"
    SPEAK_TO_HUMAN = "speak_to_human"
    SEND_CAMPAIGN = "send_campaign"
    ADD_TAG = "add_tag"
    REMOVE_TAG = "remove_tag"
    WEBHOOK = "webhook"
    END = "end"


class ConditionOperator(Enum):
    """Condition operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    REGEX = "regex"


@dataclass
class NodePosition:
    """Node position in visual editor"""
    x: float
    y: float


@dataclass
class FlowNode:
    """Represents a single node in the flow"""
    id: str
    type: NodeType
    label: str
    config: Dict[str, Any] = field(default_factory=dict)
    position: NodePosition = None
    next_nodes: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FlowNode':
        """Create node from dictionary"""
        return cls(
            id=data.get("id"),
            type=NodeType(data.get("type", "message")),
            label=data.get("label", ""),
            config=data.get("config", {}),
            position=NodePosition(**data.get("position", {"x": 0, "y": 0})) if data.get("position") else None,
            next_nodes=data.get("next_nodes", [])
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "label": self.label,
            "config": self.config,
            "position": {"x": self.position.x, "y": self.position.y} if self.position else None,
            "next_nodes": self.next_nodes
        }


@dataclass
class Flow:
    """Complete flow definition"""
    id: int
    name: str
    trigger_type: str
    trigger_value: str
    nodes: Dict[str, FlowNode]
    connections: List[Dict]
    is_active: bool
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Flow':
        """Create flow from dictionary"""
        nodes = {}
        for node_data in data.get("nodes", []):
            node = FlowNode.from_dict(node_data)
            nodes[node.id] = node
        
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            trigger_type=data.get("trigger_type", "keyword"),
            trigger_value=data.get("trigger_value", ""),
            nodes=nodes,
            connections=data.get("connections", []),
            is_active=data.get("is_active", False)
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "trigger_type": self.trigger_type,
            "trigger_value": self.trigger_value,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "connections": self.connections,
            "is_active": self.is_active
        }


@dataclass
class FlowContext:
    """Execution context for a flow"""
    flow_id: int
    contact_id: int
    contact_phone: str
    organization_id: int
    current_node_id: str
    variables: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    def set_variable(self, name: str, value: Any):
        """Set context variable"""
        self.variables[name] = value
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get context variable"""
        return self.variables.get(name, default)
    
    def add_history(self, node_id: str, action: str, data: Any = None):
        """Add to execution history"""
        self.history.append({
            "node_id": node_id,
            "action": action,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })


class NodeExecutor(ABC):
    """Base class for node executors"""
    
    @abstractmethod
    def execute(self, node: FlowNode, context: FlowContext, 
                executor: 'FlowExecutor) -> Optional[str]:
        """
        Execute node and return next node ID
        
        Returns:
            Next node ID to execute, or None to end flow
        """
        pass


class MessageExecutor(NodeExecutor):
    """Execute message nodes"""
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Send message to contact"""
        content = node.config.get("content", "")
        
        # Replace variables in content
        content = self._replace_variables(content, context)
        
        # Send message
        success = executor.send_message(context.contact_phone, content)
        
        context.add_history(node.id, "message_sent", {"content": content, "success": success})
        
        # Return first next node
        return node.next_nodes[0] if node.next_nodes else None
    
    def _replace_variables(self, text: str, context: FlowContext) -> str:
        """Replace {{variable}} patterns with values"""
        import re
        pattern = r'\{\{(\w+)\}\}'
        
        def replacer(match):
            var_name = match.group(1)
            return str(context.get_variable(var_name, match.group(0)))
        
        return re.sub(pattern, replacer, text)


class QuickReplyExecutor(NodeExecutor):
    """Execute quick reply nodes"""
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Send quick reply buttons"""
        content = node.config.get("content", "")
        buttons = node.config.get("buttons", [])
        
        content = self._replace_variables(content, context)
        
        # Format buttons for WhatsApp
        formatted_buttons = [{"id": btn.get("id"), "title": btn.get("title")} for btn in buttons]
        
        success = executor.send_quick_reply(
            context.contact_phone, 
            content, 
            formatted_buttons
        )
        
        context.add_history(node.id, "quick_reply_sent", {"buttons": len(buttons)})
        
        # Store expected responses
        context.set_variable("_expected_responses", [btn["id"] for btn in buttons])
        
        return None  # Wait for user response


class ButtonExecutor(NodeExecutor):
    """Execute button message nodes"""
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Send button message"""
        content = node.config.get("content", "")
        buttons = node.config.get("buttons", [])
        
        formatted_buttons = [{"id": btn.get("id"), "title": btn.get("title")} for btn in buttons]
        
        success = executor.send_buttons(
            context.contact_phone,
            content,
            formatted_buttons
        )
        
        context.add_history(node.id, "buttons_sent", {"count": len(buttons)})
        
        return node.next_nodes[0] if node.next_nodes else None


class ListExecutor(NodeExecutor):
    """Execute list message nodes"""
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Send list message"""
        content = node.config.get("content", "")
        header = node.config.get("header", "")
        rows = node.config.get("rows", [])
        
        formatted_rows = [
            {"id": row.get("id"), "title": row.get("title"), "description": row.get("description")}
            for row in rows
        ]
        
        success = executor.send_list(
            context.contact_phone,
            header,
            content,
            formatted_rows
        )
        
        context.add_history(node.id, "list_sent", {"rows": len(rows)})
        
        return node.next_nodes[0] if node.next_nodes else None


class AIResponseExecutor(NodeExecutor):
    """Execute AI response nodes"""
    
    def __init__(self, ai_provider=None):
        self.ai_provider = ai_provider
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Generate AI response"""
        prompt = node.config.get("prompt", "")
        system_prompt = node.config.get("system_prompt", "")
        
        # Build context for AI
        conversation_history = "\n".join([
            f"{'User' if h['action'] == 'message_received' else 'Bot'}: {h.get('data', {}).get('content', '')}"
            for h in context.history[-10:]
        ])
        
        # Replace variables in prompt
        prompt = self._replace_variables(prompt, context)
        system_prompt = self._replace_variables(system_prompt, context)
        
        # Generate response
        if self.ai_provider:
            response = self.ai_provider.generate(
                message=prompt,
                context=conversation_history
            )
        else:
            response = "I'm sorry, I'm not able to respond right now."
        
        # Send response
        executor.send_message(context.contact_phone, response)
        
        context.add_history(node.id, "ai_response", {"response_length": len(response)})
        
        return node.next_nodes[0] if node.next_nodes else None
    
    def _replace_variables(self, text: str, context: FlowContext) -> str:
        """Replace variables in text"""
        import re
        pattern = r'\{\{(\w+)\}\}'
        
        def replacer(match):
            var_name = match.group(1)
            return str(context.get_variable(var_name, match.group(0)))
        
        return re.sub(pattern, replacer, text)


class ConditionExecutor(NodeExecutor):
    """Execute condition nodes"""
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Evaluate condition and return next node"""
        conditions = node.config.get("conditions", [])
        default_next = node.config.get("default_next")
        
        for condition in conditions:
            if self._evaluate_condition(condition, context):
                context.add_history(node.id, "condition_matched", {"condition": condition})
                return condition.get("next_node")
        
        # No condition matched, use default
        context.add_history(node.id, "condition_default")
        return default_next
    
    def _evaluate_condition(self, condition: Dict, context: FlowContext) -> bool:
        """Evaluate single condition"""
        field = condition.get("field", "")
        operator = condition.get("operator", "equals")
        value = condition.get("value", "")
        
        # Get field value (from variables or metadata)
        if field.startswith("contact."):
            field = field.replace("contact.", "")
            field_value = context.metadata.get(field)
        elif field.startswith("variable."):
            field = field.replace("variable.", "")
            field_value = context.get_variable(field)
        else:
            field_value = context.get_variable(field)
        
        # Evaluate based on operator
        if operator == "equals":
            return str(field_value).lower() == str(value).lower()
        elif operator == "not_equals":
            return str(field_value).lower() != str(value).lower()
        elif operator == "contains":
            return str(value).lower() in str(field_value).lower()
        elif operator == "not_contains":
            return str(value).lower() not in str(field_value).lower()
        elif operator == "starts_with":
            return str(field_value).lower().startswith(str(value).lower())
        elif operator == "ends_with":
            return str(field_value).lower().endswith(str(value).lower())
        elif operator == "exists":
            return field_value is not None and field_value != ""
        elif operator == "not_exists":
            return field_value is None or field_value == ""
        elif operator == "greater_than":
            try:
                return float(field_value) > float(value)
            except:
                return False
        elif operator == "less_than":
            try:
                return float(field_value) < float(value)
            except:
                return False
        elif operator == "regex":
            import re
            return bool(re.match(value, str(field_value)))
        
        return False


class DelayExecutor(NodeExecutor):
    """Execute delay nodes"""
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Schedule next node after delay"""
        delay_type = node.config.get("type", "seconds")
        delay_value = node.config.get("value", 1)
        
        if delay_type == "seconds":
            seconds = delay_value
        elif delay_type == "minutes":
            seconds = delay_value * 60
        elif delay_type == "hours":
            seconds = delay_value * 3600
        elif delay_type == "days":
            seconds = delay_value * 86400
        else:
            seconds = delay_value
        
        # Schedule delayed execution
        executor.schedule_delayed_execution(
            context.flow_id,
            context.contact_id,
            node.next_nodes[0] if node.next_nodes else None,
            seconds
        )
        
        context.add_history(node.id, "delay_scheduled", {"seconds": seconds})
        
        return None  # Don't continue immediately


class APIcallExecutor(NodeExecutor):
    """Execute API call nodes"""
    
    def __init__(self, http_client=None):
        self.http_client = http_client
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Make API call and store response"""
        url = node.config.get("url", "")
        method = node.config.get("method", "GET").upper()
        headers = node.config.get("headers", {})
        body = node.config.get("body", {})
        save_to = node.config.get("save_to")
        
        # Replace variables in URL and body
        url = self._replace_variables(url, context)
        body = json.loads(self._replace_variables(json.dumps(body), context))
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=body)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=body)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=body)
            else:
                response = None
            
            if response and response.status_code < 300:
                result = response.json() if response.content else {}
                
                if save_to:
                    context.set_variable(save_to, result)
                
                context.add_history(node.id, "api_success", {"status": response.status_code})
            else:
                context.add_history(node.id, "api_error", {"status": response.status_code if response else None})
        
        except Exception as e:
            context.add_history(node.id, "api_error", {"error": str(e)})
        
        return node.next_nodes[0] if node.next_nodes else None
    
    def _replace_variables(self, text: str, context: FlowContext) -> str:
        """Replace variables in text"""
        import re
        pattern = r'\{\{(\w+)\}\}'
        
        def replacer(match):
            var_name = match.group(1)
            return str(context.get_variable(var_name, match.group(0)))
        
        return re.sub(pattern, replacer, text)


class HumanHandoffExecutor(NodeExecutor):
    """Execute human handoff nodes"""
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Transfer to human agent"""
        priority = node.config.get("priority", 5)
        message = node.config.get("message", "Transferring you to a human agent...")
        
        # Send transfer message
        executor.send_message(context.contact_phone, message)
        
        # Create conversation assignment
        executor.escalate_to_human(context, priority)
        
        context.add_history(node.id, "human_handoff", {"priority": priority})
        
        return None  # End flow, human takes over


class SpeakToHumanExecutor(NodeExecutor):
    """Execute speak to human nodes (same as handoff)"""
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Transfer to human agent"""
        message = node.config.get("message", "I'll connect you with our team.")
        
        executor.send_message(context.contact_phone, message)
        executor.escalate_to_human(context, priority=1)  # High priority
        
        context.add_history(node.id, "speak_to_human")
        
        return None


class SetVariableExecutor(NodeExecutor):
    """Execute set variable nodes"""
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Set context variable"""
        variable = node.config.get("variable")
        value = node.config.get("value")
        operation = node.config.get("operation", "set")
        
        if operation == "set":
            context.set_variable(variable, value)
        elif operation == "increment":
            current = context.get_variable(variable, 0)
            context.set_variable(variable, int(current) + int(value))
        elif operation == "decrement":
            current = context.get_variable(variable, 0)
            context.set_variable(variable, int(current) - int(value))
        
        context.add_history(node.id, "variable_set", {"variable": variable, "value": value})
        
        return node.next_nodes[0] if node.next_nodes else None


class AddTagExecutor(NodeExecutor):
    """Execute add tag nodes"""
    
    def execute(self, node: FlowNode, context: FlowContext,
               executor: 'FlowExecutor') -> Optional[str]:
        """Add tag to contact"""
        tag = node.config.get("tag")
        
        executor.add_contact_tag(context.contact_id, tag)
        
        context.add_history(node.id, "tag_added", {"tag": tag})
        
        return node.next_nodes[0] if node.next_nodes else None


class FlowExecutor:
    """
    Main flow execution engine
    Coordinates all node executors and manages flow state
    """
    
    def __init__(self, db, whatsapp_api=None, ai_provider=None):
        self.db = db
        self.whatsapp_api = whatsapp_api
        self.ai_provider = ai_provider
        
        # Initialize node executors
        self.executors = {
            NodeType.MESSAGE: MessageExecutor(),
            NodeType.QUICK_REPLY: QuickReplyExecutor(),
            NodeType.BUTTONS: ButtonExecutor(),
            NodeType.LIST: ListExecutor(),
            NodeType.AI_RESPONSE: AIResponseExecutor(ai_provider),
            NodeType.CONDITION: ConditionExecutor(),
            NodeType.DELAY: DelayExecutor(),
            NodeType.API_CALL: APIcallExecutor(),
            NodeType.SPEAK_TO_HUMAN: SpeakToHumanExecutor(),
            NodeType.SET_VARIABLE: SetVariableExecutor(),
            NodeType.ADD_TAG: AddTagExecutor(),
        }
        
        # Delayed executions queue
        self._delayed_queue = {}
    
    def execute_flow(self, flow: Flow, context: FlowContext) -> List[Dict]:
        """
        Execute a complete flow
        
        Returns:
            List of actions taken during execution
        """
        if not flow.is_active or not flow.nodes:
            return []
        
        actions = []
        current_node_id = self._get_start_node(flow)
        
        while current_node_id:
            node = flow.nodes.get(current_node_id)
            if not node:
                break
            
            # Get executor for node type
            executor = self.executors.get(node.type)
            if not executor:
                logger.warning(f"No executor for node type: {node.type}")
                break
            
            # Execute node
            try:
                next_node_id = executor.execute(node, context, self)
                actions.append({
                    "node_id": node.id,
                    "node_type": node.type.value,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Move to next node
                if next_node_id:
                    current_node_id = next_node_id
                elif node.next_nodes:
                    current_node_id = node.next_nodes[0]
                else:
                    break
                    
            except Exception as e:
                logger.error(f"Error executing node {node.id}: {e}")
                context.add_history(node.id, "error", {"error": str(e)})
                break
        
        return actions
    
    def _get_start_node(self, flow: Flow) -> Optional[str]:
        """Find the trigger/start node"""
        for node in flow.nodes.values():
            if node.type == NodeType.TRIGGER:
                return node.next_nodes[0] if node.next_nodes else None
        # If no trigger, return first node
        return list(flow.nodes.keys())[0] if flow.nodes else None
    
    def check_trigger(self, flow: Flow, trigger_type: str, trigger_value: str) -> bool:
        """Check if message matches flow trigger"""
        if trigger_type == "keyword":
            return trigger_value.lower() in flow.trigger_value.lower()
        elif trigger_type == "exact":
            return trigger_value == flow.trigger_value
        elif trigger_type == "regex":
            import re
            return bool(re.match(flow.trigger_value, trigger_value))
        elif trigger_type == "always":
            return True
        return False
    
    # =====================================
    # EXTERNAL INTEGRATIONS
    # =====================================
    
    def send_message(self, to: str, message: str) -> bool:
        """Send WhatsApp message"""
        if self.whatsapp_api:
            result = self.whatsapp_api.send_text_message(to, message)
            return result is not None
        return False
    
    def send_quick_reply(self, to: str, content: str, buttons: List[Dict]) -> bool:
        """Send quick reply message"""
        if self.whatsapp_api:
            result = self.whatsapp_api.send_interactive_message(to, buttons=buttons)
            return result is not None
        return False
    
    def send_buttons(self, to: str, content: str, buttons: List[Dict]) -> bool:
        """Send button message"""
        if self.whatsapp_api:
            result = self.whatsapp_api.send_interactive_message(to, buttons=buttons)
            return result is not None
        return False
    
    def send_list(self, to: str, header: str, content: str, rows: List[Dict]) -> bool:
        """Send list message"""
        if self.whatsapp_api:
            result = self.whatsapp_api.send_interactive_message(to, list_rows=rows)
            return result is not None
        return False
    
    def schedule_delayed_execution(self, flow_id: int, contact_id: int,
                                   next_node_id: str, delay_seconds: int):
        """Schedule delayed node execution"""
        execute_at = datetime.now() + timedelta(seconds=delay_seconds)
        
        if flow_id not in self._delayed_queue:
            self._delayed_queue[flow_id] = []
        
        self._delayed_queue[flow_id].append({
            "contact_id": contact_id,
            "next_node_id": next_node_id,
            "execute_at": execute_at
        })
    
    def escalate_to_human(self, context: FlowContext, priority: int = 5):
        """Escalate conversation to human agent"""
        # Update conversation status
        self.db.escalate_conversation(context.contact_id, priority)
        
        # Log for team inbox
        logger.info(f"Escalating contact {context.contact_id} to human (priority: {priority})")
    
    def add_contact_tag(self, contact_id: int, tag: str):
        """Add tag to contact"""
        self.db.add_contact_tag(contact_id, tag)


# =====================================
# FLOW TEMPLATES
# =====================================

FLOW_TEMPLATES = {
    "welcome": {
        "name": "Welcome Message",
        "description": "Greet new contacts",
        "nodes": [
            {"id": "trigger", "type": "trigger", "label": "Start"},
            {"id": "welcome", "type": "message", "label": "Welcome", 
             "config": {"content": "Hi {{name}}! Welcome to our business! 👋 How can I help you today?"},
             "next_nodes": ["end"]},
            {"id": "end", "type": "end", "label": "End"}
        ]
    },
    "lead_qualification": {
        "name": "Lead Qualification",
        "description": "Qualify leads with questions",
        "nodes": [
            {"id": "trigger", "type": "trigger", "label": "Start"},
            {"id": "greet", "type": "message", 
             "config": {"content": "Hi! How can I help you today?"},
             "next_nodes": ["choice"]},
            {"id": "choice", "type": "quick_reply",
             "config": {"content": "What are you interested in?", 
                       "buttons": [{"id": "product", "title": "Products 🛍️"},
                                  {"id": "pricing", "title": "Pricing 💰"},
                                  {"id": "support", "title": "Support ❓"}]},
             "next_nodes": ["product_info", "pricing_info", "support_info"]},
            {"id": "product_info", "type": "message",
             "config": {"content": "We have amazing products! Check our catalog at [link]"},
             "next_nodes": ["capture_lead"]},
            {"id": "pricing_info", "type": "ai_response",
             "config": {"prompt": "Provide pricing information"},
             "next_nodes": ["capture_lead"]},
            {"id": "support_info", "type": "message",
             "config": {"content": "Our support team is here to help!"},
             "next_nodes": ["capture_lead"]},
            {"id": "capture_lead", "type": "add_tag",
             "config": {"tag": "interested"},
             "next_nodes": ["end"]},
            {"id": "end", "type": "end"}
        ]
    },
    "order_tracking": {
        "name": "Order Tracking",
        "description": "Track order status",
        "nodes": [
            {"id": "trigger", "type": "trigger", "label": "Start"},
            {"id": "ask_order", "type": "message",
             "config": {"content": "Please enter your order ID"},
             "next_nodes": ["fetch_order"]},
            {"id": "fetch_order", "type": "api_call",
             "config": {"url": "/api/orders/{{order_id}}", "save_to": "order_status"},
             "next_nodes": ["send_status"]},
            {"id": "send_status", "type": "message",
             "config": {"content": "Your order {{order_id}} status: {{order_status}}"},
             "next_nodes": ["end"]},
            {"id": "end", "type": "end"}
        ]
    }
}
