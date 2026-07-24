"""Interactive installation profiles for Aqwel-Aion.

The normal ``pip install aqwel-aion`` flow stays non-interactive. After the
core package is installed, ``aion setup`` lets users choose optional feature
profiles from a green terminal menu.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import Dict, Optional, Sequence, Tuple


CORE_PACKAGES = ("Python >= 3.8", "numpy", "watchdog", "gitpython", "certifi")

PROFILES: Dict[str, Tuple[str, str, Tuple[str, ...]]] = {
    "core": ("Core", "Required runtime and lightweight research tools", ()),
    "ai": ("AI / Machine Learning", "Models, metrics, SciPy, pandas, and visualization", ("ai", "viz")),
    "science": ("Physics + Astronomy", "Physics, universe, and visualization", ("physics", "universe", "viz")),
    "vision": ("Computer Vision", "Pillow, OpenCV, and image operations", ("vision",)),
    "llm": ("LLM + RAG", "AI providers, tools, embeddings, and vector search", ("ai", "tools", "rag")),
    "full": ("Full installation", "All supported feature dependencies", ("full",)),
}

PROFILE_ORDER: Tuple[str, ...] = ("core", "ai", "science", "vision", "llm", "full")

PROFILE_PACKAGES: Dict[str, Tuple[str, ...]] = {
    "core": (),
    "ai": ("scipy", "scikit-learn", "pandas", "matplotlib", "transformers", "torch", "openai"),
    "science": ("matplotlib",),
    "vision": ("pillow", "opencv-python-headless"),
    "llm": ("scipy", "scikit-learn", "pandas", "transformers", "torch", "openai", "tiktoken", "sentence-transformers", "faiss-cpu"),
    "full": ("All optional Aion feature dependencies",),
}


def _style(text: str, code: str, enabled: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if enabled else text


def install_spec(profile: str, *, local: bool = False, full: bool = False) -> str:
    """Return the pip requirement for an installation profile."""
    if profile not in PROFILES:
        raise ValueError(f"Unknown installation profile: {profile}")
    target = "." if local else "aqwel-aion"
    extras = ("full",) if full else PROFILES[profile][2]
    if extras:
        target += "[" + ",".join(extras) + "]"
    return target


def _print_menu(*, color: bool) -> None:
    print()
    print(_style("  Aqwel-Aion Setup", "1", color))
    print(_style("  Choose an installation profile. Core dependencies are always included.", "36", color))
    print()
    for number, profile in enumerate(PROFILE_ORDER, start=1):
        label, description, _ = PROFILES[profile]
        marker = " (recommended)" if profile == "core" else ""
        print(f"  {_style(str(number), '92', color)}. {_style(label, '1', color)}{marker}")
        print(f"     {_style(description, '2', color)}")
    print()


def choose_profile(input_fn=input, *, color: bool = True) -> str:
    """Prompt for a profile and return its stable profile key."""
    _print_menu(color=color)
    while True:
        answer = input_fn(_style("  Select a profile [1]: ", "92", color)).strip().lower()
        if not answer:
            return "core"
        if answer in PROFILE_ORDER:
            return answer
        if answer.isdigit() and 1 <= int(answer) <= len(PROFILE_ORDER):
            return PROFILE_ORDER[int(answer) - 1]
        print(_style("  Please enter a number from 1 to 6 or a profile name.", "33", color))


def choose_full_install(input_fn=input, *, color: bool = True) -> bool:
    """Ask whether the user wants all optional Aion dependencies."""
    print(_style("  Step 2 — Choose dependency size", "1", color))
    print("  1. Selected profile only")
    print("     Core packages plus the feature profile you chose")
    print("  2. Full Aion installation")
    print("     Core packages plus every optional feature library")
    while True:
        answer = input_fn(_style("  Select dependency size [1]: ", "92", color)).strip().lower()
        if not answer or answer in ("1", "profile", "selected"):
            return False
        if answer in ("2", "full", "all", "y", "yes"):
            return True
        print(_style("  Please enter 1 or 2.", "33", color))


def confirm_install(input_fn=input, *, color: bool = True) -> bool:
    """Ask for final confirmation before invoking pip."""
    answer = input_fn(_style("  Start installation now? [Y/n]: ", "92", color)).strip().lower()
    return answer in ("", "y", "yes")


def _print_plan(profile: str, *, full: bool, spec: str, color: bool) -> None:
    print()
    print(_style("  Installation plan", "1", color))
    print(f"  Profile: {_style(PROFILES[profile][0], '92', color)}")
    print("  Required: " + ", ".join(CORE_PACKAGES))
    if full:
        print("  Optional: all Aion feature libraries")
    else:
        optional = PROFILE_PACKAGES[profile]
        print("  Optional: " + (", ".join(optional) if optional else "none"))
    print(f"  Package: {_style(spec, '96', color)}")
    print()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aion setup",
        description="Choose and install an Aqwel-Aion feature profile.",
    )
    parser.add_argument(
        "--profile",
        choices=PROFILE_ORDER,
        help="Install a profile without opening the interactive menu.",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Install the current checkout in editable mode instead of PyPI.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the pip command without running it.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Choose the full dependency set without asking the second question.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Start installation without the final confirmation prompt.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable green terminal colors.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the interactive installer and return a process exit code."""
    args = _build_parser().parse_args(argv)
    color = (
        not args.no_color
        and not os.environ.get("NO_COLOR")
        and hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
    )

    interactive = not args.profile and sys.stdin.isatty()
    if args.profile:
        profile = args.profile
    elif not interactive:
        print("Aion setup needs an interactive terminal. Use --profile for scripts or CI.")
        return 2
    else:
        profile = choose_profile(color=color)

    full = args.full
    if interactive and not args.full:
        full = choose_full_install(color=color)

    spec = install_spec(profile, local=args.local, full=full)
    command = [sys.executable, "-m", "pip", "install", "--upgrade"]
    if args.local:
        command.extend(["-e", spec])
    else:
        command.append(spec)

    rendered = " ".join(command)
    _print_plan(profile, full=full, spec=spec, color=color)
    print(_style(f"  $ {rendered}", "2", color))
    if interactive and not args.yes and not confirm_install(color=color):
        print(_style("  Installation cancelled.", "33", color))
        return 0
    if args.dry_run:
        print(_style("  Dry run complete.", "92", color))
        return 0

    result = subprocess.run(command, check=False)
    if result.returncode == 0:
        print(_style("\n  Aion setup complete.", "92", color))
        print("  Run `aion doctor` to verify your environment.")
    else:
        print(_style(f"\n  Installation failed with exit code {result.returncode}.", "31", color))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
