# pytekt.algorithms — Example Notebooks

This folder contains runnable Jupyter notebooks demonstrating the **`pytekt.algorithms`** suite, covering all 7 domain categories, the dynamic catalog discovery system, and over 570+ tested algorithms.

---

## 📚 Complete Notebook Catalog

| # | Notebook | Domain / Topics Covered | Key Functions & Utilities |
|---|---|---|---|
| **01** | [`01_search_algorithms.ipynb`](01_search_algorithms.ipynb) | **Searching** | `binary_search`, `lower_bound`, `upper_bound`, `jump_search`, `exponential_search`, `linear_search`, `First_Occurrence`, `Last_Occurrence`, `roatated_search`, `ternary_search`, `interpolation_search` |
| **02** | [`02_array_utilities.ipynb`](02_array_utilities.ipynb) | **Data Structures (Arrays)** | `flatten_array`, `flatten_deep`, `chunk_array`, `pairwise`, `sliding_window`, `rolling_sum`, `remove_duplicates`, `moving_average`, `pad_array` |
| **03** | [`03_sorting_catalog.ipynb`](03_sorting_catalog.ipynb) | **Sorting & Catalog** | `quick_sort`, `merge_sort`, `heap_sort`, `tim_sort`, `radix_sort`, `shell_sort`, `counting_sort`, `bucket_sort`, `list_algorithms("sorting")` |
| **04** | [`04_dp_greedy.ipynb`](04_dp_greedy.ipynb) | **Paradigms (DP & Greedy)** | `knapsack_01_max_value`, `lcs_length`, `edit_distance`, `lis_length`, `coin_change_min_coins`, `fractional_knapsack`, `activity_selection`, `gas_station` |
| **05** | [`05_catalog_browser.ipynb`](05_catalog_browser.ipynb) | **Catalog & Introspection** | `count_algorithms()`, `categories()`, `list_algorithms(category)`, `get_algorithm(name)`, keyword search and dynamic dispatch |
| **06** | [`06_graphs_networks.ipynb`](06_graphs_networks.ipynb) | **Graphs & Networks** | `bfs`, `dfs`, `toposort`, `shortest_path_unweighted`, `dijkstra`, `bellman_ford`, `kruskal_mst`, `prim_mst`, `pagerank`, `connected_components` |
| **07** | [`07_data_structures.ipynb`](07_data_structures.ipynb) | **Data Structures** | `TreeNode`, `build_bst_from_sorted`, `bst_search`, `inorder_traversal`, `build_max_heap`, `heapify_list`, `make_disjoint_set`, `union_sets`, `connected`, `detect_cycle_undirected` |
| **08** | [`08_mathematics_numerical.ipynb`](08_mathematics_numerical.ipynb) | **Mathematics & Geometry** | `gcd`, `lcm`, `is_prime`, `sieve_primes`, `catalan_number`, `bisection_root`, `simpson_integration`, `trapezoidal_integration`, `convex_hull`, `polygon_area`, `closest_pair_distance` |
| **09** | [`09_strings_compression.ipynb`](09_strings_compression.ipynb) | **Strings & Compression** | `longest_palindrome_substring`, `reverse_words`, `is_anagram`, `compress_string`, `kmp_search`, `run_length_encode`, `run_length_decode`, `delta_encode`, `delta_decode` |
| **10** | [`10_algorithmic_paradigms.ipynb`](10_algorithmic_paradigms.ipynb) | **Paradigms & Bit Manipulation** | `n_queens_solutions`, `subsets`, `permutations`, `container_with_most_water`, `two_sum_sorted`, `trap_rain_water`, `max_sum_subarray_size_k`, `longest_substring_without_repeating`, `popcount`, `single_number`, `hamming_distance` |

---

## 🚀 How to Run

From the repository root:

```bash
# 1. Install pytekt in editable development mode
pip install -e .

# 2. Launch Jupyter Notebook or JupyterLab
jupyter notebook pytekt/algorithms/examples/
```

All examples rely **only** on the Python standard library for algorithm execution (zero external dependencies).
