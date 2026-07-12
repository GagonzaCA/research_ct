"""Hierarchical component splitting for GMM refinement."""

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2
from typing import Dict, List, Optional, Tuple


class Hierarchical_Gmm:
    """Recursively split GMM components if statistically justified.
    
    Tests each component: fit 2-subcomponent GMM, compare BIC,
    apply likelihood ratio test for significance.
    """
    
    def __init__(
        self,
        Min_Samples: int = 1000,
        Max_Depth: int = 5,
        Significance_Alpha: float = 0.05,
    ):
        self.Min_Samples = Min_Samples
        self.Max_Depth = Max_Depth
        self.Significance_Alpha = Significance_Alpha
        
        self.Root_Gmm: Optional[GaussianMixture] = None
        self.Component_Tree: Dict = {}
    
    def Fit(self, Data: np.ndarray, Initial_K: int = 2) -> "Hierarchical_Gmm":
        """Build hierarchical GMM by recursive splitting.
        
        Args:
            Data: 1D intensities, shape (N, 1).
            Initial_K: Starting number of components.
        
        Returns:
            Self for method chaining.
        """
        if Data.ndim == 1:
            Data = Data.reshape(-1, 1)
        
        # Fit initial flat GMM
        self.Root_Gmm = GaussianMixture(
            n_components=Initial_K,
            covariance_type="full",
            random_state=42,
        )
        self.Root_Gmm.fit(Data)
        
        # Build hierarchy
        self.Component_Tree = self._Split_Component(
            Data,
            self.Root_Gmm,
            Component_Id=0,
            Depth=0,
        )
        
        return self
    
    def _Split_Component(
        self,
        Data: np.ndarray,
        Parent_Gmm: GaussianMixture,
        Component_Id: int,
        Depth: int,
    ) -> Dict:
        """Recursively test and split a single component.
        
        Args:
            Data: Full dataset.
            Parent_Gmm: Current GMM model.
            Component_Id: Index of component to test.
            Depth: Current recursion depth.
        
        Returns:
            Tree node dict with component info and children.
        """
        # Get responsibilities for this component
        Responsibilities = Parent_Gmm.predict_proba(Data)[:, Component_Id]
        Effective_Samples = Responsibilities.sum()
        
        # Stopping: too few samples
        if Effective_Samples < self.Min_Samples or Depth >= self.Max_Depth:
            return {
                "is_leaf": True,
                "component_id": Component_Id,
                "mean": Parent_Gmm.means_[Component_Id].item(),
                "variance": np.diag(Parent_Gmm.covariances_[Component_Id]).item(),
                "weight": Parent_Gmm.weights_[Component_Id],
                "depth": Depth,
            }
        
        # Fit 2-component sub-GMM on weighted data
        Sub_Gmm = GaussianMixture(n_components=2, covariance_type="full", random_state=42)
        
        # Weighted fit
        Sub_Gmm.fit(Data, sample_weight=Responsibilities)
        
        # BIC comparison
        Parent_Bic = self._Weighted_Bic(Parent_Gmm, Data, Responsibilities)
        Sub_Bic = self._Weighted_Bic(Sub_Gmm, Data, Responsibilities)
        
        # Likelihood ratio test
        Lr_Stat = 2 * (Sub_Gmm.lower_bound_ - Parent_Gmm.lower_bound_)
        Df = 3  # mean, var, weight
        P_Value = 1 - chi2.cdf(Lr_Stat, Df)
        
        # Decision
        if Sub_Bic < Parent_Bic and P_Value < self.Significance_Alpha:
            # Split accepted
            return {
                "is_leaf": False,
                "component_id": Component_Id,
                "mean": Parent_Gmm.means_[Component_Id].item(),
                "depth": Depth,
                "bic_parent": Parent_Bic,
                "bic_split": Sub_Bic,
                "p_value": P_Value,
                "left": self._Split_Component(Data, Sub_Gmm, 0, Depth + 1),
                "right": self._Split_Component(Data, Sub_Gmm, 1, Depth + 1),
            }
        
        # Split rejected
        return {
            "is_leaf": True,
            "component_id": Component_Id,
            "mean": Parent_Gmm.means_[Component_Id].item(),
            "variance": np.diag(Parent_Gmm.covariances_[Component_Id]).item(),
            "weight": Parent_Gmm.weights_[Component_Id],
            "depth": Depth,
            "bic_parent": Parent_Bic,
            "bic_split": Sub_Bic,
            "p_value": P_Value,
        }
    
    def _Weighted_Bic(
        self,
        Gmm: GaussianMixture,
        Data: np.ndarray,
        Weights: np.ndarray,
    ) -> float:
        """Compute approximate BIC for weighted data."""
        # Use effective sample size
        N_Eff = Weights.sum()
        Log_Lik = Gmm.score_samples(Data) * Weights
        Log_Lik_Sum = Log_Lik.sum() / Weights.sum() * N_Eff
        
        K_Params = Gmm.n_components * 3 - 1  # means, vars, weights (sum to 1)
        
        return -2 * Log_Lik_Sum + K_Params * np.log(N_Eff)
    
    def Get_Leaf_Components(self) -> List[Dict]:
        """Extract all leaf nodes from component tree.
        
        Returns:
            List of leaf component dictionaries.
        """
        Leaves = []
        self._Collect_Leaves(self.Component_Tree, Leaves)
        return Leaves
    
    def _Collect_Leaves(self, Node: Dict, Leaves: List[Dict]) -> None:
        """Recursive leaf collection."""
        if Node.get("is_leaf", True):
            Leaves.append(Node)
            return
        
        if "left" in Node:
            self._Collect_Leaves(Node["left"], Leaves)
        if "right" in Node:
            self._Collect_Leaves(Node["right"], Leaves)