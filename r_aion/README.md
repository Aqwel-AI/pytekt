# Aqwel-Aion for R (`r_aion`)

Native R bindings for **Aqwel-Aion** high-performance C++ numerical algorithms layer.

## Requirements
- R (>= 4.0)
- Rcpp (`install.packages("Rcpp")`)
- `devtools` (`install.packages("devtools")`)
- C++14 compiler (GCC, Clang, or MSVC)

## Installation

From R terminal:

```R
# Option A: Install directly from GitHub repository
devtools::install_github("aqwel/aion", subdir = "r_aion")

# Option B: Install from local repository directory
devtools::install("path/to/Aion/r_aion")
```

## Quickstart

```R
library(aion)

# Fast 1D Reductions
x <- c(1.0, 2.0, 3.0, 4.0, 5.0)

cat("Sum:", aion_sum(x), "\n")
cat("Mean:", aion_mean(x), "\n")
cat("Variance:", aion_variance(x), "\n")
cat("L2 Norm:", aion_norm2(x), "\n")

# Fast Dot Product
y <- c(2.0, 0.5, 1.0, 3.0, 2.0)
cat("Dot Product:", aion_dot(x, y), "\n")

# Rolling Mean
print(aion_rolling_mean(x, window = 3))

# Prefix Sum
print(aion_prefix_sum(x))

# Fast Matrix Multiplication
A <- c(1, 2, 3, 4) # 2x2 matrix
B <- c(5, 6, 7, 8) # 2x2 matrix
print(aion_matrix_multiply(A, B, m = 2, n = 2, p = 2))
```
