"""
Self-Healing Debugger for PyTekt Agent.
Autonomously runs tests, captures traceback diagnostics, surgically repairs code,
and re-verifies until 100% test pass.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
"""

from __future__ import annotations

import re
import subprocess
from typing import Any, Callable, Dict, List, Optional, Tuple


def run_pytest_diagnostic(workspace_root: str, test_target: Optional[str] = None) -> Tuple[bool, str, List[Dict[str, str]]]:
    """
    Run pytest in workspace and parse any failure diagnostics.

    Returns:
      (passed: bool, raw_output: str, failures: List[Dict[str, str]])
    """
    cmd = ["pytest", "-v"]
    if test_target:
        cmd.append(test_target)

    try:
        proc = subprocess.run(
            cmd,
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = proc.stdout + ("\n" + proc.stderr if proc.stderr else "")
        passed = proc.returncode == 0
    except subprocess.TimeoutExpired:
        return False, "Pytest timed out after 120s", [{"test": "timeout", "file": "", "message": "Timeout"}]
    except Exception as e:
        return False, f"Failed to execute pytest: {e}", [{"test": "error", "file": "", "message": str(e)}]

    failures: List[Dict[str, str]] = []
    # Parse FAILURES section
    failure_blocks = re.findall(r"_{3,}\s*(.*?)\s*_{3,}(.*?)(?=(?:_{3,}|\Z))", output, re.DOTALL)
    for title, body in failure_blocks:
        file_match = re.search(r"(\S+\.py):(\d+):", body)
        file_path = file_match.group(1) if file_match else ""
        line_num = file_match.group(2) if file_match else ""
        failures.append({
            "test": title.strip(),
            "file": file_path,
            "line": line_num,
            "traceback": body.strip()[-1500:],  # keep concise
        })

    return passed, output, failures


def run_self_healing_loop(
    session: Any,
    workspace_root: str,
    test_target: Optional[str] = None,
    max_iterations: int = 3,
    on_iteration: Optional[Callable[[int, int, str], None]] = None,
) -> Tuple[bool, str]:
    """
    Execute autonomous test & repair loop.
    Repeats: run pytest -> diagnose failures -> agent repairs -> re-run.
    """
    for iteration in range(1, max_iterations + 1):
        if on_iteration:
            on_iteration(iteration, max_iterations, "Running pytest suite...")

        passed, raw_output, failures = run_pytest_diagnostic(workspace_root, test_target)
        if passed:
            return True, f"All tests passed on iteration {iteration}!"

        if not failures:
            # Error happened outside regular test failure (e.g. collection error or syntax error)
            error_prompt = (
                f"Pytest failed with error output:\n```\n{raw_output[-2000:]}\n```\n"
                "Please read the relevant files, identify the error, and fix it using edit_file."
            )
        else:
            first_fail = failures[0]
            error_prompt = (
                f"Test failure detected:\n"
                f"Test: {first_fail['test']}\n"
                f"Location: {first_fail['file']}:{first_fail['line']}\n"
                f"Traceback:\n```\n{first_fail['traceback']}\n```\n"
                f"Total failing tests: {len(failures)}.\n\n"
                "Please read the source and test files, identify the root cause, and apply a surgical fix with edit_file."
            )

        if on_iteration:
            on_iteration(iteration, max_iterations, f"Diagnosing & repairing {len(failures)} failure(s)...")

        # Let the agent diagnose and repair
        try:
            session.send(error_prompt)
        except Exception as exc:
            return False, f"Agent encountered error during repair: {exc}"

    # Final verification run
    passed, final_out, final_fails = run_pytest_diagnostic(workspace_root, test_target)
    if passed:
        return True, f"All tests successfully repaired and passing after {max_iterations} iterations!"
    return False, f"Could not fully resolve all failures after {max_iterations} iterations ({len(final_fails)} still failing)."
