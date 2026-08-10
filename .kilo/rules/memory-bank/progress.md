# progress.md

> Dated lab-notebook log merged from: AI_CONTEXT.md (2026-07-10), AI_CONTEXT_2.md (2026-07-28), LABORATORY_NOTEBOOK.md
> NOTE: Every "completed"/"working" claim below is a SOURCE CLAIM, not confirmed truth. These chats did not know how the code was ultimately implemented.

## 2026-07 — Project Start / Week 0 (LABORATORY_NOTEBOOK.md — "Current Status and Achieved Work")

**Goal attempted:** Stand up complete repository structure and infrastructure before real data arrives.

**Methods / what was claimed complete (As of Week 0 — Project Setup):**
- Complete Python package structure (research_ct/); root config files (pyproject.toml, requirements.txt, .gitignore, LICENSE, README.md).
- 20 Python modules across 5 subpackages (io, preprocessing, segmentation, analysis, visualization).
- 11 test files with pytest fixtures and comprehensive coverage; 5 Jupyter notebooks.
- **IO:** volume_loader.py (TIFF→3D array + shape validation), volume_saver.py (.npz/TIFF), metadata_parser.py (infer bit depth, intensity range, shape — no external metadata).
- **Preprocessing (OLD pipeline):** config.py (Real_Ct, Synthetic, Gmm_Ready presets); contrast.py (white top-hat, CLAHE, percentile saturation); diffusion.py (Perona-Malik, exponential + rational conduction modes); normalization.py (range scaling, percentile clip, z-score); diagnostics.py (Sobel edge strength, book bounds, page peak finding via scipy.signal.find_peaks, histogram plotting); pipeline.py (orchestration with timing + auto-scaled params).
- **Segmentation:** gmm_fitter.py (BIC-based K selection, probability prediction, material stats); hierarchy.py (recursive splitting, weighted BIC, LRT with chi-squared); hmrf.py (ICM, 6- and 26-connectivity Potts prior); decision_engine.py (flat GMM → hierarchy → HMRF).
- **Analysis:** material_stats.py (counts, fractions, intensity stats + console report); uncertainty_maps.py (Shannon entropy, max probability, margin); page_extractor.py (connected-component labeling, centroids — placeholder for Charles' integration).
- **Visualization:** napari_viewer.py (image + labels + probability layers); plot_distributions.py (GMM overlay on histograms); export.py (probability videos, colored label stacks).
- **Tests:** conftest.py fixtures (synthetic volume, flat intensities, bimodal, trimodal); test_io, test_preprocessing, test_segmentation, test_analysis coverage as listed.
- **Notebooks:** 01_explore_raw_data, 02_run_preprocessing, 03_fit_gmm (with chunking), 04_apply_hmrf (beta tuning on subset), 05_visualize_results.

**Code quality claimed achieved:** Google-style docstrings on all public APIs; type hints throughout; modular files (no file > 300 lines); descriptive error handling; memory-efficient chunking; progress logging for long-running ops.

**Issues hit / open at this point:** No real data loaded yet; all validation still pending. Success hinges on Week 3 (meaningful GMM components on real CT data).

## Planned Methodology Log (LABORATORY_NOTEBOOK.md §5 — Phases, as intentions)

- **Phase 1 — EDA (Week 1):** load raw TIFF; global + per-slice histograms; stationarity via variogram/slice-wise stats; inspect Z-slices; identify book bounds/pages. Deliverables: data quality report, histogram analysis, stationarity assessment, initial hypothesis on # material classes.
- **Phase 2 — Preprocessing (Weeks 1–2):** White Top-Hat (disk radius ~1.5% of image dims) → CLAHE (clip limit prevents noise amplification) → Percentile Saturation (clip 0.5%/99.5%, rescale to [0,255]) → Anisotropic Diffusion (Perona-Malik; iters 50, kappa 75, gamma 0.1). Diagnostics: per-slice edge strength (Sobel magnitude mean), book bounds, page peaks (scipy.signal.find_peaks), histogram before/after.
- **Phase 3 — Flat GMM (Weeks 2–3):** flatten to 1D; for K in [K_min,K_max]: k-means++ init, EM to convergence, compute BIC; select min-BIC K; MAP hard labels + soft posteriors. Outputs: label volume, probability volume, component stats, BIC curve.
- **Phase 4 — Hierarchical Refinement (Weeks 4–5):** per component fit 2-component sub-GMM on responsibility-weighted data; BIC_parent vs BIC_split; LRT; accept split if BIC_split < BIC_parent AND p < alpha; recurse; re-fit flat GMM with leaf count as K. Outputs: JSON tree, expanded GMM, split justifications.
- **Phase 5 — HMRF (Weeks 5–6):** compute log-posteriors; init from GMM MAP; 6- or 26-connectivity; per-voxel energy `E(k) = -log P(x_i|k) + beta*sum[delta(L_j != k)]`; assign min energy; iterate to convergence. Tuning: start beta=0.5 on small subset, visual GMM-only vs HMRF.
- **Phase 6 — Analysis & Validation (Weeks 7–8):** material stats (voxel count, volume fraction, mean/std per class); uncertainty (entropy, max prob, margin); visualization (2D overlays, 3D napari, GMM decomposition, uncertainty heatmaps, probability videos); validation (stability under init perturbation, physical plausibility via connected components, cross-validation on held-out voxels).
- **Phase 7 — Integration & Documentation (Week 9):** clean code + docstrings + README; reproducible notebooks; figures; document parameter rationale; outline next steps.

## Timeline & Milestones (LABORATORY_NOTEBOOK.md §10 — 9-Week Schedule)
| Week | Phase | Activities | Deliverable | Risk |
|---|---|---|---|---|
| 1 | EDA + Setup | Load data, histograms, theory study | Data quality report; env setup | Low |
| 2 | Preprocessing | Implement contrast + diffusion | Working pipeline; diagnostic plots | Low |
| 3 | Flat GMM | GMM fitting with BIC; visualization | Automatic K selection; component plots | Low |
| 4 | Hierarchy | Recursive splitting; tree structure | Hierarchical model; split justifications | Medium |
| 5 | HMRF | Spatial regularization; parameter tuning | Smoothed labels; beta sensitivity analysis | Medium-High |
| 6 | Analysis | Statistics, uncertainty, validation | Quantified results; stability report | Medium |
| 7 | Visualization | Napari integration, export tools | Interactive 3D viewer; publication figures | Low |
| 8 | Integration | Notebooks, documentation, tests | Reproducible workflow; test coverage | Low |
| 9 | Report | Write-up, presentation, next steps | Final report; clear roadmap | Low |

## Contingency Plans (LABORATORY_NOTEBOOK.md §10)
| If This Fails | Then Do This |
|---|---|
| GMM components don't map to materials | Add spatial features (local texture, gradient magnitude) as additional dimensions |
| HMRF too slow for full volume | Run on representative subset; use as post-processing filter only |
| Ink invisible in CT | Document limitation; focus on paper/cover segmentation; suggest phase-contrast CT |
| Cover and paper indistinguishable | Use shape features (cover is thicker, at boundaries); hierarchical splitting |
| BIC selects too many/few components | Inspect BIC curve manually; use domain knowledge to constrain K |

## 2026-07-10 — Context snapshot AI_CONTEXT.md
**State claimed:** Workflow documents preprocessing as pipeline.py (Preprocess_For_Gmm): White Top-Hat → CLAHE → Percentile Saturation → Anisotropic Diffusion → Diagnostics. Segmentation exports Gmm_Fitter + Segmentation_Engine (no DP-GMM). Covariance_Type default "full". Dtypes float64. Memory §6.2 solutions: subset, chunking (claimed already implemented in 03_fit_gmm.ipynb), downsample Volume[::4,::4,::4]. Root directory lists LABORATORY_NOTEBOOK.md. HMRF-too-slow note references "1B voxels".

## 2026-07-28 — Context snapshot AI_CONTEXT_2.md
**State claimed / changes recorded:** Preprocessing replaced with pipeline_revised.py (Preprocess_For_Gmm_Revised): Global Background Correction → Gaussian Smoothing → [Optional Z-Score Per Slice] → Global Percentile Normalization → Histogram Diagnostics. Old visual pipeline declared "PERMANENTLY DEPRECATED for GMM input ... retained only for visualization of results." Added dp_gmm.py (Dp_Gmm_Fitter) + test_dp_gmm.py + explicit Fit DP-GMM / Run hierarchy entry points + interface-parity design note. Added 32 GB RAM constraint (float32 mandatory; subsample every 3rd slice → 67 slices). Covariance_Type default "tied". Dtypes: raw uint16, preprocessed/flat/responsibilities float32. visualization adds histogram_diagnostics.py. Root directory omits LABORATORY_NOTEBOOK.md. HMRF-too-slow note references "250M voxels". Memory §6.2 solutions: subset, float32 (mandatory), subsample Volume[::3], chunking for HMRF.

> All 11 conflicts resolved (2026-07-29, verified 2026-07-31). See systemPatterns.md and techContext.md for resolution details. Do NOT assume snapshot claims reflect implemented code — verify against actual repo.

## 2026-07-31 — Memory Bank Audit & Update

**Goal:** Reconcile memory bank documentation against actual code in the repo.

**Verified implementation state:**
- Package lives under `src/research_ct/` with `setuptools.find where = ["src"]` in pyproject.toml.
- **Sparse Bayesian GMM** implemented as `sparse_bayesian_gmm.py` (class: `Sparse_Bayesian_Gmm`), using sklearn BayesianGaussianMixture. Test file: `test_sparse_bayesian_gmm.py`. This is the DP-GMM alternative that was marked "planned" in previous snapshots.
- **volume_saver.py** added with lazy memmap loading, chunked streaming (`Load_From_Numpy_Chunked`, `Reduce_Streaming`), and convenience wrappers (`Compute_Labels_From_Probabilities`, `Compute_Confidence_From_Probabilities`). `_npz_registry` keeps .npz archives alive for lazy views.
- **histogram_diagnostics.py** — computational tools (Assess_Gmm_Readiness, Compute_Histogram_Statistics, Count_Visible_Modes).
- **histogram_diagnostics_viewer.py** — visualization tools (Plot_Histogram_Comparison, Plot_Slice_Histograms).
- **Notebooks renamed:** `03_gmm_and_hierarchical_segmentation.ipynb` (was `03_fit_gmm.ipynb`), `04_spatial_hmrf.ipynb` (was `04_apply_hmrf.ipynb`), `05_uncertainty_and_visualization.ipynb` (was `05_visualize_results.ipynb`).
- **decision_engine.py** — `Hierarchy_Max_Depth` default = 5 (was 3). `Run()` accepts `Use_Hierarchy` and `Use_Hmrf` flags.
- **hierarchy.py** — Internal tree structure uses `Trees` (list of dicts) and `Leaf_Nodes` (list of dicts). No single `Component_Tree` dict.
- **Memory strategy:** float64 for compute; float32 for persisted probability arrays on disk. Lazy memmap is default. `gc.collect()` forced after large operations (Windows-specific).
- **C-DTYPE resolution clarified:** Not pure float64 — mixed float64 (compute) / float32 (disk).
- **Data directories:** `src/research_ct/data/` with `raw/`, `output/`, `output/figures/`, `output/diagnostics/`, `output/processed/`.
- **requirements.txt** includes additional deps: `tifffile`, `nibabel`, `vedo`, `ipympl`, `jupyter`.
- **Test suite** has 12 test files: io (2), preprocessing (4), segmentation (4), analysis (1), plus conftest.py.

**Memory bank files updated:** systemPatterns.md, techContext.md, activeContext.md, progress.md. projectbrief.md and productContext.md unchanged (scope/context still accurate).

## Conclusion / Overall Status Assessment (LABORATORY_NOTEBOOK.md §14)
**Key strengths claimed:** fully unsupervised; probabilistic output; hierarchical (mirrors material taxonomy); spatially aware (HMRF); well-tested (pytest + synthetic fixtures); interactive (Jupyter); extensible.
**Key risks to monitor:** ink visibility depends on composition/resolution; HMRF computational cost on full volumes; validation without ground truth inherently limited.
**Verdict:** "The project is feasible and well-scoped. The code infrastructure is complete and ready for real data. Success in Week 3 (meaningful GMM components on actual CT data) will be the critical inflection point." (Recorded as a source claim, not verified.)

## Uncategorized — please review
- **Glossary (LABORATORY_NOTEBOOK.md Appendix A):** BIC, CLAHE, EM, GMM, HMRF, ICM, LRT, MAP, MRF, Potts Model, Top-Hat, Voxel — full definitions retained in source; parked here as reference material that didn't map cleanly to a single memory-bank section.
- **XRF Glossary (added 2026-08-09):** BCF (Bruker Composite File), CLR (Centered Log-Ratio), CoDa (Compositional Data Analysis), Leaf Signature (F_h — per-page compositional+spatial descriptor vector), XRF (X-Ray Fluorescence), MAD (Median Absolute Deviation).

## 2026-08-09 — Dual-Modal Pipeline Milestone

**Goal:** Execute both CT and XRF pipelines on real data; identify remaining gaps; document full implementation state.

**CT Pipeline (`research_ct`) executed on `Brevar Capucin`:**
- Raw: ~431 TIFF slices loaded from `data/raw/`.
- Preprocessing: pipeline_revised.py ran successfully; outputs in `data/output/processed/`.
- Segmentation: GMM (BIC selected K), Sparse Bayesian GMM comparison, hierarchical refinement all executed.
- HMRF: regularized labels generated in `data/output/hmrf_labels.npz`.
- Analysis: `material_stats.csv`, `high_uncertainty_regions.csv`, `per_slice_material_fractions.csv` produced.
- Visualization: Uncertainty maps, probability videos, napari-compatible exports generated in `data/output/figures/`.

**XRF Pipeline (`xrf`) executed on `Letter_1`:**
- Raw: Elemental TIFFs (Pb, K, Hg, Fe, Cu, Ca, Au, As) loaded from `data/xrf/raw/`.
- Preprocessing: BCF extraction workflow ready (TIFFs already present; BCF source in `data/xrf/bcf/`).
- CLR transform and PCA reduction applied.
- GMM segmentation produced 7 clusters; per-cluster masks exported as Fiji-compatible TIFFs.
- Spatial descriptors (Num_Regiones, Tamano_Promedio) computed per class.
- Leaf signature F_h and book-level weighted signature computed.
- Category signatures, rarity scoring, and spatial comparison modules ready for page-category tagging.

**Gaps identified:**
- `src/xrf/fusion/ct_xrf_fusion.py` is empty (0 bytes) — CT+XRF fusion not implemented.
- README.md still points to old `src/` paths (missing `research_ct/` prefix).
- XRF notebooks were not catalogued in memory bank before 2026-08-09 — 8 notebooks exist and are now documented.

**Memory bank files updated:** systemPatterns.md, techContext.md, productContext.md, activeContext.md, progress.md. projectbrief.md annotated with proposed changes.
