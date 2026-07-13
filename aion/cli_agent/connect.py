"""Connect the ReAct agent to Ollama or cloud API providers."""

from __future__ import annotations

import os
import uuid
from typing import Any, Callable, Dict, List, Optional

from ..agents.memory import SlidingWindowMemory
from ..agents.react import ReActAgent
from ..providers.adapter import ProviderAdapter, cached_model_metadata
from ..providers.errors import ProviderError
from ..providers.factory import create_provider
from ..providers.keys import resolve_api_key
from ..providers.nvidia_provider import NvidiaProvider
from ..providers.ollama import OllamaProvider
from ..tools.registry import ToolRegistry
from . import ui
from .connect_args import looks_like_model_name, normalize_company
from .constants import (
    AGENT_PROVIDER,
    CODING_AGENT_PROMPT,
    COMING_SOON_PROVIDERS,
    CONNECTABLE_PROVIDERS,
    provider_display_name,
)
from .edit_history import EditHistory
from .linter_hook import run_lint_on_file
from .mcp import register_mcp_tools
from .physics_tools import physics_system_hint
from .project import discover_project
from .session_prefs import (
    approval_gate_enabled,
    clear_connection,
    clear_provider_keys,
    saved_safety_mode,
    saved_specialist_mode,
    force_tools_enabled,
    save_connection,
    save_interaction_mode,
    save_provider_key,
    saved_allowed_commands,
    saved_interaction_mode,
    saved_mcp_servers,
    saved_model,
    saved_pinned_paths,
    saved_provider,
    saved_workspace_roots,
)
from .tool_middleware import ToolMiddleware


def _probe_ollama_tools(provider: Any, tools_schema: List[Dict[str, Any]]) -> bool:
    """Return True if this Ollama model accepts OpenAI-style tools."""
    if not tools_schema:
        return False
    try:
        provider.complete_turn(
            [{"role": "user", "content": "Say hi in one word."}],
            tools=tools_schema[:1],
            max_tokens=32,
            temperature=0,
        )
        return True
    except Exception:
        return False


def _resolve_connect_target(
    prov: Optional[str],
    mod: Optional[str],
) -> tuple[str, Optional[str], bool]:
    """
    Normalize connect args to a provider id.

    Returns (provider, model, rejected) where rejected means an unsupported provider.
    """
    p_name = (prov or "").lower().strip()
    if not p_name:
        return AGENT_PROVIDER, mod, False
    mapped = normalize_company(p_name) or p_name
    if mapped in CONNECTABLE_PROVIDERS:
        return mapped, mod, False
    if looks_like_model_name(p_name):
        from .connect_args import infer_provider_from_model

        inferred = infer_provider_from_model(p_name) or AGENT_PROVIDER
        return inferred, mod or p_name, False
    if mapped in COMING_SOON_PROVIDERS or mapped not in CONNECTABLE_PROVIDERS:
        return mapped, mod, True
    return mapped, mod, True


class AgentConnector:
    """Create and hold a connected :class:`ReActAgent`."""

    def __init__(
        self,
        *,
        cfg: Dict[str, Any],
        registry: ToolRegistry,
        tools_schema: List[Dict[str, Any]],
        session: ui.AgentSession,
        is_trusted: bool,
        system_prompt: Optional[str] = None,
        workspace_root: Optional[str] = None,
    ) -> None:
        self.cfg = cfg
        self.registry = registry
        self.tools_schema = tools_schema
        self.session = session
        self.is_trusted = is_trusted
        self.system_prompt = system_prompt
        self.workspace_root = workspace_root or os.getcwd()
        self.agent: Optional[ReActAgent] = None
        self.trust_confirmed = False
        self._raw_provider: Any = None
        self._provider_adapter: Optional[ProviderAdapter] = None
        self._planning_agent: Any = None
        self._pending_task: Optional[str] = None
        self._pending_plan_steps: Any = None
        self._event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
        self.session.session_id = uuid.uuid4().hex[:10]
        self.session.pinned_paths = saved_pinned_paths(cfg)
        self.session.project_info = discover_project(self.workspace_root)
        self.session.force_tools = force_tools_enabled(cfg)
        self.session.safety_mode = saved_safety_mode(cfg)
        self.session.specialist_mode = saved_specialist_mode(cfg)
        self.edit_history = EditHistory(self.session.session_id)
        self.tool_middleware = ToolMiddleware(
            workspace_root=self.workspace_root,
            session_id=self.session.session_id,
            approval_gate=approval_gate_enabled(cfg),
            allowed_commands=self._effective_allowed_commands(),
            edit_history=self.edit_history,
            project_info=self.session.project_info,
            safety_mode=saved_safety_mode(cfg),
        )
        self._rebuild_registry()

    def _effective_allowed_commands(self) -> List[str]:
        cmds = saved_allowed_commands(self.cfg)
        if cmds:
            return cmds
        info = self.session.project_info
        out: List[str] = []
        if info and info.test_command:
            out.append(info.test_command.split()[0])
        if info and info.lint_command:
            out.append(info.lint_command.split()[0])
        return out

    def _rebuild_registry(self) -> None:
        from .tools import build_tool_registry, tools_schema

        read_only = self.session.interaction_mode == "review"
        self.registry = build_tool_registry(
            workspace_root=self.workspace_root,
            is_trusted=self.is_trusted,
            middleware=self.tool_middleware,
            read_only=read_only,
            cfg=self.cfg,
        )
        register_mcp_tools(self.registry, saved_mcp_servers(self.cfg))
        self.tools_schema = tools_schema(is_trusted=self.is_trusted, read_only=read_only)

    def _tools_for_session(self) -> List[Dict[str, Any]]:
        if self.session.interaction_mode in ("plain", "review"):
            return []
        return self.tools_schema

    def set_force_tools(self, enabled: bool) -> None:
        self.session.force_tools = enabled
        self.cfg.setdefault("agent", {})["force_tools"] = bool(enabled)
        from .config import save_config

        save_config(self.cfg)
        if self.agent is not None:
            self.agent.force_tools = enabled  # type: ignore[attr-defined]

    def set_interaction_mode(self, mode: str) -> None:
        from .constants import normalize_interaction_mode

        normalized = normalize_interaction_mode(mode)
        if not normalized:
            raise ValueError(f"Unknown interaction mode: {mode!r}")
        self.session.interaction_mode = normalized
        save_interaction_mode(self.cfg, normalized)
        self._rebuild_registry()
        if self.session.connected and self.session.provider and self.session.model:
            prov = self.session.provider
            mod = self.session.model
            if self._raw_provider is not None:
                self.agent = self._build_agent(self._raw_provider, prov, mod)
                self._apply_session(prov, mod)

    def _load_aion_md(self) -> str:
        path = os.path.join(self.workspace_root, "AION.md")
        if not os.path.isfile(path):
            return ""
        try:
            text = open(path, encoding="utf-8").read().strip()
        except OSError:
            return ""
        if len(text) > 8000:
            return text[:8000] + "\n\n[... AION.md truncated ...]"
        return text

    def apply_trust(self, is_trusted: bool) -> None:
        """Rebuild tool registry after the user answers the trust prompt."""
        self.is_trusted = is_trusted
        self.session.is_trusted = is_trusted
        self._rebuild_registry()
        if self.agent is not None:
            self.agent.registry = self.registry
            self.agent.tools = self.tools_schema
            self.session.tools_enabled = bool(self.tools_schema)

    def connect(
        self,
        prov: Optional[str] = None,
        mod: Optional[str] = None,
        *,
        quiet: bool = False,
        new_key: bool = False,
    ) -> bool:
        raw = prov or self.session.provider or saved_provider(self.cfg)
        p_name, m_name, rejected = _resolve_connect_target(raw, mod)
        if rejected:
            if not quiet:
                label = provider_display_name(p_name)
                if p_name in COMING_SOON_PROVIDERS:
                    ui.info_print(
                        f"{ui.bold(label)} is coming soon — not available yet. "
                        f"Use {ui.cyan('/connect ollama')} or {ui.cyan('/connect nvidia')}."
                    )
                else:
                    ui.info_print(
                        f"Unknown provider {ui.bold(p_name)}. "
                        f"Try {ui.cyan('/connect')} to pick one."
                    )
            return False

        if p_name == "ollama":
            return self._connect_ollama(m_name, quiet=quiet, prov=prov, mod=mod)
        if p_name == "nvidia":
            return self._connect_nvidia(m_name, quiet=quiet, new_key=new_key)
        return False

    def set_event_callback(
        self, callback: Optional[Callable[[str, Dict[str, Any]], None]]
    ) -> None:
        self._event_callback = callback

    def _emit(self, event_type: str, **data: Any) -> None:
        if self._event_callback:
            try:
                self._event_callback(event_type, data)
            except Exception:
                pass

    def list_models_api(self, provider_id: str) -> Dict[str, Any]:
        """Return models for a provider without terminal UI."""
        provider_id = (provider_id or "").lower().strip()
        if provider_id not in CONNECTABLE_PROVIDERS:
            return {"ok": False, "error": f"Unknown provider: {provider_id}"}
        try:
            if provider_id == "ollama":
                models = OllamaProvider.list_models()
            elif provider_id == "nvidia":
                key = resolve_api_key("nvidia", self.cfg)
                if not key:
                    return {"ok": False, "error": "No API key for nvidia"}
                models = NvidiaProvider.list_models(api_key=key)
            else:
                models = []
            return {"ok": True, "models": models}
        except ProviderError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def connect_api(
        self,
        prov: Optional[str] = None,
        mod: Optional[str] = None,
        *,
        api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Headless connect for web API; returns {ok, error?, provider?, model?}."""
        if api_key and prov:
            save_provider_key(self.cfg, prov, api_key)
        ok = self.connect(prov=prov, mod=mod, quiet=True, new_key=bool(api_key))
        if ok:
            self._emit("session_updated")
            return {
                "ok": True,
                "provider": self.session.provider,
                "model": self.session.model,
            }
        return {"ok": False, "error": "Connect failed — check provider, model, and API key"}

    def session_dict(self) -> Dict[str, Any]:
        """JSON-serializable session snapshot."""
        info = self.session.project_info
        return {
            "connected": self.session.connected,
            "provider": self.session.provider,
            "model": self.session.model,
            "mode": self.session.interaction_mode,
            "trust": self.session.is_trusted,
            "tools_enabled": self.session.tools_enabled,
            "force_tools": self.session.force_tools,
            "pinned_paths": list(self.session.pinned_paths),
            "pending_plan": self.session.pending_plan,
            "workspace": self.workspace_root,
            "project": info.summary() if info else None,
            "plan_steps": (
                [s.description for s in self._pending_plan_steps]
                if self._pending_plan_steps
                else []
            ),
        }

    def _ensure_api_key(
        self,
        provider_id: str,
        *,
        new_key: bool = False,
        quiet: bool = False,
    ) -> Optional[str]:
        if not new_key:
            key = resolve_api_key(provider_id, self.cfg)
            if key:
                return key
        if quiet:
            return None
        label = provider_display_name(provider_id)
        ui.info_print(f"{label} requires an API key.")
        token = input(
            f"  {ui.ICON_AUTH} Enter API token for {ui.bold(label)} (Enter to cancel): "
        ).strip()
        if not token:
            return None
        save_provider_key(self.cfg, provider_id, token)
        ui.success_print(f"Saved API key for {ui.bold(label)}.")
        return token

    def _pick_model(
        self,
        models: List[str],
        *,
        m_name: Optional[str],
        mod: Optional[str],
        prov: Optional[str],
        saved_prov: Optional[str],
        saved_mod: Optional[str],
        quiet: bool,
        pick_model: bool,
        provider_label: str,
    ) -> Optional[str]:
        if m_name and m_name not in models:
            if mod or (prov and looks_like_model_name(prov)):
                ui.error_print(
                    f"Model {ui.bold(m_name)} not available on {provider_label}. "
                    f"Use {ui.cyan('/connect ' + provider_label.lower())} to pick one."
                )
                return None
            m_name = None

        if quiet:
            if m_name and m_name in models:
                return m_name
            if saved_prov and saved_mod and saved_mod in models:
                return saved_mod
            return models[0] if models else None

        if pick_model or not m_name:
            ui.print_menu(
                models,
                f"Select {provider_label} model ({len(models)} available)",
            )
            return models[ui.get_menu_choice(models) - 1]
        return m_name

    def _build_agent(self, provider: Any, provider_id: str, model: str) -> ReActAgent:
        from ..usage.tracking import wrap_provider_with_usage

        provider = wrap_provider_with_usage(
            provider,
            provider_name=provider_id,
            model=model,
            source="agent",
        )
        self._raw_provider = provider
        self._provider_adapter = ProviderAdapter(provider, provider_name=provider_id, model=model)

        base_prompt = self.cfg.get("agent", {}).get("system_prompt") or CODING_AGENT_PROMPT
        specialist = self.session.specialist_mode
        if specialist and specialist != "general":
            from ..agents.skills import SKILL_PROMPTS

            specialist_prompt = SKILL_PROMPTS.get(specialist)
            if specialist_prompt:
                base_prompt = specialist_prompt + "\n\n" + base_prompt
        aion_md = self._load_aion_md()
        if aion_md:
            base_prompt += f"\n\n# Project instructions (AION.md)\n{aion_md}"
        if self.session.project_info:
            base_prompt += f"\n\n# Project\n{self.session.project_info.summary()}"
        base_prompt += physics_system_hint(self.workspace_root)
        if self.session.interaction_mode == "review":
            base_prompt += (
                "\n\nReview mode: critique code quality, bugs, and style. "
                "Do not modify files or run commands."
            )
        if self.is_trusted:
            base_prompt += (
                f"\n\nWorkspace: {self.workspace_root}\n"
                "Trust: ON — you may edit files, write files, and run shell commands."
            )
        else:
            base_prompt += (
                f"\n\nWorkspace: {self.workspace_root}\n"
                "Trust: OFF — read-only; do not attempt write_file, edit_file, or run_command."
            )

        prompt = self.system_prompt or base_prompt
        tools = self._tools_for_session()
        if self.session.interaction_mode == "plain":
            provider.supports_tools = False  # type: ignore[attr-defined]

        agent = ReActAgent(
            provider=provider,
            registry=self.registry,
            tools=tools,
            system_prompt=prompt,
            memory=SlidingWindowMemory(window_size=40, system_prompt=prompt),
            max_steps=20,
            on_step=self._on_tool_step,
        )
        agent.force_tools = (
            self.session.force_tools
            or self.session.interaction_mode in ("debug", "plan")
        )
        self.tool_middleware.provider = provider_id
        self._emit("provider_capabilities", **self._provider_adapter.metadata(), **cached_model_metadata(provider_id, model))
        return agent

    def _connect_api_provider(
        self,
        provider_id: str,
        m_name: Optional[str],
        *,
        quiet: bool,
        new_key: bool,
        list_models: Callable[..., List[str]],
        create_kwargs: Callable[[str, str], Dict[str, Any]],
        label: str,
        supports_tools: bool = True,
    ) -> bool:
        api_key = self._ensure_api_key(provider_id, new_key=new_key, quiet=quiet)
        if not api_key:
            if quiet:
                ui.error_print(
                    f"No API key for {ui.bold(label)}. "
                    f"Run: {ui.cyan('aion api add Nvidia YOUR_KEY')}"
                )
            else:
                ui.error_print(
                    f"{label} requires an API key. "
                    f"Use {ui.cyan('aion api connect')} or set NVIDIA_API_KEY."
                )
            return False

        try:
            models = list_models(api_key=api_key)
        except ProviderError as e:
            ui.provider_error_print(e)
            return False
        if not models:
            ui.error_print(f"No {label} models available for this API key.")
            return False

        saved_prov = saved_provider(self.cfg)
        saved_mod = saved_model(self.cfg)
        pick_model = not quiet and m_name is None and not (
            saved_prov == provider_id and saved_mod
        )

        selected = self._pick_model(
            models,
            m_name=m_name,
            mod=None,
            prov=provider_id,
            saved_prov=saved_prov,
            saved_mod=saved_mod,
            quiet=quiet,
            pick_model=pick_model,
            provider_label=label,
        )
        if not selected:
            return False

        try:
            provider = create_provider(provider_id, **create_kwargs(selected, api_key))
            provider.supports_tools = supports_tools  # type: ignore[attr-defined]
            self.agent = self._build_agent(provider, provider_id, selected)
            self._apply_session(provider_id, selected)
            save_connection(self.cfg, provider=provider_id, model=selected)
            self.session.activity.log("connect", f"{provider_id} · {selected}")
            if not quiet:
                ui.success_print(
                    f"Connected to {ui.bold(label)} · {ui.accent_muted(selected)}. "
                    f"You can start chatting now."
                )
                ui.info_print(
                    f"Saved for next startup. {ui.dim('Use /disconnect to go offline.')}"
                )
            return True
        except ProviderError as e:
            ui.provider_error_print(e)
            return False
        except Exception as e:
            ui.error_print(f"Failed to connect: {e}")
            return False

    def _connect_cloud(
        self,
        provider_id: str,
        m_name: Optional[str],
        *,
        quiet: bool,
        new_key: bool,
    ) -> bool:
        from ..providers.gemini_provider import GeminiProvider

        list_fns = {
            "openai": lambda **kw: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            "deepseek": lambda **kw: ["deepseek-chat", "deepseek-reasoner"],
            "gemini": GeminiProvider.list_models,
            "anthropic": lambda **kw: ["claude-3-5-sonnet-latest", "claude-3-5-haiku-latest"],
        }
        list_models = list_fns.get(provider_id, lambda **kw: [])
        label = provider_display_name(provider_id)

        def create_kwargs(model: str, api_key: str) -> Dict[str, Any]:
            return {"model": model, "api_key": api_key}

        return self._connect_api_provider(
            provider_id,
            m_name,
            quiet=quiet,
            new_key=new_key,
            list_models=list_models,
            create_kwargs=create_kwargs,
            label=label,
            supports_tools=True,
        )

    def _connect_nvidia(
        self,
        m_name: Optional[str],
        *,
        quiet: bool,
        new_key: bool,
    ) -> bool:
        from ..providers.nvidia_provider import _CHAT_BLOCKLIST

        if m_name in _CHAT_BLOCKLIST:
            m_name = None
        return self._connect_api_provider(
            "nvidia",
            m_name,
            quiet=quiet,
            new_key=new_key,
            list_models=NvidiaProvider.list_models,
            create_kwargs=lambda model, api_key: {"model": model, "api_key": api_key},
            label="Nvidia",
            supports_tools=True,
        )

    def _connect_ollama(
        self,
        m_name: Optional[str],
        *,
        quiet: bool,
        prov: Optional[str],
        mod: Optional[str],
    ) -> bool:
        saved_prov = saved_provider(self.cfg)
        saved_mod = saved_model(self.cfg)
        if m_name:
            pass
        elif self.session.provider == AGENT_PROVIDER and self.session.model:
            m_name = self.session.model
        elif saved_prov == AGENT_PROVIDER and saved_mod:
            m_name = saved_mod
        else:
            m_name = None

        pick_model = not quiet and mod is None and not (
            saved_prov == AGENT_PROVIDER and saved_mod
        )

        try:
            ollama_models = OllamaProvider.list_models()
        except ProviderError as e:
            ui.provider_error_print(e)
            return False
        if not ollama_models:
            ui.error_print("No Ollama models found. Install one: ollama pull llama3")
            return False

        selected = self._pick_model(
            ollama_models,
            m_name=m_name,
            mod=mod,
            prov=prov,
            saved_prov=saved_prov,
            saved_mod=saved_mod,
            quiet=quiet,
            pick_model=pick_model,
            provider_label="Ollama",
        )
        if not selected:
            return False

        try:
            provider = create_provider(AGENT_PROVIDER, model=selected)

            if not quiet:
                if _probe_ollama_tools(provider, self.tools_schema):
                    provider.supports_tools = True  # type: ignore[attr-defined]
                else:
                    provider.supports_tools = False  # type: ignore[attr-defined]
            else:
                provider.supports_tools = False  # type: ignore[attr-defined]

            self.agent = self._build_agent(provider, AGENT_PROVIDER, selected)
            self._apply_session(AGENT_PROVIDER, selected)
            save_connection(self.cfg, provider=AGENT_PROVIDER, model=selected)
            self.session.activity.log("connect", f"ollama · {selected}")
            if not quiet:
                ui.success_print(
                    f"Connected to {ui.bold('Ollama')} · {ui.accent_muted(selected)}. "
                    f"You can start chatting now."
                )
                ui.info_print(
                    f"Saved for next startup. {ui.dim('Use /disconnect to go offline.')}"
                )
            return True
        except ProviderError as e:
            ui.provider_error_print(e)
            return False
        except Exception as e:
            ui.error_print(f"Failed to connect: {e}")
            return False

    def disconnect(
        self,
        *,
        forget_saved: bool = False,
        clear_keys_for: Optional[str] = None,
        disconnect_session: bool = True,
    ) -> bool:
        """
        End the current AI session; optionally clear saved provider or API keys.

        Returns True if API keys were cleared.
        """
        keys_cleared = False
        if clear_keys_for:
            clear_provider_keys(self.cfg, clear_keys_for)
            keys_cleared = True
        if disconnect_session:
            self.agent = None
            self.session.connected = False
            self.session.provider = None
            self.session.model = None
            self.session.tools_enabled = False
            self.session.mode = "offline"
            if forget_saved:
                clear_connection(self.cfg)
        return keys_cleared

    def _on_tool_step(self, step: int, action: str, result: str) -> None:
        if action in ("write_file", "edit_file"):
            for line in result.splitlines():
                if line.startswith("Wrote ") or line.startswith("Edited "):
                    parts = line.split()
                    if len(parts) >= 2:
                        path = parts[1].rstrip(".")
                        self.session.touched_files.add(path)
                        if self.session.interaction_mode in ("test", "debug"):
                            info = self.session.project_info
                            if info:
                                lint_out = run_lint_on_file(info, path)
                                if lint_out:
                                    ui.info_print(f"Linter: {ui.dim(lint_out[:200])}")
        preview = result.split("\n", 1)[0]
        if len(preview) > 120:
            preview = preview[:117] + "…"
        self.session.activity.log_tool(action, preview)
        self._emit("tool_step", step=step, action=action, preview=preview, result=result[:500])
        self._emit("chat_status", text=f"{action}: {preview}")
        if self.session.interaction_mode == "debug":
            ui.debug_tool_print(step, action, result)
            return
        ui.tool_print(action, preview)

    def chat(self, user_input: str) -> str:
        """Run chat with plan mode support."""
        if not self.agent:
            raise RuntimeError("Not connected")
        self.tool_middleware.start_task(user_input)
        if self.session.interaction_mode == "plan" and not self.session.pending_plan:
            from ..agents.planner import PlanningAgent

            self._planning_agent = PlanningAgent(
                self._raw_provider or self.agent.provider,
                self.registry,
                self.tools_schema,
            )
            plan = self._planning_agent._generate_plan(user_input)
            lines = [f"{i + 1}. {s.description}" for i, s in enumerate(plan)]
            ui.info_print("Plan:\n" + "\n".join(f"  {l}" for l in lines))
            ui.info_print(f"Use {ui.cyan('/approve')} to execute or edit the task.")
            self.session.pending_plan = True
            self._pending_task = user_input
            self._pending_plan_steps = plan
            self._emit("plan_ready", steps=lines)
            self._emit("session_updated")
            self.tool_middleware.finalize_task(rollback_on_failure=False)
            return "Plan ready. Type /approve to execute."

        response = self.agent.chat(user_input)
        raw = getattr(self._raw_provider, "_last_raw_response", None)
        if isinstance(raw, dict):
            usage = raw.get("usage") or {}
            total = usage.get("total_tokens")
            if total:
                self.session.activity.log_tokens(int(total))
        self.session.activity.log("chat", user_input[:80])

        if self.session.interaction_mode == "test" and self.session.touched_files:
            info = self.session.project_info
            if info and info.test_command:
                from ..tools.code_agent import run_command
                from ..tools.workspace import Workspace

                ws = Workspace(self.workspace_root)
                out = run_command(ws, info.test_command, timeout=120)
                self.session.activity.log("test", info.test_command)
                follow = (
                    f"Tests ran ({info.test_command}):\n{out[:4000]}\n"
                    "Summarize pass/fail for the user."
                )
                response = self.agent.chat(follow)
        intent = self.tool_middleware.finalize_task(rollback_on_failure=True)
        if intent is not None:
            self._emit("edit_intent", intent=intent.to_dict())
        return response

    def execute_plan(self) -> str:
        if not self._planning_agent or not getattr(self, "_pending_task", None):
            return "No pending plan. Ask a task in plan mode first."
        result = self._planning_agent.run(self._pending_task)
        self.session.pending_plan = False
        self.session.activity.log("plan", "executed")
        return result

    def print_edit_batch_summary(self) -> None:
        if self.session.interaction_mode != "debug":
            return
        if len(self.session.touched_files) < 2:
            self.session.touched_files.clear()
            return
        ui.info_print(
            f"Batch edit summary: {ui.bold(str(len(self.session.touched_files)))} files touched"
        )
        for path in sorted(self.session.touched_files):
            print(f"    {ui.dim('•')} {path}")
        self.session.touched_files.clear()

    def _apply_session(self, provider_id: str, model: str) -> None:
        self.session.connected = True
        self.session.provider = provider_id
        self.session.model = model
        self.session.mode = provider_id
        tools = self._tools_for_session()
        self.session.tools_enabled = bool(tools)
        self.session.current_status = "connected"
