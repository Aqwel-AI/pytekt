# Aion Universe

Lightweight astronomy toolkit for **observing**, **orbital mechanics**, and **cosmology basics** — NumPy-first, no Astropy required. Hot-path math runs in C++ (`aion._aion_universe`) when built; pure Python fallbacks always available.

> **Precision:** v1 is educational / prototyping quality, not publication-grade astrometry.

## Quick start

```python
from aion.universe import (
    equatorial_to_horizontal,
    moon_phase,
    now_jd,
    whats_up,
    luminosity_distance_mpc,
    using_native_extension,
)

print("C++ extension:", using_native_extension())

jd = now_jd()
phase, name = moon_phase(jd)
print(name, phase)

alt, az = equatorial_to_horizontal(6.75, -16.7, 40.0, 44.5, jd)
visible = whats_up(40.0, 44.5, jd)
print(f"Sirius alt={alt:.1f}° · {len(visible)} bright stars up")

d_l = luminosity_distance_mpc(0.1)  # Mpc, flat ΛCDM H0=70
```

`aion.cosmos` remains a deprecated import alias for `aion.universe`.

## CLI

```bash
aion universe moon
aion universe sky --lat 40.18 --lon 44.51
aion universe coords "6h 45m 08s" "-16d 42m 58s"
aion universe web              # browser dashboard (port 3857)
aion universe-dashboard        # alias for universe web
aion universe demo

# deprecated aliases still work:
aion cosmos web
```

## Web dashboard

React SPA at `aion/universe/web/` (built to `aion/universe/static/`).

**Tabs:** Tonight (Alt/Az sky map), Moon, Coordinates, Cosmology, Catalogs, Observation log.

```bash
aion universe web
# or build + launch:
./aion/universe/run_dashboard.sh

# Dev: terminal 1
aion universe web --no-browser
# terminal 2
cd aion/universe/web && npm run dev   # proxies /api → :3857
```

Observer lat/lon is read from `~/.aion.yaml` (`universe.latitude`, `universe.longitude`; `cosmos.*` still accepted) and can be saved from the UI.

## Agent (not available)

Slash commands below require the terminal agent, which is **not available** in 0.2.0. Use `aion universe …` CLI today.

- `/sky` — moon phase and bright stars above horizon
- `/sky moon` — moon only
- `/sky log` — log session to `~/.aion/cosmos.db`
- `/sky web` — open Universe dashboard in browser

## Native C++ extension

Build with the main package (requires pybind11):

```bash
pip install pybind11
pip install -e .
python -c "from aion.universe import using_native_extension; print(using_native_extension())"
```

Accelerated paths (C++ in `src/aion_universe.cpp`):

| Area | Functions |
|------|-----------|
| Time | `gmst_hours`, `lst_hours` |
| Coordinates | `equatorial_to_horizontal` (+ batch), `horizontal_to_equatorial`, `angular_separation`, galactic/ecliptic transforms, `precess` |
| Observing | `air_mass` (+ batch), `rise_set_approx`, `moon_phase_fraction`, `moon_illumination`, `is_circumpolar` |
| Orbits | Kepler solver, `hohmann_transfer`, `planet_ecliptic_position`, `position_from_elements` |
| Cosmology | comoving/luminosity/angular-diameter distance, lookback time, `redshift_from_velocity`, `hubble_flow_velocity` |
| Photometry | flux↔magnitude, distance modulus, absolute/apparent magnitude |

## Modules

| Module | Contents |
|--------|----------|
| `constants` | AU, ly, pc, c, H₀, G, J2000 |
| `units` | Angles, distances, magnitudes |
| `time` | Julian date, GMST, LST |
| `coordinates` | RA/Dec ↔ Alt/Az, galactic, separation |
| `observing` | Moon, air mass, rise/set, `whats_up` |
| `orbits` | Kepler elements, Hohmann, planet positions |
| `cosmology` | Flat ΛCDM distances, lookback time |
| `magnitude` | Distance modulus, color index |
| `catalogs` | Bright stars, Messier, planets |
| `viz` | Sky map, HR diagram (requires `[viz]`) |
| `observations` | Log sessions via `aion.db` |

## Examples

```bash
python -m aion.universe.examples.demo_coordinates
python -m aion.universe.examples.demo_sky_tonight
python -m aion.universe.examples.demo_cosmology
```

## Optional extras

```bash
pip install aqwel-aion[viz]       # matplotlib plots
pip install aqwel-aion[universe]  # same as viz for universe plots
```
