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


def test_discover_cpp_cmake_project(tmp_path):
    (tmp_path / "CMakeLists.txt").write_text(
        "cmake_minimum_required(VERSION 3.20)\nproject(demo LANGUAGES CXX)\n",
        encoding="utf-8",
    )
    (tmp_path / ".clang-tidy").write_text("Checks: '*'\n", encoding="utf-8")
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")

    info = discover_project(str(tmp_path))

    assert "cpp" in info.kinds
    assert info.framework == "cmake"
    assert info.dependency_manager == "cmake"
    assert info.build_command == "cmake --build build"
    assert info.test_command == "ctest --test-dir build --output-on-failure"
    assert info.lint_command == "clang-tidy"
