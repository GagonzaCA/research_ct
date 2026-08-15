"""
Perona-Malik anisotropic diffusion.

Edge-preserving smoothing that reduces noise in homogeneous regions
while preserving sharp boundaries between materials.
"""

import warnings
import numpy as np
from typing import Tuple


def Apply_Anisotropic_Diffusion(
    Image: np.ndarray,
    Num_Iterations: int = 500,
    Kappa: float = 50.0,
    Gamma: float = 0.1,
    Step_Size: Tuple[float, float] = (1.0, 1.0),
    Conduction_Mode: int = 1
) -> np.ndarray:
    """
    Apply Perona-Malik anisotropic diffusion filtering.
    
    Solves the PDE: dI/dt = div(c(x,y,t) * grad(I))
    where c is the conduction coefficient that decreases with gradient
    magnitude, preserving edges while smoothing homogeneous regions.
    
    Args:
        Image (np.ndarray): 2D grayscale image. Converted to float32.
        Num_Iterations (int): Number of diffusion steps.
        Kappa (float): Conduction threshold. Gradients below kappa are
            smoothed; gradients above are preserved. Typical: 50-200.
        Gamma (float): Time step. Must be <= 0.25 for numerical stability.
        Step_Size (Tuple[float, float]): Spatial step (dy, dx).
        Conduction_Mode (int): 1 for exponential conduction
            g = exp(-(grad/kappa)^2), 2 for rational conduction
            g = 1/(1+(grad/kappa)^2).
    
    Returns:
        np.ndarray: Smoothed image, float32.
    
    Raises:
        ValueError: If Gamma > 0.25 (unstable).
    
    Reference:
        Perona, P. & Malik, J. (1990). Scale-space and edge detection
        using anisotropic diffusion. IEEE TPAMI, 12(7), 629-639.
    """
    if Gamma > 0.25:
        raise ValueError(
            f"Gamma={Gamma} exceeds stability limit 0.25. "
            "Reduce time step."
        )
    
    if Image.ndim == 3:
        warnings.warn("Converting color to grayscale for diffusion")
        Image = Image.mean(axis=2)
    
    # Working copy
    Output = Image.astype(np.float32)
    
    # Difference arrays
    Delta_South = np.zeros_like(Output)
    Delta_East = np.zeros_like(Output)
    
    for _ in range(Num_Iterations):
        # Compute differences (forward differences)
        Delta_South[:-1, :] = np.diff(Output, axis=0)
        Delta_East[:, :-1] = np.diff(Output, axis=1)
        
        # Conduction coefficients
        if Conduction_Mode == 1:
            # Exponential: stronger edge preservation
            G_South = np.exp(-(Delta_South / Kappa) ** 2) / Step_Size[0]
            G_East = np.exp(-(Delta_East / Kappa) ** 2) / Step_Size[1]
        else:
            # Rational: more gradual falloff
            G_South = 1.0 / (1.0 + (Delta_South / Kappa) ** 2) / Step_Size[0]
            G_East = 1.0 / (1.0 + (Delta_East / Kappa) ** 2) / Step_Size[1]
        
        # Flux = conduction * gradient
        Flux_South = G_South * Delta_South
        Flux_East = G_East * Delta_East
        
        # Divergence (conservative form: flux in - flux out)
        Divergence_South = Flux_South.copy()
        Divergence_South[1:, :] -= Flux_South[:-1, :]
        
        Divergence_East = Flux_East.copy()
        Divergence_East[:, 1:] -= Flux_East[:, :-1]
        
        # Update
        Output += Gamma * (Divergence_South + Divergence_East)
    
    return Output