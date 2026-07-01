"""Background jobs for long-running agent tasks."""

from __future__ import annotations

import queue
import threading
import uuid
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


JobFn = Callable[[], str]


@dataclass
class BackgroundJob:
    job_id: str
    title: str
    status: str = "queued"
    result: str = ""
    logs: List[str] = field(default_factory=list)


class BackgroundJobQueue:
    """Small threaded background job queue with resumable in-memory state."""

    def __init__(self) -> None:
        self._jobs: Dict[str, BackgroundJob] = {}
        self._queue: "queue.Queue[tuple[str, JobFn]]" = queue.Queue()
        self._worker = threading.Thread(target=self._run, daemon=True, name="aion-bg-jobs")
        self._started = False

    def start(self) -> None:
        if not self._started:
            self._worker.start()
            self._started = True

    def submit(self, title: str, fn: JobFn) -> str:
        self.start()
        job_id = uuid.uuid4().hex[:8]
        self._jobs[job_id] = BackgroundJob(job_id=job_id, title=title)
        self._queue.put((job_id, fn))
        return job_id

    def _run(self) -> None:
        while True:
            job_id, fn = self._queue.get()
            job = self._jobs[job_id]
            job.status = "running"
            try:
                job.result = fn()
                job.status = "done"
            except Exception as exc:  # noqa: BLE001
                job.result = str(exc)
                job.status = "failed"

    def list_jobs(self) -> List[BackgroundJob]:
        return list(self._jobs.values())

    def get(self, job_id: str) -> Optional[BackgroundJob]:
        return self._jobs.get(job_id)
