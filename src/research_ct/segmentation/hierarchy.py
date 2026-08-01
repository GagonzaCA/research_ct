"""Hierarchical component splitting for GMM refinement with soft path propagation."""

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2
from typing import Dict, List, Optional, Tuple


class Hierarchical_Gmm:
    """Recursively split GMM components using soft path probability propagation.

    Evaluates recursive 2-component splits across all initial root components
    subject to 3 statistical criteria: effective sample size, BIC parsimony,
    and Likelihood Ratio Test (LRT) significance.
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
        self.Trees: List[Dict] = []
        self.Leaf_Nodes: List[Dict] = []

    def Fit(self, Data: np.ndarray, Initial_K: int = 2) -> "Hierarchical_Gmm":
        """Build hierarchical GMM trees by recursive splitting across all root components.

        Args:
            Data: 1D intensities view, shape (N, 1) or (N,).
            Initial_K: Number of root components from the initial flat GMM.

        Returns:
            Self for method chaining.
        """
        if Data.ndim == 1:
            Data = Data.reshape(-1, 1)

        # Fit root model across Initial_K components
        self.Root_Gmm = GaussianMixture(
            n_components=Initial_K,
            covariance_type="full",
            random_state=42,
        )
        self.Root_Gmm.fit(Data)

        # Initial root responsibilities: shape (N, Initial_K)
        Root_Responsibilities = self.Root_Gmm.predict_proba(Data)

        self.Trees = []
        # Recursively split EVERY root component k in {0, ..., Initial_K - 1}
        for Component_Index in range(Initial_K):
            Root_Path = Root_Responsibilities[:, Component_Index]
            Tree_Root = self._Split_Component(
                Data=Data,
                Path_Probabilities=Root_Path,
                Parent_Mean=self.Root_Gmm.means_[Component_Index].item(),
                Parent_Variance=np.diag(self.Root_Gmm.covariances_[Component_Index]).item(),
                Depth=0,
            )
            self.Trees.append(Tree_Root)

        # Collect flat list of all leaves across all root subtrees
        self.Leaf_Nodes = []
        for Tree in self.Trees:
            self._Collect_Leaves(Tree)

        return self

    def _Split_Component(
        self,
        Data: np.ndarray,
        Path_Probabilities: np.ndarray,
        Parent_Mean: float,
        Parent_Variance: float,
        Depth: int,
    ) -> Dict:
        """Recursively test and split a single node using sample-weighted statistics.

        Args:
            Data: Full dataset view, shape (N, 1).
            Path_Probabilities: Accumulated path probability for current node, shape (N,).
            Parent_Mean: Mean of single Gaussian fit for current node.
            Parent_Variance: Variance of single Gaussian fit for current node.
            Depth: Current recursion depth.

        Returns:
            Tree node dictionary with parameters, sub-models, and children.
        """
        Effective_Samples = Path_Probabilities.sum()

        # Gate 1: Effective sample size stopping condition
        if Effective_Samples < self.Min_Samples or Depth >= self.Max_Depth:
            return {
                "Is_Leaf": True,
                "Mean": Parent_Mean,
                "Variance": Parent_Variance,
                "Effective_Samples": Effective_Samples,
                "Depth": Depth,
                "Sub_Gmm": None,
            }

        # Fit candidate 2-component sub-GMM on weighted data
        Sub_Gmm = GaussianMixture(
            n_components=2,
            covariance_type="full",
            random_state=42,
        )
        Sub_Gmm.fit(Data, sample_weight=Path_Probabilities)

        # Compute parent single Gaussian log-likelihood on weighted sample
        Parent_Std = np.sqrt(max(Parent_Variance, 1e-10))
        Diff = Data.ravel() - Parent_Mean
        Log_Lik_Parent_Per_Sample = -0.5 * (
            np.log(2.0 * np.pi) + 2.0 * np.log(Parent_Std) + (Diff / Parent_Std) ** 2
        )
        Log_Lik_Parent_Sum = (Log_Lik_Parent_Per_Sample * Path_Probabilities).sum()

        # Compute 2-component split log-likelihood on weighted sample
        Log_Lik_Split_Per_Sample = Sub_Gmm.score_samples(Data)
        Log_Lik_Split_Sum = (Log_Lik_Split_Per_Sample * Path_Probabilities).sum()

        # Compute weighted BIC scores
        # Single 1D Gaussian: 2 parameters (mean, variance)
        Parent_Bic = -2.0 * Log_Lik_Parent_Sum + 2.0 * np.log(Effective_Samples)
        # 2-component 1D GMM: 5 parameters (2 means, 2 variances, 1 weight)
        Split_Bic = -2.0 * Log_Lik_Split_Sum + 5.0 * np.log(Effective_Samples)

        # Compute Likelihood Ratio Test (LRT) statistic and p-value (df = 5 - 2 = 3)
        Lr_Stat = max(0.0, 2.0 * (Log_Lik_Split_Sum - Log_Lik_Parent_Sum))
        P_Value = 1.0 - chi2.cdf(Lr_Stat, df=3)

        # Gate 2 & Gate 3: Model parsimony (BIC) and Statistical Significance (LRT)
        if Split_Bic < Parent_Bic and P_Value < self.Significance_Alpha:
            # Conditional responsibilities for left (0) and right (1) child branches
            Cond_Probs = Sub_Gmm.predict_proba(Data)
            Left_Path = Path_Probabilities * Cond_Probs[:, 0]
            Right_Path = Path_Probabilities * Cond_Probs[:, 1]

            Left_Mean = Sub_Gmm.means_[0].item()
            Left_Var = np.diag(Sub_Gmm.covariances_[0]).item()
            Right_Mean = Sub_Gmm.means_[1].item()
            Right_Var = np.diag(Sub_Gmm.covariances_[1]).item()

            return {
                "Is_Leaf": False,
                "Mean": Parent_Mean,
                "Variance": Parent_Variance,
                "Effective_Samples": Effective_Samples,
                "Depth": Depth,
                "Sub_Gmm": Sub_Gmm,
                "Left": self._Split_Component(Data, Left_Path, Left_Mean, Left_Var, Depth + 1),
                "Right": self._Split_Component(Data, Right_Path, Right_Mean, Right_Var, Depth + 1),
            }

        # Split rejected: treat current node as a final leaf
        return {
            "Is_Leaf": True,
            "Mean": Parent_Mean,
            "Variance": Parent_Variance,
            "Effective_Samples": Effective_Samples,
            "Depth": Depth,
            "Sub_Gmm": None,
        }

    def _Collect_Leaves(self, Node: Dict) -> None:
        """Collect references to all leaf nodes across subtrees."""
        if Node["Is_Leaf"]:
            self.Leaf_Nodes.append(Node)
            return

        if "Left" in Node:
            self._Collect_Leaves(Node["Left"])
        if "Right" in Node:
            self._Collect_Leaves(Node["Right"])

    def Predict_Leaf_Probabilities(self, Data: np.ndarray) -> np.ndarray:
        """Compute accumulated soft path probabilities for all leaf nodes across data.

        Args:
            Data: 1D intensities view, shape (N, 1) or (N,).

        Returns:
            Leaf responsibilities tensor of shape (N, L), normalized so sum_l P(leaf_l | x_i) = 1.0.
        """
        if Data.ndim == 1:
            Data = Data.reshape(-1, 1)

        N_Samples = Data.shape[0]
        N_Leaves = len(self.Leaf_Nodes)

        if self.Root_Gmm is None or N_Leaves == 0:
            raise RuntimeError("Model not fitted. Call Fit() first.")

        Root_Responsibilities = self.Root_Gmm.predict_proba(Data)
        Leaf_Probabilities = np.empty((N_Samples, N_Leaves), dtype=np.float64)

        Leaf_Counter = 0
        for Component_Index, Tree_Root in enumerate(self.Trees):
            Root_Path = Root_Responsibilities[:, Component_Index]
            Leaf_Counter = self._Evaluate_Node_Probabilities(
                Data=Data,
                Node=Tree_Root,
                Current_Path=Root_Path,
                Output_Array=Leaf_Probabilities,
                Leaf_Offset=Leaf_Counter,
            )

        # In-place normalization across leaves: sum_l P(leaf_l | x_i) = 1.0
        Row_Sums = Leaf_Probabilities.sum(axis=1, keepdims=True)
        Row_Sums[Row_Sums == 0.0] = 1.0
        Leaf_Probabilities /= Row_Sums

        return Leaf_Probabilities

    def _Evaluate_Node_Probabilities(
        self,
        Data: np.ndarray,
        Node: Dict,
        Current_Path: np.ndarray,
        Output_Array: np.ndarray,
        Leaf_Offset: int,
    ) -> int:
        """Traverse tree to evaluate leaf probabilities in pre-allocated array."""
        if Node["Is_Leaf"]:
            Output_Array[:, Leaf_Offset] = Current_Path
            return Leaf_Offset + 1

        Cond_Probs = Node["Sub_Gmm"].predict_proba(Data)
        Left_Path = Current_Path * Cond_Probs[:, 0]
        Right_Path = Current_Path * Cond_Probs[:, 1]

        Next_Offset = self._Evaluate_Node_Probabilities(
            Data, Node["Left"], Left_Path, Output_Array, Leaf_Offset
        )
        Final_Offset = self._Evaluate_Node_Probabilities(
            Data, Node["Right"], Right_Path, Output_Array, Next_Offset
        )
        return Final_Offset

    def Get_Leaf_Components(self) -> List[Dict]:
        """Extract metadata for all active leaf components."""
        return self.Leaf_Nodes
