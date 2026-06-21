"""Tests for multi-root workspace."""

from aion.cli_agent.multi_workspace import MultiWorkspace


def test_multi_workspace_primary(tmp_path):
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "a.py").write_text("x=1", encoding="utf-8")
    mw = MultiWorkspace(str(tmp_path), extra_roots=[str(sub)])
    ws = mw.workspace_for("a.py")
    assert ws.resolve("a.py").is_file()
