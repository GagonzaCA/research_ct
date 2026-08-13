"""07 — Category-level comparison and rarity review of tagged pages.

Replicates notebooks ``06_category_signature_comparison`` and
``07_rarity_review`` as a single static script.

    1. Load per-page abundances, categories, and spatial descriptors from
       ``data/xrf/output/processed/`` (only pages tagged in step 06).
    2. Aggregate per-category signatures and spreads
       (:class:`xrf.comparison.category_signatures.Category_Signature_Aggregator`).
    3. Aggregate spatial descriptors by category
       (:class:`xrf.comparison.spatial_comparison.Category_Spatial_Comparator`).
    4. Rank pages by rarity (:class:`xrf.comparison.rarity_scoring.Rarity_Scorer`).
    5. Save comparison artifacts and plots under
       ``data/xrf/output/comparison/`` (and ``montages/`` when cluster visuals
       exist).

Run from anywhere::

    python examples/xrf/07_compare_signatures.py
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

from examples.common import ensure_dirs, get_xrf_paths
from xrf.comparison.category_registry import Category_Registry
from xrf.comparison.category_signatures import Category_Signature_Aggregator
from xrf.comparison.rarity_scoring import Rarity_Scorer
from xrf.comparison.spatial_comparison import Category_Spatial_Comparator
from xrf.config import Leaf_Signature_Config, Xrf_Comparison_Config
from xrf.signatures.leaf_signature import Leaf_Signature_Extractor
from xrf.spatial.spatial_analyzer import Spatial_Analyzer
from xrf.visualization.xrf_plots import (
    Build_Category_Montage,
    Plot_Category_Signature_Bars,
    Plot_Category_Signature_Radar,
)


def main() -> None:
    """Aggregate tagged pages by category, produce plots, and rank rarity."""
    Paths = get_xrf_paths()
    ensure_dirs(Paths)

    Processed_Dir = Paths["processed"]
    Figures_Dir = Paths["figures"]
    Comparison_Dir = Paths["comparison"]
    Montages_Dir = Paths["montages"]
    Comparison_Dir.mkdir(parents=True, exist_ok=True)
    Montages_Dir.mkdir(parents=True, exist_ok=True)

    Config = Xrf_Comparison_Config()
    Sig_Config = Leaf_Signature_Config()

    # 1. Load tagged pages: signatures, categories, spatial descriptors.
    Page_Signatures = {}
    Page_Categories = {}
    Page_Spatial_Descriptors = {}

    for Meta_Path in sorted(Processed_Dir.glob("page_*_meta.json")):
        Page_Id = Meta_Path.stem.replace("_meta", "")
        Category = Category_Registry.Load_Page_Category(Meta_Path)
        if Category is None:
            print(f"[07_Compare] Skipping {Page_Id}: not tagged (run step 06).")
            continue

        with open(Meta_Path, "r", encoding="utf-8") as File:
            Meta = json.load(File)
        Optimal_K = int(Meta["optimal_k"])

        Labels = np.load(Processed_Dir / f"{Page_Id}_labels.npy")
        Class_Map = np.load(Processed_Dir / f"{Page_Id}_class_map.npy")

        Page_Signatures[Page_Id] = Leaf_Signature_Extractor.Compute_Abundances(
            Labels, Num_Classes=Optimal_K
        )
        Page_Categories[Page_Id] = Category
        Page_Spatial_Descriptors[Page_Id] = {
            str(K): Spatial_Analyzer.Extract_Spatial_Descriptors(
                Class_Map, Target_Class=K, Min_Size=Sig_Config.Min_Region_Size
            )
            for K in range(Optimal_K)
        }

    print(
        f"[07_Compare] Loaded {len(Page_Signatures)} tagged page(s) across "
        f"{len(set(Page_Categories.values()))} category/ies."
    )

    if not Page_Signatures:
        print("[07_Compare] Nothing to compare: no tagged pages. Exiting.")
        return

    # 2. Aggregate signatures and spreads by category.
    Category_Signatures = Category_Signature_Aggregator.Aggregate_By_Category(
        Page_Signatures, Page_Categories
    )
    Category_Spread = Category_Signature_Aggregator.Compute_Category_Spread(
        Page_Signatures, Page_Categories
    )

    for Category, Signature in Category_Signatures.items():
        np.save(Comparison_Dir / f"category_signature_{Category}.npy", Signature)
        np.save(Comparison_Dir / f"category_spread_{Category}.npy", Category_Spread[Category])
        print(
            f"[07_Compare] {Category}: mean={np.round(Signature, 3)}, "
            f"mad={np.round(Category_Spread[Category], 3)}"
        )

    # 3. Aggregate spatial descriptors by category.
    Category_Region_Stats = Category_Spatial_Comparator.Aggregate_Region_Stats(
        Page_Spatial_Descriptors, Page_Categories
    )
    with open(Comparison_Dir / "category_spatial_stats.json", "w", encoding="utf-8") as File:
        json.dump(Category_Region_Stats, File, indent=2)

    # 4. Plots.
    Plot_Category_Signature_Bars(
        Category_Signatures, Category_Spread, Comparison_Dir / "category_signature_bars.png"
    )
    Plot_Category_Signature_Radar(
        Category_Signatures, Comparison_Dir / "category_signature_radar.png"
    )

    # 5. Rarity ranking.
    Rankings = Rarity_Scorer.Rank_Pages_By_Rarity(Page_Signatures, Page_Categories, Config)
    Rarity_Scores = [
        {"page_id": Page_Id, "max_abs_deviation": Deviation, "is_flagged": Is_Flagged}
        for Page_Id, Deviation, Is_Flagged in Rankings
    ]
    with open(Comparison_Dir / "rarity_scores.json", "w", encoding="utf-8") as File:
        json.dump(Rarity_Scores, File, indent=2)

    # 6. Comparison summary.
    Tagged_Pages = Category_Registry.List_Tagged_Pages(Processed_Dir, Config)
    Summary = {
        "page_counts": {Category: len(Page_Ids) for Category, Page_Ids in Tagged_Pages.items()},
        "low_confidence_categories": [
            Category
            for Category, Page_Ids in Tagged_Pages.items()
            if Category != "untagged" and len(Page_Ids) < Config.Min_Pages_Per_Category
        ],
        "config": {
            "Allowed_Categories": Config.Allowed_Categories,
            "Min_Pages_Per_Category": Config.Min_Pages_Per_Category,
            "Rarity_Mad_Threshold": Config.Rarity_Mad_Threshold,
            "Min_Region_Size": Config.Min_Region_Size,
        },
    }
    with open(Comparison_Dir / "category_comparison_summary.json", "w", encoding="utf-8") as File:
        json.dump(Summary, File, indent=2)

    # 7. Optional montage of cluster visuals.
    Cluster_Visual_Paths = sorted(Figures_Dir.glob("*_Cluster_*_Visual.png"))
    if Cluster_Visual_Paths:
        for Category in Category_Signatures:
            Build_Category_Montage(
                Cluster_Visual_Paths,
                Montages_Dir / f"{Category}_cluster_montage.png",
                Grid_Cols=4,
            )
    else:
        print(f"[07_Compare] No cluster visuals found under {Figures_Dir}; skipping montage.")

    print(f"[07_Compare] Comparison artifacts saved -> {Comparison_Dir}")


if __name__ == "__main__":
    main()
