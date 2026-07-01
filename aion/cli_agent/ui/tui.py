"""Modern terminal UI controller for the Aion agent."""

from __future__ import annotations

from typing import Any

from .console import clear_screen
from .panels import render_list_panel, render_runtime_dashboard
from .style import dim


class ModernTerminalUI:
    """Render a clean modern dashboard and runtime panels in the terminal."""

    def __init__(self, *, version: str, workspace: str) -> None:
        self.version = version
        self.workspace = workspace

    def draw_dashboard(self, *, session: Any, runtime: Any) -> None:
        """Clear the screen and render the main dashboard."""
        clear_screen()
        print()
        for line in render_runtime_dashboard(
            session=session,
            runtime=runtime,
            version=self.version,
            workspace=self.workspace,
        ):
            print(line)
        print()

    def show_jobs(self, runtime: Any) -> None:
        """Render tracked runtime jobs."""
        jobs = getattr(runtime.state, "jobs", [])
        print()
        print(render_list_panel("Jobs", [f"{j['job_id']}  {j['status']}  {j['task']}" for j in jobs]))
        print()

    def show_artifacts(self, runtime: Any) -> None:
        """Render tracked artifacts."""
        artifacts = getattr(runtime.state, "artifacts", [])
        print()
        print(render_list_panel("Artifacts", [f"{a['kind']}  {a['path']}  {a.get('description', '')}".strip() for a in artifacts]))
        print()

    def show_trace(self, runtime: Any, limit: int = 20) -> None:
        """Render recent runtime trace events."""
        trace = getattr(runtime.state, "trace", [])[-limit:]
        print()
        print(render_list_panel("Trace", [f"{item.get('type', '?')}  {item}" for item in trace]))
        print()

    def show_session(self, runtime: Any) -> None:
        """Render serialized session state."""
        state = runtime.state.to_dict()
        lines = [f"{key}: {value}" for key, value in state.items() if key not in {"jobs", "artifacts", "trace"}]
        print()
        print(render_list_panel("Session", lines))
        print(dim("  use /jobs, /artifacts, or /trace for detailed runtime state"))
        print()
