"""Base types and helpers shared across all dataset loaders."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np


@dataclass
class Dataset:
    """Container returned by every ``load_*`` / ``make_*`` function.

    Attributes
    ----------
    data : np.ndarray
        Feature matrix of shape ``(n_samples, n_features)``.
    target : np.ndarray
        Target vector of shape ``(n_samples,)``.
    feature_names : list[str]
        Human-readable column names for *data*.
    target_names : list[str]
        Class / output labels (classification) or a single description
        (regression).
    description : str
        Free-form dataset description.
    name : str
        Short identifier, e.g. ``"iris"`` or ``"housing"``.
    metadata : dict
        Arbitrary extra information.
    """

    data: np.ndarray
    target: np.ndarray
    feature_names: List[str] = field(default_factory=list)
    target_names: List[str] = field(default_factory=list)
    description: str = ""
    name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def shape(self) -> Tuple[int, ...]:
        return self.data.shape

    @property
    def n_samples(self) -> int:
        return self.data.shape[0]

    @property
    def n_features(self) -> int:
        return self.data.shape[1] if self.data.ndim > 1 else 1

    def __repr__(self) -> str:
        return (
            f"Dataset(name={self.name!r}, n_samples={self.n_samples}, "
            f"n_features={self.n_features}, targets={len(self.target_names)})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a plain dictionary (useful for serialization)."""
        return {
            "data": self.data.tolist(),
            "target": self.target.tolist(),
            "feature_names": self.feature_names,
            "target_names": self.target_names,
            "name": self.name,
            "description": self.description,
        }

    def head(self, n: int = 5) -> str:
        """Pretty-print the first *n* rows."""
        lines = []
        header = self.feature_names or [f"x{i}" for i in range(self.n_features)]
        lines.append("\t".join(["target"] + header))
        for i in range(min(n, self.n_samples)):
            row = self.data[i] if self.data.ndim > 1 else [self.data[i]]
            vals = "\t".join(f"{v:.4g}" if isinstance(v, float) else str(v) for v in row)
            lines.append(f"{self.target[i]}\t{vals}")
        return "\n".join(lines)

    def to_csv(self, path: str, **kwargs: Any) -> None:
        """Write this dataset to a CSV file (see :mod:`aion.datasets.io`)."""
        from .io import write_csv
        write_csv(self, path, **kwargs)

    def to_json(self, path: str, **kwargs: Any) -> None:
        """Write this dataset to a JSON file."""
        from .io import write_json
        write_json(self, path, **kwargs)

    def to_jsonl(self, path: str, **kwargs: Any) -> None:
        """Write this dataset to JSON Lines."""
        from .io import write_jsonl
        write_jsonl(self, path, **kwargs)

    def to_parquet(self, path: str, **kwargs: Any) -> None:
        """Write this dataset to Parquet (requires pandas)."""
        from .io import write_parquet
        write_parquet(self, path, **kwargs)

    def to_dataframe(self, **kwargs: Any) -> Any:
        """Convert to a pandas DataFrame (requires pandas)."""
        from .io import to_dataframe
        return to_dataframe(self, **kwargs)

    def to_numpy(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return ``(X, y)`` for sklearn-style APIs."""
        from .io import to_numpy
        return to_numpy(self)


def train_test_split_dataset(
    ds: Dataset,
    *,
    test_ratio: float = 0.2,
    shuffle: bool = True,
    seed: Optional[int] = None,
) -> Tuple[Dataset, Dataset]:
    """Split a :class:`Dataset` into train and test :class:`Dataset` objects."""
    rng = np.random.RandomState(seed)
    n = ds.n_samples
    indices = np.arange(n)
    if shuffle:
        rng.shuffle(indices)
    split = int(n * (1 - test_ratio))
    train_idx, test_idx = indices[:split], indices[split:]
    return (
        Dataset(
            data=ds.data[train_idx],
            target=ds.target[train_idx],
            feature_names=ds.feature_names,
            target_names=ds.target_names,
            description=ds.description,
            name=ds.name + "_train",
            metadata={**ds.metadata, "split": "train"},
        ),
        Dataset(
            data=ds.data[test_idx],
            target=ds.target[test_idx],
            feature_names=ds.feature_names,
            target_names=ds.target_names,
            description=ds.description,
            name=ds.name + "_test",
            metadata={**ds.metadata, "split": "test"},
        ),
    )
