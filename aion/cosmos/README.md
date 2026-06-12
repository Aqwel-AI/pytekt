# Aion Cosmos

Lightweight astronomy toolkit for **observing**, **orbital mechanics**, and **cosmology basics** — NumPy-first, no Astropy required.

> **Precision:** v1 is educational / prototyping quality, not publication-grade astrometry.

## Quick start

```python
from aion.cosmos import (
    equatorial_to_horizontal,
    moon_phase,
    now_jd,
    whats_up,
    luminosity_distance_mpc,
)

jd = now_jd()
phase, name = moon_phase(jd)
print(name, phase)

alt, az = equatorial_to_horizontal(6.75, -16.7, 40.0, 44.5, jd)
visible = whats_up(40.0, 44.5, jd)
print(f"Sirius alt={alt:.1f}° · {len(visible)} bright stars up")

d_l = luminosity_distance_mpc(0.1)  # Mpc, flat ΛCDM H0=70
```

## CLI

```bash
aion cosmos moon
aion cosmos sky --lat 40.18 --lon 44.51
aion cosmos coords "6h 45m 08s" "-16d 42m 58s"
aion cosmos web              # browser dashboard (port 3857)
aion cosmos-dashboard        # alias for cosmos web
aion cosmos demo
```

## Web dashboard

React SPA at `aion/cosmos/web/` (built to `aion/cosmos/static/`).

**Tabs:** Tonight (Alt/Az sky map), Moon, Coordinates, Cosmology, Catalogs, Observation log.

```bash
aion cosmos web
# or build + launch:
./aion/cosmos/run_dashboard.sh

# Dev: terminal 1
aion cosmos web --no-browser
# terminal 2
cd aion/cosmos/web && npm run dev   # proxies /api → :3857
```

Observer lat/lon is read from `~/.aion.yaml` (`cosmos.latitude`, `cosmos.longitude`) and can be saved from the UI.

## Agent

In `aion agent`:

- `/sky` — moon phase and bright stars above horizon
- `/sky moon` — moon only
- `/sky log` — log session to `~/.aion/cosmos.db`
- `/sky web` — open Cosmos dashboard in browser

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
python -m aion.cosmos.examples.demo_coordinates
python -m aion.cosmos.examples.demo_sky_tonight
python -m aion.cosmos.examples.demo_cosmology
```

## Optional extras

```bash
pip install aqwel-aion[viz]    # matplotlib plots
pip install aqwel-aion[cosmos]   # same as viz for cosmos plots
```
