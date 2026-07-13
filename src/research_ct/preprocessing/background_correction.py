"""Global background correction for beam hardening removal.

Uses large-scale Gaussian blur subtraction per slice to flatten
the slowly varying intensity baseline while preserving material
contrast.
"""

import numpy as np
from scipy.ndimage import gaussian_filter
from typing import Optional


def Correct_Background_Global(
    Slice: np.ndarray,
    Sigma: float = 30.0,
) -> np.ndarray:
    """Subtract large-scale background to correct beam hardening.
    
    A Gaussian filter with large sigma estimates the low-frequency
    background gradient (beam hardening artifact). Subtracting this
    flattens the baseline without affecting high-frequency material
    boundaries.
    
    Args:
        Slice: 2D grayscale image, shape (H, W).
        Sigma: Standard deviation of Gaussian kernel in voxels.
            Larger sigma = more background removed.
            Default 30.0 works for typical book micro-CT.
    
    Returns:
        Background-corrected slice, float64, shifted to positive range.
    
    Raises:
        ValueError: If Sigma <= 0.
    """
    if Sigma <= 0:
        raise ValueError(f"Sigma must be positive, got {Sigma}")

    Slice_Float = Slice.astype(np.float64, copy=False)

    # Estimate background with large Gaussian
    Background = gaussian_filter(Slice_Float, sigma=Sigma)

    # Subtract and shift to positive
    Corrected = Slice_Float - Background
    return Corrected - Corrected.min()


def Correct_Background_Volume(
    Volume: np.ndarray,
    Sigma: float = 30.0,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Apply global background correction to entire 3D volume.

    Processes each slice independently. The background model is
    2D per-slice; no inter-slice smoothing is applied.

    Args:
        Volume: 3D array, shape (D, H, W).
        Sigma: Gaussian kernel sigma in voxels.
        out: Optional output array to write into (in-place when
            out is Volume). Must have same shape as Volume.

    Returns:
        Corrected volume, float64.
    """
    D = Volume.shape[0]

    if out is None:
        out = np.zeros_like(Volume, dtype=np.float64)
    elif out.shape != Volume.shape:
        raise ValueError(
            f"out shape {out.shape} does not match Volume shape {Volume.shape}"
        )

    for Z in range(D):
        out[Z] = Correct_Background_Global(Volume[Z], Sigma)

    return out


def Auto_Estimate_Background_Sigma(
    Volume: np.ndarray,
    Fraction: float = 0.05,
) -> float:
    """Estimate appropriate background sigma from volume dimensions.
    
    Uses a fraction of the smaller lateral dimension as a heuristic.
    For a 2000x2000 slice, Fraction=0.05 gives sigma=100.
    
    Args:
        Volume: 3D array.
        Fraction: Fraction of min(H,W) to use as sigma.
    
    Returns:
        Estimated sigma value.
    """
    _, H, W = Volume.shape
    Sigma = max(10.0, Fraction * min(H, W))
    
    return Sigma