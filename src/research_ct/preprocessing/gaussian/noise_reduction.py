"""Structural noise reduction for micro-CT volumes.

Applies a 3D isotropic Gaussian convolution filter to enforce the
Central Limit Theorem, ensuring high-frequency detector noise conforms
to the normal distributions required for GMM covariance matrices.
"""

import numpy as np
from scipy.ndimage import gaussian_filter
from typing import Optional


def Reduce_Noise_Volume(
    Volume: np.ndarray,
    Sigma: float = 0.8,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Apply isotropic Gaussian smoothing to a 3D volume.

    Args:
        Volume: The input 3D array of shape (D, H, W).
        Sigma: The standard deviation of the Gaussian kernel. Controls
            the spatial extent of the low-pass filter.
        out: Optional output array for in-place execution. Must match
            the shape and dtype of Volume to prevent reallocation.

    Returns:
        The smoothed 3D array.

    Raises:
        ValueError: If the input volume is not 3-dimensional.
    """
    if Volume.ndim != 3:
        raise ValueError(f"Expected 3D volume, got shape {Volume.shape}")

    # Validate output array shape if provided
    if out is not None and out.shape != Volume.shape:
        raise ValueError(f"out shape {out.shape} != Volume shape {Volume.shape}")

    # If Sigma is zero or negative, return the volume unmodified
    # (handling the copy logic if an out array was provided)
    if Sigma <= 0:
        if out is not None and out is not Volume:
            np.copyto(out, Volume)
            return out
        return Volume

    # Execute the 3D convolution. If 'out' is provided, this overwrites
    # the existing memory block instead of allocating a new one.
    Smoothed_Volume = gaussian_filter(Volume, sigma=Sigma, output=out)

    return Smoothed_Volume
