# Plan: Resolve All 8 Remaining Memory-Bank Conflicts

**Date:** 2026-07-29
**Goal:** Resolve C-DTYPE, C-MITIG, C-DPGMM, C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM. Clear `Conflicts to Resolve` sections entirely (all 11 now resolved). Annotate decisions in body text.

---

## Decisions (User-Confirmed)

| ID | File | Decision |
|----|------|----------|
| C-DTYPE | systemPatterns | **Option A** — float64 everywhere (code-verified: pipeline_revised.py line 78) |
| C-MITIG | systemPatterns | **Option B** — background correction + mild Gaussian smoothing (matches active pipeline_revised.py) |
| C-DPGMM | systemPatterns | **Will be implemented.** dp_gmm.py to be created; Dp_Gmm_Fitter to be used in notebook segmentation pipeline. |
| C-COV | techContext | **Option A** — covariance_type default `"full"` (code-verified: gmm_fitter.py line 21) |
| C-MEM | techContext | **Keep flexible (Option A).** Add annotation: local machine = 32 GB RAM; external/cluster resources available up to ~564 GB RAM. No hardcoded limits. |
| C-VOXELS | techContext | **~750M voxels** (201 slices) for current raw data. Other scanned books may be larger. Use as reference scale. |
| C-ROOTDOC | techContext | **Option B** — LABORATORY_NOTEBOOK.md not in repo root (code-verified: absent from root directory listing). |
| C-DIFFPARAM | techContext | **Option B dominant** for GMM pipeline; Option A parameters (Diffusion_*) are visualization-only. Both sets documented. |

---

## Edit 1 — systemPatterns.md

### 1a. Segmentation package description (line 26)

Replace:
```
- **segmentation/** — gmm_fitter.py (Gmm_Fitter), hierarchy.py (Hierarchical_Gmm), hmrf.py (Hmrf_Segmenter), decision_engine.py (Segmentation_Engine); dp_gmm.py (Dp_Gmm_Fitter) in AI_CONTEXT_2.md only.
```
With:
```
- **segmentation/** — gmm_fitter.py (Gmm_Fitter), hierarchy.py (Hierarchical_Gmm), hmrf.py (Hmrf_Segmenter), decision_engine.py (Segmentation_Engine). **dp_gmm.py (Dp_Gmm_Fitter) planned — to be implemented and used in notebook segmentation pipeline.**
```

### 1b. DP-GMM section (lines 91-95) — add implementation note

After line 95 (`more elegant but sensitive to alpha).`), append:
```
> **Decision (2026-07-29):** dp_gmm.py will be implemented. Dp_Gmm_Fitter share the same public interface as Gmm_Fitter for injection into decision_engine.py. To be used in notebook segmentation.
```

### 1c. Complicating Factors table (lines 72-79) — resolve C-MITIG

Replace:
```
**Complicating Factors — mitigation column differs, see CONFLICT C-MITIG:**
| Factor | Effect |
|---|---|
| Beam hardening | Lower-energy photons attenuated more; cupping artifact |
| Partial volume effects | Boundary voxels have mixed intensities → HMRF spatial regularization |
| Poisson noise | Variance proportional to mean |
| Ring artifacts | Circular intensity variations → Preprocessing filtering |
| Material degradation | Changed attenuation properties → Hierarchical splitting adapts |
```
With:
```
**Complicating Factors — resolved (C-MITIG):**
| Factor | Effect | Mitigation |
|---|---|---|
| Beam hardening | Lower-energy photons attenuated more; cupping artifact | Global background correction (large Gaussian subtraction) |
| Partial volume effects | Boundary voxels have mixed intensities | HMRF spatial regularization |
| Poisson noise | Variance proportional to mean | Mild Gaussian smoothing (sigma=0.8) |
| Ring artifacts | Circular intensity variations | Preprocessing filtering |
| Material degradation | Changed attenuation properties | Hierarchical splitting adapts |
```

### 1d. Data Structures table (lines 126-131) — resolve C-DTYPE

Replace:
```
## Data Structures — SEE CONFLICT C-DTYPE for dtypes
| Structure | Type | Shape | Purpose |
|---|---|---|---|
| Raw volume | np.ndarray | (D, H, W) [dtype conflict] | Input: reconstructed CT intensities |
| Preprocessed volume | np.ndarray | (D, H, W) [dtype conflict] | After preprocessing |
| Flat intensities | np.ndarray | (N,1) or (N,) [dtype conflict] | Input to GMM; N = D*H*W (or subsampled) |
| Responsibilities | np.ndarray | (N, K) [dtype conflict] | E-step output; gamma_ik |
```
With:
```
## Data Structures — resolved (C-DTYPE: float64 throughout)
| Structure | Type | Shape | Purpose |
|---|---|---|---|
| Raw volume | np.ndarray float64 | (D, H, W) | Input: reconstructed CT intensities — cast to float64 at pipeline entry |
| Preprocessed volume | np.ndarray float64 | (D, H, W) | After preprocessing (pipeline_revised.py line 78) |
| Flat intensities | np.ndarray float64 | (N,1) or (N,) | Input to GMM; N = D*H*W (or subsampled) |
| Responsibilities | np.ndarray float64 | (N, K) | E-step output; gamma_ik (sklearn default) |
```

### 1e. Workflow diagram (line 14) — note DP-GMM status

Replace line 14:
```
├── dp_gmm.py: (optional) DP-GMM for automatic K   ← AI_CONTEXT_2.md only
```
With:
```
├── dp_gmm.py: DP-GMM for automatic K   ← planned for implementation
```

### 1f. Clear Conflicts section (lines 147-164)

Replace entire `## ⚠️ Conflicts to Resolve` block through end of file:
```
## ⚠️ Conflicts to Resolve

> Resolved: C-PIPE, C-NORM, C-PRESET. See resolved notes in body text above.

Conflict: Data dtypes (C-DTYPE)
Option A (source: AI_CONTEXT.md): Raw volume (D,H,W) float64; Preprocessed volume (D,H,W) float64; Flat intensities (N,1)/(N,) float64; Responsibilities (N,K) float64.
Option B (source: AI_CONTEXT_2.md): Raw volume (D,H,W) uint16; Preprocessed volume (D,H,W) float32; Flat intensities (N,1)/(N,) float32; Responsibilities (N,K) float32.
My note: <leave blank for me to decide>

Conflict: Complicating-factor mitigations (C-MITIG)
Option A (source: AI_CONTEXT.md): Beam hardening → "Preprocessing normalization"; Poisson noise → "Anisotropic diffusion smoothing".
Option B (source: AI_CONTEXT_2.md): Beam hardening → "Global background correction (large Gaussian subtraction)"; Poisson noise → "Mild Gaussian smoothing".
My note: <leave blank for me to decide>

Conflict: DP-GMM existence in segmentation package (C-DPGMM)
Option A (source: AI_CONTEXT.md): No dp_gmm.py; segmentation exports Gmm_Fitter, Segmentation_Engine only. (Lab notebook lists DP-GMM only as stretch goal S2 / future direction.)
Option B (source: AI_CONTEXT_2.md): dp_gmm.py present — Dp_Gmm_Fitter class; exports Gmm_Fitter, Dp_Gmm_Fitter, Segmentation_Engine.
My note: <leave blank for me to decide>
```
With:
```
## Resolved Conflicts (all 6 from this file — 2026-07-29)

- **C-PIPE:** pipeline_revised.py (Option C) for GMM; pipeline.py (Option A/B) for visualization.
- **C-NORM:** normalization.py deleted; global_normalization.py is sole normalization module.
- **C-PRESET:** config.py kept; Real_Ct is legacy/visualization-only (thresholding included, not for GMM).
- **C-DTYPE:** float64 throughout (Option A). pipeline_revised.py casts to float64 at entry.
- **C-MITIG:** Background correction for beam hardening + mild Gaussian smoothing for Poisson noise (Option B). Matches active pipeline_revised.py.
- **C-DPGMM:** dp_gmm.py planned for implementation. Dp_Gmm_Fitter to be used in notebook segmentation pipeline.
```

---

## Edit 2 — techContext.md

### 2a. Root config table (line 44) — resolve C-ROOTDOC

Replace:
```
> Root-doc conflict — see Conflict C-ROOTDOC below.
```
With:
```
> **Resolved (C-ROOTDOC):** LABORATORY_NOTEBOOK.md is NOT in the repo root directory. Root contains only README.md, pyproject.toml, requirements.txt, .gitignore, LICENSE.
```

### 2b. Memory efficiency (line 50) — resolve C-MEM

Replace:
```
- **Memory efficiency** — SEE CONFLICT C-MEM.
```
With:
```
- **Memory efficiency — resolved (C-MEM):** Flexible approach. Local machine has 32 GB RAM; external/cluster resources available up to ~564 GB RAM. No hardcoded limits. Use float64 by default; subsample/chunk as needed. Key strategies: subset (Volume[:100,:,:]), chunking (implemented in 03_fit_gmm.ipynb), downsample (Volume[::4,::4,::4]).
```

### 2c. Coding structure — memory ref (line 68) — resolve C-MEM

Replace:
```
- **Memory Efficiency:** Process large volumes in chunks; avoid unnecessary copies; sample subsets for model fitting when full data too large. (dtype rule — see C-MEM)
```
With:
```
- **Memory Efficiency:** Process large volumes in chunks; avoid unnecessary copies; sample subsets for model fitting when full data too large. Local RAM: 32 GB; external resources up to ~564 GB. Default dtype: float64.
```

### 2d. Entry points — C-PIPE ref (line 104)

Replace:
```
| Run full preprocessing | pipeline.py / pipeline_revised.py [see C-PIPE] | Preprocess_For_Gmm() / Preprocess_For_Gmm_Revised() |
```
With:
```
| Run full preprocessing | pipeline_revised.py (GMM) / pipeline.py (visualization) | Preprocess_For_Gmm_Revised() / Preprocess_For_Gmm() |
```

### 2e. Entry point — DP-GMM line (line 106) — update status

Replace:
```
| Fit DP-GMM (AI_CONTEXT_2.md only) | research_ct/segmentation/dp_gmm.py | Dp_Gmm_Fitter.Fit() |
```
With:
```
| Fit DP-GMM (planned) | research_ct/segmentation/dp_gmm.py | Dp_Gmm_Fitter.Fit() |
```

### 2f. Parameter cheat sheet header (line 112) — resolve C-COV, C-DIFFPARAM

Replace:
```
## Parameter Cheat Sheet — merged (defaults differ; see C-COV and C-DIFFPARAM)
```
With:
```
## Parameter Cheat Sheet — resolved (C-COV, C-DIFFPARAM)
```

### 2g. Covariance row (line 117) — resolve C-COV

Replace:
```
| Covariance_Type | "full" / "tied" [see C-COV] | full/tied/diag/spherical | Complexity of Gaussian shapes | AI_CONTEXT.md / AI_CONTEXT_2.md |
```
With:
```
| Covariance_Type | "full" | full/tied/diag/spherical | Complexity of Gaussian shapes (default = full, code-verified) | both |
```

### 2h. Clear Conflicts section (lines 153-178)

Replace entire `## ⚠️ Conflicts to Resolve` block through end of file:
```
## ⚠️ Conflicts to Resolve

Conflict: Covariance_Type default (C-COV)
Option A (source: AI_CONTEXT.md): Covariance_Type default "full".
Option B (source: AI_CONTEXT_2.md): Covariance_Type default "tied".
My note: <leave blank for me to decide>

Conflict: Memory constraint & memory-error solutions (C-MEM)
Option A (source: AI_CONTEXT.md): §3.5 "Use np.float32 or np.float64 consistently." Memory Errors §6.2 — Solution 1: Subset = Volume[:100, :, :]; Solution 2: Use chunking (already implemented in 03_fit_gmm.ipynb); Solution 3: Downsample for initial exploration: Small = Volume[::4, ::4, ::4]. No stated RAM limit.
Option B (source: AI_CONTEXT_2.md): §3.5 "Use np.float32 or np.float64 consistently. For this project: float32 is mandatory due to 32GB RAM constraint." Constraints add "32 GB RAM → float32 mandatory; subsample every 3rd slice (67 slices); chunked processing". Memory Errors §6.2 — Solution 1: Subset = Volume[:100, :, :]; Solution 2: Use float32 instead of float64 (mandatory for this project); Solution 3: Subsample every 3rd slice: Volume[::3]; Solution 4: Use chunking for HMRF (process sub-volumes sequentially).
My note: <leave blank for me to decide>

Conflict: HMRF scale note in "HMRF Too Slow" (C-VOXELS)
Option A (source: AI_CONTEXT.md): "ICM is O(N*K*T). For 1B voxels, this is hours."
Option B (source: AI_CONTEXT_2.md): "ICM is O(N*K*T). For 250M voxels, this is hours."
My note: <leave blank for me to decide>

Conflict: Root-directory documentation listing (C-ROOTDOC)
Option A (source: AI_CONTEXT.md): Root directory table includes "LABORATORY_NOTEBOOK.md — Complete theory, methodology, timeline, bibliography" alongside AI_CONTEXT.md.
Option B (source: AI_CONTEXT_2.md): Root directory table lists AI_CONTEXT.md but OMITS LABORATORY_NOTEBOOK.md.
My note: <leave blank for me to decide>

Conflict: Diffusion vs Background/Noise/Clip parameters in cheat sheet (C-DIFFPARAM)
Option A (source: AI_CONTEXT.md): Parameter cheat sheet ends with Diffusion_Iterations (50), Diffusion_Kappa (75), Diffusion_Gamma (0.1, <=0.25).
Option B (source: AI_CONTEXT_2.md): Parameter cheat sheet instead includes DP_Max_Components, DP_Alpha, Background_Sigma (30.0), Noise_Sigma (0.8), Clip_Low_Percentile (0.1), Clip_High_Percentile (99.9); no Diffusion_* entries.
My note: <leave blank for me to decide>
```
With:
```
## Resolved Conflicts (all 5 from this file — 2026-07-29)

- **C-COV:** Covariance_Type default = `"full"` (Option A). Code-verified in gmm_fitter.py line 21.
- **C-MEM:** Flexible approach. Local machine = 32 GB RAM; external/cluster resources up to ~564 GB. No hardcoded limits. Default dtype: float64.
- **C-VOXELS:** Current raw data = ~750M voxels (201 slices × ~1900 × ~1900). Other scanned books may be larger. ICM complexity: O(N*K*T) — at scale this means hours.
- **C-ROOTDOC:** LABORATORY_NOTEBOOK.md is NOT present in the repo root directory. Root contains only README.md, pyproject.toml, requirements.txt, .gitignore, LICENSE.
- **C-DIFFPARAM:** Both parameter sets coexist. GMM pipeline uses Option B params (Background_Sigma, Noise_Sigma, Clip_Low/High_Percentile). Visualization pipeline uses Option A params (Diffusion_Iterations, Diffusion_Kappa, Diffusion_Gamma). Both preserved in cheat sheet.
```

---

## Edit 3 — activeContext.md

### 3a. Replace Conflicts section (lines 91-92)

Replace:
```
## ⚠️ Conflicts to Resolve
(Unresolved conflicts — see systemPatterns.md and techContext.md: C-DTYPE, C-MITIG, C-DPGMM, C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM. Resolved: C-PIPE, C-NORM, C-PRESET. No additional activeContext-only conflicts found.)
```
With:
```
## Resolved Conflicts (all 11 — 2026-07-29)

All conflicts from systemPatterns.md and techContext.md have been resolved against actual code:

**systemPatterns.md:** C-PIPE, C-NORM, C-PRESET, C-DTYPE, C-MITIG, C-DPGMM
**techContext.md:** C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM

See individual files for resolution details.
```

---

## Edit 4 — progress.md

### 4a. Replace conflict list (line 64)

Replace:
```
> These two snapshots disagree on multiple technical specifics; all disagreements are preserved verbatim as Conflicts in systemPatterns.md (C-DTYPE, C-MITIG, C-DPGMM) and techContext.md (C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM). **Resolved: C-PIPE, C-NORM, C-PRESET.** Do NOT assume either snapshot reflects the real implemented code.
```
With:
```
> All 11 conflicts resolved (2026-07-29). See systemPatterns.md and techContext.md for resolution details. Do NOT assume snapshot claims reflect implemented code — verify against actual repo.
```

---

## Edit 5 — README.md

### 5a. Warning banner (line 7)

Replace `They contain 8 unresolved conflicts (3 resolved: C-PIPE, C-NORM, C-PRESET).` with:
```
They contained 11 unresolved conflicts at merge time. **All 11 have been resolved (2026-07-29).**
```

### 5b. File index table — systemPatterns (line 19)

Replace `**3 conflicts (C-DTYPE, C-MITIG, C-DPGMM); C-PIPE, C-NORM, C-PRESET resolved**` with:
```
**All 6 conflicts resolved**
```

### 5c. File index table — techContext (line 20)

Replace `**5 conflicts (C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM)**` with:
```
**All 5 conflicts resolved**
```

### 5d. Conflict checklist (lines 122-143) — tick all, add resolution notes

Replace entire conflict checklist section:

Old (lines 122-143):
```
### 4a. Conflict resolution checklist (11 total — resolve against REAL code)
Tick when the source disagreement has been reconciled with your actual implementation and the `My note` field is filled in.

**systemPatterns.md**
- [x] **C-PIPE** — Preprocessing pipeline: CLAHE/Perona-Malik (AI_CONTEXT + Lab Notebook) vs revised Gaussian/global-norm (AI_CONTEXT_2, "PERMANENTLY DEPRECATED" note). ⭐ *resolved 2026-07-29* — Option C (pipeline_revised.py) active for GMM; Option A/B (pipeline.py) retained for visualization.
- [x] **C-NORM** — normalization.py vs global_normalization.py (function names differ) — *resolved 2026-07-29* — normalization.py deleted; global_normalization.py is sole module.
- [x] **C-PRESET** — Real_Ct "includes thresholding" vs "legacy, for visualization only" — *resolved 2026-07-29* — config.py kept; Real_Ct is legacy/visualization-only preset.
- [ ] **C-DTYPE** — float64 everywhere vs uint16 raw + float32 downstream
- [ ] **C-MITIG** — beam-hardening / Poisson-noise mitigation columns differ
- [ ] **C-DPGMM** — DP-GMM absent vs present (dp_gmm.py / Dp_Gmm_Fitter)

**techContext.md**
- [ ] **C-COV** — Covariance_Type default "full" vs "tied"
- [ ] **C-MEM** — no RAM limit vs 32 GB / float32 mandatory / every-3rd-slice (67 slices)
- [ ] **C-VOXELS** — "1B voxels" vs "250M voxels" in HMRF-too-slow note
- [ ] **C-ROOTDOC** — root dir lists LABORATORY_NOTEBOOK.md vs omits it
- [ ] **C-DIFFPARAM** — cheat sheet: Diffusion_* params vs DP/Background/Noise/Clip params
```

With:
```
### 4a. Conflict resolution — ALL RESOLVED (2026-07-29)

**systemPatterns.md (6/6 ✅)**
- [x] **C-PIPE** — pipeline_revised.py (C) for GMM; pipeline.py (A/B) for visualization
- [x] **C-NORM** — normalization.py deleted; global_normalization.py is sole module
- [x] **C-PRESET** — config.py kept; Real_Ct is legacy/visualization-only
- [x] **C-DTYPE** — float64 throughout (Option A). pipeline_revised.py casts to float64 at entry.
- [x] **C-MITIG** — Background correction + mild Gaussian smoothing (Option B)
- [x] **C-DPGMM** — dp_gmm.py planned for implementation; Dp_Gmm_Fitter for notebook segmentation

**techContext.md (5/5 ✅)**
- [x] **C-COV** — Covariance_Type default "full" (Option A). Code-verified: gmm_fitter.py line 21.
- [x] **C-MEM** — Flexible approach. Local 32 GB; external up to ~564 GB. Default float64.
- [x] **C-VOXELS** — ~750M voxels (201 slices). Other books may be larger.
- [x] **C-ROOTDOC** — LABORATORY_NOTEBOOK.md not in repo root (Option B).
- [x] **C-DIFFPARAM** — Both parameter sets coexist. Option B (GMM) + Option A (visualization).
```

### 5e. Work log — add final resolution entry

Replace work log rows:
```
| 2026-07-29 | Conflict resolution | Resolved C-PRESET: config.py kept; Real_Ct is legacy/visualization-only. Cleaned resolved blocks from conflict section. | systemPatterns.md, activeContext.md, progress.md, README.md | C-PRESET | Continue C-DTYPE |
| 2026-07-29 | Conflict resolution | Resolved C-NORM: deleted normalization.py; global_normalization.py is sole module | normalization.py, systemPatterns.md, activeContext.md, progress.md, README.md | C-NORM | Continue C-PRESET |
| 2026-07-29 | Conflict resolution | Resolved C-PIPE: pipeline_revised.py (Option C) for GMM, pipeline.py (Option A) for visualization | systemPatterns.md, activeContext.md, progress.md, README.md | C-PIPE | Continue C-NORM |
```
With:
```
| 2026-07-29 | Conflict resolution | Resolved all 8 remaining: C-DTYPE, C-MITIG, C-DPGMM, C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM. All 11 conflicts now resolved. | systemPatterns.md, techContext.md, activeContext.md, progress.md, README.md | all 11 done | Begin DP-GMM implementation |
| 2026-07-29 | Conflict resolution | Resolved C-PIPE, C-NORM, C-PRESET (first batch of 3) | systemPatterns.md, activeContext.md, progress.md, README.md | C-PIPE, C-NORM, C-PRESET | Continue remaining 8 |
| 2026-07-28 | Memory bank setup | Merged 3 sources → 6 files + README; laid out under .kilo/ | all | none yet | Wire into Kilo; start C-PIPE |
```

---

## Validation

- [ ] No `Conflicts to Resolve` section with unresolved blocks remains in any file
- [ ] All resolution decisions are annotated as body text in the relevant sections
- [ ] README.md checklist shows 100% ticked (6/6 + 5/5)
- [ ] README.md warning banner reflects 0 unresolved
- [ ] activeContext.md and progress.md reflect "all resolved"