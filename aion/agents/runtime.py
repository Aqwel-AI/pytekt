"""Modern shared runtime for terminal and web agent sessions."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from .artifacts import ArtifactTracker
from .events import AgentEventBus
from .jobs import BackgroundJobQueue
from .session import RuntimeSession


class AgentRuntime:
    """Coordinate one agent session, its events, artifacts, jobs, and persistence."""

    def __init__(self, *, workspace_root: str, connector: Any) -> None:
        self.workspace_root = workspace_root
        self.connector = connector
        session_id = getattr(connector.session, "session_id", "") or uuid.uuid4().hex[:10]
        self.state = RuntimeSession(session_id=session_id, cwd=workspace_root)
        self.events = AgentEventBus()
        self.artifacts = ArtifactTracker()
        self.session_dir = Path(workspace_root) / ".aion" / "sessions"
        self.job_queue = BackgroundJobQueue()
        self.connector.set_event_callback(self.on_connector_event)

    def on_connector_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Receive connector events and mirror them into runtime state."""
        self.state.add_trace(event_type, **data)
        if event_type == "tool_step":
            action = data.get("action", "")
            result = str(data.get("result", ""))
            if action in {"write_file", "edit_file"}:
                for line in result.splitlines():
                    if line.startswith("Wrote ") or line.startswith("Edited "):
                        parts = line.split()
                        if len(parts) >= 2:
                            path = parts[1].rstrip(".")
                            self.artifacts.add(path, "file", f"{action} output")
                            self.state.add_artifact(path, "file", f"{action} output")
        elif event_type == "chat_status":
            self.state.current_status = str(data.get("text", self.state.current_status))
        elif event_type == "edit_intent":
            intent = data.get("intent") or {}
            for path in intent.get("paths", []):
                self.artifacts.add(path, "file", "edit intent output")
                self.state.add_artifact(path, "file", "edit intent output")
        self.events.publish(event_type, **data)

    def connect_state(self) -> None:
        """Refresh provider/model from the connector session."""
        self.state.provider = self.connector.session.provider
        self.state.model = self.connector.session.model
        self.state.current_status = "connected" if self.connector.session.connected else "offline"

    def run_prompt(self, text: str) -> str:
        """Run one prompt through the connector and persist runtime state."""
        self.connect_state()
        job_id = uuid.uuid4().hex[:8]
        self.state.current_task = text
        self.state.current_status = "running"
        self.state.add_job(job_id, text, status="running")
        self.events.publish("job_started", job_id=job_id, task=text)
        try:
            response = self.connector.chat(text)
            self.state.update_job(job_id, status="done", result=response[:500])
            self.state.current_status = "idle"
            self.events.publish("job_completed", job_id=job_id, response=response)
            self.save()
            return response
        except Exception as exc:  # noqa: BLE001
            self.state.update_job(job_id, status="failed", result=str(exc))
            self.state.current_status = "failed"
            self.events.publish("job_failed", job_id=job_id, error=str(exc))
            self.save()
            raise

    def run_plain_stream(self, text: str) -> Iterator[str]:
        """Stream a plain-mode prompt when the underlying provider supports it."""
        self.connect_state()
        inner = getattr(self.connector._raw_provider, "_inner", self.connector._raw_provider)
        if not hasattr(inner, "complete_stream"):
            yield self.run_prompt(text)
            return

        from ..providers.base import ChatMessage

        job_id = uuid.uuid4().hex[:8]
        self.state.current_task = text
        self.state.current_status = "streaming"
        self.state.add_job(job_id, text, status="running")
        self.events.publish("job_started", job_id=job_id, task=text)

        parts: List[str] = []
        for token in inner.complete_stream([ChatMessage(role="user", content=text)], max_tokens=4096):
            parts.append(token)
            self.events.publish("chat_token", text=token, job_id=job_id)
            yield token

        response = "".join(parts)
        if self.connector.agent:
            self.connector.agent.memory.add({"role": "user", "content": text})
            self.connector.agent.memory.add({"role": "assistant", "content": response})
        self.state.update_job(job_id, status="done", result=response[:500])
        self.state.current_status = "idle"
        self.events.publish("job_completed", job_id=job_id, response=response)
        self.save()

    def save(self) -> Path:
        """Persist the runtime session into the workspace."""
        background_jobs = [job.__dict__.copy() for job in self.job_queue.list_jobs()]
        indexed = {job["job_id"]: job for job in self.state.jobs if "job_id" in job}
        for job in background_jobs:
            indexed[job["job_id"]] = job
        self.state.jobs = list(indexed.values())
        return self.state.save(self.session_dir / f"{self.state.session_id}.json")

    def resume_latest(self) -> Optional[RuntimeSession]:
        """Load the latest saved session from the workspace if one exists."""
        if not self.session_dir.exists():
            return None
        sessions = sorted(self.session_dir.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
        if not sessions:
            return None
        self.state = RuntimeSession.load(sessions[0])
        return self.state

    def submit_background(self, title: str, fn) -> str:
        """Submit a background job and mirror it into the runtime state."""
        job_id = self.job_queue.submit(title, fn)
        self.state.add_job(job_id, title, status="queued")
        self.events.publish("job_queued", job_id=job_id, title=title)
        self.save()
        return job_id
