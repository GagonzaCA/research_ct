"""03 — HMRF spatial regularization of GMM probabilities.

Replicates notebook ``04_spatial_hmrf``.

    1. Load the preprocessed volume and a (D, H, W, K) probability volume.
    2. Convert probabilities to log-space on a concrete Z-slab (memory-bounded).
    3. Run :class:`research_ct.segmentation.hmrf.Hmrf_Segmenter` (ICM with a
       Potts prior) to produce spatially regularized labels.
    4. Save ``hmrf_labels.npy`` and a GMM-vs-HMRF comparison figure.

Select which segmentation to refine with ``SEGMENTATION_SOURCE``
(``"flat"`` for ``02a``, ``"sparse"`` for ``02b``).  By default only a test
Z-slab is processed to keep peak RAM to a single slab.
"""

import sys
from pathlib import Path

# Make the repository root (for ``examples.*``) and ``src/`` importable.
_ROOT = Path(__file__).resolve().parents[2]
for _Entry in (str(_ROOT), str(_ROOT / "src")):
    if _Entry not in sys.path:
        sys.path.insert(0, _Entry)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from examples.common import ensure_dirs, get_micro_ct_paths
from research_ct.io.volume_saver import Load_From_Numpy, Load_From_Numpy_Slab
from research_ct.segmentation.hmrf import Hmrf_Segmenter

# ---------------------------------------------------------------------------
# Tunable parameters.
# ---------------------------------------------------------------------------
SEGMENTATION_SOURCE = "flat"  # "flat" (02a) or "sparse" (02b)
TEST_Z_START = 0
TEST_Z_STOP = 50  # process at most this many Z slices; None = full depth
BETA = 0.2  # Potts smoothness strength (low = fine detail, high = smooth)
MAX_ITERATIONS = 100
CONNECTIVITY = 6  # 6 or 26
CONVERGENCE_PERCENT = 0.01  # fraction of total voxels (0.1 %)
PATIENCE = 4  # consecutive stalled iterations before stopping


def main() -> None:
    """Run HMRF on a test Z-slab and export labels + comparison figure."""
    Paths = get_micro_ct_paths()
    ensure_dirs(Paths)

    Output_Dir = Paths["output"]
    Figures_Dir = Paths["figures"]
    Processed_Path = Paths["processed"] / "preprocessed_volume.npz"

    if SEGMENTATION_SOURCE == "flat":
        Probs_Path = Output_Dir / "gmm_probabilities.npy"
    elif SEGMENTATION_SOURCE == "sparse":
        Probs_Path = Output_Dir / "sparse_bayesian_probabilities.npy"
    else:
        raise ValueError(f"Unknown SEGMENTATION_SOURCE '{SEGMENTATION_SOURCE}'.")

    # 1. Load processed volume (lazy) and probability volume (lazy, for shape).
    Processed = Load_From_Numpy(Processed_Path, lazy=True)
    Probs = Load_From_Numpy(Probs_Path, lazy=True)
    D, H, W, K = Probs.shape
    print(f"[03_Hmrf] Processed: {Processed.shape}, Probs: {Probs.shape} (K={K})")

    # 2. Materialize the test Z-slab and convert to log-probabilities in place.
    Z_Stop = TEST_Z_STOP if TEST_Z_STOP is not None else D
    Z_Stop = min(Z_Stop, D)
    Probs_Slab = Load_From_Numpy_Slab(Probs_Path, TEST_Z_START, Z_Stop, dtype=np.float32)
    np.clip(Probs_Slab, 1e-10, 1.0, out=Probs_Slab)
    np.log(Probs_Slab, out=Probs_Slab)  # now Log_Probs
    Log_Probs = Probs_Slab
    print(f"[03_Hmrf] Log-probs slab: {Log_Probs.shape}")

    # 3. Derive the unregularized GMM labels for comparison.
    Labels_Gmm = Log_Probs.argmax(axis=-1).astype(np.int32)

    # 4. Run HMRF.
    Hmrf = Hmrf_Segmenter(
        Beta=BETA,
        Max_Iterations=MAX_ITERATIONS,
        Connectivity=CONNECTIVITY,
        Convergence_Percent=CONVERGENCE_PERCENT,
        Patience=PATIENCE,
    )
    Labels_Hmrf = Hmrf.Fit(Log_Probs)

    # 5. Save HMRF labels (test slab only).
    Labels_Path = Output_Dir / "hmrf_labels.npy"
    np.save(Labels_Path, Labels_Hmrf)
    print(f"[03_Hmrf] Saved HMRF labels -> {Labels_Path}")

    # 6. GMM-vs-HMRF comparison figure on three representative slices.
    Num_Slices = Labels_Hmrf.shape[0]
    Slice_Indices = [Num_Slices // 4, Num_Slices // 2, 3 * Num_Slices // 4]
    Fig, Axes = plt.subplots(3, 3, figsize=(15, 15), constrained_layout=True)

    for Col, Z in enumerate(Slice_Indices):
        Axes[0, Col].imshow(Processed[Z], cmap="gray")
        Axes[0, Col].set_title(f"Processed — Z={Z}")
        Axes[0, Col].axis("off")

        Axes[1, Col].imshow(Labels_Gmm[Z], cmap="tab10", vmin=0, vmax=K - 1)
        Axes[1, Col].set_title(f"GMM — Z={Z}")
        Axes[1, Col].axis("off")

        Axes[2, Col].imshow(Labels_Hmrf[Z], cmap="tab10", vmin=0, vmax=K - 1)
        Axes[2, Col].set_title(f"HMRF — Z={Z}")
        Axes[2, Col].axis("off")

    Axes[0, 0].set_ylabel("Intensity", fontsize=12)
    Axes[1, 0].set_ylabel("GMM Only", fontsize=12)
    Axes[2, 0].set_ylabel("HMRF", fontsize=12)
    Fig.suptitle("Spatial Regularization Comparison", fontsize=14)
    Fig.savefig(Figures_Dir / "hmrf_comparison.png", dpi=150)
    plt.close(Fig)
    print(f"[03_Hmrf] Saved comparison figure -> {Figures_Dir / 'hmrf_comparison.png'}")


if __name__ == "__main__":
    main()
