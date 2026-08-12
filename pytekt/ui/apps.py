"""Optional Gradio / Streamlit app launchers (``pip install 'pytekt[ui]'``)."""

from __future__ import annotations

from typing import Any, Optional


def gradio_available() -> bool:
    try:
        import gradio  # noqa: F401
        return True
    except ImportError:
        return False


def streamlit_available() -> bool:
    try:
        import streamlit  # noqa: F401
        return True
    except ImportError:
        return False


def launch_gradio_playground(
    *,
    share: bool = False,
    server_port: int = 7860,
) -> None:
    """Launch a minimal Gradio UI to run Python snippets (like the Hub playground).

    Requires: ``pip install 'pytekt[ui]'``
    """
    if not gradio_available():
        raise ImportError(
            "Gradio is not installed. Install with: pip install 'pytekt[ui]'"
        )
    import gradio as gr

    from ..hub.server import _run_snippet

    def run_code(code: str) -> str:
        if not code.strip():
            return "Enter code above."
        result = _run_snippet(code)
        parts = []
        if result.get("stdout"):
            parts.append(result["stdout"])
        if result.get("result"):
            parts.append("=> " + str(result["result"]))
        if result.get("error"):
            parts.append(result["error"])
        return "\n".join(parts) or "(no output)"

    demo = gr.Interface(
        fn=run_code,
        inputs=gr.Code(label="Python", language="python", lines=12),
        outputs=gr.Textbox(label="Output", lines=14),
        title="Aion Gradio Playground",
        description="Run Aion snippets interactively.",
        examples=[
            ["import pytekt\nprint(pytekt.__version__)"],
            ["from pytekt.datasets import load_iris\nprint(load_iris())"],
        ],
    )
    demo.launch(share=share, server_port=server_port)


def launch_streamlit_dataset_explorer(
    *,
    server_port: int = 8501,
) -> None:
    """Launch a Streamlit app to browse built-in :mod:`aion.datasets`.

    Requires: ``pip install 'pytekt[ui]'``
    """
    if not streamlit_available():
        raise ImportError(
            "Streamlit is not installed. Install with: pip install 'pytekt[ui]'"
        )
    import subprocess
    import sys
    from pathlib import Path

    script = Path(__file__).with_name("_streamlit_dataset_app.py")
    script.write_text(_STREAMLIT_APP_TEMPLATE, encoding="utf-8")

    env = {**dict(__import__("os").environ), "STREAMLIT_SERVER_PORT": str(server_port)}
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(script)],
        env=env,
        check=False,
    )


_STREAMLIT_APP_TEMPLATE = '''"""Streamlit dataset explorer."""
import streamlit as st
from pytekt.datasets import fetch, list_datasets

st.set_page_config(page_title="Aion datasets", layout="wide")
st.title("Aion dataset explorer")
names = [d["name"] for d in list_datasets()]
choice = st.sidebar.selectbox("Dataset", names, index=0)
ds = fetch(choice)
st.metric("Samples", ds.n_samples)
st.metric("Features", ds.n_features)
st.caption(ds.description or "")
if hasattr(ds.data, "dtype") and ds.data.dtype.kind in "fiu":
    try:
        import pandas as pd
        cols = ds.feature_names or [f"x{i}" for i in range(ds.n_features)]
        df = pd.DataFrame(ds.data, columns=cols)
        df.insert(0, "target", ds.target)
        st.dataframe(df.head(20))
    except ImportError:
        st.text(ds.head(10))
else:
    st.write("Sample rows:")
    for i in range(min(10, ds.n_samples)):
        st.write(str(ds.target[i]), str(ds.data[i]))
'''
