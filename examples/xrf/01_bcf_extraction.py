"""01 — Extract Bruker BCF hypercubes into per-page elemental TIFFs.

Replicates ``xrf_bcf_extraction`` notebook as a batch script.

    1. Scan ``data/xrf/bcf/`` for ``.bcf`` files.  The expected layout is one
       sub-folder per page (``bcf/page_name/page.bcf``); a flat layout
       (``bcf/*.bcf``) is also accepted, in which case the BCF stem is used as
       the page name.
    2. For each BCF, run
       :class:`xrf.preprocessing.bcf_extractor.Bcf_Element_Extractor` to export
       one 32-bit ``_raw.tiff`` per requested element, into
       ``data/xrf/pages/<page_name>/`` (ready for step 02).

Run from anywhere::

    python examples/xrf/01_bcf_extraction.py

Edit ``TARGET_ELEMENTS`` to match the emission lines of interest for your
dataset.
"""

import sys
from pathlib import Path

# Make the repository root (for ``examples.*``) and ``src/`` importable.
_ROOT = Path(__file__).resolve().parents[2]
for _Entry in (str(_ROOT), str(_ROOT / "src")):
    if _Entry not in sys.path:
        sys.path.insert(0, _Entry)

from examples.common import ensure_dirs, get_xrf_paths
from xrf.config import Bcf_Extraction_Config
from xrf.preprocessing.bcf_extractor import Bcf_Element_Extractor

# ---------------------------------------------------------------------------
# Tunable parameters.
# ---------------------------------------------------------------------------
# Elements (or element+line) to extract from every BCF.  Heavy elements (Z > 40)
# auto-resolve to L-alpha; light elements auto-resolve to K-alpha.
TARGET_ELEMENTS = ["Au_La", "Fe_Ka", "Cu_Ka", "Hg_La", "Pb_La", "As_Ka"]


def run() -> None:
    """Extract every BCF under ``data/xrf/bcf/`` into ``data/xrf/pages/``."""
    Paths = get_xrf_paths()
    ensure_dirs(Paths)

    Bcf_Dir = Paths["bcf"]
    Pages_Dir = Paths["pages"]

    Bcf_Paths = sorted(Bcf_Dir.rglob("*.bcf"))
    if not Bcf_Paths:
        print(f"[01_Bcf_Extraction] No .bcf files found under {Bcf_Dir}.")
        return

    Config = Bcf_Extraction_Config()
    Extractor = Bcf_Element_Extractor(
        Cutoff_At_Kv=Config.Cutoff_At_Kv,
        Peak_Width_Kev=Config.Peak_Width_Kev,
        Bg_Width_Kev=Config.Bg_Width_Kev,
        Bg_Offset_Kev=Config.Bg_Offset_Kev,
    )

    print(f"[01_Bcf_Extraction] Found {len(Bcf_Paths)} BCF file(s).")
    for Bcf_Path in Bcf_Paths:
        # Page name = enclosing sub-folder when nested, else the BCF stem.
        Page_Name = Bcf_Path.parent.name if Bcf_Path.parent != Bcf_Dir else Bcf_Path.stem
        Output_Dir = Pages_Dir / Page_Name
        print(f"[01_Bcf_Extraction] Page '{Page_Name}' <- {Bcf_Path.name}")
        Extractor.Extract_And_Save(Bcf_Path, TARGET_ELEMENTS, Output_Dir)

    print("[01_Bcf_Extraction] Extraction complete.")


def main() -> None:
    """Entry point when executed directly."""
    run()


if __name__ == "__main__":
    main()
