"""Specialized agent presets and role definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .multi import AgentRole
from .react import ReActAgent


SKILL_PROMPTS: Dict[str, str] = {
    "general": "You are a capable general-purpose autonomous agent.",
    "code": "You are a senior software engineer. Prefer concrete code changes and verification.",
    "debug": "You are a debugging agent. Isolate root causes and validate fixes.",
    "data": "You are a data-science agent. Focus on datasets, analysis, and reproducibility.",
    "research": "You are a research agent. Gather evidence and summarize findings clearly.",
    "docs": "You are a documentation agent. Produce clear, accurate developer-facing docs.",
    "physics": "You are a physics agent. Prefer quantitative reasoning and the physics toolkit.",
}


def build_specialist_role(name: str, description: Optional[str] = None) -> AgentRole:
    """Build one specialist role from the built-in prompt catalog."""
    prompt = SKILL_PROMPTS.get(name, SKILL_PROMPTS["general"])
    return AgentRole(name=name, description=description or f"{name} specialist", system_prompt=prompt)


def create_specialist_agent(
    name: str,
    *,
    provider: Any,
    registry: Any,
    tools: List[Dict[str, Any]],
) -> ReActAgent:
    """Instantiate a ready-to-run specialist ReAct agent."""
    return ReActAgent(
        provider=provider,
        registry=registry,
        tools=tools,
        system_prompt=SKILL_PROMPTS.get(name, SKILL_PROMPTS["general"]),
    )
