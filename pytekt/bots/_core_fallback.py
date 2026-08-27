"""
Pure-Python reference fallback for pytekt.bots._core components.
Used automatically when the C++ extension is not compiled or available.
"""

from __future__ import annotations

import collections
import http.server
import json
import re
import socketserver
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class UniversalEvent:
    """Platform-agnostic normalized event struct."""

    def __init__(
        self,
        id: str = "",
        chat_id: str = "",
        user_id: str = "",
        text: str = "",
        platform: str = "generic",
        event_type: str = "message",
        command: str = "",
        args: Optional[List[str]] = None,
        raw: str = "",
        metadata: Optional[Dict[str, str]] = None,
        timestamp: Optional[float] = None,
    ) -> None:
        self.id = id
        self.chat_id = chat_id
        self.user_id = user_id
        self.text = text
        self.platform = platform
        self.event_type = event_type
        self.command = command
        self.args: List[str] = list(args) if args is not None else []
        self.raw = raw
        self.metadata: Dict[str, str] = dict(metadata) if metadata is not None else {}
        self.timestamp = timestamp if timestamp is not None else time.time()

    def __repr__(self) -> str:
        return (
            f"<UniversalEvent id='{self.id}' platform='{self.platform}' "
            f"type='{self.event_type}' chat_id='{self.chat_id}' text='{self.text[:30]}'>"
        )


class Dispatcher:
    """Event router and parser matching C++ Dispatcher."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._commands: Dict[str, List[str]] = collections.defaultdict(list)
        self._patterns: List[Tuple[str, re.Pattern, str]] = []
        self._events: Dict[str, List[str]] = collections.defaultdict(list)
        self._states: Dict[str, List[str]] = collections.defaultdict(list)

    def add_command_handler(self, command: str, handler_id: str) -> None:
        with self._lock:
            cmd = command.lstrip("/!")
            self._commands[cmd].append(handler_id)

    def add_pattern_handler(self, pattern: str, handler_id: str) -> None:
        with self._lock:
            try:
                compiled = re.compile(pattern)
            except Exception:
                compiled = re.compile(re.escape(pattern))
            self._patterns.append((pattern, compiled, handler_id))

    def add_event_handler(self, event_type: str, handler_id: str) -> None:
        with self._lock:
            self._events[event_type].append(handler_id)

    def add_state_handler(self, state_name: str, handler_id: str) -> None:
        with self._lock:
            self._states[state_name].append(handler_id)

    @staticmethod
    def extract_command_and_args(text: str) -> Tuple[str, List[str]]:
        if not text:
            return "", []
        s = text.strip()
        if not s or s[0] not in ("/", "!"):
            return "", []
        parts = s.split()
        if not parts:
            return "", []
        cmd_part = parts[0][1:].split("@")[0]
        args = parts[1:]
        return cmd_part, args

    def match(self, event: UniversalEvent, current_state: str = "") -> List[str]:
        with self._lock:
            matched: List[str] = []

            # 1. State handlers
            if current_state and current_state in self._states:
                matched.extend(self._states[current_state])

            # 2. Command handlers
            if event.command and event.command in self._commands:
                matched.extend(self._commands[event.command])

            # 3. Pattern handlers
            if event.text:
                for _, regex, hid in self._patterns:
                    if regex.search(event.text):
                        matched.append(hid)

            # 4. Event type handlers
            if event.event_type and event.event_type in self._events:
                matched.extend(self._events[event.event_type])

            # 5. General message fallback
            if event.event_type != "message" and "message" in self._events:
                matched.extend(self._events["message"])

            # 6. Wildcard
            if "*" in self._events:
                matched.extend(self._events["*"])

            return matched

    def parse_telegram(self, json_str: str) -> UniversalEvent:
        ev = UniversalEvent(platform="telegram", raw=json_str)
        try:
            data = json.loads(json_str)
        except Exception:
            return ev

        ev.id = str(data.get("update_id", ""))
        msg = data.get("message") or data.get("edited_message") or data.get("channel_post")

        if "callback_query" in data:
            cb = data["callback_query"]
            ev.id = str(cb.get("id", ""))
            ev.event_type = "callback"
            ev.text = str(cb.get("data", ""))
            ev.user_id = str(cb.get("from", {}).get("id", ""))
            if "message" in cb:
                ev.chat_id = str(cb["message"].get("chat", {}).get("id", ""))
                ev.metadata["message_id"] = str(cb["message"].get("message_id", ""))
            return ev

        if not msg or not isinstance(msg, dict):
            return ev

        if "message_id" in msg:
            ev.id = str(msg["message_id"])
        if "chat" in msg:
            ev.chat_id = str(msg["chat"].get("id", ""))
        if "from" in msg:
            f = msg["from"]
            ev.user_id = str(f.get("id", ""))
            ev.metadata["username"] = str(f.get("username", ""))
            ev.metadata["first_name"] = str(f.get("first_name", ""))
            ev.metadata["last_name"] = str(f.get("last_name", ""))

        if "reply_to_message" in msg:
            ev.metadata["reply_to_message_id"] = str(msg["reply_to_message"].get("message_id", ""))

        ev.text = msg.get("text") or msg.get("caption") or ""

        if "voice" in msg:
            ev.event_type = "voice"
            ev.metadata["file_id"] = str(msg["voice"].get("file_id", ""))
            ev.metadata["duration"] = str(msg["voice"].get("duration", 0))
        elif "audio" in msg:
            ev.event_type = "voice"
            ev.metadata["file_id"] = str(msg["audio"].get("file_id", ""))
        elif "photo" in msg and isinstance(msg["photo"], list) and msg["photo"]:
            ev.event_type = "photo"
            largest = msg["photo"][-1]
            ev.metadata["file_id"] = str(largest.get("file_id", ""))
            ev.metadata["width"] = str(largest.get("width", 0))
            ev.metadata["height"] = str(largest.get("height", 0))

        if ev.text and ev.text[0] in ("/", "!"):
            cmd, args = self.extract_command_and_args(ev.text)
            if cmd:
                ev.command = cmd
                ev.args = args
                ev.event_type = "command"
        elif not ev.event_type or ev.event_type == "message":
            ev.event_type = "message"

        return ev

    def parse_discord(self, json_str: str) -> UniversalEvent:
        ev = UniversalEvent(platform="discord", raw=json_str)
        try:
            data = json.loads(json_str)
        except Exception:
            return ev

        payload = data.get("d", data)
        ev.id = str(payload.get("id", ""))
        ev.chat_id = str(payload.get("channel_id", ""))
        if "guild_id" in payload:
            ev.metadata["guild_id"] = str(payload["guild_id"])
        if "author" in payload:
            ev.user_id = str(payload["author"].get("id", ""))
            ev.metadata["username"] = str(payload["author"].get("username", ""))

        ev.text = payload.get("content", "")

        if "attachments" in payload and isinstance(payload["attachments"], list):
            for att in payload["attachments"]:
                ct = att.get("content_type", "")
                if "image/" in ct:
                    ev.event_type = "photo"
                    ev.metadata["url"] = str(att.get("url", ""))
                    ev.metadata["file_id"] = str(att.get("id", ""))
                    break
                elif "audio/" in ct:
                    ev.event_type = "voice"
                    ev.metadata["url"] = str(att.get("url", ""))
                    ev.metadata["file_id"] = str(att.get("id", ""))
                    break

        if data.get("t") == "INTERACTION_CREATE" or payload.get("type") == 2:
            ev.event_type = "interaction"
            idata = payload.get("data", {})
            if "name" in idata:
                ev.command = str(idata["name"])
                ev.event_type = "command"
                if "options" in idata and isinstance(idata["options"], list):
                    ev.args = [str(opt.get("value", "")) for opt in idata["options"]]

        if ev.text and ev.text[0] in ("/", "!"):
            cmd, args = self.extract_command_and_args(ev.text)
            if cmd:
                ev.command = cmd
                ev.args = args
                ev.event_type = "command"
        elif not ev.event_type or ev.event_type == "message":
            ev.event_type = "message"

        return ev

    def parse_generic(self, json_str: str, platform: str = "generic") -> UniversalEvent:
        ev = UniversalEvent(platform=platform, raw=json_str)
        try:
            data = json.loads(json_str)
        except Exception:
            return ev

        ev.id = str(data.get("id", ""))
        ev.chat_id = str(data.get("chat_id", ""))
        ev.user_id = str(data.get("user_id", ""))
        ev.text = str(data.get("text") or data.get("content") or "")
        ev.event_type = str(data.get("event_type", "message"))

        if "command" in data:
            ev.command = str(data["command"])

        if ev.text and ev.text[0] in ("/", "!") and not ev.command:
            cmd, args = self.extract_command_and_args(ev.text)
            if cmd:
                ev.command = cmd
                ev.args = args
                ev.event_type = "command"

        return ev


class RateLimiter:
    """In-memory token bucket rate limiter matching C++ RateLimiter."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._default_rules: Dict[str, Tuple[float, float, float]] = {}  # capacity, window, refill_rate
        self._buckets: Dict[str, Dict[str, float]] = {}  # tokens, capacity, refill_rate, last_refill, backoff_until

    @staticmethod
    def parse_rate(rate_str: str) -> Tuple[bool, float, float]:
        if not rate_str:
            return False, 1.0, 1.0
        if "/" not in rate_str:
            try:
                cap = float(rate_str)
                return True, cap, 1.0
            except Exception:
                return False, 1.0, 1.0

        parts = rate_str.split("/", 1)
        try:
            cap = float(parts[0])
        except Exception:
            return False, 1.0, 1.0

        dur_str = parts[1].strip()
        if not dur_str:
            return True, cap, 1.0

        unit = dur_str[-1].lower()
        multiplier = 1.0
        num_str = dur_str

        if unit == "s":
            multiplier = 1.0
            num_str = dur_str[:-1]
        elif unit == "m":
            multiplier = 60.0
            num_str = dur_str[:-1]
        elif unit == "h":
            multiplier = 3600.0
            num_str = dur_str[:-1]
        elif unit == "d":
            multiplier = 86400.0
            num_str = dur_str[:-1]

        try:
            val = float(num_str) if num_str else 1.0
            window = max(0.001, val * multiplier)
            return True, cap, window
        except Exception:
            return False, 1.0, 1.0

    def set_rule(self, scope: str, rate_str: str) -> None:
        ok, cap, win = self.parse_rate(rate_str)
        if ok:
            self.set_custom_rule(scope, cap, win)

    def set_custom_rule(self, scope: str, capacity: float, window_seconds: float) -> None:
        with self._lock:
            cap = max(0.001, capacity)
            win = max(0.001, window_seconds)
            refill = cap / win
            self._default_rules[scope] = (cap, win, refill)

    def _refill(self, b: Dict[str, float], now: float) -> None:
        last = b["last_refill"]
        elapsed = now - last
        if elapsed > 0:
            b["tokens"] = min(b["capacity"], b["tokens"] + elapsed * b["refill_rate"])
            b["last_refill"] = now

    def _get_rule_for_key(self, key: str) -> Tuple[float, float, float]:
        if key.startswith("user:") and "user" in self._default_rules:
            return self._default_rules["user"]
        if key.startswith("chat:") and "chat" in self._default_rules:
            return self._default_rules["chat"]
        if key == "global" and "global" in self._default_rules:
            return self._default_rules["global"]
        if key in self._default_rules:
            return self._default_rules[key]
        return (10.0, 1.0, 10.0)

    def check(self, key: str, tokens: float = 1.0) -> Tuple[bool, float]:
        with self._lock:
            now = time.monotonic()
            b = self._buckets.get(key)
            if b and now < b["backoff_until"]:
                return False, b["backoff_until"] - now

            if not b:
                cap, win, refill = self._get_rule_for_key(key)
                b = {
                    "tokens": cap,
                    "capacity": cap,
                    "refill_rate": refill,
                    "last_refill": now,
                    "backoff_until": 0.0,
                }
                self._buckets[key] = b

            self._refill(b, now)
            if b["tokens"] >= tokens:
                return True, 0.0
            else:
                needed = tokens - b["tokens"]
                retry_after = (needed / b["refill_rate"]) if b["refill_rate"] > 0 else 1.0
                return False, retry_after

    def acquire(self, key: str, tokens: float = 1.0) -> bool:
        allowed, _ = self.check(key, tokens)
        if allowed:
            with self._lock:
                if key in self._buckets:
                    self._buckets[key]["tokens"] -= tokens
            return True
        return False

    def check_and_acquire(self, user_id: str = "", chat_id: str = "", tokens: float = 1.0) -> Tuple[bool, float]:
        with self._lock:
            now = time.monotonic()
            keys: List[str] = []
            if user_id and "user" in self._default_rules:
                keys.append(f"user:{user_id}")
            if chat_id and "chat" in self._default_rules:
                keys.append(f"chat:{chat_id}")
            if "global" in self._default_rules:
                keys.append("global")

            max_retry = 0.0
            all_allowed = True

            for k in keys:
                b = self._buckets.get(k)
                if b and now < b["backoff_until"]:
                    all_allowed = False
                    max_retry = max(max_retry, b["backoff_until"] - now)
                    continue

                if not b:
                    cap, win, refill = self._get_rule_for_key(k)
                    b = {
                        "tokens": cap,
                        "capacity": cap,
                        "refill_rate": refill,
                        "last_refill": now,
                        "backoff_until": 0.0,
                    }
                    self._buckets[k] = b

                self._refill(b, now)
                if b["tokens"] < tokens:
                    all_allowed = False
                    needed = tokens - b["tokens"]
                    wait_t = (needed / b["refill_rate"]) if b["refill_rate"] > 0 else 1.0
                    max_retry = max(max_retry, wait_t)

            if all_allowed:
                for k in keys:
                    self._buckets[k]["tokens"] -= tokens
                return True, 0.0

            return False, max_retry

    def record_429(self, key: str, retry_after_seconds: float) -> None:
        with self._lock:
            now = time.monotonic()
            target = key or "global"
            if target not in self._buckets:
                cap, win, refill = self._get_rule_for_key(target)
                self._buckets[target] = {
                    "tokens": cap,
                    "capacity": cap,
                    "refill_rate": refill,
                    "last_refill": now,
                    "backoff_until": 0.0,
                }
            self._buckets[target]["backoff_until"] = now + max(0.1, retry_after_seconds)

    def get_retry_after(self, key: str) -> float:
        with self._lock:
            now = time.monotonic()
            b = self._buckets.get(key)
            if b and now < b["backoff_until"]:
                return b["backoff_until"] - now
            return 0.0

    def reset(self, key: str = "") -> None:
        with self._lock:
            if key:
                self._buckets.pop(key, None)
            else:
                self._buckets.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._buckets)


class FSM:
    """In-memory finite state machine matching C++ FSM."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._states: Dict[str, Tuple[str, float]] = {}  # state, expires_at
        self._data: Dict[str, Tuple[Dict[str, str], float]] = {}  # dict, expires_at

    def set_state(self, key: str, state: str, ttl_seconds: float = 0.0) -> None:
        with self._lock:
            now = time.monotonic()
            exp = (now + ttl_seconds) if ttl_seconds > 0 else 0.0
            self._states[key] = (state, exp)

    def get_state(self, key: str) -> str:
        with self._lock:
            rec = self._states.get(key)
            if not rec:
                return ""
            state, exp = rec
            now = time.monotonic()
            if exp > 0 and now >= exp:
                del self._states[key]
                return ""
            return state

    def clear_state(self, key: str) -> None:
        with self._lock:
            self._states.pop(key, None)

    def set_data(self, key: str, data_key: str, data_val: str, ttl_seconds: float = 0.0) -> None:
        with self._lock:
            now = time.monotonic()
            exp = (now + ttl_seconds) if ttl_seconds > 0 else 0.0
            rec = self._data.get(key)
            d = dict(rec[0]) if rec else {}
            d[data_key] = data_val
            self._data[key] = (d, exp)

    def get_data(self, key: str, data_key: str) -> str:
        with self._lock:
            rec = self._data.get(key)
            if not rec:
                return ""
            d, exp = rec
            now = time.monotonic()
            if exp > 0 and now >= exp:
                del self._data[key]
                return ""
            return d.get(data_key, "")

    def get_all_data(self, key: str) -> Dict[str, str]:
        with self._lock:
            rec = self._data.get(key)
            if not rec:
                return {}
            d, exp = rec
            now = time.monotonic()
            if exp > 0 and now >= exp:
                del self._data[key]
                return {}
            return dict(d)

    def set_all_data(self, key: str, data: Dict[str, str], ttl_seconds: float = 0.0) -> None:
        with self._lock:
            now = time.monotonic()
            exp = (now + ttl_seconds) if ttl_seconds > 0 else 0.0
            self._data[key] = (dict(data), exp)

    def clear_data(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)

    def reset(self, key: str = "") -> None:
        with self._lock:
            if key:
                self._states.pop(key, None)
                self._data.pop(key, None)
            else:
                self._states.clear()
                self._data.clear()

    def size(self) -> int:
        with self._lock:
            return len(set(self._states.keys()) | set(self._data.keys()))

    def cleanup_expired(self) -> int:
        with self._lock:
            now = time.monotonic()
            cleaned = 0
            for k in list(self._states.keys()):
                _, exp = self._states[k]
                if exp > 0 and now >= exp:
                    del self._states[k]
                    cleaned += 1
            for k in list(self._data.keys()):
                _, exp = self._data[k]
                if exp > 0 and now >= exp:
                    del self._data[k]
                    cleaned += 1
            return cleaned


class Cache:
    """In-process key-value store with TTL matching C++ Cache."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: Dict[str, Tuple[str, float]] = {}  # value, expires_at

    def set(self, key: str, value: str, ttl_seconds: float = 0.0) -> None:
        with self._lock:
            now = time.monotonic()
            exp = (now + ttl_seconds) if ttl_seconds > 0 else 0.0
            self._store[key] = (str(value), exp)

    def get(self, key: str) -> str:
        with self._lock:
            rec = self._store.get(key)
            if not rec:
                return ""
            val, exp = rec
            now = time.monotonic()
            if exp > 0 and now >= exp:
                del self._store[key]
                return ""
            return val

    def has(self, key: str) -> bool:
        return bool(self.get(key))

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._store.pop(key, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def size(self) -> int:
        self.cleanup_expired()
        with self._lock:
            return len(self._store)

    def cleanup_expired(self) -> int:
        with self._lock:
            now = time.monotonic()
            cleaned = 0
            for k in list(self._store.keys()):
                _, exp = self._store[k]
                if exp > 0 and now >= exp:
                    del self._store[k]
                    cleaned += 1
            return cleaned

    def keys(self) -> List[str]:
        self.cleanup_expired()
        with self._lock:
            return list(self._store.keys())


class AntiSpam:
    """Anti-spam and bloom-filter duplicate detection matching C++ AntiSpam."""

    def __init__(self, bloom_size: int = 65536, window_seconds: float = 300.0) -> None:
        self._lock = threading.Lock()
        self._window = window_seconds
        self._last_rot = time.monotonic()
        self._current_seen: Set[str] = set()
        self._prev_seen: Set[str] = set()

    def _rotate(self, now: float) -> None:
        if now - self._last_rot >= self._window:
            self._prev_seen = self._current_seen
            self._current_seen = set()
            self._last_rot = now

    def is_duplicate(self, text: str, user_id: str = "") -> bool:
        with self._lock:
            now = time.monotonic()
            self._rotate(now)
            key = f"{user_id}:{text}" if user_id else text
            return (key in self._current_seen) or (key in self._prev_seen)

    def add(self, text: str, user_id: str = "") -> None:
        with self._lock:
            now = time.monotonic()
            self._rotate(now)
            key = f"{user_id}:{text}" if user_id else text
            self._current_seen.add(key)

    def calculate_score(self, text: str, message_rate: float = 0.0, duplicate_count: int = 0) -> float:
        score = 0.0
        if not text:
            return score

        if message_rate > 5.0:
            score += 0.4
        elif message_rate > 2.0:
            score += 0.2

        if duplicate_count > 3:
            score += 0.5
        elif duplicate_count > 0:
            score += 0.25

        # Link count
        links = ["http://", "https://", "t.me/", "discord.gg/", "bit.ly/"]
        link_cnt = sum(text.count(m) for m in links)
        if link_cnt > 3:
            score += 0.4
        elif link_cnt >= 1:
            score += 0.15 * link_cnt

        # Caps ratio
        letters = [c for c in text if c.isalpha()]
        if len(letters) >= 10:
            caps = sum(1 for c in letters if c.isupper())
            ratio = caps / len(letters)
            if ratio > 0.8:
                score += 0.3
            elif ratio > 0.6:
                score += 0.15

        # Mentions
        mentions = text.count("@")
        if mentions > 4:
            score += 0.35
        elif mentions > 2:
            score += 0.15

        # Char repetition
        max_run = 1
        cur_run = 1
        for i in range(1, len(text)):
            if text[i] == text[i - 1]:
                cur_run += 1
                max_run = max(max_run, cur_run)
            else:
                cur_run = 1
        if max_run >= 8:
            score += 0.25
        elif max_run >= 5:
            score += 0.1

        return min(1.0, max(0.0, score))

    def is_spam(self, text: str, threshold: float = 0.7, message_rate: float = 0.0) -> bool:
        dup = 1 if self.is_duplicate(text) else 0
        score = self.calculate_score(text, message_rate, dup)
        return score >= threshold

    def reset(self) -> None:
        with self._lock:
            self._current_seen.clear()
            self._prev_seen.clear()
            self._last_rot = time.monotonic()


class Metrics:
    """Prometheus metrics collector matching C++ Metrics."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: Dict[str, float] = collections.defaultdict(float)
        self._histograms: Dict[str, Dict[str, Any]] = {}
        self._default_buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]

    def _format_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        if not labels:
            return name
        lbl_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{lbl_str}}}"

    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        with self._lock:
            key = self._format_key(name, labels)
            self._counters[key] += value

    def observe(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        with self._lock:
            key = self._format_key(name, labels)
            if key not in self._histograms:
                self._histograms[key] = {
                    "buckets": {b: 0 for b in self._default_buckets},
                    "sum": 0.0,
                    "count": 0,
                }
            hd = self._histograms[key]
            hd["count"] += 1
            hd["sum"] += value
            for b in self._default_buckets:
                if value <= b:
                    hd["buckets"][b] += 1

    def record_latency(self, command_name: str, duration_seconds: float) -> None:
        labels = {"command": command_name}
        self.observe("bot_command_latency_seconds", duration_seconds, labels)
        self.increment_counter("bot_command_calls_total", 1.0, labels)

    def export_prometheus(self) -> str:
        with self._lock:
            lines: List[str] = []
            for k, v in sorted(self._counters.items()):
                lines.append(f"{k} {v}")

            for k, hd in sorted(self._histograms.items()):
                base = k.split("{")[0]
                lbls = k[len(base) + 1 : -1] if "{" in k else ""

                for b in self._default_buckets:
                    cnt = hd["buckets"][b]
                    tag = f"{lbls},le=\"{b}\"" if lbls else f'le="{b}"'
                    lines.append(f"{base}_bucket{{{tag}}} {cnt}")

                inf_tag = f'{lbls},le="+Inf"' if lbls else 'le="+Inf"'
                lines.append(f"{base}_bucket{{{inf_tag}}} {hd['count']}")

                sum_tag = f"{{{lbls}}}" if lbls else ""
                lines.append(f"{base}_sum{sum_tag} {hd['sum']}")
                lines.append(f"{base}_count{sum_tag} {hd['count']}")

            return "\n".join(lines) + ("\n" if lines else "")

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._histograms.clear()


class WebhookServer:
    """Pure-Python Threaded HTTP Webhook Server."""

    def __init__(self) -> None:
        self._routes: Dict[str, Callable[[str, str, str], str]] = {}
        self._default_handler: Optional[Callable[[str, str, str], str]] = None
        self._server: Optional[socketserver.TCPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._host = "0.0.0.0"
        self._port = 8443
        self._running = False

    def add_route(self, path: str, handler: Callable[[str, str, str], str]) -> None:
        self._routes[path] = handler

    def set_default_handler(self, handler: Callable[[str, str, str], str]) -> None:
        self._default_handler = handler

    def start(self, host: str = "0.0.0.0", port: int = 8443) -> bool:
        if self._running:
            return True
        self._host = host
        self._port = port

        server_ref = self

        class RequestHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                self._handle("GET")

            def do_POST(self) -> None:
                self._handle("POST")

            def do_PUT(self) -> None:
                self._handle("PUT")

            def _handle(self, method: str) -> None:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8") if length > 0 else ""
                path = self.path.split("?")[0]

                handler = server_ref._routes.get(path) or server_ref._default_handler
                if handler:
                    try:
                        res = handler(method, path, body)
                        status = 200
                    except Exception as e:
                        res = json.dumps({"error": str(e)})
                        status = 500
                else:
                    res = json.dumps({"error": "not_found"})
                    status = 404

                res_bytes = res.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(res_bytes)))
                self.end_headers()
                self.wfile.write(res_bytes)

            def log_message(self, format: str, *args: Any) -> None:
                pass  # suppress standard http logs

        class ThreadingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
            allow_reuse_address = True
            daemon_threads = True

        try:
            self._server = ThreadingServer((host, port), RequestHandler)
            self._running = True
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()
            return True
        except Exception:
            self._running = False
            return False

    def stop(self) -> None:
        if self._running and self._server:
            self._running = False
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def is_running(self) -> bool:
        return self._running

    def get_port(self) -> int:
        return self._port

    def get_host(self) -> str:
        return self._host
