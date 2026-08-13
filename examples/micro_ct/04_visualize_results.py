"""04 — Static visualization of saved segmentation results (no napari).

Generates matplotlib overview figures from the artifacts produced by the
previous steps:

    - ``preprocessed_volume.npz``            (step 01)
    - ``gmm_probabilities.npy`` or           (step 02a)
      ``sparse_bayesian_probabilities.npy``  (step 02b)
    - ``hmrf_labels.npy``                    (step 03, optional)

For a few representative Z slices it shows the processed intensity, the
argmax label map, and the per-voxel confidence (max probability); if
``hmrf_labels.npy`` exists it also shows the HMRF labels.  All output is
static PNG, saved under ``data/micro_ct/output/figures/``.
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

# ---------------------------------------------------------------------------
# Tunable parameters.
# ---------------------------------------------------------------------------
PROBS_FILE = "gmm_probabilities.npy"  # or "sparse_bayesian_probabilities.npy"
SLICE_INDICES = None  # e.g. [50, 100, 150]; None = auto-pick 3 slices


def main() -> None:
    """Produce static overview figures from saved segmentation artifacts."""
    Paths = get_micro_ct_paths()
    ensure_dirs(Paths)

    Output_Dir = Paths["output"]
    Figures_Dir = Paths["figures"]
    Processed_Path = Paths["processed"] / "preprocessed_volume.npz"
    Probs_Path = Output_Dir / PROBS_FILE
    Hmrf_Path = Output_Dir / "hmrf_labels.npy"

    Processed = Load_From_Numpy(Processed_Path, lazy=True)
    Probs = Load_From_Numpy(Probs_Path, lazy=True)
    D, H, W, K = Probs.shape
    print(f"[04_Visualize] Processed: {Processed.shape}, Probs: {Probs.shape} (K={K})")

    if SLICE_INDICES is None:
        Slice_Indices = [D // 4, D // 2, 3 * D // 4]
    else:
        Slice_Indices = SLICE_INDICES

    Has_Hmrf = Hmrf_Path.exists()

    for Z in Slice_Indices:
        Prob_Slice = Load_From_Numpy_Slab(Probs_Path, Z, Z + 1, dtype=np.float32)[0]
        Label_Slice = Prob_Slice.argmax(axis=-1)
        Confidence = Prob_Slice.max(axis=-1)

        Fig, Axes = plt.subplots(1, 3 if not Has_Hmrf else 4, figsize=(18, 6))
        Axes = np.atleast_1d(Axes)

        Axes[0].imshow(Processed[Z], cmap="gray")
        Axes[0].set_title(f"Processed — Z={Z}")
        Axes[0].axis("off")

        Axes[1].imshow(Label_Slice, cmap="tab10", vmin=0, vmax=K - 1)
        Axes[1].set_title(f"Labels — Z={Z}")
        Axes[1].axis("off")

        Im = Axes[2].imshow(Confidence, cmap="viridis", vmin=0, vmax=1)
        Axes[2].set_title(f"Confidence — Z={Z}")
        Axes[2].axis("off")
        Fig.colorbar(Im, ax=Axes[2], shrink=0.8, label="max probability")

        if Has_Hmrf:
            Labels_Hmrf = Load_From_Numpy_Slab(Hmrf_Path, Z, Z + 1, dtype=np.int32)[0]
            Axes[3].imshow(Labels_Hmrf, cmap="tab10", vmin=0, vmax=K - 1)
            Axes[3].set_title(f"HMRF — Z={Z}")
            Axes[3].axis("off")

        Fig.suptitle(f"Segmentation overview — slice {Z}", fontsize=14)
        Fig.tight_layout()
        Fig.savefig(Figures_Dir / f"segmentation_overview_z{Z:04d}.png", dpi=150)
        plt.close(Fig)

    print(f"[04_Visualize] Saved {len(Slice_Indices)} overview figure(s) -> {Figures_Dir}")


if __name__ == "__main__":
    main()
