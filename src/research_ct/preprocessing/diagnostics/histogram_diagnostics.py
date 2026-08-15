"""Histogram validation tools for assessing preprocessing quality.

Provides diagnostic functions to verify that preprocessed data
has Gaussian-mixture-friendly histograms before GMM fitting.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from scipy.stats import skew, kurtosis


def Compute_Histogram_Statistics(
    Volume: np.ndarray,
    N_Bins: int = 256,
    Range: Optional[Tuple[float, float]] = None,
) -> Dict[str, any]:
    """Compute descriptive statistics of volume histogram.

    Args:
        Volume: Input 3D array.
        N_Bins: Number of histogram bins.
        Range: Optional (min, max) for histogram range.

    Returns:
        Dictionary with histogram data and statistics.
    """
    Flat = Volume.ravel()

    if Range is None:
        Range = (Flat.min(), Flat.max())

    Hist, Bin_Edges = np.histogram(Flat, bins=N_Bins, range=Range, density=True)
    Bin_Centers = (Bin_Edges[:-1] + Bin_Edges[1:]) / 2

    # Statistics
    Stats = {
        "histogram": Hist,
        "bin_centers": Bin_Centers,
        "bin_edges": Bin_Edges,
        "mean": float(Flat.mean()),
        "std": float(Flat.std()),
        "skewness": float(skew(Flat)),
        "kurtosis": float(kurtosis(Flat)),
        "min": float(Flat.min()),
        "max": float(Flat.max()),
        "n_voxels": int(Flat.size),
    }

    return Stats


def Count_Visible_Modes(
    Histogram: np.ndarray,
    Min_Prominence: float = 0.01,
    Min_Distance: int = 5,
) -> int:
    """Count number of visible modes (peaks) in histogram.

    Uses simple peak detection on smoothed histogram.

    Args:
        Histogram: 1D histogram array.
        Min_Prominence: Minimum relative peak height.
        Min_Distance: Minimum bins between peaks.

    Returns:
        Estimated number of modes.
    """
    from scipy.signal import find_peaks

    # Smooth histogram
    from scipy.ndimage import gaussian_filter1d

    Smoothed = gaussian_filter1d(Histogram, sigma=2)

    # Normalize
    Smoothed = Smoothed / Smoothed.max()

    # Find peaks
    Peaks, Properties = find_peaks(
        Smoothed,
        prominence=Min_Prominence,
        distance=Min_Distance,
    )

    return len(Peaks)


def Assess_Gmm_Readiness(
    Volume: np.ndarray,
    Exclude_Zero: bool = True,
) -> Dict[str, any]:
    """Assess whether volume histogram is suitable for GMM fitting.

    Performs multiple diagnostic checks and returns a readiness report.

    Args:
        Volume: Input 3D array.
        Exclude_Zero: If True, exclude zero-intensity voxels (air)
            from histogram analysis.

    Returns:
        Dictionary with diagnostic results.
    """
    # Prepare data
    Flat = Volume.ravel().astype(np.float64)

    if Exclude_Zero:
        Flat = Flat[Flat > 0]

    # Basic stats
    Stats = Compute_Histogram_Statistics(Flat)

    # Mode count
    N_Modes = Count_Visible_Modes(Stats["histogram"])

    # Symmetry check (Gaussian should have skew ≈ 0, kurtosis ≈ 0)
    Skew = Stats["skewness"]
    Kurt = Stats["kurtosis"]

    # Readiness score
    Score = 0.0

    # At least 2 modes (air + solid minimum)
    if N_Modes >= 2:
        Score += 0.3

    # Not too skewed
    if abs(Skew) < 1.0:
        Score += 0.2

    # Not too kurtotic
    if abs(Kurt) < 2.0:
        Score += 0.2

    # Reasonable dynamic range
    Dynamic_Range = Stats["max"] - Stats["min"]
    if Dynamic_Range > 50:
        Score += 0.3

    Report = {
        "n_modes": N_Modes,
        "skewness": Skew,
        "kurtosis": Kurt,
        "dynamic_range": Dynamic_Range,
        "readiness_score": Score,
        "is_ready": Score >= 0.6,
        "recommendation": _Get_Recommendation(Score, N_Modes, Skew, Kurt),
    }

    return Report


def _Get_Recommendation(
    Score: float,
    N_Modes: int,
    Skew: float,
    Kurt: float,
) -> str:
    """Generate human-readable recommendation."""
    if Score >= 0.8:
        return "Excellent: Histogram is well-suited for GMM fitting."

    if Score >= 0.6:
        return "Good: Proceed with GMM, monitor convergence."

    if N_Modes < 2:
        return "CRITICAL: No clear material separation. Check data quality or consider spatial features."

    if abs(Skew) > 2.0:
        return "WARNING: Highly skewed distribution. Consider log-transform or different preprocessing."

    if abs(Kurt) > 3.0:
        return "WARNING: Heavy tails or outliers. Consider more aggressive clipping."

    return "CAUTION: Marginal histogram quality. Proceed with care, validate results visually."
