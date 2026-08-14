"""Global intensity normalization strictly for ROI vectors.

Computes percentile limits explicitly on masked foreground voxels
to prevent background Dirac delta spikes, and applies user-defined
bit-depth quantization.
"""

import numpy as np
from typing import Optional


def Global_Percentile_Normalize_Masked(
    V_Obj: np.ndarray,
    Low_Percentile: float = 0.1,
    High_Percentile: float = 99.9,
    Bit_Depth: int = 32,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Linear scale a 1D feature vector using conditional percentiles.

    Args:
        V_Obj: 1D array of strictly foreground voxels.
        Low_Percentile: Lower clipping percentile.
        High_Percentile: Upper clipping percentile.
        Bit_Depth: Target output bit depth (32 for float, 16 or 8 for int).
        out: Optional output array (in-place when out is V_Obj). Valid
            only if Bit_Depth == 32 to prevent dtype conflicts.

    Returns:
        Normalized 1D array cast to the requested Bit_Depth.

    Raises:
        ValueError: If percentiles are invalid or Bit_Depth is unsupported.
    """
    if Low_Percentile >= High_Percentile:
        raise ValueError(
            f"Low_Percentile ({Low_Percentile}) must be < " f"High_Percentile ({High_Percentile})"
        )

    if Bit_Depth not in (8, 16, 32):
        raise ValueError(f"Bit_Depth must be 8, 16, or 32, got {Bit_Depth}")

    # Ensure float32 for continuous math
    V_Float = V_Obj.astype(np.float32, copy=False)

    # Compute percentiles ONLY on the foreground object
    P_Low, P_High = np.percentile(V_Float, [Low_Percentile, High_Percentile])

    if out is None:
        out = np.empty_like(V_Float, dtype=np.float32)
    elif out.shape != V_Obj.shape:
        raise ValueError(f"out shape {out.shape} != V_Obj shape {V_Obj.shape}")

    if P_High <= P_Low:
        out.fill(0.0)
        return out

    # Continuous scaling to [0.0, 1.0] range
    np.clip(V_Float, P_Low, P_High, out=out)
    out -= P_Low
    out /= P_High - P_Low

    # Apply quantization based on user selection
    if Bit_Depth == 32:
        return out

    if Bit_Depth == 16:
        out *= 65535.0
        np.round(out, out=out)
        return out.astype(np.uint16, copy=False)

    if Bit_Depth == 8:
        out *= 255.0
        np.round(out, out=out)
        return out.astype(np.uint8, copy=False)
