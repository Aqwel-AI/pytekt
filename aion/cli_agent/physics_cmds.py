"""Agent slash commands for :mod:`aion.physics`."""

from __future__ import annotations

from typing import Any, Dict

from . import ui


def handle_physics_command(args: str, *, cfg: Dict[str, Any]) -> None:
    """Handle ``/physics`` subcommands."""
    parts = args.split()
    sub = parts[0].lower() if parts else "help"

    if sub == "web":
        from ..physics.launch import ensure_physics_dashboard

        url, started = ensure_physics_dashboard(open_browser=True)
        if started:
            ui.success_print(f"Physics dashboard started at {ui.cyan(url)}")
        else:
            ui.info_print(f"Physics dashboard: {ui.cyan(url)}")
        return

    if sub == "tasks":
        from ..physics import supported_physics_tasks

        ui.info_print("Supported physics query tasks:")
        for task in supported_physics_tasks():
            ui.info_print(f"  {task}")
        return

    if sub == "query":
        text = " ".join(parts[1:]).strip()
        if not text:
            ui.error_print(f"Usage: {ui.cyan('/physics query')} <description>")
            return
        from ..physics import solve_physics_query

        result = solve_physics_query(text)
        ui.success_print(
            f"{result.output_name} = {ui.bold(str(result.output_value))} {result.unit}"
        )
        ui.info_print(result.explanation)
        return

    if sub == "pendulum":
        length = 1.0
        angle = 15.0
        for i, token in enumerate(parts[1:], 1):
            if token == "--length" and i + 1 < len(parts):
                length = float(parts[i + 1])
            if token == "--angle" and i + 1 < len(parts):
                angle = float(parts[i + 1])
        from math import pi

        from ..physics import simulate_pendulum

        result = simulate_pendulum(length, angle * pi / 180.0, steps=500)
        ui.success_print(
            f"Period (small-angle): {result.summary['small_angle_period_s']:.4f} s"
        )
        return

    ui.error_print(
        f"Usage: {ui.cyan('/physics query')} ... | {ui.cyan('/physics pendulum')} | "
        f"{ui.cyan('/physics tasks')} | {ui.cyan('/physics web')}"
    )
