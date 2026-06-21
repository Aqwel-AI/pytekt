"""In-memory event bus for agent web SSE."""

from __future__ import annotations

import json
import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional


@dataclass
class AgentEvent:
    type: str
    data: Dict[str, Any]
    ts: float = field(default_factory=time.time)

    def to_sse(self) -> str:
        payload = {"type": self.type, **self.data, "ts": self.ts}
        return f"data: {json.dumps(payload, default=str)}\n\n"


class EventBus:
    """Thread-safe pub/sub for web clients."""

    def __init__(self, maxlen: int = 500) -> None:
        self._subscribers: List[queue.Queue[AgentEvent]] = []
        self._history: List[AgentEvent] = []
        self._maxlen = maxlen
        self._lock = threading.Lock()

    def publish(self, event_type: str, **data: Any) -> None:
        event = AgentEvent(type=event_type, data=data)
        with self._lock:
            self._history.append(event)
            if len(self._history) > self._maxlen:
                self._history = self._history[-self._maxlen :]
            subs = list(self._subscribers)
        for q in subs:
            try:
                q.put_nowait(event)
            except queue.Full:
                pass

    def subscribe(self) -> queue.Queue[AgentEvent]:
        q: queue.Queue[AgentEvent] = queue.Queue(maxsize=200)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: queue.Queue[AgentEvent]) -> None:
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    def recent(self, n: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {"type": e.type, **e.data, "ts": e.ts}
                for e in self._history[-n:]
            ]

    def iter_sse(self, q: queue.Queue[AgentEvent], timeout: float = 30.0) -> Iterator[str]:
        while True:
            try:
                event = q.get(timeout=timeout)
                yield event.to_sse()
            except queue.Empty:
                yield f": keepalive {time.time()}\n\n"
