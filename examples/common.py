"""Shared path resolution and directory helpers for the example scripts.

Every example script (``examples/micro_ct/...`` and ``examples/xrf/...``)
imports this module to locate the repository root and to obtain consistent
data/output directories, so that a new student only has to worry about where
the data goes and not about path bookkeeping.

Conventions used here mirror the notebooks: the repository root is the folder
that contains ``src/``, and raw data lives under ``data/``.  All module-level
constants use ``Pascal_Case_With_Underscores`` to match the project style.
"""

from pathlib import Path


def get_project_root() -> Path:
    """Return the repository root, found by walking up until ``src/`` is seen.

    The search starts from this file's location (``examples/``) rather than
    the current working directory, so the result is correct no matter where
    the script is invoked from.

    Returns:
        Path: Absolute path to the repository root.

    Raises:
        RuntimeError: If no ``src/`` directory is found in any parent folder.
    """
    Candidate = Path(__file__).resolve().parent
    while not (Candidate / "src").exists():
        Parent = Candidate.parent
        if Parent == Candidate:
            raise RuntimeError(
                "Could not locate the project root: no 'src/' directory was "
                "found in any parent of examples/common.py."
            )
        Candidate = Parent
    return Candidate


def get_micro_ct_paths() -> dict:
    """Return the micro-CT data/output directory map.

    Layout (mirrors the micro-CT notebooks, namespaced under ``data/micro_ct/``):

        data/micro_ct/
        ├── raw/                   # TIFF slice stack (student-provided input)
        └── output/
            ├── processed/         # preprocessed_volume.npz, labels, probs
            ├── figures/           # static PNG plots
            └── diagnostics/       # edge-strength / histogram diagnostics

    Returns:
        dict: Mapping of logical names (``data``, ``raw``, ``output``,
        ``processed``, ``figures``, ``diagnostics``) to :class:`Path` objects.
    """
    Root = get_project_root()
    Data_Dir = Root / "data" / "micro_ct"
    Output_Dir = Data_Dir / "output"
    return {
        "data": Data_Dir,
        "raw": Data_Dir / "raw",
        "output": Output_Dir,
        "processed": Output_Dir / "processed",
        "figures": Output_Dir / "figures",
        "diagnostics": Output_Dir / "diagnostics",
    }


def get_xrf_paths() -> dict:
    """Return the XRF data/output directory map.

    Layout:

        data/xrf/
        ├── bcf/                   # one .bcf per page (bcf/page_name/*.bcf)
        ├── pages/                 # one folder of elemental TIFFs per page
        └── output/
            ├── processed/         # masks, valid pixels, CLR, labels, meta
            ├── figures/           # cluster visuals
            ├── diagnostics/       # optional diagnostics
            └── comparison/        # category signatures, rarity scores
                └── montages/      # assembled cluster montages

    Returns:
        dict: Mapping of logical names (``data``, ``bcf``, ``pages``,
        ``output``, ``processed``, ``figures``, ``diagnostics``,
        ``comparison``, ``montages``) to :class:`Path` objects.
    """
    Root = get_project_root()
    Data_Dir = Root / "data" / "xrf"
    Output_Dir = Data_Dir / "output"
    Comparison_Dir = Output_Dir / "comparison"
    return {
        "data": Data_Dir,
        "bcf": Data_Dir / "bcf",
        "pages": Data_Dir / "pages",
        "output": Output_Dir,
        "processed": Output_Dir / "processed",
        "figures": Output_Dir / "figures",
        "diagnostics": Output_Dir / "diagnostics",
        "comparison": Comparison_Dir,
        "montages": Comparison_Dir / "montages",
    }


def ensure_dirs(Paths: dict) -> None:
    """Create every directory in a path map if it does not exist.

    The creation is idempotent (``mkdir(parents=True, exist_ok=True)``), so it
    is safe to call at the top of every example script.  Input directories
    (e.g. ``raw``, ``bcf``, ``pages``) are created too, which gives the
    student a visible skeleton showing where to drop data.

    Args:
        Paths: A mapping returned by :func:`get_micro_ct_paths` or
            :func:`get_xrf_paths`.
    """
    for Path_Value in Paths.values():
        Path_Value.mkdir(parents=True, exist_ok=True)
