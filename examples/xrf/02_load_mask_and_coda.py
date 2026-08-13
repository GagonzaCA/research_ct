"""02 — Load elemental TIFFs, compute the valid-pixel mask, and apply CLR.

Replicates notebooks ``01_xrf_loading_and_masking`` and ``02_coda_transformations``
for every page under ``data/xrf/pages/``.

For each ``page_name/`` folder:

    1. Glob every ``.tif``/``.tiff`` (one elemental channel per file) and stack
       them with :class:`xrf.io.xrf_loader.Xrf_Loader.Load_Element_Stack`.
    2. Compute the total-intensity mask with
       :meth:`Xrf_Loader.Compute_Intensity_Mask`.
    3. Save ``<page>_mask.npy`` and ``<page>_valid_pixels.npy``.
    4. Apply the CLR transform with
       :class:`xrf.transforms.coda.Clr_Transformer.Apply_Clr_Transform` and save
       ``<page>_clr.npy``.

Runs standalone over all pages, or per-page via ``run(Page_Dir)`` (used by
``run_all_pages.py``).
"""

import sys
from pathlib import Path

# Make the repository root (for ``examples.*``) and ``src/`` importable.
_ROOT = Path(__file__).resolve().parents[2]
for _Entry in (str(_ROOT), str(_ROOT / "src")):
    if _Entry not in sys.path:
        sys.path.insert(0, _Entry)

import numpy as np

from examples.common import ensure_dirs, get_xrf_paths
from xrf.config import Xrf_Preprocessing_Config
from xrf.io.xrf_loader import Xrf_Loader
from xrf.transforms.coda import Clr_Transformer

# ---------------------------------------------------------------------------
# Tunable parameters.
# ---------------------------------------------------------------------------
ELEMENT_GLOB = "*.tif*"  # matches .tif, .tiff (including *_raw.tiff)


def run(Page_Dir: Path) -> None:
    """Load, mask, and CLR-transform a single page folder.

    Args:
        Page_Dir: Folder containing one elemental TIFF per channel, e.g.
            ``data/xrf/pages/page_001/``.
    """
    Paths = get_xrf_paths()
    ensure_dirs(Paths)

    Processed_Dir = Paths["processed"]
    Config = Xrf_Preprocessing_Config()

    Page_Id = Page_Dir.name
    File_Paths = sorted(Page_Dir.glob(ELEMENT_GLOB))
    if not File_Paths:
        print(f"[02_Load_Mask_Coda] No elemental TIFFs in {Page_Dir}; skipping.")
        return

    Stack = Xrf_Loader.Load_Element_Stack(File_Paths, Dtype=Config.Compute_Dtype)
    Mask, Valid_Pixels = Xrf_Loader.Compute_Intensity_Mask(Stack, Config.Noise_Threshold)
    print(
        f"[02_Load_Mask_Coda] {Page_Id}: stack {Stack.shape}, "
        f"valid pixels {Valid_Pixels.shape[0]:,}/{Mask.size:,}"
    )

    np.save(Processed_Dir / f"{Page_Id}_mask.npy", Mask)
    np.save(Processed_Dir / f"{Page_Id}_valid_pixels.npy", Valid_Pixels)

    Clr_Data = Clr_Transformer.Apply_Clr_Transform(
        Valid_Pixels, Delta=Config.Zero_Replacement_Delta
    )
    np.save(Processed_Dir / f"{Page_Id}_clr.npy", Clr_Data)
    print(f"[02_Load_Mask_Coda] {Page_Id}: saved mask, valid_pixels, clr -> {Processed_Dir}")


def run_all() -> None:
    """Run ``run`` over every page folder under ``data/xrf/pages/``."""
    Paths = get_xrf_paths()
    ensure_dirs(Paths)

    Page_Dirs = sorted(p for p in Paths["pages"].iterdir() if p.is_dir())
    if not Page_Dirs:
        print(f"[02_Load_Mask_Coda] No page folders found under {Paths['pages']}.")
        return

    for Page_Dir in Page_Dirs:
        run(Page_Dir)


def main() -> None:
    """Entry point when executed directly."""
    run_all()


if __name__ == "__main__":
    main()
