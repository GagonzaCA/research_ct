"""Low-level multi-page TIFF export for Dragonfly.

Saves 3D volumes as ImageJ-compatible multi-page TIFF stacks with
voxel-spacing metadata injected into the TIFF tags so Dragonfly
recognizes them as calibrated 3D images.
"""

import json
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, Union

import tifffile

Path_Like = Union[str, Path]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def Save_Volume_As_Tiff(
    Volume: np.ndarray,
    Output_Path: Path_Like,
    *,
    Voxel_Spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    Spacing_Units: str = "um",
    Compression: Optional[str] = None,
    Big_Tiff: Optional[bool] = None,
    Big_Tiff_Threshold_Bytes: int = 2 * 1024**3,
) -> Path:
    """Save a 3D volume as an ImageJ-style multi-page TIFF stack.

    Each Z-slice is written as one page.  Voxel spacing is stored in
    the XResolution / YResolution tags (converted to pixels/cm) and in
    an ImageJ metadata string so that Dragonfly auto-calibrates the
    image on import.

    Args:
        Volume: 3-D array (Z, Y, X).  May be a memmap; slices are fetched
            one at a time to avoid full materialisation.
        Output_Path: Destination ``.tif`` file path.
        Voxel_Spacing: (Z_spacing, Y_spacing, X_spacing) in *Spacing_Units*.
        Spacing_Units: Label for the spacing unit (``"um"``, ``"mm"``).
        Compression: Pass-through to ``tifffile.TiffWriter.write``
            (``None``, ``"zlib"``, ``"lzma"``, …).  None = uncompressed.
        Big_Tiff: Force BigTIFF mode.  If *None*, auto-detect from
            *Big_Tiff_Threshold_Bytes*.
        Big_Tiff_Threshold_Bytes: When the projected file size exceeds
            this threshold (and *Big_Tiff* is None), BigTIFF is enabled
            automatically.

    Returns:
        *Output_Path* as a ``Path``.
    """
    Output_Path = Path(Output_Path)
    Output_Path.parent.mkdir(parents=True, exist_ok=True)

    D, H, W = Volume.shape[:3]
    Z_Spacing, Y_Spacing, X_Spacing = Voxel_Spacing

    # --- ImageJ resolution: pixels per cm ----------------------------------
    # tifffile `imagej=True` expects (x_res, y_res) in px/cm.
    # 1 um pixel -> 10 000 px/cm; 1 mm pixel -> 10 px/cm
    Unit_To_Cm: Dict[str, float] = {
        "um": 1e4,
        "mm": 10.0,
        "cm": 1.0,
    }
    Scale = Unit_To_Cm.get(Spacing_Units.lower(), 1e4)
    Res_X = Scale / X_Spacing if X_Spacing > 0 else 1.0
    Res_Y = Scale / Y_Spacing if Y_Spacing > 0 else 1.0

    ImageJ_Meta: Dict[str, object] = {
        "spacing": Z_Spacing,
        "unit": Spacing_Units,
        "axes": "ZYX",
    }

    # ---- BigTIFF auto-detection -------------------------------------------
    if Big_Tiff is None:
        Est_Bytes = int(D) * int(H) * int(W) * np.dtype(Volume.dtype).itemsize
        Big_Tiff = Est_Bytes > Big_Tiff_Threshold_Bytes

    # ---- Write ------------------------------------------------------------
    with tifffile.TiffWriter(Output_Path, bigtiff=Big_Tiff, imagej=True) as Writer:
        Writer.write(
            Volume,
            resolution=(Res_X, Res_Y),
            resolutionunit=tifffile.RESUNIT.CENTIMETER,
            metadata=ImageJ_Meta,
            compression=Compression,
        )

    print(
        f"[DragonflyExport] Saved -> {Output_Path}  "
        f"({D}x{H}x{W}, {Volume.dtype}, bigtiff={Big_Tiff})"
    )
    return Output_Path


def Verify_Dragonfly_Channels(
    Channel_Paths: Dict[str, Path],
    *,
    Expected_Shape: Optional[Tuple[int, int, int]] = None,
) -> Dict[str, str]:
    """Quick integrity check on exported TIFF stacks.

    Opens the first page of each file and reports dimensions vs
    expected shape.

    Args:
        Channel_Paths: Dict ``{"grayscale": Path(...), "labels": ..., ...}``.
        Expected_Shape: Expected ``(Z, Y, X)``.  If None, shape is
            inferred from the first channel and all others must match.

    Returns:
        Dict mapping channel name to ``"OK"`` or an error message.
    """
    Status: Dict[str, str] = {}
    Ref_Shape: Optional[Tuple[int, int, int]] = Expected_Shape

    for Name, Path in Channel_Paths.items():
        if not Path.exists():
            Status[Name] = f"MISSING ({Path})"
            continue

        try:
            with tifffile.TiffFile(Path) as Tiff:
                Pages = len(Tiff.pages)
                if Pages == 0:
                    Status[Name] = "EMPTY"
                    continue
                H, W = Tiff.pages[0].shape

            Shape = (Pages, H, W)
            if Ref_Shape is None:
                Ref_Shape = Shape
            if Shape != Ref_Shape:
                Status[Name] = (
                    f"SHAPE MISMATCH: got {Shape}, expected {Ref_Shape}"
                )
            else:
                Status[Name] = "OK"
        except Exception as Exc:
            Status[Name] = f"ERROR: {Exc}"

    return Status


# ---------------------------------------------------------------------------
# Sidecar helpers
# ---------------------------------------------------------------------------


def Save_Dragonfly_Metadata_Json(
    Output_Path: Path_Like,
    Shape: Tuple[int, int, int],
    Voxel_Spacing: Tuple[float, float, float],
    Spacing_Units: str = "um",
    Channels: Optional[Dict[str, Dict[str, object]]] = None,
    Label_Colors: Optional[Dict[int, Tuple[int, int, int]]] = None,
    Label_Names: Optional[Dict[int, str]] = None,
) -> Path:
    """Write a human-readable JSON sidecar with acquisition metadata.

    Args:
        Output_Path: Destination ``.json`` path.
        Shape: Volume shape ``(Z, Y, X)``.
        Voxel_Spacing: ``(Z, Y, X)`` spacing in *Spacing_Units*.
        Spacing_Units: Unit label (``"um"``, ``"mm"``).
        Channels: Optional dict of channel metadata keyed by channel name.
        Label_Colors: Optional ``{label_id: (R, G, B)}``.
        Label_Names: Optional ``{label_id: "name"}``.

    Returns:
        *Output_Path* as ``Path``.
    """
    Output_Path = Path(Output_Path)
    Output_Path.parent.mkdir(parents=True, exist_ok=True)

    Doc: Dict[str, object] = {
        "shape": list(Shape),
        "voxel_spacing": {
            "z": Voxel_Spacing[0],
            "y": Voxel_Spacing[1],
            "x": Voxel_Spacing[2],
        },
        "spacing_units": Spacing_Units,
    }
    if Channels is not None:
        Doc["channels"] = Channels
    if Label_Colors is not None:
        Doc["label_colors"] = {
            str(K): list(V) for K, V in Label_Colors.items()
        }
    if Label_Names is not None:
        Doc["label_names"] = {str(K): V for K, V in Label_Names.items()}

    with open(Output_Path, "w", encoding="utf-8") as Fh:
        json.dump(Doc, Fh, indent=2, ensure_ascii=False)

    print(f"[DragonflyExport] Metadata -> {Output_Path}")
    return Output_Path


def Save_Label_Colors_Csv(
    Output_Path: Path_Like,
    Label_Colors: Dict[int, Tuple[int, int, int]],
    Label_Names: Optional[Dict[int, str]] = None,
) -> Path:
    """Write a CSV mapping ``label_id -> (R, G, B, Name)``.

    Dragonfly can import this CSV to colour-code segmentations.

    Args:
        Output_Path: Destination ``.csv`` path.
        Label_Colors: ``{label_id: (R, G, B)}`` with values 0-255.
        Label_Names: Optional ``{label_id: "name"}``.

    Returns:
        *Output_Path* as ``Path``.
    """
    import csv

    Output_Path = Path(Output_Path)
    Output_Path.parent.mkdir(parents=True, exist_ok=True)

    with open(Output_Path, "w", newline="", encoding="utf-8") as Fh:
        Writer = csv.writer(Fh)
        Writer.writerow(["Label_ID", "R", "G", "B", "Name"])

        for Lab_Id in sorted(Label_Colors.keys()):
            R, G, B = Label_Colors[Lab_Id]
            Name = (
                Label_Names.get(Lab_Id, f"Class_{Lab_Id}")
                if Label_Names
                else f"Class_{Lab_Id}"
            )
            Writer.writerow([Lab_Id, R, G, B, Name])

    print(f"[DragonflyExport] Label colours -> {Output_Path}")
    return Output_Path