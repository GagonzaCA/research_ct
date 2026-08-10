# activeContext.md

> Merged from: AI_CONTEXT.md, AI_CONTEXT_2.md, LABORATORY_NOTEBOOK.md
> NOTE: Treat all "completed"/"working" claims as proposals/intentions, NOT confirmed implementation.

## Current Focus

- As of 2026-08-09, the project has **two independently operational pipelines** — CT volumetric segmentation (`research_ct`) and XRF compositional clustering (`xrf`). Both have been executed end-to-end on real data.
- **CT pipeline** has run on `Brevar Capucin` micro-CT data (~431 TIFF slices). Outputs include GMM labels, HMRF-regularized labels, per-slice material fractions, uncertainty maps, and publication-quality diagnostic figures.
- **XRF pipeline** has run on `Letter_1` elemental data (8 elements: Pb, K, Hg, Fe, Cu, Ca, Au, As). Outputs include 7-class GMM cluster masks, per-page leaf signatures, and a book-level weighted signature.
- **Fusion gap:** `src/xrf/fusion/ct_xrf_fusion.py` exists as an empty placeholder. Cross-modal integration (using XRF compositional maps to validate/inform CT material labeling) is the next major feature.
- Memory management for Windows/32GB RAM continues to use lazy memmap loading, chunked streaming, and explicit gc.collect() in volume_saver.py.
- Dragonfly export utilities (`dragonfly_exporter.py`, `dragonfly_utils.py`) enable ImageJ-calibrated multi-page TIFF export for 3D inspection.

## Recent Changes (verified against repo 2026-07-31, updated 2026-08-09)

### 2026-08-09
- **XRF pipeline (`src/xrf/`) fully implemented:**
  - `xrf/io/xrf_loader.py` — Load_Element_Stack(), Compute_Intensity_Mask()
  - `xrf/preprocessing/bcf_extractor.py` — Bcf_Element_Extractor with dual-window Bremsstrahlung subtraction, atomic-number lookup table
  - `xrf/transforms/coda.py` — Clr_Transformer with zero replacement and Aitchison-space projection
  - `xrf/segmentation/xrf_gmm.py` — Xrf_Gmm_Segmenter with PCA + GMM in latent space
  - `xrf/spatial/spatial_analyzer.py` — Spatial_Analyzer with Reconstruct_Class_Map() and Extract_Spatial_Descriptors()
  - `xrf/signatures/leaf_signature.py` — Leaf_Signature_Extractor with Compute_Abundances() and Compute_Weighted_Book_Signature()
  - `xrf/comparison/category_registry.py` — Category_Registry with controlled vocabulary for structural categories
  - `xrf/comparison/category_signatures.py` — Category_Signature_Aggregator for per-category mean signatures
  - `xrf/comparison/rarity_scoring.py` — Rarity_Scorer with robust z-score deviation flagging
  - `xrf/comparison/spatial_comparison.py` — Category_Spatial_Comparator aggregating region stats by category
  - `xrf/config.py` — 5 dataclasses: Xrf_Preprocessing_Config, Xrf_Segmentation_Config, Leaf_Signature_Config, Xrf_Comparison_Config, Bcf_Extraction_Config
- **Dragonfly export modules added:** `research_ct/io/dragonfly_exporter.py` (ImageJ multi-page TIFF with voxel spacing), `research_ct/processing/dragonfly_utils.py` (Export_For_Dragonfly with color CSV + metadata JSON).
- **`ct_xrf_fusion.py` created as empty placeholder** (0 bytes) — fusion module planned but not yet implemented.
- **XRF tests:** 4 modules in `tests/test_xrf/` (test_spatial_comparison, test_rarity_scoring, test_category_signatures, test_category_registry) + conftest.py.
- **Real CT data loaded:** `Brevar Capucin` (~431 slices) in `data/raw/`. GMM, HMRF, and analysis outputs in `data/output/`.
- **Real XRF data loaded:** `Letter_1` elemental TIFFs (Pb, K, Hg, Fe, Cu, Ca, Au, As) in `data/xrf/raw/`. Cluster masks and signatures in `data/xrf/output/`.
- **XRF notebooks exist** (not previously documented): 8 notebooks in `notebooks/xrf/`:
  - `01_xrf_loading_and_masking.ipynb` — load elemental TIFFs, intensity mask
  - `02_coda_transformations.ipynb` — CLR transform
  - `03_gmm_spatial_clustering.ipynb` — PCA + GMM + spatial reconstruction
  - `04_leaf_signatures.ipynb` — per-page signature extraction
  - `05_page_categorization.ipynb` — structural category assignment
  - `06_category_signature_comparison.ipynb` — category norms
  - `07_rarity_review.ipynb` — rarity scoring
  - `xrf_bcf_extraction.ipynb` — BCF → elemental TIFFs

### 2026-07-31 (previous)
- **Package relocated under `src/research_ct/`** — pyproject.toml uses `[tool.setuptools.packages.find] where = ["src"]`.
- **Sparse Bayesian GMM implemented** — `sparse_bayesian_gmm.py` (Sparse_Bayesian_Gmm) using sklearn BayesianGaussianMixture with sparse Dirichlet prior. Not "planned" anymore — it is code-complete and tested (test_sparse_bayesian_gmm.py).
- **Volume I/O expanded** — `volume_saver.py` added with lazy memmap loading (Load_From_Numpy, Load_From_Numpy_Chunked, Load_From_Numpy_Slab), streaming reduction (Reduce_Streaming), and convenience wrappers (Compute_Labels_From_Probabilities, Compute_Confidence_From_Probabilities).
- **Histogram diagnostics split** — `histogram_diagnostics.py` (computational: Assess_Gmm_Readiness, Compute_Histogram_Statistics, Count_Visible_Modes) and `histogram_diagnostics_viewer.py` (visualization: Plot_Histogram_Comparison, Plot_Slice_Histograms).
- **Notebooks renamed/consolidated:**
  - `01_explore_raw_data.ipynb` — raw TIFF loading + slice/histogram inspection
  - `02_run_preprocessing.ipynb` — pipeline_revised + histogram diagnostics
  - `03_gmm_and_hierarchical_segmentation.ipynb` — BIC-GMM, Sparse Bayesian GMM comparison, hierarchical refinement, streaming label export
  - `04_spatial_hmrf.ipynb` — HMRF on test region, GMM vs HMRF comparison, visual pipeline demo
  - `05_uncertainty_and_visualization.ipynb` — material stats, uncertainty maps, napari 3D, video export
- **Memory management designed for Windows** — `_npz_registry` keeps .npz archives alive for lazy views, `gc.collect()` forced after large operations, chunked streaming writes for 24GB+ probability arrays.
- **decision_engine.py** — Hierarchy_Max_Depth default changed from 3 to 5. Run() accepts Use_Hierarchy and Use_Hmrf boolean flags.
- **hierarchy.py** — Internal structure uses `Trees` (list of dicts) and `Leaf_Nodes` (list of dicts), not a single `Component_Tree` dict.
- **Data directories** — raw, output, figures, diagnostics, processed live under `src/research_ct/data/`, git-ignored except .gitkeep.

## Immediate Next Steps (updated 2026-08-09)

1. **Implement CT-XRF fusion** (`src/xrf/fusion/ct_xrf_fusion.py`) — wire XRF elemental maps as priors or validation targets for CT GMM components.
2. **Cross-validate CT material labels vs XRF compositional clusters** where both modalities overlap (same pages).
3. **Tune XRF GMM K** — currently uses fixed Num_Components; evaluate BIC-based selection for XRF data.
4. **Continue HMRF beta tuning** if GMM noise is still visible on full CT volume.
5. **XRF notebooks exist** (8 notebooks in `notebooks/xrf/`) — verify they run end-to-end on a clean environment.
6. **Run CT pipeline end-to-end from clean environment** to confirm reproducibility:
   ```
   # From project root
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -e .
   pip install -r requirements.txt
   pytest
   ```
7. Execute CT notebooks in order: 01 → 02 → 03 → 04 → 05

## Short-Term Extensions (LABORATORY_NOTEBOOK.md — Weeks 4–6, if time permits, updated 2026-08-09)
| Extension | Effort | Value | Status |
|---|---|---|---|
| Dirichlet Process GMM | Medium | Automatic K without BIC search; elegant but computationally expensive | **Implemented** (sparse_bayesian_gmm.py) |
| XRF Elemental Pipeline | High | Compositional material identification via X-ray fluorescence; orthogonal to CT density | **Implemented** (src/xrf/) |
| CT-XRF Fusion | Medium | Multi-modal material identification using density + elemental composition | **Not started** (ct_xrf_fusion.py is empty placeholder) |
| Multi-resolution processing | Medium | Speed up by processing at reduced resolution first | Not started |
| Synthetic validation data | High | Create ground-truth volumes to quantify accuracy | Not started |
| XRF fusion | High | If XRF data available, use elemental maps to guide segmentation | **Partially implemented** — XRF pipeline operational; fusion module not yet wired |

## Medium-Term: Charles' Geometric Integration (LABORATORY_NOTEBOOK.md — Weeks 10–14)
- Concept: use high-confidence ink voxels (P(ink) > 0.7) as input to Charles' normal-vector and page-surface extraction.
- Proposed pipeline: GMM ink probability map → threshold P > 0.7 → per-voxel normals (Charles') → cluster normals into page groups (RANSAC/Hough) → fit parametric surfaces (B-splines) → project ink back onto flattened surfaces.
- Time estimate: 6–8 weeks basic page surface extraction; 12+ weeks full virtual flattening with texture mapping.

## Open Questions (LABORATORY_NOTEBOOK.md §12)

### Scientific Questions
- **How many material classes actually exist?** If BIC selects K=3 but visual inspection suggests 4, which takes precedence?
- **What is the physical interpretation of each component?** GMM components are statistical, not semantic; labeling "ink" vs "paper" requires expert judgment.
- **How to validate without ground truth?** Stability analysis and physical plausibility are necessary but not sufficient. Can synthetic data provide quantitative metrics?
- **When is hierarchical splitting justified?** The LRT assumes nested models; is this valid for all material decompositions?

### Collaboration Questions
- **Integration with Charles' geometric approach:** What probability threshold defines "high-confidence ink" for normal vector computation? How to handle ambiguous voxels?
- **Social science colleagues' needs:** Do they need 3D interactive viewing, 2D flattened pages, or quantitative material statistics? All three?

## Known Risks to Monitor (LABORATORY_NOTEBOOK.md §12 / Conclusion)
- **Ink invisible in CT** (Medium prob / Critical impact): if carbon-based ink on thick substrate, no intensity-based method can recover it. Suggest phase-contrast CT or XRF fusion.
- **Cover/paper indistinguishable** (Medium/High): use hierarchical splitting; add thickness/shape features if global GMM fails.
- **Volume too large for memory** (Medium/High): chunked processing; consider Dask for out-of-core; subsample for GMM fitting.
- **HMRF too slow** (Medium/Medium): ICM O(N*K*iterations); start with 6-connectivity and 20 iterations; GPU acceleration if needed.
- **BIC selects wrong K** (Low/Medium): always inspect BIC curve manually; use domain knowledge (expect ~4–6 materials).
- **Non-stationary distributions** (Medium/Medium): monitor via slice-wise histograms; implement local GMM if drift is severe.

## Common Issues & Debugging (AI_CONTEXT.md, AI_CONTEXT_2.md §6)
- **Import errors:** check venv activated; `pip install -e .`; run from project root (not inside research_ct/).
- **GMM convergence:** check data range [0,255]; increase max_iter; try covariance_type ('tied','diag','spherical'); reduce K_max; check for NaN/Inf.
- **HMRF too slow:** run on subset first to validate beta; use 6- instead of 26-connectivity; reduce Max_Iterations (convergence often < 20 iters); skip HMRF if GMM output already clean.
- **Memory errors:** see techContext.md CONFLICT C-MEM (solutions differ by source).

## Core Assumptions to Monitor (LABORATORY_NOTEBOOK.md §4)

### Stated Assumptions
- A1: Material brightness follows statistical distributions (Poisson→Gaussian after reconstruction) — Risk Low.
- A2: Distributions overlap to varying degrees; heavily overlapped may be indistinguishable — Risk High.
- A3: Distribution parameters initially unknown (EM is standard tool) — Risk Low.
- A4: Parameters must be calculated from experimental data (empirical Bayes; no calibration phantoms) — Risk Low.
- A5: No pre-processed ground truth exists (rules out supervised learning) — Risk Low.

### Implicit Assumptions (To Monitor)
- I1: Spatial stationarity (constant mean/variance) — violated by beam hardening/positioning → local histogram analysis; bias field correction.
- I2: Gaussian-distributed components — heavy tails/skew from beam hardening → consider t-distributions or skew-normal extensions.
- I3: Isotropic voxel spacing — anisotropic voxels distort spatial regularization → read spacing from metadata; adjust neighborhood weights.
- I4: Single book per scan volume — multiple books/fragments complicate → pre-segmentation bounding box detection.

## Resolved Conflicts (all 11 — verified 2026-07-31)

All conflicts from systemPatterns.md and techContext.md have been resolved against actual code:

**systemPatterns.md:** C-PIPE, C-NORM, C-PRESET, C-DTYPE, C-MITIG, C-DPGMM
**techContext.md:** C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM

**Key resolution updates (2026-07-31):**
- C-DPGMM: Resolved — implemented as `sparse_bayesian_gmm.py` (Sparse_Bayesian_Gmm), not `dp_gmm.py` (Dp_Gmm_Fitter)
- C-DTYPE: Clarified — float64 for compute, float32 for persisted probability arrays
- C-MEM: Windows-specific memory management with lazy memmap, chunked streaming, gc.collect()

See individual files for full resolution details.
