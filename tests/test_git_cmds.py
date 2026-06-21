"""Tests for git slash command helpers."""

from aion.cli_agent.git_context import expand_git_mention


def test_git_mention_diff(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    label, block = expand_git_mention("diff", str(tmp_path))
    assert label
    assert block is not None
