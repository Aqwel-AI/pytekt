"""Vocabulary: bidirectional token-to-id mapping with special tokens."""

from __future__ import annotations

import json
from typing import Dict, Iterable, List, Optional


_DEFAULT_SPECIALS = ["<pad>", "<unk>", "<bos>", "<eos>"]


class Vocabulary:
    """
    Token-to-id and id-to-token mapping.

    Parameters
    ----------
    special_tokens : list[str]
        Tokens reserved at the start of the id range.
    """

    def __init__(self, special_tokens: Optional[List[str]] = None) -> None:
        self._tok2id: Dict[str, int] = {}
        self._id2tok: Dict[int, str] = {}
        for tok in (special_tokens or _DEFAULT_SPECIALS):
            self._add(tok)

    @property
    def pad_id(self) -> int:
        return self._tok2id.get("<pad>", 0)

    @property
    def unk_id(self) -> int:
        return self._tok2id.get("<unk>", 1)

    @property
    def bos_id(self) -> int:
        return self._tok2id.get("<bos>", 2)

    @property
    def eos_id(self) -> int:
        return self._tok2id.get("<eos>", 3)

    def _add(self, token: str) -> int:
        if token not in self._tok2id:
            idx = len(self._tok2id)
            self._tok2id[token] = idx
            self._id2tok[idx] = token
        return self._tok2id[token]

    def add_tokens(self, tokens: Iterable[str]) -> None:
        for tok in tokens:
            self._add(tok)

    def token_to_id(self, token: str) -> int:
        return self._tok2id.get(token, self.unk_id)

    def id_to_token(self, idx: int) -> str:
        return self._id2tok.get(idx, "<unk>")

    def encode(self, tokens: List[str]) -> List[int]:
        return [self.token_to_id(t) for t in tokens]

    def decode(self, ids: List[int]) -> List[str]:
        return [self.id_to_token(i) for i in ids]

    def __len__(self) -> int:
        return len(self._tok2id)

    def __contains__(self, token: str) -> bool:
        return token in self._tok2id

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"tok2id": self._tok2id}, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "Vocabulary":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        vocab = cls(special_tokens=[])
        vocab._tok2id = {k: int(v) for k, v in data["tok2id"].items()}
        vocab._id2tok = {v: k for k, v in vocab._tok2id.items()}
        return vocab
