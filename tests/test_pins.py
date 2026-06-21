"""Tests for pinned context in mentions."""

from aion.cli_agent.mentions import expand_mentions


def test_pinned_file_attached(tmp_path):
    f = tmp_path / "pinned.txt"
    f.write_text("pinned content\n", encoding="utf-8")
    enriched, labels = expand_mentions(
        "hello",
        str(tmp_path),
        pinned_paths=["pinned.txt"],
    )
    assert "pinned content" in enriched
    assert any("pinned" in label for label in labels)
