"""
PyTekt Agent — core session and CLI entrypoint.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Callable, Dict, List, Optional

from ..providers.factory import create_provider, supported_providers
from ..providers.keys import resolve_api_key
from ..tools.code_agent import (
    edit_file,
    glob_search,
    grep_search,
    list_files,
    read_file,
    run_command,
    write_file,
)
from ..tools.registry import ToolRegistry
from ..tools.schemas import function_tool
from ..tools.workspace import Workspace
from .prompt import CODE_PROMPT, TALK_PROMPT, SYSTEM_PROMPT

# ---------------------------------------------------------------------------
# Tool schema definitions (OpenAI function-calling format)
# ---------------------------------------------------------------------------

_TOOLS: List[Dict[str, Any]] = [
    function_tool(
        "read_file",
        "Read a file from the workspace with line numbers. Use offset/limit for large files.",
        properties={
            "path": {"type": "string", "description": "File path relative to workspace root"},
            "offset": {"type": "integer", "description": "1-based start line (default 1)"},
            "limit":  {"type": "integer", "description": "Max lines to return (default 500)"},
        },
        required=["path"],
    ),
    function_tool(
        "write_file",
        "Create or overwrite a file with the given content. Use only for new files or full rewrites.",
        properties={
            "path":    {"type": "string", "description": "File path relative to workspace root"},
            "content": {"type": "string", "description": "Full file content"},
        },
        required=["path", "content"],
    ),
    function_tool(
        "edit_file",
        (
            "Replace an exact string in a file once. old_string must match verbatim "
            "(including whitespace). Prefer this over write_file for targeted edits."
        ),
        properties={
            "path":       {"type": "string", "description": "File path relative to workspace root"},
            "old_string": {"type": "string", "description": "Exact text to replace (must be unique in the file)"},
            "new_string": {"type": "string", "description": "Replacement text"},
        },
        required=["path", "old_string", "new_string"],
    ),
    function_tool(
        "list_files",
        "List files and directories under a path. Set recursive=true for deep listings.",
        properties={
            "path":      {"type": "string",  "description": "Directory path (default '.')"},
            "recursive": {"type": "boolean", "description": "Walk subdirectories (default false)"},
        },
    ),
    function_tool(
        "search_files",
        "Search file contents with a regex. Returns file:line:match lines.",
        properties={
            "pattern":      {"type": "string", "description": "Python regex pattern"},
            "path":         {"type": "string", "description": "Root directory or file to search (default '.')"},
            "glob_pattern": {"type": "string", "description": "Limit to files matching this glob (e.g. '*.py')"},
        },
        required=["pattern"],
    ),
    function_tool(
        "glob_search",
        "Find files matching a glob pattern relative to the workspace root (e.g. '**/*.py').",
        properties={
            "pattern": {"type": "string", "description": "Glob pattern"},
        },
        required=["pattern"],
    ),
    function_tool(
        "run_command",
        (
            "Execute a shell command in the workspace directory. "
            "Never use for destructive operations (rm -rf, force-push, etc.) "
            "without the user's explicit confirmation."
        ),
        properties={
            "command": {"type": "string", "description": "Shell command to run"},
            "timeout": {"type": "integer", "description": "Timeout in seconds (max 120, default 60)"},
        },
        required=["command"],
    ),
]

_ML_TOOLS: List[Dict[str, Any]] = [
    function_tool(
        "profile_dataset",
        "Inspect a tabular dataset (CSV) for dimensions, columns, null percentages, and statistics.",
        properties={
            "filepath": {"type": "string", "description": "Path to CSV dataset"},
        },
        required=["filepath"],
    ),
    function_tool(
        "fit_baseline_classifier",
        "Train a baseline classifier (gaussian_nb, logistic_regression, decision_tree) using PyTekt Core ML and evaluate metrics.",
        properties={
            "filepath": {"type": "string", "description": "Path to CSV dataset"},
            "target_column": {"type": "string", "description": "Target class column name"},
            "model_type": {"type": "string", "description": "Model type: gaussian_nb, logistic_regression, decision_tree"},
        },
        required=["filepath", "target_column"],
    ),
]

_BOT_TOOLS: List[Dict[str, Any]] = [
    function_tool(
        "scaffold_bot_project",
        "Scaffold a complete Telegram, Discord, or Slack bot project structure using PyTekt Bots.",
        properties={
            "name": {"type": "string", "description": "Project/bot name"},
            "platform": {"type": "string", "description": "Platform: telegram, discord, or slack"},
            "output_dir": {"type": "string", "description": "Directory to generate project in (default workspace)"},
        },
        required=["name", "platform"],
    ),
    function_tool(
        "test_bot_in_memory",
        "Load and verify a bot module in-memory using BotTestClient without requiring network or bot tokens.",
        properties={
            "handler_file": {"type": "string", "description": "Path to bot handler script"},
        },
        required=["handler_file"],
    ),
]

_REVIEW_TOOLS: List[Dict[str, Any]] = [
    function_tool(
        "audit_git_diff",
        "Audit uncommitted changes in git workspace for hardcoded secrets, syntax bugs, and changed files.",
        properties={},
    ),
]

# ---------------------------------------------------------------------------
# AgentSession
# ---------------------------------------------------------------------------

class AgentSession:
    """
    Multi-turn agentic REPL backed by a chat provider + workspace-sandboxed tools.
    Supports distinct operational modes:
      - 'code': Autonomous senior coding agent (Cursor-style file editing & execution).
      - 'talk': Conversational technical thought partner (explain, discuss, architecture).
      - 'ml': Autonomous data science and ML research partner.
      - 'bot': Autonomous bot architect and generator.
      - 'fix': Self-healing test runner and debugger.
      - 'review': Code reviewer and git diff auditor.
    """

    def __init__(
        self,
        workspace_root: Optional[str] = None,
        provider_name: str = "openai",
        model: str = "gpt-4o-mini",
        mode: str = "code",
        api_key: Optional[str] = None,
        max_rounds: int = 16,
        trusted: bool = True,
        cfg: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.workspace = Workspace(workspace_root or os.getcwd())
        self.max_rounds = max_rounds
        self.trusted = trusted
        self.provider_name = provider_name
        self.model_name = model
        self.mode = mode.lower() if mode else "code"

        # Build provider kwargs
        key = api_key or resolve_api_key(provider_name, cfg)
        provider_kwargs: Dict[str, Any] = {"model": model}
        if key:
            provider_kwargs["api_key"] = key

        # Provider-specific extra kwargs from config
        agent_cfg = (cfg or {}).get("agent", {})
        if provider_name == "ollama":
            ollama_host = agent_cfg.get("ollama_host", "http://localhost:11434")
            provider_kwargs["base_url"] = ollama_host.rstrip("/") + "/v1"
            if "api_key" not in provider_kwargs:
                provider_kwargs["api_key"] = "ollama"
        elif provider_name in ("openai_compatible", "compatible"):
            base_url = agent_cfg.get("custom_base_url", "http://localhost:1234/v1")
            provider_kwargs["base_url"] = base_url

        try:
            self.provider = create_provider(provider_name, **provider_kwargs)
        except Exception:
            # Fall back if key not yet provided so session can be initialized or mocked
            try:
                provider_kwargs["api_key"] = "mock_key"
                self.provider = create_provider(provider_name, **provider_kwargs)
            except Exception:
                self.provider = None
        
        system_content = self._get_prompt_for_mode()
        self.messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_content}
        ]

        # Wire tools
        ws = self.workspace
        self.registry = ToolRegistry()
        self.registry.register("read_file",   lambda **kw: read_file(ws, **kw),   required_arg_keys=["path"])
        self.registry.register("write_file",  lambda **kw: write_file(ws, **kw),  required_arg_keys=["path", "content"])
        self.registry.register("edit_file",   lambda **kw: edit_file(ws, **kw),   required_arg_keys=["path", "old_string", "new_string"])
        self.registry.register("list_files",  lambda **kw: list_files(ws, **kw))
        self.registry.register("search_files",lambda **kw: grep_search(ws, **kw), required_arg_keys=["pattern"])
        self.registry.register("glob_search", lambda **kw: glob_search(ws, **kw), required_arg_keys=["pattern"])

        # Specialized tools
        try:
            from .ml_tools import profile_dataset, fit_baseline_classifier
            self.registry.register("profile_dataset", lambda **kw: profile_dataset(ws.resolve(kw["filepath"])), required_arg_keys=["filepath"])
            self.registry.register("fit_baseline_classifier", lambda **kw: fit_baseline_classifier(ws.resolve(kw["filepath"]), kw["target_column"], kw.get("model_type", "gaussian_nb")), required_arg_keys=["filepath", "target_column"])
        except Exception:
            pass

        try:
            from .bot_tools import scaffold_bot_project, test_bot_in_memory
            self.registry.register("scaffold_bot_project", lambda **kw: scaffold_bot_project(kw["name"], kw.get("platform", "telegram"), str(ws.root)), required_arg_keys=["name"])
            self.registry.register("test_bot_in_memory", lambda **kw: test_bot_in_memory(str(ws.resolve(kw["handler_file"]))), required_arg_keys=["handler_file"])
        except Exception:
            pass

        try:
            from .review import audit_git_diff
            self.registry.register("audit_git_diff", lambda **kw: audit_git_diff(str(ws.root)))
        except Exception:
            pass

        if trusted:
            self.registry.register("run_command", lambda **kw: run_command(ws, **kw), required_arg_keys=["command"])
        else:
            self.registry.register(
                "run_command",
                lambda **kw: json.dumps({"error": "run_command is disabled (untrusted mode)"}),
            )

    def _get_prompt_for_mode(self) -> str:
        from .prompt import CODE_PROMPT, TALK_PROMPT, ML_PROMPT, BOT_PROMPT, FIX_PROMPT, REVIEW_PROMPT
        m = self.mode.lower().strip()
        if m in ("ml", "research"):
            return ML_PROMPT
        elif m in ("bot", "bots"):
            return BOT_PROMPT
        elif m in ("fix", "heal", "debug"):
            return FIX_PROMPT
        elif m in ("review", "audit"):
            return REVIEW_PROMPT
        elif m == "talk":
            return TALK_PROMPT
        return CODE_PROMPT

    def _get_tools_for_mode(self) -> Optional[List[Dict[str, Any]]]:
        if self.mode == "talk":
            return None
        tools = list(_TOOLS)
        if self.mode in ("ml", "research"):
            tools.extend(_ML_TOOLS)
        elif self.mode in ("bot", "bots"):
            tools.extend(_BOT_TOOLS)
        elif self.mode in ("review", "audit"):
            tools.extend(_REVIEW_TOOLS)
        return tools

    def set_mode(self, mode: str) -> None:
        """Switch between agent modes ('code', 'talk', 'ml', 'bot', 'fix', 'review')."""
        self.mode = mode.lower().strip()
        prompt = self._get_prompt_for_mode()
        if self.messages and self.messages[0].get("role") == "system":
            self.messages[0]["content"] = prompt
        else:
            self.messages.insert(0, {"role": "system", "content": prompt})

    def undo_last(self) -> str:
        """Undo last file modification."""
        from .undo import undo_manager
        return undo_manager.undo_last()

    def send(self, user_text: str) -> str:
        """
        Add a user message, run the tool loop, and return the assistant reply.
        """
        from ..tools.loop import run_tool_loop
        from .context import expand_prompt_context

        # Expand smart context mentions (@file, @git, @diff, @tests)
        expanded_text, _ = expand_prompt_context(user_text, str(self.workspace.root))
        self.messages.append({"role": "user", "content": expanded_text})
        
        tools = self._get_tools_for_mode()
        
        final_text, self.messages = run_tool_loop(
            self.provider,
            self.messages,
            tools,
            self.registry if tools else None,
            max_rounds=self.max_rounds if tools else 1,
            temperature=0.2 if self.mode != "talk" else 0.7,
            max_tokens=4096,
        )
        return final_text or ""

    def send_with_hooks(
        self,
        user_text: str,
        on_tool: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_tool_done: Optional[Callable[[str, str], None]] = None,
    ) -> str:
        """
        Like ``send`` but fires callbacks before/after each tool call so the TUI
        can display live tool progress.
        """
        from ..tools.loop import run_tool_loop
        from .context import expand_prompt_context

        expanded_text, _ = expand_prompt_context(user_text, str(self.workspace.root))
        self.messages.append({"role": "user", "content": expanded_text})
        
        tools = self._get_tools_for_mode()

        # Try hook-aware loop first
        try:
            final_text, self.messages = run_tool_loop(
                self.provider,
                self.messages,
                tools,
                self.registry if tools else None,
                max_rounds=self.max_rounds if tools else 1,
                temperature=0.2 if self.mode != "talk" else 0.7,
                max_tokens=4096,
                on_tool_call=on_tool if tools else None,
                on_tool_result=on_tool_done if tools else None,
            )
        except TypeError:
            # run_tool_loop doesn't accept hook kwargs — fall back
            final_text, self.messages = run_tool_loop(
                self.provider,
                self.messages,
                tools,
                self.registry if tools else None,
                max_rounds=self.max_rounds if tools else 1,
                temperature=0.2 if self.mode != "talk" else 0.7,
                max_tokens=4096,
            )

        return final_text or ""

    def reset(self) -> None:
        """Clear conversation history (keep system prompt)."""
        self.messages = [self.messages[0]]


# ---------------------------------------------------------------------------
# Session factory (used by TUI)
# ---------------------------------------------------------------------------

def _make_session(
    provider: str,
    model: str,
    mode: str = "code",
    workspace_root: Optional[str] = None,
    api_key: Optional[str] = None,
    max_rounds: int = 16,
    trusted: bool = True,
    cfg: Optional[Dict[str, Any]] = None,
) -> AgentSession:
    return AgentSession(
        workspace_root=workspace_root,
        provider_name=provider,
        model=model,
        mode=mode,
        api_key=api_key,
        max_rounds=max_rounds,
        trusted=trusted,
        cfg=cfg,
    )


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def run_agent_cli(
    task: Optional[str] = None,
    workspace: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    mode: Optional[str] = None,
    api_key: Optional[str] = None,
    max_rounds: int = 16,
    no_shell: bool = False,
) -> None:
    """
    Run the agent with the full TUI.

    - Reads ~/.pytekt.yaml for saved provider/model/mode config.
    - On first run (or if no provider configured), launches the setup wizard.
    - If *task* is given (``pytekt agent "fix the bug"``): one-shot mode.
    - Otherwise: interactive TUI REPL with CODE and TALK modes.
    """
    from ..user_config import get_config, save_config
    from . import tui

    cfg = get_config()
    agent_cfg = cfg.get("agent", {})

    # Resolve provider / model / mode (CLI flag > config > defaults)
    resolved_provider = provider or agent_cfg.get("provider") or None
    resolved_model = model or agent_cfg.get("model") or None
    resolved_mode = mode or agent_cfg.get("mode") or "code"

    # Run setup wizard if no provider configured and not in one-shot with explicit flags
    if resolved_provider is None:
        cfg = tui.run_setup_wizard(cfg)
        save_config(cfg)
        agent_cfg = cfg.get("agent", {})
        resolved_provider = agent_cfg.get("provider", "openai")
        resolved_model = agent_cfg.get("model")
        resolved_mode = agent_cfg.get("mode", "code")

    # Apply provider-specific model defaults
    _default_models = {
        "openai":    "gpt-4o",
        "anthropic": "claude-3-5-sonnet-latest",
        "claude":    "claude-3-5-sonnet-latest",
        "gemini":    "gemini-2.0-flash",
        "google":    "gemini-2.0-flash",
        "ollama":    "llama3.2",
        "deepseek":  "deepseek-chat",
        "nvidia":    "meta/llama-3.1-70b-instruct",
        "nim":       "meta/llama-3.1-70b-instruct",
        "openai_compatible": "local-model",
    }
    if not resolved_model:
        resolved_model = _default_models.get(resolved_provider.lower(), "gpt-4o")

    workspace_root = workspace or os.getcwd()

    # Build session factory for TUI (captures api_key, max_rounds, no_shell)
    def session_factory(provider: str, model: str, mode: str = "code", workspace_root: str = "", cfg: Dict[str, Any] = None):
        return _make_session(
            provider=provider,
            model=model,
            mode=mode,
            workspace_root=workspace_root or workspace_root,
            api_key=api_key,
            max_rounds=max_rounds,
            trusted=not no_shell,
            cfg=cfg,
        )

    # Get version
    try:
        from .. import __version__
        version = str(__version__)
    except Exception:
        version = "0.2.1"

    # Launch TUI
    tui.run_tui(
        session_factory=session_factory,
        workspace=workspace_root,
        provider=resolved_provider,
        model=resolved_model,
        mode=resolved_mode,
        cfg=cfg,
        save_cfg_fn=save_config,
        version=version,
        task=task,
    )
