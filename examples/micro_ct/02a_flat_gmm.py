"""02a — Flat GMM segmentation with automatic BIC K selection.

Replicates notebook ``03_gmm_and_hierarchical_segmentation`` (flat GMM part).

    1. Load ``preprocessed_volume.npz`` produced by step 01.
    2. Flatten and sub-sample voxels for tractable fitting.
    3. Fit :class:`research_ct.segmentation.gmm_fitter.Gmm_Fitter`, which scans
       K = Min_Components..Max_Components and keeps the model with the minimum
       BIC.
    4. Stream the posterior probabilities of the *selected* model to
       ``gmm_probabilities.npy`` with shape (D, H, W, K), plus a small JSON with
       the selected K and fitted parameters.

Run from anywhere::

    python examples/micro_ct/02a_flat_gmm.py

Requires ``data/micro_ct/output/processed/preprocessed_volume.npz`` (step 01).
"""

import json
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
from research_ct.io.volume_saver import Load_From_Numpy, Reduce_Streaming
from research_ct.segmentation.gmm_fitter import Gmm_Fitter
from research_ct.visualization.plot_distributions import plot_gmm_components

# ---------------------------------------------------------------------------
# Tunable parameters.
# ---------------------------------------------------------------------------
MIN_COMPONENTS = 2
MAX_COMPONENTS = 16
COVARIANCE_TYPE = "full"
SAMPLE_SIZE = 900_000  # voxels sub-sampled for fitting; use None for all
RANDOM_SEED = 42


def _Predict_Probabilities_Slab(Fitter: Gmm_Fitter) -> callable:
    """Return a slab-wise reducer that predicts (chunk, H, W, K) probabilities."""

    def _Reducer(Slab: np.ndarray) -> np.ndarray:
        Flat = Slab.reshape(-1, 1)
        Probs = Fitter.Predict_Probabilities(Flat)
        return Probs.astype(np.float32).reshape(Slab.shape[0], Slab.shape[1], Slab.shape[2], -1)

    return _Reducer


def main() -> None:
    """Fit the flat GMM and stream the optimal-K probabilities to disk."""
    Paths = get_micro_ct_paths()
    ensure_dirs(Paths)

    Processed_Path = Paths["processed"] / "preprocessed_volume.npz"
    Output_Dir = Paths["output"]
    Figures_Dir = Paths["figures"]

    # 1. Load preprocessed volume lazily (memmap).
    Processed = Load_From_Numpy(Processed_Path, lazy=True)
    Shape = Processed.shape
    print(f"[02a_Flat_Gmm] Loaded preprocessed volume: {Shape}")

    # 2. Flatten and sub-sample.
    Flat = Processed.ravel().reshape(-1, 1)
    if SAMPLE_SIZE is not None and Flat.shape[0] > SAMPLE_SIZE:
        Indices = np.random.RandomState(RANDOM_SEED).choice(
            Flat.shape[0], SAMPLE_SIZE, replace=False
        )
        Sampled = Flat[Indices]
        print(f"[02a_Flat_Gmm] Sampled {Sampled.shape[0]:,} voxels for fitting.")
    else:
        Sampled = Flat

    # 3. Fit with BIC-based K selection.
    Fitter = Gmm_Fitter(
        Min_Components=MIN_COMPONENTS,
        Max_Components=MAX_COMPONENTS,
        Covariance_Type=COVARIANCE_TYPE,
    )
    Fitter.Fit(Sampled, Verbose=True)
    K_Opt = Fitter.Num_Components
    print(f"[02a_Flat_Gmm] Optimal K = {K_Opt}")

    # 4. BIC-vs-K plot.
    Fig, Ax = plt.subplots(figsize=(8, 5))
    K_Range = list(range(Fitter.Min_Components, Fitter.Max_Components + 1))
    Ax.plot(K_Range, Fitter.Bic_Scores, "o-", linewidth=2, markersize=8, color="steelblue")
    Ax.axvline(K_Opt, color="red", linestyle="--", label=f"Selected K={K_Opt}")
    Ax.set_xlabel("Number of Components (K)")
    Ax.set_ylabel("BIC Score")
    Ax.set_title("BIC-Based Model Selection")
    Ax.legend()
    Ax.grid(True, alpha=0.3)
    Fig.savefig(Figures_Dir / "bic_selection.png", dpi=300, bbox_inches="tight")
    plt.close(Fig)

    # 5. Component-decomposition plot (small sample for speed).
    Plot_Sample = Sampled[np.random.RandomState(RANDOM_SEED).choice(
        len(Sampled), min(100_000, len(Sampled)), replace=False
    )].ravel()
    Fig = plot_gmm_components(Plot_Sample, Fitter.Model)
    Fig.savefig(Figures_Dir / "gmm_components.png", dpi=150, bbox_inches="tight")
    plt.close(Fig)

    # 6. Save the optimal-K model parameters.
    Stats = Fitter.Get_Material_Statistics()
    Params = {
        "num_components": int(K_Opt),
        "means": Stats["Means"].tolist(),
        "covariances": [np.asarray(Cov).tolist() for Cov in Fitter.Model.covariances_],
        "weights": Stats["Weights"].tolist(),
        "bic_scores": Fitter.Bic_Scores,
        "min_components": Fitter.Min_Components,
        "max_components": Fitter.Max_Components,
    }
    with open(Output_Dir / "gmm_model_parameters.json", "w", encoding="utf-8") as File:
        json.dump(Params, File, indent=2)

    # 7. Stream full-volume probabilities of the selected model to disk.
    Probs_Path = Output_Dir / "gmm_probabilities.npy"
    Reduce_Streaming(
        Processed_Path,
        Probs_Path,
        Reduce_Fn=_Predict_Probabilities_Slab(Fitter),
        chunk_size=10,
        key="volume",
    )
    print(f"[02a_Flat_Gmm] Saved probabilities (D,H,W,{K_Opt}) -> {Probs_Path}")


if __name__ == "__main__":
    main()
