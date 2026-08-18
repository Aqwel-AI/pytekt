"""
Train a small transformer on text (next-token prediction).

Reads pytekt/former/experiments/config.yaml (or uses built-in defaults),
builds dataset and model, runs training, and saves loss curve and optional
weight spectrum plot. Run: python -m pytekt.former.experiments.train_small_model
"""
import os
import numpy as np
import yaml

from pytekt.former.models import Transformer
from pytekt.former.training import Trainer, save_transformer_weights
from pytekt.former.datasets import TextDataset, create_dataloader
from pytekt.former.visualization import plot_training_metrics, plot_weight_spectrum


# Default small corpus when no data file is provided
SAMPLE_TEXT = """
To be or not to be that is the question
Whether tis nobler in the mind to suffer
The slings and arrows of outrageous fortune
Or to take arms against a sea of troubles
And by opposing end them. To die to sleep
No more and by a sleep to say we end
The heartache and the thousand natural shocks
That flesh is heir to. Tis a consummation
Devoutly to be wished. To die to sleep.
""" * 80


def load_config():
    """Load config from config.yaml in this directory, or return default dict."""
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if os.path.isfile(config_path):
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {
        "model": {
            "embedding_dim": 128,
            "num_heads": 4,
            "num_layers": 2,
            "max_seq_len": 64,
            "hidden_dim": 512,
        },
        "training": {"batch_size": 32, "lr": 1e-3, "epochs": 10, "steps_per_epoch": 50},
        "data": {"seq_length": 64, "level": "char"},
    }


def main():
    config = load_config()
    data_cfg = config.get("data", {})
    model_cfg = config.get("model", {})
    train_cfg = config.get("training", {})

    seq_length = data_cfg.get("seq_length", 64)
    level = data_cfg.get("level", "char")
    data_file = data_cfg.get("data_file")

    if data_file and os.path.isfile(data_file):
        with open(data_file) as f:
            text = f.read()
    else:
        text = SAMPLE_TEXT

    dataset, get_batch = create_dataloader(
        text,
        seq_length=seq_length,
        batch_size=train_cfg.get("batch_size", 32),
        level=level,
    )
    vocab_size = dataset.vocab_size
    model_cfg["vocab_size"] = vocab_size
    model_cfg.setdefault("max_seq_len", seq_length)

    model = Transformer(
        vocab_size=vocab_size,
        embed_dim=model_cfg.get("embedding_dim", 128),
        num_heads=model_cfg.get("num_heads", 4),
        num_layers=model_cfg.get("num_layers", 2),
        max_seq_len=model_cfg.get("max_seq_len", 64),
        hidden_dim=model_cfg.get("hidden_dim"),
    )

    trainer = Trainer(
        model,
        lr=float(train_cfg.get("lr", 1e-3)),
    )

    epochs = train_cfg.get("epochs", 10)
    steps_per_epoch = train_cfg.get("steps_per_epoch", 50)

    print("Training small transformer (next-token prediction)...")
    for epoch in range(epochs):
        loss = trainer.train_epoch(get_batch, steps_per_epoch)
        print(f"Epoch {epoch + 1}/{epochs}  loss = {loss:.4f}")

    try:
        plot_training_metrics(trainer.history, title="PyTekt transformer training loss")
        import matplotlib.pyplot as plt
        plt.savefig(os.path.join(os.path.dirname(__file__), "training_metrics.png"), dpi=120)
        plt.close()
        w = model.blocks[0].attn.W_q
        if hasattr(w, "_data") and w._data.ndim == 2:
            plot_weight_spectrum(w, title="Layer 0 Q weight spectrum")
            plt.savefig(os.path.join(os.path.dirname(__file__), "weight_spectrum.png"), dpi=120)
            plt.close()
            print("Saved training_metrics.png and weight_spectrum.png")
        else:
            print("Saved training_metrics.png")
    except Exception as e:
        print("Could not save plots:", e)

    weights_path = os.path.join(os.path.dirname(__file__), "weights.npz")
    try:
        save_transformer_weights(model, weights_path)
        print(f"Saved weights to {weights_path}")
    except Exception as e:
        print("Could not save weights:", e)

    print("Done. Use pytekt.former.examples.text_generation with the same tokenizer/dataset to generate text.")


if __name__ == "__main__":
    main()
