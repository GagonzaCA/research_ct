"""05 — Spatial analysis of reconstructed class maps.

Replicates the spatial-descriptor part of notebook ``04_leaf_signatures`` for
every processed page.

For each page:

    1. Load ``<page>_class_map.npy`` and ``<page>_meta.json`` (step 03).
    2. For every class, compute connected-component descriptors with
       :meth:`xrf.spatial.spatial_analyzer.Spatial_Analyzer.Extract_Spatial_Descriptors`
       (region count and average region size).
    3. Save ``<page>_spatial.json`` and merge the descriptors into
       ``<page>_meta.json``.

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

import numpy as np

from examples.common import ensure_dirs, get_xrf_paths
from xrf.config import Leaf_Signature_Config
from xrf.spatial.spatial_analyzer import Spatial_Analyzer


def run(Page_Dir: Path) -> None:
    """Compute and save spatial descriptors for a single page.

    Args:
        Page_Dir: The page folder; only its name (page id) is used to locate
            the class map / meta files in ``processed/``.
    """
    Paths = get_xrf_paths()
    ensure_dirs(Paths)

    Processed_Dir = Paths["processed"]
    Page_Id = Page_Dir.name
    Sig_Config = Leaf_Signature_Config()

    Class_Map_Path = Processed_Dir / f"{Page_Id}_class_map.npy"
    Meta_Path = Processed_Dir / f"{Page_Id}_meta.json"
    if not Class_Map_Path.exists() or not Meta_Path.exists():
        print(f"[05_Spatial_Analyzer] Missing class_map/meta for {Page_Id}; run step 03 "
              f"first. Skipping.")
        return

    Class_Map = np.load(Class_Map_Path)
    with open(Meta_Path, "r", encoding="utf-8") as File:
        Meta = json.load(File)
    Optimal_K = int(Meta["optimal_k"])

    Spatial_Features = {
        str(K): Spatial_Analyzer.Extract_Spatial_Descriptors(
            Class_Map, Target_Class=K, Min_Size=Sig_Config.Min_Region_Size
        )
        for K in range(Optimal_K)
    }

    with open(Processed_Dir / f"{Page_Id}_spatial.json", "w", encoding="utf-8") as File:
        json.dump(Spatial_Features, File, indent=2)

    Meta["spatial_descriptors"] = Spatial_Features
    with open(Meta_Path, "w", encoding="utf-8") as File:
        json.dump(Meta, File, indent=2)

    print(f"[05_Spatial_Analyzer] {Page_Id}: spatial descriptors for {Optimal_K} classes.")


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
