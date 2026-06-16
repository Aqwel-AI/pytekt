"""JSON API helpers for the Cosmos web dashboard."""

from __future__ import annotations

import base64
import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .catalogs import load_bright_stars, load_messier, load_planets
from .coordinates import (
    angular_separation,
    equatorial_to_galactic,
    equatorial_to_horizontal,
    horizontal_to_equatorial,
)
from .cosmology import Cosmology, hubble_flow_velocity, lookback_time_gyr, luminosity_distance_mpc
from .observations import list_observations, log_observation
from .observing import moon_illumination, moon_phase, rise_set_approx, whats_up, whats_up_all
from .orbits import planet_position
from .time import datetime_to_jd, now_jd
from .units import format_dec, format_ra, parse_dec, parse_ra


def library_info() -> Dict[str, Any]:
    try:
        from .. import __developer__, __version__

        return {
            "app": "universe",
            "version": __version__,
            "developer": __developer__,
        }
    except Exception:
        return {"app": "universe", "version": "unknown"}


def get_observer_config() -> Dict[str, float]:
    try:
        from ..cli_agent.config import get_config

        cfg = get_config()
        section = cfg.get("universe") or cfg.get("cosmos") or {}
        return {
            "latitude": float(section.get("latitude", 40.18)),
            "longitude": float(section.get("longitude", 44.51)),
        }
    except Exception:
        return {"latitude": 40.18, "longitude": 44.51}


def save_observer_config(latitude: float, longitude: float) -> Dict[str, float]:
    from ..cli_agent.config import get_config, save_config

    cfg = get_config()
    cfg.setdefault("universe", {})
    cfg["universe"]["latitude"] = latitude
    cfg["universe"]["longitude"] = longitude
    save_config(cfg)
    return {"latitude": latitude, "longitude": longitude}


def observer_payload(
    *,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    jd: Optional[float] = None,
) -> Dict[str, Any]:
    defaults = get_observer_config()
    lat = latitude if latitude is not None else defaults["latitude"]
    lon = longitude if longitude is not None else defaults["longitude"]
    jd_val = jd if jd is not None else now_jd()
    dt = datetime.now(timezone.utc)
    try:
        from ..cli_agent.context_info import get_agent_context

        context = get_agent_context()
    except Exception:
        context = {}
    return {
        "latitude": lat,
        "longitude": lon,
        "jd": jd_val,
        "utc_iso": dt.isoformat(),
        "context": context,
    }


def moon_payload(jd: Optional[float] = None) -> Dict[str, Any]:
    jd_val = jd if jd is not None else now_jd()
    phase, name = moon_phase(jd_val)
    return {
        "jd": jd_val,
        "phase": phase,
        "name": name,
        "illumination": moon_illumination(jd_val),
    }


def sky_payload(
    *,
    latitude: float,
    longitude: float,
    jd: Optional[float] = None,
    catalog: str = "all",
    min_altitude: float = 10.0,
) -> Dict[str, Any]:
    jd_val = jd if jd is not None else now_jd()
    objects = whats_up_all(
        latitude,
        longitude,
        jd_val,
        catalog_mode=catalog,
        min_altitude=min_altitude,
    )
    return {
        "latitude": latitude,
        "longitude": longitude,
        "jd": jd_val,
        "catalog": catalog,
        "min_altitude": min_altitude,
        "count": len(objects),
        "objects": objects,
    }


def coords_payload(
    *,
    mode: str,
    latitude: float,
    longitude: float,
    jd: Optional[float] = None,
    ra: Optional[str] = None,
    dec: Optional[str] = None,
    alt: Optional[float] = None,
    az: Optional[float] = None,
    ra1: Optional[str] = None,
    dec1: Optional[str] = None,
    ra2: Optional[str] = None,
    dec2: Optional[str] = None,
) -> Dict[str, Any]:
    jd_val = jd if jd is not None else now_jd()
    mode_l = (mode or "equatorial_to_horizontal").lower()

    if mode_l in ("equatorial_to_horizontal", "eq_to_hor", "radec_to_altaz"):
        ra_h = parse_ra(ra or "0h")
        dec_d = parse_dec(dec or "0d")
        alt_v, az_v = equatorial_to_horizontal(ra_h, dec_d, latitude, longitude, jd_val)
        gl, gb = equatorial_to_galactic(ra_h, dec_d)
        return {
            "mode": mode_l,
            "input": {"ra_hours": ra_h, "dec_deg": dec_d, "ra": format_ra(ra_h), "dec": format_dec(dec_d)},
            "output": {"altitude": alt_v, "azimuth": az_v, "galactic_l": gl, "galactic_b": gb},
            "jd": jd_val,
        }

    if mode_l in ("horizontal_to_equatorial", "hor_to_eq", "altaz_to_radec"):
        ra_h, dec_d = horizontal_to_equatorial(
            float(alt or 0),
            float(az or 0),
            latitude,
            longitude,
            jd_val,
        )
        return {
            "mode": mode_l,
            "input": {"altitude": alt, "azimuth": az},
            "output": {"ra_hours": ra_h, "dec_deg": dec_d, "ra": format_ra(ra_h), "dec": format_dec(dec_d)},
            "jd": jd_val,
        }

    if mode_l == "separation":
        ra1_h = parse_ra(ra1 or "0h")
        dec1_d = parse_dec(dec1 or "0d")
        ra2_h = parse_ra(ra2 or "0h")
        dec2_d = parse_dec(dec2 or "0d")
        sep = angular_separation(ra1_h, dec1_d, ra2_h, dec2_d)
        return {
            "mode": mode_l,
            "separation_deg": sep,
            "point1": {"ra": format_ra(ra1_h), "dec": format_dec(dec1_d)},
            "point2": {"ra": format_ra(ra2_h), "dec": format_dec(dec2_d)},
        }

    raise ValueError(f"Unknown coords mode: {mode!r}")


def galactic_payload(ra: str, dec: str) -> Dict[str, Any]:
    ra_h = parse_ra(ra)
    dec_d = parse_dec(dec)
    gl, gb = equatorial_to_galactic(ra_h, dec_d)
    return {"ra_hours": ra_h, "dec_deg": dec_d, "galactic_l": gl, "galactic_b": gb}


def cosmology_payload(
    z: float,
    *,
    h0: float = 70.0,
    om0: float = 0.3,
) -> Dict[str, Any]:
    cosmo = Cosmology(H0=h0, Om0=om0)
    d_l = luminosity_distance_mpc(z, cosmo)
    return {
        "z": z,
        "H0": h0,
        "Om0": om0,
        "luminosity_distance_mpc": d_l,
        "lookback_time_gyr": lookback_time_gyr(z, cosmo),
        "hubble_velocity_kms": hubble_flow_velocity(d_l, cosmo),
    }


def cosmology_curve(
    *,
    z_max: float = 2.0,
    steps: int = 20,
    h0: float = 70.0,
    om0: float = 0.3,
) -> Dict[str, Any]:
    cosmo = Cosmology(H0=h0, Om0=om0)
    points = []
    for i in range(steps + 1):
        z = z_max * i / steps
        points.append(
            {
                "z": z,
                "luminosity_distance_mpc": luminosity_distance_mpc(z, cosmo),
            }
        )
    return {"H0": h0, "Om0": om0, "points": points}


def catalog_stars() -> List[Dict[str, Any]]:
    return load_bright_stars()


def catalog_messier() -> List[Dict[str, Any]]:
    return load_messier()


def catalog_planets(jd: Optional[float] = None) -> List[Dict[str, Any]]:
    from .observing import ecliptic_to_equatorial

    jd_val = jd if jd is not None else now_jd()
    rows = []
    for planet in load_planets():
        pos = planet_position(planet["name"], jd_val)
        ra, dec = ecliptic_to_equatorial(pos["lon_deg"], pos.get("lat_deg", 0.0))
        rows.append(
            {
                **planet,
                **pos,
                "ra_hours": round(ra, 4),
                "dec_deg": round(dec, 4),
                "kind": "planet",
                "jd": jd_val,
            }
        )
    return rows


def rise_set_payload(
    *,
    ra: str,
    dec: str,
    latitude: float,
    longitude: float,
    jd: Optional[float] = None,
) -> Dict[str, Any]:
    jd_val = jd if jd is not None else now_jd()
    ra_h = parse_ra(ra)
    dec_d = parse_dec(dec)
    times = rise_set_approx(ra_h, dec_d, latitude, longitude, jd_val)
    return {
        "ra": format_ra(ra_h),
        "dec": format_dec(dec_d),
        "latitude": latitude,
        "longitude": longitude,
        "jd": jd_val,
        **times,
    }


def observations_payload(*, limit: int = 50) -> Dict[str, Any]:
    rows = list_observations(limit=limit)
    return {"count": len(rows), "observations": rows}


def log_observation_payload(
    *,
    latitude: float,
    longitude: float,
    catalog: str = "all",
    notes: str = "",
    min_altitude: float = 10.0,
) -> Dict[str, Any]:
    jd_val = now_jd()
    objects = whats_up_all(
        latitude,
        longitude,
        jd_val,
        catalog_mode=catalog,
        min_altitude=min_altitude,
    )
    row_id = log_observation(
        latitude=latitude,
        longitude=longitude,
        objects=objects,
        notes=notes,
    )
    return {"id": row_id, "object_count": len(objects), "objects": objects}


def plot_sky_png_base64(
    *,
    catalog: str = "all",
    latitude: float = 40.0,
    longitude: float = 0.0,
) -> Dict[str, Any]:
    try:
        from .viz import plot_sky_map
    except ImportError as e:
        return {"ok": False, "error": str(e)}
    jd_val = now_jd()
    rows = whats_up_all(latitude, longitude, jd_val, catalog_mode=catalog, min_altitude=-90.0)
    if not rows:
        rows = build_fallback_sky_rows()
    fig = plot_sky_map(
        [r["ra_hours"] for r in rows],
        [r["dec_deg"] for r in rows],
        labels=[r.get("name", "?") for r in rows],
        magnitudes=[r.get("vmag", 3.0) for r in rows],
    )
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    import matplotlib.pyplot as plt

    plt.close(fig)
    return {"ok": True, "image_base64": base64.b64encode(buf.getvalue()).decode("ascii")}


def build_fallback_sky_rows() -> List[Dict[str, Any]]:
    return load_bright_stars()


def parse_jd_param(jd_str: Optional[str]) -> Optional[float]:
    if not jd_str:
        return None
    return float(jd_str)


def parse_iso_to_jd(iso: Optional[str]) -> Optional[float]:
    if not iso:
        return None
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return datetime_to_jd(dt)
