"""
Simple character- or word-level tokenizer for text.

Builds a vocabulary from text; encode maps text to integer ids,
decode maps ids back to text. Special tokens <pad> and <unk> are included.
"""

from typing import List, Dict, Optional


# -----------------------------------------------------------------------------
# Tokenizer
# -----------------------------------------------------------------------------

class SimpleTokenizer:
    """
    Maps text to integer ids; character-level or word-level.

    Parameters
    ----------
    level : str, optional
        "char" for character-level, "word" for word-level (whitespace split)
        (default "char").
    """

    def __init__(self, level: str = "char"):
        self.level = level
        self.vocab: Dict[str, int] = {}
        self.reverse_vocab: Dict[int, str] = {}
        self.special = {"<pad>": 0, "<unk>": 1}
        self._built = False

    def fit(self, text: str) -> None:
        """
        Build vocabulary from text. Ids are assigned in sorted order.

        Parameters
        ----------
        text : str
            Corpus to build vocab from.
        """
        if self.level == "char":
            chars = sorted(set(text))
        else:
            words = text.split()
            chars = sorted(set(words))
        self.vocab = {**self.special}
        for i, c in enumerate(chars):
            if c not in self.vocab:
                self.vocab[c] = len(self.vocab)
        self.reverse_vocab = {v: k for k, v in self.vocab.items()}
        self._built = True

    def encode(self, text: str) -> List[int]:
        """
        Encode text to list of integer ids. Unknown tokens map to <unk>.

        Parameters
        ----------
        text : str
            Input text.

        Returns
        -------
        list of int
            Token ids.
        """
        if not self._built:
            self.fit(text)
        if self.level == "char":
            return [self.vocab.get(c, self.vocab["<unk>"]) for c in text]
        return [self.vocab.get(w, self.vocab["<unk>"]) for w in text.split()]

    def decode(self, ids: List[int]) -> str:
        """
        Decode list of ids to text. Unknown ids become "<unk>".

        Parameters
        ----------
        ids : list of int
            Token ids.

        Returns
        -------
        str
            Reconstructed text.
        """
        if self.level == "char":
            return "".join(self.reverse_vocab.get(i, "<unk>") for i in ids)
        return " ".join(self.reverse_vocab.get(i, "<unk>") for i in ids)

    @property
    def vocab_size(self) -> int:
        """Size of the vocabulary."""
        return len(self.vocab)

    @property
    def pad_id(self) -> int:
        """Id of the <pad> token."""
        return self.vocab["<pad>"]
