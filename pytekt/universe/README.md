# PyTekt Universe — Astronomy & Astrometry Toolkit

Lightweight, high-performance astronomy toolkit for **astrometry**, **orbital mechanics**, **cosmology**, and **observational astronomy** with optional C++ hardware acceleration (`pytekt._pytekt_universe`) and pure Python fallbacks.

---

## 1. Architecture & Domain Taxonomy

The package is organized into 6 modular domain subpackages:

```
pytekt/universe/
├── core/                # Physical constants (AU, C, G, J2000), units, time, C++ native acceleration
├── astrometry/          # Coordinate frames (Equatorial/Horizontal/Galactic), precession, magnitudes
├── ephemeris/           # Keplerian orbital mechanics, planetary positions, lunar almanac, observing
├── cosmology/           # FLRW cosmological distances, lookback time, Hubble flow velocity, redshift
├── catalogs/            # Built-in star/Messier/planet catalogs, dataset conversion, exoplanet queries
├── service/             # Astronomy pipeline steps, sky map & orbit plots, CLI, REST API & dashboard
├── data/                # Astronomical JSON databases (bright_stars.json, messier.json)
└── __init__.py          # Unified entry point & backward compatibility aliases
```

### Domain Subpackage Reference

| Subpackage | Key Exports | Primary Use Cases |
|---|---|---|
| **`pytekt.universe.core`** | `AU`, `C`, `G`, `J2000`, `deg_to_rad`, `format_ra`, `format_dec`, `now_jd`, `gmst`, `lst` | Physical constants, coordinate string parsing, sidereal time |
| **`pytekt.universe.astrometry`** | `equatorial_to_horizontal`, `horizontal_to_equatorial`, `equatorial_to_galactic`, `precess`, `apparent_magnitude`, `distance_modulus` | Telescope pointing, Alt/Az conversions, epoch precession, photometry |
| **`pytekt.universe.ephemeris`** | `moon_phase`, `moon_illumination`, `whats_up`, `air_mass`, `kepler_third_law`, `hohmann_transfer`, `planet_position` | Lunar phase tracking, stargazing session planning, orbital transfers |
| **`pytekt.universe.cosmology`** | `Cosmology`, `comoving_distance_mpc`, `luminosity_distance_mpc`, `lookback_time_gyr`, `redshift_from_velocity` | FLRW cosmological calculations, Hubble flow, universe expansion |
| **`pytekt.universe.catalogs`** | `load_bright_stars`, `load_messier`, `load_planets`, `catalog_to_dataset`, `fetch_exoplanet_table` | Curated celestial databases, dataset analysis, exoplanet tables |
| **`pytekt.universe.service`** | `UniverseCatalogStep`, `UniversePlotStep`, `plot_skymap`, `plot_orbit`, `run_server`, `run_universe_dashboard` | Pipeline orchestration, interactive charts, REST server & web dashboard |

---

## 2. Quick Start

### 2.1 Domain Subpackage Imports (Recommended)

```python
from pytekt.universe.core import now_jd
from pytekt.universe.astrometry import equatorial_to_horizontal
from pytekt.universe.ephemeris import moon_phase, whats_up
from pytekt.universe.cosmology import Cosmology, luminosity_distance_mpc

# 1. Ephemeris & Observing
jd = now_jd()
phase, name = moon_phase(jd)
print(f"Moon: {name} (phase={phase:.2f})")

# 2. Celestial Coordinates (Sirius Alt/Az from lat 40.0, lon 44.5)
alt, az = equatorial_to_horizontal(6.75, -16.7, 40.0, 44.5, jd)
visible = whats_up(40.0, 44.5, jd)
print(f"Sirius: alt={alt:.1f}°, az={az:.1f}° · {len(visible)} bright stars above horizon")

# 3. Cosmology Model
cosmo = Cosmology(H0=70.0, Om0=0.3)
print(f"Luminosity Distance (z=0.1): {cosmo.luminosity_distance(0.1):.1f} Mpc")
```

---

## 3. CLI & Web Dashboard

```bash
# Lunar phase
pytekt universe moon

# What's up tonight
pytekt universe sky --lat 40.18 --lon 44.51

# Coordinate conversion
pytekt universe coords "6h 45m 08s" "-16d 42m 58s"

# Launch browser dashboard (port 3857)
pytekt universe web
```
