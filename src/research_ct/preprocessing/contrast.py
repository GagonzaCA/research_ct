"""
Contrast enhancement: white top-hat filtering and CLAHE.

White top-hat isolates small bright features (ink) from large-scale
intensity gradients. CLAHE provides local contrast enhancement without
amplifying noise in homogeneous regions.
"""

import numpy as np
from skimage import exposure
from skimage.morphology import white_tophat

try:
    from skimage.morphology import disk
except ImportError:
    from skimage.morphology.footprints import disk

from typing import Tuple


def Apply_White_Tophat(
    Image: np.ndarray,
    Radius: int
) -> np.ndarray:
    """
    Apply white top-hat morphological transform.
    
    Isolates small bright regions by subtracting the morphological opening
    from the original image. Effective for enhancing ink strokes against
    uneven paper background.
    
    Args:
        Image (np.ndarray): 2D grayscale image, any numeric dtype.
        Radius (int): Radius of disk-shaped structuring element.
    
    Returns:
        np.ndarray: Filtered image, same shape as input, float64.
    
    Example:
        >>> import numpy as np
        >>> img = np.random.rand(100, 100)
        >>> filtered = Apply_White_Tophat(img, Radius=7)
        >>> filtered.shape
        (100, 100)
    """
    Structuring_Element = disk(Radius)
    
    # Pad to avoid boundary artifacts from morphology
    Pad_Width = Radius * 2
    Padded = np.pad(Image, Pad_Width, mode="reflect")
    
    Result = white_tophat(Padded, footprint=Structuring_Element)
    
    # Remove padding
    return Result[
        Pad_Width:-Pad_Width,
        Pad_Width:-Pad_Width
    ].astype(np.float64)


def Apply_Clahe(
    Image: np.ndarray,
    Kernel_Size: Tuple[int, int],
    Clip_Limit: float
) -> np.ndarray:
    """
    Apply Contrast Limited Adaptive Histogram Equalization.
    
    Operates on local tiles to enhance contrast without over-amplifying
    noise. Output is float64 in range [0, 255].
    
    Args:
        Image (np.ndarray): 2D image. If not in [0,1], normalized first.
        Kernel_Size (Tuple[int, int]): Number of tiles in (rows, cols).
        Clip_Limit (float): Clipping limit for histogram bins.
    
    Returns:
        np.ndarray: Equalized image, float64, range [0, 255].
    """
    # Normalize to [0, 1] for skimage
    Min_Val = Image.min()
    Max_Val = Image.max()
    
    if Max_Val == Min_Val:
        return np.zeros_like(Image, dtype=np.float64)
    
    Normalized = (Image - Min_Val) / (Max_Val - Min_Val)
    
    Equalized = exposure.equalize_adapthist(
        Normalized,
        kernel_size=Kernel_Size,
        clip_limit=Clip_Limit
    )
    
    # Return to [0, 255]
    return (Equalized * 255.0).astype(np.float64)


def Saturate_Percentiles(
    Image: np.ndarray,
    Low_Percentile: float,
    High_Percentile: float
) -> np.ndarray:
    """
    Clip intensities at percentiles and rescale to full range.
    
    Suppresses outlier pixels (extreme dark/bright) that would otherwise
    compress the dynamic range of the image.
    
    Args:
        Image (np.ndarray): Input image.
        Low_Percentile (float): Lower clipping percentile (0-100).
        High_Percentile (float): Upper clipping percentile (0-100).
    
    Returns:
        np.ndarray: Rescaled image, float64, range [0, 255].
    
    Raises:
        ValueError: If percentiles are invalid or equal.
    """
    if not (0 <= Low_Percentile < High_Percentile <= 100):
        raise ValueError(
            f"Invalid percentiles: {Low_Percentile}, {High_Percentile}. "
            "Must satisfy 0 <= low < high <= 100."
        )
    
    Low, High = np.percentile(Image, [Low_Percentile, High_Percentile])
    
    if Low == High:
        return np.zeros_like(Image, dtype=np.float64)
    
    Clipped = np.clip(Image, Low, High)
    Rescaled = (Clipped - Low) / (High - Low) * 255.0
    
    return Rescaled.astype(np.float64)


def Enhance_Slice_Contrast(
    Image: np.ndarray,
    Radius: int,
    Clahe_Kernel: Tuple[int, int],
    Clahe_Clip: float,
    Saturation_Percentiles: Tuple[float, float]
) -> np.ndarray:
    """
    Full contrast enhancement pipeline for a single slice.
    
    Sequence: white top-hat -> CLAHE -> percentile saturation.
    
    Args:
        Image (np.ndarray): 2D grayscale slice.
        Radius (int): Top-hat structuring element radius.
        Clahe_Kernel (Tuple[int, int]): CLAHE tile dimensions.
        Clahe_Clip (float): CLAHE clip limit.
        Saturation_Percentiles (Tuple[float, float]): (low, high) percentiles.
    
    Returns:
        np.ndarray: Enhanced slice, float64, range [0, 255].
    """
    Tophat_Result = Apply_White_Tophat(Image, Radius)
    Clahe_Result = Apply_Clahe(Tophat_Result, Clahe_Kernel, Clahe_Clip)
    Final_Result = Saturate_Percentiles(
        Clahe_Result,
        Saturation_Percentiles[0],
        Saturation_Percentiles[1]
    )
    
    return Final_Result