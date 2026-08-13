"""02b — Sparse Bayesian GMM segmentation (automatic K discovery).

Replicates the ``Sparse Bayesian GMM`` section of notebook
``03_gmm_and_hierarchical_segmentation``.

    1. Load ``preprocessed_volume.npz`` (step 01).
    2. Flatten and sub-sample voxels.
    3. Fit :class:`research_ct.segmentation.sparse_bayesian_gmm.Sparse_Bayesian_Gmm`,
       which uses a Dirichlet weight prior to collapse unneeded components to
       zero and prunes them.
    4. Stream the posterior probabilities of the *active* components to
       ``sparse_bayesian_probabilities.npy`` with shape (D, H, W, K_active).

This is the alternative to ``02a_flat_gmm.py``: run either, then point step 03
at the resulting probabilities file by editing ``SEGMENTATION_SOURCE``.
"""

import json
import sys
from pathlib import Path

# Make the repository root (for ``examples.*``) and ``src/`` importable.
_ROOT = Path(__file__).resolve().parents[2]
for _Entry in (str(_ROOT), str(_ROOT / "src")):
    if _Entry not in sys.path:
        sys.path.insert(0, _Entry)

import numpy as np

from examples.common import ensure_dirs, get_micro_ct_paths
from research_ct.io.volume_saver import Load_From_Numpy, Reduce_Streaming
from research_ct.segmentation.sparse_bayesian_gmm import Sparse_Bayesian_Gmm

# ---------------------------------------------------------------------------
# Tunable parameters.
# ---------------------------------------------------------------------------
MAX_COMPONENTS = 16
WEIGHT_CONCENTRATION_PRIOR = 1.0
WEIGHT_THRESHOLD = 1e-3
MIN_SAMPLES = 1000
COVARIANCE_TYPE = "full"
SAMPLE_SIZE = 300_000  # voxels sub-sampled for fitting; use None for all
RANDOM_SEED = 42


def _Predict_Probabilities_Slab(Model: Sparse_Bayesian_Gmm) -> callable:
    """Return a slab-wise reducer that predicts (chunk, H, W, K_active) probs."""

    def _Reducer(Slab: np.ndarray) -> np.ndarray:
        Flat = Slab.reshape(-1, 1)
        Probs = Model.Predict_Probabilities(Flat)
        return Probs.astype(np.float32).reshape(Slab.shape[0], Slab.shape[1], Slab.shape[2], -1)

    return _Reducer


def main() -> None:
    """Fit the sparse Bayesian GMM and stream active-K probabilities to disk."""
    Paths = get_micro_ct_paths()
    ensure_dirs(Paths)

    Processed_Path = Paths["processed"] / "preprocessed_volume.npz"
    Output_Dir = Paths["output"]

    # 1. Load preprocessed volume lazily.
    Processed = Load_From_Numpy(Processed_Path, lazy=True)
    print(f"[02b_Sparse_Gmm] Loaded preprocessed volume: {Processed.shape}")

    # 2. Flatten and sub-sample.
    Flat = Processed.ravel().reshape(-1, 1)
    if SAMPLE_SIZE is not None and Flat.shape[0] > SAMPLE_SIZE:
        Indices = np.random.RandomState(RANDOM_SEED).choice(
            Flat.shape[0], SAMPLE_SIZE, replace=False
        )
        Sampled = Flat[Indices]
        print(f"[02b_Sparse_Gmm] Sampled {Sampled.shape[0]:,} voxels for fitting.")
    else:
        Sampled = Flat

    # 3. Fit the overcomplete sparse Bayesian GMM.
    Model = Sparse_Bayesian_Gmm(
        Max_Components=MAX_COMPONENTS,
        Weight_Concentration_Prior=WEIGHT_CONCENTRATION_PRIOR,
        Weight_Threshold=WEIGHT_THRESHOLD,
        Min_Samples=MIN_SAMPLES,
        Covariance_Type=COVARIANCE_TYPE,
    )
    Model.Fit(Sampled, Verbose=True)
    K_Active = Model.Num_Active_Components
    Stats = Model.Get_Material_Statistics()
    print(f"[02b_Sparse_Gmm] Active components: {K_Active}/{Model.Max_Components}")
    print(f"[02b_Sparse_Gmm] Active means: {Stats['Means']}")
    print(f"[02b_Sparse_Gmm] Active weights: {Stats['Weights']}")

    # 4. Save model parameters for reference.
    Params = {
        "num_active_components": int(K_Active),
        "max_components": Model.Max_Components,
        "means": Stats["Means"].tolist(),
        "variances": [np.asarray(Var).tolist() for Var in Stats["Variances"]],
        "weights": Stats["Weights"].tolist(),
        "active_indices": Stats["Active_Indices"].tolist(),
    }
    with open(Output_Dir / "sparse_bayesian_parameters.json", "w", encoding="utf-8") as File:
        json.dump(Params, File, indent=2)

    # 5. Stream full-volume probabilities of the active components to disk.
    Probs_Path = Output_Dir / "sparse_bayesian_probabilities.npy"
    Reduce_Streaming(
        Processed_Path,
        Probs_Path,
        Reduce_Fn=_Predict_Probabilities_Slab(Model),
        chunk_size=10,
        key="volume",
    )
    print(f"[02b_Sparse_Gmm] Saved probabilities (D,H,W,{K_Active}) -> {Probs_Path}")


if __name__ == "__main__":
    main()
