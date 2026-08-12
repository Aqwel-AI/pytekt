"""
Core tensor and autograd components.

Tensor class with gradient tracking and differentiable operations
(matmul, softmax, layer_norm, relu, transpose). Full documentation:
aion/former/README.md and aion/former/docs/architecture.md.
"""

from .tensor import Tensor
from .operations import matmul, softmax, layer_norm, relu, transpose

__all__ = [
    "Tensor",
    "matmul",
    "softmax",
    "layer_norm",
    "relu",
    "transpose",
]
