# Pytekt for R (`r_pytekt`)

Native R bindings for **Pytekt** high-performance C++ numerical algorithms layer and Python AI research suite.

## Features

- **Blazing-Fast C++ Numerics (Rcpp)**: Native vectorized routines for 1D reductions, matrix multiplication, rolling windows, distance metrics, streaming histograms, and block chunk statistics.
- **Complete Python AI Suite via `reticulate`**: Access Pytekt's classical ML algorithms, physics engine, astronomy, computer vision, and transformers directly from R.

## Requirements

- R (>= 4.0)
- Rcpp (`install.packages("Rcpp")`)
- `devtools` (`install.packages("devtools")`)
- C++14 compiler (GCC, Clang, or MSVC)
- *(Optional)* `reticulate` (`install.packages("reticulate")`) for Python AI models

## Installation

From the R console:

```R
# Option A: Install directly from GitHub repository
devtools::install_github("aqwel/pytekt", subdir = "r_pytekt")

# Option B: Install from local repository directory
devtools::install("path/to/pytekt/r_pytekt")
```

---

## 1. Native High-Performance C++ Kernels

```R
library(pytekt)

x <- c(1.0, 2.0, 3.0, 4.0, 5.0)

# Reductions & Dispersion
pytekt_sum(x)                       # 15
pytekt_mean(x)                      # 3
pytekt_variance(x, ddof = 1)        # 2.5
pytekt_std(x, ddof = 1)             # 1.581139
pytekt_norm2(x)                     # 7.416198

# Extrema & 1-based indexing
pytekt_min(x)                       # 1
pytekt_max(x)                       # 5
pytekt_argmin(x)                    # 1
pytekt_argmax(x)                    # 5

# Vector Distance & Cosine Similarity
y <- c(2.0, 0.5, 1.0, 3.0, 2.0)
pytekt_dot(x, y)                    # 26
pytekt_euclidean_distance(x, y)     # 3.84056
pytekt_cosine_similarity(x, y)      # 0.77884

# Streaming & Rolling Windows
pytekt_prefix_sum(x)                # 1 3 6 10 15
pytekt_rolling_mean(x, window = 3)  # 2 3 4
pytekt_rolling_sum(x, window = 3)   # 6 9 12
pytekt_histogram(x, bins = 5, lo = 1.0, hi = 5.0) # 1 1 1 1 1
pytekt_chunk_statistics(x, chunk_size = 2)

# Matrix Multiplication (m x n) %*% (n x p) -> row-major flattened
A <- c(1, 2, 3, 4) # 2x2
B <- c(5, 6, 7, 8) # 2x2
pytekt_matrix_multiply(A, B, m = 2, n = 2, p = 2) # 19 22 43 50
```

---

## 2. Python AI & ML Research Models from R

If `reticulate` and the Python package are installed:

```R
library(pytekt)

if (pytekt_available()) {
  py <- import_pytekt()
  
  # Load datasets & train ML models
  iris <- py$datasets$load_iris()
  clf <- py$models$GaussianNB()
  clf$fit(iris$data, iris$target)
  
  preds <- clf$predict(iris$data)
  acc <- py$metrics$accuracy_score(iris$target, preds)
  cat("Accuracy:", acc, "\n")
}
```

