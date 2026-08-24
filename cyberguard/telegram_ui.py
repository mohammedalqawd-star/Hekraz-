"""Telegram menu definitions for the CyberGuard core.

Handlers are intentionally kept separate from the UI definitions so every
button can be wired to a tested function rather than a placeholder.
"""
from .tool_registry import list_tools, tool_card


def main_menu():
    return [
        [("🏠 الرئيسية", "home"), ("🛡️ الدفاعي", "defensive")],
        [("🧪 المختبرات", "labs"), ("🏆 CTF", "ctf")],
        [("🌐 أمن الويب", "web"), ("📡 الشبكات", "network")],
        [("🧠 Cyber AI", "ai"), ("📊 التقارير", "reports")],
        [("🧰 الأدوات", "tools"), ("👤 حسابي", "account")],
    ]


def tools_menu(category: str | None = None):
    tools = list_tools(category)
    return [(tool.name, f"tool:{tool.id}") for tool in tools]


def tool_description(tool_id: str):
    from .tool_registry import get_tool
    tool = get_tool(tool_id)
    if tool is None:
        return "❌ الأداة غير موجودة."
    return tool_card(tool)
