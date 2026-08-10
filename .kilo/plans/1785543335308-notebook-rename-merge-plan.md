# Notebook Audit, Rename, Merge, and Static Extension Plan

## Goal
Audit, update, and incrementally extend the existing Jupyter notebooks in `notebooks/` according to the updated nomenclature scheme via **static file modifications only**.

## Constraints
1. **STATIC ONLY**: Do NOT execute cells or run tests. All updates are static edits.
2. **NO DESTRUCTIVE OVERWRITES**: Retain existing text, comments, sample loaders, and variable names.
3. **ADDITIVE EXTENSION**: Insert new code blocks and Markdown alongside existing content.
4. **API ALIGNMENT**: Ensure imports point to `research_ct.segmentation` and method calls use PascalCase (e.g., `Predict_Probabilities`, `Fit`, `Active_Indices`).
5. **MEMORY EFFICIENCY**: Keep data passed into models as 1D intensity memory views (`.reshape(-1, 1)`).

---

## File Inventory & Naming Scheme

| Target Filename | Source / Action |
|-----------------|-----------------|
| `01_explore_raw_data.ipynb` | Keep filename & content (no changes needed). |
| `02_run_preprocessing.ipynb` | Keep filename; update import to use `pipeline_revised.py` API. |
| `03_gmm_and_hierarchical_segmentation.ipynb` | **Consolidated notebook** — merge content from legacy `03_fit_gmm.ipynb` + `04_hierarchical_segmentation.ipynb`. |
| `04_spatial_hmrf.ipynb` | **Rename** from `05_spatial_hmrf.ipynb`. |
| `05_uncertainty_and_visualization.ipynb` | **Rename** from `06_uncertainty_and_visualization.ipynb`. |

> **Note**: The current repo already contains the target filenames (`03_gmm_and_hierarchical_segmentation.ipynb`, `04_spatial_hmrf.ipynb`, `05_uncertainty_and_visualization.ipynb`). The legacy source files (`03_fit_gmm.ipynb`, `04_hierarchical_segmentation.ipynb`, `05_spatial_hmrf.ipynb`, `06_uncertainty_and_visualization.ipynb`) do **not** exist in the repo, so the "merge" is effectively an **in-place enrichment** of the already-consolidated `03_gmm_and_hierarchical_segmentation.ipynb`.

---

## Notebook-by-Notebook Modification Plan

### Notebook 01 — `01_explore_raw_data.ipynb`
- **Action**: Retain all existing cells statically.
- **Check**: Imports (`research_ct.io.volume_loader`, `research_ct.io.metadata_parser`) and dataset loading references are already correct.
- **Result**: No edits required.

---

### Notebook 02 — `02_run_preprocessing.ipynb`
- **Action**: Retain existing cells and intensity normalization narrative.
- **Modification**: The notebook already imports and calls `Preprocess_For_Gmm_Revised` from `research_ct.preprocessing.pipeline_revised`. Verify the call signature matches the current API.
- **Current API** (from `pipeline_revised.py`):
  ```python
  Preprocess_For_Gmm_Revised(
      Volume,
      Background_Sigma=None,
      Noise_Sigma=0.8,
      Clip_Low_Percentile=0.1,
      Clip_High_Percentile=99.9,
      Check_Stationarity=True,
      Apply_Slice_Standardization=False,
      Verbose=True,
  )
  ```
- **Notebook current call** (lines 65-73) already matches this API.
- **Result**: No edits required.

---

### Notebook 03 — `03_gmm_and_hierarchical_segmentation.ipynb` [CONSOLIDATED]

This notebook already contains the merged GMM + Hierarchical content. The task is to **insert a new Sparse Bayesian GMM section** and ensure API alignment.

#### Step 3A — Verify Existing API Alignment
- **Imports** (lines 12-14):
  ```python
  from research_ct.io.volume_saver import Load_From_Numpy
  from research_ct.segmentation.gmm_fitter import Gmm_Fitter
  from research_ct.visualization.plot_distributions import plot_gmm_components
  ```
  These are correct.
- **Method calls** already use PascalCase (`Fitter.Fit`, `Fitter.Get_Material_Statistics`, `Fitter.Predict_Probabilities`).
- **Data flattening** (line 55) already uses `.reshape(-1, 1)`.

#### Step 3B — Insert New Sparse Bayesian GMM Section
- **Location**: Insert a new code cell **directly after the flat GMM section** (after the `Material Statistics` cell, before the `Sparse Bayesian GMM` markdown section).
- **Content**:
  ```python
  from research_ct.segmentation.sparse_bayesian_gmm import Sparse_Bayesian_Gmm

  # Fit overcomplete Sparse Bayesian GMM
  Sparse_Model = Sparse_Bayesian_Gmm(Max_Components=10, Min_Samples=1000)
  Sparse_Model.Fit(Flat_Data)

  # Inspect active component pruning results
  Material_Stats = Sparse_Model.Get_Material_Statistics()
  print("Active Means:", Material_Stats["Means"])
  print("Active Weights:", Material_Stats["Weights"])
  ```
- **Note**: The notebook already contains a `Sparse Bayesian GMM` section (lines 148-173). The new insertion should be placed **before** that existing section, or the existing section should be updated to use the exact snippet provided in the task. To satisfy the "INSERT NEW SECTION B" requirement, we will **add** the provided snippet as a distinct new cell block adjacent to the existing one, ensuring no destructive overwrite.

#### Step 3C — Verify Hierarchical Section API
- **Import** (line 199):
  ```python
  from research_ct.segmentation.hierarchy import Hierarchical_Gmm
  ```
  Correct.
- **Method calls** use PascalCase (`Hgmm.Fit`, `Hgmm.Get_Leaf_Components`, `Hgmm.Predict_Leaf_Probabilities`). Correct.

---

### Notebook 04 — `04_spatial_hmrf.ipynb`
- **Action**: This file already has the correct target name (`04_spatial_hmrf.ipynb`). No rename needed.
- **Check API alignment**:
  - Imports (lines 13-15): `Hmrf_Segmenter`, `Compute_Labels_From_Probabilities`, `Load_From_Numpy_Slab` — all correct.
  - Method calls use PascalCase (`Hmrf.Fit`, `Load_From_Numpy`, `Compute_Labels_From_Probabilities`). Correct.
- **Result**: No edits required.

---

### Notebook 05 — `05_uncertainty_and_visualization.ipynb`
- **Action**: This file already has the correct target name (`05_uncertainty_and_visualization.ipynb`). No rename needed.
- **Check API alignment**:
  - Imports (lines 12-14): `Compute_Material_Statistics`, `Print_Material_Report`, `Compute_Uncertainty`, `Compute_Margin` — all correct.
  - Method calls use PascalCase. Correct.
- **Result**: No edits required.

---

## Summary of Required Edits

| Notebook | Edits Required |
|----------|----------------|
| `01_explore_raw_data.ipynb` | None |
| `02_run_preprocessing.ipynb` | None |
| `03_gmm_and_hierarchical_segmentation.ipynb` | **Insert** new Sparse Bayesian GMM code cell after flat GMM section |
| `04_spatial_hmrf.ipynb` | None |
| `05_uncertainty_and_visualization.ipynb` | None |

---

## Open Questions

1. **Merge semantics**: The task mentions merging `03_fit_gmm.ipynb` and `04_hierarchical_segmentation.ipynb` into `03_gmm_and_hierarchical_segmentation.ipynb`. The target file already exists and contains both GMM and Hierarchical content. Should the new Sparse Bayesian GMM snippet **replace** the existing Sparse Bayesian section, or be inserted **in addition** to it?
   - **Recommendation**: Insert **in addition** (additive extension) to satisfy the "INSERT NEW SECTION B" requirement without destructive overwrites.

2. **Variable naming in snippet**: The provided snippet uses `Flat_Data`, while the notebook currently uses `Sampled` (the sampled subset) and `Processed` (the full flattened data). Which variable should the new snippet reference?
   - **Recommendation**: Use `Sampled` (the 5M-sample subset used for fitting) to keep runtime consistent with the existing GMM fitter.

---

## Validation Plan

- After edits, verify that `03_gmm_and_hierarchical_segmentation.ipynb` contains the new Sparse Bayesian GMM code block.
- Ensure no existing cells were removed or overwritten.
- Confirm all imports point to valid modules in `research_ct.segmentation` and `research_ct.preprocessing`.
