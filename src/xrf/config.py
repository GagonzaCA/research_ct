"""
Módulo de configuración para el pipeline de Fluorescencia de Rayos X (XRF).
Define los hiperparámetros para preprocesamiento, segmentación y análisis espacial.
"""

from dataclasses import dataclass


@dataclass
class Xrf_Preprocessing_Config:
    """
    Configuración para la lectura y preprocesamiento de los datos XRF.

    Args:
        Noise_Threshold (float): Umbral de intensidad mínima acumulada tau_ruido
            para considerar un píxel como válido. Por defecto es 5.0.
        Zero_Replacement_Delta (float): Constante delta minúscula para reemplazar
            ceros antes de la transformación CLR. Por defecto es 1e-4.
        Compute_Dtype (str): Precisión numérica para los cálculos.
            Por defecto es 'float64' para evitar inestabilidad en logaritmos.
    """

    Noise_Threshold: float = 5.0
    Zero_Replacement_Delta: float = 1e-4
    Compute_Dtype: str = "float64"


@dataclass
class Xrf_Segmentation_Config:
    """
    Configuración para la reducción de dimensiones y clustering GMM.

    Args:
        Pca_Variance_Ratio (float): Fracción de varianza explicada acumulada a
            retener en la reducción PCA. Rango (0, 1]. Por defecto es 0.95.
        Gmm_Min_K (int): Número mínimo de clases composicionales K a evaluar.
            Por defecto es 2.
        Gmm_Max_K (int): Número máximo de clases composicionales K a evaluar.
            Por defecto es 8.
        Covariance_Type (str): Tipo de matriz de covarianza para el GMM
            (full, tied, diag, spherical). Por defecto es 'full'.
    """

    Pca_Variance_Ratio: float = 0.95
    Gmm_Min_K: int = 2
    Gmm_Max_K: int = 8
    Covariance_Type: str = "full"


@dataclass
class Leaf_Signature_Config:
    """
    Configuración para la extracción de firmas de hoja (F_h) y descriptores espaciales.

    Args:
        Connectivity (int): Número de vecinos para el algoritmo de componentes
            conectadas (4 u 8 para 2D). Por defecto es 8.
        Min_Region_Size (int): Número mínimo de píxeles para considerar una
            región válida en el análisis morfológico. Por defecto es 10.
    """

    Connectivity: int = 8
    Min_Region_Size: int = 10
