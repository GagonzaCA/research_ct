"""01 — Inspect raw micro-CT data and run preprocessing.

Replicates notebooks ``01_explore_raw_data`` and ``02_run_preprocessing`` as a
standalone script:

    1. Load the raw TIFF slice stack from ``data/micro_ct/raw/``.
    2. Infer scan metadata from the array properties.
    3. Run the statistics-first ROI-aware preprocessing pipeline
       (:func:`research_ct.preprocessing.pipeline_gmm.Preprocess_For_Gmm`).
    4. Save the preprocessed volume and diagnostic histogram plots.

Run from anywhere::

    python examples/micro_ct/01_inspect_and_preprocess.py

Before running, place your TIFF slices in ``data/micro_ct/raw/``.  Outputs are
written under ``data/micro_ct/output/`` (``processed/`` and ``figures/``).
"""

import sys
from pathlib import Path

# Make the repository root (for ``examples.*``) and ``src/`` (for the
# ``research_ct`` / ``xrf`` packages) importable from any working directory.
_ROOT = Path(__file__).resolve().parents[2]
for _Entry in (str(_ROOT), str(_ROOT / "src")):
    if _Entry not in sys.path:
        sys.path.insert(0, _Entry)

import matplotlib

matplotlib.use("Agg")  # non-interactive backend for headless runs
import matplotlib.pyplot as plt

from examples.common import ensure_dirs, get_micro_ct_paths
from research_ct.io.metadata_parser import Load_Metadata
from research_ct.io.volume_loader import Load_Slice_Stack
from research_ct.io.volume_saver import Save_As_Numpy

# Import the pipeline instead 
from research_ct.preprocessing.pipeline_gmm import Preprocess_For_Gmm

from research_ct.visualization.histogram_diagnostics_viewer import (
    Plot_Histogram_Comparison,
    Plot_Slice_Histograms,
)

# ---------------------------------------------------------------------------
# Tunable parameters — adjust these before running.
# ---------------------------------------------------------------------------
SLICE_PATTERN = "*.tif*"
SLICE_STOP = 201  # load at most this many slices; set to None to load all
VOXEL_SIZE_UM = 40.0  # physical voxel size, if known
NUM_PAGES = 200  # expected page count, if known

# Updated parameters for the optimized GMM pipeline
PREPROCESSING_PARAMS = {
    "Air_Threshold_Percentile": 10.0,  # Generates ROI mask to exclude air noise
    "Noise_Sigma": 0.8,  # Preserves central limit theorem Gaussian shapes
    "Clip_Low_Percentile": 0.1,  # Calculated strictly on foreground ROI
    "Clip_High_Percentile": 99.9,  # Calculated strictly on foreground ROI
    "Bit_Depth": 32,  # User-selected depth: 32 (float), 16 (int), or 8 (int)
    "Verbose": True,
}


def main() -> None:
    """Load raw data, preprocess it, and export diagnostics."""
    Paths = get_micro_ct_paths()
    ensure_dirs(Paths)

    Raw_Dir = Paths["raw"]
    Figures_Dir = Paths["figures"]
    Processed_Dir = Paths["processed"]

    # 1. Load the raw volume.
    print(f"[01_Inspect_Preprocess] Loading slices from {Raw_Dir} ...")
    Volume = Load_Slice_Stack(Raw_Dir, Pattern=SLICE_PATTERN, Stop=SLICE_STOP)
    print(f"[01_Inspect_Preprocess] Volume shape: {Volume.shape}, dtype: {Volume.dtype}")

    # 2. Infer metadata (TIFFs carry no equipment metadata).
    Metadata = Load_Metadata(Volume, Voxel_Size_Um=VOXEL_SIZE_UM, Num_Pages=NUM_PAGES)
    print(f"[01_Inspect_Preprocess] Inferred shape: {Metadata.Volume_Shape}")
    print(f"[01_Inspect_Preprocess] Bit depth: {Metadata.Bit_Depth}")
    print(f"[01_Inspect_Preprocess] Voxel size (um): {Metadata.Voxel_Size_Um}")

    # 3. Preprocessing (ROI masking + noise reduction + normalization).
    print("[01_Inspect_Preprocess] Running optimized preprocessing pipeline ...")
    Processed_Volume, Diagnostics = Preprocess_For_Gmm(Volume, **PREPROCESSING_PARAMS)

    # 4. Histogram diagnostics.
    Plot_Histogram_Comparison(
        Raw_Volume=Volume,
        Processed_Volume=Processed_Volume,
        Output_Path=Figures_Dir / "histogram_before_after.png",
        N_Bins=256,
        Exclude_Zero=True,
        Focus_Range=None,
    )
    Plot_Slice_Histograms(
        Volume,
        Figures_Dir / "histogram_per_slice_raw.png",
        N_Slices=5,
        Exclude_Zero=True,
    )
    Plot_Slice_Histograms(
        Processed_Volume,
        Figures_Dir / "histogram_per_slice_processed.png",
        N_Slices=5,
        Exclude_Zero=True,
    )

    # 5. Save the preprocessed volume for the segmentation steps.
    Save_As_Numpy(Processed_Volume, Processed_Dir / "preprocessed_volume.npz")
    print(
        f"[01_Inspect_Preprocess] Saved preprocessed volume -> "
        f"{Processed_Dir / 'preprocessed_volume.npz'}"
    )


if __name__ == "__main__":
    main()
