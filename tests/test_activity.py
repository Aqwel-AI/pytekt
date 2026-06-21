"""Tests for activity feed."""

from aion.cli_agent.activity import ActivityFeed


def test_activity_ring_buffer():
    feed = ActivityFeed(maxlen=3)
    feed.log("tool", "read_file foo.py")
    feed.log("chat", "hello")
    feed.log("connect", "ollama")
    feed.log("tokens", "100 tokens")
    recent = feed.recent(2)
    assert len(recent) == 2
    assert recent[-1].kind == "tokens"


def test_dashboard_empty():
    feed = ActivityFeed()
    assert feed.format_dashboard() == "No recent activity"
