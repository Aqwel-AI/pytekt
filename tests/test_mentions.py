"""Tests for @ mention expansion."""

from aion.cli_agent.git_context import is_git_token
from aion.cli_agent.mentions import expand_mentions


def test_git_token_detection():
    assert is_git_token("git")
    assert is_git_token("@changed")
    assert not is_git_token("src/main.py")


def test_expand_file_mention(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("hello world\n", encoding="utf-8")
    enriched, labels = expand_mentions("explain @hello.txt", str(tmp_path))
    assert "hello.txt" in labels[0]
    assert "hello world" in enriched
    assert "Attached context" in enriched


def test_expand_missing_file(tmp_path):
    enriched, labels = expand_mentions("check @missing.py", str(tmp_path))
    assert labels
    assert "missing" in labels[0].lower() or "missing" in enriched


def test_expand_folder_mention(tmp_path):
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "mod.py").write_text("x = 1\n", encoding="utf-8")
    enriched, labels = expand_mentions("review @pkg/", str(tmp_path))
    assert any("pkg" in label for label in labels)
    assert "mod.py" in enriched or "x = 1" in enriched


def test_no_mentions_passthrough(tmp_path):
    text = "just a question"
    enriched, labels = expand_mentions(text, str(tmp_path))
    assert enriched == text
    assert labels == []
