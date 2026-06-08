"""Agent CLI constants."""

from __future__ import annotations

AGENT_MODES = [
    "🦙  Local AI (Ollama)",
    "📴  Offline (disconnect)",
    "📖  Show Help Catalog",
]

AGENT_PROVIDER = "ollama"

# Shown in the dashboard; only Ollama is connectable today.
DISPLAY_PROVIDERS = [
    ("ollama", "Ollama"),
    ("aqwel", "Aqwel AI"),
    ("openai", "OpenAI"),
    ("deepseek", "DeepSeek"),
    ("gemini", "Gemini"),
    ("anthropic", "Anthropic"),
    ("groq", "Groq"),
]

COMING_SOON_PROVIDERS = frozenset(
    pid for pid, _ in DISPLAY_PROVIDERS if pid != AGENT_PROVIDER
)


def provider_display_name(provider_id: str) -> str:
    for pid, label in DISPLAY_PROVIDERS:
        if pid == provider_id:
            return label
    return provider_id.replace("_", " ").title()


def is_provider_available(provider_id: str) -> bool:
    return provider_id == AGENT_PROVIDER


CODING_AGENT_PROMPT = """You are Aion, a helpful coding assistant with optional filesystem tools.

For conversation (greetings, questions, explanations): answer clearly in natural language.
Do not call tools unless the user asks to inspect or change files.

When the user wants code changes:
- Use tools (read_file, list_files, grep, write_file, edit_file, etc.) — never tell them to run commands manually.
- Use paths relative to the workspace only (never invent absolute paths).
- read_file before edit_file; list_files/grep/glob to explore when unsure.

After tool work, summarize what changed."""


def mode_key(choice: int) -> str:
    return {1: "ollama", 2: "offline", 3: "help"}.get(choice, "ollama")
