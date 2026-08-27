#!/usr/bin/env python3
"""
PyTekt Secrets Scanner Script.

Scans the repository for accidentally hardcoded production API tokens, private keys,
and high-entropy credentials. Used in CI and pre-commit hooks.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Patterns identifying real production credentials
SECRET_PATTERNS = [
    (re.compile(r"\b[0-9]{9,10}:[a-zA-Z0-9_-]{35}\b"), "Telegram Bot Token (Production format)"),
    (re.compile(r"sk-[a-zA-Z0-9]{32,}"), "OpenAI Legacy API Key"),
    (re.compile(r"sk-proj-[a-zA-Z0-9_\-]{40,}"), "OpenAI Project API Key"),
    (re.compile(r"sk-ant-[a-zA-Z0-9_\-]{40,}"), "Anthropic API Key"),
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "Google Gemini API Key"),
    (re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH|PRIVATE) KEY-----"), "Private Key Header"),
    (re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}"), "GitHub Personal Access Token"),
]

# Patterns explicitly allowed as mock test tokens and documentation placeholders
ALLOWLIST_PATTERNS = [
    re.compile(r"123456:(?:TEST_TOKEN|MOCK|MOCK_TOKEN|ABCDEF)"),
    re.compile(r"YOUR_[A-Z0-9_]+_TOKEN"),
    re.compile(r"YOUR_[A-Z0-9_]+_KEY"),
    re.compile(r"MOCK_DISCORD"),
    re.compile(r"<REDACTED>"),
]

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "build",
    "dist",
    ".mypy_cache",
    ".eggs",
}

EXCLUDED_EXTENSIONS = {
    ".so",
    ".dylib",
    ".dll",
    ".pyc",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".bin",
    ".dat",
}


def scan_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Scan a single file for secret patterns. Returns list of (line_no, rule_name, snippet)."""
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    for line_idx, line in enumerate(content.splitlines(), start=1):
        # Skip comment headers or allowlisted dummy tokens
        if any(allowed.search(line) for allowed in ALLOWLIST_PATTERNS):
            continue

        for pattern, rule_name in SECRET_PATTERNS:
            match = pattern.search(line)
            if match:
                matched_text = match.group(0)
                # Check if matched text matches allowlist
                if any(allowed.search(matched_text) for allowed in ALLOWLIST_PATTERNS):
                    continue
                snippet = line.strip()[:100]
                findings.append((line_idx, rule_name, snippet))

    return findings


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    total_files = 0
    total_findings = 0

    print(f"🔒 Scanning repository for hardcoded secrets: {root_dir}")

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in files:
            p = Path(root) / f
            if p.suffix in EXCLUDED_EXTENSIONS:
                continue
            if p.name in ("scan_secrets.py", "code.py"):
                continue

            total_files += 1
            findings = scan_file(p)
            if findings:
                rel_path = p.relative_to(root_dir)
                for line_no, rule, snippet in findings:
                    print(f"  ❌ [FAIL] {rel_path}:{line_no} — {rule}")
                    print(f"     Snippet: {snippet}")
                    total_findings += 1

    if total_findings == 0:
        print(f"\n✅ Clean! Scanned {total_files} files with 0 secret leaks detected.")
        return 0
    else:
        print(f"\n⚠️ FAILED: Found {total_findings} potential secret leak(s) across {total_files} files.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
