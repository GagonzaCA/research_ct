# systemPatterns.md

> Merged from: AI_CONTEXT.md, AI_CONTEXT_2.md, LABORATORY_NOTEBOOK.md
> NOTE: Treat all claims as proposals/intentions, not confirmed implementation.

## High-Level Workflow (structure common to all sources)

### CT Pipeline
```
RAW TIFF STACK
  → [IO: volume_loader.py] → 3D numpy array (D, H, W)
  → [PREPROCESSING]  (resolved: pipeline_revised.py for GMM; pipeline.py retained for visualization)
  → [SEGMENTATION: decision_engine.py]
       ├── gmm_fitter.py: fit GMM, BIC selects K
       ├── sparse_bayesian_gmm.py: Bayesian GMM with automatic K via sparse Dirichlet prior
       ├── hierarchy.py: recursively split components if statistically justified
       └── hmrf.py: spatial regularization via Potts model + ICM
  → Outputs: Labels (D, H, W), Probabilities (D, H, W, K)
  → [ANALYSIS] material_stats.py, uncertainty_maps.py
  → [VISUALIZATION] napari_viewer.py, plot_distributions.py, export.py, histogram_diagnostics_viewer.py
```

### XRF Pipeline (verified 2026-08-09)
```
BCF HYPERCUBE / ELEMENTAL TIFFs
  → [IO: xrf_loader.py] → elemental data cube (M, N, n_elements)
  → [PREPROCESSING: bcf_extractor.py] → dual-window Bremsstrahlung subtraction, per-element TIFFs
  → [TRANSFORMS: coda.py] → CLR transformation (compositional → Euclidean)
  → [SEGMENTATION: xrf_gmm.py] → PCA + GMM clustering in latent space
  → [SPATIAL: spatial_analyzer.py] → class map + connected-component descriptors (Num_Regiones, Tamano_Promedio)
  → [SIGNATURES: leaf_signature.py] → per-page leaf signature F_h (abundances + spatial stats)
  → [COMPARISON] category_signatures.py, rarity_scoring.py, spatial_comparison.py
       → category norms, robust deviation scoring, page-level rarity flagging
  → [FUSION: ct_xrf_fusion.py] EMPTY PLACEHOLDER — not yet implemented
```

## Package Architecture: `src/research_ct/`

- **io/** — volume_loader.py, volume_saver.py, metadata_parser.py. Exports: Load_Slice_Stack, Load_From_Numpy, Load_From_Numpy_Chunked, Load_From_Numpy_Slab, Reduce_Streaming, Compute_Labels_From_Probabilities, Compute_Confidence_From_Probabilities, Save_As_Numpy, Save_Volume_As_Stack, Load_Metadata, Scan_Metadata. (verified 2026-07-31)
- **preprocessing/** — **Resolved:** `pipeline_revised.py` (background_correction.py, noise_reduction.py, global_normalization.py, histogram_diagnostics.py) is the active GMM pipeline. `pipeline.py` (contrast.py, diffusion.py, diagnostic.py) is retained for visualization. `normalization.py` was deleted; `global_normalization.py` handles all normalization.
- **segmentation/** — gmm_fitter.py (Gmm_Fitter), hierarchy.py (Hierarchical_Gmm), hmrf.py (Hmrf_Segmenter), sparse_bayesian_gmm.py (Sparse_Bayesian_Gmm), decision_engine.py (Segmentation_Engine). **Sparse_Bayesian_Gmm implemented — uses sklearn BayesianGaussianMixture with sparse Dirichlet prior. Active in notebook segmentation pipeline.**
- **analysis/** — material_stats.py (Compute_Material_Statistics, Print_Material_Report), uncertainty_maps.py (Compute_Uncertainty, Compute_Margin), page_extractor.py (Extract_Page_Surfaces, Get_Page_Centroids). (AI_CONTEXT.md, AI_CONTEXT_2.md)
- **visualization/** — napari_viewer.py (launch_napari_viewer), plot_distributions.py (plot_gmm_components), export.py (export_probability_video, export_label_colors), histogram_diagnostics_viewer.py (Plot_Histogram_Comparison, Plot_Slice_Histograms).

### Repository Layout (verified 2026-07-31, updated 2026-08-09)
> **Note (2026-07-31):** Package lives under `src/research_ct/`. `normalization.py` was deleted; replaced by `global_normalization.py`.
> **Note (2026-08-09):** `xrf/` package added alongside `research_ct/`. Dragonfly export modules added to research_ct.

```
src/research_ct/
├── io/               volume_loader.py, volume_saver.py, metadata_parser.py,
│                     dragonfly_exporter.py
├── preprocessing/    config.py, contrast.py, diffusion.py, diagnostic.py, pipeline.py,
│                     background_correction.py, noise_reduction.py, global_normalization.py,
│                     histogram_diagnostics.py, pipeline_revised.py
├── processing/       dragonfly_utils.py
├── segmentation/     gmm_fitter.py, hierarchy.py, hmrf.py, sparse_bayesian_gmm.py,
│                     decision_engine.py
├── analysis/         material_stats.py, uncertainty_maps.py, page_extractor.py
├── data/             raw/, output/, output/figures/, output/diagnostics/, output/processed/
└── visualization/    napari_viewer.py, plot_distributions.py, export.py,
                      histogram_diagnostics_viewer.py

src/xrf/
├── config.py                Bcf_Extraction_Config, Xrf_Preprocessing_Config,
│                            Xrf_Segmentation_Config, Leaf_Signature_Config,
│                            Xrf_Comparison_Config
├── io/                      xrf_loader.py (Xrf_Loader)
├── preprocessing/           bcf_extractor.py (Bcf_Element_Extractor)
├── segmentation/            xrf_gmm.py (Xrf_Gmm_Segmenter)
├── transforms/              coda.py (Clr_Transformer)
├── spatial/                 spatial_analyzer.py (Spatial_Analyzer)
├── signatures/              leaf_signature.py (Leaf_Signature_Extractor)
├── comparison/              category_registry.py (Category_Registry),
│                            category_signatures.py (Category_Signature_Aggregator),
│                            rarity_scoring.py (Rarity_Scorer),
│                            spatial_comparison.py (Category_Spatial_Comparator)
└── fusion/                  ct_xrf_fusion.py (EMPTY — placeholder, not implemented)
```

## Key Design Decisions (with reasoning)

### From AI_CONTEXT.md / AI_CONTEXT_2.md
- **CRITICAL DESIGN:** Each algorithm is independent. decision_engine.py wires them together but any component can be used standalone. (both)
- **Interface parity (verified 2026-07-31):** Gmm_Fitter and Sparse_Bayesian_Gmm share similar public interfaces (Fit, Predict_Probabilities, Predict_Labels, Get_Material_Statistics). decision_engine.py currently injects Gmm_Fitter directly but the Bayesian variant is used independently in notebooks.
- **Ink-first page inference:** use high-confidence ink voxels (P(ink) > 0.7) rather than all bright voxels (both; see productContext.md).

### From LABORATORY_NOTEBOOK.md — Key Design Decisions table
| Decision | Rationale |
|---|---|
| **Unsupervised (no ground truth)** | Cultural heritage reality; no labeled datasets exist |
| **Intensity-only first** | Simplest valid approach; spatial added only if needed |
| **Probabilistic output** | Essential for handling overlaps; enables uncertainty quantification |
| **Modular pipeline** | Each phase can be run independently, tuned, or replaced |
| **Python + scientific stack** | Mature ecosystem; napari for visualization; sklearn for GMM |
| **BIC over AIC** | Stronger penalty for complexity; preferred for model selection |
| **HMRF as optional** | Adds significant runtime; only used if GMM output is too noisy |

## Preset Definitions

- **Real_Ct:** Aggressive enhancement, includes thresholding (Threshold_Percentile=85.0). **Legacy — used only by visualization pipeline (pipeline.py); not for GMM.**
- **Synthetic:** Minimal processing for clean data. (all sources)
- **Gmm_Ready:** Balanced, NO THRESHOLDING (let GMM handle separation). (all sources)

## Mathematical & Theoretical Foundations (common to AI_CONTEXT.md and AI_CONTEXT_2.md unless noted)

### Physics of Micro-CT
- Beer-Lambert law: `I = I_0 * exp(-integral of mu(x,y,z) ds)`. Reconstructed voxel intensity v(x,y,z) ≈ proportional to mu.
- Photon counting: `N ~ Poisson(lambda)`; after log-transform + reconstruction, voxel values ≈ Gaussian by CLT: `v_i ~ Normal(mu_k, sigma_k^2)` if voxel i belongs to material k.
- KEY IMPLICATION: Each material class generates a Gaussian distribution of intensities; overall histogram is a mixture of these Gaussians.

**Complicating Factors — resolved (C-MITIG):**
| Factor | Effect | Mitigation |
|---|---|---|
| Beam hardening | Lower-energy photons attenuated more; cupping artifact | Global background correction (large Gaussian subtraction) |
| Partial volume effects | Boundary voxels have mixed intensities | HMRF spatial regularization |
| Poisson noise | Variance proportional to mean | Mild Gaussian smoothing (sigma=0.8) |
| Ring artifacts | Circular intensity variations | Preprocessing filtering |
| Material degradation | Changed attenuation properties | Hierarchical splitting adapts |

### GMM
- Definition: `p(x) = sum_k [ pi_k * Normal(x | mu_k, sigma_k^2) ]`, with `pi_k >= 0`, `sum_k pi_k = 1`.
- Log-likelihood: `ln L(theta) = sum_i ln( sum_k pi_k * Normal(x_i | mu_k, sigma_k^2) )`.
- **EM algorithm:** E-step computes responsibilities `gamma_{i,k}`; M-step updates `N_k = sum_i gamma_ik`, `mu_k`, `sigma_k^2`, `pi_k = N_k / N`.
- Properties: monotonic convergence to a local maximum; sensitive to initialization; **k-means++ initialization is used**; multiple random inits for global optimum.
- **BIC:** `BIC(K) = -2 * ln(L_hat_K) + p_K * ln(N)`, where `p_K = 3K - 1` (K means + K variances + (K-1) independent weights).
- BIC procedure: fit K = K_min..K_max, select `K* = argmin_K BIC(K)`.
- **Adjustment for this problem:** K_min = 2 (at least air + solid), K_max = 8 (air, paper, ink, cover, adhesive, noise, and margin). Multiple random inits (via scikit-learn). If BIC curve is flat, domain knowledge breaks ties.
- BIC limitations: assumes model in "correct" class; small N tends to underfit (AIC may be preferred); local optima → multiple inits essential.

### Sparse Bayesian GMM (sparse_bayesian_gmm.py — verified 2026-07-31)
- Implemented using sklearn's BayesianGaussianMixture with a sparse Dirichlet weight prior (weight_concentration_prior_type="dirichlet_distribution").
- Truncate at Max_Components (default 10); components with weight < Weight_Threshold (1e-3) or effective samples < Min_Samples (1000) are pruned.
- After pruning, remaining K_active components are the discovered materials. Weights are renormalized to sum to 1.
- Class name: Sparse_Bayesian_Gmm. Methods: Fit, Predict_Probabilities, Predict_Labels, Get_Material_Statistics.
- Comparison: BIC fits many models & selects one (more deterministic); Sparse Bayesian fits one overcomplete model that self-prunes (more elegant but sensitive to weight_concentration_prior).

> **Decision (2026-07-29, implemented 2026-07-31):** sparse_bayesian_gmm.py is implemented. Sparse_Bayesian_Gmm shares a similar public interface as Gmm_Fitter. Used independently in notebook 03_gmm_and_hierarchical_segmentation.ipynb for side-by-side comparison with BIC-GMM.

### Hierarchical GMM
- Motivation: flat GMM fails for nested structure (e.g., "organic matter" → "paper"/"cover"); ink sub-types (carbon-based vs iron-gall); K varies by intensity region.
- Algorithm: fit initial GMM K_0; for each component extract weighted subset with weights `gamma_ik`; fit 2-component sub-GMM; compare BIC parent vs split; LRT statistic `Lambda = 2*(ln L_split - ln L_parent)`; under H_0, `Lambda ~ chi^2_{df}` with df = 3 (mean, variance, weight); accept split if `BIC_split < BIC_parent AND p < alpha`; recurse; collect leaves = new K; re-fit flat GMM. Output: JSON-serializable tree + refined flat GMM.
- Weighted BIC uses effective sample size `N_k^ = sum_i gamma_ik`.
- KEY FEATURE: hierarchy provides interpretability — each split corresponds to a physical material subdivision.

### HMRF
- Motivation: GMM treats voxels independently (physically unrealistic — ink clusters along strokes, paper forms sheets, air fills voids). Spatial coherence resolves ambiguous voxels.
- MRF Markov property: `P(L_i | L_{V\{i}}) = P(L_i | L_{N_i})`. Joint = Gibbs distribution `P(L) = (1/Z) exp(-U(L))`.
- **Potts model:** `U_spatial(L) = beta * sum_{<i,j>} delta(L_i != L_j)`; higher beta = stronger smoothing = larger homogeneous regions.
- **Full HMRF energy:** `U(L) = sum_i [ -ln p(x_i | L_i) ] + beta * sum_{<i,j>} delta(L_i != L_j)`.
- **ICM (Iterated Conditional Modes):** greedy coordinate descent from GMM MAP init; per voxel `E_{i,k} = -ln p(x_i|k) + beta * sum_j delta(k != L_j)`; assign argmin; stop when no changes or max iters.
- Neighborhoods: 6-connectivity (faster, preserves thin structures) vs 26-connectivity (stronger smoothing, slower). DEFAULT: 6-connectivity.
- beta tuning: 0.1–0.3 weak; 0.5–1.0 moderate (default); 2.0+ strong (risk losing thin structures). Tuning procedure: run on ~50-slice subset with beta=0.5, visually compare GMM-only vs HMRF, adjust.
- Limitations: isotropic smoothing (uniform beta suboptimal); stationary GMM assumption (beam hardening causes drift; local GMM may be needed); ICM greedy (may miss better configs; simulated annealing alternative); computational cost O(N*K*T*|N|).

### Preprocessing math — Both pipelines exist; pipeline_revised.py (below) is the active GMM pipeline, pipeline.py above for visualization.
- **White Top-Hat (AI_CONTEXT.md, LABORATORY_NOTEBOOK.md):** `T_white(f) = f - (f ∘ b)`; disk radius auto-scaled to ~1.5% of image dimensions.
- **CLAHE (AI_CONTEXT.md, LABORATORY_NOTEBOOK.md):** local tiles, clip histogram at clip limit C, interpolate; kernel_size default auto-scaled to image_size // 8; clip_limit default 0.05–0.1.
- **Perona-Malik Anisotropic Diffusion (AI_CONTEXT.md, LABORATORY_NOTEBOOK.md):** `∂I/∂t = div(c(x,y,t) grad(I))`; exponential form `c = exp(-(grad I/kappa)^2)`; rational form `c = 1/(1+(grad I/kappa)^2)`; iterations 50, kappa 75, gamma 0.1 (must be ≤ 0.25 for 2D stability).
- **Global Background Correction (AI_CONTEXT_2.md):** `Background = G_sigma * I`, `I_corrected = I - Background`; sigma ≈ 30 voxels; auto-scaled ~1.5–5% of image dims or manually 30.
- **Mild Gaussian Smoothing (AI_CONTEXT_2.md):** isotropic Gaussian sigma = 0.8 voxels (range 0.5–1.5); reduces Poisson/reconstruction noise via CLT; linear & shift-invariant, preserves global mixture structure.
- **Global Percentile Normalization (AI_CONTEXT_2.md):** `I_norm = (I - P_low)/(P_high - P_low) * (Target_Max - Target_Min) + Target_Min`. CRITICAL DISTINCTION FROM CLAHE: CLAHE applies different transforms per tile, destroying global relationships; global normalization does not.

### Uncertainty Quantification (all sources)
- **Shannon Entropy:** `H_i = -sum_k gamma_ik * ln(gamma_ik)`; 0 = certain, ln(K) = max uncertainty.
- **Margin:** `M_i = gamma_{i,k1} - gamma_{i,k2}`; ~0 highly ambiguous, ~1 highly confident.
- **Max Probability** (LABORATORY_NOTEBOOK.md) — confidence measure.

## Data Structures — resolved (C-DTYPE: float64 throughout)
| Structure | Type | Shape | Purpose |
|---|---|---|---|
| Raw volume | np.ndarray float64 | (D, H, W) | Input: reconstructed CT intensities — cast to float64 at pipeline entry |
| Preprocessed volume | np.ndarray float64 | (D, H, W) | After preprocessing (pipeline_revised.py line 78) |
| Flat intensities | np.ndarray float64 | (N,1) or (N,) | Input to GMM; N = D*H*W (or subsampled) |
| Responsibilities | np.ndarray float64 | (N, K) | E-step output; gamma_ik (sklearn default) |
| Hard labels | np.ndarray | (D, H, W), int32 | MAP component assignment |
| Probability volume | np.ndarray | (D, H, W, K), float32 | Full posterior distribution |
| Log-probabilities | np.ndarray | (D, H, W, K), float32 | Input to HMRF energy computation |
| Entropy map | np.ndarray | (D, H, W), float32 | Uncertainty visualization |
| Label tree | dict | Recursive | Hierarchical component structure |
| Metadata | dataclass | Scalar fields | Volume properties inferred from array |

### XRF Data Structures (added 2026-08-09)
| Structure | Type | Shape | Purpose |
|---|---|---|---|
| Elemental data cube | np.ndarray float64 | (M, N, n_elements) | Raw XRF intensities per element |
| CLR data | np.ndarray float64 | (N_valid, n_elements) | Log-ratio transformed proportions |
| Class map | np.ndarray int32 | (M, N) | Per-pixel GMM class assignment |
| Leaf signature F_h | np.ndarray float64 | (n_classes + n_spatial,) | Per-page descriptive vector |
| Category median/MAD | np.ndarray float64 | (n_classes,) | Robust category-level norms |

## Spatial Context & Geometric Priors (LABORATORY_NOTEBOOK.md §2.5)
- Ink → thin elongated structures (text strokes); Paper → extended planar sheets; Covers → thick rigid boundaries; Air → exterior + inter-page gaps.
- Post-segmentation exploitation: connected component analysis (remove isolated noise), morphological filtering (smooth boundaries), normal vector estimation (Charles'), surface fitting (virtual flattening).

## Validation Without Ground Truth (LABORATORY_NOTEBOOK.md §2.6)
- Stability Analysis (initialization perturbations); Internal Metrics (Silhouette score, Davies-Bouldin index, log-likelihood on held-out data); Physical Plausibility; Cross-Modal Comparison; Expert Visual Inspection.

## Resolved Conflicts (all 6 from this file — updated 2026-07-31)

- **C-PIPE:** pipeline_revised.py (Option C) for GMM; pipeline.py (Option A/B) for visualization.
- **C-NORM:** normalization.py deleted; global_normalization.py is sole normalization module.
- **C-PRESET:** config.py kept; Real_Ct is legacy/visualization-only (thresholding included, not for GMM).
- **C-DTYPE:** float64 for preprocessing/computation; float32 for persisted probability arrays on disk (code-verified).
- **C-MITIG:** Background correction for beam hardening + mild Gaussian smoothing for Poisson noise (Option B). Matches active pipeline_revised.py.
- **C-DPGMM:** sparse_bayesian_gmm.py implemented. Sparse_Bayesian_Gmm used in notebook segmentation pipeline for comparison with BIC-GMM.
