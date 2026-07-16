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
        Log_Probabilities: np.ndarray,
    ) -> np.ndarray:
        """Run ICM optimization for HMRF.

        Args:
            Log_Probabilities: Log p(x_i | k) for each class k.
                Shape: (D, H, W, K). Must be a writable in-memory array
                for the slice being processed — not a raw memmap.

        Returns:
            Integer labels, shape (D, H, W).
        """
        D, H, W, K = Log_Probabilities.shape
        Neighbors = self._Get_Neighbors()

        # Initialize from MAP — no extra allocation, argmax is O(D*H*W*K)
        self.Labels = np.argmax(Log_Probabilities, axis=3).astype(np.int32)

        for Iteration in range(self.Max_Iterations):

            # Energy array reused across K_Class iterations — allocated once
            Energy = np.empty((D, H, W), dtype=np.float32)
            Best_Energy = np.full((D, H, W), np.inf, dtype=np.float32)
            Best_Label = self.Labels.copy()

            for K_Class in range(K):
                # Likelihood term — view, no copy
                np.negative(Log_Probabilities[..., K_Class], out=Energy)

                # Spatial prior — accumulate neighbor disagreements in-place
                for Dz, Dy, Dx in Neighbors:
                    # Compute shifted label view with padding
                    Neighbor_Labels = self._Shifted_View(self.Labels, Dz, Dy, Dx)
                    # Add Beta wherever neighbor disagrees with candidate K_Class
                    Energy += np.where(Neighbor_Labels != K_Class, self.Beta, 0.0)

                # Update best label wherever this class has lower energy
                Improved = Energy < Best_Energy
                Best_Energy[Improved] = Energy[Improved]
                Best_Label[Improved] = K_Class

            Changes = int(np.sum(Best_Label != self.Labels))
            np.copyto(self.Labels, Best_Label)

            del Best_Energy, Best_Label, Energy

            print(f"[HMRF] Iteration {Iteration + 1}: {Changes} changes")

            if Changes == 0:
                print("[HMRF] Converged")
                break

        return self.Labels

    def _Shifted_View(
        self,
        Array: np.ndarray,
        Dz: int,
        Dy: int,
        Dx: int,
    ) -> np.ndarray:
        """Return neighbor values as a (D,H,W) array, boundary-padded with -1
        so boundary voxels never falsely match any valid label."""
        D, H, W = Array.shape
        Result = np.full((D, H, W), -1, dtype=Array.dtype)

        # Source and destination slices for each axis
        Sz = slice(max(-Dz, 0), D - max(Dz, 0) or None)
        Dz_Slice = slice(max(Dz, 0), D - max(-Dz, 0) or None)
        Sy = slice(max(-Dy, 0), H - max(Dy, 0) or None)
        Dy_Slice = slice(max(Dy, 0), H - max(-Dy, 0) or None)
        Sx = slice(max(-Dx, 0), W - max(Dx, 0) or None)
        Dx_Slice = slice(max(Dx, 0), W - max(-Dx, 0) or None)

        Result[Dz_Slice, Dy_Slice, Dx_Slice] = Array[Sz, Sy, Sx]
        return Result

    def _Get_Neighbors(self) -> List[Tuple[int, int, int]]:
        """Get neighbor offsets for chosen connectivity."""
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

        raise ValueError(f"Connectivity {self.Connectivity} not supported")
