"""Optional pandas export for query results."""

from __future__ import annotations

from typing import Any, Dict, List


def rows_to_dataframe(rows: List[Dict[str, Any]]):
    """Convert row dicts to a pandas DataFrame (requires pandas)."""
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError(
            "pandas is required for to_df(). Install with: pip install pandas"
        ) from e
    return pd.DataFrame(rows)
