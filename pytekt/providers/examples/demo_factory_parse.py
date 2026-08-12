"""List supported provider names and parse a minimal chat-completion JSON."""
from __future__ import annotations

from pytekt.providers import parse_chat_completion_response, supported_providers


def main() -> None:
    names = supported_providers()
    assert "openai" in names
    fake = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello from a stub response.",
                }
            }
        ]
    }
    turn = parse_chat_completion_response(fake)
    assert turn.content and not turn.tool_calls
    print("demo_factory_parse ok — providers:", ", ".join(names[:3]), "…")
    print("  parsed content:", turn.content)


if __name__ == "__main__":
    main()
