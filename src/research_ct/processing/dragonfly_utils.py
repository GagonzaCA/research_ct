"""High-level Dragonfly export orchestration.

Thin wrapper around ``research_ct.io.dragonfly_exporter`` that
produces a self-describing directory with three TIFF stacks, a
metadata JSON, and a label-colour CSV — everything needed to drop
into Dragonfly for 3D inspection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import numpy as np

from research_ct.io.dragonfly_exporter import (
    Save_Label_Colors_Csv,
    Save_Dragonfly_Metadata_Json,
    Save_Volume_As_Tiff,
)

Path_Like = Union[str, Path]

# ---------------------------------------------------------------------------
# Default material palette (background, paper, ink, cover)
# ---------------------------------------------------------------------------

_DEFAULT_COLORS: Dict[int, Tuple[int, int, int]] = {
    0: (0, 0, 0),
    1: (255, 228, 181),
    2: (47, 79, 79),
    3: (139, 69, 19),
}

_DEFAULT_NAMES: Dict[int, str] = {
    0: "Background",
    1: "Paper",
    2: "Ink",
    3: "Cover",
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass
class Dragonfly_Export_Config:
    """Parameters for a Dragonfly export batch."""

    Output_Dir: Path
    """Directory that will contain all exported files."""

    Voxel_Spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    """(Z, Y, X) spacing in *Spacing_Units*."""

    Spacing_Units: str = "um"
    """Unit label (``"um"``, ``"mm"``, ``"cm"``)."""

    Label_Colors: Dict[int, Tuple[int, int, int]] = field(default_factory=lambda: dict(_DEFAULT_COLORS))
    """``{class_id: (R, G, B)}`` mapping, 0-255 per channel."""

    Label_Names: Dict[int, str] = field(default_factory=lambda: dict(_DEFAULT_NAMES))
    """``{class_id: "name"}`` mapping."""

    Compression: Optional[str] = None
    """TIFF compression (None = uncompressed)."""


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def Export_Dragonfly_Channels(
    Processed: np.ndarray,
    Labels: np.ndarray,
    Entropy: np.ndarray,
    Config: Dragonfly_Export_Config,
    *,
    Prefix: str = "dragonfly",
    Big_Tiff: Optional[bool] = None,
) -> Dict[str, Path]:
    """Export the three analysis channels as Dragonfly-compatible TIFF stacks.

    Creates the following files inside ``Config.Output_Dir``:

    * ``{Prefix}_grayscale.tif`` — preprocessed intensity volume
    * ``{Prefix}_labels.tif`` — RGB label volume with user-defined colours
    * ``{Prefix}_entropy.tif`` — entropy (uncertainty) heatmap
    * ``{Prefix}_metadata.json`` — shape, spacing, and class metadata
    * ``{Prefix}_label_colors.csv`` — Dragonfly material colour table

    All writes stream slice-by-slice to keep memory bounded for large
    memmap-backed arrays.

    Args:
        Processed: ``(D, H, W)`` grayscale volume (float or int).
        Labels: ``(D, H, W)`` integer labels.
        Entropy: ``(D, H, W)`` entropy map.
        Config: Export parameters.
        Prefix: Basename prefix for written files.
        Big_Tiff: If True, force BigTIFF.  If None, auto-detect.

    Returns:
        Dict mapping channel name (``"grayscale"``, ``"labels"``, ``"entropy"``)
        to the written ``Path``.
    """
    Output_Dir = Path(Config.Output_Dir)
    Output_Dir.mkdir(parents=True, exist_ok=True)

    # ---- Sidecar files -------------------------------------------------
    Save_Dragonfly_Metadata_Json(
        Output_Dir / f"{Prefix}_metadata.json",
        Shape=Processed.shape[:3],
        Voxel_Spacing=Config.Voxel_Spacing,
        Spacing_Units=Config.Spacing_Units,
        Channels={
            "grayscale": {"dtype": str(Processed.dtype)},
            "labels": {"dtype": "uint16", "num_classes": len(Config.Label_Colors)},
            "entropy": {"dtype": "float32"},
        },
        Label_Colors=Config.Label_Colors,
        Label_Names=Config.Label_Names,
    )
    Save_Label_Colors_Csv(
        Output_Dir / f"{Prefix}_label_colors.csv",
        Label_Colors=Config.Label_Colors,
        Label_Names=Config.Label_Names,
    )

    # ---- Channel TIFFs -------------------------------------------------
    Grayscale_Path = Save_Volume_As_Tiff(
        Processed,
        Output_Dir / f"{Prefix}_grayscale.tif",
        Voxel_Spacing=Config.Voxel_Spacing,
        Spacing_Units=Config.Spacing_Units,
        Compression=Config.Compression,
        Big_Tiff=Big_Tiff,
    )

    # ── Label TIFF (single-channel uint16 — Dragonfly reads the CSV for colours)
    Labels_Path = Save_Volume_As_Tiff(
        Labels.astype(np.uint16, copy=False),
        Output_Dir / f"{Prefix}_labels.tif",
        Voxel_Spacing=Config.Voxel_Spacing,
        Spacing_Units=Config.Spacing_Units,
        Compression=Config.Compression,
        Big_Tiff=Big_Tiff,
    )

    Entropy_Path = Save_Volume_As_Tiff(
        Entropy.astype(np.float32, copy=False),
        Output_Dir / f"{Prefix}_entropy.tif",
        Voxel_Spacing=Config.Voxel_Spacing,
        Spacing_Units=Config.Spacing_Units,
        Compression=Config.Compression,
        Big_Tiff=Big_Tiff,
    )

    Paths: Dict[str, Path] = {
        "grayscale": Grayscale_Path,
        "labels": Labels_Path,
        "entropy": Entropy_Path,
    }

    print(f"[DragonflyExport] {len(Paths)} channels written -> {Output_Dir}")
    return Paths