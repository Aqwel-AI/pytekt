"""
Visualization tools for attention, metrics, and weight spectrum.

Attention heatmaps (single head or all heads), training loss/metrics over
epochs, and eigenvalue/singular-value distribution of weight matrices.
Requires matplotlib.
"""

from .attention_map import plot_attention_map, plot_multi_head_attention
from .training_metrics import plot_training_metrics
from .weight_spectrum import plot_weight_spectrum

__all__ = ["plot_attention_map", "plot_multi_head_attention", "plot_training_metrics", "plot_weight_spectrum"]
