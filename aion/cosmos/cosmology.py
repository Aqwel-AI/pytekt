"""Basic cosmology calculations (flat Lambda-CDM)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from .constants import C, H0_DEFAULT, OMEGA_M_DEFAULT


@dataclass
class Cosmology:
    """Flat Lambda-CDM cosmology."""

    H0: float = H0_DEFAULT  # km/s/Mpc
    Om0: float = OMEGA_M_DEFAULT
    Ode0: Optional[float] = None

    def __post_init__(self) -> None:
        if self.Ode0 is None:
            self.Ode0 = 1.0 - self.Om0

    @property
    def h(self) -> float:
        return self.H0 / 100.0


def redshift_from_velocity(v_kms: float) -> float:
    """Special relativistic redshift from recession velocity."""
    beta = v_kms / (C / 1000.0)
    return math.sqrt((1 + beta) / (1 - beta)) - 1.0 if abs(beta) < 1 else float("inf")


def hubble_flow_velocity(distance_mpc: float, cosmo: Optional[Cosmology] = None) -> float:
    cosmo = cosmo or Cosmology()
    return cosmo.H0 * distance_mpc


def _e_z(z: float, cosmo: Cosmology) -> float:
    return math.sqrt(cosmo.Om0 * (1 + z) ** 3 + cosmo.Ode0)


def comoving_distance_mpc(z: float, cosmo: Optional[Cosmology] = None, *, steps: int = 200) -> float:
    """Comoving distance (Mpc) via numerical integration."""
    cosmo = cosmo or Cosmology()
    if z <= 0:
        return 0.0
    dz = z / steps
    total = 0.0
    for i in range(steps):
        zi = (i + 0.5) * dz
        total += dz / _e_z(zi, cosmo)
    return (C / 1000.0) / cosmo.H0 * total


def luminosity_distance_mpc(z: float, cosmo: Optional[Cosmology] = None) -> float:
    """Luminosity distance in Mpc (flat universe)."""
    return comoving_distance_mpc(z, cosmo) * (1 + z)


def angular_diameter_distance_mpc(z: float, cosmo: Optional[Cosmology] = None) -> float:
    d_l = luminosity_distance_mpc(z, cosmo)
    return d_l / (1 + z) ** 2


def lookback_time_gyr(z: float, cosmo: Optional[Cosmology] = None, *, steps: int = 200) -> float:
    """Lookback time in Gyr (flat universe, numerical integral)."""
    cosmo = cosmo or Cosmology()
    if z <= 0:
        return 0.0
    dz = z / steps
    total = 0.0
    for i in range(steps):
        zi = (i + 0.5) * dz
        total += dz / ((1 + zi) * _e_z(zi, cosmo))
    # Hubble time ≈ 9.778 Gyr / h for H0 = 100*h km/s/Mpc
    return 9.77813 / cosmo.h * total


def distance_modulus_cosmo(z: float, cosmo: Optional[Cosmology] = None) -> float:
    d_l = luminosity_distance_mpc(z, cosmo)
    d_pc = d_l * 1e6
    return 5.0 * math.log10(d_pc / 10.0)
