"""Input prompt with optional @ path tab completion and fuzzy picker."""

from __future__ import annotations

import difflib
import os
import readline
from pathlib import Path
from typing import List, Optional, Set

from ..command_vocab import complete_slash_line

_COMPLETER_ROOT: Optional[str] = None
_COMPLETER_PREFIX: str = ""


def _skip_dir_names(workspace_root: str) -> Set[str]:
    try:
        from ..ignore import merged_skip_dirs

        return merged_skip_dirs(workspace_root)
    except Exception:
        from ...tools.code_agent import _SKIP_DIRS

        return set(_SKIP_DIRS)


def _collect_all_rel_paths(root: Path, skip: Set[str]) -> List[str]:
    out: List[str] = []
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in skip and not d.startswith(".")]
            rel_dir = Path(dirpath).relative_to(root)
            prefix = "" if str(rel_dir) == "." else str(rel_dir).replace("\\", "/") + "/"
            for name in filenames:
                if name.startswith("."):
                    continue
                out.append(prefix + name)
            for name in dirnames:
                out.append(prefix + name + "/")
    except OSError:
        pass
    return out


def _walk_rel_paths(root: Path, prefix: str, skip: Set[str]) -> List[str]:
    prefix = prefix.lstrip("./")
    if not prefix:
        candidates: List[str] = []
        try:
            for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
                if child.name.startswith("."):
                    continue
                if child.is_dir() and child.name in skip:
                    continue
                rel = child.relative_to(root).as_posix()
                candidates.append(rel + ("/" if child.is_dir() else ""))
        except OSError:
            pass
        return candidates

    all_paths = _collect_all_rel_paths(root, skip)
    if len(prefix) >= 2:
        fuzzy = difflib.get_close_matches(prefix, all_paths, n=8, cutoff=0.3)
        direct = [p for p in all_paths if p.startswith(prefix)]
        merged = direct + [p for p in fuzzy if p not in direct]
        return merged[:12]

    base = root
    partial = prefix
    if "/" in prefix:
        dir_part, _, file_part = prefix.rpartition("/")
        base = root / dir_part
        partial = file_part
    else:
        file_part = partial

    if not base.is_dir():
        return []

    out: List[str] = []
    try:
        for child in sorted(base.iterdir(), key=lambda p: p.name.lower()):
            if child.name.startswith("."):
                continue
            if child.is_dir() and child.name in skip:
                continue
            name = child.name
            if partial and not name.startswith(partial):
                continue
            rel = child.relative_to(root).as_posix()
            out.append(rel + ("/" if child.is_dir() else ""))
    except OSError:
        pass
    return out


def _at_path_completer(text: str, state: int) -> Optional[str]:
    global _COMPLETER_PREFIX
    if _COMPLETER_ROOT is None:
        return None

    if state == 0:
        line = readline.get_line_buffer()
        idx = readline.get_endidx()
        before = line[:idx]
        at = before.rfind("@")
        if at < 0:
            _COMPLETER_PREFIX = ""
            return None
        _COMPLETER_PREFIX = before[at + 1 :]
        skip = _skip_dir_names(_COMPLETER_ROOT)
        _at_path_completer.matches = _walk_rel_paths(  # type: ignore[attr-defined]
            Path(_COMPLETER_ROOT),
            _COMPLETER_PREFIX,
            skip,
        )

    matches = getattr(_at_path_completer, "matches", [])
    if state < len(matches):
        return matches[state]
    return None


def _unified_completer(text: str, state: int) -> Optional[str]:
    line = readline.get_line_buffer()
    if line.startswith("/"):
        if state == 0:
            candidates = complete_slash_line(line)
            _unified_completer.matches = candidates  # type: ignore[attr-defined]
        matches = getattr(_unified_completer, "matches", [])
        if state < len(matches):
            candidate = matches[state]
            # Return suffix to append from current cursor word
            idx = readline.get_endidx()
            prefix = line[:idx]
            if candidate.startswith(prefix):
                return candidate[len(prefix) :]
            return candidate
        return None
    return _at_path_completer(text, state)


def pick_fuzzy_path(workspace_root: str, partial: str) -> Optional[str]:
    """Interactive numbered pick when multiple fuzzy @ matches exist."""
    from .style import accent, dim

    skip = _skip_dir_names(workspace_root)
    all_paths = _collect_all_rel_paths(Path(workspace_root), skip)
    matches = [p for p in all_paths if partial.lower() in p.lower()]
    if not matches:
        matches = difflib.get_close_matches(partial, all_paths, n=10, cutoff=0.3)
    if len(matches) <= 1:
        return matches[0] if matches else None
    from .console import get_menu_choice, print_menu

    print_menu(matches, f"Pick @ path for {partial!r}")
    choice = get_menu_choice(matches)
    return matches[choice - 1]


def configure_input(workspace_root: str) -> None:
    global _COMPLETER_ROOT
    _COMPLETER_ROOT = os.path.abspath(workspace_root)
    try:
        readline.set_completer_delims(" \t\n;")
        readline.parse_and_bind("tab: complete")
        readline.set_completer(_unified_completer)
    except Exception:
        pass


def aion_input_prompt() -> str:
    from .style import accent, bold, dim

    return input(f"{accent(bold('You'))} {dim('» ')}").strip()
