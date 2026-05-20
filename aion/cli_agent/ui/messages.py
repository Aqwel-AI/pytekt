"""Chat-style output for the agent loop."""

from __future__ import annotations

from .style import (
    accent,
    accent_muted,
    bold,
    dim,
    italic,
    magenta,
    red,
    yellow,
)

AION_LABEL = "Aion"


def _aion_tag() -> str:
    return accent(bold(AION_LABEL)) + dim(" »")


def agent_print(text: str, name: str = "Aion") -> None:
    del name  # always branded as Aion
    print(f"\n{_aion_tag()}")
    for line in text.split("\n"):
        print(f"  {line}")


def user_input_prompt() -> str:
    return input(f"\n{accent(bold('You'))} {dim('» ')}").strip()


def tool_print(tool_name: str, args: str) -> None:
    print(
        f"  {_aion_tag()} {italic(accent_muted('tool'))} "
        f"{accent(bold(tool_name))}({dim(args)})"
    )


def success_print(text: str) -> None:
    print(f"  {accent('»')} {text}")


def error_print(text: str) -> None:
    print(f"  {red('»')} {text}")


def provider_error_print(err: object) -> None:
    """Show a provider/API failure in plain language (not a raw HTTP dump)."""
    from ...providers.errors import ProviderError

    if isinstance(err, ProviderError):
        msg = err.friendly_message()
        title = "Could not get a reply"
    else:
        msg = str(err)
        title = "Something went wrong"

    print(f"  {red('»')} {bold(title)}")
    for line in msg.split("\n"):
        if not line.strip():
            print()
        elif line.startswith("What you can do:"):
            print(f"  {line}")
        elif line.startswith("  •"):
            print(f"  {dim(line)}")
        else:
            print(f"  {line}")


def info_print(text: str) -> None:
    print(f"  {dim('»')} {text}")


def coming_soon_banner(feature: str) -> None:
    bar = "─" * max(16, len(feature) + 4)
    print(f"\n  {bold(magenta('─── ' + feature.upper() + ' ───'))}")
    print(f"  {yellow('🧠')} This feature is currently in development.")
    print(f"  {dim('Stay tuned for updates from Aqwel AI!')}")
    print(f"  {bold(magenta(bar))} \n")
