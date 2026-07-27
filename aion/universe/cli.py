"""``aion universe`` subcommands."""

from __future__ import annotations

import argparse

from .coordinates import angular_separation, equatorial_to_horizontal
from .observing import moon_phase, whats_up
from .time import now_jd
from .units import format_dec, format_ra, parse_dec, parse_ra


def universe_main(args: argparse.Namespace) -> None:
    action = getattr(args, "universe_action", None) or "help"

    if action == "moon":
        jd = now_jd()
        phase, name = moon_phase(jd)
        print(f"  Moon: {name} (phase {phase:.2f})")
        return

    if action in ("sky", "observe"):
        jd = now_jd()
        lat = args.lat
        lon = args.lon
        visible = whats_up(lat, lon, jd)
        print(f"  Objects above {args.min_alt}° (lat={lat}, lon={lon}):")
        for obj in visible[: args.limit]:
            print(
                f"    {obj.get('name', '?'):16}  alt={obj['altitude']:5.1f}°  "
                f"az={obj['azimuth']:6.1f}°  V={obj.get('vmag', '')}"
            )
        return

    if action == "coords":
        ra = parse_ra(args.ra)
        dec = parse_dec(args.dec)
        jd = now_jd()
        alt, az = equatorial_to_horizontal(ra, dec, args.lat, args.lon, jd)
        print(f"  RA {format_ra(ra)}  Dec {format_dec(dec)}")
        print(f"  Alt {alt:.2f}°  Az {az:.2f}°")
        return

    if action == "separation":
        sep = angular_separation(
            parse_ra(args.ra1),
            parse_dec(args.dec1),
            parse_ra(args.ra2),
            parse_dec(args.dec2),
        )
        print(f"  Angular separation: {sep:.4f}°")
        return

    if action == "demo":
        from .examples.demo_coordinates import main

        main()
        return

    if action == "web":
        from .launch import run_universe_dashboard

        run_universe_dashboard(
            host=getattr(args, "host", "127.0.0.1"),
            port=getattr(args, "port", 3857),
            open_browser=not getattr(args, "no_browser", False),
        )
        return

    print("  Usage: aion universe moon | sky | coords | separation | web | demo")


# Backward-compatible alias
cosmos_main = universe_main
