"""Revised preprocessing pipeline optimized for GMM/HMRF segmentation.

Replaces the visual-enhancement pipeline with a statistics-first
approach that preserves global intensity relationships and produces
Gaussian-mixture-friendly histograms.
"""

import time
import numpy as np

from typing import Tuple, Dict, Optional

from .background_correction import Correct_Background_Volume, Auto_Estimate_Background_Sigma
from .noise_reduction import Reduce_Noise_Volume
from .global_normalization import (
    Global_Percentile_Normalize,
    Z_Score_Per_Slice,
    Check_Slice_Stationarity,
)
from .histogram_diagnostics import Assess_Gmm_Readiness


def Preprocess_For_Gmm_Revised(
    Volume: np.ndarray,
    Background_Sigma: Optional[float] = None,
    Noise_Sigma: float = 0.8,
    Clip_Low_Percentile: float = 0.1,
    Clip_High_Percentile: float = 99.9,
    Check_Stationarity: bool = True,
    Apply_Slice_Standardization: bool = False,
    Verbose: bool = True,
) -> Tuple[np.ndarray, Dict]:
    """Complete preprocessing pipeline for GMM segmentation.

    Pipeline:
        1. Global background correction (beam hardening removal)
        2. Mild Gaussian noise reduction
        3. Optional per-slice standardization (if non-stationary)
        4. Global percentile normalization

    Args:
        Volume: Raw 3D volume (D, H, W), any numeric dtype.
        Background_Sigma: Gaussian sigma for background estimation.
            If None, auto-estimated from volume dimensions.
        Noise_Sigma: Gaussian sigma for noise reduction (default 0.8).
        Clip_Low_Percentile: Lower percentile for global clipping.
        Clip_High_Percentile: Upper percentile for global clipping.
        Check_Stationarity: Whether to test for slice-to-slice drift.
        Apply_Slice_Standardization: Force per-slice z-score even if
            stationary. Use with caution.
        Verbose: Print progress messages.

    Returns:
        Tuple of (preprocessed_volume, diagnostics_dict).
        diagnostics_dict contains histogram stats and GMM readiness.
    """
    D, H, W = Volume.shape

    if Verbose:
        print(
            f"[Preprocess_GMM] Input: {Volume.shape}, "
            f"dtype={Volume.dtype}, range [{Volume.min():.1f}, {Volume.max():.1f}]"
        )

    # Step 0: Convert to float64
    Volume_Float = Volume.astype(np.float64)

    # Step 1: Global background correction
    if Background_Sigma is None:
        Background_Sigma = Auto_Estimate_Background_Sigma(Volume_Float)

    if Verbose:
        print(f"\n[Step 1/4] Background correction (sigma={Background_Sigma:.1f})...")
    T0 = time.time()

    Corrected = Correct_Background_Volume(Volume_Float, Background_Sigma)

    if Verbose:
        print(
            f"[Step 1/4] Done in {time.time()-T0:.1f}s. "
            f"Range: [{Corrected.min():.1f}, {Corrected.max():.1f}]"
        )

    # Step 2: Noise reduction
    if Verbose:
        print(f"\n[Step 2/4] Noise reduction (sigma={Noise_Sigma})...")
    T0 = time.time()

    Smoothed = Reduce_Noise_Volume(Corrected, Noise_Sigma)

    if Verbose:
        print(
            f"[Step 2/4] Done in {time.time()-T0:.1f}s. "
            f"Range: [{Smoothed.min():.1f}, {Smoothed.max():.1f}]"
        )

    # Step 3: Stationarity check and optional standardization
    Need_Standardization = Apply_Slice_Standardization

    if Check_Stationarity and not Apply_Slice_Standardization:
        if Verbose:
            print("\n[Step 3/4] Checking slice stationarity...")

        Is_Stationary, Similarity = Check_Slice_Stationarity(Smoothed)

        if Verbose:
            print(f"[Step 3/4] Stationarity: {Is_Stationary} " f"(similarity={Similarity:.3f})")

        Need_Standardization = not Is_Stationary

    if Need_Standardization:
        if Verbose:
            print("[Step 3/4] Applying per-slice standardization...")

        Standardized = Z_Score_Per_Slice(Smoothed)
    else:
        Standardized = Smoothed

    # Step 4: Global normalization
    if Verbose:
        print(
            f"\n[Step 4/4] Global normalization "
            f"({Clip_Low_Percentile}-{Clip_High_Percentile} percentiles)..."
        )
    T0 = time.time()

    Normalized = Global_Percentile_Normalize(
        Standardized,
        Low_Percentile=Clip_Low_Percentile,
        High_Percentile=Clip_High_Percentile,
        Target_Min=0.0,
        Target_Max=255.0,
    )

    if Verbose:
        print(
            f"[Step 4/4] Done in {time.time()-T0:.1f}s. "
            f"Range: [{Normalized.min():.1f}, {Normalized.max():.1f}]"
        )

    # Diagnostics
    if Verbose:
        print("\n[Diagnostics] Assessing GMM readiness...")

    Readiness = Assess_Gmm_Readiness(Normalized, Exclude_Zero=True)

    if Verbose:
        print(
            f"[Diagnostics] Modes: {Readiness['n_modes']}, "
            f"Skew: {Readiness['skewness']:.2f}, "
            f"Kurt: {Readiness['kurtosis']:.2f}"
        )
        print(f"[Diagnostics] Readiness score: {Readiness['readiness_score']:.2f}")
        print(f"[Diagnostics] {Readiness['recommendation']}")

    Diagnostics = {
        "input_shape": Volume.shape,
        "input_dtype": str(Volume.dtype),
        "background_sigma": Background_Sigma,
        "noise_sigma": Noise_Sigma,
        "stationarity_applied": Need_Standardization,
        "clip_percentiles": (Clip_Low_Percentile, Clip_High_Percentile),
        "readiness": Readiness,
        "output_range": (float(Normalized.min()), float(Normalized.max())),
    }

    return Normalized, Diagnostics
