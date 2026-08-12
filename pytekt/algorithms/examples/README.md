# pytekt.algorithms — Example Notebooks

This folder contains Jupyter notebooks that demonstrate the full **pytekt.algorithms** API with detailed explanations and runnable examples.

## Notebooks

| Notebook | Content |
|----------|---------|
| **01_search_algorithms.ipynb** | Binary search, lower/upper bound, jump, exponential, linear search; first/last occurrence; is_sorted, find_peak_element; rotated, ternary, interpolation search. |
| **02_array_utilities.ipynb** | flatten_array, flatten_deep, chunk_array, pairwise, sliding_window, rolling_sum, remove_duplicates, moving_avarage, pad_array. |

## How to run

From the project root:

```bash
pip install -e .
jupyter notebook aion/algorithms/examples/
```

Or open the notebooks in JupyterLab or VS Code. The package uses only the Python standard library for algorithms (no extra dependencies for these examples).
