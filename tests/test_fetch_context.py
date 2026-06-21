"""Tests for @web/@docs fetch guards."""

from aion.cli_agent.fetch_context import _validate_url, fetch_docs


def test_block_localhost():
    assert _validate_url("http://localhost/foo") is not None
    assert _validate_url("file:///etc/passwd") is not None


def test_docs_unknown_key():
    label, block = fetch_docs("unknown:key")
    assert "Unknown docs" in block
