"""Intensity normalization utilities."""

import numpy as np
from typing import Optional, Tuple


def Normalize_To_Range(
    Image: np.ndarray,
    Target_Min: float = 0.0,
    Target_Max: float = 255.0,
) -> np.ndarray:
    """Linear scale image to target range.
    
    Args:
        Image: Input array.
        Target_Min: Desired minimum.
        Target_Max: Desired maximum.
    
    Returns:
        Scaled array.
    """
    Min_Val = Image.min()
    Max_Val = Image.max()
    
    if Max_Val == Min_Val:
        return np.full_like(Image, Target_Min)
    
    Scaled = (Image - Min_Val) / (Max_Val - Min_Val)
    return Scaled * (Target_Max - Target_Min) + Target_Min


def Percentile_Clip(
    Image: np.ndarray,
    Low_Percentile: float = 0.5,
    High_Percentile: float = 99.5,
) -> Tuple[np.ndarray, float, float]:
    """Clip image at percentiles without rescaling.
    
    Args:
        Image: Input array.
        Low_Percentile: Lower clip percentile.
        High_Percentile: Upper clip percentile.
    
    Returns:
        Tuple of (clipped_image, actual_low, actual_high).
    """
    Low, High = np.percentile(Image, [Low_Percentile, High_Percentile])
    return np.clip(Image, Low, High), Low, High


def Z_Score_Normalize(Image: np.ndarray) -> np.ndarray:
    """Standardize to zero mean, unit variance.
    
    Args:
        Image: Input array.
    
    Returns:
        Standardized array.
    """
    Mean = Image.mean()
    Std = Image.std()
    
    if Std == 0:
        return np.zeros_like(Image)
    
    return (Image - Mean) / Std