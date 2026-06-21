"""Tests for @symbol mentions."""

from aion.cli_agent.symbols import parse_symbol_token, resolve_symbol


def test_parse_symbol_token():
    assert parse_symbol_token("mod.py:MyClass.method") == ("mod.py", "MyClass.method")
    assert parse_symbol_token("symbol:foo.py:bar") == ("foo.py", "bar")


def test_resolve_python_function(tmp_path):
    f = tmp_path / "mod.py"
    f.write_text("def hello():\n    return 1\n", encoding="utf-8")
    label, block = resolve_symbol(str(tmp_path), "mod.py", "hello")
    assert "hello" in block
    assert "def hello" in block
