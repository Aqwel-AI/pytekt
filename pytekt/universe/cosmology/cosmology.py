"""Basic cosmology calculations (flat Lambda-CDM)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from pytekt.universe.core.constants import C, H0_DEFAULT, OMEGA_M_DEFAULT


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


def _redshift_from_velocity_py(v_kms: float) -> float:
    beta = v_kms / (C / 1000.0)
    return math.sqrt((1 + beta) / (1 - beta)) - 1.0 if abs(beta) < 1 else float("inf")


def redshift_from_velocity(v_kms: float) -> float:
    """Special relativistic redshift from recession velocity."""
    from pytekt.universe.core._native import redshift_from_velocity as _rz

    return _rz(v_kms)


def hubble_flow_velocity(distance_mpc: float, cosmo: Optional[Cosmology] = None) -> float:
    cosmo = cosmo or Cosmology()
    from pytekt.universe.core._native import hubble_flow_velocity as _hfv

    return _hfv(distance_mpc, cosmo.H0)


def _e_z(z: float, cosmo: Cosmology) -> float:
    return math.sqrt(cosmo.Om0 * (1 + z) ** 3 + cosmo.Ode0)


def _comoving_distance_py(
    z: float, H0: float, Om0: float, Ode0: float, *, steps: int = 200
) -> float:
    if z <= 0:
        return 0.0
    dz = z / steps
    total = 0.0
    for i in range(steps):
        zi = (i + 0.5) * dz
        total += dz / math.sqrt(Om0 * (1 + zi) ** 3 + Ode0)
    return (C / 1000.0) / H0 * total


def comoving_distance_mpc(z: float, cosmo: Optional[Cosmology] = None, *, steps: int = 200) -> float:
    """Comoving distance (Mpc) via numerical integration."""
    cosmo = cosmo or Cosmology()
    from pytekt.universe.core._native import comoving_distance_mpc as _native_dc

    return _native_dc(z, cosmo.H0, cosmo.Om0, cosmo.Ode0, steps=steps)


def luminosity_distance_mpc(z: float, cosmo: Optional[Cosmology] = None) -> float:
    """Luminosity distance in Mpc (flat universe)."""
    cosmo = cosmo or Cosmology()
    from pytekt.universe.core._native import luminosity_distance_mpc as _native_dl

    return _native_dl(z, cosmo.H0, cosmo.Om0, cosmo.Ode0)


def angular_diameter_distance_mpc(z: float, cosmo: Optional[Cosmology] = None) -> float:
    cosmo = cosmo or Cosmology()
    from pytekt.universe.core._native import angular_diameter_distance_mpc as _native_da

    return _native_da(z, cosmo.H0, cosmo.Om0, cosmo.Ode0)


def _lookback_time_py(
    z: float, H0: float, Om0: float, Ode0: float, *, steps: int = 200
) -> float:
    if z <= 0:
        return 0.0
    h = H0 / 100.0
    dz = z / steps
    total = 0.0
    for i in range(steps):
        zi = (i + 0.5) * dz
        total += dz / ((1 + zi) * math.sqrt(Om0 * (1 + zi) ** 3 + Ode0))
    return 9.77813 / h * total


def lookback_time_gyr(z: float, cosmo: Optional[Cosmology] = None, *, steps: int = 200) -> float:
    """Lookback time in Gyr (flat universe, numerical integral)."""
    cosmo = cosmo or Cosmology()
    from pytekt.universe.core._native import lookback_time_gyr as _native_lb

    return _native_lb(z, cosmo.H0, cosmo.Om0, cosmo.Ode0, steps=steps)


def distance_modulus_cosmo(z: float, cosmo: Optional[Cosmology] = None) -> float:
    d_l = luminosity_distance_mpc(z, cosmo)
    d_pc = d_l * 1e6
    return 5.0 * math.log10(d_pc / 10.0)
