"""Random mathematics functions."""

from .._shared import Any, Callable, List, Optional, Sequence, Tuple, Union, math, np, random


def set_seed(seed: int) -> None:
    """
    Set the seed for all random number generators to ensure reproducibility.
    
    This function sets seeds for both Python's built-in random module and NumPy's
    random number generator, ensuring consistent results across runs.
    
    Args:
        seed: The seed value to use for random number generation (integer)
        
    Examples:
        >>> set_seed(42)
        >>> random.random()  # Will always return the same value for this seed
        0.6394267984578837
        >>> np.random.rand(3)  # Will always produce the same array for this seed
        array([0.37454012, 0.95071431, 0.73199394])
    """
    random.seed(seed)
    np.random.seed(seed)


def random_choice(probabilities: List[float]) -> int:
    """
    Select an index based on a probability distribution using weighted random selection.
    
    Args:
        probabilities: List of probabilities that should sum to approximately 1.0
        
    Returns:
        The chosen index (0-based)
        
    Raises:
        ValueError: If probabilities list is empty
        
    Examples:
        >>> set_seed(42)
        >>> random_choice([0.1, 0.7, 0.2])
        1  # Most likely to return 1 due to 0.7 probability
        >>> random_choice([0.5, 0.5])  # Equal probability
        0
    """
    if not probabilities:
        raise ValueError("Probabilities list cannot be empty")
    
    cumulative = []
    current = 0.0
    
    for p in probabilities:
        current += p
        cumulative.append(current)
    
    r = random.random()  # uniform [0,1)
    
    for i, threshold in enumerate(cumulative):
        if r < threshold:
            return i
    
    return len(probabilities) - 1


def shuffle_list(data: List[Any]) -> List[Any]:
    """
    Shuffle a list and return a new shuffled list (does not modify the original).
    
    Uses Fisher-Yates shuffle algorithm for uniform randomness.
    
    Args:
        data: Input list to shuffle
        
    Returns:
        New shuffled copy of the list
        
    Examples:
        >>> original = [1, 2, 3, 4, 5]
        >>> shuffled = shuffle_list(original)
        >>> original  # Original list unchanged
        [1, 2, 3, 4, 5]
        >>> len(shuffled) == len(original)
        True
    """
    shuffled = data[:]  # Create a copy
    random.shuffle(shuffled)
    return shuffled


def sample_uniform(low: float = 0.0, high: float = 1.0, size: int = 1) -> List[float]:
    """
    Generate random samples from a uniform distribution.
    
    Args:
        low: Lower bound (inclusive, default=0.0)
        high: Upper bound (exclusive, default=1.0)
        size: Number of samples to generate (default=1)
        
    Returns:
        List of uniformly distributed random values
        
    Raises:
        ValueError: If low >= high or size < 1
        
    Examples:
        >>> set_seed(42)
        >>> sample_uniform(0, 10, 3)
        [6.39, 9.50, 7.31]  # Values between 0 and 10
        >>> sample_uniform(-1, 1, 2)
        [-0.25, 0.46]  # Values between -1 and 1
    """
    if low >= high:
        raise ValueError("low must be less than high")
    if size < 1:
        raise ValueError("size must be at least 1")
    
    return [random.uniform(low, high) for _ in range(size)]


def sample_normal(mean: float = 0.0, std: float = 1.0, size: int = 1) -> List[float]:
    """
    Generate random samples from a normal (Gaussian) distribution.
    
    Uses Box-Muller transformation for generating normally distributed values.
    
    Args:
        mean: Mean of the distribution (default=0.0)
        std: Standard deviation of the distribution (default=1.0, must be > 0)
        size: Number of samples to generate (default=1)
        
    Returns:
        List of normally distributed random values
        
    Raises:
        ValueError: If std <= 0 or size < 1
        
    Examples:
        >>> set_seed(42)
        >>> sample_normal(mean=5, std=2, size=3)
        [4.2, 6.1, 3.8]  # Values around mean=5 with std=2
        >>> sample_normal()  # Standard normal (mean=0, std=1)
        [0.49]
    """
    if std <= 0:
        raise ValueError("Standard deviation must be positive")
    if size < 1:
        raise ValueError("size must be at least 1")
    
    return [random.gauss(mean, std) for _ in range(size)]


def train_test_split(data: List[Any], ratio: float = 0.8) -> Tuple[List[Any], List[Any]]:
    """
    Split dataset into training and testing sets with random shuffling.
    
    Args:
        data: Dataset to split
        ratio: Proportion of data for training (default=0.8, must be between 0 and 1)
        
    Returns:
        Tuple of (train_set, test_set)
        
    Raises:
        ValueError: If ratio is not between 0 and 1
        
    Examples:
        >>> data = list(range(10))  # [0, 1, 2, ..., 9]
        >>> train, test = train_test_split(data, ratio=0.7)
        >>> len(train), len(test)
        (7, 3)
        >>> set(train + test) == set(data)  # All data preserved
        True
    """
    if not 0 < ratio < 1:
        raise ValueError("ratio must be between 0 and 1")
    
    shuffled_data = shuffle_list(data)
    split_index = int(len(shuffled_data) * ratio)
    return shuffled_data[:split_index], shuffled_data[split_index:]


__all__ = ['set_seed', 'random_choice', 'shuffle_list', 'sample_uniform', 'sample_normal', 'train_test_split']
