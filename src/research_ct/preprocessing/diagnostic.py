"""Diagnostic tools: edge strength, page detection, histograms."""

import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from scipy.ndimage import sobel, gaussian_filter1d
from scipy.signal import find_peaks

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def Compute_Edge_Strength(Volume: np.ndarray) -> List[float]:
    """Compute per-slice mean Sobel magnitude.
    
    Text layers produce high edge strength.
    
    Args:
        Volume: 3D array (D, H, W).
    
    Returns:
        List of edge strength scores per slice.
    """
    Scores = []
    for Z in range(Volume.shape[0]):
        Sx = sobel(Volume[Z], axis=0)
        Sy = sobel(Volume[Z], axis=1)
        Scores.append(np.sqrt(Sx**2 + Sy**2).mean())
    
    return Scores


def Find_Book_Bounds(
    Edge_Strength: List[float],
    Threshold_Ratio: float = 0.3,
) -> Tuple[int, int]:
    """Find book interior start/end from edge strength.
    
    Args:
        Edge_Strength: Per-slice scores.
        Threshold_Ratio: Fraction of peak for threshold.
    
    Returns:
        (start_slice, end_slice).
    """
    Es = np.array(Edge_Strength)
    Peak_Val = Es.max()
    Threshold = Es.min() + Threshold_Ratio * (Peak_Val - Es.min())
    
    Above = np.where(Es > Threshold)[0]
    if len(Above) == 0:
        return 0, len(Es) - 1
    
    return int(Above[0]), int(Above[-1])


def Find_Page_Peaks(
    Edge_Strength: List[float],
    Book_Start: int,
    Book_End: int,
    Min_Distance: int = 5,
    Min_Prominence: float = 1.5,
    Smooth_Sigma: float = 0.75,
    Expected_Pages: Optional[int] = None,
) -> List[int]:
    """Find page surfaces as peaks in edge-strength profile.
    
    Args:
        Edge_Strength: Per-slice scores.
        Book_Start: First slice of book interior.
        Book_End: Last slice of book interior.
        Min_Distance: Minimum slices between peaks.
        Min_Prominence: Minimum peak prominence.
        Smooth_Sigma: Gaussian smoothing sigma.
        Expected_Pages: If known, adapt prominence to find this many.
    
    Returns:
        List of slice indices where pages are detected.
    """
    Es_Raw = np.array(Edge_Strength[Book_Start:Book_End + 1], dtype=np.float64)
    
    if Smooth_Sigma > 0 and len(Es_Raw) > 5:
        Es = gaussian_filter1d(Es_Raw, sigma=Smooth_Sigma)
    else:
        Es = Es_Raw
    
    Prominence = Min_Prominence
    Prominence_Floor = 0.2
    Best_Peaks = np.array([], dtype=int)
    
    while Prominence >= Prominence_Floor:
        Peaks, _ = find_peaks(Es, distance=Min_Distance, prominence=Prominence)
        if Expected_Pages is None or len(Peaks) >= Expected_Pages:
            Best_Peaks = Peaks
            break
        Best_Peaks = Peaks
        Prominence -= 0.1
    
    return (Best_Peaks + Book_Start).tolist()


def Diagnose_Volume(
    Volume: np.ndarray,
    Out_Dir: Path,
    Config_Dict: Dict,
    Expected_Pages: Optional[int] = None,
) -> Dict:
    """Run full diagnostic and save plots.
    
    Args:
        Volume: 3D array.
        Out_Dir: Directory for output figures.
        Config_Dict: Preprocessing config values for titles.
        Expected_Pages: Known page count if available.
    
    Returns:
        Dictionary with diagnostics data.
    """
    Out_Dir = Path(Out_Dir)
    Out_Dir.mkdir(parents=True, exist_ok=True)
    D = Volume.shape[0]
    
    # Compute statistics
    Means = [Volume[Z].mean() for Z in range(D)]
    Edge_Strength = Compute_Edge_Strength(Volume)
    
    # Find bounds and peaks
    Book_Start, Book_End = Find_Book_Bounds(Edge_Strength)
    Peaks = Find_Page_Peaks(
        Edge_Strength,
        Book_Start,
        Book_End,
        Config_Dict.get("Page_Peak_Min_Distance", 5),
        Config_Dict.get("Page_Peak_Min_Prominence", 1.5),
        Config_Dict.get("Edge_Smooth_Sigma", 0.75),
        Expected_Pages,
    )
    
    # Console report
    print(f"\n{'Slice':<6} | {'Edge':<12} | {'Mean':<12}")
    print("-" * 35)
    for Z in range(D):
        print(f"{Z:<6} | {Edge_Strength[Z]:<12.2f} | {Means[Z]:<12.2f}")
    
    print(f"\n[diagnose] Book: slices {Book_Start}-{Book_End}")
    print(f"[diagnose] {len(Peaks)} page peaks: {Peaks}")
    
    # Plot edge strength
    Fig, Ax = plt.subplots(figsize=(max(10, D * 0.1), 5))
    Ax.plot(Edge_Strength, "o-", markersize=3, alpha=0.5, label="Raw")
    
    Es_Smooth = gaussian_filter1d(np.array(Edge_Strength), sigma=0.75)
    Ax.plot(Es_Smooth, "-", linewidth=2, label="Smoothed")
    
    Ax.axvline(Book_Start, color="green", linestyle="--", alpha=0.7)
    Ax.axvline(Book_End, color="green", linestyle="--", alpha=0.7)
    for P in Peaks:
        Ax.axvline(P, color="blue", linestyle=":", alpha=0.3)
    
    Ax.set_xlabel("Slice (Z)")
    Ax.set_ylabel("Edge Strength")
    Ax.set_title("Page Surface Detection")
    Ax.legend()
    Ax.grid(True, alpha=0.3)
    
    Fig.savefig(Out_Dir / "edge_strength.png", dpi=150, bbox_inches="tight")
    plt.close(Fig)
    
    # Plot histogram
    Fig, Ax = plt.subplots(figsize=(10, 5))
    Book_Voxels = Volume[Book_Start:Book_End + 1].ravel()
    Ax.hist(Book_Voxels, bins=256, range=(0, 255), density=True, alpha=0.7)
    Ax.set_xlabel("Intensity")
    Ax.set_ylabel("Density")
    Ax.set_title("Intensity Histogram (Book Interior)")
    Ax.grid(True, alpha=0.3)
    
    Fig.savefig(Out_Dir / "histogram.png", dpi=150, bbox_inches="tight")
    plt.close(Fig)
    
    return {
        "means": Means,
        "edge_strength": Edge_Strength,
        "book_start": Book_Start,
        "book_end": Book_End,
        "page_peaks": Peaks,
        "histogram_data": Book_Voxels,
    }