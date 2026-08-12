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
        Computes connected-component descriptors for a class efficiently.

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

        # Early exit if no features exist
        if Num_Features == 0:
            return {"Num_Regiones": 0.0, "Tamano_Promedio": 0.0}

        # OPTIMIZATION: Compute all region areas in a single pass.
        # np.bincount returns an array where index == Region_Id and value == Area.
        # We slice [1:] to drop index 0 (the background area).
        All_Areas = np.bincount(Labeled_Array.ravel())[1:]

        # Filter out regions smaller than Min_Size using vectorized boolean indexing
        Valid_Areas = All_Areas[All_Areas >= Min_Size]

        Valid_Regions = len(Valid_Areas)
        Avg_Size = np.mean(Valid_Areas) if Valid_Regions > 0 else 0.0

        return {"Num_Regiones": float(Valid_Regions), "Tamano_Promedio": float(Avg_Size)}
