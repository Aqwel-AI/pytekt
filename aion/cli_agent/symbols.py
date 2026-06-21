"""Resolve @symbol mentions to code blocks."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import List, Optional, Tuple

from ..tools.code_agent import grep_search
from ..tools.workspace import Workspace

_SYMBOL_TOKEN_RE = re.compile(
    r"^(?:symbol:)?(?P<path>[^:]+):(?P<name>.+)$|^(?P<path2>[^:]+\.py):(?P<name2>\w+)$"
)


def parse_symbol_token(token: str) -> Optional[Tuple[str, str]]:
    """Return (file_path, qualname) or None."""
    if token.startswith("symbol:"):
        token = token[7:]
    m = _SYMBOL_TOKEN_RE.match(token)
    if not m:
        if ":" in token and token.endswith(".py"):
            path, _, name = token.partition(":")
            return path, name
        return None
    path = m.group("path") or m.group("path2")
    name = m.group("name") or m.group("name2")
    if not path or not name:
        return None
    return path, name


def _extract_python_block(source: str, qualname: str) -> Optional[Tuple[int, int, str]]:
    parts = qualname.split(".")
    target = parts[-1]
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.found: Optional[Tuple[int, int, str]] = None

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            if node.name == target and self.found is None:
                end = getattr(node, "end_lineno", node.lineno)
                lines = source.splitlines()
                block = "\n".join(lines[node.lineno - 1 : end])
                self.found = (node.lineno, end, block)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self.visit_FunctionDef(node)  # type: ignore[arg-type]

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            if node.name == target and self.found is None:
                end = getattr(node, "end_lineno", node.lineno)
                lines = source.splitlines()
                block = "\n".join(lines[node.lineno - 1 : end])
                self.found = (node.lineno, end, block)
            self.generic_visit(node)

    v = Visitor()
    v.visit(tree)
    return v.found


def resolve_symbol(
    workspace_root: str,
    file_path: str,
    qualname: str,
) -> Tuple[str, str]:
    """Return (label, xml block) for a symbol mention."""
    ws = Workspace(workspace_root)
    try:
        resolved = ws.resolve(file_path)
    except PermissionError as e:
        return f"{file_path}:{qualname}", f'<error path="{file_path}">{e}</error>'

    if not resolved.is_file():
        return f"{file_path}:{qualname}", f'<error path="{file_path}">Not a file.</error>'

    try:
        source = resolved.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return f"{file_path}:{qualname}", f'<error path="{file_path}">{e}</error>'

    extracted = _extract_python_block(source, qualname)
    if extracted:
        start, end, block = extracted
        xml = (
            f'<symbol path="{file_path}" name="{qualname}" lines="{start}-{end}">\n'
            f"{block}\n</symbol>"
        )
        return f"{file_path}:{qualname}", xml

    hits = grep_search(ws, rf"^\s*(def|class)\s+{re.escape(qualname.split('.')[-1])}\b", file_path)
    if hits.startswith("No matches"):
        return f"{file_path}:{qualname}", (
            f'<error path="{file_path}">Symbol {qualname!r} not found.</error>'
        )
    xml = f'<symbol path="{file_path}" name="{qualname}">\n{hits}\n</symbol>'
    return f"{file_path}:{qualname}", xml


def is_symbol_token(token: str) -> bool:
    return parse_symbol_token(token) is not None
