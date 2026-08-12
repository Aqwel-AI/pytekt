"""Byte-Pair Encoding tokenizer (trainable)."""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Dict, List, Optional, Tuple

from .vocab import Vocabulary


class BPETokenizer:
    """
    Byte-Pair Encoding tokenizer.

    Train on a corpus to learn sub-word merges, then encode / decode text.
    Compatible with :class:`aion.tokenizer.Vocabulary` for id mapping.

    Parameters
    ----------
    vocab_size : int
        Target vocabulary size (including special tokens).
    """

    def __init__(self, vocab_size: int = 8000) -> None:
        self.vocab_size = vocab_size
        self.merges: List[Tuple[str, str]] = []
        self.vocab = Vocabulary()
        self._trained = False

    def train(self, texts: List[str]) -> None:
        """Learn BPE merges from a list of text strings."""
        word_freqs: Counter[str] = Counter()
        for text in texts:
            for word in self._pre_tokenize(text):
                word_freqs[" ".join(word) + " </w>"] += 1

        for ch in set("".join("".join(t) for t in word_freqs)):
            self.vocab._add(ch)
        self.vocab._add("</w>")

        while len(self.vocab) < self.vocab_size:
            pairs = self._get_pair_counts(word_freqs)
            if not pairs:
                break
            best = max(pairs, key=pairs.get)  # type: ignore[arg-type]
            new_token = best[0] + best[1]
            self.merges.append(best)
            self.vocab._add(new_token)
            word_freqs = self._merge_pair(word_freqs, best)

        self._trained = True

    def encode(self, text: str) -> List[int]:
        """Tokenize *text* and return token ids."""
        tokens: List[str] = []
        for word in self._pre_tokenize(text):
            word_str = " ".join(word) + " </w>"
            for a, b in self.merges:
                word_str = word_str.replace(f"{a} {b}", a + b)
            tokens.extend(word_str.split())
        return self.vocab.encode(tokens)

    def decode(self, ids: List[int]) -> str:
        """Convert token ids back to text."""
        tokens = self.vocab.decode(ids)
        text = "".join(tokens)
        text = text.replace("</w>", " ")
        return text.strip()

    def tokenize(self, text: str) -> List[str]:
        """Return sub-word tokens as strings (no id conversion)."""
        tokens: List[str] = []
        for word in self._pre_tokenize(text):
            word_str = " ".join(word) + " </w>"
            for a, b in self.merges:
                word_str = word_str.replace(f"{a} {b}", a + b)
            tokens.extend(word_str.split())
        return tokens

    def save(self, path: str) -> None:
        """Save merges and vocabulary to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"merges": self.merges, "vocab_size": self.vocab_size},
                f,
                ensure_ascii=False,
                indent=2,
            )
        self.vocab.save(path.replace(".json", "_vocab.json"))

    @classmethod
    def load(cls, path: str) -> "BPETokenizer":
        """Load a trained tokenizer from disk."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        tok = cls(vocab_size=data["vocab_size"])
        tok.merges = [tuple(m) for m in data["merges"]]  # type: ignore[misc]
        tok.vocab = Vocabulary.load(path.replace(".json", "_vocab.json"))
        tok._trained = True
        return tok

    @staticmethod
    def _pre_tokenize(text: str) -> List[List[str]]:
        return [list(w) for w in text.strip().split()]

    @staticmethod
    def _get_pair_counts(word_freqs: Counter[str]) -> Counter[Tuple[str, str]]:
        pairs: Counter[Tuple[str, str]] = Counter()
        for word, freq in word_freqs.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i + 1])] += freq
        return pairs

    @staticmethod
    def _merge_pair(
        word_freqs: Counter[str], pair: Tuple[str, str]
    ) -> Counter[str]:
        new_freqs: Counter[str] = Counter()
        bigram = f"{pair[0]} {pair[1]}"
        replacement = pair[0] + pair[1]
        for word, freq in word_freqs.items():
            new_word = word.replace(bigram, replacement)
            new_freqs[new_word] = freq
        return new_freqs
