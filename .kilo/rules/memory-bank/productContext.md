# productContext.md

> Merged from: AI_CONTEXT.md, AI_CONTEXT_2.md, LABORATORY_NOTEBOOK.md
> NOTE: Treat all claims as proposals/intentions, not confirmed implementation.

## Why This Project Exists

Historical books, particularly sealed or damaged volumes, contain invaluable textual and illustrative information that cannot be accessed through conventional means without destroying the artifact. Micro-computed tomography (micro-CT) offers a non-destructive imaging modality that captures the internal three-dimensional structure of these objects at micron-scale resolution. (LABORATORY_NOTEBOOK.md)

The fundamental challenge: **how to automatically distinguish between different materials** (air, paper substrate, ink, book covers, adhesives, and other binding materials) based solely on their X-ray attenuation properties, without any pre-existing labeled training data. (LABORATORY_NOTEBOOK.md)

## Why This Is Hard (LABORATORY_NOTEBOOK.md)

- **No Ground Truth:** No pre-segmented "correct answer" to train supervised ML. Every book is unique in material composition, degradation state, and scanning conditions.
- **Overlapping Distributions:** X-ray attenuation values of different materials overlap significantly. Carbon-based ink on thick parchment may be nearly indistinguishable from thin paper regions.
- **Unknown Parameters:** Mean, variance, and shape of distributions are not known a priori and must be estimated directly from the data.
- **Scale and Noise:** Micro-CT volumes can range from gigabytes to tens of gigabytes. Poisson noise propagates through reconstruction into approximately Gaussian voxel-level noise.
- **Spatial Variation:** Beam hardening, sample positioning, and material degradation cause non-stationary intensity distributions across the volume.

## Prior Art and Inspiration (LABORATORY_NOTEBOOK.md)

- **The Herculaneum Papyri Project (Seales et al., 2011):** Demonstrated the extreme difficulty of ink detection in carbonized scrolls. Carbon-based ink can be virtually invisible in CT, requiring phase-contrast or sophisticated statistical methods.
- **The En-Gedi Scroll (2015):** First successful virtual unrolling of a charred biblical scroll using micro-CT and manual segmentation.
- **Virtual Unrolling of Historic Scrolls (Liu, Rosin et al., 2018):** Automatic layer segmentation pipelines for similar data types.
- **Diffeomorphic Spiral Fitting (Henderson, WACV 2026):** State-of-the-art geometric approach to page surface extraction, combining model-based priors with neural predictions.

Common thread: **the segmentation problem must be solved before any text can be read, and segmentation without ground truth demands unsupervised, statistically principled methods.** (LABORATORY_NOTEBOOK.md)

## Users / Downstream Consumers (AI_CONTEXT.md, AI_CONTEXT_2.md)

| User | Need | How This Project Helps |
|---|---|---|
| Gabriel (you) | Automatic segmentation, methodology paper | Complete pipeline, reproducible notebooks |
| Charles | Geometric page extraction | High-confidence ink masks, uncertainty maps |
| Social science colleagues | Visualize 3D structure, understand material composition | Napari viewer, material statistics, colored exports |
| Future researchers | Build on this work | Modular code, comprehensive documentation |

## Inputs

### CT (Primary)
- **Raw input:** RAW TIFF STACK → 3D numpy array (D, H, W) via IO/volume_loader.py. (AI_CONTEXT.md, AI_CONTEXT_2.md)
- **Raw data is ONLY TIFF files. No scanner metadata exists.** All metadata (bit depth, shape, intensity range) is inferred from the numpy array itself. (AI_CONTEXT.md, AI_CONTEXT_2.md — CRITICAL CONSTRAINT)
- **Data directories:** `data/raw/` (raw TIFF slices), `data/processed/` (preprocessed .npz), `data/output/` (labels, probabilities, diagnostics, figures) — all git-ignored. (AI_CONTEXT.md, AI_CONTEXT_2.md)

### XRF (Secondary — verified 2026-08-09)
- **Elemental TIFFs:** Per-element raster images → 3D data cube (M, N, n_elements) via `xrf/io/xrf_loader.py`. Source: `data/xrf/raw/`.
- **BCF hypercube:** Bruker `.bcf` spectrum-image files → elemental TIFFs via dual-window Bremsstrahlung subtraction in `xrf/preprocessing/bcf_extractor.py`. Source: `data/xrf/bcf/`.
- **Data directories:** `data/xrf/raw/` (elemental TIFFs), `data/xrf/bcf/` (BCF files), `data/xrf/output/` (processed, figures) — all git-ignored.

## Outputs

### CT
- **Labels** (D, H, W) — MAP component assignment. (AI_CONTEXT.md, AI_CONTEXT_2.md)
- **Probabilities** (D, H, W, K) — full posterior distribution. (AI_CONTEXT.md, AI_CONTEXT_2.md)
- **Analysis:** per-class voxel counts, fractions, intensities (material_stats.py); entropy, confidence, margin maps (uncertainty_maps.py). (AI_CONTEXT.md, AI_CONTEXT_2.md)
- **Visualization:** interactive 3D rendering (napari), GMM component overlay plots, videos, colored stacks. (AI_CONTEXT.md, AI_CONTEXT_2.md)
- **Notebook outputs:** `preprocessed_volume.npz`, `gmm_labels.npz`, `gmm_probabilities.npz`, `hmrf_labels.npz` (optional), videos/plots/colored stacks. (AI_CONTEXT.md, AI_CONTEXT_2.md)

### XRF (verified 2026-08-09)
- **Per-page leaf signatures** `F_h` — abundance vector + spatial descriptors per page (leaf_signature.py).
- **Category-level signatures** — aggregated compositional norms by structural page type (text_only, chapter_start, illustration, mixed, unknown).
- **Rarity-flagged pages** — robust z-score deviations from category median, as triage heuristic for human review.
- **Per-cluster masks** — Fiji-compatible TIFFs for each GMM class on each page.

## Integration With External Work — Charles' Geometric Approach

Charles' work focuses on extracting page geometry using normal vectors and parametric surface fitting. The probabilistic output from this segmentation enables: (AI_CONTEXT.md, AI_CONTEXT_2.md)
- **INK-FIRST PAGE INFERENCE:** Use high-confidence ink voxels (P(ink) > 0.7) to compute normal vectors, rather than all bright voxels.
- **UNCERTAINTY-AWARE FITTING:** Skip ambiguous voxels in surface fitting; weight by confidence.
- **MATERIAL-AWARE ANALYSIS:** Distinguish text strokes from noise or cover artifacts.

## Multi-Modal XRF + CT Integration (verified 2026-08-09)

XRF provides complementary elemental composition data at page-level resolution, orthogonal to CT's volumetric density classification. The XRF pipeline (`src/xrf/`) generates per-page leaf signatures and category-level compositional norms that can be cross-referenced against CT material labels.

- **Current state:** Both CT and XRF pipelines are independently operational on real data (`Brevar Capucin` CT stack, `Letter_1` XRF elemental TIFFs).
- **Gap:** `src/xrf/fusion/ct_xrf_fusion.py` exists as an empty placeholder (0 bytes). Multi-modal fusion — e.g., using XRF element maps to validate or refine CT material assignments — is not yet implemented.
- **Planned approach:** Elemental abundance vectors from XRF can serve as soft priors or validation targets for CT GMM components at page boundaries where both modalities overlap.

**Proposed integration pipeline** (AI_CONTEXT.md, AI_CONTEXT_2.md):
```
GMM Output: P(ink) probability map
  → Threshold at P > 0.7 → binary ink mask
  → Charles' normal vector computation (on confident ink voxels only)
  → Cluster normals → page-oriented groups
  → Fit B-spline surfaces → flattened pages
  → Project ink back onto surfaces → readable text
```

**Time Estimate (LABORATORY_NOTEBOOK.md):** 6–8 weeks for basic page surface extraction; 12+ weeks for full virtual flattening with texture mapping.

## Long-Term Vision (LABORATORY_NOTEBOOK.md)

- Fully automatic pipeline: Raw TIFF → segmented volume → flattened pages → readable text.
- Multi-modal integration: CT + XRF + photography for robust material identification.
- Deep learning augmentation: Self-supervised networks trained on synthetic data for ink detection.
- Publication: Journal paper on unsupervised segmentation methodology for cultural heritage CT.
