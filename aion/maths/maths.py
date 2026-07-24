"""Flat compatibility API for the categorized :mod:`aion.maths` package."""

from typing import Dict, List, Optional, Tuple, Union

from .arithmetic.functions import *  # noqa: F401,F403
from .random.functions import *  # noqa: F401,F403
from .linear_algebra.functions import *  # noqa: F401,F403
from .statistics.functions import *  # noqa: F401,F403
from .trigonometry.functions import *  # noqa: F401,F403
from .machine_learning.functions import *  # noqa: F401,F403
from .signal_processing.functions import *  # noqa: F401,F403
from .probability.functions import *  # noqa: F401,F403
from .number_theory.functions import *  # noqa: F401,F403
from .utilities.functions import *  # noqa: F401,F403

MATH_SECTIONS: Dict[str, Tuple[str, ...]] = {'arithmetic': ('addition', 'subtraction', 'multiplication', 'division', 'power', 'sqrt', 'log', 'log10', 'exp', 'abs_value', 'factorial', 'gcd', 'lcm'), 'random': ('set_seed', 'random_choice', 'shuffle_list', 'sample_uniform', 'sample_normal', 'train_test_split'), 'linear_algebra': ('dot_product', 'transpose', 'matrix_multiply', 'normalize_vector', 'determinant', 'matrix_inverse', 'eigenvalues', 'svd', 'matrix_rank', 'cross_product', 'vector_magnitude'), 'statistics': ('mean', 'median', 'variance', 'std_dev', 'min_max_scale', 'z_score', 'correlation', 'linear_regression', 'covariance'), 'trigonometry': ('sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'degrees', 'radians'), 'machine_learning': ('sigmoid', 'tanh_activation', 'relu', 'leaky_relu', 'softmax', 'mse_loss', 'mae_loss', 'cross_entropy_loss', 'euclidean_distance', 'manhattan_distance', 'cosine_similarity', 'hamming_distance'), 'signal_processing': ('fft', 'ifft', 'convolution'), 'probability': ('normal_pdf', 'normal_cdf', 'binomial_pmf', 'poisson_pmf'), 'number_theory': ('is_prime', 'fibonacci', 'prime_factors'), 'utilities': ('clamp', 'lerp')}


def list_sections() -> List[str]:
    """Return the available mathematics sections in display order."""
    return list(MATH_SECTIONS)


def section_functions(
    section: Optional[str] = None,
) -> Union[Dict[str, Tuple[str, ...]], Tuple[str, ...]]:
    """Return the function names grouped by section."""
    if section is None:
        return dict(MATH_SECTIONS)
    try:
        return MATH_SECTIONS[section]
    except KeyError as exc:
        available = ", ".join(MATH_SECTIONS)
        raise ValueError(
            f"Unknown maths section '{section}'. Available: {available}"
        ) from exc


__all__ = [
    "MATH_SECTIONS",
    "list_sections",
    "section_functions",
    *[name for names in MATH_SECTIONS.values() for name in names],
]
