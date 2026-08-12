"""
Aion transformer module — runnable examples.

Single entry point that demonstrates: tokenizer/dataset, forward pass,
short training, attention visualization, text generation, and training
metrics plot. Outputs are saved to aion/former/examples_results/.

Run from project root:
  python -m pytekt.former.example

Or from this directory:
  python example.py

For full scripts see:
  - aion.former.experiments.train_small_model  (training + config)
  - aion.former.examples.attention_demo       (attention heatmaps)
  - aion.former.examples.text_generation      (next-token generation)
"""

import os
import numpy as np

# -----------------------------------------------------------------------------
# 1. Imports from pytekt.former
# -----------------------------------------------------------------------------
from pytekt.former import (
    Transformer,
    Trainer,
    TextDataset,
    create_dataloader,
    plot_attention_map,
    plot_training_metrics,
)

# -----------------------------------------------------------------------------
# 2. Tokenizer and dataset
# -----------------------------------------------------------------------------
def example_tokenizer_and_dataset():
    """
    Build a small character-level dataset from text.

    Returns
    -------
    dataset : TextDataset
        Dataset with vocab and tokenizer.
    seq_length : int
        Context length used.
    """
    text = "The quick brown fox jumps over the lazy dog. " * 20
    seq_length = 32
    dataset = TextDataset(text, seq_length=seq_length, level="char")
    print("Vocabulary size:", dataset.vocab_size)
    print("Dataset length (number of windows):", len(dataset))
    inputs, targets = dataset.get_batch(4)
    print("Batch inputs shape:", inputs.shape, "targets shape:", targets.shape)
    sample_ids = inputs[0]
    decoded = dataset.tokenizer.decode(sample_ids.tolist())
    print("First sequence (decoded):", repr(decoded[:50]), "...")
    return dataset, seq_length


# -----------------------------------------------------------------------------
# 3. Model forward pass
# -----------------------------------------------------------------------------
def example_forward(dataset, seq_length):
    """
    Create a small transformer and run one forward pass.

    Parameters
    ----------
    dataset : TextDataset
        Dataset (for vocab_size).
    seq_length : int
        Sequence length for model.

    Returns
    -------
    model : Transformer
        The model.
    logits : Tensor
        Output logits.
    attention_weights_list : list of np.ndarray
        Attention weights per layer.
    """
    model = Transformer(
        vocab_size=dataset.vocab_size,
        embed_dim=64,
        num_heads=4,
        num_layers=2,
        max_seq_len=seq_length,
    )
    inputs, _ = dataset.get_batch(2)
    logits, attention_weights_list = model.forward(inputs)
    print("Logits shape:", logits._data.shape)
    print("Number of layers (attention weight tensors):", len(attention_weights_list))
    print("Attention weights shape (layer 0):", attention_weights_list[0].shape)
    return model, logits, attention_weights_list


# -----------------------------------------------------------------------------
# 4. Short training loop
# -----------------------------------------------------------------------------
def example_training():
    """
    Train for a few steps and show loss.

    Returns
    -------
    Trainer
        Trainer with history from one epoch.
    """
    text = "Hello world. " * 100
    dataset, get_batch = create_dataloader(
        text, seq_length=16, batch_size=8, level="char"
    )
    model = Transformer(
        vocab_size=dataset.vocab_size,
        embed_dim=32,
        num_heads=2,
        num_layers=1,
        max_seq_len=16,
    )
    trainer = Trainer(model, lr=0.01)
    print("Training for 1 epoch (5 steps)...")
    loss = trainer.train_epoch(get_batch, steps_per_epoch=5)
    print(f"  epoch loss = {loss:.4f}")
    print("Training history:", [h["loss"] for h in trainer.history])
    return trainer


# -----------------------------------------------------------------------------
# 5. Attention visualization (saves PNG if matplotlib available)
# -----------------------------------------------------------------------------
def _examples_results_dir():
    """Directory for example output files; created if missing."""
    import os
    d = os.path.join(os.path.dirname(__file__), "examples_results")
    os.makedirs(d, exist_ok=True)
    return d


def _try_import_matplotlib_pyplot():
    """Return matplotlib.pyplot if available, else None."""
    try:
        import importlib
        return importlib.import_module("matplotlib.pyplot")
    except ImportError:
        return None


def example_attention_visualization(model, dataset, attention_weights_list, inputs):
    """
    Plot attention for first layer, first head; save to examples_results.
    """
    plt = _try_import_matplotlib_pyplot()
    if plt is None:
        print("Skipping attention plot (matplotlib not available)")
        return

    tokens = [dataset.tokenizer.reverse_vocab.get(i, "?") for i in inputs[0]]
    plot_attention_map(
        attention_weights_list[0],
        tokens=tokens,
        layer=0,
        head=0,
        title="Layer 0 Head 0",
    )
    plt.tight_layout()
    path = os.path.join(_examples_results_dir(), "example_attention.png")
    plt.savefig(path, dpi=120)
    plt.close()
    print("Saved", path)


# -----------------------------------------------------------------------------
# 6. Text generation (greedy, few tokens)
# -----------------------------------------------------------------------------
def example_text_generation(dataset, model, seq_length, prompt="The ", num_tokens=20):
    """
    Generate a short sequence from a prompt (greedy decode).

    Parameters
    ----------
    dataset : TextDataset
        Dataset with tokenizer.
    model : Transformer
        The model.
    seq_length : int
        Context length.
    prompt : str, optional
        Initial text (default "The ").
    num_tokens : int, optional
        Number of new tokens to generate (default 20).

    Returns
    -------
    str
        prompt + generated text.
    """
    ids = dataset.tokenizer.encode(prompt)
    if len(ids) > seq_length:
        ids = ids[-seq_length:]
    generated = list(ids)
    for _ in range(num_tokens):
        context = np.array([generated[-seq_length:]], dtype=np.int64)
        logits, _ = model.forward(context)
        next_id = int(np.argmax(logits._data[0, -1]))
        generated.append(next_id)
    return dataset.tokenizer.decode(generated)


# -----------------------------------------------------------------------------
# 7. Training metrics plot (saves PNG if matplotlib available)
# -----------------------------------------------------------------------------
def example_plot_training_metrics(trainer):
    """
    Plot loss curve from trainer history; save to examples_results.
    """
    plt = _try_import_matplotlib_pyplot()
    if plt is None:
        print("Skipping training plot (matplotlib not available)")
        return

    plot_training_metrics(trainer.history, title="Example training loss")
    path = os.path.join(_examples_results_dir(), "example_training_metrics.png")
    plt.savefig(path, dpi=120)
    plt.close()
    print("Saved", path)


# -----------------------------------------------------------------------------
# Main: run all examples
# -----------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Aion transformer module — examples")
    print("=" * 60)

    print("\n--- 1. Tokenizer and dataset ---")
    dataset, seq_length = example_tokenizer_and_dataset()

    print("\n--- 2. Model forward pass ---")
    model, logits, attention_weights_list = example_forward(dataset, seq_length)

    print("\n--- 3. Short training loop ---")
    trainer = example_training()

    print("\n--- 4. Attention visualization ---")
    inputs, _ = dataset.get_batch(1)
    logits, attn_list = model.forward(inputs)
    example_attention_visualization(model, dataset, attn_list, inputs)

    print("\n--- 5. Text generation (greedy) ---")
    generated = example_text_generation(
        dataset, model, seq_length, prompt="The ", num_tokens=30
    )
    print("Prompt: 'The '")
    print("Generated:", repr(generated))

    print("\n--- 6. Training metrics plot ---")
    example_plot_training_metrics(trainer)

    print("\n" + "=" * 60)
    print("Done. For full scripts run:")
    print("  python -m pytekt.former.experiments.train_small_model")
    print("  python -m pytekt.former.examples.attention_demo")
    print("  python -m pytekt.former.examples.text_generation")
    print("=" * 60)


if __name__ == "__main__":
    main()
