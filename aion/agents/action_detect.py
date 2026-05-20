"""Detect when the user expects filesystem / coding tool actions."""

from __future__ import annotations

import re

_ACTION_PATTERNS = re.compile(
    r"\b("
    r"create|make|add|write|edit|modify|update|delete|remove|"
    r"fix|implement|refactor|generate|save|"
    r"file|folder|directory|script|code|"
    r"run\s+test|pytest|npm|pip\s+install"
    r")\b",
    re.IGNORECASE,
)

_INSTRUCTION_ONLY = re.compile(
    r"\b(run this|execute|paste|copy this|type this|in your terminal|yourself)\b",
    re.IGNORECASE,
)


def needs_tool_action(user_input: str) -> bool:
    text = user_input.strip()
    if len(text) < 4:
        return False
    return bool(_ACTION_PATTERNS.search(text))


def looks_like_instructions_only(assistant_text: str) -> bool:
    if not assistant_text:
        return False
    t = assistant_text.lower()
    if "```" in t and ("shell" in t or "python" in t or "bash" in t):
        return True
    if "echo " in t and ">" in t:
        return True
    if _INSTRUCTION_ONLY.search(assistant_text):
        return True
    if "simulat" in t and "environment" in t:
        return True
    return False
