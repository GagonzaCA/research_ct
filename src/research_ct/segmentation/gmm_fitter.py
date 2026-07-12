"""Gaussian Mixture Model fitting with automatic K selection."""

import numpy as np
from sklearn.mixture import GaussianMixture
from typing import Dict, List, Optional, Tuple


class Gmm_Fitter:
    """Fit GMM to intensity data with BIC-based model selection.
    
    Attributes:
        Num_Components: Selected K.
        Model: Fitted sklearn GaussianMixture.
        Bic_Scores: BIC for each K tested.
    """
    
    def __init__(
        self,
        Min_Components: int = 1,
        Max_Components: int = 10,
        Covariance_Type: str = "full",
    ):
        self.Min_Components = Min_Components
        self.Max_Components = Max_Components
        self.Covariance_Type = Covariance_Type
        
        self.Num_Components: Optional[int] = None
        self.Model: Optional[GaussianMixture] = None
        self.Bic_Scores: List[float] = []
    
    def Fit(self, Data: np.ndarray, Verbose: bool = True) -> "Gmm_Fitter":
        """Fit GMM with automatic K selection via BIC.
        
        Args:
            Data: 1D array of intensities, shape (N,) or (N, 1).
            Verbose: Print progress.
        
        Returns:
            Self for method chaining.
        """
        if Data.ndim == 1:
            Data = Data.reshape(-1, 1)
        
        self.Bic_Scores = []
        Best_Bic = np.inf
        Best_Model = None
        Best_K = self.Min_Components
        
        for K in range(self.Min_Components, self.Max_Components + 1):
            Model = GaussianMixture(
                n_components=K,
                covariance_type=self.Covariance_Type,
                random_state=42,
                max_iter=1000,
            )
            Model.fit(Data)
            
            Bic = Model.bic(Data)
            self.Bic_Scores.append(Bic)
            
            if Verbose:
                print(f"  K={K}: BIC={Bic:.2e}, converged={Model.converged_}")
            
            if Bic < Best_Bic:
                Best_Bic = Bic
                Best_Model = Model
                Best_K = K
        
        self.Num_Components = Best_K
        self.Model = Best_Model
        
        if Verbose:
            print(f"[Gmm_Fitter] Selected K={Best_K}")
        
        return self
    
    def Predict_Labels(self, Data: np.ndarray) -> np.ndarray:
        """Predict hard labels (argmax posterior).
        
        Args:
            Data: Intensities, shape (N,) or (N, 1).
        
        Returns:
            Integer labels, shape (N,).
        """
        if self.Model is None:
            raise RuntimeError("Model not fitted. Call Fit() first.")
        
        if Data.ndim == 1:
            Data = Data.reshape(-1, 1)
        
        return self.Model.predict(Data)
    
    def Predict_Probabilities(self, Data: np.ndarray) -> np.ndarray:
        """Predict posterior probabilities.
        
        Args:
            Data: Intensities, shape (N,) or (N, 1).
        
        Returns:
            Probabilities, shape (N, K).
        """
        if self.Model is None:
            raise RuntimeError("Model not fitted. Call Fit() first.")
        
        if Data.ndim == 1:
            Data = Data.reshape(-1, 1)
        
        return self.Model.predict_proba(Data)
    
    def Get_Material_Statistics(self) -> Dict[str, np.ndarray]:
        """Extract fitted parameters per component.
        
        Returns:
            Dict with Means, Variances, Weights.
        """
        if self.Model is None:
            raise RuntimeError("Model not fitted. Call Fit() first.")
        
        Variances = np.array([
            np.diag(Cov) if Cov.ndim == 2 else Cov
            for Cov in self.Model.covariances_
        ])
        
        return {
            "Means": self.Model.means_.flatten(),
            "Variances": Variances,
            "Weights": self.Model.weights_,
        }