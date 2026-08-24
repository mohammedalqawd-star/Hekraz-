"""CyberGuard tool registry.

Only safe/defensive and isolated-lab capabilities are registered here.
"""
from dataclasses import dataclass
from typing import Callable, Any

@dataclass(frozen=True)
class Tool:
    id: str
    name: str
    category: str
    description: str
    purpose: str
    lab_only: bool
    handler: Callable[..., Any] | None = None

TOOLS: dict[str, Tool] = {}

def register(tool: Tool) -> None:
    TOOLS[tool.id] = tool

def list_tools(category: str | None = None) -> list[Tool]:
    values = list(TOOLS.values())
    return [t for t in values if category is None or t.category == category]

def get_tool(tool_id: str) -> Tool | None:
    return TOOLS.get(tool_id)

register(Tool(
    id="web_headers",
    name="HTTP Security Headers",
    category="web",
    description="Collects HTTP response headers for an authorized target or local lab.",
    purpose="Helps identify missing or weak browser security controls.",
    lab_only=False,
))
register(Tool(
    id="dns_lookup",
    name="DNS Lookup",
    category="network",
    description="Resolves DNS records for an authorized target.",
    purpose="Supports defensive DNS troubleshooting and asset inventory.",
    lab_only=False,
))
register(Tool(
    id="ctf_lab",
    name="CTF Lab",
    category="lab",
    description="Runs educational challenges inside an isolated Cyber Range.",
    purpose="Provides hands-on security training without targeting third parties.",
    lab_only=True,
))

def tool_card(tool: Tool) -> str:
    scope = "🧪 مختبر معزول" if tool.lab_only else "🔐 هدف مصرح به فقط"
    return (
        f"🧰 {tool.name}\n\n"
        f"📌 ما هي؟ {tool.description}\n"
        f"🎯 المهمة: {tool.purpose}\n"
        f"🔒 النطاق: {scope}\n"
        f"🆔 {tool.id}"
    )
