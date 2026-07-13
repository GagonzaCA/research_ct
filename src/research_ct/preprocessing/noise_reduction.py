"""Mild isotropic Gaussian smoothing for noise reduction.

Designed specifically to tighten material intensity distributions
into approximately Gaussian shapes for GMM fitting. Uses linear,
shift-invariant filtering that preserves global mixture structure.
"""

import numpy as np
from scipy.ndimage import gaussian_filter
from typing import Optional


def Reduce_Noise_Gaussian(
    Image: np.ndarray,
    Sigma: float = 0.8,
) -> np.ndarray:
    """Apply mild Gaussian smoothing to reduce Poisson noise.

    The sigma is intentionally small (sub-voxel) to avoid blurring
    material boundaries while sufficient to apply the Central Limit
    Theorem effect that makes noise more Gaussian.

    Args:
        Image: Input array, any shape.
        Sigma: Standard deviation of Gaussian kernel in voxels.
            Default 0.8 is optimal for most micro-CT data.
            Range: 0.5–1.5 recommended.

    Returns:
        Smoothed array, float64.

    Raises:
        ValueError: If Sigma <= 0.
    """
    if Sigma <= 0:
        raise ValueError(f"Sigma must be positive, got {Sigma}")

    Image_Float = Image.astype(np.float64, copy=False)
    return gaussian_filter(Image_Float, sigma=Sigma)


def Reduce_Noise_Volume(
    Volume: np.ndarray,
    Sigma: float = 0.8,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Apply Gaussian smoothing to entire 3D volume.

    Uses 3D Gaussian kernel for isotropic smoothing across all
    dimensions. For anisotropic voxels, consider per-slice 2D
    smoothing with different sigmas.

    Args:
        Volume: 3D array, shape (D, H, W).
        Sigma: Gaussian kernel sigma in voxels.
        out: Optional output array (in-place when out is Volume).

    Returns:
        Smoothed volume, float64.
    """
    Volume_Float = Volume.astype(np.float64, copy=False)
    return gaussian_filter(Volume_Float, sigma=Sigma, output=out)
