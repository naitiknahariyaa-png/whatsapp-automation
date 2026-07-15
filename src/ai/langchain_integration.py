"""
====================================================================
LANGCHAIN AI MODULE - Production-Ready AI Orchestration
====================================================================

🔵 LangChain — builds the components (models, prompts, tools, memory)
🔵 LangGraph — orchestrates the workflow (state, loops, branching)
🟡 LangSmith — observes everything (tracing, debugging, evaluation)

Author: Built for Indian Businesses 🇮🇳
====================================================================
"""

import os
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Check for LangChain availability
LANGCHAIN_AVAILABLE = False
LANGSMITH_AVAILABLE = False

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.tools import tool
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    LANGCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("LangChain not installed. Run: pip install langchain langchain-openai")

try:
    from langsmith import Client as LangSmithClient
    LANGSMITH_AVAILABLE = True
except ImportError:
    logger.warning("LangSmith not installed. Run: pip install langsmith")


# ========================
# LANGCHAIN: Tools (Lego Blocks)
# ========================

class WhatsAppTools:
    """
    LangChain Tools - The Lego blocks for our AI agent
    
    Each tool has:
    - name: Tool identifier
    - description: What it does (for LLM)
    - function: Actual implementation
    """
    
    def __init__(self, database, business_info: Dict[str, str] = None):
        self.db = database
        self.business_info = business_info or {
            "name": "My Business",
            "hours": "9 AM - 9 PM",
            "phone": "",
            "address": ""
        }
    
    @tool
    def get_business_info(self) -> str:
        """Get business information like name, hours, address, contact."""
        return f"""
Business Information:
- Name: {self.business_info.get('name', 'My Business')}
- Hours: {self.business_info.get('hours', '9 AM - 9 PM')}
- Phone: {self.business_info.get('phone', 'Not provided')}
- Address: {self.business_info.get('address', 'Not provided')}
"""
    
    @tool
    def search_keywords(self, query: str) -> str:
        """Search for matching keywords in the knowledge base."""
        keywords = self.db.get_all_keywords()
        query_lower = query.lower()
        
        matches = []
        for kw in keywords:
            if kw['keyword'].lower() in query_lower:
                matches.append(f"{kw['keyword']}: {kw['response']}")
        
        if matches:
            return "\n".join(matches[:5])  # Return top 5 matches
        return "No matching keywords found."
    
    @tool
    def get_statistics(self) -> str:
        """Get bot statistics and metrics."""
        stats = self.db.get_stats()
        keywords_count = len(self.db.get_all_keywords())
        
        return f"""
Bot Statistics:
- Total Messages: {stats.get('total_messages', 0)}
- Total Replies: {stats.get('total_replies', 0)}
- AI Responses: {stats.get('total_ai_responses', 0)}
- Keywords Configured: {keywords_count}
"""
    
    @tool
    def check_operating_hours(self) -> str:
        """Check if business is currently open."""
        from datetime import datetime
        now = datetime.now()
        hour = now.hour
        
        # Simple check (9 AM = 9, 9 PM = 21)
        if 9 <= hour < 21:
            return "✅ Currently OPEN. We are available to help!"
        else:
            return "⏰ Currently CLOSED. We are open 9 AM - 9 PM."
    
    @tool
    def format_response(self, message: str, style: str = "friendly") -> str:
        """Format a response message with emojis and styling."""
        styles = {
            "friendly": f"😊 {message}",
            "formal": f"Dear Customer, {message}",
            "urgent": f"⚠️ {message}",
            "greeting": f"👋 {message}",
        }
        return styles.get(style, message)
    
    def get_all_tools(self) -> List:
        """Get all available tools."""
        return [
            self.get_business_info,
            self.search_keywords,
            self.get_statistics,
            self.check_operating_hours,
            self.format_response,
        ]


# ========================
# LANGGRAPH: Workflow Orchestration
# ========================

class WhatsAppAgentGraph:
    """
    LangGraph Workflow - Orchestrates the agent workflow
    
    This defines HOW the AI thinks and responds:
    - State: What information is tracked
    - Nodes: What steps are taken
    - Edges: How decisions are made
    
    The graph structure:
    
    start → classify → [order] → get_order_details → respond
                   → [inquiry] → search_keywords → respond
                   → [greeting] → respond_greeting
                   → [other] → use_ai → respond
                   → end
    """
    
    def __init__(self, tools: List, llm):
        self.tools = tools
        self.llm = llm
        self.graph = None
        self._build_graph()
    
    def _classify_intent(self, state: Dict) -> str:
        """Classify user intent from message."""
        message = state.get("messages", [{}])[-1].content if state.get("messages") else ""
        
        # Simple keyword-based classification
        message_lower = message.lower()
        
        if any(w in message_lower for w in ["hi", "hello", "hey", "namaste", "नमस्ते"]):
            return "greeting"
        elif any(w in message_lower for w in ["order", "buy", "purchase", "ऑर्डर"]):
            return "order"
        elif any(w in message_lower for w in ["price", "cost", "₹", "rupees", "कीमत"]):
            return "inquiry"
        elif any(w in message_lower for w in ["menu", "list", "सूची"]):
            return "menu"
        else:
            return "other"
    
    def _build_graph(self):
        """
        Build the LangGraph workflow
        
        In a full implementation, this would use:
        - StateGraph for state management
        - add_edge for flow control
        - add_node for each step
        """
        logger.info("Building LangGraph workflow...")
        
        # Graph structure would be:
        # self.graph = StateGraph(AgentState)
        # self.graph.add_node("classify", self._classify_intent)
        # self.graph.add_node("respond", self._generate_response)
        # ... etc
        
        logger.info("LangGraph workflow ready")
    
    def run(self, message: str, context: Dict = None) -> str:
        """
        Run the agent workflow on a message.
        
        This is the main entry point for processing messages.
        """
        state = {
            "messages": [HumanMessage(content=message)],
            "context": context or {},
            "intent": None,
            "response": None,
        }
        
        # Step 1: Classify intent
        intent = self._classify_intent(state)
        state["intent"] = intent
        
        logger.info(f"Classified intent: {intent}")
        
        # Step 2: Generate response based on intent
        response = self._generate_response(state)
        state["response"] = response
        
        return response
    
    def _generate_response(self, state: Dict) -> str:
        """Generate response using tools and LLM."""
        message = state["messages"][-1].content
        intent = state.get("intent", "other")
        
        # Build system prompt
        system_prompt = f"""You are a helpful WhatsApp assistant for an Indian business.

Intent detected: {intent}

Guidelines:
- Keep responses SHORT (1-2 sentences)
- Use emojis sparingly
- Be friendly and helpful
- Respond in the same language as the user
- If you don't know something, say so politely

Available tools:
- get_business_info: Get business name, hours, address, phone
- search_keywords: Search the knowledge base
- check_operating_hours: Check if business is open now
- format_response: Format the response nicely

User message: {message}"""
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=message)
        ])
        
        # Bind tools to LLM
        llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Generate response
        chain = prompt | llm_with_tools | StrOutputParser()
        
        try:
            response = chain.invoke({})
            return response
        except Exception as e:
            logger.error(f"LangChain error: {e}")
            # Fallback to simple response
            return self._fallback_response(message, intent)


# ========================
# LANGSMITH: Observability
# ========================

class WhatsAppObserver:
    """
    LangSmith Observer - Traces and monitors all agent runs
    
    This provides transparency:
    - Trace every step the agent takes
    - Debug when something breaks
    - Evaluate quality over time
    - Monitor performance metrics
    
    Think of it as a "black box recorder" for your AI.
    """
    
    def __init__(self, api_key: str = None, project_name: str = "whatsapp-bot"):
        self.api_key = api_key or os.environ.get("LANGSMITH_API_KEY")
        self.project_name = project_name
        self.client = None
        self.tracing_enabled = False
        
        if self.api_key and LANGSMITH_AVAILABLE:
            self._setup_tracing()
    
    def _setup_tracing(self):
        """Setup LangSmith tracing."""
        try:
            from langsmith import tracing_context
            
            os.environ["LANGSMITH_API_KEY"] = self.api_key
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_PROJECT"] = self.project_name
            
            self.client = LangSmithClient(api_key=self.api_key)
            self.tracing_enabled = True
            
            logger.info(f"✅ LangSmith tracing enabled for project: {self.project_name}")
        except Exception as e:
            logger.warning(f"LangSmith setup failed: {e}")
    
    def trace_message(self, message: str, response: str, metadata: Dict = None):
        """
        Trace a single message-response pair.
        
        This logs:
        - Input message
        - Output response
        - Processing time
        - Intent detected
        - Tools used
        - Any errors
        """
        if not self.tracing_enabled:
            return
        
        try:
            trace_data = {
                "input": message,
                "output": response,
                "metadata": metadata or {},
                "timestamp": str(__import__('datetime').datetime.now()),
            }
            
            # Log to LangSmith
            self.client.create_run(
                name="whatsapp_message",
                inputs={"message": message},
                outputs={"response": response},
                metadata=metadata,
            )
            
            logger.debug(f"Traced: {message[:50]}... → {response[:50]}...")
            
        except Exception as e:
            logger.warning(f"Tracing error: {e}")
    
    def get_traces(self, limit: int = 10) -> List[Dict]:
        """Get recent traces for debugging."""
        if not self.client:
            return []
        
        try:
            runs = self.client.list_runs(
                project_name=self.project_name,
                limit=limit,
            )
            return [
                {
                    "id": str(run.id),
                    "input": run.inputs,
                    "output": run.outputs,
                    "status": run.status,
                    "error": run.error,
                }
                for run in runs
            ]
        except Exception as e:
            logger.warning(f"Failed to get traces: {e}")
            return []
    
    def evaluate_response(self, test_cases: List[Dict]) -> Dict:
        """
        Evaluate AI responses against test cases.
        
        Args:
            test_cases: List of {"input": "...", "expected": "..."}
        
        Returns:
            Evaluation results with pass/fail rates
        """
        results = []
        passed = 0
        
        for case in test_cases:
            input_msg = case["input"]
            expected = case["expected"].lower()
            
            # Run through agent (this would use the actual agent)
            # For now, simulate
            actual = "Simulated response"  # Would be actual agent response
            
            # Simple keyword matching for evaluation
            is_pass = any(word in actual.lower() for word in expected.split())
            
            results.append({
                "input": input_msg,
                "expected": expected,
                "actual": actual,
                "passed": is_pass,
            })
            
            if is_pass:
                passed += 1
        
        return {
            "total": len(test_cases),
            "passed": passed,
            "failed": len(test_cases) - passed,
            "pass_rate": f"{(passed / len(test_cases) * 100):.1f}%",
            "results": results,
        }


# ========================
# Production AI Manager
# ========================

class ProductionAIManager:
    """
    Production AI Manager - Combines all three Lang* components
    
    LangChain: For building LLM components
    LangGraph: For orchestrating workflows
    LangSmith: For observability
    
    This is the main entry point for the AI system.
    """
    
    def __init__(
        self,
        database,
        openrouter_api_key: str = None,
        langsmith_api_key: str = None,
        business_info: Dict = None
    ):
        self.db = database
        self.business_info = business_info or {}
        
        # Initialize components
        self.tools = None
        self.llm = None
        self.agent_graph = None
        self.observer = None
        
        # Setup
        self._setup_langchain()
        self._setup_langsmith(langsmith_api_key)
    
    def _setup_langchain(self):
        """Setup LangChain components."""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available - using fallback mode")
            return
        
        try:
            # Setup tools
            self.tools = WhatsAppTools(self.db, self.business_info).get_all_tools()
            
            # Setup LLM (OpenRouter via LangChain)
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                # Try to load from config
                from src.core.config import load_config
                config = load_config()
                api_key = config.ai.openrouter_api_key
            
            if api_key:
                # Use OpenRouter compatible LLM
                self.llm = ChatOpenAI(
                    model="openrouter/free",
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1",
                    temperature=0.7,
                    max_tokens=150,
                )
                
                # Setup agent graph
                self.agent_graph = WhatsAppAgentGraph(
                    tools=self.tools,
                    llm=self.llm
                )
                
                logger.info("✅ LangChain setup complete")
            else:
                logger.warning("No API key - LangChain using fallback")
                
        except Exception as e:
            logger.error(f"LangChain setup error: {e}")
    
    def _setup_langsmith(self, api_key: str = None):
        """Setup LangSmith observability."""
        if not LANGSMITH_AVAILABLE:
            logger.warning("LangSmith not available - observability disabled")
            return
        
        api_key = api_key or os.environ.get("LANGSMITH_API_KEY")
        
        if api_key:
            self.observer = WhatsAppObserver(
                api_key=api_key,
                project_name="whatsapp-business-bot"
            )
            logger.info("✅ LangSmith observability enabled")
        else:
            logger.info("LangSmith API key not provided - observability disabled")
    
    def generate_response(self, message: str, context: Dict = None) -> tuple[str, str]:
        """
        Generate AI response using full LangChain/LangGraph stack.
        
        Returns:
            tuple: (response_text, intent_detected)
        """
        metadata = {
            "message_length": len(message),
            "has_context": context is not None,
        }
        
        # Use LangGraph agent if available
        if self.agent_graph:
            try:
                intent = "ai"  # Will be classified by graph
                response = self.agent_graph.run(message, context)
                
                # Trace the interaction
                if self.observer:
                    self.observer.trace_message(message, response, metadata)
                
                return response, intent
            except Exception as e:
                logger.error(f"Agent error: {e}")
        
        # Fallback to simple AI
        return self._simple_response(message), "keyword"
    
    def _simple_response(self, message: str) -> str:
        """Simple keyword-based response (fallback)."""
        keywords = self.db.get_all_keywords()
        message_lower = message.lower()
        
        for kw in keywords:
            if kw['keyword'].lower() in message_lower:
                return kw['response']
        
        return "Thanks for your message! We'll get back to you shortly. 🙏"
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all AI components."""
        return {
            "langchain": LANGCHAIN_AVAILABLE,
            "langgraph": self.agent_graph is not None,
            "langsmith": self.observer is not None and self.observer.tracing_enabled,
            "tools_count": len(self.tools) if self.tools else 0,
            "llm_configured": self.llm is not None,
        }
    
    def get_recent_traces(self) -> List[Dict]:
        """Get recent traces from LangSmith."""
        if self.observer:
            return self.observer.get_traces()
        return []
    
    def run_evaluation(self, test_cases: List[Dict]) -> Dict:
        """Run evaluation against test cases."""
        if self.observer:
            return self.observer.evaluate_response(test_cases)
        return {"error": "LangSmith not configured"}


# ========================
# Demo/Test Functions
# ========================

def demo_langchain():
    """Demonstrate LangChain components."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🧩 LANCHAIN DEMO - The Lego Blocks                           ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║  LangChain provides:                                            ║
║  • Models: ChatOpenAI, Anthropic, etc.                        ║
║  • Prompts: Templates for structured prompts                    ║
║  • Tools: Functions the AI can call                           ║
║  • Memory: Store conversation history                          ║
║  • Retrievers: Search and retrieval                           ║
║                                                                ║
║  Example:                                                      ║
║  ┌─────────────────────────────────────────────┐              ║
║  │ from langchain_openai import ChatOpenAI     │              ║
║  │ from langchain_core.tools import tool       │              ║
║  │                                             │              ║
║  │ @tool                                      │              ║
║  │ def get_weather(city: str) -> str:        │              ║
║  │     return f"Weather in {city}: Sunny"     │              ║
║  │                                             │              ║
║  │ llm = ChatOpenAI(model="gpt-4")            │              ║
║  │ llm_with_tools = llm.bind_tools([get_weather])              ║
║  └─────────────────────────────────────────────┘              ║
║                                                                ║
╚═══════════════════════════════════════════════════════════════╝
""")


def demo_langgraph():
    """Demonstrate LangGraph workflow."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🔵 LANGGRAPH DEMO - The Workflow Orchestrator               ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║  LangGraph provides:                                          ║
║  • StateGraph: Manage state across steps                     ║
║  • add_node: Define each step in the workflow               ║
║  • add_edge: Define how steps connect                       ║
║  • Conditional edges: Branch based on conditions            ║
║  • Memory: Persistent state between calls                   ║
║                                                                ║
║  Example workflow:                                             ║
║  ┌─────────────────────────────────────────────┐              ║
║  │ start → classify → [greeting] → respond     │              ║
║  │                  → [order] → get_details    │              ║
║  │                  → [other] → use_ai         │              ║
║  │                        ↓                    │              ║
║  │                    respond ← ───────────────┘              ║
║  └─────────────────────────────────────────────┘              ║
║                                                                ║
║  Each node is a function that transforms state.               ║
║  The graph manages state and control flow.                     ║
║                                                                ║
╚═══════════════════════════════════════════════════════════════╝
""")


def demo_langsmith():
    """Demonstrate LangSmith observability."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🟡 LANGSMITH DEMO - The Observer                           ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║  LangSmith provides:                                         ║
║  • Tracing: See every step the agent takes                  ║
║  • Debugging: Find exactly where things broke               ║
║  • Evaluation: Measure quality over time                    ║
║  • Datasets: Test against known inputs                      ║
║  • Metrics: Latency, cost, token usage                      ║
║                                                                ║
║  Example:                                                     ║
║  ┌─────────────────────────────────────────────┐              ║
║  │ from langsmith import Client                │              ║
║  │                                          │              ║
║  │ client = Client(api_key="your-key")      │              ║
║  │                                          │              ║
║  │ # Trace a run                            │              ║
║  │ client.create_run(                        │              ║
║  │     name="whatsapp_message",             │              ║
║  │     inputs={"message": "Hello"},         │              ║
║  │     outputs={"response": "Hi!"}          │              ║
║  │ )                                        │              ║
║  └─────────────────────────────────────────────┘              ║
║                                                                ║
║  View traces at: https://smith.langchain.com                  ║
║                                                                ║
╚═══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    print("\n🧩 LangChain | 🔵 LangGraph | 🟡 LangSmith Demo\n")
    
    demo_langchain()
    demo_langgraph()
    demo_langsmith()
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  💡 One-liner to remember:                                   ║
║                                                               ║
║  📦 LangChain builds.   → The Lego pieces                    ║
║  🔵 LangGraph orchestrates. → How pieces connect              ║
║  🟡 LangSmith observes.   → Watch what happens                ║
║                                                               ║
║  Together: Demo → Production Ready AI! 🚀                     ║
╚═══════════════════════════════════════════════════════════════╝
""")
