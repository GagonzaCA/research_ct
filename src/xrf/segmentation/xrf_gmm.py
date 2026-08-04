"""
Módulo para la reducción de dimensiones y clustering probabilístico de datos XRF.
"""

import numpy as np
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from typing import Tuple, List, Dict


class Xrf_Gmm_Segmenter:
    """
    Clase encargada de reducir dimensionalidad (PCA) y agrupar comportamientos (GMM).
    """

    @staticmethod
    def Fit_Predict(
        Clr_Data: np.ndarray,
        Num_Components: int,
        Variance_Ratio: float = 0.95,
        Covariance_Type: str = "full",
    ) -> Tuple[np.ndarray, np.ndarray, PCA, GaussianMixture]:
        """
        Aplica PCA para retener varianza y luego ajusta un GMM.

        Args:
            Clr_Data (np.ndarray): Datos en espacio log-ratio (N_validos, n).
            Num_Components (int): Número de clases K a buscar.
            Variance_Ratio (float, optional): Varianza a retener. Por defecto 0.95.
            Covariance_Type (str, optional): Tipo de covarianza. Por defecto "full".

        Returns:
            Tuple:
                - Etiquetas discretas (N_validos,)
                - Probabilidades posteriores (N_validos, K)
                - Objeto PCA entrenado
                - Objeto GMM entrenado
        """
        # Reducción PCA
        Pca_Model = PCA(n_components=Variance_Ratio, svd_solver="full")
        Z_Data = Pca_Model.fit_transform(Clr_Data)

        # Clustering GMM
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
        Calcula el criterio de información bayesiano (BIC) para un rango de K.

        Args:
            Clr_Data (np.ndarray): Datos en espacio log-ratio.
            K_Range (List[int]): Lista de valores K a evaluar.
            Variance_Ratio (float): Varianza a retener en PCA previo.

        Returns:
            Dict[int, float]: Diccionario que mapea K con su puntaje BIC.
        """
        Pca_Model = PCA(n_components=Variance_Ratio, svd_solver="full")
        Z_Data = Pca_Model.fit_transform(Clr_Data)

        Bic_Scores = {}
        for K in K_Range:
            Model = GaussianMixture(n_components=K, random_state=42).fit(Z_Data)
            Bic_Scores[K] = Model.bic(Z_Data)

        return Bic_Scores
