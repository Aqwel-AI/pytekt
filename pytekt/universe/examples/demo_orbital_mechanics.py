"""Demo: Orbital mechanics, planetary positions, and Hohmann transfers."""

from __future__ import annotations

from pytekt.universe.core.constants import AU, MU_SUN
from pytekt.universe.ephemeris.orbits import (
    OrbitalElements,
    hohmann_transfer,
    kepler_third_law,
    planet_position,
    true_anomaly_from_mean,
)


def main() -> None:
    print("=== PyTekt Universe: Orbital Mechanics Demo ===")

    # 1. Kepler's Third Law
    period_earth_sec = kepler_third_law(AU, MU_SUN)
    period_earth_days = period_earth_sec / (24 * 3600)
    print(f"Earth Orbital Period: {period_earth_days:.2f} days (expected ~365.25)")

    # 2. Hohmann Transfer: Earth to Mars (r1=1.0 AU, r2=1.524 AU)
    r1_m = 1.0 * AU
    r2_m = 1.524 * AU
    res = hohmann_transfer(r1_m, r2_m, MU_SUN)
    tof_days = res["transfer_time_s"] / (24 * 3600)
    print("\nEarth -> Mars Hohmann Transfer:")
    print(f"  Delta-v 1 (Departure): {res['dv1'] / 1000.0:.2f} km/s")
    print(f"  Delta-v 2 (Arrival):   {res['dv2'] / 1000.0:.2f} km/s")
    print(f"  Total Delta-v:         {res['total_dv'] / 1000.0:.2f} km/s")
    print(f"  Time of Flight:        {tof_days:.1f} days (~{tof_days / 30.4:.1f} months)")

    # 3. Kepler Equation (Mean Anomaly -> True Anomaly)
    mean_anomaly_deg = 45.0
    eccentricity = 0.206  # Mercury-like
    nu_deg = true_anomaly_from_mean(mean_anomaly_deg, eccentricity)
    print(f"\nKepler Equation (e={eccentricity}):")
    print(f"  Mean Anomaly: {mean_anomaly_deg:.1f}° -> True Anomaly: {nu_deg:.1f}°")

    # 4. Planetary Positions
    print("\nPlanetary Positions at J2000:")
    for planet in ("Mercury", "Venus", "Earth", "Mars", "Jupiter"):
        pos = planet_position(planet, 2451545.0)
        print(f"  {planet:8}: r = {pos['r_au']:.3f} AU, heliocentric long = {pos['lon_deg']:.1f}°")

    print("\n[OK] demo_orbital_mechanics completed successfully.")


if __name__ == "__main__":
    main()
