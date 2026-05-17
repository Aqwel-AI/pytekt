"""
User interface tools for Aion — dashboards, HTML reports, and app launchers.

Provides a single import surface for browser UIs and static HTML dashboards
without requiring a separate front-end stack. Core features use the stdlib;
optional Gradio/Streamlit helpers need ``pip install 'aqwel-aion[ui]'``.

Quick start
-----------
>>> from aion.ui import launch_hub, PageBuilder
>>> launch_hub()  # same as ``aion start`` — Aion Hub in the browser
>>> page = PageBuilder("My experiment")
>>> page.add_metrics({"accuracy": 0.94, "loss": 0.12})
>>> page.save("report.html")
"""

from .html import PageBuilder, escape_html, table_html, metrics_row_html
from .dashboard import (
    build_experiment_dashboard,
    build_dataset_report,
    open_html_file,
)
from .launchers import (
    launch_hub,
    launch_monitor,
    open_in_browser,
    list_ui_interfaces,
)
from .apps import (
    gradio_available,
    streamlit_available,
    launch_gradio_playground,
    launch_streamlit_dataset_explorer,
)

__all__ = [
    "PageBuilder",
    "escape_html",
    "table_html",
    "metrics_row_html",
    "build_experiment_dashboard",
    "build_dataset_report",
    "open_html_file",
    "launch_hub",
    "launch_monitor",
    "open_in_browser",
    "list_ui_interfaces",
    "gradio_available",
    "streamlit_available",
    "launch_gradio_playground",
    "launch_streamlit_dataset_explorer",
]
