"""06 — Assign structural categories to processed pages.

Replicates notebook ``05_page_categorization`` as a non-interactive script.

The category vocabulary lives in ``Xrf_Comparison_Config.Allowed_Categories``
(text_only, chapter_start, illustration, mixed, unknown).  This is a
human-judgment step: edit ``PAGE_CATEGORIES`` below to map each page id to its
category, then run the script.  Already-tagged pages are skipped; pages left
out of ``PAGE_CATEGORIES`` and still untagged are reported but not modified.

Run from anywhere::

    python examples/xrf/06_page_categorization.py

Only pages that already have a ``page_*_meta.json`` (from step 03) are
considered.
"""

import sys
from pathlib import Path

# Make the repository root (for ``examples.*``) and ``src/`` importable.
_ROOT = Path(__file__).resolve().parents[2]
for _Entry in (str(_ROOT), str(_ROOT / "src")):
    if _Entry not in sys.path:
        sys.path.insert(0, _Entry)

from examples.common import ensure_dirs, get_xrf_paths
from xrf.comparison.category_registry import Category_Registry
from xrf.config import Xrf_Comparison_Config

# ---------------------------------------------------------------------------
# Human-judgment step: edit this mapping with the structural category of each
# page.  Leave a page out to skip it (it stays untagged).
# ---------------------------------------------------------------------------
PAGE_CATEGORIES = {
    # "page_001": "text_only",
    # "page_002": "illustration",
    # "page_003": "chapter_start",
}


def main() -> None:
    """Tag each page listed in ``PAGE_CATEGORIES`` and print a summary."""
    Paths = get_xrf_paths()
    ensure_dirs(Paths)

    Processed_Dir = Paths["processed"]
    Config = Xrf_Comparison_Config()

    Meta_Paths = sorted(Processed_Dir.glob("page_*_meta.json"))
    print(f"[06_Categorize] Found {len(Meta_Paths)} processed page(s).")

    for Meta_Path in Meta_Paths:
        Page_Id = Meta_Path.stem.replace("_meta", "")

        if Category_Registry.Load_Page_Category(Meta_Path) is not None:
            continue

        Category = PAGE_CATEGORIES.get(Page_Id)
        if Category is None:
            print(f"[06_Categorize] {Page_Id}: untagged (not listed in PAGE_CATEGORIES).")
            continue

        try:
            Category_Registry.Write_Page_Category(
                Meta_Path, Category, Config, Tag_Source="manual"
            )
        except ValueError as Error:
            print(f"[06_Categorize] Skipped {Page_Id}: {Error}")

    # Summary grouped by category.
    Tagged_Pages = Category_Registry.List_Tagged_Pages(Processed_Dir, Config)
    for Category, Page_Ids in Tagged_Pages.items():
        Flag = (
            " (low-confidence: below Min_Pages_Per_Category)"
            if Category != "untagged" and len(Page_Ids) < Config.Min_Pages_Per_Category
            else ""
        )
        print(f"[06_Categorize] {Category}: {len(Page_Ids)} page(s){Flag} -> {Page_Ids}")


if __name__ == "__main__":
    main()
