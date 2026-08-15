"""Optimized preprocessing pipeline for GMM segmentation.

Executes domain restriction, structural noise reduction, and
ROI-aware normalization while safely preserving GMM variance assumptions.
"""

import time
import numpy as np

from typing import Tuple, Dict

from .gaussian.roi_masking import Create_Roi_Mask
from .gaussian.noise_reduction import Reduce_Noise_Volume
from .gaussian.global_normalization import Global_Percentile_Normalize_Masked
from .diagnostics.histogram_diagnostics import Assess_Gmm_Readiness


def Preprocess_For_Gmm(
    Volume: np.ndarray,
    Air_Threshold_Percentile: float = 10.0,
    Noise_Sigma: float = 0.8,
    Clip_Low_Percentile: float = 0.1,
    Clip_High_Percentile: float = 99.9,
    Bit_Depth: int = 32,
    Verbose: bool = True,
) -> Tuple[np.ndarray, Dict]:
    """Complete ROI-aware pipeline for GMM segmentation.

    Pipeline:
        1. ROI Masking (Ignore ambient air)
        2. Isotropic Gaussian noise reduction
        3. 1D extraction and continuous percentile normalization
        4. 3D spatial reconstruction

    Args:
        Volume: Raw 3D volume (D, H, W).
        Air_Threshold_Percentile: Noise floor cutoff to exclude air.
        Noise_Sigma: Gaussian sigma for noise reduction (default 0.8).
        Clip_Low_Percentile: Lower percentile computed on ROI only.
        Clip_High_Percentile: Upper percentile computed on ROI only.
        Bit_Depth: Target export depth (32, 16, or 8).
        Verbose: Print progress messages.

    Returns:
        Tuple of (preprocessed_3D_volume, diagnostics_dict).
    """
    if Volume.ndim != 3:
        raise ValueError(f"Expected 3D volume, got shape {Volume.shape}")

    def _vprint(*args, **kwargs):
        if Verbose:
            print(*args, **kwargs)

    _vprint(f"[Preprocess_GMM] Input: {Volume.shape}, Bit Depth: {Bit_Depth}")

    # ── Step 0: Initial allocation ──
    Working = Volume.astype(np.float32, copy=True)

    # ── Step 1: Domain Restriction (ROI Masking) ──
    _vprint(f"\n[Step 1/4] Creating ROI Mask (threshold p={Air_Threshold_Percentile})...")
    t0 = time.time()

    Mask = Create_Roi_Mask(Working, Air_Threshold_Percentile)

    _vprint(f"[Step 1/4] Done in {time.time() - t0:.1f}s.")

    # ── Step 2: Noise reduction (in-place) ──
    _vprint(f"\n[Step 2/4] Noise reduction (sigma={Noise_Sigma})...")
    t0 = time.time()

    Working = Reduce_Noise_Volume(Working, Noise_Sigma, out=Working)

    _vprint(f"[Step 2/4] Done in {time.time() - t0:.1f}s.")

    # ── Step 3: ROI-Aware Normalization ──
    _vprint(
        f"\n[Step 3/4] 1D Extraction and Normalization "
        f"({Clip_Low_Percentile}-{Clip_High_Percentile} percentiles)..."
    )
    t0 = time.time()

    # Extract foreground to 1D vector
    V_Obj = Working[Mask]

    # Normalize and conditionally cast the 1D vector (in-place on float32)
    V_Norm = Global_Percentile_Normalize_Masked(
        V_Obj,
        Low_Percentile=Clip_Low_Percentile,
        High_Percentile=Clip_High_Percentile,
        Bit_Depth=Bit_Depth,
        out=V_Obj if Bit_Depth == 32 else None,
    )

    _vprint(f"[Step 3/4] Done in {time.time() - t0:.1f}s.")

    # ── Step 4: 3D Spatial Reconstruction ──
    _vprint(f"\n[Step 4/4] 3D Tensor Reconstruction...")
    t0 = time.time()

    Output_Volume = np.zeros_like(Working, dtype=V_Norm.dtype)
    Output_Volume[Mask] = V_Norm

    _vprint(f"[Step 4/4] Done in {time.time() - t0:.1f}s.")

    # ── Diagnostics ──
    _vprint("\n[Diagnostics] Assessing GMM readiness...")

    # Exclude absolute zeros assigned to air during reconstruction
    Readiness = Assess_Gmm_Readiness(Output_Volume, Exclude_Zero=False)

    if Verbose:
        print(f"[Diagnostics] Modes: {Readiness['n_modes']}, " f"Skew: {Readiness['skewness']:.2f}")
        print(f"[Diagnostics] {Readiness['recommendation']}")

    Diagnostics = {
        "input_shape": Volume.shape,
        "bit_depth_selected": Bit_Depth,
        "roi_voxels": int(np.sum(Mask)),
        "noise_sigma": Noise_Sigma,
        "clip_percentiles": (Clip_Low_Percentile, Clip_High_Percentile),
        "readiness": Readiness,
    }

    return Output_Volume, Diagnostics
