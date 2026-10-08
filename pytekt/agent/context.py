"""
Smart Context Resolver for PyTekt Agent.
Expands @file, @git, @diff, and @tests in user prompts before passing to the LLM.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
"""

from __future__ import annotations

import os
import re
import subprocess
from typing import List, Tuple


def expand_prompt_context(user_text: str, workspace_root: str) -> Tuple[str, List[str]]:
    """
    Search for @mentions in user_text and expand them with real workspace context.

    Supported mentions:
      - @path/to/file or @file.py: reads file and appends context block
      - @git: appends git status and branch info
      - @diff: appends current git diff
      - @tests: appends recent pytest output or runs pytest --collect-only
    """
    expanded_blocks: List[str] = []
    mentions_found: List[str] = []

    # 1. Check for @git
    if re.search(r"(?:^|\s)@git(?:\s|$)", user_text):
        mentions_found.append("@git")
        try:
            res = subprocess.run(
                ["git", "status", "--short"],
                cwd=workspace_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            expanded_blocks.append(f"### Git Status:\n```\n{res.stdout.strip() or 'Working tree clean'}\n```")
        except Exception as e:
            expanded_blocks.append(f"### Git Status:\nError: {e}")

    # 2. Check for @diff
    if re.search(r"(?:^|\s)@diff(?:\s|$)", user_text):
        mentions_found.append("@diff")
        try:
            res = subprocess.run(
                ["git", "diff", "--stat"],
                cwd=workspace_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            res_full = subprocess.run(
                ["git", "diff"],
                cwd=workspace_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            diff_text = res_full.stdout[:4000] if len(res_full.stdout) > 4000 else res_full.stdout
            expanded_blocks.append(f"### Git Diff:\n```diff\n{diff_text.strip() or 'No changes'}\n```")
        except Exception as e:
            expanded_blocks.append(f"### Git Diff:\nError: {e}")

    # 3. Check for @tests
    if re.search(r"(?:^|\s)@tests(?:\s|$)", user_text):
        mentions_found.append("@tests")
        try:
            res = subprocess.run(
                ["pytest", "-q", "--maxfail=3"],
                cwd=workspace_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = res.stdout or res.stderr
            truncated = output[-3000:] if len(output) > 3000 else output
            expanded_blocks.append(f"### Pytest Summary:\n```\n{truncated.strip()}\n```")
        except Exception as e:
            expanded_blocks.append(f"### Pytest Summary:\nError running pytest: {e}")

    # 4. Check for @filepath
    file_matches = re.findall(r"(?:^|\s)@([a-zA-Z0-9_\-\./\\]+\.[a-zA-Z0-9_]+)", user_text)
    for rel_path in file_matches:
        if rel_path in ("git", "diff", "tests"):
            continue
        full_path = os.path.join(workspace_root, rel_path)
        if os.path.isfile(full_path):
            mentions_found.append(f"@{rel_path}")
            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                # Limit size to prevent blowing context
                if len(content) > 8000:
                    content = content[:8000] + "\n... [truncated]"
                expanded_blocks.append(f"### Context: {rel_path}\n```\n{content}\n```")
            except Exception as e:
                expanded_blocks.append(f"### Context: {rel_path}\nError reading file: {e}")

    if not expanded_blocks:
        return user_text, []

    combined_text = user_text + "\n\n" + "\n\n".join(expanded_blocks)
    return combined_text, mentions_found
