"""
====================================================================
MENU - Menu Structure Definition
====================================================================

Defines the menu structure for the CLI.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class MenuCategory(Enum):
    """Menu categories"""
    MAIN = "main"
    SETTINGS = "settings"
    BUSINESS = "business"
    DEVELOPER = "developer"


@dataclass
class MenuItem:
    """A single menu item"""
    number: str
    icon: str
    title: str
    description: str
    command: str
    category: MenuCategory = MenuCategory.MAIN


# Main menu items
MAIN_MENU_ITEMS: List[MenuItem] = [
    MenuItem("1", "🚀", "Start Auto-Reply Bot", "Start monitoring WhatsApp for messages", "start_bot"),
    MenuItem("2", "📱", "Setup WhatsApp", "Connect to WhatsApp Web or Cloud API", "setup_whatsapp"),
    MenuItem("3", "🤖", "Setup AI", "Configure OpenRouter, Groq, or Keyword AI", "setup_ai"),
    MenuItem("4", "📝", "Add Keywords", "Add custom keyword responses", "add_keyword"),
    MenuItem("5", "📊", "View Statistics", "See message and reply stats", "view_stats"),
    MenuItem("6", "💬", "Test Reply", "Test auto-reply with a sample message", "test_reply"),
    MenuItem("7", "📜", "View Keywords", "List all custom keywords", "view_keywords"),
    MenuItem("8", "🏪", "Cafe Menu", "Load cafe menu options", "load_cafe_menu"),
    MenuItem("9", "⚡", "Cache Stats", "View AI response cache statistics", "view_cache_stats"),
    MenuItem("10", "🌐", "API Server", "Start FastAPI webhook server", "start_api_server"),
    MenuItem("11", "🧪", "Run Tests", "Run pytest unit tests", "run_tests"),
    MenuItem("12", "🧠", "LangChain Stack", "View LangChain AI integration", "show_langchain_stack"),
    MenuItem("13", "🗑️", "Clear Data", "Reset database and cache", "clear_data"),
]


def get_menu_item(command: str) -> Optional[MenuItem]:
    """Get menu item by command name"""
    for item in MAIN_MENU_ITEMS:
        if item.command == command:
            return item
    return None
