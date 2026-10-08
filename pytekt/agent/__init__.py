"""
PyTekt Agent — autonomous terminal coding assistant.

Entry point: ``pytekt agent``

Exposes:
    AgentSession   — the main REPL / one-shot session class
    run_agent_cli  — ``pytekt agent`` CLI handler (called from cli.py)
"""

from .core import AgentSession, run_agent_cli
from .undo import undo_manager, UndoManager
from .connect import test_provider_connection, save_provider_connection, run_connect_interactive
from .healer import run_self_healing_loop
from .ml_tools import profile_dataset, fit_baseline_classifier
from .bot_tools import scaffold_bot_project, test_bot_in_memory
from .review import audit_git_diff

__all__ = [
    "AgentSession",
    "run_agent_cli",
    "undo_manager",
    "UndoManager",
    "test_provider_connection",
    "save_provider_connection",
    "run_connect_interactive",
    "run_self_healing_loop",
    "profile_dataset",
    "fit_baseline_classifier",
    "scaffold_bot_project",
    "test_bot_in_memory",
    "audit_git_diff",
]
