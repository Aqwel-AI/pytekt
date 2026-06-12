"""Demo: cosmology distances."""

from __future__ import annotations

from aion.cosmos import Cosmology, lookback_time_gyr, luminosity_distance_mpc


def main() -> None:
    cosmo = Cosmology(H0=70, Om0=0.3)
    for z in (0.01, 0.1, 1.0):
        d_l = luminosity_distance_mpc(z, cosmo)
        t_lb = lookback_time_gyr(z, cosmo)
        print(f"z={z}: D_L={d_l:.1f} Mpc, lookback={t_lb:.2f} Gyr")
    print("demo_cosmology ok")


if __name__ == "__main__":
    main()
