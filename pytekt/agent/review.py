"""
Code Review & Git Diff Audit Tools for PyTekt Agent.
Inspects uncommitted changes, scans for leaked credentials, and drafts commit messages.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
"""

from __future__ import annotations

import re
import subprocess
from typing import Any, Dict, List


_SECRET_PATTERNS = [
    (re.compile(r"(?:api[_-]?key|apikey|secret|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]", re.IGNORECASE), "High: Potential hardcoded API key/secret"),
    (re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----"), "Critical: Private encryption key exposed"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "Critical: OpenAI API key exposed"),
    (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "Critical: GitHub Personal Access Token exposed"),
]

_DEBUG_PATTERNS = [
    (re.compile(r"^\+\s*breakpoint\(\)", re.MULTILINE), "Warning: Leftover breakpoint() call"),
    (re.compile(r"^\+\s*debugger;", re.MULTILINE), "Warning: Leftover debugger statement"),
]


def audit_git_diff(workspace_root: str) -> Dict[str, Any]:
    """
    Audit git diff in workspace for leaked secrets, debug leftovers, and changed files.
    """
    try:
        stat_proc = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        diff_proc = subprocess.run(
            ["git", "diff"],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        untracked_proc = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception as e:
        return {"error": f"Failed to run git audit: {e}"}

    diff_text = diff_proc.stdout or ""
    untracked_files = [f for f in untracked_proc.stdout.splitlines() if f.strip()]
    
    findings: List[Dict[str, str]] = []

    # Check for secrets
    for pattern, desc in _SECRET_PATTERNS:
        matches = pattern.findall(diff_text)
        if matches:
            findings.append({"type": "security", "severity": "high", "description": desc, "count": str(len(matches))})

    # Check for debug statements
    for pattern, desc in _DEBUG_PATTERNS:
        matches = pattern.findall(diff_text)
        if matches:
            findings.append({"type": "code_smell", "severity": "medium", "description": desc, "count": str(len(matches))})

    return {
        "stat": stat_proc.stdout.strip() or "No uncommitted modifications",
        "diff_length": len(diff_text),
        "untracked_files": untracked_files,
        "findings": findings,
        "is_clean": len(findings) == 0,
    }
