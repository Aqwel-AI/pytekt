"""
PyTekt Agent TUI — Claude Code-style terminal user interface.

Features:
  • Claude Code aesthetics: refined typography, rounded frames, sleek prompt
  • Interactive arrow-key menus (↑ ↓ Enter) for provider, model, and mode switching
  • Claude Code tool cards with live execution timers, status badges & inline diffs
  • Multi-language syntax highlighting (Python, JS/TS, Shell, JSON, YAML, SQL, C/C++, Diff)
  • Markdown renderer with rounded code boxes, bullet styling, and inline badges
  • Persistent command history (~/.pytekt_history) via readline
  • Tab completion for slash commands and @file mentions
  • Live animated spinner with elapsed duration timer
  • Rich slash commands: /mode, /code, /talk, /connect, /model, /diff, /status, /clear, /reset, /help, /quit

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
"""

from __future__ import annotations

import getpass
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Terminal & Color Engine
# ---------------------------------------------------------------------------

_IS_TTY = sys.stdout.isatty()
_USE_COLOR = _IS_TTY and os.environ.get("NO_COLOR") is None


def _c(code: str, t: str) -> str:
    return f"\033[{code}m{t}\033[0m" if _USE_COLOR else t


def bold(t: str) -> str:        return _c("1", t)
def dim(t: str) -> str:         return _c("2", t)
def italic(t: str) -> str:      return _c("3", t)
def underline(t: str) -> str:   return _c("4", t)

# Core palette
def red(t: str) -> str:         return _c("38;5;203", t)
def green(t: str) -> str:       return _c("38;5;120", t)
def yellow(t: str) -> str:      return _c("38;5;221", t)
def blue(t: str) -> str:        return _c("38;5;75", t)
def magenta(t: str) -> str:     return _c("38;5;176", t)
def purple(t: str) -> str:      return _c("38;5;141", t)
def cyan(t: str) -> str:        return _c("38;5;80", t)
def orange(t: str) -> str:      return _c("38;5;215", t)
def coral(t: str) -> str:       return _c("38;5;209", t)
def white(t: str) -> str:       return _c("38;5;255", t)
def gray(t: str) -> str:        return _c("38;5;244", t)
def dark_gray(t: str) -> str:   return _c("38;5;238", t)
def bg_dark(t: str) -> str:     return _c("48;5;236", t)
def bg_code(t: str) -> str:     return _c("48;5;235", t)
def bg_badge(t: str) -> str:    return _c("48;5;237", t)


def _reset_seq() -> str:      return "\033[0m" if _USE_COLOR else ""
def _clear_line() -> str:     return "\033[2K\r" if _USE_COLOR else "\r"
def _hide_cursor() -> str:    return "\033[?25l" if _USE_COLOR else ""
def _show_cursor() -> str:    return "\033[?25h" if _USE_COLOR else ""


def W() -> int:
    return max(60, shutil.get_terminal_size((80, 24)).columns)


def _strip_ansi(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*[a-zA-Z]", "", s)


def _visible_len(s: str) -> int:
    return len(_strip_ansi(s))


def _hr(char: str = "─", w: int = 0) -> str:
    w = w or min(W() - 4, 88)
    return dark_gray(char * w)


# ---------------------------------------------------------------------------
# Readline Setup & Tab Auto-Completion
# ---------------------------------------------------------------------------

_SLASH_COMMANDS = [
    "/mode", "/code", "/talk", "/ml", "/bot", "/fix", "/review", "/undo",
    "/connect", "/model", "/diff", "/status", "/clear", "/reset", "/help", "/quit", "/exit",
]

_HISTORY_FILE = os.path.expanduser("~/.pytekt_history")


def _setup_readline(workspace: str) -> None:
    try:
        import readline
        readline.parse_and_bind("tab: complete")
        
        # Load history
        if os.path.exists(_HISTORY_FILE):
            try:
                readline.read_history_file(_HISTORY_FILE)
            except Exception:
                pass

        def _completer(text: str, state: int) -> Optional[str]:
            line = readline.get_line_buffer()
            
            # Slash commands completion
            if line.startswith("/"):
                matches = [cmd for cmd in _SLASH_COMMANDS if cmd.startswith(text)]
                return matches[state] if state < len(matches) else None

            # @file completion or path completion
            target = text
            prefix = ""
            if text.startswith("@"):
                prefix = "@"
                target = text[1:]

            dir_part, file_part = os.path.split(target)
            search_dir = os.path.join(workspace, dir_part) if dir_part else workspace
            
            try:
                candidates = []
                if os.path.isdir(search_dir):
                    for entry in os.listdir(search_dir):
                        if entry.startswith(".") and not file_part.startswith("."):
                            continue
                        if entry.startswith(file_part):
                            full_cand = os.path.join(dir_part, entry) if dir_part else entry
                            if os.path.isdir(os.path.join(search_dir, entry)):
                                full_cand += "/"
                            candidates.append(prefix + full_cand)
                candidates.sort()
                return candidates[state] if state < len(candidates) else None
            except Exception:
                return None

        readline.set_completer(_completer)
        readline.set_completer_delims(" \t\n`~!#$%^&*()=+[{]}\\|;:'\",<>?")
    except ImportError:
        pass


def _save_readline_history() -> None:
    try:
        import readline
        readline.set_history_length(1000)
        readline.write_history_file(_HISTORY_FILE)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Arrow-key Interactive Selector (TTY Raw Mode)
# ---------------------------------------------------------------------------

try:
    import termios as _termios
    import tty as _tty
    _HAS_RAW = True
except ImportError:
    _HAS_RAW = False


def _read_key() -> str:
    fd = sys.stdin.fileno()
    old = _termios.tcgetattr(fd)
    try:
        _tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch2 = sys.stdin.read(1)
            if ch2 == "[":
                ch3 = sys.stdin.read(1)
                if ch3 == "A": return "UP"
                if ch3 == "B": return "DOWN"
                if ch3 == "C": return "RIGHT"
                if ch3 == "D": return "LEFT"
            return "ESC"
        if ch in ("\r", "\n"):  return "ENTER"
        if ch == "\x03":        return "ESC"  # Ctrl-C
        if ch == "\x04":        return "ESC"  # Ctrl-D
        return ch
    finally:
        _termios.tcsetattr(fd, _termios.TCSADRAIN, old)


def _live_select(
    options: List[Tuple[str, str]],
    *,
    title: str = "",
    subtitle: str = "",
    current_idx: int = 0,
    allow_custom: bool = False,
    custom_label: str = "Enter manually…",
) -> int:
    all_opts = list(options)
    if allow_custom:
        all_opts.append(("__custom__", dim(custom_label)))

    n = len(all_opts)
    idx = max(0, min(current_idx, n - 1))

    if not _IS_TTY or not _HAS_RAW:
        if title:
            print("  " + bold(white(title)))
        if subtitle:
            print("  " + gray(subtitle))
        for i, (_, lbl) in enumerate(all_opts):
            star = bold(coral(">")) + " " if i == idx else "  "
            print(f"  {star}{bold(cyan(str(i + 1)))}. {lbl}")
        print()
        raw = _prompt_input(f"Enter number [1-{n}]", str(idx + 1))
        if raw.isdigit():
            r = int(raw) - 1
            if 0 <= r < n:
                return r
        return idx

    header_lines = 0
    if title:    header_lines += 1
    if subtitle: header_lines += 1
    if title or subtitle: header_lines += 1

    body_lines = 1 + n + 1 + 1 + 1
    total_lines = header_lines + body_lines

    def _draw(redraw: bool = False) -> None:
        if redraw:
            sys.stdout.write(f"\033[{total_lines}A")

        out: List[str] = []
        if title:
            out.append(_clear_line() + "  " + bold(white(title)))
        if subtitle:
            out.append(_clear_line() + "  " + gray(subtitle))
        if title or subtitle:
            out.append(_clear_line())

        out.append(_clear_line())

        for i, (_, lbl) in enumerate(all_opts):
            if i == idx:
                row = "  " + bold(coral(">")) + " " + bold(white(f" {lbl} "))
            else:
                row = "    " + dim(lbl)
            out.append(_clear_line() + row)

        out.append(_clear_line())
        out.append(
            _clear_line() + "  " +
            dark_gray("↑↓ navigate  ·  Enter select  ·  Esc cancel")
        )
        out.append(_clear_line())

        sys.stdout.write("\n".join(out) + "\n")
        sys.stdout.flush()

    _draw(redraw=False)

    sys.stdout.write(_hide_cursor())
    sys.stdout.flush()
    try:
        while True:
            key = _read_key()
            if key == "UP":
                idx = (idx - 1) % n
                _draw(redraw=True)
            elif key == "DOWN":
                idx = (idx + 1) % n
                _draw(redraw=True)
            elif key == "ENTER":
                break
            elif key in ("ESC", "q", "Q"):
                idx = -1
                break
    finally:
        sys.stdout.write(_show_cursor())
        sys.stdout.flush()

    if allow_custom and idx == len(options):
        return len(options)
    return idx


# ---------------------------------------------------------------------------
# Syntax Highlighting Engine (Pure Stdlib ANSI)
# ---------------------------------------------------------------------------

_PY_KEYWORDS = {
    "def", "class", "return", "import", "from", "if", "else", "elif",
    "for", "while", "try", "except", "finally", "with", "as", "pass",
    "break", "continue", "and", "or", "not", "in", "is", "True", "False",
    "None", "lambda", "yield", "async", "await", "raise", "del", "assert",
    "type", "match", "case", "self", "cls",
}

_JS_KEYWORDS = {
    "const", "let", "var", "function", "return", "import", "from", "export",
    "default", "if", "else", "for", "while", "do", "switch", "case", "break",
    "continue", "try", "catch", "finally", "throw", "new", "class", "extends",
    "this", "async", "await", "yield", "typeof", "instanceof", "in", "of",
    "true", "false", "null", "undefined",
}


def _hl_python(line: str) -> str:
    if not _USE_COLOR:
        return line
    stripped = line.lstrip()
    if stripped.startswith("#"):
        return gray(line)
    parts = re.split(r'(""".*?"""|\'\'\'.*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\'|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*\b|[^\w\s])', line)
    out = []
    for p in parts:
        if not p: continue
        if (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
            out.append(green(p))
        elif p in _PY_KEYWORDS:
            out.append(coral(p))
        elif re.fullmatch(r"\d+(?:\.\d+)?", p):
            out.append(yellow(p))
        elif re.fullmatch(r"[A-Z][A-Za-z0-9_]*", p):
            out.append(cyan(p))
        elif re.fullmatch(r"[A-Z_][A-Z0-9_]{2,}", p):
            out.append(purple(p))
        else:
            out.append(p)
    return "".join(out)


def _hl_js(line: str) -> str:
    if not _USE_COLOR:
        return line
    stripped = line.lstrip()
    if stripped.startswith("//") or stripped.startswith("/*"):
        return gray(line)
    parts = re.split(r'(`.*?`|"[^"\n]*"|\'[^\'\n]*\'|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*\b|[^\w\s])', line)
    out = []
    for p in parts:
        if not p: continue
        if (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")) or (p.startswith('`') and p.endswith('`')):
            out.append(green(p))
        elif p in _JS_KEYWORDS:
            out.append(coral(p))
        elif re.fullmatch(r"\d+(?:\.\d+)?", p):
            out.append(yellow(p))
        elif re.fullmatch(r"[A-Z][A-Za-z0-9_]*", p):
            out.append(cyan(p))
        else:
            out.append(p)
    return "".join(out)


def _hl_json(line: str) -> str:
    if not _USE_COLOR:
        return line
    line = re.sub(r'("[\w\-_]+")(\s*:)', lambda m: cyan(m.group(1)) + m.group(2), line)
    line = re.sub(r':\s*("[^"]*")', lambda m: ": " + green(m.group(1)), line)
    line = re.sub(r'\b(true|false|null)\b', lambda m: coral(m.group(1)), line)
    line = re.sub(r'\b(\d+(?:\.\d+)?)\b', lambda m: yellow(m.group(1)), line)
    return line


def _hl_yaml(line: str) -> str:
    if not _USE_COLOR:
        return line
    if line.strip().startswith("#"):
        return gray(line)
    line = re.sub(r'^(\s*[\w\-_]+)(\s*:)', lambda m: cyan(m.group(1)) + m.group(2), line)
    line = re.sub(r':\s*("[^"]*"|\'[^\']*\')', lambda m: ": " + green(m.group(1)), line)
    line = re.sub(r'\b(true|false|null|yes|no)\b', lambda m: coral(m.group(1)), line)
    return line


def _hl_shell(line: str) -> str:
    if not _USE_COLOR:
        return line
    stripped = line.lstrip()
    if stripped.startswith("#"):
        return gray(line)
    m = re.match(r'^(\s*)(\S+)(.*)', line, re.DOTALL)
    if m:
        return m.group(1) + bold(cyan(m.group(2))) + white(m.group(3))
    return line


def _hl_diff(line: str) -> str:
    if not _USE_COLOR:
        return line
    if line.startswith("+"):
        return green(line)
    if line.startswith("-"):
        return red(line)
    if line.startswith("@@"):
        return cyan(line)
    return gray(line)


_LANG_HIGHLIGHTERS: Dict[str, Callable[[str], str]] = {
    "python": _hl_python, "py": _hl_python,
    "javascript": _hl_js, "js": _hl_js, "typescript": _hl_js, "ts": _hl_js, "jsx": _hl_js, "tsx": _hl_js,
    "json": _hl_json, "yaml": _hl_yaml, "yml": _hl_yaml,
    "bash": _hl_shell, "sh": _hl_shell, "shell": _hl_shell, "zsh": _hl_shell,
    "diff": _hl_diff, "patch": _hl_diff,
}


def _render_code_block(lang: str, code: str) -> str:
    w = min(W() - 4, 96)
    hl = _LANG_HIGHLIGHTERS.get(lang.lower(), lambda l: l)
    inner_w = w - 4
    label = f" {lang} " if lang else " code "

    top = "  " + dark_gray("╭─") + coral(bold(label)) + dark_gray("─" * max(2, inner_w - len(label)) + "╮")
    lines = code.split("\n")
    body = []
    for raw in lines:
        colored = hl(raw)
        pad = " " * max(0, inner_w - _visible_len(raw))
        body.append("  " + dark_gray("│ ") + colored + pad + dark_gray(" │"))
    bot = "  " + dark_gray("╰" + "─" * (inner_w + 2) + "╯")
    return "\n".join([top] + body + [bot])


# ---------------------------------------------------------------------------
# Claude-style Markdown Renderer
# ---------------------------------------------------------------------------

def render_md(text: str) -> str:
    lines = text.split("\n")
    out: List[str] = []
    in_code = False
    lang = ""
    code_buf: List[str] = []

    for line in lines:
        if line.startswith("```"):
            if in_code:
                out.append(_render_code_block(lang, "\n".join(code_buf)))
                in_code = False
                lang = ""
                code_buf = []
            else:
                in_code = True
                lang = line[3:].strip()
            continue
        if in_code:
            code_buf.append(line)
            continue

        # Headings
        if line.startswith("### "):
            out.append(bold(coral("  ### " + line[4:])))
            continue
        if line.startswith("## "):
            out.append(bold(cyan("  ## " + line[3:])))
            continue
        if line.startswith("# "):
            out.append(bold(white("  # " + line[2:])))
            continue

        # Horizontal rule
        if re.fullmatch(r"[-*_]{3,}\s*", line):
            out.append("  " + _hr())
            continue

        # Blockquote
        if line.startswith("> "):
            out.append("  " + dark_gray("│ ") + italic(gray(line[2:])))
            continue

        # Bullet list
        if line.startswith(("- ", "* ", "+ ")):
            rest = line[2:]
            rest = re.sub(r"\*\*(.+?)\*\*", lambda m: bold(white(m.group(1))), rest)
            rest = re.sub(r"`([^`]+)`", lambda m: bg_badge(cyan(f" {m.group(1)} ")), rest)
            out.append("  " + coral("•") + " " + rest)
            continue

        # Numbered list
        m = re.match(r"^(\d+)[.)]\s+(.*)", line)
        if m:
            rest = m.group(2)
            rest = re.sub(r"\*\*(.+?)\*\*", lambda m2: bold(white(m2.group(1))), rest)
            rest = re.sub(r"`([^`]+)`", lambda m2: bg_badge(cyan(f" {m2.group(1)} ")), rest)
            out.append("  " + bold(cyan(m.group(1) + ".")) + " " + rest)
            continue

        # Inline formatting
        formatted = re.sub(r"\*\*(.+?)\*\*", lambda m: bold(white(m.group(1))), line)
        formatted = re.sub(r"`([^`]+)`", lambda m: bg_badge(cyan(f" {m.group(1)} ")), formatted)
        out.append(formatted)

    if in_code and code_buf:
        out.append(_render_code_block(lang, "\n".join(code_buf)))

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Claude-Style Live Animated Spinner with Timer
# ---------------------------------------------------------------------------

_BRAILLE_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"] if _USE_COLOR else ["-", "\\", "|", "/"]


class Spinner:
    def __init__(self, label: str = "Thinking") -> None:
        self.label = label
        self._stop = threading.Event()
        self._t: Optional[threading.Thread] = None
        self._start_time = 0.0

    def _loop(self) -> None:
        sys.stdout.write(_hide_cursor())
        sys.stdout.flush()
        i = 0
        while not self._stop.is_set():
            elapsed = time.time() - self._start_time
            frame = _BRAILLE_FRAMES[i % len(_BRAILLE_FRAMES)]
            timer = f"({elapsed:.1f}s)" if elapsed >= 0.5 else ""
            sys.stdout.write(f"\r  {coral(frame)} {gray(self.label)} {dark_gray(timer)}   ")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        sys.stdout.write(_clear_line())
        sys.stdout.write(_show_cursor())
        sys.stdout.flush()

    def start(self) -> None:
        self._start_time = time.time()
        self._stop.clear()
        self._t = threading.Thread(target=self._loop, daemon=True)
        self._t.start()

    def stop(self, final: str = "") -> None:
        self._stop.set()
        if self._t:
            self._t.join(timeout=0.3)
        if final:
            print(final)

    def update(self, label: str) -> None:
        self.label = label


# ---------------------------------------------------------------------------
# Claude Code Tool Execution Cards
# ---------------------------------------------------------------------------

def _render_diff_card(path: str, old_str: str, new_str: str) -> None:
    """Render a Claude-style diff card for edit operations."""
    w = min(W() - 4, 92)
    inner_w = w - 4
    header = f" diff: {os.path.basename(path)} "
    print("    " + dark_gray("╭─") + yellow(bold(header)) + dark_gray("─" * max(2, inner_w - len(header)) + "╮"))
    
    for line in old_str.split("\n"):
        truncated = line[:inner_w - 4]
        pad = " " * max(0, inner_w - _visible_len(truncated) - 2)
        print("    " + dark_gray("│ ") + red("- " + truncated) + pad + dark_gray(" │"))
    for line in new_str.split("\n"):
        truncated = line[:inner_w - 4]
        pad = " " * max(0, inner_w - _visible_len(truncated) - 2)
        print("    " + dark_gray("│ ") + green("+ " + truncated) + pad + dark_gray(" │"))
    
    print("    " + dark_gray("╰" + "─" * (inner_w + 2) + "╯"))


def _render_output_card(title: str, text: str, max_lines: int = 8) -> None:
    """Render command stdout/stderr or tool output in a rounded box."""
    if not text.strip():
        return
    w = min(W() - 4, 92)
    inner_w = w - 4
    header = f" {title} "
    print("    " + dark_gray("╭─") + cyan(bold(header)) + dark_gray("─" * max(2, inner_w - len(header)) + "╮"))
    
    lines = text.split("\n")
    for raw in lines[:max_lines]:
        truncated = raw[:inner_w - 2]
        pad = " " * max(0, inner_w - _visible_len(truncated))
        print("    " + dark_gray("│ ") + gray(truncated) + pad + dark_gray(" │"))
    
    if len(lines) > max_lines:
        more_msg = f"... +{len(lines) - max_lines} more lines"
        pad = " " * max(0, inner_w - len(more_msg))
        print("    " + dark_gray("│ ") + dark_gray(more_msg) + pad + dark_gray(" │"))
    
    print("    " + dark_gray("╰" + "─" * (inner_w + 2) + "╯"))


def _render_error_card(title: str, message: str, hint: Optional[str] = None) -> None:
    """Render a Claude-style error card with rounded frame and helpful hints."""
    w = min(W() - 4, 92)
    inner_w = w - 4
    header = f" [ERR] {title} "
    print()
    print("  " + dark_gray("╭─") + red(bold(header)) + dark_gray("─" * max(2, inner_w - len(header)) + "╮"))
    
    for line in message.strip().split("\n"):
        truncated = line[:inner_w - 2]
        pad = " " * max(0, inner_w - _visible_len(truncated))
        print("  " + dark_gray("│ ") + white(truncated) + pad + dark_gray(" │"))
    
    if hint:
        print("  " + dark_gray("│" + " " * (inner_w + 2) + "│"))
        for hline in hint.strip().split("\n"):
            truncated = hline[:inner_w - 2]
            pad = " " * max(0, inner_w - _visible_len(truncated))
            print("  " + dark_gray("│ ") + cyan(truncated) + pad + dark_gray(" │"))
            
    print("  " + dark_gray("╰" + "─" * (inner_w + 2) + "╯"))
    print()


def print_tool_start(name: str, args: Dict[str, Any]) -> None:
    """Print tool invocation header in Claude Code style."""
    if name == "read_file":
        path = args.get("path", "")
        print(f"\n  {coral('>')} {bold(white('Read'))} {cyan(path)}")
    elif name == "write_file":
        path = args.get("path", "")
        print(f"\n  {coral('>')} {bold(white('Write'))} {cyan(path)}")
    elif name == "edit_file":
        path = args.get("path", "")
        print(f"\n  {coral('>')} {bold(white('Edit'))} {cyan(path)}")
    elif name == "run_command":
        cmd = args.get("command", "")
        print(f"\n  {coral('>')} {bold(white('Bash'))} {green(cmd)}")
    elif name in ("search_files", "glob_search"):
        pat = args.get("pattern", "")
        print(f"\n  {coral('>')} {bold(white('Search'))} {yellow(f'pattern=\"{pat}\"')}")
    elif name == "list_files":
        path = args.get("path", ".")
        print(f"\n  {coral('>')} {bold(white('List directory'))} {cyan(path)}")
    else:
        print(f"\n  {coral('>')} {bold(white(name))}")


def print_tool_finish(name: str, result: str, args: Optional[Dict[str, Any]] = None) -> None:
    """Print tool completion details, diffs, and result summary."""
    args = args or {}
    is_err = "error" in str(result).lower() or "exception" in str(result).lower()
    
    if name == "edit_file" and not is_err:
        old_s = args.get("old_string", "")
        new_s = args.get("new_string", "")
        path = args.get("path", "")
        if old_s and new_s:
            _render_diff_card(path, old_s, new_s)
        print(f"    {dark_gray('└─')} {green('[OK]')} {gray('applied replacement')}")
    elif name == "run_command":
        if result and not is_err:
            _render_output_card("output", result, max_lines=6)
            print(f"    {dark_gray('└─')} {green('[OK]')} {gray('completed with exit code 0')}")
        elif is_err:
            _render_output_card("error", result, max_lines=6)
            print(f"    {dark_gray('└─')} {red('[ERR]')} {red('command failed')}")
    elif name == "read_file" and not is_err:
        line_count = len(result.split("\n"))
        print(f"    {dark_gray('└─')} {green('[OK]')} {gray(f'read {line_count} lines ({len(result)} bytes)')}")
    elif is_err:
        print(f"    {dark_gray('└─')} {red('[ERR]')} {red(str(result)[:80])}")
    else:
        summary = str(result).split("\n")[0][:70]
        print(f"    {dark_gray('└─')} {green('[OK]')} {gray(summary)}")


# ---------------------------------------------------------------------------
# Provider & Model Definitions
# ---------------------------------------------------------------------------

PROVIDERS: Dict[str, Dict[str, Any]] = {
    "ollama": {
        "label":       "Ollama (Local)",
        "subtitle":    "Run local models without API keys",
        "icon":        "[ollama]",
        "needs_key":   False,
        "env_key":     None,
        "default_model": "llama3.2",
        "models":      [],
        "color":       purple,
    },
    "anthropic": {
        "label":       "Anthropic",
        "subtitle":    "Claude 3.5 Sonnet, Claude 3.5 Haiku, Opus",
        "icon":        "[anthropic]",
        "needs_key":   True,
        "env_key":     "ANTHROPIC_API_KEY",
        "default_model": "claude-3-5-sonnet-latest",
        "models":      [
            "claude-3-5-sonnet-latest", "claude-3-5-haiku-latest",
            "claude-3-opus-latest", "claude-3-haiku-20240307",
        ],
        "color":       coral,
    },
    "openai": {
        "label":       "OpenAI",
        "subtitle":    "GPT-4o, GPT-4o-mini, o1, o3-mini",
        "icon":        "[openai]",
        "needs_key":   True,
        "env_key":     "OPENAI_API_KEY",
        "default_model": "gpt-4o",
        "models":      ["gpt-4o", "gpt-4o-mini", "o3-mini", "gpt-4-turbo"],
        "color":       green,
    },
    "gemini": {
        "label":       "Google Gemini",
        "subtitle":    "Gemini 2.0 Flash, Gemini 1.5 Pro",
        "icon":        "[gemini]",
        "needs_key":   True,
        "env_key":     "GEMINI_API_KEY",
        "default_model": "gemini-2.0-flash",
        "models":      [
            "gemini-2.0-flash", "gemini-2.0-flash-lite",
            "gemini-1.5-pro", "gemini-1.5-flash",
        ],
        "color":       blue,
    },
    "deepseek": {
        "label":       "DeepSeek",
        "subtitle":    "DeepSeek V3, DeepSeek R1 (reasoning)",
        "icon":        "[deepseek]",
        "needs_key":   True,
        "env_key":     "DEEPSEEK_API_KEY",
        "default_model": "deepseek-chat",
        "models":      ["deepseek-chat", "deepseek-reasoner"],
        "color":       cyan,
    },
    "nvidia": {
        "label":       "NVIDIA NIM",
        "subtitle":    "LLaMA 3.3 70B, Mistral, Nemotron",
        "icon":        "[nvidia]",
        "needs_key":   True,
        "env_key":     "NVIDIA_API_KEY",
        "default_model": "meta/llama-3.1-70b-instruct",
        "models":      [
            "meta/llama-3.1-8b-instruct",
            "meta/llama-3.3-70b-instruct",
            "mistralai/mistral-7b-instruct-v0.3",
            "deepseek-ai/deepseek-v4-flash",
        ],
        "color":       green,
    },
    "openai_compatible": {
        "label":       "Custom OpenAI-Compatible",
        "subtitle":    "LM Studio, vLLM, llama.cpp, LocalAI",
        "icon":        "[custom]",
        "needs_key":   False,
        "env_key":     None,
        "default_model": "local-model",
        "models":      [],
        "color":       yellow,
    },
}

_PROVIDER_KEYS = list(PROVIDERS.keys())


# ---------------------------------------------------------------------------
# Git Info Helper
# ---------------------------------------------------------------------------

def _get_git_branch(cwd: str) -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True
        )
        return res.stdout.strip()
    except Exception:
        return ""


def _get_git_diff_summary(cwd: str) -> str:
    try:
        res = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True
        )
        return res.stdout.strip()
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Claude Code Header & Prompt
# ---------------------------------------------------------------------------

def print_banner(version: str, provider: str, model: str, mode: str, workspace: str) -> None:
    """Claude Code-style clean frame and welcome screen."""
    w = min(W() - 4, 88)
    branch = _get_git_branch(workspace)
    branch_str = f" ({branch})" if branch else ""
    rel_ws = os.path.relpath(workspace)
    if rel_ws == ".":
        rel_ws = os.path.basename(os.path.abspath(workspace))
    
    _mode_tags = {
        "code": green("[CODE]"),
        "talk": purple("[TALK]"),
        "ml": blue("[ML]"),
        "bot": cyan("[BOT]"),
        "fix": yellow("[FIX]"),
        "review": magenta("[REVIEW]"),
    }
    mode_tag = _mode_tags.get(mode.lower(), green(f"[{mode.upper()}]"))
    
    print()
    print("  " + dark_gray("╭─ ") + coral(bold("pytekt agent")) + dark_gray(f" v{version} ─") + dark_gray("─" * max(2, w - 24 - len(version)) + "╮"))
    print("  " + dark_gray("│ ") + f"{mode_tag}  ·  {coral(provider)}/{yellow(model)}  ·  {gray(rel_ws)}{dark_gray(branch_str)}" + " " * max(0, w - _visible_len(f"{mode_tag}  ·  {provider}/{model}  ·  {rel_ws}{branch_str}") - 2) + dark_gray(" │"))
    print("  " + dark_gray("╰" + "─" * (w + 2) + "╯"))
    print()
    print("  " + gray("Autonomous AI coding assistant in your terminal."))
    print("  " + dark_gray("Type your task directly  ·  ") + cyan("/mode") + dark_gray(" switch mode  ·  ") + cyan("/connect") + dark_gray(" change model  ·  ") + cyan("/help") + dark_gray(" commands"))
    print()


def render_prompt_line(workspace: str, provider: str, model: str, mode: str) -> str:
    """Claude Code-style single prompt glyph."""
    return "\n  " + coral(bold(">")) + " "


# ---------------------------------------------------------------------------
# /status Card
# ---------------------------------------------------------------------------

def print_status(
    provider: str,
    model: str,
    mode: str,
    workspace: str,
    turns: int,
    cfg: Dict[str, Any],
) -> None:
    w = min(W() - 4, 80)
    branch = _get_git_branch(workspace)
    _mode_tags = {
        "code": green("[CODE] Mode (Autonomous agent)"),
        "talk": purple("[TALK] Mode (Technical thought partner)"),
        "ml": blue("[ML] Mode (Data science & research)"),
        "bot": cyan("[BOT] Mode (Bot architect)"),
        "fix": yellow("[FIX] Mode (Self-healing test runner)"),
        "review": magenta("[REVIEW] Mode (Git diff auditor)"),
    }
    mode_str = _mode_tags.get(mode.lower(), green(f"[{mode.upper()}] Mode"))
    
    print()
    print("  " + dark_gray("╭─ ") + bold(white("Session Status")) + dark_gray(" ─" * (w - 18) + "╮"))
    print(f"  {dark_gray('│')}  {gray('Mode:')}        {mode_str}")
    print(f"  {dark_gray('│')}  {gray('Provider:')}    {coral(bold(provider))}")
    print(f"  {dark_gray('│')}  {gray('Model:')}       {yellow(model)}")
    print(f"  {dark_gray('│')}  {gray('Workspace:')}   {blue(os.path.abspath(workspace))}" + (gray(f" (git:{branch})") if branch else ""))
    print(f"  {dark_gray('│')}  {gray('Turns:')}       {white(str(turns))}")
    print("  " + dark_gray("├─ ") + bold(white("Configured Providers")) + dark_gray(" ─" * (w - 24) + "┤"))
    
    keys_cfg = cfg.get("keys") or {}
    for pname, pinfo in PROVIDERS.items():
        if not pinfo["needs_key"]:
            status = green("[OK]  (no key required)")
        else:
            env_var = pinfo["env_key"] or ""
            if os.environ.get(env_var):
                status = green(f"[OK]  env:{env_var}")
            elif keys_cfg.get(f"{pname}_api_key"):
                status = green("[OK]  saved in config")
            else:
                status = dark_gray("[--]  not configured")
        print(f"  {dark_gray('│')}  {white(pinfo['icon']):<12} {white(pname):<16} {status}")
    
    print("  " + dark_gray("╰" + "─" * w + "╯"))
    print()


# ---------------------------------------------------------------------------
# /diff Command
# ---------------------------------------------------------------------------

def run_diff_command(workspace: str) -> None:
    """Print colored git diff of current session changes."""
    diff_text = _get_git_diff_summary(workspace)
    if not diff_text:
        print("  " + gray("No uncommitted changes in workspace."))
        return
    
    print()
    print("  " + bold(white("Uncommitted Git Changes:")))
    print("  " + _hr())
    for line in diff_text.split("\n"):
        print("    " + gray(line))
    print()


# ---------------------------------------------------------------------------
# /help Screen
# ---------------------------------------------------------------------------

HELP_SCREEN = """
  {h}PyTekt Agent Commands{r}
  {hr}
  {c}/mode{r} {y}[mode]{r}            Switch mode: code, talk, ml, bot, fix, review
  {c}/code{r}                  Autonomous coding (file read/edit, bash tools)
  {c}/talk{r}                  Conversational thought partner & explanations
  {c}/ml{r}                    Autonomous data science & ML research partner
  {c}/bot{r}                   Bot architect & scaffolding (Telegram/Discord/Slack)
  {c}/fix{r}                   Run self-healing pytest debugger loop
  {c}/review{r}                Audit git diff for leaked secrets, code smells & PR draft
  {c}/undo{r}                  Rollback the most recent file edit made by agent
  {c}/connect{r}               Interactive AI provider & model switcher
  {c}/model{r} {y}<name>{r}           Change model without switching provider
  {c}/diff{r}                  Show git diff summary of current workspace changes
  {c}/status{r}                Display session metadata, turns, and API keys
  {c}/clear{r}                 Clear screen and refresh header
  {c}/reset{r}                 Clear conversation history (start fresh turn)
  {c}/help{r}                  Show this command reference
  {c}/quit{r}                  Exit agent mode ({g}or Ctrl-D{r})

  {h}Agent Modes{r}
  {hr}
  {grn}[CODE]{r}   Reads files, performs precision diffs, runs tests and shell commands.
  {mg}[TALK]{r}   High-level technical conversation, architecture reviews, debugging.
  {bl}[ML]{r}     Explores datasets, trains PyTekt models, plots metrics & ROC curves.
  {cy}[BOT]{r}    Scaffolds Telegram/Discord/Slack bots and validates with BotTestClient.
  {yl}[FIX]{r}    Autonomously diagnoses failing tests, edits code, and self-heals.
  {mg}[REVIEW]{r} Audits uncommitted changes, scans for secrets, drafts commit messages.

  {h}Tips{r}
  {hr}
  • Type {c}@file.py{r} to inject file contents into your prompt
  • Type {c}@git{r} or {c}@diff{r} to inject current git diff
  • Type {c}@tests{r} to inject recent pytest results
  • Type {c}/undo{r} to instantly revert the agent's last file modification
  • Up / Down arrow keys cycle through command history ({g}~/.pytekt_history{r})
  • Press {c}Ctrl+C{r} to interrupt a running command or generation
""".format(
    h=bold(white("")), r=_reset_seq(),
    hr=dim("─" * 48),
    c=bold(cyan("")), y=yellow(""), g=gray(""), grn=green(""),
    mg=purple(""), bl=blue(""), cy=cyan(""), yl=yellow(""),
)


# ---------------------------------------------------------------------------
# Provider & Model Interactive Connect Flows
# ---------------------------------------------------------------------------

def _fetch_ollama_models(host: str = "http://localhost:11434") -> List[str]:
    import ssl, urllib.request, urllib.error
    url = f"{host.rstrip('/')}/api/tags"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=3, context=ctx) as r:
            data = json.loads(r.read())
        return [m["name"] for m in data.get("models", []) if m.get("name")]
    except Exception:
        return []


def _fetch_nvidia_models(api_key: str) -> List[str]:
    try:
        from ..providers.nvidia_provider import NvidiaProvider
        return NvidiaProvider.list_models(api_key=api_key)
    except Exception:
        return []


def _prompt_input(label: str, default: str = "", secret: bool = False) -> str:
    dflt = f" [{dim(default)}]" if default else ""
    prompt_str = "  " + bold(coral("›")) + " " + label + dflt + " "
    try:
        if secret:
            return getpass.getpass(prompt_str).strip() or default
        sys.stdout.write(prompt_str)
        sys.stdout.flush()
        return input().strip() or default
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def _pick_provider(current: str) -> int:
    try:
        default_idx = _PROVIDER_KEYS.index(current)
    except ValueError:
        default_idx = 0

    options: List[Tuple[str, str]] = []
    for key, info in PROVIDERS.items():
        key_badge = dim(" (no key)") if not info["needs_key"] else dim(" (API key)")
        active = "  " + green("[active]") if key == current else ""
        label = (
            f"{info['icon']}  " +
            info["color"](bold(f"{info['label']:<18}")) +
            "  " + gray(info["subtitle"]) +
            key_badge + active
        )
        options.append((key, label))

    return _live_select(
        options,
        title="Connect to AI Provider",
        subtitle="Use ↑ ↓ to navigate, Enter to select",
        current_idx=default_idx,
    )


def _pick_model(key: str, info: Dict[str, Any], existing_key: str = "") -> str:
    models: List[str] = []

    if key == "ollama":
        spin = Spinner("Querying Ollama models")
        spin.start()
        models = _fetch_ollama_models()
        spin.stop()
    elif key == "nvidia" and existing_key:
        spin = Spinner("Querying NVIDIA NIM catalog")
        spin.start()
        models = _fetch_nvidia_models(existing_key)
        spin.stop()

    if not models:
        models = list(info["models"]) or [info["default_model"]]

    show = models[:14]
    if models and default not in models:
        default = models[0]
    try:
        default_idx = show.index(default)
    except ValueError:
        default_idx = 0

    options = [(m, (coral("* ") if m == default else "  ") + m) for m in show]

    idx = _live_select(
        options,
        title=f"Select Model  —  {info['label']}",
        subtitle="Use ↑ ↓ to navigate, Enter to select",
        current_idx=default_idx,
        allow_custom=True,
        custom_label="Type custom model name…",
    )

    if idx == -1:
        return default
    if idx >= len(show):
        return _prompt_input("Model name", default)
    return show[idx]


def run_connect(cfg: Dict[str, Any], current_provider: str, current_model: str) -> Tuple[str, str, Dict[str, Any]]:
    print()
    print("  " + bold(white("[+]  Switch AI Provider")))
    print("  " + dark_gray(f"Current: {current_provider} / {current_model}"))
    print()

    pidx = _pick_provider(current_provider)
    if pidx == -1:
        print("  " + gray("Cancelled."))
        return current_provider, current_model, cfg

    chosen_key = _PROVIDER_KEYS[pidx]
    info = PROVIDERS[chosen_key]

    if chosen_key == "openai_compatible":
        saved_url = cfg.get("agent", {}).get("custom_base_url", "http://localhost:1234/v1")
        base_url = _prompt_input("Base URL", saved_url)
        cfg.setdefault("agent", {})["custom_base_url"] = base_url

    if chosen_key == "ollama":
        saved_host = cfg.get("agent", {}).get("ollama_host", "http://localhost:11434")
        host = _prompt_input("Ollama host", saved_host)
        cfg.setdefault("agent", {})["ollama_host"] = host

    existing_key = ""
    if info["needs_key"] and info["env_key"]:
        env_val = os.environ.get(info["env_key"], "")
        cfg_val = (cfg.get("keys") or {}).get(f"{chosen_key}_api_key", "")
        existing_key = env_val or cfg_val

        if not existing_key:
            print("  " + yellow("[!]") + f"  API key required for {bold(info['label'])}.")
            new_key = _prompt_input("API key", secret=True)
            if new_key:
                existing_key = new_key
                cfg.setdefault("keys", {})[f"{chosen_key}_api_key"] = new_key

    chosen_model = _pick_model(chosen_key, info, existing_key)
    cfg.setdefault("agent", {})["provider"] = chosen_key
    cfg["agent"]["model"] = chosen_model

    print()
    print("  " + green("[OK]") + "  Connected: " + info["color"](bold(chosen_key)) + gray(" / ") + yellow(chosen_model))
    print()
    return chosen_key, chosen_model, cfg


# ---------------------------------------------------------------------------
# Assistant Reply Formatter
# ---------------------------------------------------------------------------

def print_reply(text: str) -> None:
    """Print assistant reply rendered with Claude Code styling."""
    rendered = render_md(text)
    print()
    print(rendered)
    print()


# ---------------------------------------------------------------------------
# Main TUI REPL Loop
# ---------------------------------------------------------------------------

def run_tui(
    session_factory: Callable[..., Any],
    workspace: str,
    provider: str,
    model: str,
    mode: str = "code",
    cfg: Optional[Dict[str, Any]] = None,
    save_cfg_fn: Optional[Callable[[Dict[str, Any]], None]] = None,
    version: str = "0.2.1",
    task: Optional[str] = None,
) -> None:
    if cfg is None:
        cfg = {}
    if save_cfg_fn is None:
        save_cfg_fn = lambda c: None

    _setup_readline(workspace)
    print_banner(version, provider, model, mode, workspace)

    # Initial session spin-up
    spin = Spinner("Initializing agent session")
    spin.start()
    try:
        session = session_factory(provider=provider, model=model, mode=mode, workspace_root=workspace, cfg=cfg)
        has_key = getattr(session, "has_key", True)
        if not has_key and provider != "ollama":
            spin.stop(green("  [OK]") + gray(f"  Ready ({mode.upper()} mode)") + yellow("  [!] No API key configured"))
            print(dark_gray("     → Type ") + cyan("/connect") + dark_gray(" to set up your API key, or export ") + cyan(f"{provider.upper()}_API_KEY") + dark_gray("."))
        else:
            spin.stop(green("  [OK]") + gray(f"  Ready ({mode.upper()} mode)"))
    except Exception as exc:
        spin.stop()
        print(red(f"  [ERR] Could not initialize session: {exc}"))
        print(gray("  → Use /connect to configure a provider or enter an API key."))
        session = None

    turns = 0

    def _rebuild_session() -> Any:
        sp = Spinner("Connecting")
        sp.start()
        try:
            s = session_factory(provider=provider, model=model, mode=mode, workspace_root=workspace, cfg=cfg)
            sp.stop()
            return s
        except Exception as exc:
            sp.stop()
            print(red(f"  [ERR] {exc}"))
            return None

    def _do_connect() -> None:
        nonlocal provider, model, session
        new_p, new_m, new_cfg = run_connect(cfg, provider, model)
        cfg.update(new_cfg)
        save_cfg_fn(cfg)
        provider = new_p
        model = new_m
        session = _rebuild_session()

    def _switch_mode(new_mode: str) -> None:
        nonlocal mode
        m_raw = new_mode.lower().strip()
        if m_raw in ("code", "talk", "ml", "bot", "fix", "review"):
            mode = m_raw
        else:
            mode = "talk" if mode == "code" else "code"
        cfg.setdefault("agent", {})["mode"] = mode
        save_cfg_fn(cfg)
        if session:
            session.set_mode(mode)
        _tags = {
            "code": green("[CODE] Mode"),
            "talk": purple("[TALK] Mode"),
            "ml": blue("[ML] Mode"),
            "bot": cyan("[BOT] Mode"),
            "fix": yellow("[FIX] Mode"),
            "review": magenta("[REVIEW] Mode"),
        }
        tag = _tags.get(mode, green(f"[{mode.upper()}] Mode"))
        print("  " + green("[OK]") + f"  Switched to {tag}")

    def _send(text: str) -> Optional[str]:
        nonlocal turns
        spin_label = "Coding" if mode == "code" else ("Researching" if mode == "ml" else "Thinking")
        spin2 = Spinner(spin_label)
        spin2.start()
        try:
            if hasattr(session, "send_with_hooks"):
                def _on_tool(name: str, args: Dict[str, Any]):
                    spin2.stop()
                    print_tool_start(name, args)
                    spin2.start()

                def _on_tool_done(name: str, result: str, args: Optional[Dict[str, Any]] = None):
                    spin2.stop()
                    print_tool_finish(name, result, args)
                    spin2.start()

                reply = session.send_with_hooks(text, on_tool=_on_tool, on_tool_done=_on_tool_done)
            else:
                reply = session.send(text)
            spin2.stop()
            turns += 1
            return reply
        except KeyboardInterrupt:
            spin2.stop()
            print(yellow("\n  [!]  Interrupted"))
            return None
        except Exception as exc:
            spin2.stop()
            err_msg = str(exc).strip()
            friendly = getattr(exc, "friendly_message", None)
            if callable(friendly):
                try:
                    err_msg = friendly()
                except Exception:
                    pass

            p_label = provider.capitalize()
            hint = f"• Type /connect to configure or test your API key\n• Or export {provider.upper()}_API_KEY=... in your shell"
            _render_error_card(f"{p_label} Error", err_msg, hint=hint)

            lower_err = str(exc).lower()
            if any(k in lower_err for k in ("unauthorized", "401", "rejected", "api key", "no api key", "forbidden", "403")):
                if not task:
                    try:
                        sys.stdout.write("  " + bold(cyan("Would you like to configure your API key now? [y/N]: ")))
                        sys.stdout.flush()
                        ans = input().strip().lower()
                        if ans in ("y", "yes"):
                            _do_connect()
                    except (EOFError, KeyboardInterrupt):
                        print()
            return None

    # ── One-shot mode ───────────────────────────────────────────────────────
    if task:
        if session is None:
            print(red("  [ERR]  No active session. Cannot run task."))
            return
        reply = _send(task)
        if reply:
            print_reply(reply)
        _save_readline_history()
        return

    # ── Interactive REPL ────────────────────────────────────────────────────
    while True:
        try:
            prompt_str = render_prompt_line(workspace, provider, model, mode)
            sys.stdout.write(prompt_str)
            sys.stdout.flush()
            raw = input()
        except (EOFError, KeyboardInterrupt):
            print("\n  " + dark_gray("Exiting pytekt agent. Bye!"))
            _save_readline_history()
            break

        line = raw.strip()
        if not line:
            continue

        # ── Slash Commands ──────────────────────────────────────────────────
        if line.startswith("/"):
            parts = line.split(None, 1)
            cmd = parts[0].lower()
            rest = parts[1] if len(parts) > 1 else ""

            if cmd == "/mode":
                if rest.lower() in ("code", "talk", "ml", "bot", "fix", "review"):
                    _switch_mode(rest.lower())
                else:
                    _switch_mode("talk" if mode == "code" else "code")

            elif cmd == "/code":
                _switch_mode("code")

            elif cmd == "/talk":
                _switch_mode("talk")

            elif cmd == "/ml":
                _switch_mode("ml")

            elif cmd == "/bot":
                _switch_mode("bot")

            elif cmd == "/undo":
                if session and hasattr(session, "undo_last"):
                    res = session.undo_last()
                    print("  " + green("[OK]") + gray(f"  {res}"))
                else:
                    print(gray("  Nothing to undo."))

            elif cmd == "/fix":
                if session is None:
                    print(red("  [ERR]  No active session."))
                    continue
                try:
                    from .healer import run_self_healing_loop
                    print()
                    print("  " + bold(white("[FIX]  Self-Healing Test & Debugger")))
                    print("  " + dark_gray("Running pytest diagnostics in workspace..."))
                    def _on_iter(curr, total, msg):
                        print(f"  {cyan(f'[{curr}/{total}]')} {gray(msg)}")
                    ok, summary = run_self_healing_loop(session, workspace, on_iteration=_on_iter)
                    if ok:
                        print("  " + green("[OK]") + f"  {summary}")
                    else:
                        print("  " + red("[ERR]") + f"  {summary}")
                    print()
                except Exception as exc:
                    _render_error_card("Fix Error", str(exc), hint="• Ensure pytest is installed in your active environment")

            elif cmd == "/review":
                try:
                    from .review import audit_git_diff
                    print()
                    print("  " + bold(white("[REVIEW]  Git Diff & Code Review Audit")))
                    audit = audit_git_diff(workspace)
                    if "error" in audit:
                        print(red(f"  [ERR]  {audit['error']}"))
                    else:
                        print(f"  {gray('Stat:')}\n{audit['stat']}")
                        if audit["findings"]:
                            print("\n  " + yellow(bold("Findings detected:")))
                            for f in audit["findings"]:
                                color_fn = red if f.get("severity") == "high" else yellow
                                print(f"    {color_fn('•')} {f['description']}")
                        else:
                            print("\n  " + green("[OK] Clean!") + gray(" No leaked secrets or debug statements detected."))
                    print()
                except Exception as exc:
                    _render_error_card("Review Error", str(exc))

            elif cmd == "/connect":
                _do_connect()

            elif cmd == "/model":
                if rest:
                    model = rest.strip()
                    cfg.setdefault("agent", {})["model"] = model
                    save_cfg_fn(cfg)
                    session = _rebuild_session()
                    if session:
                        print("  " + green("[OK]") + gray(f"  Model set to: {model}"))
                else:
                    info = PROVIDERS.get(provider, {})
                    existing_key = (cfg.get("keys") or {}).get(f"{provider}_api_key", "") or os.environ.get(info.get("env_key") or "", "")
                    new_model = _pick_model(provider, info, existing_key)
                    model = new_model
                    cfg.setdefault("agent", {})["model"] = model
                    save_cfg_fn(cfg)
                    session = _rebuild_session()
                    if session:
                        print("  " + green("[OK]") + gray(f"  Switched to: {model}"))

            elif cmd == "/diff":
                run_diff_command(workspace)

            elif cmd == "/status":
                print_status(provider, model, mode, workspace, turns, cfg)

            elif cmd == "/reset":
                if session:
                    session.reset()
                print("  " + green("[OK]") + gray("  Conversation history reset."))
                turns = 0

            elif cmd == "/clear":
                os.system("clear" if os.name != "nt" else "cls")
                print_banner(version, provider, model, mode, workspace)

            elif cmd in ("/help", "/h", "/?"):
                print(HELP_SCREEN)

            elif cmd in ("/quit", "/exit", "/q"):
                print("\n  " + dark_gray("Exiting pytekt agent. Bye!"))
                _save_readline_history()
                break

            else:
                print("  " + yellow("[!]") + gray(f"  Unknown command '{cmd}'. Type /help for command list."))

            continue

        # ── Regular Task Prompt ─────────────────────────────────────────────
        if session is None:
            print(red("  [ERR]  No active session. Run /connect to select a provider."))
            continue

        reply = _send(line)
        if reply:
            print_reply(reply)


# ---------------------------------------------------------------------------
# First Run Setup Wizard
# ---------------------------------------------------------------------------

def run_setup_wizard(cfg: Dict[str, Any]) -> Dict[str, Any]:
    print()
    print("  " + bold(white("Welcome to PyTekt Agent")))
    print("  " + _hr())
    print("  " + gray("Let's configure your AI model provider to get started.\n"
                      "  You can change this anytime with ") + cyan("/connect") + gray(".\n"))
    
    current_p = cfg.get("agent", {}).get("provider", "anthropic")
    current_m = cfg.get("agent", {}).get("model", "")
    new_p, new_m, new_cfg = run_connect(cfg, current_p, current_m)
    return new_cfg


