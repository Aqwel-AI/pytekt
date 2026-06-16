"""Agent slash commands for :mod:`aion.universe`."""

from __future__ import annotations

from typing import Any, Dict

from . import ui


def _observer_cfg(cfg: Dict[str, Any]) -> tuple[float, float]:
    section = cfg.get("universe") or cfg.get("cosmos") or {}
    return float(section.get("latitude", 40.18)), float(section.get("longitude", 44.51))


def handle_sky_command(args: str, *, cfg: Dict[str, Any]) -> None:
    """Handle ``/sky`` — moon phase and visible bright stars."""
    from ..universe import moon_phase, now_jd, whats_up
    from ..universe.observations import log_observation

    parts = args.split()
    sub = parts[0].lower() if parts else "tonight"
    lat, lon = _observer_cfg(cfg)

    if sub in ("tonight", "up", ""):
        jd = now_jd()
        phase, name = moon_phase(jd)
        ui.info_print(f"Moon: {ui.bold(name)} (phase {phase:.2f})")
        visible = whats_up(lat, lon, jd)
        if not visible:
            ui.info_print("No bright stars above 10° at your configured lat/lon.")
            return
        ui.info_print(f"Bright stars above horizon ({ui.bold(str(len(visible)))}):")
        for obj in visible[:10]:
            ui.info_print(
                f"  {obj.get('name', '?'):14} alt={obj['altitude']:.1f}° "
                f"az={obj['azimuth']:.1f}°"
            )
        return

    if sub == "log":
        jd = now_jd()
        visible = whats_up(lat, lon, jd)
        log_observation(latitude=lat, longitude=lon, objects=visible, notes=args)
        ui.success_print(f"Logged {len(visible)} objects to {ui.cyan('~/.aion/universe.db')}")
        return

    if sub == "moon":
        phase, name = moon_phase(now_jd())
        ui.info_print(f"Moon: {ui.bold(name)} · phase {phase:.2f}")
        return

    if sub == "web":
        from ..universe.launch import ensure_universe_dashboard

        url, started = ensure_universe_dashboard(open_browser=True)
        if started:
            ui.success_print(f"Universe dashboard started at {ui.cyan(url)}")
        else:
            ui.info_print(f"Universe dashboard: {ui.cyan(url)}")
        return

    ui.error_print(
        f"Usage: {ui.cyan('/sky')} | {ui.cyan('/sky moon')} | {ui.cyan('/sky log')} | {ui.cyan('/sky web')}"
    )
