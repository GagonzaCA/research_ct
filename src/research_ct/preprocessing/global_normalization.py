"""Global intensity normalization using volume-wide percentiles.

Linear rescaling that preserves the global intensity-to-material
relationship. Avoids local transforms like CLAHE that destroy
mixture model assumptions.
"""

import numpy as np
from typing import Tuple, Optional


def Global_Percentile_Normalize(
    Volume: np.ndarray,
    Low_Percentile: float = 0.1,
    High_Percentile: float = 99.9,
    Target_Min: float = 0.0,
    Target_Max: float = 255.0,
) -> np.ndarray:
    """Linear scale entire volume using global percentiles.

    Every voxel is transformed by the same affine function:
        I' = (I - P_low) / (P_high - P_low) * (Target_Max - Target_Min) + Target_Min

    This preserves proportional separation between materials.

    Args:
        Volume: Input 3D array.
        Low_Percentile: Lower clipping percentile (default 0.1).
        High_Percentile: Upper clipping percentile (default 99.9).
        Target_Min: Desired output minimum.
        Target_Max: Desired output maximum.

    Returns:
        Normalized volume, float64, range [Target_Min, Target_Max].

    Raises:
        ValueError: If Low_Percentile >= High_Percentile.
    """
    if Low_Percentile >= High_Percentile:
        raise ValueError(
            f"Low_Percentile ({Low_Percentile}) must be < " f"High_Percentile ({High_Percentile})"
        )

    Volume_Float = Volume.astype(np.float64)

    # Compute global percentiles
    Low_Val, High_Val = np.percentile(
        Volume_Float,
        [Low_Percentile, High_Percentile],
    )

    if High_Val <= Low_Val:
        # Constant image
        return np.full_like(Volume_Float, Target_Min)

    # Clip and rescale
    Clipped = np.clip(Volume_Float, Low_Val, High_Val)
    Normalized = (Clipped - Low_Val) / (High_Val - Low_Val)
    Normalized = Normalized * (Target_Max - Target_Min) + Target_Min

    return Normalized


def Z_Score_Per_Slice(
    Volume: np.ndarray,
) -> np.ndarray:
    """Standardize each slice independently to correct inter-slice drift.

    Computes per-slice mean and std, then applies z-score:
        I'_z = (I_z - mu_z) / sigma_z

    Use only if histograms vary significantly between slices.
    This removes global intensity differences but preserves
    within-slice contrast.

    Args:
        Volume: 3D array, shape (D, H, W).

    Returns:
        Standardized volume, float64, approximately N(0,1) per slice.
    """
    D = Volume.shape[0]
    Standardized = np.zeros_like(Volume, dtype=np.float64)

    for Z in range(D):
        Slice = Volume[Z].astype(np.float64)
        Mean = Slice.mean()
        Std = Slice.std()

        if Std > 0:
            Standardized[Z] = (Slice - Mean) / Std
        else:
            Standardized[Z] = Slice - Mean

    return Standardized


def Check_Slice_Stationarity(
    Volume: np.ndarray,
    N_Bins: int = 256,
) -> Tuple[bool, float]:
    """Check if volume intensity distribution is stationary across slices.

    Compares histogram intersection between first, middle, and last slices.

    Args:
        Volume: 3D array.
        N_Bins: Number of histogram bins.

    Returns:
        Tuple of (is_stationary, similarity_score).
        is_stationary: True if similarity > 0.8.
        similarity_score: Histogram intersection score [0, 1].
    """
    D = Volume.shape[0]

    # Compute histograms
    Hist_0, Bins = np.histogram(Volume[0], bins=N_Bins, density=True)
    Hist_mid, _ = np.histogram(Volume[D // 2], bins=Bins, density=True)
    Hist_end, _ = np.histogram(Volume[-1], bins=Bins, density=True)

    # Histogram intersection
    Sim_0_mid = np.minimum(Hist_0, Hist_mid).sum()
    Sim_0_end = np.minimum(Hist_0, Hist_end).sum()

    Similarity = min(Sim_0_mid, Sim_0_end)

    Is_Stationary = Similarity > 0.8

    return Is_Stationary, Similarity
