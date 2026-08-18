"""Demo: coordinate transforms."""

from __future__ import annotations

from pytekt.universe import (
    angular_separation,
    equatorial_to_galactic,
    equatorial_to_horizontal,
    format_dec,
    format_ra,
    now_jd,
    parse_ra,
    parse_dec,
)


def main() -> None:
    # Sirius
    ra = parse_ra("6h 45m 08s")
    dec = parse_dec("-16d 42m 58s")
    jd = now_jd()
    lat, lon = 40.18, 44.51  # Yerevan approx
    alt, az = equatorial_to_horizontal(ra, dec, lat, lon, jd)
    gl, gb = equatorial_to_galactic(ra, dec)
    sep = angular_separation(ra, dec, parse_ra("6h 23m"), parse_dec("+23d 28m"))
    print("Sirius:")
    print(f"  RA/Dec: {format_ra(ra)}  {format_dec(dec)}")
    print(f"  Alt/Az @ lat={lat}: {alt:.1f}° / {az:.1f}°")
    print(f"  Galactic l,b: {gl:.1f}°, {gb:.1f}°")
    print(f"  Sep to Pollux region: {sep:.2f}°")
    print("demo_coordinates ok")


if __name__ == "__main__":
    main()
