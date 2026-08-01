"""Orchestration engine: GMM -> Hierarchical Refinement -> Spatial HMRF."""

import numpy as np
from typing import Dict, Optional, Tuple

from .gmm_fitter import Gmm_Fitter
from .hierarchy import Hierarchical_Gmm
from .hmrf import Hmrf_Segmenter


class Segmentation_Engine:
    """End-to-end segmentation engine operating on 3D micro-CT volumes.

    Usage:
        >>> Engine = Segmentation_Engine()
        >>> Labels, Probabilities = Engine.Run(Volume)
    """

    def __init__(
        self,
        Gmm_Min_K: int = 2,
        Gmm_Max_K: int = 8,
        Hierarchy_Max_Depth: int = 5,
        Hierarchy_Min_Samples: int = 1000,
        Hierarchy_Alpha: float = 0.05,
        Hmrf_Beta: float = 0.5,
        Hmrf_Iterations: int = 50,
    ):
        self.Gmm_Min_K = Gmm_Min_K
        self.Gmm_Max_K = Gmm_Max_K
        self.Hierarchy_Max_Depth = Hierarchy_Max_Depth
        self.Hierarchy_Min_Samples = Hierarchy_Min_Samples
        self.Hierarchy_Alpha = Hierarchy_Alpha
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
        """Run complete segmentation pipeline without array copies.

        Args:
            Volume: Preprocessed 3D volume, shape (D, H, W).
            Use_Hierarchy: Enable soft hierarchical splitting.
            Use_Hmrf: Enable spatial regularization.

        Returns:
            Tuple of (Labels, Probabilities):
                Labels: Integer label volume, shape (D, H, W).
                Probabilities: Component posterior volume, shape (D, H, W, K_Final).
        """
        D, H, W = Volume.shape
        Flat_Data = Volume.reshape(-1, 1)

        print("[Engine] Step 1/3: Fitting flat baseline GMM...")
        self.Gmm = Gmm_Fitter(
            Min_Components=self.Gmm_Min_K,
            Max_Components=self.Gmm_Max_K,
        )
        self.Gmm.Fit(Flat_Data)

        Initial_K = self.Gmm.Num_Components
        print(f"[Engine] Flat GMM selected initial K={Initial_K}")

        Probabilities = self.Gmm.Predict_Probabilities(Flat_Data)

        # Optional Step 2: Soft Hierarchical Refinement
        if Use_Hierarchy:
            print("[Engine] Step 2/3: Building soft hierarchical refinement trees...")
            self.Hierarchy = Hierarchical_Gmm(
                Min_Samples=self.Hierarchy_Min_Samples,
                Max_Depth=self.Hierarchy_Max_Depth,
                Significance_Alpha=self.Hierarchy_Alpha,
            )
            self.Hierarchy.Fit(Flat_Data, Initial_K=Initial_K)

            # Extract soft leaf path probabilities directly (no flat GMM re-fitting)
            Probabilities = self.Hierarchy.Predict_Leaf_Probabilities(Flat_Data)
            Final_K = Probabilities.shape[1]
            print(f"[Engine] Hierarchical refinement produced Final K={Final_K} leaf components")
        else:
            Final_K = Initial_K

        # Compute log unary scores for spatial regularization
        Log_Probs = np.log(Probabilities + 1e-10)
        Log_Probs_Volume = Log_Probs.reshape(D, H, W, Final_K)
        Prob_Volume = Probabilities.reshape(D, H, W, Final_K)

        # Optional Step 3: Spatial HMRF Optimization
        if Use_Hmrf:
            print("[Engine] Step 3/3: Running HMRF spatial regularization...")
            self.Hmrf = Hmrf_Segmenter(
                Beta=self.Hmrf_Beta,
                Max_Iterations=self.Hmrf_Iterations,
            )
            # Pass log unary probabilities volume directly as the primary parameter
            Labels = self.Hmrf.Fit(Log_Probs_Volume)
        else:
            Labels = np.argmax(Probabilities, axis=1).reshape(D, H, W)

        print("[Engine] Segmentation complete successfully.")
        return Labels, Prob_Volume
