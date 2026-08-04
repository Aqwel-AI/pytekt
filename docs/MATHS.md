# Aion mathematics

`aion.maths` is the core numerical toolbox. It uses NumPy, with standard
library fallbacks where practical, and does not require the optional AI or
visualization extras.

The implementation is organized as a package under `aion/maths/`. Each
category contains its own `functions.py` implementation and `__init__.py`
exports, while `aion.maths` keeps the original flat API for backwards
compatibility.

## Sections

| Section | Main capabilities |
| --- | --- |
| `arithmetic` | Basic operations, powers, logarithms, factorials, GCD, and LCM |
| `random` | Reproducible sampling, shuffling, and train/test splitting |
| `linear_algebra` | Vectors, matrices, determinants, inverses, eigenvalues, and SVD |
| `statistics` | Mean, median, variance, scaling, correlation, regression, and covariance |
| `trigonometry` | Trigonometric functions, inverse functions, degrees, and radians |
| `machine_learning` | Activations, losses, and distance metrics |
| `signal_processing` | FFT, inverse FFT, and convolution |
| `probability` | Normal, binomial, and Poisson distributions |
| `number_theory` | Primality, Fibonacci numbers, and prime factorization |
| `utilities` | Clamping and linear interpolation |

## Discover sections

```python
from aion import maths

print(maths.list_sections())
print(maths.section_functions("linear_algebra"))
```

Focused imports are also available:

```python
from aion.maths.linear_algebra import determinant, matrix_multiply
from aion.maths.statistics import mean, variance
from aion.maths.probability import normal_pdf
```

For example, the linear algebra implementation is in
`aion/maths/linear_algebra/functions.py`.

## Examples

```python
from aion import maths

maths.addition(2, 3)
maths.matrix_multiply([[1, 2]], [[3], [4]])
maths.mean([1, 2, 3, 4, 5])
maths.sigmoid([0, 1, -1])
maths.normal_pdf(0)
maths.prime_factors(84)
```

For the full function reference, inspect the docstrings or generate API
documentation with Aion's documentation helpers.
