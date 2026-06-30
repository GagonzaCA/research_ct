"""
Volume I/O: loading and saving 3D micro-CT data.

Supports TIFF stacks, PNG sequences, and NIfTI. Handles color-to-grayscale
conversion, dtype normalization, and format fallbacks.
"""

import numpy as np
import imageio.v3 as iio
from pathlib import Path
from typing import Union, List, Optional, Callable


Path_Like = Union[str, Path]


def Load_Slice_Stack(
    Folder: Path_Like,
    Pattern: str = "*.tif*",
    Sort_Key: Optional[Callable] = None
) -> np.ndarray:
    """
    Load a directory of image slices into a 3D volume.
    
    Attempts TIFF first, then PNG. Converts color images to grayscale.
    All slices must have the same (H, W) shape.
    
    Args:
        Folder (Path_Like): Directory containing slice images.
        Pattern (str): Glob pattern for selecting files.
        Sort_Key (Optional[Callable]): Function for sorting file names.
            Default: alphabetical.
    
    Returns:
        np.ndarray: Volume of shape (D, H, W), dtype float64.
    
    Raises:
        FileNotFoundError: If no matching files found.
        ValueError: If slices have inconsistent shapes.
    
    Example:
        >>> vol = Load_Slice_Stack("./data/raw", Pattern="reco*.png")
        >>> vol.shape
        (15, 512, 512)
    """
    Folder = Path(Folder)
    
    Files = sorted(Folder.glob(Pattern), key=Sort_Key)
    
    # Fallback patterns
    if not Files:
        for Fallback in ["*.png", "*.jpg", "*.bmp"]:
            Files = sorted(Folder.glob(Fallback), key=Sort_Key)
            if Files:
                break
    
    if not Files:
        Available = list(Folder.iterdir())[:10]
        raise FileNotFoundError(
            f"No images in {Folder} matching '{Pattern}'. "
            f"Found: {[p.name for p in Available]}..."
        )
    
    print(f"[Load_Slice_Stack] {len(Files)} slices from {Folder}")
    
    # Read first slice to determine shape
    First_Slice = iio.imread(Files[0])
    
    if First_Slice.ndim == 3:
        First_Slice = np.mean(First_Slice[..., :3], axis=-1)
    
    Height, Width = First_Slice.shape
    Depth = len(Files)
    
    Volume = np.zeros((Depth, Height, Width), dtype=np.float64)
    Volume[0] = First_Slice.astype(np.float64)
    
    # Read remaining slices
    for Z, File_Path in enumerate(Files[1:], start=1):
        Slice = iio.imread(File_Path)
        
        if Slice.ndim == 3:
            Slice = np.mean(Slice[..., :3], axis=-1)
        
        if Slice.shape != (Height, Width):
            raise ValueError(
                f"Shape mismatch at {File_Path.name}: "
                f"expected {(Height, Width)}, got {Slice.shape}"
            )
        
        Volume[Z] = Slice.astype(np.float64)
    
    print(f"[Load_Slice_Stack] Volume: {Volume.shape}, "
          f"range [{Volume.min():.1f}, {Volume.max():.1f}]")
    
    return Volume


def Save_Volume_As_Stack(
    Volume: np.ndarray,
    Folder: Path_Like,
    Prefix: str = "slice",
    Extension: str = ".tiff"
) -> None:
    """
    Save a 3D volume as individual slice images.
    
    Normalizes to uint8 before saving.
    
    Args:
        Volume (np.ndarray): 3D array of shape (D, H, W).
        Folder (Path_Like): Output directory (created if needed).
        Prefix (str): File name prefix.
        Extension (str): File extension.
    """
    Folder = Path(Folder)
    Folder.mkdir(parents=True, exist_ok=True)
    
    for Z in range(Volume.shape[0]):
        Slice = Volume[Z]
        
        # Normalize to uint8
        if Slice.max() > 255 or Slice.min() < 0 or Slice.dtype != np.uint8:
            Min_Val, Max_Val = Slice.min(), Slice.max()
            if Max_Val == Min_Val:
                Slice_U8 = np.zeros_like(Slice, dtype=np.uint8)
            else:
                Slice_U8 = (
                    (Slice - Min_Val) / (Max_Val - Min_Val) * 255.0
                ).astype(np.uint8)
        else:
            Slice_U8 = Slice.astype(np.uint8)
        
        File_Name = f"{Prefix}_{Z:04d}{Extension}"
        iio.imwrite(Folder / File_Name, Slice_U8)
    
    print(f"[Save_Volume_As_Stack] {Volume.shape[0]} slices → {Folder}")
    
    
