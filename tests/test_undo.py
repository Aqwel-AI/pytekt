"""Tests for edit history /undo."""

from aion.cli_agent.edit_history import EditHistory


def test_undo_restores_file(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("original\n", encoding="utf-8")
    hist = EditHistory("test-session")
    hist.snapshot_before(str(tmp_path), "a.txt")
    f.write_text("changed\n", encoding="utf-8")
    msg = hist.undo_last(str(tmp_path))
    assert "Restored" in msg
    assert f.read_text(encoding="utf-8") == "original\n"
