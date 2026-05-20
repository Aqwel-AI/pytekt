"""Agent CLI constants."""

from __future__ import annotations

AGENT_MODES = [
    "💻  Coding Agent (OpenAI, DeepSeek…)",
    "🦙  Local AI (Ollama)",
    "📴  Offline (disconnect)",
    "📖  Show Help Catalog",
]

# Shown in menus; not connectable until the hosted API ships
COMING_SOON_PROVIDERS = frozenset({"aqwel"})

CLOUD_PROVIDERS = [
    "✨ Aqwel AI (coming soon)",
    "🟢 OpenAI (recommended for coding)",
    "🐋 DeepSeek (coding + tools)",
    "🔌 OpenAI Compatible",
    "🔵 Gemini (chat only)",
    "🟠 Anthropic (chat only)",
    "🦙 Ollama",
]

DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "deepseek": "deepseek-chat",
    "gemini": "gemini-2.0-flash",
    "anthropic": "claude-3-5-sonnet-20240620",
    "openai_compatible": "default-model",
}

# Providers that implement native OpenAI-style tool calling
NATIVE_TOOL_PROVIDERS = frozenset({
    "openai",
    "deepseek",
    "openai_compatible",
    "compatible",
})

CODING_AGENT_PROMPT = """You are Aion, a helpful coding assistant with optional filesystem tools.

For conversation (greetings, questions, explanations): answer clearly in natural language.
Do not call tools unless the user asks to inspect or change files.

When the user wants code changes:
- Use tools (read_file, list_files, grep, write_file, edit_file, etc.) — never tell them to run commands manually.
- Use paths relative to the workspace only (never invent absolute paths).
- read_file before edit_file; list_files/grep/glob to explore when unsure.

After tool work, summarize what changed."""


def mode_key(choice: int) -> str:
    return {1: "cloud", 2: "ollama", 3: "offline", 4: "help"}.get(choice, "cloud")


def provider_id_from_menu_label(label: str) -> str:
    low = label.lower()
    if "aqwel" in low:
        return "aqwel"
    # "🟢 OpenAI (recommended...)" -> openai
    part = label.split(maxsplit=1)[1].lower()
    return part.split("(")[0].strip().replace(" ", "_")
