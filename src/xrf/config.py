"""
Configuration module for the X-Ray Fluorescence (XRF) pipeline.
Defines hyperparameters for preprocessing, segmentation, and spatial analysis.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Xrf_Preprocessing_Config:
    """
    Configuration for XRF data reading and preprocessing.

    Args:
        Noise_Threshold (float): Minimum accumulated intensity threshold tau_noise
            to consider a pixel valid. Defaults to 5.0.
        Zero_Replacement_Delta (float): Tiny delta constant to replace zeros before
            the CLR transformation. Defaults to 1e-4.
        Compute_Dtype (str): Numeric precision for computations.
            Defaults to 'float64' to avoid instability in logarithms.
    """

    Noise_Threshold: float = 5.0
    Zero_Replacement_Delta: float = 1e-4
    Compute_Dtype: str = "float64"


@dataclass
class Xrf_Segmentation_Config:
    """
    Configuration for dimensionality reduction and GMM clustering.

    Args:
        Pca_Variance_Ratio (float): Fraction of cumulative explained variance to
            retain in PCA reduction. Range (0, 1]. Defaults to 0.95.
        Gmm_Min_K (int): Minimum number of compositional classes K to evaluate.
            Defaults to 2.
        Gmm_Max_K (int): Maximum number of compositional classes K to evaluate.
            Defaults to 8.
        Covariance_Type (str): Covariance matrix type for the GMM
            (full, tied, diag, spherical). Defaults to 'full'.
    """

    Pca_Variance_Ratio: float = 0.95
    Gmm_Min_K: int = 2
    Gmm_Max_K: int = 8
    Covariance_Type: str = "full"


@dataclass
class Leaf_Signature_Config:
    """
    Configuration for leaf signature (F_h) extraction and spatial descriptors.

    Args:
        Connectivity (int): Number of neighbors for the connected-components
            algorithm (4 or 8 for 2D). Defaults to 8.
        Min_Region_Size (int): Minimum number of pixels to consider a region
            valid in morphological analysis. Defaults to 10.
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


@dataclass
class Bcf_Extraction_Config:
    """Hyperparameters for BCF-to-elemental-TIFF extraction.

    Controls dual-window Bremsstrahlung subtraction window geometry and
    the detector energy cutoff. All energy values in keV.

    Args:
        Cutoff_At_Kv: Detector energy ceiling; channels above this are
            discarded during BCF loading. Defaults to 40.0.
        Peak_Width_Kev: Half-width of the integration window centered
            on the emission line. Defaults to 0.20.
        Bg_Width_Kev: Half-width of each background-sideband window
            used for continuum estimation. Defaults to 0.10.
        Bg_Offset_Kev: Distance from the line center to each sideband
            center. Defaults to 0.25.
        Output_Dir: Directory where extracted element TIFFs are written.
            Defaults to ``data/xrf/raw/`` relative to the project root.
    """

    Cutoff_At_Kv: float = 40.0
    Peak_Width_Kev: float = 0.20
    Bg_Width_Kev: float = 0.10
    Bg_Offset_Kev: float = 0.25
    Output_Dir: Path = field(default_factory=lambda: Path("data", "xrf", "raw"))
