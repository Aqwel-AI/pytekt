"""
Visualize attention maps from a small transformer.

Builds a tiny model and dataset, runs one forward pass, and saves
attention heatmaps (single head and all heads) as PNG files. No training.
Run: python -m pytekt.former.examples.attention_demo
"""
import os
import numpy as np
import matplotlib.pyplot as plt

from pytekt.former.models import Transformer
from pytekt.former.datasets import TextDataset
from pytekt.former.visualization import plot_attention_map, plot_multi_head_attention


def main():
    # Minimal text and short sequence for quick demo
    text = "Hello world this is a short sequence for attention demo. " * 4
    seq_length = 32
    dataset = TextDataset(text, seq_length=seq_length, level="char")
    model = Transformer(
        vocab_size=dataset.vocab_size,
        embed_dim=64,
        num_heads=4,
        num_layers=2,
        max_seq_len=seq_length,
    )
    # Single batch to get attention weights
    ids = dataset.get_batch(1)
    inputs = ids[0]
    logits, attention_weights_list = model.forward(inputs)
    tokens = [dataset.tokenizer.reverse_vocab.get(i, "?") for i in inputs[0]]
    # Save single-head heatmap
    plot_attention_map(
        attention_weights_list[0],
        tokens=tokens,
        layer=0,
        head=0,
        title="Layer 0 Head 0",
    )
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(__file__), "attention_demo_head0.png"), dpi=120)
    plt.close()
    # Save all-heads grid
    plot_multi_head_attention(attention_weights_list[0], layer=0, tokens=tokens)
    plt.savefig(os.path.join(os.path.dirname(__file__), "attention_demo_all_heads.png"), dpi=120)
    plt.close()
    print("Saved attention_demo_head0.png and attention_demo_all_heads.png")


if __name__ == "__main__":
    main()
