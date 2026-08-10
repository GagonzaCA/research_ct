# Plan: Sync Memory Bank to Current Implementation (2026-08-09)

## Goal

Update all six memory-bank files so they accurately reflect the codebase as of 2026-08-09, including newly implemented packages, verified outputs, and empty placeholders.

## Audit Summary (codebase vs. memory bank)

### New Since Last Update (2026-07-31)

| Find | Status | Action |
|---|---|---|
| `src/xrf/` package (XRF pipeline) | **Fully implemented** — 11 modules, config, tests, generated outputs | Add to `systemPatterns.md`, `techContext.md`, `productContext.md`, `activeContext.md`, `progress.md` |
| `src/research_ct/io/dragonfly_exporter.py` | **Implemented** — ImageJ-compatible multi-page TIFF with voxel spacing | Add to `systemPatterns.md`, `techContext.md` |
| `src/research_ct/processing/dragonfly_utils.py` | **Implemented** — high-level Dragonfly export orchestration + colors CSV | Add to `systemPatterns.md`, `techContext.md` |
| Real CT data (`Brevar Capucin`, ~431 slices) | **Loaded, processed** — outputs in `data/output/` | Note in `activeContext.md`, `progress.md` |
| XRF elemental data (`Letter_1`: Pb, K, Hg, Fe, Cu, Ca, Au, As) | **Loaded, processed** — cluster masks + signatures in `data/xrf/output/` | Note in `activeContext.md`, `progress.md` |
| `src/xrf/fusion/ct_xrf_fusion.py` | **Empty (0 bytes)** — planned but not implemented | Note as empty placeholder in relevant files |
| `tests/test_xrf/` | **4 test modules** exist | Update `techContext.md` test count |

### Verified Unchanged (correct in memory bank)

- `research_ct` package structure, class names, public APIs.
- 5 notebooks (01–05) names and purposes.
- Resolved conflicts C-PIPE, C-NORM, C-PRESET, C-DTYPE, C-MITIG, C-DPGMM, C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM.
- Parameter defaults (Gmm_Min_K, Gmm_Max_K, Covariance_Type, etc.).

---

## File-by-File Update Instructions

### 1. `projectbrief.md`

**Scope:** Mostly unchanged. Add a bullet under Stretch Goals clarifying that XRF fusion is now partially implemented as a separate `xrf` package, but the CT→XRF fusion module (`ct_xrf_fusion.py`) is still empty.

**Edits:**
- In Stretch Goals table, update S4 row: change status from "Not started" to note that `xrf` package exists separately; CT-XRF fusion module is empty.

**Do NOT edit** `projectbrief.md` directly (per instructions: suggest changes instead). Instead, add a note block at the bottom:

```md
## Proposed Changes (for developer review)
- S4 (XRF fusion): update status to reflect that `src/xrf/` pipeline is implemented but `src/xrf/fusion/ct_xrf_fusion.py` remains empty (0 bytes). CT-XRF integration not yet wired.
```

### 2. `productContext.md`

**Scope:** Add XRF as a secondary input modality and downstream analysis path.

**Edits:**
1. **Inputs section:** Add a second bullet under "Raw input" for XRF:
   - `XRF elemental TIFFs` → 3D data cube (M, N, n_elements) via `xrf/io/xrf_loader.py`.
   - BCF hypercube extraction via `xrf/preprocessing/bcf_extractor.py`.
2. **Outputs section:** Add XRF outputs:
   - Per-page leaf signature vectors (`F_h`)
   - Category-level compositional signatures
   - Rarity-flagged page lists
3. **Integration section:** Add a paragraph about XRF→CT fusion intent:
   - `ct_xrf_fusion.py` is a placeholder (0 bytes) planned for multi-modal material identification.

### 3. `systemPatterns.md`

**Scope:** Add XRF package architecture and Dragonfly export to the module map.

**Edits:**
1. **High-Level Workflow:** Append an XRF branch after the CT pipeline:
   ```
   XRF BCF / elemental TIFFs
     → [IO: xrf_loader.py] → elemental data cube (M, N, n)
     → [PREPROCESSING: bcf_extractor.py] → dual-window Bremsstrahlung subtraction
     → [TRANSFORMS: coda.py] → CLR transformation
     → [SEGMENTATION: xrf_gmm.py] → PCA + GMM clustering
     → [SPATIAL: spatial_analyzer.py] → class map + connected-component descriptors
     → [SIGNATURES: leaf_signature.py] → leaf signature F_h
     → [COMPARISON: category_signatures.py, rarity_scoring.py] → category norms + rarity flags
   ```
2. **Package Architecture:** Add a second package block:
   ```
   src/xrf/
   ├── config.py           Bcf_Extraction_Config, Xrf_Preprocessing_Config, etc.
   ├── io/                 xrf_loader.py
   ├── preprocessing/      bcf_extractor.py
   ├── segmentation/       xrf_gmm.py
   ├── transforms/         coda.py (CLR)
   ├── spatial/            spatial_analyzer.py
   ├── signatures/         leaf_signature.py
   ├── comparison/         category_registry.py, category_signatures.py, rarity_scoring.py, spatial_comparison.py
   └── fusion/             ct_xrf_fusion.py (EMPTY — placeholder)
   ```
3. **research_ct additions:** Under `io/`, add `dragonfly_exporter.py`. Under a new `processing/` subpackage (or under `io/`), add `dragonfly_utils.py`.
4. **Data Structures:** No changes needed for CT structures. For XRF, add:
   - `Elemental cube` | np.ndarray float64 | (M, N, n_elements) | Raw XRF intensities per element
   - `CLR data` | np.ndarray float64 | (N_valid, n_elements) | Log-ratio transformed proportions
   - `Leaf signature F_h` | np.ndarray float64 | (n_classes + spatial_dims,) | Per-page descriptive vector

### 4. `techContext.md`

**Scope:** Add XRF dependencies, new modules, tests, and entry points.

**Edits:**
1. **Core Stack:** Note that `hyperspy>=2.0.0` and `exspy` in `pyproject.toml` are for XRF BCF extraction.
2. **Root Configuration Files:** Unchanged.
3. **Parameter Cheat Sheet:** Add XRF parameters:
   | Parameter | Default | Range | Effect | Source |
   |---|---|---|---|---|
   | Xrf_Noise_Threshold | 5.0 | 0–50 | Min intensity for valid pixel | xrf/config.py |
   | Xrf_Zero_Replacement_Delta | 1e-4 | 1e-6–1e-2 | Zero replacement before CLR | xrf/config.py |
   | Xrf_Pca_Variance_Ratio | 0.95 | (0,1] | PCA retained variance | xrf/config.py |
   | Bcf_Cutoff_At_Kv | 40.0 | 10–80 | Detector energy ceiling (keV) | xrf/config.py |
   | Bcf_Peak_Width_Kev | 0.20 | 0.05–1.0 | Emission line integration half-width | xrf/config.py |
   | Bcf_Bg_Width_Kev | 0.10 | 0.05–0.5 | Background sideband half-width | xrf/config.py |
   | Bcf_Bg_Offset_Kev | 0.25 | 0.1–1.0 | Sideband offset from line center | xrf/config.py |
4. **File-to-Theory Mapping:** Add:
   - `xrf_loader.py` → Multispectral image I/O, threshold masking
   - `bcf_extractor.py` → X-ray emission line physics, dual-window background subtraction
   - `coda.py` → Compositional data analysis, Centered Log-Ratio (CLR), Aitchison geometry
   - `xrf_gmm.py` → PCA dimensionality reduction, GMM clustering in latent space
   - `spatial_analyzer.py` → Connected-component analysis, morphological descriptors
   - `leaf_signature.py` → Abundance vectors, weighted averaging
   - `category_signatures.py`, `rarity_scoring.py` → Robust statistics (median, MAD), z-scoring
5. **Test Suite:** Update count: `tests/test_xrf/` has 4 modules (conftest + 4 test files). Total tests now include both CT and XRF suites.
6. **Entry Points:** Add XRF table:
   | Task | File to Open | Key Class/Function |
   |---|---|---|
   | Load elemental TIFFs | src/xrf/io/xrf_loader.py | Xrf_Loader.Load_Element_Stack() |
   | Extract BCF elements | src/xrf/preprocessing/bcf_extractor.py | Bcf_Element_Extractor |
   | CLR transform | src/xrf/transforms/coda.py | Clr_Transformer.Apply_Clr_Transform() |
   | Segment XRF | src/xrf/segmentation/xrf_gmm.py | Xrf_Gmm_Segmenter.Fit_Predict() |
   | Spatial descriptors | src/xrf/spatial/spatial_analyzer.py | Spatial_Analyzer.Extract_Spatial_Descriptors() |
   | Build leaf signature | src/xrf/signatures/leaf_signature.py | Leaf_Signature_Extractor.Compute_Abundances() |
   | Category comparison | src/xrf/comparison/category_signatures.py | Category_Signature_Aggregator.Aggregate_By_Category() |
   | Rarity scoring | src/xrf/comparison/rarity_scoring.py | Rarity_Scorer.Flag_Rare_Pages() |
   | Dragonfly export | src/research_ct/processing/dragonfly_utils.py | Export_For_Dragonfly() |

### 5. `activeContext.md`

**Scope:** Update current focus to reflect that both CT and XRF pipelines are operational; CT-XRF fusion is the remaining gap.

**Edits:**
1. **Current Focus:** Add:
   - CT pipeline (research_ct) has been executed on real `Brevar Capucin` data (~431 slices). Outputs: GMM labels/probabilities, HMRF labels, uncertainty maps, material stats CSVs, diagnostic figures.
   - XRF pipeline (xrf) has been executed on `Letter_1` elemental data. Outputs: 7-class cluster masks, per-page leaf signatures, spatial descriptors, category comparison framework.
2. **Recent Changes:** Add 2026-08-09 block:
   - `xrf/` package added: full Bruker BCF → elemental TIFF → CLR → PCA+GMM → spatial analysis → leaf signature → category comparison pipeline.
   - `dragonfly_exporter.py` and `dragonfly_utils.py` added for ImageJ-calibrated TIFF export.
   - `ct_xrf_fusion.py` created as empty placeholder (fusion not yet implemented).
   - Real CT and XRF data loaded; both pipelines executed end-to-end.
3. **Immediate Next Steps:** Update:
   1. Implement `ct_xrf_fusion.py` (CT + XRF voxel-level or page-level fusion).
   2. Validate XRF page signatures against CT material labels where both modalities overlap.
   3. Tune XRF GMM `Num_Components` vs. BIC.
   4. Continue HMRF beta tuning if GMM noise is still visible on full volume.
4. **Short-Term Extensions table:** Update XRF row to "Implemented" and move `ct_xrf_fusion.py` into a new row:
   | CT-XRF Fusion | Medium | Multi-modal material identification | Not started (placeholder file exists) |

### 6. `progress.md`

**Scope:** Append a new dated entry for 2026-08-09 documenting the dual-pipeline milestone.

**Edits:**
1. Append new section:

```md
## 2026-08-09 — Dual-Modal Pipeline Milestone

**Goal:** Execute both CT and XRF pipelines on real data; identify remaining gaps.

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
- Leaf signature `F_h` and book-level weighted signature computed.
- Category signatures, rarity scoring, and spatial comparison modules ready for page-category tagging.

**Gaps identified:**
- `src/xrf/fusion/ct_xrf_fusion.py` is empty — CT+XRF fusion not implemented.
- README.md still points to old `src/` paths (missing `research_ct/` prefix).
- No notebook yet for XRF pipeline walkthrough.
```

2. **Overall Status Assessment:** Update conclusion to:
   - "Both CT and XRF pipelines are individually operational on real data. The critical next inflection point is multi-modal fusion (`ct_xrf_fusion.py`) and cross-validation between CT material labels and XRF compositional classes."

3. **Uncategorized:** Add XRF glossary terms if needed:
   - CLR, CoDa, BCF, XRF, Leaf Signature, Rarity Score.

---

## Risks & Caveats

1. **Conflict C-XRF:** The `xrf` package was not part of the original 9-week scope. Treat its presence as an **extension** rather than a requirement for CT success.
2. **README drift:** `README.md` paths (`src/preprocessing/` instead of `src/research_ct/preprocessing/`) are out of sync. Flag for a separate README cleanup task.
3. **Empty placeholder `ct_xrf_fusion.py`:** Must be explicitly documented as 0 bytes so future agents do not assume it is functional.
4. **Do not modify `projectbrief.md` directly** — append proposed-change notes only.

## Validation Plan

After an implementation agent executes these updates:

1. Run `cat .kilo/rules/memory-bank/*.md | grep -i "xrf\|dragonfly" | wc -l` — should return > 20 matches (currently 0).
2. Verify every new module listed is importable:
   ```python
   from xrf.io.xrf_loader import Xrf_Loader
   from xrf.transforms.coda import Clr_Transformer
   from xrf.segmentation.xrf_gmm import Xrf_Gmm_Segmenter
   from xrf.spatial.spatial_analyzer import Spatial_Analyzer
   from xrf.signatures.leaf_signature import Leaf_Signature_Extractor
   from xrf.comparison.category_registry import Category_Registry
   from xrf.comparison.category_signatures import Category_Signature_Aggregator
   from xrf.comparison.rarity_scoring import Rarity_Scorer
   from research_ct.processing.dragonfly_utils import Export_For_Dragonfly
   from research_ct.io.dragonfly_exporter import Save_Volume_As_Tiff
   ```
3. Confirm `src/xrf/fusion/ct_xrf_fusion.py` is still 0 bytes — if it gains content, memory bank must be re-audited.

## Open Questions (for user / next session)

- Should `productContext.md` list Charles’ geometric integration and the XRF pipeline as **parallel** downstream consumers, or should XRF fusion feed back into CT segmentation?
- Is the 9-week timeline still the binding constraint, or has the XRF work extended the scope?
- Does any XRF notebook exist outside of `notebooks/` (e.g., in `xrf/` or root) that should be catalogued?
