"""Built-in astronomical catalogs."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
if not os.path.isdir(_DATA_DIR):
    _DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _load_json(name: str) -> List[Dict[str, Any]]:
    path = os.path.join(_DATA_DIR, name)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_bright_stars() -> List[Dict[str, Any]]:
    """~17 brightest stars with RA (hours), Dec (deg), V magnitude."""
    return _load_json("bright_stars.json")


def load_messier() -> List[Dict[str, Any]]:
    """Selected Messier objects."""
    return _load_json("messier.json")


def load_planets() -> List[Dict[str, Any]]:
    """
    Mean orbital elements at J2000 (low precision).

    a in AU, angles in degrees, period in years.
    """
    return [
        {"name": "Mercury", "a": 0.387, "e": 0.206, "i": 7.0, "L": 252.25, "period_yr": 0.24},
        {"name": "Venus", "a": 0.723, "e": 0.007, "i": 3.4, "L": 181.98, "period_yr": 0.62},
        {"name": "Earth", "a": 1.000, "e": 0.017, "i": 0.0, "L": 100.46, "period_yr": 1.00},
        {"name": "Mars", "a": 1.524, "e": 0.093, "i": 1.85, "L": 355.45, "period_yr": 1.88},
        {"name": "Jupiter", "a": 5.203, "e": 0.048, "i": 1.30, "L": 34.40, "period_yr": 11.86},
        {"name": "Saturn", "a": 9.537, "e": 0.054, "i": 2.49, "L": 49.94, "period_yr": 29.46},
        {"name": "Uranus", "a": 19.191, "e": 0.047, "i": 0.77, "L": 313.23, "period_yr": 84.01},
        {"name": "Neptune", "a": 30.069, "e": 0.009, "i": 1.77, "L": 304.88, "period_yr": 164.8},
    ]


def catalog_to_dataset(catalog: List[Dict[str, Any]], *, name: str = "universe"):
    """Export catalog rows as :class:`pytekt.datasets.Dataset`."""
    import numpy as np
    from ..datasets import Dataset

    ra = np.array([float(r.get("ra_hours", r.get("ra", 0))) for r in catalog])
    dec = np.array([float(r.get("dec_deg", r.get("dec", 0))) for r in catalog])
    vmag = np.array([float(r.get("vmag", 0)) for r in catalog])
    data = np.column_stack([ra, dec, vmag])
    return Dataset(
        data=data,
        target=np.zeros(len(catalog)),
        feature_names=["ra_hours", "dec_deg", "vmag"],
        target_names=["n/a"],
        name=name,
        metadata={"n": len(catalog)},
    )
