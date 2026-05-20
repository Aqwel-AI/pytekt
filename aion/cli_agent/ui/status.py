"""Session state display: mode, provider, model, trust, tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .console import divider
from .style import (
    ICON_CHAT,
    ICON_CODE,
    ICON_GLOBE,
    ICON_OFFLINE,
    ICON_OLLAMA,
    ICON_TRUST,
    PROVIDER_ICONS,
    bold,
    accent,
    accent_muted,
    dim,
    red,
    yellow,
)


@dataclass
class AgentSession:
    """Current agent CLI session for the status bar."""

    mode: str = "offline"  # offline | cloud | ollama
    provider: Optional[str] = None
    model: Optional[str] = None
    is_trusted: bool = False
    tools_enabled: bool = False
    connected: bool = False

    @property
    def mode_label(self) -> str:
        if self.mode == "ollama":
            return f"{ICON_OLLAMA} Local (Ollama)"
        if self.mode == "cloud":
            return f"{ICON_GLOBE} Cloud AI"
        return f"{ICON_OFFLINE} Offline"

    @property
    def provider_label(self) -> str:
        if not self.provider:
            return "—"
        icon = PROVIDER_ICONS.get(self.provider.lower(), "•")
        return f"{icon} {self.provider.replace('_', ' ').title()}"

    @property
    def tools_label(self) -> str:
        if not self.connected:
            return dim("n/a")
        if self.tools_enabled:
            return accent(f"{ICON_CODE} Vibe Coding ON")
        return yellow(f"{ICON_CHAT} Chat only")


def format_status_line(session: AgentSession) -> str:
    parts = [bold(session.mode_label)]
    if session.connected and session.provider:
        parts.append(session.provider_label)
        if session.model:
            parts.append(accent_muted(session.model))
    parts.append(
        f"{ICON_TRUST} Trust: {accent('Yes') if session.is_trusted else red('No')}"
    )
    parts.append(session.tools_label)
    return "  " + dim("│ ").join(parts)


def print_status_bar(session: AgentSession) -> None:
    print(format_status_line(session))


def print_session_footer() -> None:
    """Optional footer — kept empty (no command hints)."""
    pass


def spinner_label(session: AgentSession) -> str:
    if session.mode == "ollama":
        return "Thinking (Ollama)..."
    if session.tools_enabled:
        return "Vibe Coding..."
    return "Thinking..."
