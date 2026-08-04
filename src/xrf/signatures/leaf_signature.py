"""
Módulo para sintetizar la composición y estructura de una hoja en la firma compacta F_h.
"""

import numpy as np
from typing import List, Dict


class Leaf_Signature_Extractor:
    """Clase para compilar la firma descriptiva de una página de libro."""

    @staticmethod
    def Compute_Abundances(Labels: np.ndarray, Num_Classes: int) -> np.ndarray:
        """
        Calcula la fracción de área A_k que ocupa cada clase.

        Args:
            Labels (np.ndarray): Vector de asignaciones 1D.
            Num_Classes (int): Número total K de clases GMM.

        Returns:
            np.ndarray: Vector de abundancias (K,) que suma 1.0.
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
        Calcula el modelo promedio global del documento aplicando pesos.

        Args:
            Signatures (np.ndarray): Matriz de firmas (H_paginas, D_features).
            Weights (np.ndarray): Vector de pesos w_h (H_paginas,).

        Returns:
            np.ndarray: Firma global promediada F_bar (D_features,).
        """
        Normalized_Weights = Weights / np.sum(Weights)
        return np.average(Signatures, axis=0, weights=Normalized_Weights)
