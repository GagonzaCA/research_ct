"""Main preprocessing pipeline orchestrator."""

import time
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Optional

from .visual.config import Preprocessing_Config
from .visual.contrast import Enhance_Slice_Contrast
from .visual.diffusion import Apply_Anisotropic_Diffusion
from .diagnostics.diagnostic import Diagnose_Volume


def Preprocess_For_visual(
    Volume: np.ndarray,
    Config: Preprocessing_Config,
    Out_Dir: Optional[Path] = None,
    Expected_Pages: Optional[int] = None,
    Save_Intermediates: bool = False,
) -> Tuple[np.ndarray, Dict]:
    """Complete preprocessing pipeline for GMM segmentation.
    
    Steps:
        1. Contrast enhancement (top-hat + CLAHE + saturation)
        2. Anisotropic diffusion (Perona-Malik)
        3. Diagnostics (edge strength, page peaks, histogram)
    
    Args:
        Volume: Raw 3D volume (D, H, W).
        Config: Preprocessing configuration.
        Out_Dir: Directory for diagnostic outputs.
        Expected_Pages: Known page count if available.
        Save_Intermediates: Save enhanced and diffusion outputs.
    
    Returns:
        Tuple of (preprocessed_volume, diagnostics_dict).
    """
    D, H, W = Volume.shape
    print(f"[pipeline] Input: {Volume.shape}, range [{Volume.min():.1f}, {Volume.max():.1f}]")
    
    # Auto-scale parameters
    Radius = Config.Radius if Config.Radius is not None else max(3, int(0.015 * min(H, W)))
    Clahe_Kernel = Config.Clahe_Kernel if Config.Clahe_Kernel is not None else (
        max(8, H // 8), max(8, W // 8)
    )
    
    print(f"[pipeline] radius={Radius}, clahe={Clahe_Kernel}")
    
    # Step 1: Contrast enhancement
    print("\n[Step 1/3] Contrast enhancement...")
    T0 = time.time()
    Enhanced = np.zeros_like(Volume)
    
    for Z in range(D):
        Enhanced[Z] = Enhance_Slice_Contrast(
            Volume[Z],
            Radius,
            Clahe_Kernel,
            Config.Clahe_Clip,
            Config.Saturation_Percentiles,
        )
    
    print(f"[Step 1/3] Done in {time.time()-T0:.1f}s")
    
    # Step 2: Anisotropic diffusion
    print("\n[Step 2/3] Anisotropic diffusion...")
    T0 = time.time()
    Processed = np.zeros_like(Enhanced)
    
    for Z in range(D):
        Diffused = Apply_Anisotropic_Diffusion(
            Enhanced[Z],
            Num_Iterations=Config.Diffusion_Iterations,
            Kappa=Config.Diffusion_Kappa,
            Gamma=Config.Diffusion_Gamma,
        )
        
        # Normalize to [0, 255]
        Min_Val, Max_Val = Diffused.min(), Diffused.max()
        if Max_Val > Min_Val:
            Processed[Z] = (Diffused - Min_Val) / (Max_Val - Min_Val) * 255.0
    
    print(f"[Step 2/3] Done in {time.time()-T0:.1f}s")
    
    # Step 3: Diagnostics
    print("\n[Step 3/3] Diagnostics...")
    Config_Dict = {
        "Page_Peak_Min_Distance": Config.Page_Peak_Min_Distance,
        "Page_Peak_Min_Prominence": Config.Page_Peak_Min_Prominence,
        "Edge_Smooth_Sigma": Config.Edge_Smooth_Sigma,
    }
    
    Diagnostics = Diagnose_Volume(
        Processed,
        Out_Dir or Path("./output/diagnostics"),
        Config_Dict,
        Expected_Pages,
    )
    
    print(f"\n[pipeline] Output: {Processed.shape}")
    print(f"[pipeline] Range: [{Processed.min():.1f}, {Processed.max():.1f}]")
    
    return Processed, Diagnostics