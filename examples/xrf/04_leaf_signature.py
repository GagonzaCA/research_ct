"""04 — Extract per-page leaf signatures (abundance vectors).

Replicates the abundance part of notebook ``04_leaf_signatures`` for every
processed page.

For each page:

    1. Load ``<page>_labels.npy`` and ``<page>_meta.json`` (step 03).
    2. Compute the area-abundance vector ``A_k`` with
       :meth:`xrf.signatures.leaf_signature.Leaf_Signature_Extractor.Compute_Abundances`.
    3. Save ``<page>_signature.npy`` and merge the abundances into
       ``<page>_meta.json``.

Spatial descriptors (the second half of the leaf signature) are handled by
``05_spatial_analyzer.py``.  Runs standalone over all pages, or per-page via
``run(Page_Dir)``.
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
from xrf.signatures.leaf_signature import Leaf_Signature_Extractor


def run(Page_Dir: Path) -> None:
    """Compute and save the abundance signature for a single page.

    Args:
        Page_Dir: The page folder; only its name (page id) is used to locate
            the labels/meta files in ``processed/``.
    """
    Paths = get_xrf_paths()
    ensure_dirs(Paths)

    Processed_Dir = Paths["processed"]
    Page_Id = Page_Dir.name

    Labels_Path = Processed_Dir / f"{Page_Id}_labels.npy"
    Meta_Path = Processed_Dir / f"{Page_Id}_meta.json"
    if not Labels_Path.exists() or not Meta_Path.exists():
        print(f"[04_Leaf_Signature] Missing labels/meta for {Page_Id}; run step 03 first. "
              f"Skipping.")
        return

    Labels = np.load(Labels_Path)
    with open(Meta_Path, "r", encoding="utf-8") as File:
        Meta = json.load(File)
    Optimal_K = int(Meta["optimal_k"])

    Abundances = Leaf_Signature_Extractor.Compute_Abundances(Labels, Num_Classes=Optimal_K)
    np.save(Processed_Dir / f"{Page_Id}_signature.npy", Abundances)

    Meta["abundances"] = Abundances.tolist()
    with open(Meta_Path, "w", encoding="utf-8") as File:
        json.dump(Meta, File, indent=2)

    print(f"[04_Leaf_Signature] {Page_Id}: abundances {np.round(Abundances, 3)}")


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
