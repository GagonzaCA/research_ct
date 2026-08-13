"""Batch runner — process every XRF page through steps 02→05.

Discovers all ``page_name/`` folders under ``data/xrf/pages/`` and, for each
one, runs the per-page processing chain in order:

    02_load_mask_and_coda.run()   # mask + CLR
    03_gmm_cluster.run()          # PCA + GMM clustering
    04_leaf_signature.run()       # abundance signature
    05_spatial_analyzer.run()     # spatial descriptors

Step 01 (BCF extraction) and the comparison steps 06/07 are intentionally
left out of the batch: BCF extraction is a one-time ingest, and categorization
is a human-judgment step.

The step scripts are loaded from their file paths with ``importlib`` because
their names start with digits and therefore are not valid Python identifiers.

Run from anywhere::

    python examples/xrf/run_all_pages.py
"""

import importlib.util
import sys
from pathlib import Path

# Make the repository root (for ``examples.*``) and ``src/`` importable.
_ROOT = Path(__file__).resolve().parents[2]
for _Entry in (str(_ROOT), str(_ROOT / "src")):
    if _Entry not in sys.path:
        sys.path.insert(0, _Entry)

from examples.common import ensure_dirs, get_xrf_paths

# Ordered per-page processing steps (file name -> human label).
_STEPS = [
    ("02_load_mask_and_coda.py", "load + mask + CLR"),
    ("03_gmm_cluster.py", "PCA + GMM clustering"),
    ("04_leaf_signature.py", "leaf signature"),
    ("05_spatial_analyzer.py", "spatial analysis"),
]


def _Load_Step(File_Name: str):
    """Import a sibling step module by file path (names start with digits)."""
    Step_Path = Path(__file__).with_name(File_Name)
    Spec = importlib.util.spec_from_file_location(Step_Path.stem, Step_Path)
    Module = importlib.util.module_from_spec(Spec)
    Spec.loader.exec_module(Module)
    return Module


def main() -> None:
    """Run the 02→05 chain over every page folder."""
    Paths = get_xrf_paths()
    ensure_dirs(Paths)

    Pages_Dir = Paths["pages"]
    Page_Dirs = sorted(p for p in Pages_Dir.iterdir() if p.is_dir())
    if not Page_Dirs:
        print(f"[Run_All_Pages] No page folders found under {Pages_Dir}.")
        return

    Steps = [_Load_Step(File_Name) for File_Name, _ in _STEPS]
    print(f"[Run_All_Pages] Found {len(Page_Dirs)} page(s).")

    for Page_Dir in Page_Dirs:
        print(f"\n[Run_All_Pages] ==== Processing {Page_Dir.name} ====")
        for (_, Label), Step in zip(_STEPS, Steps):
            print(f"[Run_All_Pages] --- {Label} ---")
            Step.run(Page_Dir)

    print("\n[Run_All_Pages] Batch processing complete.")


if __name__ == "__main__":
    main()
