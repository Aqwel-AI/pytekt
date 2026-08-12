"""Save a synthetic attention heatmap (no trained model)."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import numpy as np

from pytekt.former.visualization import plot_attention_map


def main() -> None:
    # (batch, heads, seq, seq)
    w = np.random.rand(1, 1, 6, 6).astype(np.float64)
    w /= w.sum(axis=-1, keepdims=True)
    ax = plot_attention_map(w, tokens=[f"t{i}" for i in range(6)], title="synthetic")
    out = "attention_demo.png"
    ax.figure.savefig(out, dpi=120, bbox_inches="tight")
    print("demo_attention_plot ok — wrote", out)


if __name__ == "__main__":
    main()
