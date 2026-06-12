"""Pipeline steps for cosmos workflows."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..pipeline.core import Step


class CosmosCatalogStep(Step):
    """Load a builtin catalog into pipeline data."""

    name = "cosmos_catalog"

    def __init__(self, catalog: str = "bright_stars", *, as_key: str = "catalog") -> None:
        self.catalog = catalog
        self.as_key = as_key

    def run(self, data: Any, ctx: Dict[str, Any]) -> Any:
        from . import catalogs

        loaders = {
            "bright_stars": catalogs.load_bright_stars,
            "messier": catalogs.load_messier,
            "planets": catalogs.load_planets,
        }
        loader = loaders.get(self.catalog, catalogs.load_bright_stars)
        rows = loader()
        if isinstance(data, dict):
            out = dict(data)
            out[self.as_key] = rows
            return out
        ctx[self.as_key] = rows
        return data


class CosmosPlotStep(Step):
    """Plot sky map from catalog in pipeline data (requires [viz])."""

    name = "cosmos_plot"

    def __init__(self, *, data_key: str = "catalog", save_path: Optional[str] = None) -> None:
        self.data_key = data_key
        self.save_path = save_path

    def run(self, data: Any, ctx: Dict[str, Any]) -> Any:
        from .viz import plot_sky_map

        rows: List[Dict[str, Any]]
        if isinstance(data, dict) and self.data_key in data:
            rows = data[self.data_key]
        else:
            rows = ctx.get(self.data_key, [])
        plot_sky_map(
            [r["ra_hours"] for r in rows],
            [r["dec_deg"] for r in rows],
            labels=[r.get("name", "") for r in rows],
            magnitudes=[r.get("vmag") for r in rows if "vmag" in r],
            save_path=self.save_path,
        )
        return data
