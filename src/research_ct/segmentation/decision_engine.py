"""Orchestration: GMM -> Hierarchy -> HMRF pipeline."""

import numpy as np
from typing import Dict, Optional, Tuple

from .gmm_fitter import Gmm_Fitter
from .hierarchy import Hierarchical_Gmm
from .hmrf import Hmrf_Segmenter


class Segmentation_Engine:
    """End-to-end segmentation: flat GMM -> hierarchy -> HMRF.
    
    Usage:
        >>> Engine = Segmentation_Engine()
        >>> Labels, Probabilities = Engine.Run(Volume)
    """
    
    def __init__(
        self,
        Gmm_Min_K: int = 2,
        Gmm_Max_K: int = 8,
        Hierarchy_Max_Depth: int = 3,
        Hmrf_Beta: float = 0.5,
        Hmrf_Iterations: int = 50,
    ):
        self.Gmm_Min_K = Gmm_Min_K
        self.Gmm_Max_K = Gmm_Max_K
        self.Hierarchy_Max_Depth = Hierarchy_Max_Depth
        self.Hmrf_Beta = Hmrf_Beta
        self.Hmrf_Iterations = Hmrf_Iterations
        
        self.Gmm: Optional[Gmm_Fitter] = None
        self.Hierarchy: Optional[Hierarchical_Gmm] = None
        self.Hmrf: Optional[Hmrf_Segmenter] = None
    
    def Run(
        self,
        Volume: np.ndarray,
        Use_Hierarchy: bool = True,
        Use_Hmrf: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Run complete segmentation pipeline.
        
        Args:
            Volume: Preprocessed 3D volume (D, H, W).
            Use_Hierarchy: Enable hierarchical splitting.
            Use_Hmrf: Enable spatial regularization.
        
        Returns:
            Tuple of (labels, probabilities).
                Labels: integer array (D, H, W).
                Probabilities: float array (D, H, W, K).
        """
        print("[Engine] Step 1/3: Fitting flat GMM...")
        
        # Flatten for GMM
        Flat_Data = Volume.ravel().reshape(-1, 1)
        
        self.Gmm = Gmm_Fitter(
            Min_Components=self.Gmm_Min_K,
            Max_Components=self.Gmm_Max_K,
        )
        self.Gmm.Fit(Flat_Data)
        
        K = self.Gmm.Num_Components
        print(f"[Engine] GMM found K={K} components")
        
        # Get probabilities
        Probabilities = self.Gmm.Predict_Probabilities(Flat_Data)
        Log_Probs = np.log(Probabilities + 1e-10)
        
        # Reshape to volume
        D, H, W = Volume.shape
        Log_Probs_Volume = Log_Probs.reshape(D, H, W, K)
        Prob_Volume = Probabilities.reshape(D, H, W, K)
        
        Labels = self.Gmm.Predict_Labels(Flat_Data).reshape(D, H, W)
        
        # Hierarchy (optional)
        if Use_Hierarchy and K < self.Gmm_Max_K:
            print("[Engine] Step 2/3: Hierarchical refinement...")
            self.Hierarchy = Hierarchical_Gmm(
                Max_Depth=self.Hierarchy_Max_Depth,
            )
            self.Hierarchy.Fit(Flat_Data, Initial_K=K)
            
            # Re-fit with expanded K
            Leaves = self.Hierarchy.Get_Leaf_Components()
            New_K = len(Leaves)
            
            if New_K > K:
                print(f"[Engine] Expanded to K={New_K}")
                self.Gmm = Gmm_Fitter(
                    Min_Components=New_K,
                    Max_Components=New_K,
                )
                self.Gmm.Fit(Flat_Data)
                
                Probabilities = self.Gmm.Predict_Probabilities(Flat_Data)
                Log_Probs_Volume = np.log(Probabilities + 1e-10).reshape(D, H, W, New_K)
                Prob_Volume = Probabilities.reshape(D, H, W, New_K)
                Labels = self.Gmm.Predict_Labels(Flat_Data).reshape(D, H, W)
        
        # HMRF (optional)
        if Use_Hmrf:
            print("[Engine] Step 3/3: HMRF spatial regularization...")
            self.Hmrf = Hmrf_Segmenter(
                Beta=self.Hmrf_Beta,
                Max_Iterations=self.Hmrf_Iterations,
            )
            Labels = self.Hmrf.Fit(Volume, Log_Probs_Volume)
        
        print("[Engine] Segmentation complete")
        return Labels, Prob_Volume