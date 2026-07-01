"""Shared event bus for agent runtimes and UIs."""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentEvent:
    """One runtime event emitted by the agent system."""

    type: str
    data: Dict[str, Any]
    ts: float = field(default_factory=time.time)


class AgentEventBus:
    """Thread-safe in-process event bus with replayable history."""

    def __init__(self, maxlen: int = 500) -> None:
        self._maxlen = maxlen
        self._history: List[AgentEvent] = []
        self._subscribers: List[queue.Queue[AgentEvent]] = []
        self._lock = threading.Lock()

    def publish(self, event_type: str, **data: Any) -> AgentEvent:
        """Publish an event to history and subscribers."""
        event = AgentEvent(type=event_type, data=data)
        with self._lock:
            self._history.append(event)
            if len(self._history) > self._maxlen:
                self._history = self._history[-self._maxlen :]
            subscribers = list(self._subscribers)
        for subscriber in subscribers:
            try:
                subscriber.put_nowait(event)
            except queue.Full:
                pass
        return event

    def recent(self, n: int = 50) -> List[AgentEvent]:
        """Return the most recent events."""
        with self._lock:
            return list(self._history[-n:])

    def subscribe(self) -> queue.Queue[AgentEvent]:
        """Subscribe to future events."""
        q: queue.Queue[AgentEvent] = queue.Queue(maxsize=200)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: queue.Queue[AgentEvent]) -> None:
        """Remove a subscriber queue."""
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)
