"""Session state display: mode, provider, model, trust, tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set

from ..activity import ActivityFeed
from ..project import ProjectInfo

from .console import divider
from .style import (
    ICON_CHAT,
    ICON_CODE,
    ICON_GLOBE,
    ICON_OFFLINE,
    ICON_OLLAMA,
    ICON_THINK,
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

    mode: str = "offline"  # offline | ollama | nvidia | …
    interaction_mode: str = "agent"  # plain | agent | debug
    provider: Optional[str] = None
    model: Optional[str] = None
    is_trusted: bool = False
    tools_enabled: bool = False
    connected: bool = False
    touched_files: Set[str] = field(default_factory=set)
    pinned_paths: List[str] = field(default_factory=list)
    activity: ActivityFeed = field(default_factory=ActivityFeed)
    project_info: Optional[ProjectInfo] = None
    force_tools: bool = False
    session_id: str = "default"
    pending_plan: bool = False

    @property
    def connection_label(self) -> str:
        if self.mode == "ollama":
            return f"{ICON_OLLAMA} Local (Ollama)"
        if self.mode == "nvidia":
            return f"{ICON_GLOBE} Nvidia NIM"
        return f"{ICON_OFFLINE} Offline"

    @property
    def mode_label(self) -> str:
        return self.connection_label

    @property
    def interaction_label(self) -> str:
        labels = {
            "plain": f"{ICON_CHAT} Plain",
            "agent": f"{ICON_CODE} Agent",
            "debug": f"{ICON_THINK} Debug",
            "plan": f"{ICON_THINK} Plan",
            "review": f"{ICON_CHAT} Review",
            "test": f"{ICON_CODE} Test",
        }
        return labels.get(self.interaction_mode, self.interaction_mode.title())

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
        if self.interaction_mode == "plain":
            return yellow(f"{ICON_CHAT} Chat only")
        if self.tools_enabled:
            return accent(f"{ICON_CODE} Tools ON")
        return yellow(f"{ICON_CHAT} Chat only")


def format_status_line(session: AgentSession) -> str:
    parts = [bold(session.interaction_label)]
    if session.connected and session.provider:
        parts.append(session.provider_label)
        if session.model:
            parts.append(accent_muted(session.model))
    parts.append(
        f"{ICON_TRUST} Trust: {accent('Yes') if session.is_trusted else red('No')}"
    )
    parts.append(session.tools_label)
    return "  " + dim("│ ").join(parts)


def format_session_summary(session: AgentSession) -> str:
    """Compact summary for dashboard SESSION row."""
    if session.connected and session.provider:
        prov = session.provider.replace("_", " ").title()
        model = session.model or ""
        conn = accent_muted(f"● {prov}") + (accent_muted(f" · {model}") if model else "")
    else:
        conn = accent_muted("○ Not connected")
    trust = accent("Yes") if session.is_trusted else red("No")
    tools = "ON" if session.tools_enabled and session.interaction_mode != "plain" else "OFF"
    return (
        f"{conn}\n"
        f"  {dim('Mode:')} {session.interaction_mode.title()}"
        f" {dim('· Trust:')} {trust}"
        f" {dim('· Tools:')} {tools}"
    )


def print_status_bar(session: AgentSession) -> None:
    print(format_status_line(session))


def print_session_footer() -> None:
    """Optional footer — kept empty (no command hints)."""
    pass


def spinner_label(session: AgentSession) -> str:
    if session.interaction_mode == "debug":
        return "Debug trace running..."
    if session.interaction_mode == "plain":
        return "Thinking..."
    if session.mode == "ollama":
        return "Thinking (Ollama)..."
    if session.mode == "nvidia":
        return "Thinking (Nvidia)..."
    if session.tools_enabled:
        return "Agent working..."
    return "Thinking..."
