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
║       🤖 WHATSAPP AI BOT v3.0 🤖                           ║
║       SIMPLIFIED VERSION                                      ║
║                                                               ║
║     ✅ Pydantic Validation  ✅ FastAPI Webhook               ║
║     ✅ Multi-Provider AI   ✅ Auto-Recovery System          ║
║     ✅ SQLite (Safe)      ✅ pytest Tests                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{C.END}
"""


# Menu text
MENU = f"""
{C.CYAN}═══════════════════════════════════════════════════════════{C.END}

  {C.BOLD}📱 WhatsApp AI Bot v3.0{C.END}

{C.GREEN}[1]{C.END}  🚀 Start Auto-Reply Bot
{C.GREEN}[2]{C.END}  📱 Setup WhatsApp Session
{C.GREEN}[3]{C.END}  🤖 Setup AI Provider
{C.GREEN}[4]{C.END}  📝 Add Keywords
{C.GREEN}[5]{C.END}  📊 View Statistics
{C.GREEN}[6]{C.END}  💬 Test Auto-Reply
{C.GREEN}[7]{C.END}  📜 View Keywords
{C.GREEN}[8]{C.END}  🏪 Cafe Menu Options
{C.GREEN}[9]{C.END}  ⚡ View Cache Stats
{C.GREEN}[10]{C.END} 🌐 Start API Server (FastAPI)
{C.GREEN}[11]{C.END} 🧪 Run Tests
{C.GREEN}[12]{C.END} 🧠 LangChain AI Stack
{C.GREEN}[13]{C.END} 🗑️  Clear All Data

{C.GREEN}[0]{C.END}   {C.RED}Exit{C.END}

{C.CYAN}═══════════════════════════════════════════════════════════{C.END}
"""
