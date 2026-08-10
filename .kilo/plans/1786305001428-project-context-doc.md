# Plan: Produce `PROJECT_CONTEXT.md`

## Status
Research/documentation task. No source code inspected requires changes — this plan's deliverable IS the final document content below. An implementation-capable agent (or the user) should copy the "Final Document Content" section verbatim into a new file at the repo root: `PROJECT_CONTEXT.md`.

## How this was produced
- Read the full memory bank (`.kilo/rules/memory-bank/{projectbrief,productContext,systemPatterns,techContext,activeContext,progress}.md`) — covers the Micro-CT pipeline in depth but does **not** mention the XRF pipeline at all.
- Read XRF source directly since it is undocumented in the memory bank: `src/xrf/{config.py, io/xrf_loader.py, transforms/coda.py, segmentation/xrf_gmm.py, signatures/leaf_signature.py, spatial/spatial_analyzer.py, fusion/ct_xrf_fusion.py (empty stub), visualization/xrf_plots.py (empty stub)}`.
- Cross-checked memory-bank claims against real code: `gmm_fitter.py`, `hmrf.py`, `sparse_bayesian_gmm.py`, `decision_engine.py`, `pipeline_revised.py`, `uncertainty_maps.py`.
- Inspected `data/xrf/raw/` (element TIFFs: Pb, K, Hg, Fe, Cu, Ca, Au, As) and `data/xrf/output/` (per-page `.npy` artifacts, `Cluster_0..7` figures/masks, `book_global_signature.npy`) to confirm the XRF pipeline is implemented and has produced real outputs (8 clusters, matching `Gmm_Max_K=8` default).
- Verified there is no XRF test suite (`tests/` only covers `io`, `preprocessing`, `segmentation` (CT), `analysis` for the CT side) and `xrf/fusion` + `xrf/visualization` are placeholder/empty files — flagged as a gap in the document.

## Task for the implementation agent
1. Create `PROJECT_CONTEXT.md` at the repository root (`C:\Users\gabri\Documento\Mitacs\research_ct\PROJECT_CONTEXT.md`).
2. Paste the exact Markdown from "Final Document Content" below, unmodified.
3. No other files should be changed.

## Validation
- Confirm the new file exists at repo root and renders as valid Markdown.
- No code, tests, or notebooks are touched by this task.

## Open notes for the user (not blocking)
- The XRF `fusion/` (CT-XRF fusion) and `visualization/xrf_plots.py` modules are currently empty stub files — the document marks CT-XRF fusion as **planned/not implemented** and multi-modal analysis as aspirational per `productContext.md`'s "Long-Term Vision".
- Per project memory-bank rules, all Micro-CT claims are sourced from `.kilo/rules/memory-bank/*.md`, which itself states these are proposals reconciled against code as of 2026-07-31 (11/11 conflicts resolved). The XRF section below is instead sourced directly from live code inspection (today), since no memory-bank coverage exists for XRF.

---

## Final Document Content (copy verbatim into `PROJECT_CONTEXT.md`)

```markdown
# Project Context: Micro-CT and XRF Analysis Pipeline

## 1. Project Overview & Scope

This repository implements **two complementary, unsupervised statistical pipelines** for non-destructive analysis of sealed/damaged historical books:

1. **Micro-CT pipeline** (`src/research_ct/`) — segments 3D X-ray micro-computed-tomography volumes into physical material classes (air, paper, ink, cover, adhesive) using unsupervised probabilistic modeling of voxel attenuation intensities. No ground-truth labels exist for historical artifacts, so the system must *discover* material classes directly from the intensity histogram rather than rely on manual thresholds or supervised training data.
2. **XRF pipeline** (`src/xrf/`) — segments 2D X-ray fluorescence elemental maps (per-chemical-element TIFF images, e.g. Pb, Hg, Fe, Cu, Au, As, Ca, K) into compositional classes representing ink/pigment recipes, using compositional-data analysis (CoDa) and Gaussian Mixture clustering in log-ratio space.

**Primary users:** the project author (methodology + eventual publication), a collaborator ("Charles") building geometric page-surface extraction that consumes ink-probability maps, social-science/humanities colleagues who need visual/interactive outputs, and future researchers extending the codebase.

**Main scientific objective:** given only raw imaging data (no scanner metadata, no calibration phantoms, no labeled training sets), automatically and reproducibly identify material/pigment classes and quantify the confidence of each assignment, enabling downstream tasks such as ink-driven virtual page unwrapping and elemental characterization of historical ink/pigment recipes.

**Relationship between the two pipelines today:** they are implemented as **separate, currently independent** packages (`src/research_ct/` for CT, `src/xrf/` for XRF). A CT–XRF fusion module (`src/xrf/fusion/ct_xrf_fusion.py`) and an XRF visualization module (`src/xrf/visualization/xrf_plots.py`) exist as **empty placeholder files** — multi-modal (CT + XRF) fusion is a stated long-term goal, not yet implemented.

## 2. Workflows and Pipelines

### 2.1 Micro-CT Pipeline

```
RAW TIFF SLICE STACK
  → [io/volume_loader.py] Load_Slice_Stack() → 3D numpy array (D, H, W)
  → [preprocessing/pipeline_revised.py] Preprocess_For_Gmm_Revised()
       1. Global background correction (beam-hardening / cupping removal)
       2. Mild Gaussian noise reduction
       3. Optional per-slice z-score standardization (only if non-stationary)
       4. Global percentile normalization → [0, 255]
       + histogram_diagnostics.py: Assess_Gmm_Readiness() (mode count, skew, kurtosis, readiness score)
  → [segmentation/decision_engine.py] Segmentation_Engine.Run()
       Step 1: gmm_fitter.py — flat GMM, BIC selects K (baseline)
               (alternative: sparse_bayesian_gmm.py — self-pruning Bayesian GMM, used independently in notebooks for comparison)
       Step 2 (optional): hierarchy.py — recursively split components if a likelihood-ratio test justifies it
       Step 3 (optional): hmrf.py — Potts-model spatial regularization via Iterated Conditional Modes (ICM)
  → Outputs: Labels (D, H, W) int, Probabilities (D, H, W, K) float
  → [analysis/] material_stats.py (per-class counts/fractions/intensity stats), uncertainty_maps.py (entropy, max-probability, margin)
  → [visualization/] napari_viewer.py (3D interactive), plot_distributions.py (GMM overlay on histograms), export.py (probability videos, colored label stacks), histogram_diagnostics_viewer.py
```

Notebook-level execution order: `01_explore_raw_data.ipynb` → `02_run_preprocessing.ipynb` → `03_gmm_and_hierarchical_segmentation.ipynb` → `04_spatial_hmrf.ipynb` → `05_uncertainty_and_visualization.ipynb`.

Each stage is designed to be independently runnable: `decision_engine.py`'s `Segmentation_Engine.Run(Volume, Use_Hierarchy=True, Use_Hmrf=True)` wires the three segmentation steps together, but `Use_Hierarchy` / `Use_Hmrf` can be individually disabled, and any component (`Gmm_Fitter`, `Hierarchical_Gmm`, `Hmrf_Segmenter`, `Sparse_Bayesian_Gmm`) can be used standalone.

A legacy visualization-only preprocessing path (`preprocessing/pipeline.py`, using `contrast.py` white top-hat/CLAHE and `diffusion.py` Perona-Malik anisotropic diffusion) is retained but is **not** used to feed the GMM — it was superseded by `pipeline_revised.py` for statistical/segmentation purposes because CLAHE's per-tile transforms destroy the global intensity relationships that a global GMM needs.

### 2.2 XRF Pipeline

```
Per-element raw TIFF files (data/xrf/raw/: e.g. Letter_1_{Pb_La, Hg_La, Fe_Ka, Cu_Ka, Au_La, As_Ka, Ca_Ka, K_Ka}.tiff)
  → [xrf/io/xrf_loader.py] Xrf_Loader.Load_Element_Stack() → element cube (M, N, n_elements), float64
  → Xrf_Loader.Compute_Intensity_Mask(Stack, Tau_Noise)
       Total_Intensity T(p) = sum over elements per pixel
       Mask = T(p) >= Noise_Threshold (default 5.0)   → discards background/substrate pixels
       Valid_Pixels = flattened (N_valid, n_elements) matrix of in-mask pixels
  → [xrf/transforms/coda.py] Clr_Transformer.Apply_Clr_Transform()
       1. Closure: normalize each pixel's element vector to proportions (sum = 1)
       2. Zero replacement: zeros → Zero_Replacement_Delta (default 1e-4), renormalize
       3. Centered Log-Ratio (CLR) transform → maps compositional simplex data into unconstrained real space R^n
  → [xrf/segmentation/xrf_gmm.py] Xrf_Gmm_Segmenter
       1. PCA dimensionality reduction, retaining Pca_Variance_Ratio (default 0.95) cumulative explained variance
       2. GaussianMixture clustering on the PCA-reduced CLR data (Gmm_Min_K=2..Gmm_Max_K=8, Covariance_Type="full")
       3. Optional: Compute_Bic_Curve() sweeps K to help choose cluster count (analogous to CT pipeline's BIC selection)
  → labels (N_valid,) + posterior probabilities (N_valid, K)
  → [xrf/spatial/spatial_analyzer.py] Spatial_Analyzer
       Reconstruct_Class_Map(): scatter flat labels back onto the original 2D (M, N) grid using the validity Mask (background filled with -1)
       Extract_Spatial_Descriptors(): connected-component analysis (8-connectivity) per class → region count, average region size — filters regions smaller than Min_Region_Size (default 10 px)
  → [xrf/signatures/leaf_signature.py] Leaf_Signature_Extractor
       Compute_Abundances(): per-page compositional signature = fractional area A_k occupied by each class k (a vector summing to 1)
       Compute_Weighted_Book_Signature(): weighted average of many pages' signatures → a single book-level/global compositional "fingerprint" F_bar
  → Outputs observed under data/xrf/output/: per-page processed arrays (`page_001_{mask,valid_pixels,clr,labels,class_map}.npy`, `page_001_meta.json`), a book-level signature (`book_global_signature.npy`), and per-cluster visualization artifacts (`Cluster_0..7_Visual.png`, `Cluster_0..7_Fiji_Mask.tiff` — masks exported for use in the Fiji/ImageJ ecosystem)
  → [xrf/visualization/xrf_plots.py] — currently an EMPTY placeholder module (no plotting code implemented yet, despite producing `_Visual.png` outputs by some other/manual means)
```

Note: there is no XRF-equivalent of the CT pipeline's Jupyter notebooks in the `notebooks/` directory and no dedicated `tests/test_xrf*` suite — the XRF pipeline currently lacks the notebook-driven and pytest-driven workflow that the CT side has.

## 3. Mathematical Models & Scientific Concepts

### 3.1 Micro-CT Mathematics

**Physics of image formation (Beer–Lambert + reconstruction statistics):**
- Beer–Lambert law: `I = I_0 · exp(−∫ μ(x,y,z) ds)`; reconstructed voxel intensity is treated as proportional to the local attenuation coefficient μ.
- Photon counting is Poisson (`N ~ Poisson(λ)`); after log-transform and tomographic reconstruction, by the Central Limit Theorem voxel intensities within a homogeneous material are treated as approximately Gaussian: `v_i ~ Normal(μ_k, σ_k²)` for voxels belonging to material k. This is the physical justification for modeling the whole-volume histogram as a **Gaussian Mixture**.
- Complicating factors and their code-level mitigations: beam hardening / cupping (mitigated by large-Gaussian background subtraction, `background_correction.py`), partial-volume boundary blending (mitigated by HMRF spatial regularization), Poisson noise (mitigated by mild Gaussian smoothing, σ≈0.8), ring artifacts (preprocessing filtering), material degradation (addressed by hierarchical component splitting rather than a fixed model).

**Gaussian Mixture Model (GMM) — `gmm_fitter.py`:**
- `p(x) = Σ_k π_k · Normal(x | μ_k, σ_k²)`, with `π_k ≥ 0`, `Σ_k π_k = 1`.
- Fit via the EM algorithm (delegated to `sklearn.mixture.GaussianMixture`): E-step computes responsibilities γ_ik; M-step updates `N_k = Σ_i γ_ik`, `μ_k`, `σ_k²`, `π_k = N_k / N`.
- k-means++ initialization; `random_state=42` fixed for reproducibility; `max_iter=1000`.
- **Model selection via BIC:** `BIC(K) = −2·ln L̂_K + p_K·ln N`. The code fits every `K` in `[Min_Components, Max_Components]` (default 2–8) and keeps the model with the lowest BIC (`self.Bic_Scores` records every candidate for inspection/plotting). BIC's stronger complexity penalty (vs. AIC) is the stated reason for preferring it, given the risk of over-fitting spurious components to noise.
- Limitations acknowledged in the design: BIC assumes the "true" model is in the tested family; can underfit on small N; is subject to local optima, hence multiple random restarts / manual BIC-curve inspection are recommended.

**Sparse (self-pruning) Bayesian GMM — `sparse_bayesian_gmm.py`:**
- Wraps `sklearn.mixture.BayesianGaussianMixture` with `weight_concentration_prior_type="dirichlet_distribution"` (a *sparse* Dirichlet prior on mixture weights) and an overcomplete truncation level `Max_Components` (default 10).
- After fitting, components are pruned to "active" status only if `weight ≥ Weight_Threshold` (default 1e-3) **and** effective sample size (`Σ_i responsibility_ik`) `≥ Min_Samples` (default 1000); a fallback keeps at least the single highest-weight component if pruning is too aggressive.
- Active weights are renormalized to sum to 1 after pruning.
- This is an alternative to the BIC sweep: instead of fitting many models and picking one, it fits **one** overcomplete model that self-prunes — described in the codebase as "more elegant but sensitive to the weight-concentration prior."

**Hierarchical GMM splitting — `hierarchy.py`:**
- Motivation: a flat GMM cannot represent nested material taxonomies (e.g., "organic matter" → paper vs. cover; ink sub-types).
- Procedure: fit an initial GMM with K₀ components; for each component, extract a responsibility-weighted subset (weights = γ_ik) and fit a 2-component sub-GMM; compare `BIC_split` vs. `BIC_parent`; compute a likelihood-ratio test statistic `Λ = 2·(ln L_split − ln L_parent)`, which under H₀ is asymptotically `Λ ~ χ²_df` with `df = 3` (mean, variance, weight); accept the split only if `BIC_split < BIC_parent AND p < Significance_Alpha` (default 0.05); recurse up to `Hierarchy_Max_Depth` (default 5); final leaf count becomes the refined K. Internally represented as `Trees`/`Leaf_Nodes` (lists of dicts), and soft leaf-path probabilities can be extracted directly via `Predict_Leaf_Probabilities()` without re-fitting a flat GMM.

**HMRF spatial regularization — `hmrf.py`:**
- Rationale: voxel-independent GMM classification is physically unrealistic since materials are spatially coherent (ink follows stroke geometry, paper forms sheets, air fills contiguous voids).
- Markov Random Field with Markov property `P(L_i | L_{V\{i}}) = P(L_i | L_{N_i})`; joint distribution is a Gibbs form `P(L) = (1/Z)·exp(−U(L))`.
- **Potts spatial prior:** `U_spatial(L) = β · Σ_{⟨i,j⟩} δ(L_i ≠ L_j)`.
- **Full energy** (exactly as implemented): `E(z) = Σ_i −log P(x_i | z_i) + β · Σ_{(i,j)∈Edges} δ(z_i ≠ z_j)`.
- Optimized via **Iterated Conditional Modes (ICM)**: greedy per-voxel coordinate descent initialized from the GMM MAP labeling; at each iteration and for each class k, compute `E_i(k) = −log P(x_i|k) + β·Σ_j δ(k ≠ L_j)` over the chosen neighborhood, assign the argmin class; iterate until no voxel changes or `Max_Iterations` (default 50) is reached.
- Neighborhoods: 6-connectivity (default; faster, better preserves thin stroke-like structures) or 26-connectivity (stronger smoothing, slower); implemented via boundary-padded shifted array views (no explicit padding array duplication across the whole volume beyond the (D,H,W) buffer).
- β (`Hmrf_Beta`, default 0.5) trades off spatial smoothness vs. fidelity to the unary GMM/posterior term; documented tuning range 0.1–2.0+ (weak → strong), typically validated visually on a small slice subset before running on the full volume.
- Known limitations (documented, not resolved in code): isotropic β is suboptimal if smoothing needs vary spatially; assumes a stationary GMM (violated under beam-hardening drift); ICM is a greedy local optimizer (can miss better global configurations; simulated annealing is a documented but unimplemented alternative); computational cost scales as `O(N·K·Iterations·|Neighborhood|)`.

**Uncertainty quantification — `uncertainty_maps.py`:**
- **Shannon entropy:** `H_i = −Σ_k p_ik · ln(p_ik)` (probabilities clipped to `[1e-10, 1.0]` to avoid `log(0)`); 0 = fully certain, `ln(K)` = maximal uncertainty.
- **Max probability (confidence):** `max_k p_ik`.
- **Margin:** difference between the top-1 and top-2 (or top-`Top_K`) sorted posterior probabilities per voxel; near-zero margin indicates ambiguity between two (or more) classes.

**Data types:** float64 is used for all in-memory computation (chosen to avoid numerical instability in EM/log computations); persisted probability arrays on disk are stored as float32 to control storage size for large volumes. Raw input is cast to float64 once at the start of `Preprocess_For_Gmm_Revised` (single allocation, subsequent steps operate in-place via `out=` parameters).

### 3.2 XRF Mathematics

**Elemental/atomic basis:** each XRF channel corresponds to a characteristic X-ray emission line of a specific element (observed channels use Kα or Lα lines, e.g. `Fe_Ka`, `Pb_La`, `Hg_La`, `Cu_Ka`, `Au_La`, `As_Ka`, `Ca_Ka`, `K_Ka`). These elements are historically associated with specific inks/pigments (e.g. iron in iron-gall ink; lead, mercury, copper, and arsenic in various historical pigments; calcium in chalk/gesso grounds; potassium as a common trace/mordant element) — the pipeline is designed to discover *compositional classes* corresponding to different ink/pigment recipes rather than to fit a physical emission-yield model.

**Compositional Data Analysis (CoDa) — `transforms/coda.py`:**
- XRF element intensities per pixel are **compositional data**: only *relative* proportions are physically meaningful (total counts vary with dwell time, sample thickness, detector geometry, etc.), so raw intensities cannot be fed directly into Euclidean-geometry methods like PCA/GMM without violating their implicit distance assumptions ("the closure problem").
- **Closure:** each pixel's element vector is renormalized to proportions summing to 1: `x_i' = x_i / Σ_j x_j`.
- **Zero replacement:** exact zero proportions are replaced by a small constant `δ` (default 1e-4) prior to taking logs, then the vector is renormalized again.
- **Centered Log-Ratio (CLR) transform:** `clr(x)_i = ln(x_i / g(x))`, where `g(x)` is the geometric mean of the composition (implemented as the arithmetic mean of the log-proportions, i.e. `ln x_i − mean_j(ln x_j)`). This projects the constrained simplex data into unconstrained Euclidean space `R^n`, making standard Euclidean statistical/clustering methods valid.

**Noise/validity gating — `io/xrf_loader.py`:**
- Total intensity per pixel `T(p) = Σ_elements Stack[p, ·]`; pixels with `T(p) < τ_noise` (`Noise_Threshold`, default 5.0) are excluded as background/substrate before any compositional analysis, since near-zero-count pixels have unreliable compositional ratios.

**Dimensionality reduction + clustering — `segmentation/xrf_gmm.py`:**
- **PCA** on CLR-transformed data, retaining components up to a target cumulative explained-variance ratio (`Pca_Variance_Ratio`, default 0.95, via `svd_solver="full"`) — reduces the n-element CLR space to a lower-dimensional space before clustering, both for statistical efficiency and to mitigate the rank-deficiency inherent to CLR-transformed data (CLR vectors always sum to zero, so the effective dimensionality is `n−1`).
- **GMM clustering** on the PCA-reduced data (`sklearn.mixture.GaussianMixture`, `Covariance_Type="full"` default, `random_state=42`), searching `Gmm_Min_K..Gmm_Max_K` (defaults 2–8) — architecturally the same BIC-driven model-selection idea used in the CT pipeline, exposed via `Compute_Bic_Curve()`.
- This mirrors the CT pipeline's GMM+BIC approach but is applied to elemental composition ratios rather than to scalar attenuation intensity, and requires the CoDa/CLR preprocessing step that the CT pipeline (a single-channel modality) does not need.

**Signature/summary statistics — `signatures/leaf_signature.py`:**
- **Per-page abundances:** `A_k = (# pixels labeled k) / (# valid pixels)` for each class `k` — a normalized histogram of compositional-class area fractions, forming a compact per-page "leaf signature" vector.
- **Book-level signature:** a weighted average across pages, `F̄ = Σ_h w_h · F_h / Σ_h w_h`, producing a single aggregate compositional fingerprint for the whole book/document (persisted as `book_global_signature.npy`).

**Spatial/morphological descriptors — `spatial/spatial_analyzer.py`:**
- Flat cluster labels are scattered back onto the original 2D pixel grid using the validity mask (`Reconstruct_Class_Map`, background filled with -1).
- **Connected Component Analysis (CCA)** (via `scipy.ndimage.label`, 8-connectivity structuring element) computes, per class, the number of valid regions and their average pixel area, filtering out components smaller than `Min_Region_Size` (default 10 px) — analogous in spirit to the CT pipeline's spatial-plausibility checks (e.g., ink should form elongated strokes, not isolated speckles), but implemented as a discrete post-hoc morphological filter rather than an embedded MRF energy term.

## 4. Code Architecture & Structures

* **Design Patterns:**
  - **Object-oriented, single-responsibility classes** wrapping (mostly) `scikit-learn` estimators: `Gmm_Fitter`, `Sparse_Bayesian_Gmm`, `Hierarchical_Gmm`, `Hmrf_Segmenter` (CT); `Xrf_Loader`, `Clr_Transformer`, `Xrf_Gmm_Segmenter`, `Leaf_Signature_Extractor`, `Spatial_Analyzer` (XRF). Most XRF classes expose only `@staticmethod`s (pure functional wrappers with no persisted instance state), whereas CT classes are stateful (`Fit()` mutates `self.Model`, `self.Labels`, etc., then `Predict_*` methods reuse fitted state) — a "fit/predict" estimator-style pattern.
  - **Orchestration / Facade pattern:** `decision_engine.py`'s `Segmentation_Engine` composes the three independent CT segmentation stages into one `Run()` call, but each stage remains independently usable — an explicit design rule ("each algorithm is independent; the decision engine wires them together").
  - **Configuration objects as dataclasses**, not dicts (`preprocessing/config.py::Preprocessing_Config`, `xrf/config.py::Xrf_Preprocessing_Config`/`Xrf_Segmentation_Config`/`Leaf_Signature_Config`) with typed fields, defaults, and preset factory methods — "configuration as data."
  - **Interface parity by convention, not inheritance:** `Gmm_Fitter` and `Sparse_Bayesian_Gmm` deliberately expose the same method names (`Fit`, `Predict_Probabilities`, `Predict_Labels`, `Get_Material_Statistics`) so they are interchangeable in downstream code, without a shared abstract base class currently enforcing this.
  - **Pure/side-effect-explicit functions:** preprocessing steps in `pipeline_revised.py` take an `out=` parameter to explicitly control in-place mutation vs. new-array allocation, minimizing memory churn on large volumes.

* **Data Structures:**
  - **N-dimensional NumPy arrays** are the backbone of both pipelines:
    - CT: 3D volumes `(D, H, W)`; flattened to `(N, 1)` or `(N,)` for 1D-intensity GMM fitting; 4D `(D, H, W, K)` for per-voxel class-probability/log-probability volumes; label volumes as 3D `int32`.
    - XRF: 3D element cubes `(M, N, n_elements)`; a 2D boolean validity `Mask (M, N)`; flattened `(N_valid, n_elements)` matrices for CLR/PCA/GMM stages; 1D label vectors `(N_valid,)`; 2D reconstructed `Class_Map (M, N)` with a sentinel fill value (-1) for excluded/background pixels.
  - **Dict/JSON-serializable trees** for the CT hierarchical GMM (`Trees`, `Leaf_Nodes` — lists of dicts capturing each split's parent/child statistics and test results), enabling interpretable inspection of *why* a component was split.
  - **Persisted artifacts on disk:** `.npz`/`.npy` for volumes, labels, probabilities, and XRF per-page arrays (mask, valid pixels, CLR data, labels, class map); `.json` for lightweight page metadata; `.tiff`/`.png` for exported label-colored figures and Fiji-compatible masks.
  - **`dataclass`-based metadata and configuration** rather than ad hoc dicts (`Preprocessing_Config`, `Xrf_*_Config` classes) — typed, documented, defaulted.

* **State Management / Data Flow:**
  - Both pipelines are **linear, staged pipelines** with each stage consuming the previous stage's array output and (for CT) an accompanying diagnostics dict; there is no shared mutable global state — data flows explicitly through function/method arguments and return values.
  - CT pipeline emphasizes **in-place array mutation with explicit `out=` buffers** to control memory footprint for large volumes (documented rationale: local machine constrained to ~32 GB RAM; university cluster access to ~560 GB RAM is occasional, not default).
  - XRF pipeline is currently **stateless/functional** at each stage (mostly static methods returning new arrays) with intermediate results persisted to disk per page (`data/xrf/output/processed/page_NNN_*.npy`) rather than kept only in memory, then aggregated into a single book-level signature — a batch/offline data-flow style rather than an in-memory streaming one.
  - Cross-pipeline (CT↔XRF) data flow is **not yet implemented**: `ct_xrf_fusion.py` is an empty file, so today the two pipelines do not exchange data programmatically despite the shared long-term vision of multi-modal fusion.

## 5. Coding Rules & Conventions

* **Naming convention (CT package, and largely followed by XRF code too):**
  - Classes: `Pascal_Case_With_Underscores` (e.g. `Gmm_Fitter`, `Hmrf_Segmenter`, `Xrf_Gmm_Segmenter`, `Clr_Transformer`).
  - Functions/methods: verb-object, same underscored Pascal style (e.g. `Load_Slice_Stack()`, `Compute_Intensity_Mask()`, `Apply_Clr_Transform()`).
  - Variables: descriptive underscored Pascal style (e.g. `Num_Components`, `Background_Sigma`, `Valid_Pixels`).
  - Constants: `UPPER_CASE` (documented convention; not densely exercised in the reviewed files).
  - Private helpers: leading underscore (e.g. `_Shifted_View`, `_Weighted_Bic` per memory bank; `_vprint` observed in `pipeline_revised.py`).
  - Type aliases for filesystem paths: `Path_Like = Union[str, Path]` (used identically in both `research_ct` and `xrf` IO modules).
* **Docstrings:** Google-style (`Args:`, `Returns:`, optionally `Raises:`) on public functions/classes; XRF module docstrings are written in **Spanish**, in contrast to CT module docstrings, which are in **English** — this is a real, observed inconsistency across the two pipelines, not a documented rule, and should be flagged/clarified if unifying language is desired.
* **Type hints:** present throughout on function signatures in both pipelines (`np.ndarray`, `Tuple`, `Dict`, `List`, `Optional`, etc.).
* **Error handling:** guard clauses raising specific exceptions with descriptive messages (e.g. `Preprocess_For_Gmm_Revised` validates `ndim`, non-empty, and `np.isfinite`; `Xrf_Loader.Load_Element_Stack` raises `ValueError` on an empty path list; `Hmrf_Segmenter._Get_Neighbors` raises `ValueError` for unsupported connectivity values; `Gmm_Fitter`/`Sparse_Bayesian_Gmm` raise `RuntimeError` if predict is called before `Fit()`).
* **Progress logging:** long-running operations print bracketed module-tag progress messages, e.g. `[Engine] ...`, `[HMRF] ...`, `[Preprocess_GMM] ...`, `[Gmm_Fitter] ...`, `[Sparse_Bayesian_Gmm] ...` — matches the documented `[ModuleName]` logging-prefix convention.
* **Modularity rules (documented in techContext.md, largely followed):** single-responsibility, files kept small (~300-line soft limit); `io`/`preprocessing` must not import from `segmentation`/`analysis` (no circular imports); pure functions preferred, `Apply_` prefix implies a transformation; configuration as dataclasses, not dicts; heavy/optional visualization libraries (`napari`, `matplotlib`) imported lazily inside functions to avoid overhead in headless environments.
* **Formatting/linting/typing tools (declared in `pyproject.toml`, dev extras):** Black (line-length 100, target Python 3.10), Flake8, Mypy (`warn_return_any=True`, `warn_unused_configs=True`, `ignore_missing_imports=True`), all under `requires-python = ">=3.10"`.
* **Testing:** Pytest suite under `tests/`, configured via `pyproject.toml` (`testpaths=["tests"]`, `test_*.py`/`Test_*`/`test_*` discovery conventions), with `conftest.py` fixtures (synthetic volume, flat intensities, bimodal/trimodal data). Coverage is CT-only today: `test_io/`, `test_preprocessing/`, `test_segmentation/` (including `test_sparse_bayesian_gmm.py`, `test_hmrf.py`, `test_hierarchy.py`, `test_gmm_fitter.py`), `test_analysis/`. **There is no XRF test directory** — a notable gap given the XRF pipeline is functionally complete for its core stages.

## 6. Known Assumptions & Constraints

* **Hardware/memory:**
  - Local development machine: Windows, ~32 GB RAM — drives the "float64 compute / float32-on-disk" split and chunked/lazy-memmap I/O design for CT volumes.
  - Occasional access to a university cluster with ~560 GB RAM, but not available continuously — code is designed to be debuggable on small subsamples/subsets locally, then scaled up opportunistically.
  - Current real CT dataset size referenced in the memory bank: ~750M voxels (≈201 slices × ~1900 × ~1900) — large enough that streaming/chunked probability computation (rather than full in-memory materialization) is treated as necessary, not optional.
* **No ground truth / no scanner metadata (CT):** all metadata (bit depth, shape, intensity range) must be inferred from the raw NumPy array itself; there is no external calibration or labeled validation set — all validation is qualitative (stability under initialization perturbation, physical plausibility, expert visual inspection) rather than accuracy-metric-based.
* **Statistical/algorithmic parameters actually used as defaults in code (verified against source, not just memory bank):**
  | Parameter | Default | Where |
  |---|---|---|
  | `Gmm_Min_K` / `Gmm_Max_K` (CT) | 1 / 10 (class default in `Gmm_Fitter.__init__`; engine wraps with 2 / 8) | `segmentation/gmm_fitter.py`, `decision_engine.py` |
  | `Covariance_Type` (CT GMM) | `"full"` | `gmm_fitter.py`, `sparse_bayesian_gmm.py` |
  | `Hierarchy_Max_Depth` | 5 | `decision_engine.py` |
  | `Hierarchy_Min_Samples` | 1000 | `decision_engine.py` |
  | `Hierarchy_Alpha` (LRT significance) | 0.05 | `decision_engine.py` |
  | `Hmrf_Beta` | 0.5 | `decision_engine.py`, `hmrf.py` |
  | `Hmrf_Iterations` | 50 | `decision_engine.py`, `hmrf.py` |
  | `Connectivity` (HMRF) | 6 | `hmrf.py` |
  | `Sparse_Bayesian_Gmm.Max_Components` | 10 | `sparse_bayesian_gmm.py` |
  | `Weight_Threshold` (sparse GMM pruning) | 1e-3 | `sparse_bayesian_gmm.py` |
  | `Min_Samples` (sparse GMM pruning, effective sample count) | 1000 | `sparse_bayesian_gmm.py` |
  | `Noise_Sigma` (CT preprocessing) | 0.8 | `pipeline_revised.py` |
  | `Clip_Low_Percentile` / `Clip_High_Percentile` | 0.1 / 99.9 | `pipeline_revised.py` |
  | `Background_Sigma` | auto-estimated from volume dims if `None` | `pipeline_revised.py` |
  | `Xrf_Preprocessing_Config.Noise_Threshold` (τ_noise) | 5.0 | `xrf/config.py` |
  | `Xrf_Preprocessing_Config.Zero_Replacement_Delta` (CLR δ) | 1e-4 | `xrf/config.py` |
  | `Xrf_Segmentation_Config.Pca_Variance_Ratio` | 0.95 | `xrf/config.py` |
  | `Xrf_Segmentation_Config.Gmm_Min_K` / `Gmm_Max_K` | 2 / 8 | `xrf/config.py` |
  | `Xrf_Segmentation_Config.Covariance_Type` | `"full"` | `xrf/config.py` |
  | `Leaf_Signature_Config.Connectivity` | 8 | `xrf/config.py` |
  | `Leaf_Signature_Config.Min_Region_Size` | 10 px | `xrf/config.py` |
  | Random seed (both GMM fits) | 42 (fixed) | `gmm_fitter.py`, `sparse_bayesian_gmm.py`, `xrf_gmm.py` |
* **Baseline physical assumptions inherent to the models (documented as risks in the memory bank, not fully mitigated in code):**
  - Voxel/pixel intensities within one material class are approximately Gaussian (Poisson→Gaussian via CLT) — may fail under heavy beam-hardening skew or heavy-tailed noise; the code does not currently implement skew-normal/t-distribution alternatives.
  - Spatial stationarity of the intensity distribution is assumed by default but explicitly checked (`Check_Slice_Stationarity`) and can be locally corrected via optional per-slice z-scoring if violated.
  - Isotropic voxel spacing is assumed by the HMRF neighborhood weighting (no voxel-size-aware anisotropic weighting is implemented).
  - CT ink may be physically invisible to attenuation-based imaging for certain ink chemistries/substrate thicknesses — an acknowledged hard limitation motivating potential XRF fusion (not yet implemented) or phase-contrast imaging (out of scope).
  - XRF CLR/PCA/GMM assumes elemental composition ratios (not raw counts) are the physically meaningful signal, and that a fixed noise-intensity threshold (`Tau_Noise`) is sufficient to separate substrate/background pixels from material-bearing pixels — no dynamic/adaptive thresholding is implemented.
* **Explicit non-goals / out-of-scope items:** no supervised learning or manually labeled training data; no manual threshold tuning as a *required* step (HMRF/threshold-based masking are optional, tunable knobs, not hard-coded cutoffs, except the XRF `Tau_Noise` gate and CT's legacy `Real_Ct` preset's `Threshold_Percentile=85.0`, which is explicitly marked legacy/visualization-only, not used for GMM); full virtual page unwrapping (meshing, texture mapping, hole handling) is explicitly out of scope — only a proof-of-concept ink-probability hand-off to a collaborator's geometric extraction is targeted; CT–XRF fusion and XRF-side visualization are aspirational (empty stub files today), not implemented.
```
