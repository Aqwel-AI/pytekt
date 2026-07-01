from __future__ import annotations

from pathlib import Path

import aion
from aion.cli_agent import ui
from aion.cli_agent.commands_runtime import handle_runtime_command


class DummyConnector:
    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = workspace_root
        self.session = ui.AgentSession(
            mode="offline",
            interaction_mode="agent",
            provider="ollama",
            model="llama3",
            connected=True,
            is_trusted=True,
            session_id="sess123",
        )
        self._callback = None
        self._raw_provider = None
        self.agent = None

    def set_event_callback(self, callback):
        self._callback = callback

    def chat(self, text: str) -> str:
        if self._callback:
            self._callback("tool_step", {"action": "write_file", "result": "Wrote output.txt."})
        return f"answer: {text}"


class DummyTUI:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def show_jobs(self, runtime):
        self.calls.append("jobs")

    def show_artifacts(self, runtime):
        self.calls.append("artifacts")

    def show_trace(self, runtime, limit: int = 20):
        self.calls.append("trace")

    def show_session(self, runtime):
        self.calls.append("session")


def test_runtime_tracks_jobs_artifacts_and_session(tmp_path):
    connector = DummyConnector(str(tmp_path))
    runtime = aion.agents.AgentRuntime(workspace_root=str(tmp_path), connector=connector)

    response = runtime.run_prompt("create a file")

    assert response == "answer: create a file"
    assert runtime.state.jobs[0]["status"] == "done"
    assert runtime.state.artifacts[0]["path"] == "output.txt"
    saved = tmp_path / ".aion" / "sessions" / "sess123.json"
    assert saved.exists()


def test_runtime_resume_latest(tmp_path):
    connector = DummyConnector(str(tmp_path))
    runtime = aion.agents.AgentRuntime(workspace_root=str(tmp_path), connector=connector)
    runtime.state.current_task = "debug build"
    runtime.save()

    restored = runtime.resume_latest()
    assert restored is not None
    assert restored.current_task == "debug build"


def test_render_runtime_dashboard(tmp_path):
    connector = DummyConnector(str(tmp_path))
    runtime = aion.agents.AgentRuntime(workspace_root=str(tmp_path), connector=connector)
    runtime.state.current_task = "Investigate failing tests"
    lines = ui.render_runtime_dashboard(
        session=connector.session,
        runtime=runtime,
        version="0.2.0",
        workspace=str(tmp_path),
    )
    rendered = "\n".join(lines)
    assert "Modern Agent Terminal" in rendered
    assert "Investigate failing tests" in rendered
    assert "/jobs" in rendered


def test_runtime_slash_commands(tmp_path):
    connector = DummyConnector(str(tmp_path))
    runtime = aion.agents.AgentRuntime(workspace_root=str(tmp_path), connector=connector)
    tui = DummyTUI()
    runtime.save()

    assert handle_runtime_command("/jobs", runtime=runtime, tui=tui) is None
    assert handle_runtime_command("/artifacts", runtime=runtime, tui=tui) is None
    assert handle_runtime_command("/trace", runtime=runtime, tui=tui) is None
    assert handle_runtime_command("/session", runtime=runtime, tui=tui) is None
    assert handle_runtime_command("/resume", runtime=runtime, tui=tui) is None
    assert tui.calls == ["jobs", "artifacts", "trace", "session", "session"]
