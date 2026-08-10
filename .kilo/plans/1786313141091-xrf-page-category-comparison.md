# XRF Page-Category Comparison Extension — Implementation Plan

Source spec: `C:\Users\gabri\Downloads\xrf_page_category_extension_context.md` (read in full,
all 13 sections). This plan captures verified repo state, flags discrepancies between the
spec and the actual code, and gives the code agent a strict, step-gated build order.

`[Memory Bank: Active]` — read. None of the 11 documented conflicts (C-PIPE, C-NORM,
C-PRESET, C-DTYPE, C-MITIG, C-DPGMM, C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM) touch
the XRF comparison extension — all are CT-pipeline-specific and already marked resolved in
`activeContext.md`. No blocking conflict applies here.

## Verified current state (read directly, not assumed)

- `src/xrf/config.py` (63 lines): Spanish module docstring + Spanish Google-style docstrings.
  Only imports `from dataclasses import dataclass`. Contains `Xrf_Preprocessing_Config`,
  `Xrf_Segmentation_Config`, `Leaf_Signature_Config`. **No `field` or `List` imported yet** —
  adding `Xrf_Comparison_Config` requires adding `from dataclasses import dataclass, field`
  and `from typing import List` to the existing import block (additive only, per Rule 1).
- `src/xrf/io/xrf_loader.py` (72 lines): Spanish docstrings, defines `Path_Like = Union[str, Path]`
  and `Xrf_Loader` with `Load_Element_Stack` / `Compute_Intensity_Mask`. **No `json` import
  yet** — `Update_Page_Metadata` needs `import json` added to the top-level imports.
  `Path_Like` alias is reusable as-is.
- `src/xrf/signatures/leaf_signature.py` (47 lines): `Leaf_Signature_Extractor` with
  `Compute_Abundances` and `Compute_Weighted_Book_Signature` (weighted average via
  `np.average`). Confirms the reuse target referenced in spec §6.4.
- `src/xrf/spatial/spatial_analyzer.py` (65 lines): `Spatial_Analyzer.Extract_Spatial_Descriptors`
  returns `{"Num_Regiones": float, "Tamano_Promedio": float}` (Spanish keys!) — not
  `{mean_region_count, mean_region_size}` as spec §6.5 assumes. **Flag:** `Category_Spatial_Comparator.Aggregate_Region_Stats`
  must consume the actual dict keys (`Num_Regiones`, `Tamano_Promedio`) from
  `Extract_Spatial_Descriptors`, translating to English only in the *new* module's own
  output naming (`mean_region_count`, `mean_region_size`), not by touching `spatial_analyzer.py`.
- `src/xrf/visualization/xrf_plots.py`: confirmed empty (0 lines) — a real placeholder, matches
  spec §6.7.
- Real data on disk: only **one** processed page exists — `data/xrf/output/processed/page_001_*`.
  `page_001_meta.json` currently contains only `{"optimal_k": 8}` — **no `page_id`,
  `n_valid_pixels`, or any of the fields spec §7 assumes are already present.** This is much
  sparser than the spec's example schema. `Update_Page_Metadata` must merge fields into
  whatever keys already exist without assuming `page_id`/`n_valid_pixels` are present.
  Category tagging smoke test (build-order step 4) will only be able to exercise a single
  real page — acceptable for a round-trip smoke test, but not a real multi-page tagging pass.
- `data/xrf/output/figures/` has `Cluster_0_Visual.png` … `Cluster_7_Visual.png` (book-level,
  not per-category — there's currently no per-category cluster visualization to montage,
  since only one page/category exists so far). `Build_Category_Montage` just takes whatever
  paths are passed in — no change needed, just noting the montage will be thin until more
  pages are tagged.
- `notebooks/xrf/` already has `01_xrf_loading_and_masking.ipynb` … `04_leaf_signatures.ipynb`.
  **Discrepancy found:** spec §5 (file tree) and §12 decision D1 both say new notebooks should
  be numbered `05_page_categorization.ipynb`, `06_category_signature_comparison.ipynb`,
  `07_rarity_review.ipynb` (continuing after existing 01–04). But spec §8 and §13 (build order
  step 5/9) name them `01_page_categorization.ipynb`, `02_category_signature_comparison.ipynb`,
  `03_rarity_review.ipynb` — an internal contradiction in the spec. **Resolution: use `05_`,
  `06_`, `07_`** — this matches both D1's explicit instruction and the actual repo state
  (01–04 already taken). Flagged here per Rule 7; proceeding with 05/06/07 unless the user
  overrides.
- `src/xrf/__init__.py` re-exports each submodule's public class. New `comparison/__init__.py`
  should follow the same pattern (export `Category_Registry`, `Category_Signature_Aggregator`,
  `Category_Spatial_Comparator`, `Rarity_Scorer`); top-level `xrf/__init__.py` update is not
  spec'd — leave it untouched unless the user asks, since Section 5 doesn't list it as a file
  to touch.
- `tests/test_xrf/` does not exist yet (confirmed no matches) — fresh package, no collisions.
  Root `tests/conftest.py` has CT-only fixtures (`synthetic_volume`, etc.) — unrelated to this
  extension; the new `tests/test_xrf/conftest.py` is separate and additive.

## Ground rules carried into execution (from the user's message)

1. Show current `xrf/config.py` and `xrf/io/xrf_loader.py` contents before editing — **done
   above**; both files are confirmed compatible with the additive changes in spec §6.1/§6.2,
   modulo the import additions noted above. No other code in those two files changes.
2. Do not touch anything in `src/research_ct/`, `src/xrf/segmentation/`, `src/xrf/transforms/`,
   or `src/xrf/spatial/` except as explicitly listed in spec §5 (none of those three XRF
   subpackages are listed as touched — so they are fully off-limits).
3. One build-order step at a time; show diff after each; wait before continuing.
4. Match existing conventions: `Pascal_Case_With_Underscores`, Google-style docstrings in
   **English** for all new/added content (per D2 — but existing Spanish text in untouched
   parts of `config.py`/`xrf_loader.py` is left as-is, since Rule 1 forbids touching more than
   spec §6 requires), type hints everywhere, guard clauses raising specific exceptions,
   `[Bracketed_Name]` progress logs, dataclass configs, static methods with no instance state,
   lazy `matplotlib` imports inside functions. Section 11's table is the compliance checklist.
5. Write each test file alongside its module (not batched at the end); run `pytest` after each
   test file is added and report results before moving on.
6. Non-goals are hard boundaries: no CT–XRF fusion, no hypothesis testing/p-values, no
   automated/heuristic tagging implementation (schema field reserved only), no inter-rater
   tooling, no bootstrapped CIs. If a step seems to need one of these, stop and ask instead of
   improvising.
7. D1 (notebook numbering → resolved as 05/06/07 above), D2 (English for all new docstrings/
   identifiers), D3 (`Xrf_Comparison_Config` lives in the existing `xrf/config.py`, no new
   config file) are implemented as written; the one concrete conflict found (D1 numbering vs.
   §8/§13 text) is flagged above and resolved in D1's favor.
8. Soft 300-line limit per new file. Per spec §6, each new module has one class with 2–4
   static methods — all comfortably under 300 lines; no split anticipated. If any drafted file
   approaches the limit during implementation, stop and propose a split before writing it.

## Build order (gate after each step; wait for explicit go-ahead before the next)

1. **`xrf/config.py`** — add `Xrf_Comparison_Config` dataclass (English docstring, per §6.1
   verbatim) plus the two additive imports (`field`, `List`). Show diff.
2. **`xrf/io/xrf_loader.py`** — add `Update_Page_Metadata(Meta_Path, **Fields)` per §6.2
   (English docstring; `import json` added; raises `FileNotFoundError` if `Meta_Path` doesn't
   exist; reads existing JSON, merges `Fields`, writes back). Show diff.
3. **`xrf/comparison/__init__.py` + `category_registry.py`** implementing `Category_Registry`
   per §6.3, plus **`tests/test_xrf/conftest.py`** (only the registry-relevant fixtures needed
   at this point — synthetic `Page_Signatures`/`Page_Categories`/`Page_Spatial_Descriptors`
   fixtures can be added incrementally as later steps need them, or all up front if simpler —
   confirm with user which) and **`tests/test_xrf/test_comparison/test_category_registry.py`**
   per §9. Run `pytest tests/test_xrf/` and report results.
4. **Manual smoke test**: use `Category_Registry.Write_Page_Category` against the real
   `page_001_meta.json` (only real page available) to confirm the read/write round-trip works
   against actual on-disk data (which lacks `page_id`/`n_valid_pixels` — confirm merge behavior
   is correct regardless). Report the resulting JSON diff; do not commit this test tag unless
   the user confirms they want `page_001` actually tagged.
5. **`notebooks/xrf/05_page_categorization.ipynb`** — manual tagging notebook per §8, using the
   resolved 05/06/07 numbering.
6. **`xrf/comparison/category_signatures.py`** (`Category_Signature_Aggregator`, §6.4) and
   **`xrf/comparison/spatial_comparison.py`** (`Category_Spatial_Comparator`, §6.5 — consuming
   `Extract_Spatial_Descriptors`'s actual `Num_Regiones`/`Tamano_Promedio` keys as noted above)
   plus their tests (`test_category_signatures.py`, `test_spatial_comparison.py`). Run pytest
   after each test file, report results.
7. **`xrf/visualization/xrf_plots.py`** — implement `Plot_Category_Signature_Bars`,
   `Plot_Category_Signature_Radar`, `Build_Category_Montage` per §6.7 (lazy `matplotlib`
   import inside each function).
8. **`xrf/comparison/rarity_scoring.py`** (`Rarity_Scorer`, §6.6) +
   `tests/test_xrf/test_comparison/test_rarity_scoring.py` (including the `MAD == 0` →
   `RuntimeError` case). Run pytest, report results.
9. **`notebooks/xrf/06_category_signature_comparison.ipynb`** and
   **`notebooks/xrf/07_rarity_review.ipynb`** per §8.

## Validation

- After every new test file: `pytest tests/test_xrf/ -v` (and the full suite occasionally to
  confirm no cross-package breakage), results shown to the user before proceeding.
- Section 11's compliance table double-checked against the final diff of each file before
  moving to the next build-order step.

## Open item for the user (not resolved unilaterally)

- Step 3 conftest fixture scope: build all of `tests/test_xrf/conftest.py`'s fixtures
  (registry + signatures + spatial) up front in step 3, or add each fixture only when the step
  that needs it arrives? Recommend building all fixtures up front in step 3 since spec §9
  describes them as one fixture file, but the corresponding *test files* still get written
  step-by-step as their modules land.
