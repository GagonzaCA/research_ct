"""
Module of transformations for Compositional Data Analysis (CoDa).
Implements the Centered Log-Ratio (CLR) transformation to overcome the closure effect.
"""

import numpy as np


class Clr_Transformer:
    """
    Class to apply proportional and CLR transformations to XRF data.
    """

    @staticmethod
    def Apply_Clr_Transform(Valid_Pixels: np.ndarray, Delta: float = 1e-4) -> np.ndarray:
        """
        Converts raw intensities to proportions, applies zero replacement, and
        projects to Euclidean space via the CLR transformation.

        Args:
            Valid_Pixels (np.ndarray): Array (N_valid, n) with raw intensities >= 0.
            Delta (float, optional): Small constant for zero replacement.
                Defaults to 1e-4.

        Returns:
            np.ndarray: Array (N_valid, n) transformed to real space (R^n).
        """
        # 1. Normalization (closure) to proportions (sum = 1)
        Row_Sums = np.sum(Valid_Pixels, axis=1, keepdims=True)
        Proportions = Valid_Pixels / Row_Sums

        # 2. Simple multiplicative zero replacement
        Proportions[Proportions == 0.0] = Delta

        # Renormalization after imputing zeros
        Proportions = Proportions / np.sum(Proportions, axis=1, keepdims=True)

        # 3. Centered Log-Ratio (CLR) transformation
        # log( x_i / geometric_mean(x) )
        Log_Proportions = np.log(Proportions)
        Geometric_Mean = np.mean(Log_Proportions, axis=1, keepdims=True)
        Clr_Data = Log_Proportions - Geometric_Mean

        return Clr_Data
