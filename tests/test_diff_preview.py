"""Tests for diff preview."""

from aion.cli_agent.diff_preview import preview_write, unified_diff


def test_unified_diff():
    diff = unified_diff("a\n", "b\n", path="x.txt")
    assert "---" in diff
    assert "x.txt" in diff


def test_preview_write(tmp_path):
    diff = preview_write(str(tmp_path), "new.py", "print('hi')\n")
    assert "new.py" in diff
    assert "print" in diff
