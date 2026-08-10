"""
Module for topological reconstruction and extraction of spatial metrics (CCA).
"""

import numpy as np
from scipy import ndimage
from typing import Dict, Any


class Spatial_Analyzer:
    """Class to map labels to 2D and analyze their morphology."""

    @staticmethod
    def Reconstruct_Class_Map(
        Labels: np.ndarray, Mask: np.ndarray, Fill_Value: int = -1
    ) -> np.ndarray:
        """
        Maps the flattened label vector back to the 2D grid.

        Args:
            Labels (np.ndarray): 1D labels (N_valid,).
            Mask (np.ndarray): 2D binary mask (M, N).
            Fill_Value (int, optional): Background (noise) value. Defaults to -1.

        Returns:
            np.ndarray: 2D class map of shape (M, N).
        """
        Class_Map = np.full(Mask.shape, Fill_Value, dtype=np.int32)
        Class_Map[Mask] = Labels
        return Class_Map

    @staticmethod
    def Extract_Spatial_Descriptors(
        Class_Map: np.ndarray, Target_Class: int, Min_Size: int = 10
    ) -> Dict[str, float]:
        """
        Computes connected-component descriptors for a class.

        Args:
            Class_Map (np.ndarray): 2D class map.
            Target_Class (int): Identifier of the class to analyze.
            Min_Size (int): Minimum size to consider a region.

        Returns:
            Dict[str, float]: Dictionary with Num_Regions and Average_Size.
        """
        Binary_Mask = (Class_Map == Target_Class).astype(np.uint8)

        # 8-connectivity (3x3 matrix of ones)
        Structure = np.ones((3, 3), dtype=np.uint8)
        Labeled_Array, Num_Features = ndimage.label(Binary_Mask, structure=Structure)

        Valid_Regions = 0
        Total_Area = 0

        # Filter small regions
        for Region_Id in range(1, Num_Features + 1):
            Area = np.sum(Labeled_Array == Region_Id)
            if Area >= Min_Size:
                Valid_Regions += 1
                Total_Area += Area

        Avg_Size = Total_Area / Valid_Regions if Valid_Regions > 0 else 0.0

        return {"Num_Regiones": float(Valid_Regions), "Tamano_Promedio": float(Avg_Size)}
