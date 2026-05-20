"""Tests for coding-agent filesystem tools."""

import tempfile
from pathlib import Path

import pytest

from aion.tools.code_agent import edit_file, read_file, write_file
from aion.tools.workspace import Workspace


@pytest.fixture
def ws(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "hello.py").write_text("def greet():\n    return 'hi'\n", encoding="utf-8")
    return Workspace(tmp_path)


def test_read_file_line_numbers(ws):
    out = read_file(ws, "pkg/hello.py")
    assert "1|" in out
    assert "def greet" in out


def test_edit_file_unique(ws):
    r = edit_file(ws, "pkg/hello.py", "return 'hi'", "return 'hello'")
    assert "Edited" in r
    text = Path(ws.root, "pkg/hello.py").read_text(encoding="utf-8")
    assert "hello" in text


def test_edit_file_not_found(ws):
    r = edit_file(ws, "pkg/hello.py", "missing", "x")
    assert "not found" in r


def test_write_file(ws):
    r = write_file(ws, "pkg/new.py", "x = 1\n")
    assert "Wrote" in r
    assert Path(ws.root, "pkg/new.py").exists()


def test_workspace_escape(ws):
    with pytest.raises(PermissionError):
        ws.resolve("../../etc/passwd")
