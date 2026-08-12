"""Demo: what is visible tonight."""

from __future__ import annotations

from pytekt.universe import moon_phase, now_jd, whats_up


def main() -> None:
    jd = now_jd()
    phase, name = moon_phase(jd)
    print(f"Moon: {name} (phase {phase:.2f})")
    visible = whats_up(40.18, 44.51, jd)
    print("Bright stars above 10°:")
    for obj in visible[:8]:
        print(f"  {obj['name']:12} alt={obj['altitude']:5.1f}° az={obj['azimuth']:5.1f}°")
    print("demo_sky_tonight ok")


if __name__ == "__main__":
    main()
