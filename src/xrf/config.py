"""
Módulo de configuración para el pipeline de Fluorescencia de Rayos X (XRF).
Define los hiperparámetros para preprocesamiento, segmentación y análisis espacial.
"""

from dataclasses import dataclass, field
from typing import List


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


@dataclass
class Xrf_Comparison_Config:
    """Configuration for category-level XRF page comparison.

    Attributes:
        Allowed_Categories: Fixed vocabulary of structural page-category
            labels. Kept as an explicit, editable list rather than an enum
            so new categories can be added without a code change.
        Min_Pages_Per_Category: Categories with fewer tagged pages than this
            still get computed, but are flagged low-confidence everywhere
            they're reported (plots, summary json).
        Rarity_Mad_Threshold: Robust z-score magnitude above which a page is
            flagged as "rare" relative to its category. This is a triage
            threshold for human review, not a significance level.
        Min_Region_Size: Passed through to spatial comparison; mirrors
            Leaf_Signature_Config.Min_Region_Size for consistency.
    """

    Allowed_Categories: List[str] = field(default_factory=lambda: [
        "text_only", "chapter_start", "illustration", "mixed", "unknown"
    ])
    Min_Pages_Per_Category: int = 5
    Rarity_Mad_Threshold: float = 3.5
    Min_Region_Size: int = 10
