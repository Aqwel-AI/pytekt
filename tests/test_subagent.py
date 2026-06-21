"""Tests for research subagent registry."""

from aion.cli_agent.subagent import _read_only_registry


def test_read_only_registry_has_no_write(tmp_path):
    reg = _read_only_registry(str(tmp_path))
    assert "read_file" in reg._fns
    assert "write_file" not in reg._fns
