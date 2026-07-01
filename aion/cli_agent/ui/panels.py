"""Modern terminal panels for the interactive agent UI."""

from __future__ import annotations

import os
from typing import Any, Iterable, List

from .style import accent, accent_muted, bold, dim, pad_visible
from .theme import section_title, status_chip

BOX_WIDTH = 92
INNER = BOX_WIDTH - 2


def _line(content: str = "") -> str:
    return accent("│") + pad_visible(content, INNER) + accent("│")


def _rule() -> str:
    return accent("├" + "─" * INNER + "┤")


def render_runtime_dashboard(*, session: Any, runtime: Any, version: str, workspace: str) -> List[str]:
    """Render a modern dashboard view for the terminal agent."""
    cwd = workspace.replace(os.path.expanduser("~"), "~")
    if len(cwd) > INNER - 10:
        cwd = "…" + cwd[-(INNER - 11) :]

    runtime_state = getattr(runtime, "state", None)
    current_status = getattr(runtime_state, "current_status", "idle")
    current_task = getattr(runtime_state, "current_task", "") or "No active task"
    jobs = len(getattr(runtime_state, "jobs", [])) if runtime_state else 0
    artifacts = len(getattr(runtime_state, "artifacts", [])) if runtime_state else 0

    tone = "good" if session.connected else "warn"
    provider = session.provider or "offline"
    model = session.model or "—"
    mode = session.interaction_mode
    safety = getattr(session, "safety_mode", "workspace-write")
    role = getattr(session, "specialist_mode", "general")

    lines = [
        accent("┌" + "─" * INNER + "┐"),
        _line(f"{bold('AION')} {accent_muted('· Modern Agent Terminal')} {dim('v' + version)}"),
        _rule(),
        _line(
            " ".join(
                [
                    status_chip("provider", provider, tone=tone),
                    status_chip("model", model, tone="info"),
                    status_chip("mode", mode, tone="active"),
                    status_chip("role", role, tone="info"),
                    status_chip("safety", safety, tone="warn" if safety != "full-trusted" else "good"),
                    status_chip("status", current_status, tone="active" if current_status not in {"failed", "offline"} else "error"),
                ]
            )
        ),
        _line(f"{dim('workspace')} {cwd}"),
        _line(f"{dim('task')} {current_task[:INNER - 7]}"),
        _line(f"{dim('jobs')} {jobs}   {dim('artifacts')} {artifacts}   {dim('trust')} {'on' if session.is_trusted else 'off'}"),
        _rule(),
        _line(section_title("Recent Activity")),
    ]

    activity_text = session.activity.format_dashboard(6) if hasattr(session, "activity") else "No recent activity"
    for item in activity_text.splitlines():
        lines.append(_line(f"  {item.strip()}"))

    lines.extend(
        [
            _rule(),
            _line(section_title("Command Palette")),
            _line("  /connect ollama   /connect nvidia   /mode agent|plain|debug"),
            _line("  /jobs   /artifacts   /trace   /session   /resume   /diff   /revert"),
            _line("  /safety <mode>   /role <mode>   /validate   /bg-test"),
            accent("└" + "─" * INNER + "┘"),
        ]
    )
    return lines


def render_list_panel(title: str, items: Iterable[str]) -> str:
    """Render a titled plain-text panel for command outputs."""
    rendered = [section_title(title)]
    items_list = list(items)
    if not items_list:
        rendered.append(dim("  empty"))
    else:
        rendered.extend(f"  {item}" for item in items_list)
    return "\n".join(rendered)
