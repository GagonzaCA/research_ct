"""Hidden Markov Random Field for spatial regularization."""

import numpy as np
from typing import Optional, Tuple, List


class Hmrf_Segmenter:
    """HMRF with Potts prior for 3D spatial regularization.
    
    Energy: E(L) = sum -log p(x_i | L_i) + beta * sum delta(L_i != L_j)
    """
    
    def __init__(
        self,
        Beta: float = 0.5,
        Max_Iterations: int = 50,
        Connectivity: int = 6,
    ):
        self.Beta = Beta
        self.Max_Iterations = Max_Iterations
        self.Connectivity = Connectivity
        
        self.Labels: Optional[np.ndarray] = None
    
    def Fit(
        self,
        Volume: np.ndarray,
        Log_Probabilities: np.ndarray,
    ) -> np.ndarray:
        """Run ICM optimization for HMRF.
        
        Args:
            Volume: 3D array (D, H, W) — used for shape only.
            Log_Probabilities: Log p(x_i | k) for each class k.
                Shape: (D, H, W, K).
        
        Returns:
            Integer labels, shape (D, H, W).
        """
        D, H, W, K = Log_Probabilities.shape
        
        # Initialize from MAP
        self.Labels = np.argmax(Log_Probabilities, axis=3)
        
        # Define neighbors based on connectivity
        Neighbors = self._Get_Neighbors()
        
        for Iteration in range(self.Max_Iterations):
            Changes = 0
            
            for Z in range(D):
                for Y in range(H):
                    for X in range(W):
                        Current_Label = self.Labels[Z, Y, X]
                        
                        Best_Energy = float("inf")
                        Best_Label = Current_Label
                        
                        for K_Class in range(K):
                            # Likelihood term
                            Likelihood = -Log_Probabilities[Z, Y, X, K_Class]
                            
                            # Spatial prior (Potts model)
                            Spatial = 0
                            for Dz, Dy, Dx in Neighbors:
                                Nz, Ny, Nx = Z + Dz, Y + Dy, X + Dx
                                if (0 <= Nz < D and 0 <= Ny < H and 0 <= Nx < W):
                                    if self.Labels[Nz, Ny, Nx] != K_Class:
                                        Spatial += self.Beta
                            
                            Energy = Likelihood + Spatial
                            
                            if Energy < Best_Energy:
                                Best_Energy = Energy
                                Best_Label = K_Class
                        
                        if Best_Label != Current_Label:
                            self.Labels[Z, Y, X] = Best_Label
                            Changes += 1
            
            print(f"[HMRF] Iteration {Iteration + 1}: {Changes} changes")
            
            if Changes == 0:
                print("[HMRF] Converged")
                break
        
        return self.Labels
    
    def _Get_Neighbors(self) -> List[Tuple[int, int, int]]:
        """Get neighbor offsets for chosen connectivity."""
        if self.Connectivity == 6:
            return [
                (-1, 0, 0), (1, 0, 0),
                (0, -1, 0), (0, 1, 0),
                (0, 0, -1), (0, 0, 1),
            ]
        elif self.Connectivity == 26:
            Neighbors = []
            for Dz in (-1, 0, 1):
                for Dy in (-1, 0, 1):
                    for Dx in (-1, 0, 1):
                        if Dz == Dy == Dx == 0:
                            continue
                        Neighbors.append((Dz, Dy, Dx))
            return Neighbors
        
        raise ValueError(f"Connectivity {self.Connectivity} not supported")