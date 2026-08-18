"""Tokenizer + sliding-window dataloader demo."""
from __future__ import annotations

from pytekt.former.datasets import SimpleTokenizer, create_dataloader


def main() -> None:
    text = "hello world " * 20
    tok = SimpleTokenizer(level="char")
    tok.fit(text)
    assert tok.vocab_size >= 2
    ids = tok.encode("hello")
    assert tok.decode(ids) == "hello"

    dataset, get_batch = create_dataloader(text, seq_length=8, batch_size=4, level="char")
    x, y = get_batch()
    assert x.shape == (4, 8) and y.shape == (4, 8)
    print("demo_tokenizer ok — vocab_size =", dataset.vocab_size)


if __name__ == "__main__":
    main()
