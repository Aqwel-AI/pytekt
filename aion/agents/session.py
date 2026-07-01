"""Persistent agent session model for terminal and web runtimes."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


PathLike = Union[str, Path]


@dataclass
class RuntimeSession:
    """Persistent runtime session for one terminal agent conversation."""

    session_id: str
    provider: Optional[str] = None
    model: Optional[str] = None
    cwd: str = "."
    current_task: str = ""
    current_status: str = "idle"
    token_usage: int = 0
    jobs: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    trace: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_job(self, job_id: str, task: str, status: str = "queued") -> None:
        """Track one runtime job."""
        self.jobs.append({"job_id": job_id, "task": task, "status": status})

    def update_job(self, job_id: str, *, status: Optional[str] = None, result: Optional[str] = None) -> None:
        """Update one tracked job."""
        for job in self.jobs:
            if job["job_id"] == job_id:
                if status is not None:
                    job["status"] = status
                if result is not None:
                    job["result"] = result
                return

    def add_artifact(self, path: str, kind: str, description: str = "") -> None:
        """Track one generated artifact."""
        self.artifacts.append({"path": path, "kind": kind, "description": description})

    def add_trace(self, event_type: str, **data: Any) -> None:
        """Append one trace event."""
        self.trace.append({"type": event_type, **data})

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this session."""
        return asdict(self)

    def save(self, path: PathLike) -> Path:
        """Write the session to disk as JSON."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: PathLike) -> "RuntimeSession":
        """Load a session from disk."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**data)
