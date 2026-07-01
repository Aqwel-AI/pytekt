"""Self-review helpers for agent outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CritiqueResult:
    """Structured critique for one draft answer or tool result."""

    approved: bool
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class SelfReviewAgent:
    """A lightweight critic that can use heuristics or an LLM provider."""

    def __init__(self, provider: Optional[Any] = None) -> None:
        self.provider = provider

    def review(
        self,
        draft: str,
        *,
        task: str = "",
        tool_history: Optional[List[Dict[str, Any]]] = None,
        require_tool_use: bool = False,
    ) -> CritiqueResult:
        """Review a draft answer and return a structured critique."""
        issues: List[str] = []
        suggestions: List[str] = []
        if not draft.strip():
            issues.append("empty_output")
            suggestions.append("Produce a concrete final answer.")
        if require_tool_use and not tool_history:
            issues.append("missing_tool_use")
            suggestions.append("Use an appropriate tool before finalizing.")
        if task and draft.strip().casefold() == task.strip().casefold():
            issues.append("answer_repeats_task")
            suggestions.append("Answer the request instead of repeating it.")
        if "TODO" in draft or "placeholder" in draft.casefold():
            issues.append("unfinished_output")
            suggestions.append("Resolve placeholders before finalizing.")
        return CritiqueResult(approved=not issues, issues=issues, suggestions=suggestions)
