"""
Universe Astronomical Catalogs & Remote Querying
================================================

Provides curated built-in catalogs and remote query clients:
- Bright stars catalog (~17 brightest navigational stars)
- Messier deep-sky objects catalog
- Planetary mean orbital elements (J2000)
- Conversion of catalogs to PyTekt Dataset objects
- NASA Exoplanet Archive query client
"""

from __future__ import annotations

from .catalog_fetch import (
    EXOPLANET_CSV_URL,
    fetch_exoplanet_table,
)
from .catalogs import (
    catalog_to_dataset,
    load_bright_stars,
    load_messier,
    load_planets,
)

__all__ = [
    "load_bright_stars",
    "load_messier",
    "load_planets",
    "catalog_to_dataset",
    "fetch_exoplanet_table",
    "EXOPLANET_CSV_URL",
]
