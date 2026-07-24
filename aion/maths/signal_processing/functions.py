"""Signal Processing mathematics functions."""

from .._shared import Any, Callable, List, Optional, Sequence, Tuple, Union, math, np, random


def fft(signal: Sequence[Union[int, float, complex]]) -> List[complex]:
    """
    Compute the Fast Fourier Transform of a signal.
    
    Args:
        signal: Input signal (real or complex)
        
    Returns:
        FFT coefficients
        
    Examples:
        >>> fft([1, 0, 1, 0])
        [(2+0j), (0+0j), (2+0j), (0+0j)]
    """
    return np.fft.fft(signal).tolist()


def ifft(coefficients: Sequence[complex]) -> List[complex]:
    """
    Compute the Inverse Fast Fourier Transform.
    
    Args:
        coefficients: FFT coefficients
        
    Returns:
        Reconstructed signal
        
    Examples:
        >>> ifft([(2+0j), (0+0j), (2+0j), (0+0j)])
        [(1+0j), (0+0j), (1+0j), (0+0j)]
    """
    return np.fft.ifft(coefficients).tolist()


def convolution(signal: Sequence[Union[int, float]], kernel: Sequence[Union[int, float]]) -> List[float]:
    """
    Compute 1D convolution of signal with kernel.
    
    Args:
        signal: Input signal
        kernel: Convolution kernel
        
    Returns:
        Convolved signal
        
    Examples:
        >>> convolution([1, 2, 3], [1, 0, -1])
        [1.0, 2.0, 2.0, 0.0, -3.0]
    """
    return np.convolve(signal, kernel, mode='full').tolist()


__all__ = ['fft', 'ifft', 'convolution']
