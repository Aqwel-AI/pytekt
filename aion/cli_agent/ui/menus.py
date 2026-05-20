"""Interactive menus and prompts."""

from __future__ import annotations

from typing import List, Optional

from .style import ICON_CONFIG, bold, cyan, dim, red


def print_menu(options: List[str], title: str = "Select an option") -> None:
    print(f"  {bold(title)}:")
    for i, opt in enumerate(options, 1):
        print(f"    {cyan(str(i))} {opt}")
    print()


def get_menu_choice(options: List[str], *, default: int = 1) -> int:
    while True:
        try:
            choice = input(
                f"\n  {bold('Choice (1-' + str(len(options)) + '):')} "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {dim('Cancelled.')}")
            raise
        if not choice:
            return default
        try:
            idx = int(choice)
        except ValueError:
            print(f"  {red('Invalid choice. Please try again.')}")
            continue
        if 1 <= idx <= len(options):
            return idx
        print(f"  {red('Invalid choice. Please try again.')}")


def get_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        try:
            val = input(f"  {bold(prompt)}{suffix}: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {dim('Cancelled.')}")
            raise
        if not val:
            return default
        if val in ("y", "yes"):
            return True
        if val in ("n", "no"):
            return False
        print(f"  {red('Please enter y or n.')}")


def prompt_text(label: str, *, icon: str = ICON_CONFIG, required: bool = True) -> Optional[str]:
    try:
        val = input(f"  {icon} {label}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n  {dim('Cancelled.')}")
        raise
    if required and not val:
        return None
    return val or None
