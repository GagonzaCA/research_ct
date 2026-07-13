"""Diagnostic histogram visualization for preprocessing validation."""

import numpy as np
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for headless environments
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, Optional
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks


# Cell: Plot before/after histograms (excluding zero intensities)


def Plot_Histogram_Comparison(
    Raw_Volume: np.ndarray,
    Processed_Volume: np.ndarray,
    Output_Path: Path,
    N_Bins: int = 256,
    Exclude_Zero: bool = True,
    Focus_Range: Optional[Tuple[float, float]] = None,
) -> None:
    """Plot histograms of raw and preprocessed volumes side by side.

    Excludes zero-intensity voxels (air) to focus on material
    distributions. Optionally zooms into a specific intensity range.

    Args:
        Raw_Volume: Raw 3D volume.
        Processed_Volume: Preprocessed 3D volume.
        Output_Path: Where to save the figure.
        N_Bins: Number of histogram bins.
        Exclude_Zero: If True, exclude voxels with intensity <= 0.
        Focus_Range: Optional (min, max) to zoom x-axis.
    """
    # Prepare data
    Raw_Flat = Raw_Volume.ravel().astype(np.float64)
    Proc_Flat = Processed_Volume.ravel().astype(np.float64)

    if Exclude_Zero:
        Raw_Flat = Raw_Flat[Raw_Flat > 0]
        Proc_Flat = Proc_Flat[Proc_Flat > 0]
        Title_Suffix = " (Air Excluded)"
    else:
        Title_Suffix = " (All Voxels)"

    # Compute histograms
    Raw_Hist, Raw_Bins = np.histogram(Raw_Flat, bins=N_Bins, density=True)
    Proc_Hist, Proc_Bins = np.histogram(Proc_Flat, bins=N_Bins, density=True)

    Raw_Centers = (Raw_Bins[:-1] + Raw_Bins[1:]) / 2
    Proc_Centers = (Proc_Bins[:-1] + Proc_Bins[1:]) / 2

    # Create figure
    Fig, Axes = plt.subplots(2, 2, figsize=(14, 10))
    Fig.suptitle(
        f"Histogram Comparison: Raw vs. Preprocessed{Title_Suffix}", fontsize=14, fontweight="bold"
    )

    # --- Top Left: Raw histogram (full range) ---
    Ax = Axes[0, 0]
    Ax.fill_between(Raw_Centers, Raw_Hist, alpha=0.6, color="steelblue", label="Raw")
    Ax.set_xlabel("Intensity")
    Ax.set_ylabel("Density")
    Ax.set_title(f"Raw Volume{Title_Suffix}")
    Ax.grid(True, alpha=0.3)
    Ax.legend()

    # Add statistics text
    Raw_Stats = (
        f"Mean: {Raw_Flat.mean():.1f}\n"
        f"Std: {Raw_Flat.std():.1f}\n"
        f"Min: {Raw_Flat.min():.1f}\n"
        f"Max: {Raw_Flat.max():.1f}\n"
        f"N: {len(Raw_Flat):,}"
    )
    Ax.text(
        0.97,
        0.97,
        Raw_Stats,
        transform=Ax.transAxes,
        fontsize=9,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    # --- Top Right: Preprocessed histogram (full range) ---
    Ax = Axes[0, 1]
    Ax.fill_between(Proc_Centers, Proc_Hist, alpha=0.6, color="forestgreen", label="Preprocessed")
    Ax.set_xlabel("Intensity")
    Ax.set_ylabel("Density")
    Ax.set_title(f"Preprocessed Volume{Title_Suffix}")
    Ax.grid(True, alpha=0.3)
    Ax.legend()

    # Add statistics text
    Proc_Stats = (
        f"Mean: {Proc_Flat.mean():.1f}\n"
        f"Std: {Proc_Flat.std():.1f}\n"
        f"Min: {Proc_Flat.min():.1f}\n"
        f"Max: {Proc_Flat.max():.1f}\n"
        f"N: {len(Proc_Flat):,}"
    )
    Ax.text(
        0.97,
        0.97,
        Proc_Stats,
        transform=Ax.transAxes,
        fontsize=9,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.5),
    )

    # --- Bottom Left: Overlay comparison ---
    Ax = Axes[1, 0]
    Ax.fill_between(Raw_Centers, Raw_Hist, alpha=0.4, color="steelblue", label="Raw")
    Ax.fill_between(Proc_Centers, Proc_Hist, alpha=0.4, color="forestgreen", label="Preprocessed")
    Ax.set_xlabel("Intensity")
    Ax.set_ylabel("Density")
    Ax.set_title("Overlay Comparison")
    Ax.grid(True, alpha=0.3)
    Ax.legend()

    # --- Bottom Right: Zoomed view (material region) ---
    Ax = Axes[1, 1]

    # Determine zoom range from processed data (materials, not air)
    if Focus_Range is not None:
        Zoom_Min, Zoom_Max = Focus_Range
    else:
        # Auto-zoom: exclude bottom 5% and top 1% of non-zero processed data
        Zoom_Min = np.percentile(Proc_Flat, 5)
        Zoom_Max = np.percentile(Proc_Flat, 99)

    # Filter histograms to zoom range
    Raw_Mask = (Raw_Centers >= Zoom_Min) & (Raw_Centers <= Zoom_Max)
    Proc_Mask = (Proc_Centers >= Zoom_Min) & (Proc_Centers <= Zoom_Max)

    Ax.fill_between(
        Raw_Centers[Raw_Mask], Raw_Hist[Raw_Mask], alpha=0.5, color="steelblue", label="Raw"
    )
    Ax.fill_between(
        Proc_Centers[Proc_Mask],
        Proc_Hist[Proc_Mask],
        alpha=0.5,
        color="forestgreen",
        label="Preprocessed",
    )
    Ax.set_xlabel("Intensity")
    Ax.set_ylabel("Density")
    Ax.set_title(f"Zoomed: [{Zoom_Min:.1f}, {Zoom_Max:.1f}]")
    Ax.grid(True, alpha=0.3)
    Ax.legend()



    Proc_Smooth = gaussian_filter1d(Proc_Hist, sigma=2)
    Proc_Smooth = Proc_Smooth / Proc_Smooth.max()
    Peaks, _ = find_peaks(Proc_Smooth[Proc_Mask], prominence=0.02, distance=5)

    Ax.text(
        0.03,
        0.97,
        f"Visible modes: {len(Peaks)}",
        transform=Ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.7),
    )

    # Mark detected peaks
    for Peak in Peaks:
        Proc_Zoom_Centers = Proc_Centers[Proc_Mask]
        if Peak < len(Proc_Zoom_Centers):
            Ax.axvline(Proc_Zoom_Centers[Peak], color="red", linestyle="--", alpha=0.5, linewidth=1)

    plt.tight_layout()
    Fig.savefig(Output_Path, dpi=150, bbox_inches="tight")
    plt.close(Fig)

    print(f"[Plot_Histogram_Comparison] Saved → {Output_Path}")




def Plot_Slice_Histograms(
    Volume: np.ndarray,
    Output_Path: Path,
    N_Slices: int = 5,
    Exclude_Zero: bool = True,
) -> None:
    """Plot histograms for multiple slices to check stationarity.

    Args:
        Volume: 3D volume.
        Output_Path: Save path.
        N_Slices: Number of slices to sample.
        Exclude_Zero: Exclude air voxels.
    """
    D = Volume.shape[0]
    Slice_Indices = np.linspace(0, D - 1, N_Slices, dtype=int)

    Fig, Ax = plt.subplots(figsize=(12, 6))

    Colors = plt.cm.viridis(np.linspace(0, 1, N_Slices))

    for Idx, Z in enumerate(Slice_Indices):
        Slice = Volume[Z].ravel().astype(np.float64)

        if Exclude_Zero:
            Slice = Slice[Slice > 0]

        Hist, Bins = np.histogram(Slice, bins=128, density=True)
        Centers = (Bins[:-1] + Bins[1:]) / 2

        Ax.plot(Centers, Hist, color=Colors[Idx], alpha=0.7, label=f"Slice {Z}", linewidth=2)

    Ax.set_xlabel("Intensity")
    Ax.set_ylabel("Density")
    Ax.set_title("Per-Slice Histograms (Air Excluded)")
    Ax.grid(True, alpha=0.3)
    Ax.legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    Fig.savefig(Output_Path, dpi=150, bbox_inches="tight")
    plt.close(Fig)

    print(f"[Plot_Slice_Histograms] Saved → {Output_Path}")



