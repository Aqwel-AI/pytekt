"""Text augmentation transforms for data enrichment."""

from __future__ import annotations

import random
from typing import List, Optional


def random_delete(text: str, p: float = 0.1, *, seed: Optional[int] = None) -> str:
    """Randomly delete words with probability *p*."""
    rng = random.Random(seed)
    words = text.split()
    if len(words) <= 1:
        return text
    kept = [w for w in words if rng.random() > p]
    return " ".join(kept) if kept else words[0]


def random_swap(text: str, n: int = 1, *, seed: Optional[int] = None) -> str:
    """Randomly swap *n* pairs of adjacent words."""
    rng = random.Random(seed)
    words = text.split()
    for _ in range(n):
        if len(words) < 2:
            break
        i = rng.randint(0, len(words) - 2)
        words[i], words[i + 1] = words[i + 1], words[i]
    return " ".join(words)


def random_insert(text: str, n: int = 1, *, seed: Optional[int] = None) -> str:
    """Duplicate *n* random words and insert them at random positions."""
    rng = random.Random(seed)
    words = text.split()
    for _ in range(n):
        if not words:
            break
        word = rng.choice(words)
        pos = rng.randint(0, len(words))
        words.insert(pos, word)
    return " ".join(words)


_SIMPLE_SYNONYMS = {
    "good": ["great", "fine", "excellent"],
    "bad": ["poor", "terrible", "awful"],
    "big": ["large", "huge", "enormous"],
    "small": ["tiny", "little", "mini"],
    "fast": ["quick", "rapid", "speedy"],
    "slow": ["sluggish", "gradual", "lazy"],
    "happy": ["glad", "joyful", "cheerful"],
    "sad": ["unhappy", "sorrowful", "gloomy"],
    "important": ["crucial", "vital", "essential"],
    "easy": ["simple", "effortless", "straightforward"],
}


def synonym_replace(
    text: str,
    n: int = 1,
    *,
    synonyms: Optional[dict] = None,
    seed: Optional[int] = None,
) -> str:
    """
    Replace up to *n* words with synonyms from a lookup table.

    Uses a small built-in synonym map by default; pass *synonyms* to override.
    """
    rng = random.Random(seed)
    table = synonyms or _SIMPLE_SYNONYMS
    words = text.split()
    indices = list(range(len(words)))
    rng.shuffle(indices)
    replaced = 0
    for i in indices:
        lower = words[i].lower()
        if lower in table:
            words[i] = rng.choice(table[lower])
            replaced += 1
            if replaced >= n:
                break
    return " ".join(words)


def augment_text(
    text: str,
    *,
    num_variants: int = 4,
    p_delete: float = 0.1,
    n_swap: int = 1,
    n_insert: int = 1,
    n_synonym: int = 1,
    seed: Optional[int] = None,
) -> List[str]:
    """
    Generate multiple augmented variants of *text* by applying random
    deletion, swapping, insertion, and synonym replacement.
    """
    rng = random.Random(seed)
    variants: List[str] = []
    ops = [
        lambda t, s: random_delete(t, p_delete, seed=s),
        lambda t, s: random_swap(t, n_swap, seed=s),
        lambda t, s: random_insert(t, n_insert, seed=s),
        lambda t, s: synonym_replace(t, n_synonym, seed=s),
    ]
    for _ in range(num_variants):
        s = rng.randint(0, 2**31)
        op = rng.choice(ops)
        variants.append(op(text, s))
    return variants
