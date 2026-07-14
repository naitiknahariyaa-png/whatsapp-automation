"""
Auto-Reply Engine Module
Handles keyword-based and AI-powered response generation
"""

import re
import time
from datetime import datetime


class ReplyEngine:
    """Auto-reply engine with keyword and AI support"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.delay = self.config.get('delay', 1)
        self.max_daily = self.config.get('max_daily_replies', 100)
        self.reply_count = 0
        
        # Load keyword rules
        self.keywords = {}
        for rule in self.config.get('keywords', []):
            keyword = rule.get('keyword', '').lower()
            response = rule.get('response', '')
            if keyword:
                self.keywords[keyword] = response
        
        # Default responses
        self.default_reply = self.config.get(
            'default_reply',
            "Thanks for your message! We'll get back to you shortly. 🙏"
        )
        
        # Conversation memory per contact
        self.memory = {}
        self.memory_limit = 10
        
        # Personality settings
        self.personalities = self.config.get('personalities', {
            'default': {
                'name': 'Assistant',
                'greeting': 'Hello! How can I help you?',
                'tone': 'friendly'
            }
        })
        
    def add_keyword(self, keyword, response):
        """Add a new keyword rule"""
        self.keywords[keyword.lower()] = response
        print(f"Added keyword: '{keyword}' → '{response}'")
        
    def remove_keyword(self, keyword):
        """Remove a keyword rule"""
        if keyword.lower() in self.keywords:
            del self.keywords[keyword.lower()]
            print(f"Removed keyword: '{keyword}'")
            
    def get_keyword_reply(self, message):
        """Get reply based on keyword matching"""
        message_lower = message.lower().strip()
        
        # Check each keyword
        for keyword, reply in self.keywords.items():
            # Full word match
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, message_lower):
                return reply
            
            # Partial match
            if keyword in message_lower:
                return reply
                
        return None
    
    def get_ai_reply(self, message, ai_router, sender=None):
        """Get AI-powered reply"""
        if not ai_router:
            return None
            
        try:
            # Build context with conversation memory
            context = self.get_context(sender)
            
            # Generate response
            response = ai_router.generate_response(
                message,
                context=context,
                sender=sender
            )
            
            return response
            
        except Exception as e:
            print(f"AI reply error: {e}")
            return None
    
    def get_context(self, sender):
        """Get conversation context for a sender"""
        if not sender:
            return ""
            
        if sender not in self.memory:
            self.memory[sender] = []
            
        messages = self.memory[sender]
        
        if not messages:
            return ""
            
        # Build context string
        context = "Recent conversation:\n"
        for msg in messages[-self.memory_limit:]:
            context += f"- {msg['sender']}: {msg['content']}\n"
            
        return context
    
    def update_memory(self, sender, user_message, bot_response):
        """Update conversation memory"""
        if not sender:
            return
            
        if sender not in self.memory:
            self.memory[sender] = []
            
        # Add to memory
        self.memory[sender].append({
            'sender': 'user',
            'content': user_message,
            'time': datetime.now()
        })
        
        self.memory[sender].append({
            'sender': 'bot',
            'content': bot_response,
            'time': datetime.now()
        })
        
        # Trim memory
        if len(self.memory[sender]) > self.memory_limit * 2:
            self.memory[sender] = self.memory[sender][-self.memory_limit * 2:]
    
    def get_reply(self, message, ai_router=None, sender=None):
        """
        Main method to get a reply
        Combines keyword matching with AI fallback
        """
        if not self.enabled:
            return None
            
        # Rate limiting
        if self.reply_count >= self.max_daily:
            return "Daily reply limit reached. We'll respond tomorrow!"
            
        # Apply delay
        time.sleep(self.delay)
        
        # Try keyword match first
        reply = self.get_keyword_reply(message)
        
        if reply:
            self.reply_count += 1
            self.update_memory(sender, message, reply)
            return reply
            
        # Try AI if available
        if ai_router:
            reply = self.get_ai_reply(message, ai_router, sender)
            if reply:
                self.reply_count += 1
                self.update_memory(sender, message, reply)
                return reply
        
        # Default fallback
        self.update_memory(sender, message, self.default_reply)
        return self.default_reply
    
    def reset_daily_count(self):
        """Reset the daily reply counter"""
        self.reply_count = 0
        
    def get_stats(self):
        """Get reply engine statistics"""
        return {
            'enabled': self.enabled,
            'keyword_count': len(self.keywords),
            'today_replies': self.reply_count,
            'max_daily': self.max_daily,
            'memory_contacts': len(self.memory)
        }


# ──────────────────────────────────────────────
# Advanced Reply Engine with Multiple Strategies
# ──────────────────────────────────────────────

class AdvancedReplyEngine(ReplyEngine):
    """
    Extended Reply Engine with advanced features:
    - Sentiment analysis
    - Intent detection
    - Multi-turn conversation
    - Personality switching
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # Intent patterns
        self.intents = {
            'greeting': ['hi', 'hello', 'hey', 'namaste', 'hola', 'yo'],
            'goodbye': ['bye', 'tata', 'see you', 'take care', 'later'],
            'question': ['?', 'what', 'how', 'when', 'where', 'why', 'which'],
            'thanks': ['thank', 'thanks', 'appreciate', 'grateful'],
            'order': ['order', 'buy', 'purchase', 'want to get'],
            'price': ['price', 'cost', 'how much', 'rate', 'rupee', '₹'],
            'support': ['help', 'issue', 'problem', 'not working', 'error'],
        }
        
        # Sentiment indicators
        self.positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome']
        self.negative_words = ['bad', 'worst', 'hate', 'terrible', 'angry', 'frustrated', 'disappointed']
        
    def detect_intent(self, message):
        """Detect user intent from message"""
        message_lower = message.lower()
        
        for intent, patterns in self.intents.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return intent
                    
        return 'unknown'
    
    def analyze_sentiment(self, message):
        """Simple sentiment analysis"""
        message_lower = message.lower()
        
        positive_count = sum(1 for word in self.positive_words if word in message_lower)
        negative_count = sum(1 for word in self.negative_words if word in message_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def get_intent_response(self, intent, sentiment='neutral'):
        """Get response based on detected intent"""
        responses = {
            'greeting': {
                'positive': "Hey! Great to see you! 😊 How can I help?",
                'negative': "Hi there! I sense you might have an issue. How can I assist?",
                'neutral': "Hello! Welcome! How can I help you today? 👋"
            },
            'goodbye': {
                'positive': "Happy to help! Take care! 👋",
                'negative': "Sorry if something went wrong. Bye! Take care!",
                'neutral': "Goodbye! Have a great day! 👋"
            },
            'question': {
                'positive': "Great question! Let me help you with that.",
                'negative': "I understand your concern. Let me help clarify.",
                'neutral': "I'll do my best to answer that for you."
            },
            'thanks': {
                'positive': "You're welcome! Happy to help! 😊",
                'negative': "I hope things get better! Let me know if you need anything else.",
                'neutral': "You're welcome! Anything else I can help with?"
            },
            'order': {
                'positive': "Excellent choice! Let me help you with your order!",
                'negative': "I see you're ready to order. Let's get that sorted!",
                'neutral': "Sure! I'd be happy to help you place an order."
            },
            'price': {
                'positive': "Great interest! Here's our pricing info:",
                'negative': "I understand price is important. Let me share our best rates:",
                'neutral': "Here's our pricing information:"
            },
            'support': {
                'positive': "I'll help you right away!",
                'negative': "I'm sorry you're having trouble. Let me help fix this!",
                'neutral': "I'm here to help! What seems to be the problem?"
            }
        }
        
        return responses.get(intent, {}).get(sentiment, self.default_reply)
    
    def get_reply(self, message, ai_router=None, sender=None):
        """Enhanced reply with intent and sentiment analysis"""
        if not self.enabled:
            return None
            
        # Detect intent and sentiment
        intent = self.detect_intent(message)
        sentiment = self.analyze_sentiment(message)
        
        # Check for keyword match first
        keyword_reply = self.get_keyword_reply(message)
        if keyword_reply:
            self.reply_count += 1
            self.update_memory(sender, message, keyword_reply)
            return keyword_reply
            
        # Use intent-based response
        if intent != 'unknown':
            response = self.get_intent_response(intent, sentiment)
            self.reply_count += 1
            self.update_memory(sender, message, response)
            return response
            
        # Try AI as fallback
        if ai_router:
            ai_reply = self.get_ai_reply(message, ai_router, sender)
            if ai_reply:
                self.reply_count += 1
                self.update_memory(sender, message, ai_reply)
                return ai_reply
                
        # Ultimate fallback
        self.update_memory(sender, message, self.default_reply)
        return self.default_reply
