"""
Preprocessing configuration and presets.

Provides the Preprocessing_Config class for centralized parameter management
with built-in presets for different data types (real CT, synthetic, GMM-ready).
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict


@dataclass
class Preprocessing_Config:
    """
    Centralized configuration for the preprocessing pipeline.
    
    Attributes:
        -Radius (int): Structuring element radius for white top-hat filter.
            Auto-scaled to image size if None.
            
        -Clahe_Kernel (Tuple[int, int]): Kernel size for CLAHE.
            Auto-scaled if None.
            
        -Clahe_Clip (float): Clip limit for CLAHE contrast enhancement.
        
        -Diffusion_Iterations (int): Number of Perona-Malik iterations.
        
        -Diffusion_Kappa (float): Conduction coefficient.
            Higher values smooth more; lower values preserve edges.
            
        -Diffusion_Gamma (float): Time step. Must be <= 0.25 for stability.
        
        -Saturation_Percentiles (Tuple[float, float]): Low and high percentiles
            for intensity clipping.
            
        -Threshold_Percentile (Optional[float]): Percentile for background
            suppression. None disables thresholding (recommended for GMM).
            
        -Edge_Smooth_Sigma (float): Gaussian sigma for edge-strength smoothing.
        
        -Page_Peak_Min_Distance (int): Minimum slice distance between pages.
        
        -Page_Peak_Min_Prominence (float): Minimum edge-strength prominence
            for page detection.
    
    Example:
        >>> config = Preprocessing_Config(preset="Gmm_Ready")
        >>> config.Radius
        7
    """
    
    # --- Top-hat & CLAHE ---
    Radius: Optional[int] = None
    Clahe_Kernel: Optional[Tuple[int, int]] = None
    Clahe_Clip: float = 0.1
    
    # --- Anisotropic diffusion ---
    Diffusion_Iterations: int = 50
    Diffusion_Kappa: float = 75.0
    Diffusion_Gamma: float = 0.1
    
    # --- Intensity normalization ---
    Saturation_Percentiles: Tuple[float, float] = (0.5, 99.5)
    Threshold_Percentile: Optional[float] = None
    
    # --- Page detection ---
    Edge_Smooth_Sigma: float = 0.75
    Page_Peak_Min_Distance: int = 5
    Page_Peak_Min_Prominence: float = 1.5
    
    # --- Internal ---
    _Preset_Name: str = field(default="Custom", repr=False)
    
    # Class-level presets
    _Presets: Dict[str, Dict] = field(default_factory=dict, repr=False)
    
    def __post_init__(self):
        """Initialize presets after dataclass construction."""
        self._Presets = {
            "Real_Ct": {
                "Radius": 15,
                "Clahe_Kernel": (50, 50),
                "Clahe_Clip": 0.1,
                "Diffusion_Iterations": 70,
                "Diffusion_Kappa": 100.0,
                "Diffusion_Gamma": 0.1,
                "Saturation_Percentiles": (1.0, 99.0),
                "Threshold_Percentile": 85.0,
                "Edge_Smooth_Sigma": 0.75,
                "Page_Peak_Min_Distance": 5,
                "Page_Peak_Min_Prominence": 1.5,
            },
            "Synthetic": {
                "Radius": None,
                "Clahe_Kernel": None,
                "Clahe_Clip": 0.1,
                "Diffusion_Iterations": 10,
                "Diffusion_Kappa": 200.0,
                "Diffusion_Gamma": 0.1,
                "Saturation_Percentiles": (1.0, 99.0),
                "Threshold_Percentile": 30.0,
                "Edge_Smooth_Sigma": 0.75,
                "Page_Peak_Min_Distance": 5,
                "Page_Peak_Min_Prominence": 1.0,
            },
            "Gmm_Ready": {
                "Radius": 7,
                "Clahe_Kernel": (32, 32),
                "Clahe_Clip": 0.05,
                "Diffusion_Iterations": 50,
                "Diffusion_Kappa": 75.0,
                "Diffusion_Gamma": 0.1,
                "Saturation_Percentiles": (0.5, 99.5),
                "Threshold_Percentile": None,
                "Edge_Smooth_Sigma": 0.75,
                "Page_Peak_Min_Distance": 5,
                "Page_Peak_Min_Prominence": 1.5,
            },
        }
    
    @classmethod
    def From_Preset(cls, preset_name: str) -> "Preprocessing_Config":
        """
        Create configuration from a named preset.
        
        Args:
            preset_name (str): One of "Real_Ct", "Synthetic", "Gmm_Ready".
        
        Returns:
            Preprocessing_Config: Configured instance.
        
        Raises:
            ValueError: If preset_name is not recognized.
        """
        instance = cls()
        instance._Preset_Name = preset_name
        
        if preset_name not in instance._Presets:
            available = ", ".join(instance._Presets.keys())
            raise ValueError(
                f"Unknown preset '{preset_name}'. "
                f"Available: {available}"
            )
        
        params = instance._Presets[preset_name]
        for key, value in params.items():
            setattr(instance, key, value)
        
        return instance
    
    def __repr__(self) -> str:
        """String representation showing preset and key parameters."""
        return (
            f"Preprocessing_Config(preset='{self._Preset_Name}', "
            f"Radius={self.Radius}, "
            f"Diffusion_Kappa={self.Diffusion_Kappa}, "
            f"Threshold_Percentile={self.Threshold_Percentile})"
        )