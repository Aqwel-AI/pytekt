"""Demo: Astronomical catalogs and dataset conversion."""

from __future__ import annotations

from pytekt.universe.catalogs.catalogs import (
    catalog_to_dataset,
    load_bright_stars,
    load_messier,
    load_planets,
)


def main() -> None:
    print("=== PyTekt Universe: Catalogs Demo ===")

    # 1. Bright Stars
    stars = load_bright_stars()
    print(f"Loaded {len(stars)} bright stars. Top 5:")
    for s in stars[:5]:
        print(f"  {s['name']:15} RA={s['ra_hours']:5.2f}h  Dec={s['dec_deg']:+6.1f}°  Vmag={s['vmag']:+4.2f}")

    # 2. Messier Objects
    messier = load_messier()
    print(f"\nLoaded {len(messier)} Messier objects. Samples:")
    for m in messier[:5]:
        print(f"  {m['name']:6} ({m.get('common_name', 'N/A'):18}): type={m.get('type', '?'):12} constellation={m.get('constellation', '?')}")

    # 3. Planets Orbital Data
    planets = load_planets()
    print(f"\nLoaded {len(planets)} solar system bodies:")
    for p in planets:
        print(f"  {p['name']:8}: a = {p['a']:5.3f} AU, e = {p['e']:5.3f}, i = {p['i']:4.1f}°, period = {p['period_yr']:5.2f} yr")

    # 4. Conversion to PyTekt Dataset
    ds = catalog_to_dataset(stars)
    print(f"\nConverted to Dataset: {ds}")

    print("\n[OK] demo_catalogs completed successfully.")


if __name__ == "__main__":
    main()
