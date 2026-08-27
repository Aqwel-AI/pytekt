"""
Event-Loop Job Scheduler for PyTekt Bots.
Provides @bot.every("1h") and @bot.cron("0 9 * * *") recurring task decorators
running directly on the bot event loop without third-party dependencies.
"""

from __future__ import annotations

import asyncio
import datetime
import inspect
import logging
import re
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

if TYPE_CHECKING:
    from .base import Bot

logger = logging.getLogger("pytekt.bots.scheduler")


def parse_interval_seconds(interval: Union[str, int, float]) -> float:
    """Parse human interval string like '30s', '15m', '2h', '1d' into seconds."""
    if isinstance(interval, (int, float)):
        return max(0.1, float(interval))

    s = str(interval).strip().lower()
    if not s:
        return 60.0

    match = re.match(r"^([\d\.]+)\s*([a-z]*)$", s)
    if not match:
        try:
            return max(0.1, float(s))
        except ValueError:
            return 60.0

    num_str, unit = match.groups()
    val = float(num_str)

    if unit in ("s", "sec", "second", "seconds", ""):
        return val
    elif unit in ("m", "min", "minute", "minutes"):
        return val * 60.0
    elif unit in ("h", "hr", "hour", "hours"):
        return val * 3600.0
    elif unit in ("d", "day", "days"):
        return val * 86400.0
    elif unit in ("w", "week", "weeks"):
        return val * 604800.0

    return val


class CronMatcher:
    """Minimal 5-field cron expression evaluator."""

    def __init__(self, expr: str) -> None:
        self.raw_expr = expr.strip()
        parts = self.raw_expr.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression '{expr}'. Must have 5 fields: minute hour dom month dow")
        self.minute_field, self.hour_field, self.dom_field, self.month_field, self.dow_field = parts

    @staticmethod
    def _match_field(field_expr: str, value: int) -> bool:
        if field_expr == "*":
            return True
        if field_expr.startswith("*/"):
            try:
                step = int(field_expr[2:])
                return value % step == 0
            except ValueError:
                return False
        if "," in field_expr:
            subparts = field_expr.split(",")
            return any(CronMatcher._match_field(sp.strip(), value) for sp in subparts)
        if "-" in field_expr:
            try:
                low, high = map(int, field_expr.split("-"))
                return low <= value <= high
            except ValueError:
                return False
        try:
            return int(field_expr) == value
        except ValueError:
            return False

    def matches(self, dt: datetime.datetime) -> bool:
        """Check if datetime matches cron expression."""
        if not self._match_field(self.minute_field, dt.minute):
            return False
        if not self._match_field(self.hour_field, dt.hour):
            return False
        if not self._match_field(self.dom_field, dt.day):
            return False
        if not self._match_field(self.month_field, dt.month):
            return False
        # Python weekday: Monday is 0, Sunday is 6. Cron: Sunday is 0 or 7.
        cron_dow = (dt.weekday() + 1) % 7
        if not self._match_field(self.dow_field, cron_dow):
            return False
        return True


class ScheduledJob:
    """A registered scheduled recurring job."""

    def __init__(
        self,
        name: str,
        fn: Callable[..., Any],
        *,
        interval: Optional[float] = None,
        cron_expr: Optional[str] = None,
    ) -> None:
        self.name = name
        self.fn = fn
        self.interval = interval
        self.cron_matcher = CronMatcher(cron_expr) if cron_expr else None
        self.last_run: float = 0.0
        self.last_cron_minute: Optional[int] = None

    async def execute(self, bot: Bot) -> Any:
        """Run job with error containment."""
        try:
            sig = inspect.signature(self.fn)
            if len(sig.parameters) > 0:
                res = self.fn(bot)
            else:
                res = self.fn()
            if inspect.iscoroutine(res):
                return await res
            return res
        except Exception as e:
            logger.error("Error executing scheduled job '%s': %s", self.name, e, exc_info=True)


class Scheduler:
    """Manages periodic and cron-scheduled background tasks."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.jobs: List[ScheduledJob] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def add_interval_job(self, interval: Union[str, int, float], fn: Callable[..., Any]) -> ScheduledJob:
        sec = parse_interval_seconds(interval)
        job = ScheduledJob(name=fn.__name__, fn=fn, interval=sec)
        self.jobs.append(job)
        return job

    def add_cron_job(self, cron_expr: str, fn: Callable[..., Any]) -> ScheduledJob:
        job = ScheduledJob(name=fn.__name__, fn=fn, cron_expr=cron_expr)
        self.jobs.append(job)
        return job

    async def run_loop(self) -> None:
        """Background runner checking job schedules."""
        self._running = True
        logger.info("Bot scheduler started with %d registered job(s)", len(self.jobs))

        while self._running:
            now = time.time()
            now_dt = datetime.datetime.now()

            for job in self.jobs:
                if not self._running:
                    break

                # 1. Interval Check
                if job.interval is not None:
                    if job.last_run == 0.0 or (now - job.last_run) >= job.interval:
                        job.last_run = now
                        asyncio.create_task(job.execute(self.bot))

                # 2. Cron Check
                elif job.cron_matcher is not None:
                    curr_min = now_dt.minute
                    if job.last_cron_minute != curr_min and job.cron_matcher.matches(now_dt):
                        job.last_cron_minute = curr_min
                        job.last_run = now
                        asyncio.create_task(job.execute(self.bot))

            await asyncio.sleep(1.0)

    def start(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> Optional[asyncio.Task]:
        """Start scheduler as an asyncio Task if event loop is active."""
        try:
            running_loop = loop or asyncio.get_running_loop()
            if self._task is None or self._task.done():
                self._task = running_loop.create_task(self.run_loop())
            return self._task
        except RuntimeError:
            # Event loop not running yet; bot.run() will start or caller starts when loop active
            return None

    def stop(self) -> None:
        """Stop scheduler."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
