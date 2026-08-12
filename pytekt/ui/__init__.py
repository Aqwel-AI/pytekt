"""
User interface layer for PyTekt — **React-style frontend in Python**.

Build declarative UIs with components, props, and ``html.*`` tags (like JSX),
then render to static HTML or serve locally. No Node.js or React install required.

Quick start (React-like)
------------------------
>>> from pytekt.ui import Component, html, render_app, AppShell, MetricGrid
>>> class Dashboard(Component):
...     def render(self):
...         return AppShell(
...             title="My ML App",
...             subtitle="Training run #42",
...             children=MetricGrid(metrics={"accuracy": 0.94, "loss": 0.08}),
...         )
>>> render_app(Dashboard(), output="dashboard.html", open_browser=True)

Legacy helpers (reports & launchers)
------------------------------------
>>> from pytekt.ui import PageBuilder, launch_hub
>>> launch_hub()
"""

# React-style core
from .vdom import VNode, h, Fragment, render_vnode
from .html_tags import html
from .component import Component, function_component, render_component
from .render import render, render_app, serve_app
from .builtins import (
    AppShell,
    Button,
    Card,
    DataTable,
    Metric,
    MetricGrid,
    Row,
    Stack,
    Text,
)
from .theme import REACT_THEME_CSS

# HTML reports (imperative builder)
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
    # React-style API
    "VNode",
    "h",
    "Fragment",
    "render_vnode",
    "html",
    "Component",
    "function_component",
    "render_component",
    "render",
    "render_app",
    "serve_app",
    "AppShell",
    "Button",
    "Card",
    "DataTable",
    "Metric",
    "MetricGrid",
    "Row",
    "Stack",
    "Text",
    "REACT_THEME_CSS",
    # Legacy / launchers
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
