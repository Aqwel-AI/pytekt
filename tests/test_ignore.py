"""Tests for .aionignore filtering."""

from aion.cli_agent.ignore import IgnoreMatcher, merged_skip_dirs


def test_default_skip_dirs(tmp_path):
    (tmp_path / "node_modules").mkdir()
    skip = merged_skip_dirs(str(tmp_path))
    assert "node_modules" in skip


def test_aionignore_pattern(tmp_path):
    (tmp_path / ".aionignore").write_text("secret/\n*.log\n", encoding="utf-8")
    m = IgnoreMatcher(str(tmp_path))
    assert m.should_skip_path("secret/file.txt")
    assert m.should_skip_path("foo.log")


def test_filter_paths(tmp_path):
    (tmp_path / ".aionignore").write_text("skip.txt\n", encoding="utf-8")
    m = IgnoreMatcher(str(tmp_path))
    out = m.filter_paths(["a.py", "skip.txt", "b.py"])
    assert out == ["a.py", "b.py"]
