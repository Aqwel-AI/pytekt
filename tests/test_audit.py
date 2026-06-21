"""Tests for audit log."""

from aion.cli_agent import audit


def test_audit_log_roundtrip(tmp_path, monkeypatch):
    path = tmp_path / "agent_audit.jsonl"
    monkeypatch.setattr(audit, "_AUDIT_PATH", path)
    audit.log_action(action="write_file", path="foo.py", provider="test")
    entries = audit.read_recent(5)
    assert len(entries) == 1
    assert entries[0]["action"] == "write_file"
