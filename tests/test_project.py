"""Tests for project auto-discovery."""

from aion.cli_agent.project import discover_project


def test_discover_python_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\n',
        encoding="utf-8",
    )
    info = discover_project(str(tmp_path))
    assert "python" in info.kinds
    assert info.test_command == "pytest"
    assert info.lint_command == "ruff check ."
    assert info.package_name == "demo"


def test_discover_package_json(tmp_path):
    (tmp_path / "package.json").write_text(
        '{"name":"app","scripts":{"test":"vitest","lint":"eslint ."}}',
        encoding="utf-8",
    )
    info = discover_project(str(tmp_path))
    assert "node" in info.kinds
    assert info.test_command == "npm test"
