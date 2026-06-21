"""Session activity ring buffer for dashboard and /status."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, List, Optional


@dataclass
class ActivityEvent:
    kind: str  # tool | chat | connect | pin | tokens
    detail: str
    ts: str = field(default_factory=lambda: datetime.now().strftime("%H:%M"))

    def format_line(self) -> str:
        return f"{self.ts} {self.kind}: {self.detail}"


class ActivityFeed:
    """Fixed-size activity log attached to a session."""

    def __init__(self, maxlen: int = 50) -> None:
        self._events: Deque[ActivityEvent] = deque(maxlen=maxlen)

    def log(self, kind: str, detail: str) -> None:
        preview = detail if len(detail) <= 120 else detail[:117] + "…"
        self._events.append(ActivityEvent(kind=kind, detail=preview))

    def log_tool(self, name: str, preview: str) -> None:
        self.log("tool", f"{name} — {preview}")

    def log_tokens(self, count: Optional[int]) -> None:
        if count is not None:
            self.log("tokens", f"{count} tokens")

    def recent(self, n: int = 5) -> List[ActivityEvent]:
        return list(self._events)[-n:]

    def format_dashboard(self, n: int = 5) -> str:
        events = self.recent(n)
        if not events:
            return "No recent activity"
        return "\n".join(f"  {e.format_line()}" for e in events)
