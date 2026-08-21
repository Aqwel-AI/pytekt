# PyTekt Universe — Examples

Runnable examples demonstrating coordinate systems, observational astronomy, cosmological expansion, orbital dynamics, and astronomical catalogs.

---

## 📚 Example Demos

| Script | Domain | Description | Run Command |
|---|---|---|---|
| [`demo_coordinates.py`](demo_coordinates.py) | **Astrometry** | Equatorial, Horizontal (Alt/Az), and Galactic coordinate transformations, angular separation, and precession. | `python -m pytekt.universe.examples.demo_coordinates` |
| [`demo_sky_tonight.py`](demo_sky_tonight.py) | **Ephemeris** | Lunar phase & illumination calculation and visible bright stars for tonight. | `python -m pytekt.universe.examples.demo_sky_tonight` |
| [`demo_orbital_mechanics.py`](demo_orbital_mechanics.py) | **Ephemeris** | Kepler's 3rd Law, Earth-to-Mars Hohmann transfer delta-v, Kepler equation solver, and planetary positions. | `python -m pytekt.universe.examples.demo_orbital_mechanics` |
| [`demo_cosmology.py`](demo_cosmology.py) | **Cosmology** | FLRW cosmology model, luminosity distances, comoving distances, and lookback time across redshifts. | `python -m pytekt.universe.examples.demo_cosmology` |
| [`demo_catalogs.py`](demo_catalogs.py) | **Catalogs** | Loading built-in bright star and Messier object catalogs and converting them into PyTekt Dataset format. | `python -m pytekt.universe.examples.demo_catalogs` |

---

## 🚀 Running All Demos

```bash
python -m pytekt.universe.examples.demo_coordinates
python -m pytekt.universe.examples.demo_sky_tonight
python -m pytekt.universe.examples.demo_orbital_mechanics
python -m pytekt.universe.examples.demo_cosmology
python -m pytekt.universe.examples.demo_catalogs
```
