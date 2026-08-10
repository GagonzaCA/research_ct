"""
Module for dimensionality reduction and probabilistic clustering of XRF data.
"""

import numpy as np
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from typing import Tuple, List, Dict


class Xrf_Gmm_Segmenter:
    """
    Class responsible for reducing dimensionality (PCA) and grouping behaviors (GMM).
    """

    @staticmethod
    def Fit_Predict(
        Clr_Data: np.ndarray,
        Num_Components: int,
        Variance_Ratio: float = 0.95,
        Covariance_Type: str = "full",
    ) -> Tuple[np.ndarray, np.ndarray, PCA, GaussianMixture]:
        """
        Applies PCA to retain variance and then fits a GMM.

        Args:
            Clr_Data (np.ndarray): Data in log-ratio space (N_valid, n).
            Num_Components (int): Number of classes K to search for.
            Variance_Ratio (float, optional): Variance to retain. Defaults to 0.95.
            Covariance_Type (str, optional): Covariance type. Defaults to "full".

        Returns:
            Tuple:
                - Discrete labels (N_valid,)
                - Posterior probabilities (N_valid, K)
                - Trained PCA object
                - Trained GMM object
        """
        # PCA reduction
        Pca_Model = PCA(n_components=Variance_Ratio, svd_solver="full")
        Z_Data = Pca_Model.fit_transform(Clr_Data)

        # GMM clustering
        Gmm_Model = GaussianMixture(
            n_components=Num_Components, covariance_type=Covariance_Type, random_state=42
        )
        Gmm_Model.fit(Z_Data)

        Labels = Gmm_Model.predict(Z_Data)
        Probabilities = Gmm_Model.predict_proba(Z_Data)

        return Labels, Probabilities, Pca_Model, Gmm_Model

    @staticmethod
    def Compute_Bic_Curve(
        Clr_Data: np.ndarray, K_Range: List[int], Variance_Ratio: float = 0.95
    ) -> Dict[int, float]:
        """
        Computes the Bayesian Information Criterion (BIC) for a range of K.

        Args:
            Clr_Data (np.ndarray): Data in log-ratio space.
            K_Range (List[int]): List of K values to evaluate.
            Variance_Ratio (float): Variance to retain in prior PCA.

        Returns:
            Dict[int, float]: Dictionary mapping K to its BIC score.
        """
        Pca_Model = PCA(n_components=Variance_Ratio, svd_solver="full")
        Z_Data = Pca_Model.fit_transform(Clr_Data)

        Bic_Scores = {}
        for K in K_Range:
            Model = GaussianMixture(n_components=K, random_state=42).fit(Z_Data)
            Bic_Scores[K] = Model.bic(Z_Data)

        return Bic_Scores
