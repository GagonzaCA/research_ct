"""Uncertainty quantification from probabilistic segmentation."""

import numpy as np
from typing import Tuple


def Compute_Uncertainty(Probabilities: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute uncertainty maps from class probabilities.
    
    Args:
        Probabilities: Class probabilities, shape (D, H, W, K).
    
    Returns:
        Tuple of (entropy, max_probability).
            Entropy: shape (D, H, W), high = uncertain.
            Max_Probability: shape (D, H, W), high = confident.
    """
    # Shannon entropy: H = -sum(p * log(p))
    # Clip to avoid log(0)
    Clipped = np.clip(Probabilities, 1e-10, 1.0)
    Entropy = -np.sum(Clipped * np.log(Clipped), axis=3)
    
    # Maximum probability (confidence)
    Max_Prob = np.max(Probabilities, axis=3)
    
    return Entropy, Max_Prob


def Compute_Margin(
    Probabilities: np.ndarray,
    Top_K: int = 2,
) -> np.ndarray:
    """Compute margin between top two class probabilities.
    
    Small margin = high uncertainty (ambiguous between two classes).
    
    Args:
        Probabilities: Class probabilities, shape (D, H, W, K).
        Top_K: Number of top classes to compare.
    
    Returns:
        Margin array, shape (D, H, W).
    """
    Sorted = np.sort(Probabilities, axis=3)
    
    if Top_K == 2:
        return Sorted[..., -1] - Sorted[..., -2]
    
    return Sorted[..., -1] - Sorted[..., -Top_K].mean(axis=3)