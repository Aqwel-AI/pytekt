"""Tests for JSON tool protocol."""

import json

from pytekt.agents.json_tools import extract_json_object
from pytekt.tools.registry import ToolRegistry
from pytekt.tools.workspace import Workspace
from pytekt.tools.code_agent import write_file


def test_extract_json_plain():
    obj = extract_json_object('{"tool":"write_file","arguments":{"path":"a.txt"}}')
    assert obj["tool"] == "write_file"


def test_extract_json_fence():
    text = 'Here:\n```json\n{"done":true,"message":"ok"}\n```'
    obj = extract_json_object(text)
    assert obj["done"] is True


def test_write_via_registry(tmp_path):
    ws = Workspace(tmp_path)
    reg = ToolRegistry()
    reg.register("write_file", lambda path, content: write_file(ws, path, content))
    out = reg.call("write_file", json.dumps({"path": "Text.txt", "content": "Armenia"}))
    assert "Wrote" in out
    assert (tmp_path / "Text.txt").read_text(encoding="utf-8") == "Armenia"
