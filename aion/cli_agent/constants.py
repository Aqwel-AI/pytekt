"""Agent CLI constants."""

from __future__ import annotations

from typing import Optional

AGENT_MODES = [
    "🦙  Local AI (Ollama)",
    "📴  Offline (disconnect)",
    "📖  Show Help Catalog",
]

AGENT_PROVIDER = "ollama"

# Shown in the dashboard; connectable providers can be used via /connect.
DISPLAY_PROVIDERS = [
    ("ollama", "Ollama"),
    ("nvidia", "Nvidia"),
    ("openai", "OpenAI"),
    ("anthropic", "Anthropic"),
    ("gemini", "Gemini"),
    ("deepseek", "DeepSeek"),
]

# Providers available via /connect (API key or local).
CONNECTABLE_PROVIDERS = frozenset({
    "ollama",
    "nvidia",
    "openai",
    "anthropic",
    "gemini",
    "deepseek",
})

PROVIDER_ENV_VARS = {
    "nvidia": "NVIDIA_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}

COMING_SOON_PROVIDERS = frozenset(
    pid for pid, _ in DISPLAY_PROVIDERS if pid not in CONNECTABLE_PROVIDERS
)

INTERACTION_MODES = ("plain", "agent", "debug", "plan", "review", "test")
DEFAULT_INTERACTION_MODE = "agent"
SAFETY_MODES = ("read-only", "workspace-write", "full-trusted", "shell-disabled", "network-disabled")
SPECIALIST_MODES = ("general", "code", "debug", "review", "research", "docs", "physics", "data")

INTERACTION_MODE_LABELS = {
    "plain": "Plain (chat only)",
    "agent": "Agent (tools when needed)",
    "debug": "Debug (verbose tools)",
    "plan": "Plan (plan then execute)",
    "review": "Review (read-only critique)",
    "test": "Test (auto-run tests after edits)",
}


def normalize_interaction_mode(name: str) -> Optional[str]:
    key = name.lower().strip()
    if key in INTERACTION_MODES:
        return key
    for mode in INTERACTION_MODES:
        if key.startswith(mode):
            return mode
    return None


def normalize_safety_mode(name: str) -> Optional[str]:
    key = name.lower().strip()
    if key in SAFETY_MODES:
        return key
    return None


def normalize_specialist_mode(name: str) -> Optional[str]:
    key = name.lower().strip()
    if key in SPECIALIST_MODES:
        return key
    return None


def provider_display_name(provider_id: str) -> str:
    for pid, label in DISPLAY_PROVIDERS:
        if pid == provider_id:
            return label
    return provider_id.replace("_", " ").title()


def is_provider_available(provider_id: str) -> bool:
    return provider_id in CONNECTABLE_PROVIDERS


CODING_AGENT_PROMPT = """You are Aion, a helpful coding assistant with optional filesystem tools.

For conversation (greetings, questions, explanations): answer clearly in natural language.
Do not call tools unless the user asks to inspect or change files.

When the user wants code changes:
- Use tools (read_file, list_files, grep, write_file, edit_file, etc.) — never tell them to run commands manually.
- Use paths relative to the workspace only (never invent absolute paths).
- read_file before edit_file; list_files/grep/glob to explore when unsure.

When the user attaches files or folders with @path in their message, that content is already
in the message — do not call read_file again unless they need a fresher version.

After tool work, summarize what changed."""


def mode_key(choice: int) -> str:
    return {1: "ollama", 2: "offline", 3: "help"}.get(choice, "ollama")
