"""03 — PCA + GMM clustering of CLR-transformed XRF data.

Replicates notebook ``03_gmm_spatial_clustering`` for every processed page.

For each page:

    1. Load ``<page>_clr.npy`` (step 02).
    2. Compute the BIC curve over ``K`` and auto-select the optimal ``K``
       (minimum BIC).
    3. Fit/Predict with :class:`xrf.segmentation.xrf_gmm.Xrf_Gmm_Segmenter`.
    4. Save ``<page>_labels.npy``, ``<page>_probabilities.npy``,
       ``<page>_class_map.npy``, and ``<page>_meta.json`` (with ``optimal_k``).
    5. Export the class map and per-class isolated PNGs to ``figures/``.

Runs standalone over all pages, or per-page via ``run(Page_Dir)``.
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
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

from examples.common import ensure_dirs, get_xrf_paths
from xrf.config import Xrf_Segmentation_Config
from xrf.segmentation.xrf_gmm import Xrf_Gmm_Segmenter
from xrf.spatial.spatial_analyzer import Spatial_Analyzer


def run(Page_Dir: Path) -> None:
    """Cluster a single processed page with PCA + GMM.

    Args:
        Page_Dir: The page folder; only its name (page id) is used to locate
            the CLR/mask files in ``processed/``.
    """
    Paths = get_xrf_paths()
    ensure_dirs(Paths)

    Processed_Dir = Paths["processed"]
    Figures_Dir = Paths["figures"]

    Page_Id = Page_Dir.name
    Clr_Path = Processed_Dir / f"{Page_Id}_clr.npy"
    Mask_Path = Processed_Dir / f"{Page_Id}_mask.npy"
    if not Clr_Path.exists():
        print(f"[03_Gmm_Cluster] Missing {Clr_Path.name}; run step 02 first. Skipping {Page_Id}.")
        return

    Clr_Data = np.load(Clr_Path)
    Seg_Config = Xrf_Segmentation_Config()
    K_Range = list(range(Seg_Config.Gmm_Min_K, Seg_Config.Gmm_Max_K + 1))

    # BIC curve + auto-selection.
    Bic_Scores = Xrf_Gmm_Segmenter.Compute_Bic_Curve(
        Clr_Data, K_Range=K_Range, Variance_Ratio=Seg_Config.Pca_Variance_Ratio
    )
    Optimal_K = min(Bic_Scores, key=Bic_Scores.get)
    print(f"[03_Gmm_Cluster] {Page_Id}: BIC={Bic_Scores}, optimal K={Optimal_K}")

    Fig, Ax = plt.subplots(figsize=(7, 4))
    Ax.plot(list(Bic_Scores.keys()), list(Bic_Scores.values()), marker="o")
    Ax.axvline(Optimal_K, color="red", linestyle="--", label=f"Selected K={Optimal_K}")
    Ax.set_title("Bayesian Information Criterion (BIC)")
    Ax.set_xlabel("Number of Components (K)")
    Ax.set_ylabel("BIC Score (Lower is Better)")
    Ax.legend()
    Ax.grid(True)
    Fig.savefig(Figures_Dir / f"{Page_Id}_bic.png", dpi=150, bbox_inches="tight")
    plt.close(Fig)

    # Fit / predict with the selected K.
    Labels, Probabilities, _, _ = Xrf_Gmm_Segmenter.Fit_Predict(
        Clr_Data,
        Num_Components=Optimal_K,
        Variance_Ratio=Seg_Config.Pca_Variance_Ratio,
        Covariance_Type=Seg_Config.Covariance_Type,
    )

    np.save(Processed_Dir / f"{Page_Id}_labels.npy", Labels)
    np.save(Processed_Dir / f"{Page_Id}_probabilities.npy", Probabilities)

    # Reconstruct 2D class map and export.
    Mask = np.load(Mask_Path)
    Class_Map = Spatial_Analyzer.Reconstruct_Class_Map(Labels, Mask)
    np.save(Processed_Dir / f"{Page_Id}_class_map.npy", Class_Map)

    with open(Processed_Dir / f"{Page_Id}_meta.json", "w", encoding="utf-8") as File:
        json.dump({"optimal_k": int(Optimal_K)}, File, indent=2)

    # Class-map figure.
    Cmap = plt.get_cmap("tab10", Optimal_K)
    Cmap.set_bad(color="black")
    Fig, Ax = plt.subplots(figsize=(8, 8), dpi=300)
    Ax.imshow(Class_Map, cmap=Cmap, vmin=-0.5, vmax=Optimal_K - 0.5, interpolation="nearest")
    Ax.set_title(f"{Page_Id} — class map (K={Optimal_K})")
    Ax.axis("off")
    Legend_Patches = [mpatches.Patch(color=Cmap(i), label=f"Class {i}") for i in range(Optimal_K)]
    Ax.legend(handles=Legend_Patches, title="Assigned Classes", loc="center left",
              bbox_to_anchor=(1.05, 0.5), frameon=False)
    Fig.savefig(Figures_Dir / f"{Page_Id}_class_map.png", bbox_inches="tight", facecolor="white")
    plt.close(Fig)

    # Per-class isolated PNGs (used later by the montage step).
    for K in range(Optimal_K):
        Isolated_Mask = (Class_Map == K).astype(np.uint8)
        Binary_Cmap = mcolors.ListedColormap(["black", Cmap(K)])
        Fig, Ax = plt.subplots(figsize=(6, 6), dpi=300)
        Ax.imshow(Isolated_Mask, cmap=Binary_Cmap, interpolation="nearest")
        Ax.set_title(f"Class {K} Isolated", fontsize=14, weight="bold", color=Cmap(K))
        Ax.axis("off")
        Fig.savefig(Figures_Dir / f"{Page_Id}_Cluster_{K}_Visual.png",
                    bbox_inches="tight", facecolor="white")
        plt.close(Fig)

    print(f"[03_Gmm_Cluster] {Page_Id}: labels, probabilities, class_map, meta saved.")


def run_all() -> None:
    """Run ``run`` over every page folder under ``data/xrf/pages/``."""
    Paths = get_xrf_paths()
    ensure_dirs(Paths)

    Page_Dirs = sorted(p for p in Paths["pages"].iterdir() if p.is_dir())
    for Page_Dir in Page_Dirs:
        run(Page_Dir)


def main() -> None:
    """Entry point when executed directly."""
    run_all()


if __name__ == "__main__":
    main()
