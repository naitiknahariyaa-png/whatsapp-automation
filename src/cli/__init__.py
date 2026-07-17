"""
====================================================================
CLI MODULE - User Interface Components
====================================================================

Contains:
- colors.py: Terminal color codes
- menu.py: Banner and menu text
- commands.py: All menu command implementations

Author: Built for Indian Businesses 🇮🇳
====================================================================
"""

from .colors import C, BANNER, MENU
from .commands import (
    setup_ai,
    add_keyword,
    view_keywords,
    view_stats,
    test_reply,
    view_cache_stats,
    start_api_server,
    run_tests,
    show_langchain_stack,
    setup_langsmith,
    clear_data,
    load_cafe_menu,
    setup_whatsapp,
    start_bot,
)

__all__ = [
    "C",
    "BANNER",
    "MENU",
    "setup_ai",
    "add_keyword",
    "view_keywords",
    "view_stats",
    "test_reply",
    "view_cache_stats",
    "start_api_server",
    "run_tests",
    "show_langchain_stack",
    "setup_langsmith",
    "clear_data",
    "load_cafe_menu",
    "setup_whatsapp",
    "start_bot",
]
