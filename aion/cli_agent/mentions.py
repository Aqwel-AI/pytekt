"""Expand @file / @folder / @git / @symbol / @web mentions in user messages."""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import List, Optional, Tuple

from ..tools.code_agent import list_files, read_file
from ..tools.workspace import Workspace
from .fetch_context import (
    expand_docs_token,
    expand_web_token,
    is_docs_token,
    is_web_token,
)
from .git_context import expand_git_mention, is_git_token
from .ignore import IgnoreMatcher
from .multi_workspace import MultiWorkspace
from .symbols import is_symbol_token, parse_symbol_token, resolve_symbol

_MENTION_RE = re.compile(
    r'@"([^"]+)"|@([^\s@]+)'
)
_MAX_TOTAL_CHARS = 30000
_MAX_FOLDER_FILES = 6
_MAX_FILE_LINES = 400

_TEXT_EXTENSIONS = frozenset({
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".js", ".ts",
    ".tsx", ".jsx", ".html", ".css", ".rs", ".go", ".java", ".c", ".cpp",
    ".h", ".sh", ".sql", ".ini", ".cfg", ".env.example",
})


def _is_probably_text(path: Path) -> bool:
    if path.suffix.lower() in _TEXT_EXTENSIONS:
        return True
    return path.suffix == "" and path.name.upper() in {"Makefile", "Dockerfile", "LICENSE"}


def _extract_mention_tokens(text: str) -> List[str]:
    tokens: List[str] = []
    for match in _MENTION_RE.finditer(text):
        quoted, bare = match.group(1), match.group(2)
        token = quoted if quoted is not None else bare
        if token:
            tokens.append(token)
    return tokens


def _strip_mentions(text: str) -> str:
    return _MENTION_RE.sub("", text).strip()


def _load_open_files(workspace_root: str) -> List[str]:
    sidecar = Path(workspace_root) / ".aion" / "open_files.json"
    if not sidecar.is_file():
        return []
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        updated = float(data.get("updated_at", 0))
        if time.time() - updated > 30:
            return []
        files = data.get("files") or []
        return [str(f.get("path")) for f in files if f.get("path")]
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return []


def _attach_file(ws: Workspace, rel: str, budget: int, matcher: IgnoreMatcher) -> Tuple[str, str, int]:
    if matcher.should_skip_path(rel):
        block = f'<file path="{rel}">\nSkipped (.aionignore)\n</file>'
        return rel, block, len(block)
    content = read_file(ws, rel, limit=_MAX_FILE_LINES)
    label = rel
    if content.startswith("Error"):
        block = f'<file path="{rel}">\n{content}\n</file>'
        used = len(block)
        return label, block, used
    if len(content) > budget:
        content = content[:budget] + "\n[... truncated ...]"
    block = f'<file path="{rel}">\n{content}\n</file>'
    return label, block, len(block)


def _attach_folder(ws: Workspace, rel: str, budget: int, matcher: IgnoreMatcher) -> Tuple[str, str, int]:
    listing = list_files(ws, rel, recursive=True)
    label = f"{rel.rstrip('/')}/"
    if listing.startswith("Error"):
        block = f'<folder path="{label}">\n{listing}\n</folder>'
        return label, block, len(block)

    lines = listing.splitlines()
    text_files: List[str] = []
    for line in lines:
        if line.endswith("/") or line.startswith("…"):
            continue
        if matcher.should_skip_path(line):
            continue
        if _is_probably_text(Path(line)):
            text_files.append(line)
        if len(text_files) >= _MAX_FOLDER_FILES:
            break

    parts = [f"<folder-listing path=\"{label}\">\n{listing}\n</folder-listing>"]
    used = len(parts[0])
    attached: List[str] = [label]
    for file_path in text_files:
        if used >= budget:
            break
        file_label, file_block, file_used = _attach_file(
            ws, file_path, min(budget - used, 8000), matcher
        )
        parts.append(file_block)
        used += file_used
        attached.append(file_label)

    block = "\n".join(parts)
    return ", ".join(attached), block, used


def expand_mentions(
    text: str,
    workspace_root: str,
    *,
    pinned_paths: Optional[List[str]] = None,
    extra_roots: Optional[List[str]] = None,
) -> Tuple[str, List[str]]:
    """
    Expand @ mentions into attached context.

    Returns (enriched_message, attachment_labels).
    """
    tokens = _extract_mention_tokens(text)
    pin_tokens = list(pinned_paths or [])
    open_files = _load_open_files(workspace_root)
    for p in open_files:
        if p not in pin_tokens and p not in tokens:
            pin_tokens.append(p)

    all_tokens = pin_tokens + [t for t in tokens if t not in pin_tokens]
    if not all_tokens and not tokens:
        return text, []

    multi = MultiWorkspace(workspace_root, extra_roots=extra_roots)
    matcher = IgnoreMatcher(workspace_root)
    blocks: List[str] = []
    labels: List[str] = []
    budget = _MAX_TOTAL_CHARS
    question = _strip_mentions(text) or text

    for token in all_tokens:
        if budget <= 0:
            labels.append("(budget exceeded)")
            break

        from_pin = token in (pinned_paths or []) or token in open_files

        if is_git_token(token):
            label, block = expand_git_mention(token, workspace_root)
            if block:
                if len(block) > budget:
                    block = block[:budget] + "\n[... truncated ...]"
                blocks.append(block)
                labels.append(("pinned " if from_pin else "") + label)
                budget -= len(block)
            continue

        if is_web_token(token):
            label, block = expand_web_token(token)
            if len(block) > budget:
                block = block[:budget] + "\n[... truncated ...]"
            blocks.append(block)
            labels.append(label)
            budget -= len(block)
            continue

        if is_docs_token(token):
            label, block = expand_docs_token(token)
            if len(block) > budget:
                block = block[:budget] + "\n[... truncated ...]"
            blocks.append(block)
            labels.append(label)
            budget -= len(block)
            continue

        if is_symbol_token(token):
            parsed = parse_symbol_token(token if not token.startswith("symbol:") else token[7:])
            if parsed:
                path, qualname = parsed
                label, block = resolve_symbol(workspace_root, path, qualname)
                if len(block) > budget:
                    block = block[:budget] + "\n[... truncated ...]"
                blocks.append(block)
                labels.append(label)
                budget -= len(block)
                continue

        rel = token.strip().lstrip("./")
        ws = multi.workspace_for(rel)
        try:
            resolved = ws.resolve(rel)
        except PermissionError as e:
            blocks.append(f'<error path="{rel}">{e}</error>')
            labels.append(f"{rel} (denied)")
            continue

        if resolved.is_dir() or rel.endswith("/"):
            folder_path = rel if rel.endswith("/") else rel + "/"
            label, block, used = _attach_folder(
                ws, folder_path.rstrip("/") or ".", budget, matcher
            )
            blocks.append(block)
            labels.append(("pinned " if from_pin else "") + label)
            budget -= used
        elif resolved.is_file():
            label, block, used = _attach_file(ws, rel, budget, matcher)
            blocks.append(block)
            labels.append(("pinned " if from_pin else "") + label)
            budget -= used
        else:
            blocks.append(f'<error path="{rel}">Not found or not a file/folder.</error>')
            labels.append(f"{rel} (missing)")

    if not blocks:
        return text, []

    enriched = question + "\n\n--- Attached context ---\n" + "\n".join(blocks)
    return enriched, labels
