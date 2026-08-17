"""05 — Interactive 3D napari viewer for segmentation results.

Launches a napari viewer with the preprocessed volume, hard labels, and
class probability layers from the previous steps.

    - ``preprocessed_volume.npz``               (step 01)
    - ``gmm_probabilities.npy``                 (step 02a)
    - ``gmm_labels.npy``                        (derived automatically from probs)

Set ``SEGMENTATION_SOURCE = "sparse"`` to load the Bayesian GMM outputs from
step 02b instead.

The viewer blocks until the napari window is closed.
"""

import sys
from pathlib import Path

# Make the repository root (for ``examples.*``) and ``src/`` importable.
_ROOT = Path(__file__).resolve().parents[2]
for _Entry in (str(_ROOT), str(_ROOT / "src")):
    if _Entry not in sys.path:
        sys.path.insert(0, _Entry)

from examples.common import get_micro_ct_paths
from research_ct.io.volume_saver import (
    Load_From_Numpy,
    Compute_Labels_From_Probabilities,
)
from research_ct.visualization.napari_viewer import launch_napari_viewer

# ---------------------------------------------------------------------------
# Tunable parameters.
# ---------------------------------------------------------------------------
SEGMENTATION_SOURCE = "flat"  # "flat" (02a) or "sparse" (02b)
RENDER_3D = False             # start viewer in 3D mode


def main() -> None:
    """Load saved segmentation results and open the interactive napari viewer."""
    Paths = get_micro_ct_paths()
    Output_Dir = Paths["output"]

    Processed_Path = Paths["processed"] / "preprocessed_volume.npz"

    if SEGMENTATION_SOURCE == "flat":
        Probs_Path = Output_Dir / "gmm_probabilities.npy"
        Labels_Path = Output_Dir / "gmm_labels.npy"
        Source_Label = "flat GMM"
    elif SEGMENTATION_SOURCE == "sparse":
        Probs_Path = Output_Dir / "sparse_bayesian_probabilities.npy"
        Labels_Path = Output_Dir / "sparse_bayesian_labels.npy"
        Source_Label = "sparse Bayesian GMM"
    else:
        raise ValueError(f"Unknown SEGMENTATION_SOURCE '{SEGMENTATION_SOURCE}'.")

    if not Probs_Path.exists():
        raise FileNotFoundError(
            f"Probability file not found: {Probs_Path}\n"
            f"Run {'02a_flat_gmm.py' if SEGMENTATION_SOURCE == 'flat' else '02b_sparse_bayesian_gmm.py'} first."
        )

    # Step 02a/02b only saves probabilities, not hard labels.
    # Derive them chunked (memory-bounded) if the file is missing.
    if not Labels_Path.exists():
        print(f"[05_Napari_Viewer] Labels file missing — deriving labels from "
              f"probabilities (slab-by-slab) …")
        Compute_Labels_From_Probabilities(Probs_Path, Labels_Path)

    # Lazy memmap — no data enters RAM until napari indexes into it.
    Processed = Load_From_Numpy(Processed_Path, lazy=True)
    Probs = Load_From_Numpy(Probs_Path, lazy=True)
    Labels = Load_From_Numpy(Labels_Path, lazy=True)

    print(
        f"[05_Napari_Viewer] Loaded: {Processed.shape}, "
        f"Labels: {Labels.shape}, Probs: {Probs.shape}"
    )
    print(f"[05_Napari_Viewer] Source: {Source_Label}")
    print("[05_Napari_Viewer] Launching napari — close the viewer window to exit.")

    launch_napari_viewer(
        Volume=Processed,
        Labels=Labels,
        Probabilities=Probs,
        # Entropy is intentionally omitted — no uncertainty overlay.
        Render_3d=RENDER_3D,
        Title="micro-CT Segmentation — Interactive Viewer",
    )


if __name__ == "__main__":
    main()