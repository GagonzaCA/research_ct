"""06 — Calculate geometric normals for isolated classes.

Replicates the 3D surface normal evaluation for a specific segmented class:

    1. Loads `preprocessed_volume.npz` and `gmm_probabilities.npy`.
    2. Converts the GMM probabilities into hard labels via argmax.
    3. Isolates a specific target class (e.g., ink).
    4. Calculates 3D geometric normals encoded as RGB arrays.
    5. Saves the resulting 4D (D,H,W,3) volume and static slice previews.

Run from anywhere::

    python examples/micro_ct/06_geometric_normals.py
"""

import sys
from pathlib import Path

# Make the repository root and src/ importable from any working directory.
_ROOT = Path(__file__).resolve().parents[2]
for _Entry in (str(_ROOT), str(_ROOT / "src")):
    if _Entry not in sys.path:
        sys.path.insert(0, _Entry)

import matplotlib

matplotlib.use("Agg")  # non-interactive backend for headless runs
import matplotlib.pyplot as plt
import numpy as np

from examples.common import ensure_dirs, get_micro_ct_paths
from research_ct.io.volume_saver import Load_From_Numpy, Save_As_Numpy
from research_ct.analysis import Calculate_Class_Normals

# ---------------------------------------------------------------------------
# Tunable parameters — adjust these before running.
# ---------------------------------------------------------------------------
PROBS_FILE = "gmm_probabilities.npy"  # Input from step 02a
TARGET_CLASS = 2  # The integer label corresponding to your target (e.g., ink)
SLICE_INDICES = [50, 100, 150]  # Z-slices to render as static PNGs


def main() -> None:
    """Calculate geometric normals and export visualization figures."""
    Paths = get_micro_ct_paths()
    ensure_dirs(Paths)

    Processed_Path = Paths["processed"] / "preprocessed_volume.npz"
    Probs_Path = Paths["output"] / PROBS_FILE
    Normals_Out_Path = Paths["processed"] / f"class_{TARGET_CLASS}_normals.npz"
    Figures_Dir = Paths["figures"]

    # 1. Load the required volumes into memory
    print(f"[06_Geometric_Normals] Loading volumes...")
    Processed = Load_From_Numpy(Processed_Path)
    Probs = Load_From_Numpy(Probs_Path)

    # 2. Extract hard labels (argmax) as done in 04_visualize.py
    print("[06_Geometric_Normals] Converting probabilities to hard labels...")
    Labels = Probs.argmax(axis=-1).astype(np.uint8)

    # 3. Calculate the RGB geometric normals
    print(f"[06_Geometric_Normals] Calculating 3D normals for Class {TARGET_CLASS}...")
    RGB_Normals = Calculate_Class_Normals(
        Labels_Volume=Labels,
        Target_Class=TARGET_CLASS,
        Base_Intensity_Volume=Processed,
        Display_Out=True,
    )

    # 4. Save the full 4D volume for 3D viewers (e.g., 3D Slicer / Fiji)
    print(
        f"[06_Geometric_Normals] Saving volume (shape: {RGB_Normals.shape}) to {Normals_Out_Path}"
    )
    Save_As_Numpy(RGB_Normals, Normals_Out_Path)

    # 5. Generate static 2D slice previews for quick review
    print("[06_Geometric_Normals] Generating static slice previews...")
    for Z in SLICE_INDICES:
        if Z >= RGB_Normals.shape[0]:
            print(f"  -> Skipping Z={Z} (out of bounds)")
            continue

        Fig, Axes = plt.subplots(1, 2, figsize=(12, 6))
        Axes = np.atleast_1d(Axes)

        # Left: Original preprocessed intensity
        Axes[0].imshow(Processed[Z], cmap="gray")
        Axes[0].set_title(f"Processed Intensity — Z={Z}")
        Axes[0].axis("off")

        # Right: The newly calculated RGB normal surface
        Axes[1].imshow(RGB_Normals[Z])
        Axes[1].set_title(f"Class {TARGET_CLASS} Normals (RGB) — Z={Z}")
        Axes[1].axis("off")

        Fig.suptitle(f"Geometric Normals Preview — slice {Z}", fontsize=14)
        Fig.tight_layout()
        Fig.savefig(Figures_Dir / f"normals_overview_z{Z:04d}.png", dpi=150)
        plt.close(Fig)

    print(f"[06_Geometric_Normals] Saved static figure(s) -> {Figures_Dir}")


if __name__ == "__main__":
    main()
