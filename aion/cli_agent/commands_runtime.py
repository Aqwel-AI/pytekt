"""Runtime slash commands for the modern terminal agent UI."""

from __future__ import annotations

from typing import Any, Optional


def handle_runtime_command(
    text: str,
    *,
    runtime: Any,
    tui: Any,
) -> Optional[str]:
    """Handle runtime-specific slash commands. Return None when handled."""
    if not text.startswith("/"):
        return "chat"

    parts = text[1:].split(maxsplit=1)
    cmd = parts[0].lower()

    if cmd == "jobs":
        tui.show_jobs(runtime)
        return None
    if cmd == "artifacts":
        tui.show_artifacts(runtime)
        return None
    if cmd == "trace":
        tui.show_trace(runtime)
        return None
    if cmd == "session":
        tui.show_session(runtime)
        return None
    if cmd == "resume":
        restored = runtime.resume_latest()
        if restored is not None:
            tui.show_session(runtime)
        return None
    if cmd == "bg-test":
        info = getattr(runtime.connector.session, "project_info", None)
        if info and info.test_command:
            runtime.submit_background(
                f"test: {info.test_command}",
                lambda: runtime.connector.registry.call("run_command", '{"command": "%s", "timeout": 120}' % info.test_command.replace('"', '\\"')),
            )
            tui.show_jobs(runtime)
        return None
    return "unhandled"
