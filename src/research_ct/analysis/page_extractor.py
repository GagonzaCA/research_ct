"""Page surface extraction from segmented volumes.

Placeholder for future geometric analysis (Charles' approach).
"""

import numpy as np
from typing import List, Optional


def Extract_Page_Surfaces(
    Labels: np.ndarray,
    Page_Class: int = 1,
) -> List[np.ndarray]:
    """Extract binary masks for each connected page surface.
    
    Args:
        Labels: Segmented volume (D, H, W).
        Page_Class: Integer label for paper material.
    
    Returns:
        List of binary masks, one per connected page component.
    """
    from scipy import ndimage
    
    Page_Mask = (Labels == Page_Class).astype(np.int32)
    
    # Label connected components in 3D
    Labeled, Num_Features = ndimage.label(Page_Mask)
    
    Masks = []
    for I in range(1, Num_Features + 1):
        Mask = (Labeled == I)
        if Mask.sum() > 100:  # Filter small noise
            Masks.append(Mask)
    
    return Masks


def Get_Page_Centroids(
    Masks: List[np.ndarray],
) -> List[tuple]:
    """Compute centroids of page masks.
    
    Args:
        Masks: List of binary page masks.
    
    Returns:
        List of (z, y, x) centroid tuples.
    """
    Centroids = []
    for Mask in Masks:
        Indices = np.where(Mask)
        Centroid = tuple(np.mean(Indices[i]) for i in range(3))
        Centroids.append(Centroid)
    
    return Centroids