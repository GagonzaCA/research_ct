"""Metadata extraction from TIFF stacks and manual inference."""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional, Dict
import numpy as np


@dataclass
class Scan_Metadata:
    """Inferred metadata from TIFF volume analysis.
    
    Since raw TIFFs have no equipment metadata, all values are
    inferred from pixel statistics or set to defaults.
    
    Attributes:
        Voxel_Size_Um: Default (1, 1, 1) unless calibrated.
        Volume_Shape: (D, H, W) from array.
        Bit_Depth: From dtype (8, 16, 32).
        Intensity_Range: (min, max) from actual data.
        Scanner_Model: "Unknown" (no equipment metadata).
        Num_Pages: None (must be set manually if known).
    """
    
    Voxel_Size_Um: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    Volume_Shape: Tuple[int, int, int] = (0, 0, 0)
    Bit_Depth: int = 16
    Intensity_Range: Tuple[float, float] = (0.0, 65535.0)
    Scanner_Model: str = "Unknown"
    Num_Pages: Optional[int] = None
    Page_Thickness_Voxels: Optional[int] = None
    Raw_Metadata: Optional[Dict] = None


def Load_Metadata(
    Volume: np.ndarray,
    Voxel_Size_Um: Optional[float] = None,
    Num_Pages: Optional[int] = None,
) -> Scan_Metadata:
    """Infer metadata from a loaded numpy volume.
    
    This is the primary entry point when no external metadata exists.
    All values are derived from array properties.
    
    Args:
        Volume: Loaded 3D volume.
        Voxel_Size_Um: Voxel size if known from calibration.
        Num_Pages: Expected page count if known.
    
    Returns:
        Scan_Metadata with inferred values.
    """
    D, H, W = Volume.shape
    
    # Bit depth from dtype
    if Volume.dtype == np.uint8:
        Bit_Depth = 8
    elif Volume.dtype == np.uint16:
        Bit_Depth = 16
    elif Volume.dtype == np.uint32:
        Bit_Depth = 32
    else:
        Bit_Depth = Volume.dtype.itemsize * 8
    
    # Intensity range from actual data
    Intensity_Min = float(Volume.min())
    Intensity_Max = float(Volume.max())
    
    # Theoretical max for integer types
    if np.issubdtype(Volume.dtype, np.integer):
        Theoretical_Max = float(2**Bit_Depth - 1)
        Intensity_Max = max(Intensity_Max, Theoretical_Max)
    
    Metadata = Scan_Metadata(
        Voxel_Size_Um=(Voxel_Size_Um or 1.0,) * 3,
        Volume_Shape=(D, H, W),
        Bit_Depth=Bit_Depth,
        Intensity_Range=(Intensity_Min, Intensity_Max),
        Num_Pages=Num_Pages,
        Raw_Metadata={
            "inferred": True,
            "dtype": str(Volume.dtype),
            "actual_data_range": (float(Volume.min()), float(Volume.max())),
        },
    )
    
    print(f"[Load_Metadata] Inferred: shape={Metadata.Volume_Shape}, "
          f"bit_depth={Metadata.Bit_Depth}, range={Metadata.Intensity_Range}")
    
    return Metadata