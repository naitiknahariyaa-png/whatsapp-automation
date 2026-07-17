"""
====================================================================
COLORS - Terminal Color Codes
====================================================================

Simple ANSI color codes for terminal output.
"""

# Color class for easy access
class C:
    """Terminal color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


# Banner text
BANNER = f"""
{C.CYAN}{C.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🤖 WHATSAPP AI BOT v3.0 🤖                              ║
║     🚀 PRO EDITION - FULL FEATURES 🚀                       ║
║                                                               ║
║     ✅ WhatsApp v2.0 (Fixed Auto-Reply)                      ║
║     ✅ OmniRoute (250+ AI Providers)                         ║
║     ✅ Chatwoot (CRM Integration)                            ║
║     ✅ Redis Cache + Supabase DB                             ║
║     ✅ 20+ Professional Skills                                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{C.END}
"""


# Menu text
MENU = f"""
{C.CYAN}═══════════════════════════════════════════════════════════{C.END}

  {C.BOLD}📱 WhatsApp AI Bot v3.0 PRO{C.END}

{C.GREEN}[1]{C.END}  🚀 Start Auto-Reply Bot (Fixed v2.0)
{C.GREEN}[2]{C.END}  📱 Setup WhatsApp Session
{C.GREEN}[3]{C.END}  🤖 Setup AI (OpenRouter/Groq/OmniRoute)
{C.GREEN}[4]{C.END}  📝 Add Keywords
{C.GREEN}[5]{C.END}  📊 View Statistics
{C.GREEN}[6]{C.END}  💬 Test Auto-Reply
{C.GREEN}[7]{C.END}  📜 View Keywords
{C.GREEN}[8]{C.END}  🔌 Integration Tools
{C.GREEN}[9]{C.END}  ⚡ View Cache Stats
{C.GREEN}[10]{C.END} 🌐 Start API Server (FastAPI)
{C.GREEN}[11]{C.END} 🧪 Run Tests
{C.GREEN}[12]{C.END} 🧠 LangChain AI Stack
{C.GREEN}[13]{C.END} 🗑️  Clear All Data
{C.GREEN}[14]{C.END} 📚 View Skills & Integrations

{C.GREEN}[0]{C.END}   {C.RED}Exit{C.END}

{C.CYAN}═══════════════════════════════════════════════════════════{C.END}
"""
