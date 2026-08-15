"""Domain restriction tools for micro-CT data.

Generates logical masks to separate physical objects from ambient
background noise, ensuring statistical bounds are not distorted by air.
"""

import numpy as np


def Create_Roi_Mask(
    Volume: np.ndarray,
    Threshold_Percentile: float = 10.0,
) -> np.ndarray:
    """Create a boolean mask isolating foreground from background.

    Computes a noise floor threshold based on the specified percentile
    and returns a binary mask where True represents the object.

    Args:
        Volume: 3D array, shape (D, H, W).
        Threshold_Percentile: Percentile of intensity to use as the
            air-to-object cutoff.

    Returns:
        Boolean mask array of the same shape as Volume.
    """
    Threshold = np.percentile(Volume, Threshold_Percentile)
    Mask = Volume > Threshold

    return Mask
