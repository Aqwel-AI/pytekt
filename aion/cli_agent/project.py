"""Project and workspace intelligence for the terminal agent."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


CPP_SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".c++"}
CPP_HEADER_SUFFIXES = {".h", ".hh", ".hpp", ".hxx"}
CPP_SUFFIXES = CPP_SOURCE_SUFFIXES | CPP_HEADER_SUFFIXES


@dataclass
class ProjectInfo:
    """Detected project metadata for prompts, validation, and commands."""

    root: str
    kinds: List[str]
    test_command: Optional[str] = None
    lint_command: Optional[str] = None
    build_command: Optional[str] = None
    package_name: Optional[str] = None
    framework: Optional[str] = None
    dependency_manager: Optional[str] = None
    conventions: List[str] = field(default_factory=list)
    signals: Dict[str, str] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [f"Project root: {self.root}"]
        if self.kinds:
            lines.append(f"Detected: {', '.join(self.kinds)}")
        if self.framework:
            lines.append(f"Framework: {self.framework}")
        if self.package_name:
            lines.append(f"Package: {self.package_name}")
        if self.dependency_manager:
            lines.append(f"Dependency manager: {self.dependency_manager}")
        if self.test_command:
            lines.append(f"Test: {self.test_command}")
        if self.lint_command:
            lines.append(f"Lint: {self.lint_command}")
        if self.build_command:
            lines.append(f"Build: {self.build_command}")
        if self.conventions:
            lines.append(f"Conventions: {', '.join(self.conventions)}")
        return "\n".join(lines)


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _has_cpp_sources(root: Path) -> bool:
    for pattern in ("*.c", "*.cc", "*.cpp", "*.cxx", "*.c++", "*.h", "*.hh", "*.hpp", "*.hxx"):
        if any(root.rglob(pattern)):
            return True
    return False


def _append_kind(kinds: List[str], kind: str) -> None:
    if kind not in kinds:
        kinds.append(kind)


def discover_project(workspace_root: Optional[str] = None) -> ProjectInfo:
    root = Path(workspace_root or os.getcwd()).resolve()
    kinds: List[str] = []
    test_cmd: Optional[str] = None
    lint_cmd: Optional[str] = None
    build_cmd: Optional[str] = None
    package_name: Optional[str] = None
    framework: Optional[str] = None
    dependency_manager: Optional[str] = None
    conventions: List[str] = []
    signals: Dict[str, str] = {}

    pyproject = root / "pyproject.toml"
    package_json = root / "package.json"
    cargo_toml = root / "Cargo.toml"
    makefile = root / "Makefile"
    cmake_lists = root / "CMakeLists.txt"
    meson_build = root / "meson.build"
    compile_commands = root / "compile_commands.json"
    clang_tidy = root / ".clang-tidy"
    clang_format = root / ".clang-format"
    conanfile = root / "conanfile.txt"
    conanfile_py = root / "conanfile.py"
    vcpkg_json = root / "vcpkg.json"
    readme = root / "README.md"
    aion_md = root / "AION.md"
    requirements = root / "requirements.txt"
    poetry_lock = root / "poetry.lock"
    pnpm_lock = root / "pnpm-lock.yaml"
    yarn_lock = root / "yarn.lock"
    uv_lock = root / "uv.lock"

    if pyproject.is_file():
        _append_kind(kinds, "python")
        test_cmd = test_cmd or "pytest"
        lint_cmd = lint_cmd or "ruff check ."
        dependency_manager = dependency_manager or "pyproject"
        text = _safe_read(pyproject)
        if "[tool.pytest" in text or "[tool.pytest.ini_options]" in text:
            signals["pytest"] = "configured"
        if "[tool.ruff" in text:
            signals["ruff"] = "configured"
        if "pybind11" in text.casefold():
            signals["pybind11"] = "configured"
        if "django" in text.casefold():
            framework = framework or "django"
        if "fastapi" in text.casefold():
            framework = framework or "fastapi"
        if "flask" in text.casefold():
            framework = framework or "flask"
        if "[project]" in text and "name" in text:
            for line in text.splitlines():
                if line.strip().startswith("name"):
                    package_name = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    elif (root / "setup.py").is_file():
        _append_kind(kinds, "python")
        test_cmd = test_cmd or "pytest"
        dependency_manager = dependency_manager or "setuptools"

    if requirements.is_file():
        dependency_manager = dependency_manager or "pip"
    if poetry_lock.is_file():
        dependency_manager = "poetry"
    if uv_lock.is_file():
        dependency_manager = "uv"

    if package_json.is_file():
        _append_kind(kinds, "node")
        dependency_manager = dependency_manager or "npm"
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            package_name = data.get("name") or package_name
            scripts = data.get("scripts") or {}
            if "test" in scripts:
                test_cmd = test_cmd or "npm test"
            if "lint" in scripts:
                lint_cmd = lint_cmd or "npm run lint"
            if "build" in scripts:
                build_cmd = build_cmd or "npm run build"
            deps = " ".join(list((data.get("dependencies") or {}).keys()) + list((data.get("devDependencies") or {}).keys())).casefold()
            if "react" in deps:
                framework = framework or "react"
            if "next" in deps:
                framework = framework or "nextjs"
            if "vue" in deps:
                framework = framework or "vue"
            if "svelte" in deps:
                framework = framework or "svelte"
            if "typescript" in deps:
                _append_kind(kinds, "typescript")
        except (OSError, json.JSONDecodeError):
            pass
    if pnpm_lock.is_file():
        dependency_manager = "pnpm"
    if yarn_lock.is_file():
        dependency_manager = "yarn"

    if makefile.is_file():
        _append_kind(kinds, "make")
        if not test_cmd:
            test_cmd = "make test"
        if not lint_cmd:
            lint_cmd = "make lint"
        if not build_cmd:
            build_cmd = "make build"

    if (root / "tox.ini").is_file():
        _append_kind(kinds, "tox")
        test_cmd = test_cmd or "tox"

    if cargo_toml.is_file():
        _append_kind(kinds, "rust")
        dependency_manager = dependency_manager or "cargo"
        test_cmd = test_cmd or "cargo test"
        lint_cmd = lint_cmd or "cargo clippy --all-targets --all-features"
        build_cmd = build_cmd or "cargo build"

    if (root / "go.mod").is_file():
        _append_kind(kinds, "go")
        dependency_manager = dependency_manager or "go modules"
        test_cmd = test_cmd or "go test ./..."
        build_cmd = build_cmd or "go build ./..."

    cpp_detected = (
        cmake_lists.is_file()
        or meson_build.is_file()
        or compile_commands.is_file()
        or clang_tidy.is_file()
        or clang_format.is_file()
        or conanfile.is_file()
        or conanfile_py.is_file()
        or vcpkg_json.is_file()
        or _has_cpp_sources(root)
    )
    if cpp_detected:
        _append_kind(kinds, "cpp")
        if cmake_lists.is_file():
            framework = framework or "cmake"
            build_cmd = build_cmd or "cmake --build build"
            test_cmd = test_cmd or "ctest --test-dir build --output-on-failure"
        elif meson_build.is_file():
            framework = framework or "meson"
            build_cmd = build_cmd or "meson compile -C build"
            test_cmd = test_cmd or "meson test -C build --print-errorlogs"
        if clang_tidy.is_file() or compile_commands.is_file():
            lint_cmd = lint_cmd or "clang-tidy"
        elif clang_format.is_file():
            lint_cmd = lint_cmd or "clang-format --dry-run --Werror"
        if vcpkg_json.is_file():
            dependency_manager = dependency_manager or "vcpkg"
        elif conanfile.is_file() or conanfile_py.is_file():
            dependency_manager = dependency_manager or "conan"
        elif cmake_lists.is_file():
            dependency_manager = dependency_manager or "cmake"
        elif meson_build.is_file():
            dependency_manager = dependency_manager or "meson"
        if compile_commands.is_file():
            signals["compile_commands"] = "present"
        if clang_tidy.is_file():
            signals["clang_tidy"] = "configured"
        if clang_format.is_file():
            signals["clang_format"] = "configured"

    if (root / ".pre-commit-config.yaml").is_file():
        conventions.append("pre-commit")
    if aion_md.is_file():
        conventions.append("AION.md")
    if readme.is_file():
        readme_text = _safe_read(readme).casefold()
        if "contributing" in readme_text:
            conventions.append("CONTRIBUTING guidance in README")
        if "pytest" in readme_text and not test_cmd:
            test_cmd = "pytest"

    if (root / ".github" / "workflows").is_dir():
        conventions.append("GitHub Actions")
    if (root / ".editorconfig").is_file():
        conventions.append(".editorconfig")

    return ProjectInfo(
        root=str(root),
        kinds=sorted(set(kinds)) or ["generic"],
        test_command=test_cmd,
        lint_command=lint_cmd,
        build_command=build_cmd,
        package_name=package_name,
        framework=framework,
        dependency_manager=dependency_manager,
        conventions=conventions,
        signals=signals,
    )
