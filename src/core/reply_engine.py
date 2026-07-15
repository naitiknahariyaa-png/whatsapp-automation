"""
====================================================================
REPLY ENGINE - Smart Auto-Reply Logic
====================================================================

Handles:
- Keyword matching
- AI response generation
- Context tracking
- Response caching
- Business logic

Author: Built for Indian Businesses 🇮🇳
====================================================================
"""

import re
import logging
import hashlib
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ReplyContext:
    """Context for a conversation"""
    
    def __init__(self, session_id: str, sender: str):
        self.session_id = session_id
        self.sender = sender
        self.history: List[Dict[str, str]] = []
        self.last_keyword: Optional[str] = None
        self.state: str = "idle"  # idle, ordering, asking, etc.
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def add_message(self, role: str, content: str):
        """Add message to history"""
        self.history.append({
            "role": role,
            "content": content,
            "time": datetime.now().isoformat()
        })
        self.last_activity = datetime.now()
        
        # Keep only last 20 messages
        if len(self.history) > 20:
            self.history = self.history[-20:]
    
    def get_context_string(self, max_messages: int = 5) -> str:
        """Get conversation history as string"""
        recent = self.history[-max_messages:] if self.history else []
        return "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in recent
        ])
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if context has expired"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)


class ReplyEngine:
    """
    Smart Reply Engine for WhatsApp Bot
    
    Features:
    - Keyword matching with priority
    - AI integration
    - Conversation context
    - Response templates
    - Business logic
    """
    
    def __init__(
        self,
        db,  # Database instance
        ai_manager,  # AI Manager instance
        business_name: str = "My Business",
        business_hours: str = "9 AM - 9 PM",
        business_phone: str = ""
    ):
        self.db = db
        self.ai = ai_manager
        self.business_name = business_name
        self.business_hours = business_hours
        self.business_phone = business_phone
        
        # Context storage
        self.contexts: Dict[str, ReplyContext] = {}
        self.context_timeout = 30  # minutes
        
        # Response templates
        self.templates = self._load_default_templates()
        
        # Priority keywords (checked first)
        self.priority_keywords = {
            "order": ["order", "buy", "purchase", "ऑर्डर", "खरीदना"],
            "price": ["price", "cost", "₹", "rupees", "कीमत", "दाम"],
            "menu": ["menu", "list", "सूची", "मेन्यू"],
            "location": ["where", "location", "address", "पता", "कहाँ"],
            "hours": ["hours", "open", "close", "time", "समय", "खुला"],
            "contact": ["call", "phone", "contact", "number", "फोन"],
            "delivery": ["delivery", "deliver", "shipping", "डिलीवरी"],
            "help": ["help", "support", "assist", "मदद"],
            "thanks": ["thanks", "thank", "thanking", "धन्यवाद"],
            "bye": ["bye", "goodbye", "tata", "再见"],
        }
        
        logger.info("Reply Engine initialized")
    
    def _load_default_templates(self) -> Dict[str, str]:
        """Load default response templates"""
        return {
            "greeting": "Hello! 👋 Welcome to {business}! How can I help you today?",
            "order": "Great choice! 🎉 To place an order, please tell us:\n1. What would you like?\n2. Your delivery address\n3. Contact number",
            "menu": "📋 Here's our menu!\n\n☕ Coffee\n🍔 Burgers\n🍕 Pizza\n🍝 Pasta\n🍰 Desserts\n\nWhat would you like?",
            "hours": "🕐 We're open {hours}.\n\nWhat else can I help you with?",
            "location": "📍 Visit us at [Your Address]\n\nNeed directions? Call us!",
            "price": "💰 Our prices are very affordable!\n\n• Coffee: ₹99-179\n• Burgers: ₹149-299\n• Pizza: ₹199-499\n\nWhat would you like to order?",
            "delivery": "🚚 Yes, we deliver!\n\n• Within 5km: FREE\n• 5-10km: ₹30\n• 10km+: ₹50\n\nMinimum order: ₹199",
            "contact": "📞 Contact us:\n• Phone: {phone}\n• WhatsApp: Same number\n\nWe're here to help!",
            "thanks": "You're welcome! 😊 Is there anything else I can help you with?",
            "bye": "Goodbye! 👋 Have a great day! See you soon!",
            "default": "Thanks for your message! 🙏\n\nI'll get back to you shortly with more information.\n\nYou can also call us at {phone} for immediate assistance.",
            "unknown": "I'm not sure I understand. 🤔\n\nTry asking about:\n• Menu & Prices\n• Ordering\n• Delivery\n• Business Hours\n• Contact Info",
        }
    
    def get_context(self, sender: str) -> ReplyContext:
        """Get or create conversation context"""
        if sender not in self.contexts:
            self.contexts[sender] = ReplyContext(sender, sender)
        
        ctx = self.contexts[sender]
        
        # Clean up expired contexts
        if ctx.is_expired(self.context_timeout):
            ctx = ReplyContext(sender, sender)
            self.contexts[sender] = ctx
        
        return ctx
    
    def process_message(self, sender: str, message: str) -> str:
        """
        Process incoming message and generate response
        
        Args:
            sender: Sender identifier (phone/name)
            message: Incoming message text
            
        Returns:
            str: Response message
        """
        # Get or create context
        ctx = self.get_context(sender)
        
        # Add to history
        ctx.add_message("user", message)
        
        # Clean message
        clean_message = message.strip()
        message_lower = clean_message.lower()
        
        # Check priority keywords first
        for category, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    response = self._handle_category(category, ctx)
                    if response:
                        ctx.add_message("assistant", response)
                        return response
        
        # Try database keywords
        db_response = self.db.find_reply(clean_message)
        if db_response:
            ctx.add_message("assistant", db_response)
            return db_response
        
        # Use AI if configured
        context_str = ctx.get_context_string()
        ai_response, provider = self.ai.generate(clean_message, context_str)
        
        if ai_response:
            ctx.add_message("assistant", ai_response)
            self.db.log_message(sender, clean_message, ai_response, provider != "keyword")
            return ai_response
        
        # Fall back to default
        response = self.templates["unknown"].format(
            phone=self.business_phone,
            business=self.business_name
        )
        ctx.add_message("assistant", response)
        return response
    
    def _handle_category(self, category: str, ctx: ReplyContext) -> Optional[str]:
        """Handle specific keyword category"""
        ctx.last_keyword = category
        
        templates = {
            "greeting": self.templates["greeting"].format(business=self.business_name),
            "order": self.templates["order"],
            "menu": self.templates["menu"],
            "hours": self.templates["hours"].format(hours=self.business_hours),
            "location": self.templates["location"],
            "price": self.templates["price"],
            "delivery": self.templates["delivery"],
            "contact": self.templates["contact"].format(phone=self.business_phone),
            "thanks": self.templates["thanks"],
            "bye": self.templates["bye"],
        }
        
        return templates.get(category)
    
    def add_keyword_response(self, keyword: str, response: str, category: str = "general") -> bool:
        """Add a custom keyword response"""
        return self.db.add_keyword(keyword, response, category)
    
    def set_business_info(self, **kwargs):
        """Update business information"""
        if "name" in kwargs:
            self.business_name = kwargs["name"]
        if "hours" in kwargs:
            self.business_hours = kwargs["hours"]
        if "phone" in kwargs:
            self.business_phone = kwargs["phone"]
        
        # Update templates
        self.templates["greeting"] = self.templates["greeting"].format(business=self.business_name)
        self.templates["hours"] = self.templates["hours"].format(hours=self.business_hours)
        self.templates["contact"] = self.templates["contact"].format(phone=self.business_phone)
        
        logger.info(f"Business info updated: {kwargs}")
    
    def clear_context(self, sender: str = None):
        """Clear conversation context(s)"""
        if sender:
            if sender in self.contexts:
                del self.contexts[sender]
        else:
            self.contexts.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get reply engine statistics"""
        return {
            "active_contexts": len(self.contexts),
            "templates_loaded": len(self.templates),
            "categories": list(self.priority_keywords.keys()),
        }


# ========================
# Response Utilities
# ========================

def format_menu_item(name: str, price: str, description: str = "") -> str:
    """Format a menu item for display"""
    if description:
        return f"• {name} - ₹{price}\n  {description}"
    return f"• {name} - ₹{price}"


def format_order_confirmation(
    items: List[Dict[str, Any]],
    total: float,
    delivery_fee: float = 0
) -> str:
    """Format order confirmation message"""
    msg = "📦 *Order Confirmed!*\n\n"
    msg += "*Items:*\n"
    
    for item in items:
        msg += f"• {item['name']} x{item['qty']} - ₹{item['price'] * item['qty']}\n"
    
    msg += f"\n*Subtotal:* ₹{total}"
    if delivery_fee > 0:
        msg += f"\n*Delivery:* ₹{delivery_fee}"
    msg += f"\n*Total:* ₹{total + delivery_fee}"
    
    msg += "\n\n⏱️ Estimated delivery: 30-45 minutes"
    
    return msg


def format_price_list(items: List[Dict[str, Any]], title: str = "Price List") -> str:
    """Format a price list message"""
    msg = f"💰 *{title}*\n\n"
    
    for item in items:
        if "category" in item and item["category"]:
            msg += f"\n_{item['category']}_:\n"
        
        if "items" in item:
            for sub_item in item["items"]:
                msg += f"• {sub_item['name']} - ₹{sub_item['price']}\n"
        else:
            msg += f"• {item['name']} - ₹{item['price']}\n"
    
    return msg


def validate_phone_number(phone: str) -> bool:
    """Validate Indian phone number"""
    # Remove spaces, dashes, plus
    clean = re.sub(r'[\s\-+]', '', phone)
    
    # Check if 10 digits (Indian mobile) or 12 digits (with 91)
    if len(clean) == 10 and clean.isdigit():
        return True
    if len(clean) == 12 and clean.startswith("91") and clean[2:].isdigit():
        return True
    
    return False


def format_phone_for_whatsapp(phone: str) -> str:
    """Format phone number for WhatsApp API"""
    clean = re.sub(r'[\s\-+]', '', phone)
    
    # Add 91 if 10 digits (Indian number)
    if len(clean) == 10:
        clean = "91" + clean
    
    return clean
