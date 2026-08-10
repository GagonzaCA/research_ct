# techContext.md

> Merged from: AI_CONTEXT.md, AI_CONTEXT_2.md, LABORATORY_NOTEBOOK.md
> NOTE: Treat all claims as proposals/intentions, not confirmed implementation.

## Language & Core Stack (LABORATORY_NOTEBOOK.md §8 — with "why")

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Language |
| NumPy | 1.24+ | N-dimensional arrays, vectorized operations |
| SciPy | 1.10+ | Signal processing, optimization, statistics |
| scikit-image | 0.21+ | Image processing (morphology, filters, exposure) |
| scikit-learn | 1.3+ | GMM implementation, EM algorithm |
| Matplotlib | 3.7+ | Static plotting and figure generation |
| imageio | 2.31+ | TIFF I/O, video export |
| Pillow | 10.0+ | Image format support |
| tifffile | 2021+ | Multi-page TIFF, Dragonfly-format export |
| hyperspy | 2.0+ | BCF hypercube loading for XRF pipeline |
| exspy | — | X-ray spectroscopy extension (HS signal1d) |

### Visualization
| Tool | Version | Purpose |
|---|---|---|
| napari | 0.4.18+ | Interactive 3D volume and label rendering |
| pyvista | 0.42+ | Alternative: publication-quality 3D (optional) |

### Development
| Tool | Version | Purpose |
|---|---|---|
| pytest | 7.4+ | Unit testing |
| pytest-cov | 4.1+ | Coverage reports |
| black | 23.0+ | Code formatting |
| flake8 | 6.0+ | Linting |
| mypy | 1.5+ | Static type checking |
| JupyterLab | 4.0+ | Interactive notebooks |

## Root Configuration Files (AI_CONTEXT.md, AI_CONTEXT_2.md)
| File | Duty |
|---|---|
| pyproject.toml | Package metadata, dependencies, build config, tool settings (black, pytest, mypy) |
| requirements.txt | Human-readable dependency list with version pins |
| .gitignore | Excludes __pycache__/, data files, notebook checkpoints |
| LICENSE | MIT License |
| README.md | Project overview, quick start, structure diagram |
| AI_CONTEXT.md | AI assistant reference |
> **Resolved (C-ROOTDOC):** LABORATORY_NOTEBOOK.md is NOT in the repo root directory. Root contains only README.md, pyproject.toml, requirements.txt, .gitignore, LICENSE.

## Constraints (technical)

- **Raw TIFF only; no scanner metadata exists.** All metadata (bit depth, shape, intensity range) inferred from the numpy array itself. metadata_parser.py: Infer metadata from array properties. (AI_CONTEXT.md, AI_CONTEXT_2.md)
- **Never commit data files.** Only `.gitkeep` files are tracked to preserve directory structure; data/raw, data/processed, data/output all .gitignored. (AI_CONTEXT.md, AI_CONTEXT_2.md)
- **Memory efficiency — resolved (C-MEM):** Flexible approach. Local machine has 32 GB RAM; external/cluster resources available up to ~564 GB RAM. No hardcoded limits. Use float64 by default; subsample/chunk as needed. Key strategies: subset (Volume[:100,:,:]), chunking (implemented in 03_fit_gmm.ipynb), downsample (Volume[::4,::4,::4]).
- **Code quality practices (LABORATORY_NOTEBOOK.md §7):** Type hints on all function signatures; comprehensive Google-style docstrings; modular design (single responsibility); pytest suite with synthetic fixtures; **Black code formatting (line length 100)**.

## Coding Structure & Developing Rules (AI_CONTEXT.md, AI_CONTEXT_2.md §3)

### Naming Conventions
| Entity | Convention | Example |
|---|---|---|
| Classes | Pascal_Case_With_Underscores | Gmm_Fitter, Hmrf_Segmenter, Preprocessing_Config |
| Functions | Verb_Object descriptive | Load_Slice_Stack(), Compute_Edge_Strength() |
| Variables | Descriptive_Name | Num_Components, Edge_Strength, Voxel_Size_Um |
| Constants | UPPER_CASE | MAX_ITERATIONS, DEFAULT_BETA |
| Private | Leading underscore | _Split_Component(), _Weighted_Bic() |
| Type alias | Path_Like = Union[str, Path] | Used for function signatures |

- **Docstring standard:** Google Style — every public function/class must have Args, Returns, and optionally Raises.
- **Type Hints:** All signatures must include type hints. Use `Path_Like = Union[str, Path]` for filesystem paths.
- **Error Handling:** Raise specific exceptions with descriptive messages; validate inputs early (guard clauses); log progress for long-running operations using `[ModuleName]` prefix.
- **Memory Efficiency:** Process large volumes in chunks via volume_saver.py (Load_From_Numpy_Chunked, Reduce_Streaming, Compute_Labels_From_Probabilities). Avoid unnecessary copies; sample subsets for model fitting when full data too large. Local RAM: 32 GB (Windows); external resources up to ~564 GB. Default compute dtype: float64. Disk-stored probability arrays: float32. Lazy memmap loading is default for .npy/.npz files.
- **Modular Design Rules:** SINGLE RESPONSIBILITY (split files > ~300 lines); NO CIRCULAR IMPORTS (io/preprocessing never import segmentation/analysis); PURE FUNCTIONS PREFERRED (Apply_ prefix implies transformation); CONFIGURATION AS DATA (dataclasses not dicts; presets are class methods); LAZY IMPORTS (import napari/matplotlib inside functions to avoid overhead in headless environments).
- **Testing Rules:** Every public function should have ≥1 test; use fixtures in conftest.py; test edge cases (empty inputs, constant images, shape mismatches); name tests descriptively `test_what_condition`.

## Setup / Daily Development Commands (verified 2026-07-31)
```
# From project root
python -m venv venv
source venv/bin/activate
pip install -e .                # install from src/
pip install -r requirements.txt
# Verify imports work
python -c "from research_ct.segmentation.gmm_fitter import Gmm_Fitter; print('OK')"
# Run tests
pytest
# Launch notebooks
jupyter lab
# Format code
black src/ tests/
# Type check
mypy src/
```

### Command Reference (LABORATORY_NOTEBOOK.md Appendix B — adds flake8 + coverage variants)
```
# Setup: python -m venv venv ; source venv/bin/activate ; pip install -e ".[dev]"
# Testing: pytest ; pytest -v ; pytest --cov
# Development: black src/ ; mypy src/ ; flake8 src/
# Notebooks: jupyter lab
```
> NOTE: LABORATORY_NOTEBOOK.md Appendix B references `src/` for black/mypy/flake8 targets and `pip install -e ".[dev]"` from `cd research_ct`, whereas AI_CONTEXT §1.4 targets `research_ct/`. Minor path discrepancy — flagged, not resolved.

## Entry Points for Development (verified 2026-07-31, updated 2026-08-09)
| Task | File to Open | Key Class/Function |
|---|---|---|
| Load raw data | src/research_ct/io/volume_loader.py | Load_Slice_Stack() |
| Lazy-load saved volumes | src/research_ct/io/volume_saver.py | Load_From_Numpy(), Load_From_Numpy_Chunked(), Load_From_Numpy_Slab() |
| Configure preprocessing | src/research_ct/preprocessing/config.py | Preprocessing_Config.From_Preset() |
| Run full preprocessing | src/research_ct/preprocessing/pipeline_revised.py (GMM) / pipeline.py (visualization) | Preprocess_For_Gmm_Revised() / Preprocess_For_Gmm() |
| Fit GMM | src/research_ct/segmentation/gmm_fitter.py | Gmm_Fitter.Fit() |
| Fit Sparse Bayesian GMM | src/research_ct/segmentation/sparse_bayesian_gmm.py | Sparse_Bayesian_Gmm.Fit() |
| Run hierarchy | src/research_ct/segmentation/hierarchy.py | Hierarchical_Gmm.Fit() |
| Run full segmentation | src/research_ct/segmentation/decision_engine.py | Segmentation_Engine.Run() |
| View results | src/research_ct/visualization/napari_viewer.py | launch_napari_viewer() |
| Export outputs | src/research_ct/visualization/export.py | export_probability_video(), export_label_colors() |
| Export for Dragonfly | src/research_ct/processing/dragonfly_utils.py | Export_For_Dragonfly() |
| Run tests | tests/ directory | pytest |

### XRF Entry Points (added 2026-08-09)
| Task | File to Open | Key Class/Function |
|---|---|---|
| Load elemental TIFFs | src/xrf/io/xrf_loader.py | Xrf_Loader.Load_Element_Stack() |
| Extract from BCF | src/xrf/preprocessing/bcf_extractor.py | Bcf_Element_Extractor |
| CLR transform | src/xrf/transforms/coda.py | Clr_Transformer.Apply_Clr_Transform() |
| Segment XRF data | src/xrf/segmentation/xrf_gmm.py | Xrf_Gmm_Segmenter.Fit_Predict() |
| Reconstruct class map | src/xrf/spatial/spatial_analyzer.py | Spatial_Analyzer.Reconstruct_Class_Map() |
| Extract spatial descriptors | src/xrf/spatial/spatial_analyzer.py | Spatial_Analyzer.Extract_Spatial_Descriptors() |
| Build leaf signature | src/xrf/signatures/leaf_signature.py | Leaf_Signature_Extractor.Compute_Abundances() |
| Compute weighted book sig | src/xrf/signatures/leaf_signature.py | Leaf_Signature_Extractor.Compute_Weighted_Book_Signature() |
| Aggregate by category | src/xrf/comparison/category_signatures.py | Category_Signature_Aggregator.Aggregate_By_Category() |
| Score rarity | src/xrf/comparison/rarity_scoring.py | Rarity_Scorer.Flag_Rare_Pages() |
| Validate/assign category | src/xrf/comparison/category_registry.py | Category_Registry.Validate_Category_Tag() |
| Aggregate spatial by cat | src/xrf/comparison/spatial_comparison.py | Category_Spatial_Comparator.Aggregate_Region_Stats() |

## Parameter Cheat Sheet — resolved (C-COV, C-DIFFPARAM)
| Parameter | Default | Range | Effect | Source |
|---|---|---|---|---|
| Gmm_Min_K | 2 | 1-10 | Minimum components to test | both |
| Gmm_Max_K | 8 | 2-15 | Maximum components to test | both |
| Covariance_Type | "full" | full/tied/diag/spherical | Complexity of Gaussian shapes (default = full, code-verified) | both |
| DP_Max_Components | 20 | 10-50 | Truncation level for DP-GMM | AI_CONTEXT_2.md |
| DP_Alpha | 1.0 | 0.01-10.0 | Weight concentration prior | AI_CONTEXT_2.md |
| Hierarchy_Max_Depth | 3 | 1-5 | Maximum recursion depth | both |
| Significance_Alpha | 0.05 | 0.01-0.1 | LRT significance threshold | both |
| Hmrf_Beta | 0.5 | 0.1-2.0 | Spatial smoothness strength | both |
| Hmrf_Iterations | 50 | 10-100 | ICM maximum iterations | both |
| Connectivity | 6 | 6, 26 | Neighborhood size | both |
| Background_Sigma | 30.0 | 10-100 | Beam hardening removal strength | AI_CONTEXT_2.md |
| Noise_Sigma | 0.8 | 0.5-1.5 | Noise reduction strength | AI_CONTEXT_2.md |
| Clip_Low_Percentile | 0.1 | 0.0-1.0 | Lower clipping bound | AI_CONTEXT_2.md |
| Clip_High_Percentile | 99.9 | 99.0-100.0 | Upper clipping bound | AI_CONTEXT_2.md |
| Diffusion_Iterations | 50 | 10-200 | Smoothing strength | AI_CONTEXT.md |
| Diffusion_Kappa | 75 | 10-200 | Edge preservation threshold | AI_CONTEXT.md |
| Diffusion_Gamma | 0.1 | <=0.25 | Time step (stability) | AI_CONTEXT.md |

### XRF Parameters (added 2026-08-09)
| Parameter | Default | Range | Effect | Source |
|---|---|---|---|---|
| Xrf_Noise_Threshold | 5.0 | 0–50 | Min accumulated intensity for valid pixel mask | xrf/config.py |
| Xrf_Zero_Replacement_Delta | 1e-4 | 1e-6–1e-2 | Small constant to replace zeros before CLR | xrf/config.py |
| Xrf_Pca_Variance_Ratio | 0.95 | (0, 1] | Cumulative explained variance retained by PCA | xrf/config.py |
| Xrf_Gmm_Min_K | 2 | 1–10 | Min components for XRF GMM | xrf/config.py |
| Xrf_Gmm_Max_K | 8 | 2–15 | Max components for XRF GMM | xrf/config.py |
| Xrf_Connectivity | 8 | 4, 8 | CCA neighborhood for 2D spatial analysis | xrf/config.py |
| Xrf_Min_Region_Size | 10 | 1–100 | Min pixels to consider a valid connected component | xrf/config.py |
| Bcf_Cutoff_At_Kv | 40.0 | 10–80 | Detector energy ceiling (keV) | xrf/config.py |
| Bcf_Peak_Width_Kev | 0.20 | 0.05–1.0 | Half-width of emission-line integration window | xrf/config.py |
| Bcf_Bg_Width_Kev | 0.10 | 0.05–0.5 | Half-width of background sideband window | xrf/config.py |
| Bcf_Bg_Offset_Kev | 0.25 | 0.1–1.0 | Distance from line center to sideband center | xrf/config.py |
| Rarity_Mad_Threshold | 3.5 | 2.0–5.0 | Robust z-score magnitude for rarity flagging | xrf/config.py |

## File-to-Theory Mapping (merged + verified 2026-07-31, updated 2026-08-09)
- gmm_fitter.py → GMM, EM algorithm, BIC model selection (both)
- sparse_bayesian_gmm.py → Bayesian nonparametrics, Dirichlet Process, variational inference, component pruning (implemented)
- hierarchy.py → Hierarchical clustering, LRT, chi-squared test (both)
- hmrf.py → MRF, Potts model, ICM optimization, Gibbs distribution (both)
- background_correction.py → Large-scale filtering, beam hardening correction (AI_CONTEXT_2.md)
- noise_reduction.py → Gaussian convolution, Central Limit Theorem (AI_CONTEXT_2.md)
- global_normalization.py → Linear affine transforms, percentile clipping (AI_CONTEXT_2.md)
- histogram_diagnostics.py → Distribution shape analysis, mode counting, GMM readiness assessment (AI_CONTEXT_2.md)
- contrast.py → Morphological operations, histogram equalization (AI_CONTEXT.md)
- diffusion.py → PDEs, finite differences, anisotropic diffusion (AI_CONTEXT.md)
- uncertainty_maps.py → Information theory, entropy (both)
- volume_saver.py → Lazy I/O, memmap, chunked streaming, .npz/.npy dual support (new — implemented)

### XRF File-to-Theory (added 2026-08-09)
- xrf_loader.py → Multispectral image I/O, threshold-based pixel masking
- bcf_extractor.py → X-ray emission line physics, dual-window background subtraction, Bruker BCF format
- coda.py → Compositional Data Analysis (CoDa), Centered Log-Ratio (CLR), Aitchison geometry
- xrf_gmm.py → PCA dimensionality reduction, GMM clustering in latent space
- spatial_analyzer.py → Connected-component analysis (CCA), morphological region descriptors
- leaf_signature.py → Per-page abundance vectors, weighted averaging
- category_signatures.py → Group-wise signature aggregation
- rarity_scoring.py → Robust statistics (median, MAD), z-score triage heuristic
- spatial_comparison.py → Per-category spatial descriptor aggregation
- category_registry.py → Controlled vocabulary for structural page categories

### Dragonfly Export (added 2026-08-09)
- dragonfly_exporter.py → Multi-page TIFF with ImageJ metadata, voxel-spacing calibration, BigTIFF support
- dragonfly_utils.py → Dragonfly orchestration, label-color CSV, self-describing export directories

## Test Suite (AI_CONTEXT.md, AI_CONTEXT_2.md §2.3, updated 2026-08-09)
- conftest.py fixtures: synthetic_volume, flat_intensities, bimodal_data, trimodal_data.
- test_io/ (volume_loader, metadata_parser), test_preprocessing/ (config, contrast, diffusion, diagnostics), test_segmentation/ (gmm_fitter, hierarchy, test_sparse_bayesian_gmm.py, test_hmrf.py), test_analysis/ (material_stats).
- **test_xrf/** (added 2026-08-09): conftest.py + 4 test modules: test_spatial_comparison.py, test_rarity_scoring.py, test_category_signatures.py, test_category_registry.py.

## Notebooks (verified 2026-07-31, updated 2026-08-09)
- 01_explore_raw_data.ipynb — Load raw TIFF, inspect histograms, metadata
- 02_run_preprocessing.ipynb — Run pipeline_revised, histogram comparisons, save preprocessed volume
- 03_gmm_and_hierarchical_segmentation.ipynb — BIC-GMM fit, Sparse Bayesian GMM comparison, hierarchical refinement, streaming label export
- 04_spatial_hmrf.ipynb — HMRF on test region, GMM vs HMRF comparison, visual pipeline demo
- 05_uncertainty_and_visualization.ipynb — Material stats, uncertainty maps, napari 3D, export videos

### XRF Notebooks (added 2026-08-09)
- 01_xrf_loading_and_masking.ipynb — Load elemental TIFFs, compute intensity mask
- 02_coda_transformations.ipynb — CLR transformation, zero replacement
- 03_gmm_spatial_clustering.ipynb — PCA reduction, GMM clustering, 2D class map
- 04_leaf_signatures.ipynb — Per-page leaf signature F_h computation
- 05_page_categorization.ipynb — Structural category assignment
- 06_category_signature_comparison.ipynb — Category-level compositional norms
- 07_rarity_review.ipynb — Robust z-score rarity flagging
- xrf_bcf_extraction.ipynb — Bruker BCF hypercube → elemental TIFF extraction

## Resolved Conflicts (all 5 from this file — updated 2026-07-31)

- **C-COV:** Covariance_Type default = `"full"` (Option A). Code-verified in gmm_fitter.py line 21.
- **C-MEM:** Flexible approach. Local machine = 32 GB RAM (Windows); external/cluster resources up to ~564 GB. No hardcoded limits. Compute dtype: float64. Disk-stored probabilities: float32. Lazy memmap with chunked streaming via volume_saver.py.
- **C-VOXELS:** Current raw data = ~750M voxels (201 slices × ~1900 × ~1900). Streaming label/probability computation avoids full materialization.
- **C-ROOTDOC:** LABORATORY_NOTEBOOK.md is NOT present in the repo root directory. Root contains only README.md, pyproject.toml, requirements.txt, .gitignore, LICENSE.
- **C-DIFFPARAM:** Both parameter sets coexist. GMM pipeline uses Option B params (Background_Sigma, Noise_Sigma, Clip_Low/High_Percentile). Visualization pipeline uses Option A params (Diffusion_Iterations, Diffusion_Kappa, Diffusion_Gamma). Both preserved in cheat sheet.
