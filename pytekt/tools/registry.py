"""Map tool names to callables; validate arguments without eval."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional


class ToolRegistry:
    """
    Register Python callables by name; invoke with JSON arguments from the model.
    """

    def __init__(self) -> None:
        self._fns: Dict[str, Callable[..., Any]] = {}
        self._required: Dict[str, List[str]] = {}

    def register(
        self,
        name: str,
        fn: Callable[..., Any],
        *,
        required_arg_keys: Optional[List[str]] = None,
    ) -> None:
        """
        Register ``fn``. If ``required_arg_keys`` is set, JSON args must contain
        those keys (stdlib check only; not full JSON Schema validation).
        """
        self._fns[name] = fn
        if required_arg_keys:
            self._required[name] = list(required_arg_keys)

    def call(self, name: str, arguments_json: str) -> str:
        """
        Parse ``arguments_json``, validate required keys, call the tool, return
        a string suitable for a ``role: tool`` message ``content``.
        """
        if name not in self._fns:
            return json.dumps({"error": f"unknown_tool: {name}"})
        try:
            args: Dict[str, Any] = (
                json.loads(arguments_json) if arguments_json.strip() else {}
            )
        except json.JSONDecodeError as e:
            return json.dumps({"error": "invalid_json", "detail": str(e)})
        if not isinstance(args, dict):
            return json.dumps({"error": "arguments_must_be_json_object"})
        req = self._required.get(name, [])
        missing = [k for k in req if k not in args]
        if missing:
            return json.dumps({"error": "missing_keys", "keys": missing})
        try:
            out = self._fns[name](**args)
        except TypeError as e:
            return json.dumps({"error": "call_failed", "detail": str(e)})
        except Exception as e:  # noqa: BLE001 — surface to model
            return json.dumps({"error": "tool_exception", "detail": str(e)})
        if isinstance(out, str):
            return out
        return json.dumps(out, default=str)
