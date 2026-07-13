"""Demo: simple pendulum simulation."""

from __future__ import annotations

from math import degrees, pi

from aion.physics.constraints import pendulum_energy_series, total_energy_drift
from aion.physics.systems import simulate_pendulum


def main() -> None:
    length = 1.0
    angle_deg = 15.0
    result = simulate_pendulum(length, angle_deg * pi / 180.0, dt=0.01, steps=2000)
    energies = pendulum_energy_series(result.trajectory, length=length)
    drift = total_energy_drift(energies)
    print(f"Pendulum length={length} m, initial angle={angle_deg}°")
    print(f"  Small-angle period (analytic): {result.summary['small_angle_period_s']:.4f} s")
    print(f"  Max theta: {degrees(result.summary['max_theta_rad']):.2f}°")
    print(f"  Relative energy drift: {drift:.2e}")
    print("demo_pendulum ok")


if __name__ == "__main__":
    main()
