"""Combine multiple matplotlib figures into one PDF or HTML string."""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Sequence, Union

PathLike = Union[str, Path]


def save_figures_pdf(figures: Sequence[Any], output_path: PathLike) -> str:
    """
    Write each matplotlib ``Figure`` to a multi-page PDF using ``PdfPages``.
    Closes figures after saving.
    """
    import matplotlib.pyplot as plt  # pyright: ignore [reportMissingImports]
    from matplotlib.backends.backend_pdf import PdfPages  # pyright: ignore

    path = str(output_path)
    with PdfPages(path) as pdf:
        for fig in figures:
            pdf.savefig(fig)
            plt.close(fig)
    return path


def figures_to_html_img_tags(figures: Sequence[Any], *, fmt: str = "png") -> str:
    """
    Render figures to base64-embedded ``<img>`` tags (no external files).
    Closes figures after drawing.
    """
    import base64
    import io

    import matplotlib.pyplot as plt  # pyright: ignore [reportMissingImports]

    parts: List[str] = []
    for fig in figures:
        buf = io.BytesIO()
        fig.savefig(buf, format=fmt, bbox_inches="tight")
        plt.close(fig)
        b64 = base64.standard_b64encode(buf.getvalue()).decode("ascii")
        parts.append(f'<img src="data:image/{fmt};base64,{b64}" alt="figure" />')
    return "\n".join(parts)
