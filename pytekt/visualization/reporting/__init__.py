"""
Report & Publication Export Utilities
=====================================

Provides publication-grade report compilation and figure export tools:
- Exporting figure bundles into multi-page PDF documents
- Base64 HTML img tag conversion for interactive dashboards
"""

from __future__ import annotations

from .report import figures_to_html_img_tags, save_figures_pdf

__all__ = [
    "figures_to_html_img_tags",
    "save_figures_pdf",
]
