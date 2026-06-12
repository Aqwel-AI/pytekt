"""Stdlib HTTP server for the Aion Cosmos dashboard."""

from __future__ import annotations

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Any
from urllib.parse import parse_qs, urlparse

from . import web_api

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def _qs_float(qs: dict, key: str, default: float) -> float:
    raw = (qs.get(key) or [None])[0]
    return float(raw) if raw is not None else default


def _qs_str(qs: dict, key: str, default: str = "") -> str:
    return (qs.get(key) or [default])[0]


class CosmosHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        try:
            if path == "/api/info":
                self._json(web_api.library_info())
            elif path == "/api/observer":
                jd = web_api.parse_jd_param((qs.get("jd") or [None])[0])
                lat_raw = (qs.get("lat") or qs.get("latitude") or [None])[0]
                lon_raw = (qs.get("lon") or qs.get("longitude") or [None])[0]
                self._json(
                    web_api.observer_payload(
                        latitude=float(lat_raw) if lat_raw is not None else None,
                        longitude=float(lon_raw) if lon_raw is not None else None,
                        jd=jd,
                    )
                )
            elif path == "/api/moon":
                jd = web_api.parse_jd_param((qs.get("jd") or [None])[0])
                self._json(web_api.moon_payload(jd))
            elif path == "/api/sky":
                obs = web_api.get_observer_config()
                lat = _qs_float(qs, "lat", _qs_float(qs, "latitude", obs["latitude"]))
                lon = _qs_float(qs, "lon", _qs_float(qs, "longitude", obs["longitude"]))
                jd = web_api.parse_jd_param((qs.get("jd") or [None])[0])
                catalog = _qs_str(qs, "catalog", "all")
                min_alt = _qs_float(qs, "min_alt", _qs_float(qs, "min_altitude", 10.0))
                self._json(
                    web_api.sky_payload(
                        latitude=lat,
                        longitude=lon,
                        jd=jd,
                        catalog=catalog,
                        min_altitude=min_alt,
                    )
                )
            elif path == "/api/coords":
                obs = web_api.get_observer_config()
                lat = _qs_float(qs, "lat", _qs_float(qs, "latitude", obs["latitude"]))
                lon = _qs_float(qs, "lon", _qs_float(qs, "longitude", obs["longitude"]))
                jd = web_api.parse_jd_param((qs.get("jd") or [None])[0])
                self._json(
                    web_api.coords_payload(
                        mode=_qs_str(qs, "mode", "equatorial_to_horizontal"),
                        latitude=lat,
                        longitude=lon,
                        jd=jd,
                        ra=_qs_str(qs, "ra"),
                        dec=_qs_str(qs, "dec"),
                        alt=_qs_float(qs, "alt", 0.0) if qs.get("alt") else None,
                        az=_qs_float(qs, "az", 0.0) if qs.get("az") else None,
                        ra1=_qs_str(qs, "ra1"),
                        dec1=_qs_str(qs, "dec1"),
                        ra2=_qs_str(qs, "ra2"),
                        dec2=_qs_str(qs, "dec2"),
                    )
                )
            elif path == "/api/galactic":
                self._json(web_api.galactic_payload(_qs_str(qs, "ra"), _qs_str(qs, "dec")))
            elif path == "/api/cosmology":
                z = _qs_float(qs, "z", 0.1)
                h0 = _qs_float(qs, "H0", _qs_float(qs, "h0", 70.0))
                om0 = _qs_float(qs, "Om0", _qs_float(qs, "om0", 0.3))
                if (qs.get("curve") or ["0"])[0] in ("1", "true", "yes"):
                    self._json(web_api.cosmology_curve(z_max=z, h0=h0, om0=om0))
                else:
                    self._json(web_api.cosmology_payload(z, h0=h0, om0=om0))
            elif path == "/api/catalog/stars":
                self._json({"objects": web_api.catalog_stars()})
            elif path == "/api/catalog/messier":
                self._json({"objects": web_api.catalog_messier()})
            elif path == "/api/catalog/planets":
                jd = web_api.parse_jd_param((qs.get("jd") or [None])[0])
                self._json({"objects": web_api.catalog_planets(jd)})
            elif path == "/api/rise-set":
                obs = web_api.get_observer_config()
                lat = _qs_float(qs, "lat", _qs_float(qs, "latitude", obs["latitude"]))
                lon = _qs_float(qs, "lon", _qs_float(qs, "longitude", obs["longitude"]))
                jd = web_api.parse_jd_param((qs.get("jd") or [None])[0])
                self._json(
                    web_api.rise_set_payload(
                        ra=_qs_str(qs, "ra", "0h"),
                        dec=_qs_str(qs, "dec", "0d"),
                        latitude=lat,
                        longitude=lon,
                        jd=jd,
                    )
                )
            elif path == "/api/observations":
                limit = int((qs.get("limit") or ["50"])[0])
                self._json(web_api.observations_payload(limit=limit))
            elif path == "/api/plot/sky":
                obs = web_api.get_observer_config()
                lat = _qs_float(qs, "lat", obs["latitude"])
                lon = _qs_float(qs, "lon", obs["longitude"])
                catalog = _qs_str(qs, "catalog", "all")
                self._json(
                    web_api.plot_sky_png_base64(
                        catalog=catalog,
                        latitude=lat,
                        longitude=lon,
                    )
                )
            elif path.startswith("/api/"):
                self.send_error(404)
            elif path in ("/", "", "/cosmos", "/cosmos/"):
                self.path = "/index.html"
                super().do_GET()
            else:
                disk = os.path.join(STATIC_DIR, path.lstrip("/"))
                if os.path.isfile(disk):
                    super().do_GET()
                else:
                    self.path = "/index.html"
                    super().do_GET()
        except Exception as e:
            self._json({"error": str(e)}, status=400)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            data = {}

        try:
            if parsed.path == "/api/observer":
                lat = float(data.get("latitude", data.get("lat", 40.18)))
                lon = float(data.get("longitude", data.get("lon", 44.51)))
                saved = web_api.save_observer_config(lat, lon)
                self._json({"ok": True, **web_api.observer_payload(latitude=lat, longitude=lon), **saved})
            elif parsed.path == "/api/observations":
                obs = web_api.get_observer_config()
                lat = float(data.get("latitude", obs["latitude"]))
                lon = float(data.get("longitude", obs["longitude"]))
                result = web_api.log_observation_payload(
                    latitude=lat,
                    longitude=lon,
                    catalog=str(data.get("catalog", "all")),
                    notes=str(data.get("notes", "")),
                    min_altitude=float(data.get("min_altitude", 10.0)),
                )
                self._json({"ok": True, **result})
            else:
                self.send_error(404)
        except Exception as e:
            self._json({"error": str(e)}, status=400)

    def _json(self, data: Any, status: int = 200) -> None:
        payload = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        pass


def run_server(host: str = "127.0.0.1", port: int = 3857) -> None:
    import errno

    if not os.path.isdir(STATIC_DIR):
        print(
            f"Cosmos static assets missing at {STATIC_DIR}. "
            "Run: cd aion/cosmos/web && npm install && npm run build",
            file=sys.stderr,
        )

    try:
        server = HTTPServer((host, port), CosmosHandler)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            print(f"Port {port} in use — cosmos dashboard may already be running: http://{host}:{port}/")
            return
        raise

    print(f"Aion Cosmos Dashboard: http://{host}:{port}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
