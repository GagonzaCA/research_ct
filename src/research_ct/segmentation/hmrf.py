"""Hidden Markov Random Field (HMRF) with Potts prior for 3D spatial regularization."""

import numpy as np
from typing import Optional, Tuple, List


class Hmrf_Segmenter:
    """HMRF spatial regularization using Iterated Conditional Modes (ICM).

    Energy Formulation:
        E(z) = sum_i -log P(x_i | z_i) + Beta * sum_{(i,j) in E} delta(z_i != z_j)
    """

    def __init__(
        self,
        Beta: float = 0.5,
        Max_Iterations: int = 50,
        Connectivity: int = 6,
        Convergence_Percent: float = 0.001,
        Patience: int = 4,
    ):
        self.Beta = Beta
        self.Max_Iterations = Max_Iterations
        self.Connectivity = Connectivity
        self.Convergence_Percent = Convergence_Percent
        self.Patience = Patience

        self.Labels: Optional[np.ndarray] = None

    def Fit(
        self,
        Log_Probabilities: np.ndarray,
    ) -> np.ndarray:
        """Run ICM optimization for spatial label field regularization.

        Stopping criteria (checked in order):
            1. ``Changes == 0`` — exact convergence.
            2. ``Changes < int(Total_Voxels * Convergence_Percent)`` for
               ``Patience`` consecutive iterations — relative threshold.

        Args:
            Log_Probabilities: Pre-computed log unary scores, shape (D, H, W, K).

        Returns:
            Regularized integer labels, shape (D, H, W).
        """
        D, H, W, K = Log_Probabilities.shape
        Neighbors = self._Get_Neighbors()
        Total_Voxels = D * H * W
        Min_Changes = max(1, int(Total_Voxels * self.Convergence_Percent))
        Stalled_Count = 0

        # Initialize labels using Maximum A Posteriori (MAP)
        self.Labels = np.argmax(Log_Probabilities, axis=3).astype(np.int32)

        # Allocate memory buffers once to avoid memory churn across iterations
        Energy = np.empty((D, H, W), dtype=np.float64)
        Best_Energy = np.empty((D, H, W), dtype=np.float64)
        Best_Label = np.empty((D, H, W), dtype=np.int32)

        for Iteration in range(self.Max_Iterations):
            Best_Energy.fill(np.inf)
            np.copyto(Best_Label, self.Labels)

            for K_Class in range(K):
                # Unary potential: -log P(x_i | K_Class) calculated in-place
                np.negative(Log_Probabilities[..., K_Class], out=Energy)

                # Pairwise Potts spatial prior: accumulate neighbor mismatches in-place
                for Dz, Dy, Dx in Neighbors:
                    Neighbor_Labels = self._Shifted_View(self.Labels, Dz, Dy, Dx)
                    Energy += np.where(Neighbor_Labels != K_Class, self.Beta, 0.0)

                # Update best label wherever candidate class achieves strictly lower energy
                Improved = Energy < Best_Energy
                Best_Energy[Improved] = Energy[Improved]
                Best_Label[Improved] = K_Class

            Changes = int(np.sum(Best_Label != self.Labels))
            np.copyto(self.Labels, Best_Label)

            print(
                f"[HMRF] Iteration {Iteration + 1}/{self.Max_Iterations}: {Changes} label updates"
            )

            if Changes == 0:
                print("[HMRF] Spatial optimization converged.")
                break

            if Changes < Min_Changes:
                Stalled_Count += 1
                if Stalled_Count >= self.Patience:
                    print(
                        f"[HMRF] Converged below {self.Convergence_Percent:.4%} "
                        f"threshold for {self.Patience} iterations."
                    )
                    break
            else:
                Stalled_Count = 0

        return self.Labels

    def _Shifted_View(
        self,
        Array: np.ndarray,
        Dz: int,
        Dy: int,
        Dx: int,
    ) -> np.ndarray:
        """Construct boundary-padded neighbor view without full volume duplication."""
        D, H, W = Array.shape
        Result = np.full((D, H, W), -1, dtype=Array.dtype)

        Sz = slice(max(-Dz, 0), D - max(Dz, 0) or None)
        Dz_Slice = slice(max(Dz, 0), D - max(-Dz, 0) or None)
        Sy = slice(max(-Dy, 0), H - max(Dy, 0) or None)
        Dy_Slice = slice(max(Dy, 0), H - max(-Dy, 0) or None)
        Sx = slice(max(-Dx, 0), W - max(Dx, 0) or None)
        Dx_Slice = slice(max(Dx, 0), W - max(-Dx, 0) or None)

        Result[Dz_Slice, Dy_Slice, Dx_Slice] = Array[Sz, Sy, Sx]
        return Result

    def _Get_Neighbors(self) -> List[Tuple[int, int, int]]:
        """Get relative offset directions for chosen spatial connectivity."""
        if self.Connectivity == 6:
            return [
                (-1, 0, 0),
                (1, 0, 0),
                (0, -1, 0),
                (0, 1, 0),
                (0, 0, -1),
                (0, 0, 1),
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

        raise ValueError(f"Connectivity {self.Connectivity} not supported. Choose 6 or 26.")
