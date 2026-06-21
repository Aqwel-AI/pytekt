"""Tests for secret scanning."""

from aion.cli_agent.secret_scan import scan_text, should_block


def test_detect_api_key_pattern():
    hits = scan_text('key = "nvapi-abcdefghijklmnopqrstuvwxyz"')
    assert hits


def test_clean_text():
    blocked, hits = should_block("hello world")
    assert not blocked
    assert not hits
