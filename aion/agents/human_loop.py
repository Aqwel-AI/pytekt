"""Human approval checkpoints for sensitive operations."""

from __future__ import annotations

from typing import Callable, Optional


ApprovalFn = Callable[[str], bool]


def require_approval(prompt: str, approval_fn: Optional[ApprovalFn] = None) -> bool:
    """Check whether a sensitive action has human approval."""
    if approval_fn is None:
        return False
    return bool(approval_fn(prompt))
