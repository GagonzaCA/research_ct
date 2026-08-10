# projectbrief.md

> Merged from: AI_CONTEXT.md (2026-07-10), AI_CONTEXT_2.md (2026-07-28), LABORATORY_NOTEBOOK.md
> Project: research_ct — Unsupervised Material Segmentation for Micro-CT of Sealed Historical Books
> Author: Gabriel Augusto Gonzalez Lozano — University of Western Ontario
> Date Started: July 2026 — Project Duration: 9 Weeks (LABORATORY_NOTEBOOK.md)
> NOTE: All claims below are treated as proposals/intentions, not confirmed implementation.

## Scope

This project implements an unsupervised, automatic pipeline to segment micro-CT volumes of sealed historical books into material classes (air, paper, ink, cover, adhesive) using statistical modeling of X-ray attenuation intensity distributions. No ground truth labels exist. No manual threshold tuning is required. The system discovers material classes directly from the data. (AI_CONTEXT.md, AI_CONTEXT_2.md)

## Primary Goal

Develop an **unsupervised, automatic algorithm** that segments micro-CT volumes of sealed books into material classes (air, paper, ink, cover, adhesive) using statistical modeling of intensity distributions, without manual threshold tuning or labeled training data. (LABORATORY_NOTEBOOK.md)

Automatically segment micro-CT volumes into material classes without manual threshold tuning or labeled training data. (AI_CONTEXT.md, AI_CONTEXT_2.md)

## Core Requirements / Specific Objectives (LABORATORY_NOTEBOOK.md)

- **O1** — Implement GMM with automatic K selection via BIC. Success: BIC curve shows clear minimum; components map to physical materials.
- **O2** — Implement hierarchical component splitting. Success: Tree structure reflects material taxonomy (air → solid → paper/ink/cover).
- **O3** — Implement HMRF spatial regularization. Success: Reduced salt-and-pepper noise; preserved fine structures.
- **O4** — Generate probabilistic output. Success: Each voxel has class probabilities, not just hard labels.
- **O5** — Create diagnostic and visualization tools. Success: Histograms, edge profiles, 3D napari viewer, uncertainty maps.
- **O6** — Validate on real micro-CT data. Success: Segmentation is stable, physically plausible, and enables downstream analysis.

## Stretch Goals (LABORATORY_NOTEBOOK.md)

- **S1** — Integrate with Charles' geometric page extraction (use ink probability maps as input to normal vector estimation). Feasibility: High — synergistic.
- **S2** — Dirichlet Process GMM (automatically determine K without BIC search). Feasibility: Medium — computational cost.
- **S3** — Multi-scale analysis (process at multiple resolutions for speed/accuracy trade-off). Feasibility: Medium.
- **S4** — Synthetic data generation (create ground-truth volumes for quantitative validation). Feasibility: Low — time dependent.

## Constraints

| Constraint | Implication | Source |
|---|---|---|
| No ground truth | Unsupervised methods only; validation is qualitative/expert-based | AI_CONTEXT.md, AI_CONTEXT_2.md |
| Raw TIFF only | No scanner metadata; all parameters inferred from data | AI_CONTEXT.md, AI_CONTEXT_2.md |
| 9-week timeline | HMRF and hierarchy are stretch goals; flat GMM + BIC is minimum viable | AI_CONTEXT.md, AI_CONTEXT_2.md |
| Large volumes | Memory-efficient chunking required; subset sampling for model fitting | AI_CONTEXT.md, AI_CONTEXT_2.md |
| Multi-user | Code must be readable, documented, and reproducible | AI_CONTEXT.md, AI_CONTEXT_2.md |

> Additional constraint present only in AI_CONTEXT_2.md — see Conflict C-MEM below:
> `32 GB RAM → float32 mandatory; subsample every 3rd slice (67 slices); chunked processing` (AI_CONTEXT_2.md)
> New option : ~560 GB RAM can be used in university computer lab - can not be used frequently, few hour a day. Better to get code written previously and tested in short subsamples and datasets (for debugging purpose)

## Success Criteria (AI_CONTEXT.md, AI_CONTEXT_2.md — identical in both)

| Criterion | Measurement |
|---|---|
| Automatic K selection | BIC curve shows clear minimum; selected K matches expected materials |
| Physical plausibility | Ink forms thin lines, not random speckles; paper forms sheets |
| Stability | Small perturbations to initialization produce similar segmentations |
| Uncertainty quantification | Ambiguous regions correctly identified (high entropy at material boundaries) |
| Computational feasibility | Full volume processes in < 2 hours on available hardware |
| Reproducibility | Same code + same data produces same results (random seed fixed) |

## Non-Goals (explicit)

- **No supervised learning / no labeled training data** — ruled out by cultural-heritage reality (LABORATORY_NOTEBOOK.md A5; AI_CONTEXT constraints).
- **No manual threshold tuning** — the system must discover classes directly from data (AI_CONTEXT.md, AI_CONTEXT_2.md).
- **HMRF is optional / stretch** — "Adds significant runtime; only used if GMM output is too noisy" (LABORATORY_NOTEBOOK.md). "HMRF and hierarchy are stretch goals; flat GMM + BIC is minimum viable" (AI_CONTEXT.md, AI_CONTEXT_2.md).
- **Full virtual unwrapping is NOT in scope** — the geometric extension is "not a full virtual unwrapping (that requires meshing, texture mapping, handling holes)" but a proof-of-concept for ink-driven page geometry (LABORATORY_NOTEBOOK.md).

## Realistic Deliverable for 9 Weeks (LABORATORY_NOTEBOOK.md — Critical Path)

The project succeeds if and only if:
- **Week 3:** Flat GMM produces physically meaningful components on real data.
- **Week 5:** HMRF (or decision not to use it) is justified with visual evidence.
- **Week 7:** 3D visualization enables intuitive inspection by non-technical colleagues.

---

## Proposed Changes (for developer review — 2026-08-09)

These are suggested updates based on codebase audit. Do not merge without developer approval.

### Stretch Goal Status Updates
- **S4 (XRF fusion):** `src/xrf/` pipeline is fully implemented and executed on real data (`Letter_1`). However, the CT-XRF fusion bridge (`src/xrf/fusion/ct_xrf_fusion.py`) remains an empty placeholder (0 bytes). Suggest updating this stretch goal to "Partially implemented — separate XRF pipeline operational; fusion not wired."
- **S2 (DP-GMM):** Already implemented as `sparse_bayesian_gmm.py`. Stretch goal table can reflect this.

### Scope Extension Consideration
- The `xrf/` package represents a significant scope expansion beyond the original CT-focused project. Consider whether XRF should become a second "Primary Goal" bullet (multi-modal material identification) or remain a stretch-goal extension.
- Dragonfly export utilities (`dragonfly_exporter.py`, `dragonfly_utils.py`) add a deployment/visualization path not originally scoped. Worth listing as a deliverable if it is being used for collaboration with non-technical colleagues.
