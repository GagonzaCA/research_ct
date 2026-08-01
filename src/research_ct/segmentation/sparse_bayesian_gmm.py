"""Sparse Finite Bayesian Gaussian Mixture Model with Variational Inference."""

import numpy as np
from sklearn.mixture import BayesianGaussianMixture
from typing import Dict, Optional


class Sparse_Bayesian_Gmm:
    """Overcomplete Bayesian GMM with sparse Dirichlet weight prior.

    Automatically collapses unneeded components to zero weight during inference.
    Active components are filtered based on weight thresholds and effective sample sizes.
    """

    def __init__(
        self,
        Max_Components: int = 10,
        Weight_Concentration_Prior: Optional[float] = None,
        Weight_Threshold: float = 1e-3,
        Min_Samples: int = 1000,
        Covariance_Type: str = "full",
        Random_State: int = 42,
    ):
        self.Max_Components = Max_Components
        self.Weight_Concentration_Prior = Weight_Concentration_Prior
        self.Weight_Threshold = Weight_Threshold
        self.Min_Samples = Min_Samples
        self.Covariance_Type = Covariance_Type
        self.Random_State = Random_State

        self.Model: Optional[BayesianGaussianMixture] = None
        self.Active_Indices: np.ndarray = np.array([])
        self.Num_Active_Components: int = 0
        self.Means: np.ndarray = np.array([])
        self.Variances: np.ndarray = np.array([])
        self.Weights: np.ndarray = np.array([])

    def Fit(self, Data: np.ndarray, Verbose: bool = True) -> "Sparse_Bayesian_Gmm":
        """Fit overcomplete model and prune inactive components.

        Args:
            Data: 1D intensity dataset view, shape (N, 1) or (N,).
            Verbose: Print active component counts.

        Returns:
            Self for method chaining.
        """
        if Data.ndim == 1:
            Data = Data.reshape(-1, 1)

        self.Model = BayesianGaussianMixture(
            n_components=self.Max_Components,
            covariance_type=self.Covariance_Type,
            weight_concentration_prior_type="dirichlet_distribution",
            weight_concentration_prior=self.Weight_Concentration_Prior,
            random_state=self.Random_State,
            max_iter=1000,
        )
        self.Model.fit(Data)

        # Calculate full component responsibilities
        Raw_Weights = self.Model.weights_
        Responsibilities = self.Model.predict_proba(Data)
        Effective_Samples = Responsibilities.sum(axis=0)

        # Thresholding for active status
        Active_Mask = (Raw_Weights >= self.Weight_Threshold) & (
            Effective_Samples >= self.Min_Samples
        )
        self.Active_Indices = np.where(Active_Mask)[0]
        self.Num_Active_Components = len(self.Active_Indices)

        # Fallback mechanism if thresholding is too aggressive
        if self.Num_Active_Components == 0:
            Fallback_Index = np.argmax(Raw_Weights)
            self.Active_Indices = np.array([Fallback_Index])
            self.Num_Active_Components = 1

        self.Means = self.Model.means_[self.Active_Indices].flatten()

        Raw_Covariances = self.Model.covariances_[self.Active_Indices]
        if self.Covariance_Type == "full":
            self.Variances = np.array([np.diag(Cov) for Cov in Raw_Covariances])
        else:
            self.Variances = Raw_Covariances.flatten()

        self.Weights = Raw_Weights[self.Active_Indices]

        # Renormalize extracted weights
        self.Weights /= self.Weights.sum()

        if Verbose:
            print(
                f"[Sparse_Bayesian_Gmm] Retained {self.Num_Active_Components}/{self.Max_Components} active components."
            )

        return self

    def Predict_Probabilities(self, Data: np.ndarray) -> np.ndarray:
        """Predict soft responsibilities normalized over active components only.

        Args:
            Data: 1D intensity dataset view.

        Returns:
            Normalized active probabilities, shape (N, K_active).
        """
        if self.Model is None:
            raise RuntimeError("Model is not fitted. Call Fit() first.")

        if Data.ndim == 1:
            Data = Data.reshape(-1, 1)

        # Obtain full responsibilities and slice dynamically
        Raw_Responsibilities = self.Model.predict_proba(Data)
        Active_Responsibilities = Raw_Responsibilities[:, self.Active_Indices]

        # In-place row normalization
        Row_Sums = Active_Responsibilities.sum(axis=1, keepdims=True)
        Row_Sums[Row_Sums == 0.0] = 1.0
        Active_Responsibilities /= Row_Sums

        return Active_Responsibilities

    def Predict_Labels(self, Data: np.ndarray) -> np.ndarray:
        """Predict hard integer labels based on active components.

        Returns:
            Array of integers, shape (N,).
        """
        Active_Probabilities = self.Predict_Probabilities(Data)
        return np.argmax(Active_Probabilities, axis=1)

    def Get_Material_Statistics(self) -> Dict[str, np.ndarray]:
        """Return parameters for active components."""
        return {
            "Means": self.Means,
            "Variances": self.Variances,
            "Weights": self.Weights,
            "Active_Indices": self.Active_Indices,
        }
