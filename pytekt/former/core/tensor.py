"""
Minimal tensor class for the Aion transformer module.

NumPy-backed array with optional gradient tracking for autograd.
Used by all model layers and operations in aion.former.
"""

import numpy as np
from typing import Optional, Tuple, List, Callable


# -----------------------------------------------------------------------------
# Tensor class
# -----------------------------------------------------------------------------

class Tensor:
    """
    Array with optional gradient tracking for automatic differentiation.

    Parameters
    ----------
    data : np.ndarray or array-like
        Numerical data; converted to float64 if not already an ndarray.
    requires_grad : bool, optional
        Whether to track gradients for this tensor (default False).
    _grad_fn : callable, optional
        Backward function; used internally by operations.
    _prev : tuple of Tensor, optional
        Input tensors that produced this one; used for backward pass.

    Attributes
    ----------
    _data : np.ndarray
        The underlying array.
    grad : np.ndarray or None
        Gradient accumulated during backward pass.
    shape, ndim : tuple, int
        Shape and number of dimensions (from _data).
    """

    __array_priority__ = 1.0  # Ensures Tensor ops take precedence in mixed NumPy/Tensor expressions

    def __init__(
        self,
        data: np.ndarray,
        requires_grad: bool = False,
        _grad_fn: Optional[Callable] = None,
        _prev: Optional[Tuple["Tensor", ...]] = None,
    ):
        # Coerce to float64 ndarray for consistent computation
        if not isinstance(data, np.ndarray):
            data = np.asarray(data, dtype=np.float64)
        self._data = data
        self.requires_grad = requires_grad
        self._grad_fn = _grad_fn
        self._prev = _prev if _prev else ()
        self.grad: Optional[np.ndarray] = None
        self._shape = self._data.shape

    @property
    def data(self) -> np.ndarray:
        """Return the underlying NumPy array."""
        return self._data

    @data.setter
    def data(self, value: np.ndarray) -> None:
        """Set the underlying array and update cached shape."""
        self._data = value
        self._shape = value.shape

    @property
    def shape(self) -> Tuple[int, ...]:
        """Shape of the tensor."""
        return self._shape

    @property
    def ndim(self) -> int:
        """Number of dimensions."""
        return self._data.ndim

    def __repr__(self) -> str:
        return f"Tensor({self._data}, requires_grad={self.requires_grad})"

    def __neg__(self) -> "Tensor":
        return _neg(self)

    def __add__(self, other) -> "Tensor":
        return _add(self, other)

    def __radd__(self, other) -> "Tensor":
        return _add(other, self)

    def __sub__(self, other) -> "Tensor":
        return _sub(self, other)

    def __mul__(self, other) -> "Tensor":
        return _mul(self, other)

    def __rmul__(self, other) -> "Tensor":
        return _mul(other, self)

    def __matmul__(self, other) -> "Tensor":
        from .operations import matmul
        return matmul(self, other)

    def __getitem__(self, key):
        return _getitem(self, key)

    def sum(self, axis=None, keepdims=False) -> "Tensor":
        """Sum over axes; supports backward."""
        return _sum(self, axis=axis, keepdims=keepdims)

    def mean(self, axis=None, keepdims=False) -> "Tensor":
        """Mean over axes; supports backward."""
        return _mean(self, axis=axis, keepdims=keepdims)

    def reshape(self, *shape: int) -> "Tensor":
        """Reshape tensor; supports backward."""
        return _reshape(self, shape)

    def T(self) -> "Tensor":
        """Transpose last two dimensions."""
        from .operations import transpose
        return transpose(self)

    def backward(self, gradient: Optional[np.ndarray] = None) -> None:
        """
        Run backward pass from this tensor.

        Parameters
        ----------
        gradient : np.ndarray, optional
            Upstream gradient; defaults to ones_like(_data) for scalar loss.
        """
        if gradient is None:
            gradient = np.ones_like(self._data)
        # Accumulate gradient from multiple backward calls if needed
        if self.grad is None:
            self.grad = gradient
        else:
            self.grad = self.grad + gradient
        # Propagate to inputs via backward function
        if self._grad_fn is not None and self._prev:
            grads = self._grad_fn(self.grad, self, *self._prev)
            if not isinstance(grads, tuple):
                grads = (grads,)
            for i, inp in enumerate(self._prev):
                if inp.requires_grad and i < len(grads) and grads[i] is not None:
                    inp.backward(grads[i])

    def zero_grad(self) -> None:
        """Clear gradient and recursively clear gradients of input tensors."""
        self.grad = None
        for p in self._prev:
            if hasattr(p, "zero_grad"):
                p.zero_grad()

    def numpy(self) -> np.ndarray:
        """Return a copy of the underlying array."""
        return self._data.copy()


# -----------------------------------------------------------------------------
# Internal ops that build the computation graph
# -----------------------------------------------------------------------------

def _make_tensor(
    data: np.ndarray,
    requires_grad: bool,
    grad_fn: Optional[Callable],
    *prev: "Tensor",
) -> Tensor:
    """
    Build a new tensor with optional gradient tracking and backward function.

    Parameters
    ----------
    data : np.ndarray
        Output data of the operation.
    requires_grad : bool
        Whether this tensor needs gradients.
    grad_fn : callable or None
        Backward function (grad, out, *inputs) -> tuple of input grads.
    *prev : Tensor
        Input tensors that produced this output.

    Returns
    -------
    Tensor
        New tensor; requires_grad is True if any input requires_grad.
    """
    req = requires_grad or any(p.requires_grad for p in prev)
    return Tensor(data, requires_grad=req, _grad_fn=grad_fn, _prev=prev)


def _neg_backward(grad: np.ndarray, out: Tensor, x: Tensor) -> Tuple[np.ndarray]:
    return (-grad,)


def _neg(x: Tensor) -> Tensor:
    return _make_tensor(-x._data, False, _neg_backward, x)


def _add_backward(grad: np.ndarray, out: Tensor, a: Tensor, b: Tensor) -> Tuple[np.ndarray, np.ndarray]:
    ga = grad
    gb = grad
    if a.shape != grad.shape:
        ga = np.sum(grad, axis=tuple(range(grad.ndim - a.ndim)), keepdims=False)
    if b.shape != grad.shape:
        gb = np.sum(grad, axis=tuple(range(grad.ndim - b.ndim)), keepdims=False)
    return (ga, gb)


def _add(a: Tensor, b: Tensor) -> Tensor:
    a_data = a._data if isinstance(a, Tensor) else np.asarray(a, dtype=np.float64)
    b_data = b._data if isinstance(b, Tensor) else np.asarray(b, dtype=np.float64)
    if not isinstance(a, Tensor):
        a = Tensor(a_data, requires_grad=False)
    if not isinstance(b, Tensor):
        b = Tensor(b_data, requires_grad=False)
    return _make_tensor(a_data + b_data, False, _add_backward, a, b)


def _sub(a: Tensor, b: Tensor) -> Tensor:
    return _add(a, _neg(b))


def _mul_backward(grad: np.ndarray, out: Tensor, a: Tensor, b: Tensor) -> Tuple[np.ndarray, np.ndarray]:
    return (grad * b._data, grad * a._data)


def _mul(a: Tensor, b: Tensor) -> Tensor:
    a_data = a._data if isinstance(a, Tensor) else np.asarray(a, dtype=np.float64)
    b_data = b._data if isinstance(b, Tensor) else np.asarray(b, dtype=np.float64)
    if not isinstance(a, Tensor):
        a = Tensor(a_data, requires_grad=False)
    if not isinstance(b, Tensor):
        b = Tensor(b_data, requires_grad=False)
    return _make_tensor(a_data * b_data, False, _mul_backward, a, b)


def _getitem(x: Tensor, key) -> Tensor:
    def _backward(grad: np.ndarray, out: Tensor, xx: Tensor) -> Tuple[np.ndarray]:
        g = np.zeros_like(xx._data)
        g[key] = grad
        return (g,)
    return _make_tensor(x._data[key], False, _backward, x)


def _sum_backward(grad: np.ndarray, out: Tensor, x: Tensor, axis, keepdims) -> Tuple[np.ndarray]:
    if axis is not None and not keepdims:
        grad = np.expand_dims(grad, axis=axis)
    return (np.broadcast_to(grad, x.shape),)


def _sum(x: Tensor, axis=None, keepdims=False) -> Tensor:
    data = np.sum(x._data, axis=axis, keepdims=keepdims)
    return _make_tensor(
        data,
        False,
        lambda g, o, xx: _sum_backward(g, o, xx, axis, keepdims),
        x,
    )


def _mean_backward(grad: np.ndarray, out: Tensor, x: Tensor, axis, keepdims) -> Tuple[np.ndarray]:
    n = np.prod(x.shape) if axis is None else np.prod(np.array(x.shape)[np.atleast_1d(axis)])
    if axis is not None and not keepdims:
        grad = np.expand_dims(grad, axis=axis)
    return (np.broadcast_to(grad / n, x.shape),)


def _mean(x: Tensor, axis=None, keepdims=False) -> Tensor:
    data = np.mean(x._data, axis=axis, keepdims=keepdims)
    return _make_tensor(
        data,
        False,
        lambda g, o, xx: _mean_backward(g, o, xx, axis, keepdims),
        x,
    )


def _reshape_backward(grad: np.ndarray, out: Tensor, x: Tensor, shape: Tuple[int, ...]) -> Tuple[np.ndarray]:
    return (grad.reshape(x.shape),)


def _reshape(x: Tensor, shape: Tuple[int, ...]) -> Tensor:
    if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
        shape = shape[0]
    data = x._data.reshape(*shape)
    return _make_tensor(
        data,
        False,
        lambda g, o, xx: _reshape_backward(g, o, xx, shape),
        x,
    )
