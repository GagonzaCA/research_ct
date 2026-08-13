# Plan: Create `examples/` Scripts for Pipeline Testing

## Objective
Create standalone Python scripts in `examples/` that allow a new student to test the `research_ct` and `xrf` packages without running notebooks. Scripts follow the approved proposal and project coding conventions (`Pascal_Case_With_Underscores`, Google-style docstrings, Black line-length 100).

---

## Revised Area: Phase 4 — Validation (Logical Only)

**Do not run files against live data.** Data is not yet available. Verification is strictly logical:

1. **Import verification**: For each script, confirm that all imports resolve correctly by inspecting `sys.path` and checking that the imported classes/functions exist in the target modules.
2. **Path resolution**: Verify that `common.py` returns correct absolute `Path` objects when called from `examples/micro_ct/` and `examples/xrf/` subdirectories.
3. **I/O contract**: Check that each script reads the expected files (e.g., `preprocessed_volume.npz`) and writes the expected outputs (e.g., `gmm_probabilities.npy`, PNG plots) by reviewing the notebook-to-script mapping and the underlying API signatures.
4. **Static plot check**: Confirm that no script imports or calls `napari` or any interactive viewer; only `matplotlib.pyplot` with `matplotlib.use("Agg")` is allowed.
5. **Batch runner flow**: Verify that `run_all_pages.py` correctly discovers `page_name/` subfolders and calls the step functions in order (`02_load_mask_and_coda.run()` → `03_gmm_cluster.run()` → `04_leaf_signature.run()` → `05_spatial_analyzer.run()`).
6. **Data structure assumption**: Confirm that `data/xrf/pages/page_name/` and `data/xrf/bcf/page_name/` conventions are documented in script docstrings so the student knows where to place data before running.

---

## Full Plan

### Phase 1: Foundation
**1.1 Create `examples/common.py`**
- Implement `get_project_root()` to traverse upward until `src/` is found.
- Implement `get_micro_ct_paths()` returning `DATA_DIR`, `RAW_DATA_DIR`, `OUTPUT_DATA_DIR`, `FIGURES_DIR`, `DIAG_DIR`, `PROCESSED_DATA_DIR` as `Path` objects.
- Implement `get_xrf_paths()` with the same pattern, including `BCF_DIR` and `PAGES_DIR`.
- Implement `ensure_dirs(Paths_Dict)` to create missing directories.
- All constants use `Pascal_Case_With_Underscores`.

---

### Phase 2: Micro_CT Scripts
**2.1 `examples/micro_ct/01_inspect_and_preprocess.py`**
- Load raw TIFF stack via `Load_Slice_Stack`.
- Infer metadata via `Load_Metadata`.
- Run `Preprocess_For_Gmm` or `Preprocess_For_Gmm_Revised`.
- Save `preprocessed_volume.npz` to `PROCESSED_DATA_DIR`.
- Save diagnostic histogram plots to `FIGURES_DIR`.

**2.2 `examples/micro_ct/02a_flat_gmm.py`**
- Load `preprocessed_volume.npz`.
- Flatten and sample voxels.
- Fit `Gmm_Fitter` with BIC-based K selection.
- Save optimal model and `gmm_probabilities.npy`.
- Save BIC plot to `FIGURES_DIR`.

**2.3 `examples/micro_ct/02b_sparse_bayesian_gmm.py`**
- Load `preprocessed_volume.npz`.
- Fit `SparseBayesianGMM` (DP-GMM), prune negligible components.
- Save model and probabilities.
- For student comparison with flat GMM.

**2.4 `examples/micro_ct/03_hmrf_refinement.py`**
- Load `preprocessed_volume.npz` and `gmm_probabilities.npy`.
- Run `Hmrf_Segmenter`.
- Allow selecting segmentation source (flat or sparse bayesian).
- Save `hmrf_labels.npy`.

**2.5 `examples/micro_ct/04_visualize_results.py`**
- Generate static matplotlib figures (slice overlays, label maps) from saved `.npy`/`.npz`.
- Exclude napari.
- Save to `FIGURES_DIR`.

---

### Phase 3: XRF Scripts
**3.1 `examples/xrf/01_bcf_extraction.py`**
- Scan `BCF_DIR / *` for subfolders.
- Extract each BCF to `RAW_DATA_DIR / page_name/`.

**3.2 `examples/xrf/02_load_mask_and_coda.py`**
- Scan `PAGES_DIR / *` for `page_name/` folders.
- Load elemental TIFFs, compute mask via `Xrf_Loader.Compute_Intensity_Mask`.
- Apply `Clr_Transformer`.
- Save masked data and CLR output per page.

**3.3 `examples/xrf/03_gmm_cluster.py`**
- Load CLR data per page.
- Run `Xrf_Gmm_Segmenter` with BIC K selection.
- Save cluster labels and probabilities.

**3.4 `examples/xrf/04_leaf_signature.py`**
- Load per-page cluster results.
- Extract signature via `Leaf_Signature_Extractor`.
- Save `page_NNN_meta.json`.

**3.5 `examples/xrf/05_spatial_analyzer.py`**
- Load per-page labels and raw data.
- Run `Spatial_Analyzer`.
- Save spatial statistics.

**3.6 `examples/xrf/06_page_categorization.py`**
- Load existing `page_*_meta.json` files.
- Assign categories via `Category_Registry`.
- Update metadata.

**3.7 `examples/xrf/07_compare_signatures.py`**
- Load categorized metadata.
- Run category-level and rarity comparisons.
- Save comparison plots and reports.

**3.8 `examples/xrf/run_all_pages.py`**
- Discover all `page_name/` folders in `PAGES_DIR`.
- Call `02_load_mask_and_coda.run(PAGE_DIR)`, `03_gmm_cluster.run(PAGE_DIR)`, `04_leaf_signature.run(PAGE_DIR)`, `05_spatial_analyzer.run(PAGE_DIR)` sequentially.
- No CLI arguments.
