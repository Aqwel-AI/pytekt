"""
Autograd and backward passes for core operations.

Backward logic for matmul, softmax, layer_norm, relu, and transpose
lives in operations.py; this module re-exports Tensor for convenience.
"""

from .tensor import Tensor

__all__ = ["Tensor"]
