#!/usr/bin/env python3
"""
PyTekt - Code Snippets
==========================

Utilities for extracting, formatting, and summarizing code snippets.

The original module exposed a few regex helpers for functions, classes, and
comments. This version keeps that lightweight ergonomics but uses Python's
``ast`` and ``tokenize`` modules wherever structural accuracy matters.

The design goal is pragmatic:

- work well on Python snippets, not only full files
- return structured data that is useful for docs, RAG, and code review tooling
- fail softly on malformed snippets by returning empty collections
- stay dependency-free and notebook-friendly
"""

from __future__ import annotations

import ast
import io
import re
import textwrap
import tokenize
from typing import Any, Dict, List, Optional


CODE_BLOCK_PATTERN = re.compile(
    r"```(?P<language>[\w.+-]*)[ \t]*\n(?P<code>.*?)```",
    re.DOTALL,
)


def _normalize_code(code: str) -> str:
    """Dedent and trim surrounding blank lines to stabilize parsing."""
    return textwrap.dedent(code).strip("\n")


def _parse_python(code: str) -> Optional[ast.Module]:
    """
    Parse Python code into an AST and return ``None`` on syntax errors.

    Snippet-oriented utilities should degrade gracefully because users often
    inspect partial blocks copied from notebooks, diffs, or chat messages.
    """
    normalized = _normalize_code(code)
    if not normalized:
        return None
    try:
        return ast.parse(normalized)
    except SyntaxError:
        return None


def _node_to_source(code: str, node: ast.AST) -> str:
    """
    Recover source text for an AST node.

    ``ast.get_source_segment`` gives the most faithful answer when location
    information is present. ``ast.unparse`` is the fallback for synthesized or
    location-less nodes.
    """
    normalized = _normalize_code(code)
    source = ast.get_source_segment(normalized, node)
    if source is not None:
        return source.strip()
    return ast.unparse(node).strip()


def _iter_function_nodes(tree: ast.Module) -> List[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Return every function-like node, including methods and nested functions."""
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def _format_arg(arg: ast.arg, annotation: Optional[ast.AST]) -> str:
    """Render one function argument with an optional annotation."""
    rendered = arg.arg
    if annotation is not None:
        rendered += f": {ast.unparse(annotation)}"
    return rendered


def _format_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Render a compact, human-readable Python function signature."""
    args = node.args
    parts: List[str] = []

    posonly = args.posonlyargs
    positional = args.args
    kwonly = args.kwonlyargs
    defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)

    for arg in posonly:
        parts.append(_format_arg(arg, arg.annotation))
    if posonly:
        parts.append("/")

    for arg, default in zip(positional, defaults):
        rendered = _format_arg(arg, arg.annotation)
        if default is not None:
            rendered += f" = {ast.unparse(default)}"
        parts.append(rendered)

    if args.vararg is not None:
        parts.append("*" + _format_arg(args.vararg, args.vararg.annotation))
    elif kwonly:
        parts.append("*")

    for arg, default in zip(kwonly, args.kw_defaults):
        rendered = _format_arg(arg, arg.annotation)
        if default is not None:
            rendered += f" = {ast.unparse(default)}"
        parts.append(rendered)

    if args.kwarg is not None:
        parts.append("**" + _format_arg(args.kwarg, args.kwarg.annotation))

    rendered = f"{node.name}({', '.join(parts)})"
    if node.returns is not None:
        rendered += f" -> {ast.unparse(node.returns)}"
    return rendered


def _walk_target_names(target: ast.AST) -> List[str]:
    """Extract assigned symbol names from assignment targets."""
    names: List[str] = []
    if isinstance(target, ast.Name):
        names.append(target.id)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for element in target.elts:
            names.extend(_walk_target_names(element))
    elif isinstance(target, ast.Attribute):
        names.append(ast.unparse(target))
    return names


def extract_comments(code: str) -> List[str]:
    """
    Return Python comments from *code* using the tokenizer.

    Using ``tokenize`` avoids false positives from ``#`` characters that appear
    inside strings, which is a common weakness of regex-only approaches.
    """
    normalized = _normalize_code(code)
    if not normalized:
        return []

    comments: List[str] = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(normalized).readline):
            if token.type == tokenize.COMMENT:
                comments.append(token.string)
    except tokenize.TokenError:
        return comments
    return comments


def extract_functions(code: str) -> List[str]:
    """Return names of synchronous Python functions defined in *code*."""
    tree = _parse_python(code)
    if tree is None:
        return []
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


def extract_class_defs(code: str) -> List[str]:
    """Return class names defined in *code*."""
    tree = _parse_python(code)
    if tree is None:
        return []
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


def extract_docstrings(code: str) -> List[str]:
    """
    Return module, class, and function docstrings found in *code*.

    Only actual docstrings are returned. Triple-quoted strings used as ordinary
    values are ignored.
    """
    tree = _parse_python(code)
    if tree is None:
        return []

    docstrings: List[str] = []
    module_docstring = ast.get_docstring(tree)
    if module_docstring:
        docstrings.append(module_docstring)

    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings.append(docstring)
    return docstrings


def extract_imports(code: str) -> List[str]:
    """Return imported module names from ``import`` and ``from ... import`` statements."""
    tree = _parse_python(code)
    if tree is None:
        return []

    imports: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = "." * node.level + module
            imports.append(module or "." * node.level)
    return imports


def extract_decorators(code: str) -> List[str]:
    """Return decorator expressions applied to functions, methods, and classes."""
    tree = _parse_python(code)
    if tree is None:
        return []

    decorators: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators.extend(_node_to_source(code, decorator) for decorator in node.decorator_list)
    return decorators


def extract_async_functions(code: str) -> List[str]:
    """Return names of ``async def`` functions defined in *code*."""
    tree = _parse_python(code)
    if tree is None:
        return []
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)]


def extract_methods(code: str, class_name: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Return class-to-method mappings for classes defined in *code*.

    When ``class_name`` is provided, only that class is returned if present.
    """
    tree = _parse_python(code)
    if tree is None:
        return {}

    methods: Dict[str, List[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if class_name is not None and node.name != class_name:
            continue
        methods[node.name] = [
            child.name
            for child in node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
    return methods


def extract_constants(code: str) -> List[str]:
    """
    Return module-level constant names that follow the conventional UPPER_CASE style.
    """
    tree = _parse_python(code)
    if tree is None:
        return []

    constants: List[str] = []
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                for name in _walk_target_names(target):
                    if name.isupper():
                        constants.append(name)
        elif isinstance(node, ast.AnnAssign):
            for name in _walk_target_names(node.target):
                if name.isupper():
                    constants.append(name)
    return constants


def extract_assignments(code: str) -> List[str]:
    """Return assigned symbol names discovered in assignment statements."""
    tree = _parse_python(code)
    if tree is None:
        return []

    assignments: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                assignments.extend(_walk_target_names(target))
        elif isinstance(node, ast.AnnAssign):
            assignments.extend(_walk_target_names(node.target))
        elif isinstance(node, ast.AugAssign):
            assignments.extend(_walk_target_names(node.target))
    return assignments


def extract_type_hints(code: str) -> Dict[str, str]:
    """
    Return extracted type hints from function signatures and annotated assignments.

    Keys use a compact namespaced format such as ``func:param``,
    ``func:return``, and ``variable``.
    """
    tree = _parse_python(code)
    if tree is None:
        return {}

    hints: Dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in (
                list(node.args.posonlyargs)
                + list(node.args.args)
                + list(node.args.kwonlyargs)
            ):
                if arg.annotation is not None:
                    hints[f"{node.name}:{arg.arg}"] = ast.unparse(arg.annotation)
            if node.args.vararg and node.args.vararg.annotation is not None:
                hints[f"{node.name}:*{node.args.vararg.arg}"] = ast.unparse(node.args.vararg.annotation)
            if node.args.kwarg and node.args.kwarg.annotation is not None:
                hints[f"{node.name}:**{node.args.kwarg.arg}"] = ast.unparse(node.args.kwarg.annotation)
            if node.returns is not None:
                hints[f"{node.name}:return"] = ast.unparse(node.returns)
        elif isinstance(node, ast.AnnAssign):
            for name in _walk_target_names(node.target):
                hints[name] = ast.unparse(node.annotation)
    return hints


def extract_function_signatures(code: str) -> Dict[str, str]:
    """Return rendered signatures for synchronous and asynchronous functions."""
    tree = _parse_python(code)
    if tree is None:
        return {}
    return {node.name: _format_signature(node) for node in _iter_function_nodes(tree)}


def extract_class_bases(code: str) -> Dict[str, List[str]]:
    """Return base classes for each class defined in *code*."""
    tree = _parse_python(code)
    if tree is None:
        return {}
    return {
        node.name: [ast.unparse(base) for base in node.bases]
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    }


def extract_todo_comments(code: str) -> List[str]:
    """Return comments containing TODO-like markers."""
    return [
        comment
        for comment in extract_comments(code)
        if re.search(r"\b(TODO|FIXME|HACK|NOTE)\b", comment, re.IGNORECASE)
    ]


def extract_raise_statements(code: str) -> List[str]:
    """Return ``raise`` expressions from *code*."""
    tree = _parse_python(code)
    if tree is None:
        return []

    raises: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            if node.exc is None:
                raises.append("raise")
            else:
                raises.append(f"raise {ast.unparse(node.exc)}")
    return raises


def extract_return_statements(code: str) -> List[str]:
    """Return rendered return expressions from *code*."""
    tree = _parse_python(code)
    if tree is None:
        return []

    returns: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Return):
            if node.value is None:
                returns.append("return")
            else:
                returns.append(f"return {ast.unparse(node.value)}")
    return returns


def extract_code_blocks(text: str, language: Optional[str] = None) -> List[str]:
    """
    Return fenced Markdown code blocks from *text*.

    When ``language`` is supplied, only blocks with a matching fence language
    label are returned.
    """
    blocks: List[str] = []
    language_filter = language.casefold() if language is not None else None
    for match in CODE_BLOCK_PATTERN.finditer(text):
        block_language = match.group("language").strip().casefold()
        if language_filter is not None and block_language != language_filter:
            continue
        blocks.append(match.group("code").strip("\n"))
    return blocks


def format_snippet(code: str, indent: int = 4) -> str:
    """
    Normalize a code snippet for display or storage.

    The function dedents the snippet, strips surrounding blank lines, converts
    tabs to spaces, and reapplies a consistent left margin.
    """
    if indent < 0:
        raise ValueError("indent must be non-negative")
    normalized = _normalize_code(code).expandtabs(indent or 4)
    if not normalized:
        return ""
    prefix = " " * indent
    return "\n".join(prefix + line if line else "" for line in normalized.splitlines())


def truncate_snippet(code: str, max_lines: int = 30) -> str:
    """Truncate *code* to at most ``max_lines`` logical lines."""
    if max_lines <= 0:
        raise ValueError("max_lines must be positive")
    lines = _normalize_code(code).splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[:max_lines] + ["..."])


def snippet_line_count(code: str) -> int:
    """Return the number of non-empty logical lines in *code*."""
    return sum(1 for line in _normalize_code(code).splitlines() if line.strip())


def is_valid_python_snippet(code: str) -> bool:
    """Return ``True`` when *code* parses successfully as Python."""
    return _parse_python(code) is not None


def summarize_python_snippet(code: str) -> Dict[str, Any]:
    """
    Return a compact summary of the structure of a Python snippet.

    The output is shaped for logging, indexing, or quick UI previews.
    """
    tree = _parse_python(code)
    comments = extract_comments(code)
    functions = extract_functions(code)
    async_functions = extract_async_functions(code)
    classes = extract_class_defs(code)
    imports = extract_imports(code)
    docstrings = extract_docstrings(code)
    todos = extract_todo_comments(code)

    return {
        "is_valid_python": tree is not None,
        "line_count": snippet_line_count(code),
        "comment_count": len(comments),
        "todo_comment_count": len(todos),
        "function_count": len(functions),
        "async_function_count": len(async_functions),
        "class_count": len(classes),
        "import_count": len(imports),
        "docstring_count": len(docstrings),
        "functions": functions,
        "async_functions": async_functions,
        "classes": classes,
        "imports": imports,
    }


def extract_python_entities(code: str) -> Dict[str, Any]:
    """
    Return a structured snapshot of the Python entities present in *code*.

    This is the high-level entry point for callers that want one pass over a
    snippet instead of many separate extraction calls.
    """
    tree = _parse_python(code)
    if tree is None:
        return {
            "functions": [],
            "async_functions": [],
            "classes": [],
            "methods": {},
            "imports": [],
            "decorators": [],
            "constants": [],
            "assignments": [],
            "docstrings": [],
            "type_hints": {},
            "function_signatures": {},
            "class_bases": {},
            "todo_comments": [],
            "raise_statements": [],
            "return_statements": [],
        }

    return {
        "functions": extract_functions(code),
        "async_functions": extract_async_functions(code),
        "classes": extract_class_defs(code),
        "methods": extract_methods(code),
        "imports": extract_imports(code),
        "decorators": extract_decorators(code),
        "constants": extract_constants(code),
        "assignments": extract_assignments(code),
        "docstrings": extract_docstrings(code),
        "type_hints": extract_type_hints(code),
        "function_signatures": extract_function_signatures(code),
        "class_bases": extract_class_bases(code),
        "todo_comments": extract_todo_comments(code),
        "raise_statements": extract_raise_statements(code),
        "return_statements": extract_return_statements(code),
    }
