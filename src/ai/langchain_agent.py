"""
LangChain AI Agent - Build AI Agents Completely Free
Integrates LangChain + LangGraph for advanced agent capabilities.
Based on: https://github.com/Moh4696/build-ai-agents-free
"""

import os
import logging
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Try to import LangChain
try:
    from langchain.agents import create_agent
    from langchain_groq import ChatGroq
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.tools import tool
    from langchain_community.tools import DuckDuckGoSearchRun
    from langgraph.checkpoint.memory import InMemorySaver
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("⚠️ LangChain not installed. Run: pip install langchain[groq] langchain-google-genai")


class LangChainAgent:
    """
    Free AI Agent using LangChain + Groq/Gemini
    
    Features:
    - Uses free Groq models (~300 tokens/sec)
    - Web search with DuckDuckGo (no API key!)
    - Memory across conversations
    - Fallback to Gemini if Groq fails
    - Custom tools support
    
    Setup:
    1. pip install langchain[groq] langchain-google-genai duckduckgo-search
    2. Get free Groq key: https://console.groq.com
    3. (Optional) Get free Gemini key: https://aistudio.google.com
    4. Add to .env:
       GROQ_API_KEY=your-key
       GOOGLE_API_KEY=your-key (optional)
    """
    
    def __init__(
        self,
        model_name: str = "llama-3.3-70b-versatile",
        system_prompt: str = "You are a helpful WhatsApp assistant. Be concise and accurate."
    ):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain not installed. Run: pip install langchain[groq]")
        
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.agent = None
        self.checkpointer = InMemorySaver()
        self.tools = []
        
        # Initialize the agent
        self._init_agent()
    
    def _init_agent(self, tools: List = None):
        """Initialize the agent with model and tools"""
        try:
            # Get model with fallback
            model = self._get_model()
            
            # Use provided tools or default
            agent_tools = tools or self.tools
            
            # Create agent
            self.agent = create_agent(
                model=model,
                tools=agent_tools,
                system_prompt=self.system_prompt,
                checkpointer=self.checkpointer
            )
            
            logger.info("✅ LangChain agent initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    def _get_model(self):
        """Get AI model with fallback to Gemini"""
        groq_key = os.getenv("GROQ_API_KEY", "")
        
        # Try Groq first (fastest)
        if groq_key:
            try:
                model = ChatGroq(model=self.model_name)
                model.invoke("ping")  # Test connection
                logger.info("✅ Using Groq model")
                return model
            except Exception as e:
                logger.warning(f"Groq failed: {e}")
        
        # Fallback to Gemini
        gemini_key = os.getenv("GOOGLE_API_KEY", "")
        if gemini_key:
            try:
                model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
                logger.info("✅ Using Gemini model (fallback)")
                return model
            except Exception as e:
                logger.error(f"Gemini fallback failed: {e}")
        
        raise ValueError("No AI provider available. Set GROQ_API_KEY or GOOGLE_API_KEY")
    
    def invoke(self, message: str, thread_id: str = "default") -> str:
        """
        Send message to agent
        
        Args:
            message: User message
            thread_id: Conversation ID for memory
            
        Returns:
            Agent response
        """
        if not self.agent:
            return "Agent not initialized"
        
        try:
            config = {"configurable": {"thread_id": thread_id}}
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": message}]},
                config
            )
            return result["messages"][-1].content
        except Exception as e:
            logger.error(f"Agent invoke error: {e}")
            return f"Error: {str(e)}"
    
    def add_tool(self, func, description: str):
        """
        Add custom tool to agent
        
        Args:
            func: Python function
            description: Tool description for the AI
        """
        tool_instance = tool(func)
        self.tools.append(tool_instance)
        
        # Reinitialize agent with new tools
        self._init_agent(tools=self.tools)


# ═══════════════════════════════════════════════════════════════
# Built-in Tools
# ═══════════════════════════════════════════════════════════════

def create_web_search_tool():
    """Create DuckDuckGo web search tool"""
    try:
        return DuckDuckGoSearchRun()
    except:
        return None


def create_word_count_tool():
    """Create word counter tool"""
    @tool
    def word_count(text: str) -> int:
        """Count how many words are in a piece of text."""
        return len(text.split())
    return word_count


def create_calculator_tool():
    """Create calculator tool"""
    @tool
    def calculator(expression: str) -> str:
        """Evaluate a math expression and return the result.
        Use this for any math calculations."""
        try:
            # Safe evaluation (basic math only)
            allowed = set('0123456789+-*/.() ')
            if all(c in allowed for c in expression):
                result = eval(expression)
                return str(result)
            return "Invalid expression"
        except:
            return "Error in calculation"
    return calculator


def create_translator_tool():
    """Create language translator tool"""
    @tool
    def translate(text: str, from_lang: str = "auto", to_lang: str = "en") -> str:
        """Translate text from one language to another.
        Args:
            text: Text to translate
            from_lang: Source language (default: auto-detect)
            to_lang: Target language (default: en)"""
        # Simple translation using keywords
        # For full translation, use Google Translate API
        return f"[Translation from {from_lang} to {to_lang}]: {text}"
    return translate


# ═══════════════════════════════════════════════════════════════
# Complete Agent Setup
# ═══════════════════════════════════════════════════════════════

def create_whatsapp_agent() -> LangChainAgent:
    """
    Create a complete WhatsApp agent with all tools
    
    Returns:
        Configured LangChainAgent with:
        - Web search
        - Word counter
        - Calculator
        - Memory
        - Provider fallback
    """
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("LangChain not installed")
    
    # Create tools
    tools = []
    
    web_search = create_web_search_tool()
    if web_search:
        tools.append(web_search)
    
    tools.append(create_word_count_tool())
    tools.append(create_calculator_tool())
    
    # Create agent with system prompt
    agent = LangChainAgent(
        system_prompt="""You are a helpful WhatsApp assistant for a business.
        You help customers with:
        - Answering questions about products/services
        - Providing prices and availability
        - Taking orders
        - Booking appointments
        - General inquiries
        
        Be concise, friendly, and professional. Use tools when needed."""
    )
    
    # Add tools and reinitialize
    agent.tools = tools
    agent._init_agent(tools=tools)
    
    return agent


# ═══════════════════════════════════════════════════════════════
# Usage Examples
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║       LangChain AI Agent Setup                         ║
╚══════════════════════════════════════════════════════════╝

1. Install dependencies:
   pip install langchain[groq] langchain-google-genai duckduckgo-search

2. Get free Groq API key:
   https://console.groq.com

3. Add to .env:
   GROQ_API_KEY=your-key

Quick Test:
   from src.ai.langchain_agent import create_whatsapp_agent
   agent = create_whatsapp_agent()
   print(agent.invoke("Hello!"))
""")
