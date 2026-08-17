"""
Geometric normal analysis for isolated structural classes (e.g., ink).

Adapted from Charles' 3D vector evaluation algorithm. Extracts surface normals
from segmented structural components and encodes them as RGB color channels
for visualization and geometric analysis.
"""

import numpy as np
from collections import deque
from typing import Optional, List, Tuple

# =============================================================================
# PUBLIC API: The I/O & Masking Wrapper
# =============================================================================


def Calculate_Class_Normals(
    Labels_Volume: np.ndarray,
    Target_Class: int,
    Base_Intensity_Volume: Optional[np.ndarray] = None,
    Threshold: int = 190,
    Connectivity: int = 26,
    Up_Dir: int = 1,
    Display_Out: bool = True,
) -> np.ndarray:
    """
    Isolate a specific GMM class and compute 3D geometric normals.

    Args:
        Labels_Volume (np.ndarray): The hard labels (D, H, W) derived from the GMM.
        Target_Class (int): The integer label corresponding to the target (e.g., ink).
        Base_Intensity_Volume (Optional[np.ndarray]): Original gray values if required.
        Threshold (int): Intensity threshold for the region growing.
        Connectivity (int): 6, 18, or 26 connected neighborhood.
        Up_Dir (int): Orientation multiplier for the Z-axis.
        Display_Out (bool): Whether to format the output for visualization (max axis).

    Returns:
        np.ndarray: A 4D array (D, H, W, 3) of dtype uint8 encoding XYZ vectors as RGB.
    """
    # 1. Isolate the class using a binary mask
    Class_Mask = (Labels_Volume == Target_Class).astype(np.uint8)

    if Base_Intensity_Volume is not None:
        Active_Volume = Base_Intensity_Volume * Class_Mask
    else:
        # Treat the binary mask as the volume itself, scaled to 255 so it passes Threshold
        Active_Volume = Class_Mask * 255

    print(f"Calculating raw normals for Target Class: {Target_Class}")
    Raw_Normals = _Compute_Raw_Normals(Active_Volume, Threshold, Connectivity)

    print(f"Calculating average normal regions for Target Class: {Target_Class}")
    Avg_Normals = _Compute_Avg_Normal_3D(
        volGray=Active_Volume,
        volC=Raw_Normals,
        thresh=Threshold,
        connectivity=Connectivity,
        up_dir=Up_Dir,
        display_out=Display_Out,
    )

    return Avg_Normals


# =============================================================================
# PRIVATE API: The Geometric Engine (Charles' Core Logic)
# =============================================================================


class _Point:
    """Memory-efficient 3D coordinate struct for region growing."""

    __slots__ = ("z", "x", "y")

    def __init__(self, z: int, x: int, y: int):
        self.z = z
        self.x = x
        self.y = y


def _neighbors(connectivity: int) -> List[Tuple[int, int, int]]:
    """Generate relative offset directions for chosen spatial connectivity."""
    nb = []
    for dz in (-1, 0, 1):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dz == dx == dy == 0:
                    continue
                if connectivity == 6 and (abs(dz) + abs(dx) + abs(dy) != 1):
                    continue
                if connectivity == 18 and (abs(dz) + abs(dx) + abs(dy) > 2):
                    continue
                nb.append((dz, dx, dy))
    return nb


def _resize(inVector: np.ndarray) -> np.ndarray:
    """Rescales unit vector, mapping [-1.0, 1.0] to [1, 255] for storage."""
    vLen = np.linalg.norm(inVector)
    if vLen == 0:
        return inVector
    unitV = inVector / vLen
    return np.int_(np.add(np.multiply(unitV, 127), 128))


def _normal(vol: np.ndarray, p: _Point, thresh: int, connectivity: int) -> np.ndarray:
    """Calculates normal vector by evaluating adjacent dark/empty pixels."""
    D, H, W = vol.shape
    outList = [0, 0, 0]

    for dz, dx, dy in _neighbors(connectivity):
        nz, nx, ny = p.z + dz, p.x + dx, p.y + dy
        if (not (0 <= nz < D and 0 <= nx < H and 0 <= ny < W)) or vol[nz, nx, ny] < thresh:
            outList[0] += dz
            outList[1] += dx
            outList[2] += dy

    return _resize(np.array(outList))


def _Compute_Raw_Normals(img: np.ndarray, thresh: int, connectivity: int) -> np.ndarray:
    """Calculates all boundary normals for the volume."""
    newSize = img.shape + (3,)
    outImg = np.zeros(newSize, dtype=np.uint8)

    # Note: Pure Python nested loops over 3D volumes. Can be vectorized
    # or accelerated with Numba in the future if speed becomes a bottleneck.
    for z in range(img.shape[0]):
        for x in range(img.shape[1]):
            for y in range(img.shape[2]):
                if img[z, x, y] >= thresh:
                    outImg[z, x, y, :] = _normal(img, _Point(z, x, y), thresh, connectivity)
    return outImg


def _align_angle(angle: np.ndarray, up_dir: int = 1) -> np.ndarray:
    """Flips angle if it points downwards to maintain consistent axis measurement."""
    if (int(angle[0]) - 128) * up_dir < 0:
        temp = np.int32(np.subtract(255, angle))
    else:
        temp = np.int32(angle)
    return np.subtract(temp, 128)


def _align_abs(angle: np.ndarray) -> np.ndarray:
    """Maps absolute value of each axis optimized for axis determination."""
    temp = np.absolute(np.int32(np.subtract(angle, 128)))
    return np.multiply(temp, 2)


def _maxAxis(angle: np.ndarray) -> np.ndarray:
    """Isolates the largest axis component, zeroes out the rest."""
    output = np.zeros(angle.shape, dtype=np.uint8)
    index = np.argmax(angle)
    output[index] = 255
    return output


def _Compute_Avg_Normal_3D(
    volGray: np.ndarray,
    volC: np.ndarray,
    thresh: int,
    connectivity: int,
    up_dir: int,
    display_out: bool,
) -> np.ndarray:
    """
    Region grows connected shapes and averages their internal normals.
    Assumes flat components perpendicular to page.
    """
    D, H, W = volGray.shape
    out_mask = np.zeros((D, H, W, 3), dtype=np.uint8)
    nbs = _neighbors(connectivity)

    for z in range(D):
        for x in range(H):
            for y in range(W):
                # Require point to have information and not already be processed
                if not (np.array_equal(volC[z, x, y, :], [0, 0, 0])) and np.array_equal(
                    out_mask[z, x, y, :], [0, 0, 0]
                ):

                    pointList = [_Point(z, x, y)]
                    avgAngle = np.subtract(np.int16(volC[z, x, y, :]), 128)

                    Q = deque([_Point(z, x, y)])

                    while Q:
                        p = Q.popleft()

                        for dz, dx, dy in nbs:
                            nz, nx, ny = p.z + dz, p.x + dx, p.y + dy

                            if not (0 <= nz < D and 0 <= nx < H and 0 <= ny < W):
                                continue
                            if out_mask[nz, nx, ny, 0] != 0 and out_mask[nz, nx, ny, 1] != 0:
                                continue

                            val = int(volGray[nz, nx, ny])
                            if val >= thresh:
                                if display_out:
                                    avgAngle = np.add(avgAngle, _align_abs(volC[nz, nx, ny, :]))
                                else:
                                    avgAngle = np.add(
                                        avgAngle, _align_angle(volC[nz, nx, ny, :], up_dir)
                                    )

                                pointList.append(_Point(nz, nx, ny))
                                Q.append(_Point(nz, nx, ny))

                                # Update placeholder to mark as processed
                                out_mask[nz, nx, ny, :] = 255

                    if display_out:
                        finalAvgAngle = _maxAxis(avgAngle)
                    else:
                        finalAvgAngle = _resize(avgAngle)

                    # Paint the region with the averaged normal
                    for p2 in pointList:
                        out_mask[p2.z, p2.x, p2.y, 0] = finalAvgAngle[0]
                        out_mask[p2.z, p2.x, p2.y, 1] = finalAvgAngle[1]
                        out_mask[p2.z, p2.x, p2.y, 2] = finalAvgAngle[2]

    return out_mask
