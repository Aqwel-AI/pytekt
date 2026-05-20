"""Tests for aion.usage store and aggregates."""

from __future__ import annotations

import os
import tempfile

import pytest

from aion.usage.aggregate import build_summary, build_timeseries, filter_events
from aion.usage.extract import extract_usage_from_response, estimate_tokens
from aion.usage.record import record_llm_call
from aion.usage.launch import is_aion_usage_server, resolve_usage_port
from aion.usage.store import UsageStore


def test_extract_openai_usage():
    raw = {"usage": {"prompt_tokens": 100, "completion_tokens": 50}}
    assert extract_usage_from_response(raw) == (100, 50)


def test_record_and_summary():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "events.jsonl")
        store = UsageStore(path)
        record_llm_call(
            provider="openai",
            model="gpt-4o-mini",
            prompt_tokens=200,
            completion_tokens=80,
            store=store,
        )
        events = store.read_all()
        assert len(events) == 1
        assert events[0]["total_tokens"] == 280
        summary = build_summary(events, range_key="today")
        assert summary["call_count"] == 1
        assert summary["total_tokens"] == 280


def test_timeseries_today():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "events.jsonl")
        store = UsageStore(path)
        record_llm_call(provider="gemini", model="flash", prompt_tokens=10, completion_tokens=5, store=store)
        events = store.read_all()
        ts = build_timeseries(events, range_key="today")
        assert "labels" in ts
        assert len(ts["tokens"]) == len(ts["labels"])


def test_resolve_port_when_3333_not_aion():
    """Port 3333 may be another app; Aion should not treat it as our dashboard."""
    port, running = resolve_usage_port("127.0.0.1", 3847)
    assert port >= 3847
    if is_aion_usage_server("127.0.0.1", 3333):
        pytest.skip("3333 happens to be Aion in this environment")
    else:
        p, already = resolve_usage_port("127.0.0.1", 3333)
        assert not already or is_aion_usage_server("127.0.0.1", p)


def test_get_system_info_survives_cpu_freq_failure(monkeypatch):
    """macOS Apple Silicon: psutil.cpu_freq() can raise FileNotFoundError."""
    import sys

    from aion.usage import hardware_api

    class FakePsutil:
        @staticmethod
        def cpu_count(logical=True):
            return 8 if logical else 4

        @staticmethod
        def cpu_freq():
            raise FileNotFoundError("sysctl HW_CPU_FREQ")

    monkeypatch.setitem(sys.modules, "psutil", FakePsutil)
    info = hardware_api.get_system_info()
    assert info["logical_cores"] == 8
    assert "cpu_freq_mhz" not in info


def test_estimate_tokens_fallback():
    p, c = estimate_tokens(
        [{"role": "user", "content": "Hello world"}],
        "Hi there",
        model="gpt-4o-mini",
    )
    assert p >= 1
    assert c >= 0
