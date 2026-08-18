"""OpenAI-style tool definitions for chat/completions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def function_tool(
    name: str,
    description: str,
    *,
    properties: Dict[str, Any],
    required: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Build one entry for the ``tools`` array (type ``function``).

    Parameters
    ----------
    name
        Function name exposed to the model.
    description
        Human-readable description for the model.
    properties
        JSON-Schema-style ``properties`` object (types, descriptions, etc.).
    required
        List of required property names; default empty.
    """
    req = list(required or [])
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": dict(properties),
        "required": req,
    }
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }
