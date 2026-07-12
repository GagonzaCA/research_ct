"""Plotting utilities for GMM and histograms."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Optional


def plot_gmm_components(
    Data: np.ndarray,
    Gmm_Model,
    Output_Path: Optional[str] = None,
) -> plt.Figure:
    """Plot histogram with overlaid GMM components.
    
    Args:
        Data: 1D intensity array.
        Gmm_Model: Fitted sklearn GaussianMixture.
        Output_Path: Optional path to save figure.
    
    Returns:
        Matplotlib figure.
    """
    Fig, Ax = plt.subplots(figsize=(10, 6))
    
    # Histogram
    Ax.hist(Data, bins=256, density=True, alpha=0.5, color="gray", label="Data")
    
    # Individual components
    X = np.linspace(Data.min(), Data.max(), 1000)
    
    for K in range(Gmm_Model.n_components):
        Mean = Gmm_Model.means_[K, 0]
        Var = Gmm_Model.covariances_[K, 0, 0]
        Weight = Gmm_Model.weights_[K]
        
        Y = Weight * (1 / np.sqrt(2 * np.pi * Var)) * np.exp(-0.5 * (X - Mean)**2 / Var)
        
        Ax.plot(X, Y, linewidth=2, label=f"Comp {K}: μ={Mean:.1f}, σ²={Var:.1f}")
    
    # Mixture
    from scipy.stats import norm
    Y_Mix = np.zeros_like(X)
    for K in range(Gmm_Model.n_components):
        Y_Mix += Gmm_Model.weights_[K] * norm.pdf(
            X,
            Gmm_Model.means_[K, 0],
            np.sqrt(Gmm_Model.covariances_[K, 0, 0]),
        )
    
    Ax.plot(X, Y_Mix, "k--", linewidth=2, label="Mixture")
    
    Ax.set_xlabel("Intensity")
    Ax.set_ylabel("Density")
    Ax.set_title("GMM Component Decomposition")
    Ax.legend()
    Ax.grid(True, alpha=0.3)
    
    if Output_Path:
        Fig.savefig(Output_Path, dpi=150, bbox_inches="tight")
    
    return Fig