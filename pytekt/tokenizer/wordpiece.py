"""WordPiece tokenizer (BERT-style)."""

from __future__ import annotations

import json
from collections import Counter
from typing import Dict, List, Optional

from .vocab import Vocabulary


class WordPieceTokenizer:
    """
    WordPiece tokenizer using greedy longest-match-first.

    Continuation sub-words are prefixed with ``##``.

    Parameters
    ----------
    vocab_size : int
        Target vocabulary size.
    unk_token : str
        Token for out-of-vocabulary characters.
    """

    def __init__(self, vocab_size: int = 8000, unk_token: str = "<unk>") -> None:
        self.vocab_size = vocab_size
        self.unk_token = unk_token
        self.vocab = Vocabulary()
        self._word_vocab: set[str] = set()
        self._trained = False

    def train(self, texts: List[str]) -> None:
        """Build vocabulary from corpus using WordPiece scoring."""
        word_freqs: Counter[str] = Counter()
        for text in texts:
            for word in text.strip().split():
                word_freqs[word] += 1

        chars: set[str] = set()
        for word in word_freqs:
            for i, ch in enumerate(word):
                token = ch if i == 0 else f"##{ch}"
                chars.add(token)

        for ch in sorted(chars):
            self.vocab._add(ch)

        while len(self.vocab) < self.vocab_size:
            scores = self._score_pairs(word_freqs)
            if not scores:
                break
            best = max(scores, key=scores.get)  # type: ignore[arg-type]
            self.vocab._add(best)
            self._word_vocab.add(best)

        self._trained = True

    def encode(self, text: str) -> List[int]:
        """Tokenize and return ids."""
        return self.vocab.encode(self.tokenize(text))

    def decode(self, ids: List[int]) -> str:
        """Convert ids back to text."""
        tokens = self.vocab.decode(ids)
        text = ""
        for tok in tokens:
            if tok.startswith("##"):
                text += tok[2:]
            else:
                if text:
                    text += " "
                text += tok
        return text

    def tokenize(self, text: str) -> List[str]:
        """Return sub-word tokens as strings."""
        tokens: List[str] = []
        for word in text.strip().split():
            sub = self._tokenize_word(word)
            tokens.extend(sub)
        return tokens

    def _tokenize_word(self, word: str) -> List[str]:
        tokens: List[str] = []
        start = 0
        while start < len(word):
            end = len(word)
            found = None
            while start < end:
                substr = word[start:end]
                if start > 0:
                    substr = f"##{substr}"
                if substr in self.vocab:
                    found = substr
                    break
                end -= 1
            if found is None:
                tokens.append(self.unk_token)
                start += 1
            else:
                tokens.append(found)
                start = end
        return tokens

    def _score_pairs(self, word_freqs: Counter[str]) -> Dict[str, float]:
        pair_freq: Counter[str] = Counter()
        piece_freq: Counter[str] = Counter()
        for word, freq in word_freqs.items():
            pieces = self._tokenize_word(word)
            for i, p in enumerate(pieces):
                piece_freq[p] += freq
                if i < len(pieces) - 1:
                    merged = pieces[i].replace("##", "") + pieces[i + 1].replace("##", "")
                    if i > 0:
                        merged = f"##{merged}"
                    pair_freq[merged] += freq

        scores: Dict[str, float] = {}
        for pair, freq in pair_freq.items():
            clean = pair.replace("##", "")
            if len(clean) < 2:
                continue
            p1 = clean[0]
            p2 = f"##{clean[1:]}"
            denom = piece_freq.get(p1, 1) * piece_freq.get(p2, 1)
            scores[pair] = freq / denom if denom else 0
        return scores

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"vocab_size": self.vocab_size, "unk": self.unk_token}, f, indent=2)
        self.vocab.save(path.replace(".json", "_vocab.json"))

    @classmethod
    def load(cls, path: str) -> "WordPieceTokenizer":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        tok = cls(vocab_size=data["vocab_size"], unk_token=data.get("unk", "<unk>"))
        tok.vocab = Vocabulary.load(path.replace(".json", "_vocab.json"))
        tok._trained = True
        return tok
