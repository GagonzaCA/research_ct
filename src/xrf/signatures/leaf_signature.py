"""
Module to synthesize leaf composition and structure into the compact signature F_h.
"""

import numpy as np
from typing import List, Dict


class Leaf_Signature_Extractor:
    """Class to compile the descriptive signature of a book page."""

    @staticmethod
    def Compute_Abundances(Labels: np.ndarray, Num_Classes: int) -> np.ndarray:
        """
        Computes the area fraction A_k occupied by each class.

        Args:
            Labels (np.ndarray): 1D assignment vector.
            Num_Classes (int): Total number K of GMM classes.

        Returns:
            np.ndarray: Abundance vector (K,) that sums to 1.0.
        """
        Total_Valid = len(Labels)
        if Total_Valid == 0:
            return np.zeros(Num_Classes)

        Abundances = np.zeros(Num_Classes)
        for K in range(Num_Classes):
            Abundances[K] = np.sum(Labels == K) / Total_Valid

        return Abundances

    @staticmethod
    def Compute_Weighted_Book_Signature(Signatures: np.ndarray, Weights: np.ndarray) -> np.ndarray:
        """
        Computes the global average model of the document by applying weights.

        Args:
            Signatures (np.ndarray): Signature matrix (H_pages, D_features).
            Weights (np.ndarray): Weight vector w_h (H_pages,).

        Returns:
            np.ndarray: Averaged global signature F_bar (D_features,).
        """
        Normalized_Weights = Weights / np.sum(Weights)
        return np.average(Signatures, axis=0, weights=Normalized_Weights)
