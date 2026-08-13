# Plan: Generate `report_content.tex`

## Status notes (read first)
- **`[Memory Bank: Active]`** — correction: `.kilo/rules/memory-bank/` *does* exist (my earlier glob call failed silently on this path; a direct directory read confirmed `projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`, `activeContext.md`, `progress.md`, `README.md`). All six files were read. The bank states all 11 of its original conflicts (C-PIPE, C-NORM, C-PRESET, C-DTYPE, C-MITIG, C-DPGMM, C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM) are already resolved against the actual code as of 2026-07-31/2026-08-09 — so no conflict needs to be surfaced to the user for this task. Content below is cross-checked against both the memory bank and direct reads of `src/` (the two agree closely). Per the bank's own rule, bank claims are still treated as source claims (some, like exact real-data filenames/counts and "already executed on real data" statements, were not independently re-verified by opening `data/`), and are labeled as such below where used.
- Access respected: only `src/research_ct/`, `src/xrf/`, `notebooks/**` (names only), `README.md`, and the two external reference `.tex` files were inspected. `tests/`, `docs/`, and `data/` were **not** opened.
- Figure decision (user-confirmed): existing PNGs live under `data/output/` and `data/xrf/output/`, which are off-limits. **Use Rule 3 (`[NEW PLOT NEEDED]`) placeholders for every figure** — do not `\includegraphics` anything from `data/`.
- Output location: write the file to `C:\Users\gabri\Documento\Mitacs\report_content.tex` (the `Mitacs/` folder, **one level above** the `research_ct` package root — not inside it).
- No preamble: do not include `\documentclass`, `\usepackage`, or `\begin{document}`/`\end{document}`. Start directly at the first `\section`.
- Do not flatten "Level 0/1/2" headers from the reference proposal/report — use plain descriptive `\subsection` titles instead (e.g. "Nonparametric Component Discovery", not "Level 0").

## Task
Implementation agent should:
1. Open `C:\Users\gabri\Documento\Mitacs\` and confirm it exists (it is the parent of the `research_ct` workspace).
2. Create the file `C:\Users\gabri\Documento\Mitacs\report_content.tex`.
3. Write the **exact LaTeX body** in the "Final Content" section below into that file, verbatim (it is already complete, section-tagged, figure/TikZ-spec annotated, and ready to `\input{}`/`\include{}` into the user's existing template).
4. Do not run any Python, do not open `data/`, `tests/`, or `docs/`, do not add a preamble.
5. Stop after writing the file — no further iteration unless the user asks.

## Source-to-content mapping (for traceability, not to be included in the .tex)
| Report content | Source file |
|---|---|
| GMM + BIC selection | `src/research_ct/segmentation/gmm_fitter.py` |
| Sparse/overcomplete Bayesian GMM (DP-style pruning) | `src/research_ct/segmentation/sparse_bayesian_gmm.py` |
| Hierarchical soft splitting, LRT | `src/research_ct/segmentation/hierarchy.py` |
| HMRF / Potts / ICM | `src/research_ct/segmentation/hmrf.py` |
| Orchestration engine | `src/research_ct/segmentation/decision_engine.py` |
| Background correction (beam hardening) | `src/research_ct/preprocessing/background_correction.py` |
| Global percentile normalization, per-slice z-score, stationarity check | `src/research_ct/preprocessing/global_normalization.py` |
| Histogram / GMM-readiness diagnostics | `src/research_ct/preprocessing/histogram_diagnostics.py` |
| Full preprocessing pipeline order | `src/research_ct/preprocessing/pipeline_revised.py` |
| Material statistics (volume fraction, per-class mean/std) | `src/research_ct/analysis/material_stats.py` |
| Uncertainty (Shannon entropy, margin) | `src/research_ct/analysis/uncertainty_maps.py` |
| Page surface / connected components | `src/research_ct/analysis/page_extractor.py` |
| CLR transform (CoDa) | `src/xrf/transforms/coda.py` |
| PCA + GMM clustering on XRF, BIC curve | `src/xrf/segmentation/xrf_gmm.py` |
| Spatial connected-component descriptors (XRF) | `src/xrf/spatial/spatial_analyzer.py` |
| Per-page leaf signature | `src/xrf/signatures/leaf_signature.py` |
| Category signature aggregation, MAD spread | `src/xrf/comparison/category_signatures.py` |
| Rarity scoring (robust z-score triage) | `src/xrf/comparison/rarity_scoring.py` |
| CT–XRF fusion | `src/xrf/fusion/ct_xrf_fusion.py` (**empty placeholder — 0 lines**, note as future work) |
| Package/module layout, notebook table | `README.md` |
| Diagrams/table style inspiration (not copied verbatim, no "Level" headers used) | attached `Report.tex`, `Proposal_Gabriel_Augusto_Gonzalez_Lozano.tex` |
| Project scope, users, real-data names, timeline/risk context (source claims, labeled as such) | `.kilo/rules/memory-bank/{projectbrief,productContext,activeContext,progress}.md` |

## Memory-bank additions folded into the content below (source claims)
- Real datasets referenced in the bank: CT pipeline run on a **"Brevar Capucin"** micro-CT stack (~431 TIFF slices); XRF pipeline run on **"Letter\_1"** elemental TIFFs across 8 elements (Pb, K, Hg, Fe, Cu, Ca, Au, As), producing a 7-cluster GMM segmentation. These are `activeContext.md`/`progress.md` claims about prior runs, not independently re-verified by opening `data/` for this task — the Results section below states them as reported prior outputs, not confirmed-fresh findings.
- Downstream users identified in `productContext.md`: the author (methodology/reproducible pipeline), a collaborator ("Charles") doing geometric page-surface extraction from ink probability maps, non-technical social-science colleagues needing 3D/visual outputs, and future researchers extending the modular codebase.
- `projectbrief.md` primary objectives (O1–O6) and constraints (no ground truth, raw-TIFF-only input, memory limits) map directly onto the Introduction/Methodology framing already drafted from code.
- `activeContext.md` immediate next steps / known risks (CT–XRF fusion not implemented, ink-in-CT visibility risk, HMRF performance at scale, non-stationary intensity drift) map onto the Conclusion's "remaining open work" paragraph — expanded below to also cite these named risks.

## Final Content (write verbatim to `Mitacs/report_content.tex`)

```latex
% ==============================================================================
% report_content.tex
% Sections only — no preamble. Intended for \input{} into an existing template.
% ==============================================================================

\section{Introduction}

Micro-CT scanning of sealed historical books produces volumetric data in which
material composition (air, paper, ink, cover, adhesive) must be inferred purely
from voxel intensity and local geometry, since the books cannot be physically
opened. Existing approaches in this line of work rely on fixed-$k$ clustering
(K-Means, fuzzy C-means) or manual intensity thresholds. Both require per-scan
parameter tuning, assume the number of materials is already known, and produce
hard labels with no notion of confidence.

This project addresses three coupled problems: (1) the number of material
classes $K$ and their intensity statistics are unknown a priori and must be
estimated from the data itself; (2) no ground-truth labels exist, so supervised
learning is not applicable; (3) material boundaries are spatially structured
(e.g. ink strokes are thin and contiguous), so a purely intensity-based
decision is locally ambiguous and must be resolved using neighborhood context.
A complementary X-Ray Fluorescence (XRF) elemental-mapping pipeline is also
developed to cross-validate material identity using elemental composition
rather than absorption contrast alone, since carbon-based inks are often
poorly distinguishable from paper under absorption CT.

The codebase (`research_ct` for CT volumes, `xrf` for elemental maps) implements
an unsupervised, statistics-first pipeline: Gaussian Mixture Models (GMM) with
automatic model-order selection, hierarchical refinement of ambiguous
components, spatial regularization via a Hidden Markov Random Field (HMRF),
and downstream uncertainty and material-statistics reporting. The XRF branch
performs compositional-data-correct elemental clustering, per-page signature
extraction, and rarity triage for expert review.

Four groups of stakeholders motivate the project's outputs: the author, who
needs a reproducible methodology; a collaborator pursuing geometric
page-surface extraction from high-confidence ink probability maps; non-technical
social-science colleagues who need visual and statistical summaries rather
than raw arrays; and future researchers extending the modular codebase without
re-deriving the underlying statistics.

\section{Methodology}

\subsection{Gaussian Mixture Modeling of Voxel Intensity}

Each voxel intensity $x_i$ is assumed drawn from a finite mixture of Gaussian
components, one per material class:

$$
p(x) = \sum_{k=1}^{K} \pi_k \, \mathcal{N}(x \mid \mu_k, \sigma_k^2)
$$

where $\pi_k$ is the mixing weight, and $\mu_k, \sigma_k^2$ the mean and
variance of material class $k$. Parameters are estimated via Expectation-
Maximization (EM), yielding per-voxel posterior responsibilities
$\gamma_{ik} = P(z_i = k \mid x_i)$.

\subsection{Automatic Model-Order Selection (BIC and Sparse Bayesian Priors)}

The number of components $K$ is not fixed by hand. Two complementary
strategies are implemented:

\textbf{Bayesian Information Criterion (BIC) sweep.} A grid of candidate
$K \in [K_{\min}, K_{\max}]$ is fit and scored by

$$
\text{BIC}(K) = -2 \ln \hat{L} + p_K \ln N
$$

where $\hat L$ is the maximized data likelihood, $p_K$ the number of free
parameters for a $K$-component model, and $N$ the sample size. The $K$
minimizing BIC is retained (\texttt{Gmm\_Fitter}).

\textbf{Sparse overcomplete Bayesian GMM.} An intentionally overcomplete
mixture ($K_{\max}$ components) is fit with a Dirichlet weight-concentration
prior via variational inference (\texttt{sklearn.BayesianGaussianMixture}).
Components are retained only if both their weight and their effective sample
count exceed thresholds:

$$
\text{Active}(k) \iff \pi_k \geq \tau_\pi \ \text{and} \ \sum_i \gamma_{ik} \geq N_{\min}
$$

This lets the data "switch off" unsupported components rather than
committing to a fixed $K$ in advance (\texttt{Sparse\_Bayesian\_Gmm}).

\subsection{Hierarchical Refinement of Components}

Each root component from the flat GMM is recursively tested for internal
substructure using soft path-probability propagation: every voxel retains a
fractional membership $\gamma$ along the tree rather than being hard-assigned
before the tree is built. For a candidate node with accumulated path
probability $\gamma_i$ over $N$ effective samples $N_{\text{eff}} = \sum_i \gamma_i$,
a single Gaussian (parent) is compared against a 2-component split (child)
fit with the same sample weights.

Weighted log-likelihoods are compared via BIC, penalizing the split's extra
parameters (2 for the unsplit 1D Gaussian vs.\ 5 for a 2-component 1D GMM:
two means, two variances, one weight):

\begin{align*}
\text{BIC}_{\text{parent}} &= -2 \ln \hat{L}_{\text{parent}} + 2 \ln N_{\text{eff}} \\
\text{BIC}_{\text{split}} &= -2 \ln \hat{L}_{\text{split}} + 5 \ln N_{\text{eff}}
\end{align*}

Statistical significance of the split is additionally verified with a
Likelihood-Ratio Test (LRT):

$$
\Lambda = 2\left(\ln \hat{L}_{\text{split}} - \ln \hat{L}_{\text{parent}}\right), \qquad
\Lambda \sim \chi^2_{(3)} \ \text{under } H_0
$$

with 3 degrees of freedom (5 split parameters minus 2 parent parameters). A
node is split only if \emph{both} $\text{BIC}_{\text{split}} < \text{BIC}_{\text{parent}}$
\emph{and} the LRT $p$-value is below $\alpha = 0.05$. Recursion stops when
either gate fails, when the effective sample count drops below $N_{\min}$, or
when a maximum tree depth is reached (\texttt{Hierarchical\_Gmm}).
Crucially, components split — not data: every voxel keeps a normalized soft
membership across all final leaf components, $\sum_\ell P(\ell \mid x_i) = 1$.

\subsection{Spatial Regularization via Hidden Markov Random Field}

Pure intensity-based classification ignores 3D spatial coherence, so
ambiguous voxels (near-equal posterior across two classes) are resolved using
a Potts-model HMRF. The total energy of a label field $\mathbf{L}$ combines
the GMM's unary (data) term with a pairwise spatial smoothness term:

$$
E(\mathbf{L}) = \underbrace{\sum_i -\ln p(x_i \mid L_i)}_{\text{GMM likelihood (unary)}}
\;+\; \underbrace{\beta \sum_{i \sim j} \delta(L_i \neq L_j)}_{\text{Potts prior (pairwise)}}
$$

where $i \sim j$ ranges over the 6- or 26-connected 3D neighborhood of voxel
$i$, $\beta$ controls smoothness strength, and $\delta(\cdot)$ is 1 when
neighboring labels disagree. The energy is minimized by Iterated Conditional
Modes (ICM): each voxel's label is updated to the class minimizing its local
energy given the current labels of its neighbors, iterating until no labels
change or a maximum iteration count is reached (\texttt{Hmrf\_Segmenter}).

\subsection{Uncertainty Quantification}

Because the pipeline is fully probabilistic, per-voxel confidence can be
reported directly from the posterior $\gamma_{i\cdot}$ rather than only a
hard label. Two complementary measures are computed:

$$
H_i = -\sum_{k} \gamma_{ik} \ln \gamma_{ik} \qquad \text{(Shannon entropy; high = uncertain)}
$$

and the margin between the top two class posteriors,
$M_i = \gamma_{i,(1)} - \gamma_{i,(2)}$, where $\gamma_{i,(1)} \geq \gamma_{i,(2)}$
are the sorted posteriors (small margin = ambiguous between exactly two
classes) (\texttt{Compute\_Uncertainty}, \texttt{Compute\_Margin}).

\subsection{Preprocessing: Statistics-First, Not Visualization-First}

A key methodological finding is that preprocessing must preserve the global
intensity-to-material relationship the GMM relies on, rather than optimize
for human visual contrast. Local-contrast tools such as CLAHE or anisotropic
(Perona--Malik) diffusion actively destroy the global statistical structure
GMM depends on, because they remap intensities differently in different
spatial regions. The revised pipeline instead applies, in order:

\begin{enumerate}[nosep]
    \item \textbf{Global background correction} — a large-sigma Gaussian
    estimates the slowly varying beam-hardening baseline per slice, which is
    then subtracted and shifted positive:
    $$ I_{\text{corr}} = I - G_\sigma * I - \min\left(I - G_\sigma * I\right) $$
    \item \textbf{Mild Gaussian smoothing} (typically $\sigma \approx 0.8$) to
    tighten per-material distributions without merging modes.
    \item \textbf{Optional per-slice standardization} if a stationarity check
    (histogram intersection between first/middle/last slice) indicates
    slice-to-slice drift: $I'_z = (I_z - \mu_z)/\sigma_z$.
    \item \textbf{Global percentile normalization} — a single affine map
    applied identically to every voxel, preserving relative material
    ordering:
    $$ I' = \frac{I - P_{\text{low}}}{P_{\text{high}} - P_{\text{low}}}
    \left(T_{\max} - T_{\min}\right) + T_{\min} $$
\end{enumerate}

A histogram-diagnostics module scores GMM-readiness on a 0--1 scale from mode
count, skewness, kurtosis, and dynamic range before any GMM fitting is
attempted, flagging volumes that need re-preprocessing.

\subsection{XRF Branch: Compositional Data Analysis and Elemental Clustering}

Elemental XRF maps are proportions of a finite element panel and therefore
live on the simplex, not in Euclidean space — summing raw intensities and
comparing them directly is statistically invalid (the "closure" problem). The
XRF branch first normalizes each valid pixel's element-intensity vector to
proportions, replaces exact zeros with a small constant $\delta$ for
numerical stability, and applies the Centered Log-Ratio (CLR) transform:

$$
\text{CLR}(x)_i = \ln x_i - \frac{1}{n}\sum_{j=1}^n \ln x_j
$$

which maps the simplex into real Euclidean space where standard multivariate
statistics (and Euclidean-distance-based clustering) are valid
(\texttt{Clr\_Transformer}). Dimensionality is then reduced with PCA
(retaining a target variance fraction, e.g. 95\%) before fitting a GMM in the
reduced space, again with BIC used to sweep candidate $K$
(\texttt{Xrf\_Gmm\_Segmenter}).

\subsection{XRF Branch: Page Signatures and Rarity Triage}

For each page, a compact composition signature is built from the per-class
area fraction of the clustered elemental map:

$$
A_k = \frac{1}{N}\sum_{i=1}^N \mathbb{1}[\text{label}_i = k], \qquad
\sum_k A_k = 1
$$

(\texttt{Leaf\_Signature\_Extractor}). Page signatures are aggregated into
per-structural-category signatures using a weighted mean, with spread
measured by the per-class Median Absolute Deviation (MAD) rather than
standard deviation, since category groups can be small
(\texttt{Category\_Signature\_Aggregator}). Individual pages are then ranked
by a robust per-class deviation from their category:

$$
z_k = 0.6745 \cdot \frac{x_k - \text{median}_k}{\text{MAD}_k}
$$

flagging a page when $\max_k |z_k|$ exceeds a configured threshold
(\texttt{Rarity\_Scorer}). This is explicitly documented in the code as a
triage/ranking heuristic for human review, not a hypothesis test, since
small-$N$ category groups do not support formal significance claims.

\section{Procedure/Pipeline}

% ==============================================================================
% [TIKZ SPECIFICATION: CT Segmentation Pipeline (Data Flow)]
% Recommended Packages: \usepackage{tikz}
% TikZ Libraries Needed: \usetikzlibrary{positioning, arrows.meta, shapes.geometric, calc}
% Diagram Type: Horizontal multi-stage pipeline with side annotations
%
% STYLES & NODES:
%   - Data node: [draw, rectangle, dashed, rounded corners, fill=gray!10] -> data artifacts
%   - Process node: [draw, rectangle, rounded corners, fill=blue!10] -> processing steps
%   - Decision node: [draw, diamond, aspect=2, fill=orange!10] -> readiness/branch check
%
% LAYOUT & CONNECTIONS (left to right, wrap to a second row if needed):
%   1. Data: "Raw TIFF stack (D slices)" (research_ct.io.volume_loader)
%   2. -> Process: "Background correction" I_corr = I - G_sigma*I  (background_correction.py)
%   3. -> Process: "Gaussian smoothing (sigma~0.8)" (global_normalization.py / pipeline_revised.py)
%   4. -> Decision: "Stationary across slices?" -> if no: "Per-slice z-score" side branch
%   5. -> Process: "Global percentile normalization" (global_normalization.py)
%   6. -> Decision: "GMM-ready? (histogram_diagnostics.py readiness score)" -> if no: loop back to step 2 with adjusted sigma
%   7. -> Process: "Flat GMM fit, BIC sweep over K" (gmm_fitter.py) -> Data: "mu_k, sigma_k, pi_k"
%   8. -> Process: "Hierarchical soft splitting (BIC + LRT gates)" (hierarchy.py) -> Data: "Leaf component tree, gamma_ik"
%   9. -> Process: "HMRF spatial regularization (ICM, Potts beta)" (hmrf.py) -> Data: "Label volume L, shape (D,H,W)"
%   10. -> Process (parallel branch off step 9's probabilities): "Uncertainty maps: entropy H_i, margin M_i" (uncertainty_maps.py)
%   11. -> Process: "Material statistics: per-class voxel counts, volume fraction" (material_stats.py)
%   12. -> Process (optional): "Page surface extraction (connected components)" (page_extractor.py)
% Annotate step 6's "no" branch in red/dashed; annotate steps 1-6 as "Preprocessing" and 7-9 as "Segmentation Core" and 10-12 as "Analysis/Output" using a background \fit box or braces per stage.
% ==============================================================================

% ==============================================================================
% [TIKZ SPECIFICATION: XRF Elemental Pipeline (Data Flow)]
% Recommended Packages: \usepackage{tikz}
% TikZ Libraries Needed: \usetikzlibrary{positioning, arrows.meta, shapes.geometric}
% Diagram Type: Horizontal multi-stage pipeline
%
% STYLES & NODES: same style conventions as the CT pipeline spec above.
%
% LAYOUT & CONNECTIONS:
%   1. Data: "Raw .bcf file / elemental TIFFs" -> Process: "BCF extraction" (xrf.preprocessing.bcf_extractor)
%   2. -> Process: "Loading + valid-pixel masking" (xrf.io.xrf_loader)
%   3. -> Process: "Proportions + zero replacement + CLR transform" x_i -> ln(x_i) - mean(ln x)  (xrf.transforms.coda.Clr_Transformer)
%   4. -> Process: "PCA (retain ~95% variance) + GMM clustering, BIC sweep over K" (xrf.segmentation.xrf_gmm.Xrf_Gmm_Segmenter)
%   5. -> Process: "2D class-map reconstruction + connected-component descriptors" (xrf.spatial.spatial_analyzer.Spatial_Analyzer)
%   6. -> Process: "Per-page leaf signature A_k (area fractions)" (xrf.signatures.leaf_signature.Leaf_Signature_Extractor)
%   7. -> Process: "Per-category signature aggregation (weighted mean, MAD spread)" (xrf.comparison.category_signatures)
%   8. -> Process: "Rarity scoring: robust z-score ranking" (xrf.comparison.rarity_scoring.Rarity_Scorer) -> Data: "Flagged pages for human review"
%   9. Dashed/future branch off step 4 and off the CT "Label volume L": -> Process (todo, empty file): "CT-XRF fusion" (xrf.fusion.ct_xrf_fusion — currently an empty placeholder module) -> Data: "Joint material catalog"
% ==============================================================================

The two pipelines are currently independent and are driven from ordered
Jupyter notebooks rather than a single CLI entry point, which keeps each
processing step inspectable in isolation during development:

\begin{center}
\begin{tabular}{ll}
\toprule
\textbf{Notebook} & \textbf{Purpose} \\
\midrule
\texttt{01\_explore\_raw\_data.ipynb} & Load raw TIFF stack, inspect histograms/metadata \\
\texttt{02\_run\_preprocessing.ipynb} & Run preprocessing pipeline, histogram diagnostics \\
\texttt{03\_gmm\_and\_hierarchical\_segmentation.ipynb} & BIC-GMM, sparse Bayesian GMM, hierarchy, streaming export \\
\texttt{04\_spatial\_hmrf.ipynb} & HMRF on a test region, GMM-only vs.\ HMRF comparison \\
\texttt{05\_uncertainty\_and\_visualization.ipynb} & Material stats, uncertainty maps, napari 3D, video export \\
\midrule
\texttt{xrf/xrf\_bcf\_extraction.ipynb} & Extract elemental maps from raw \texttt{.bcf} \\
\texttt{xrf/01\_xrf\_loading\_and\_masking.ipynb} & Load elemental TIFFs, build valid-pixel mask \\
\texttt{xrf/02\_coda\_transformations.ipynb} & Proportions + CLR transform \\
\texttt{xrf/03\_gmm\_spatial\_clustering.ipynb} & PCA + GMM clustering, spatial descriptors \\
\texttt{xrf/04\_leaf\_signatures.ipynb} & Per-page abundance signatures \\
\texttt{xrf/05\_page\_categorization.ipynb} & Assign structural category tags to pages \\
\texttt{xrf/06\_category\_signature\_comparison.ipynb} & Aggregate signatures per category \\
\texttt{xrf/07\_rarity\_review.ipynb} & Rank/flag pages by robust deviation \\
\bottomrule
\end{tabular}
\end{center}

\section{Results}

% ==============================================================================
% [NEW PLOT NEEDED: GMM Component Decomposition]
% Suggested Source: Generated from `Gmm_Fitter` / `Sparse_Bayesian_Gmm` outputs in notebook 03
% Plot Type: Overlaid histogram + fitted Gaussian component curves (line chart)
% X-Axis: Label = "Voxel Intensity (normalized, 0-255)", Range/Scale = [0 to 255]
% Y-Axis: Label = "Probability Density", Range/Scale = [0 to max density]
% Data Series / Curves:
%   1. Raw normalized intensity histogram (Color: Gray, filled bars)
%   2. Full mixture density sum_k pi_k N(x|mu_k,sigma_k^2) (Color: Black, Solid)
%   3. One dashed curve per retained component k, colored by hypothesized material (air/paper/ink/cover)
% Key Trend to Highlight: Number of active components K selected by BIC (or retained by sparse weight threshold), and how well component means align with visually distinct histogram modes.
% ==============================================================================

% ==============================================================================
% [NEW PLOT NEEDED: BIC Model-Selection Curve]
% Suggested Source: `Gmm_Fitter.Bic_Scores` collected during the K-sweep in notebook 03
% Plot Type: Line chart
% X-Axis: Label = "Number of Components K", Range/Scale = [Min_Components to Max_Components]
% Y-Axis: Label = "BIC Score", Range/Scale = [min(Bic_Scores) to max(Bic_Scores)]
% Data Series / Curves:
%   1. BIC(K) (Color: Blue, Solid, marker at each integer K)
% Key Trend to Highlight: Mark the minimum BIC point as the selected K with a vertical dashed line/annotation.
% ==============================================================================

% ==============================================================================
% [NEW PLOT NEEDED: Hierarchical Component Tree]
% Suggested Source: `Hierarchical_Gmm.Trees` structure from notebook 03
% Plot Type: Tree/dendrogram diagram (not a data plot — structural diagram)
% Key elements: Root node per initial component; internal nodes annotated with BIC_parent vs BIC_split and LRT p-value; leaf nodes annotated with Effective_Samples and final Mean/Variance.
% Key Trend to Highlight: Which branches passed both the BIC-improvement gate and the p<0.05 significance gate versus which were rejected and kept as leaves.
% ==============================================================================

% ==============================================================================
% [NEW PLOT NEEDED: HMRF Before/After Spatial Regularization]
% Suggested Source: `Hmrf_Segmenter.Fit` outputs from notebook 04, compared against the pre-HMRF argmax labels
% Plot Type: Side-by-side 2D slice label maps (categorical heatmap / segmentation mask comparison)
% X-Axis: Label = "Voxel column (pixels)"
% Y-Axis: Label = "Voxel row (pixels)"
% Data Series / Curves:
%   1. Left panel: GMM-only argmax labels (no spatial term)
%   2. Right panel: HMRF-regularized labels after ICM convergence
% Key Trend to Highlight: Reduction of speckled/isolated mislabeled voxels near material boundaries after applying the beta-weighted Potts prior; annotate the number of ICM iterations to convergence and the number of labels changed per iteration.
% ==============================================================================

% ==============================================================================
% [NEW PLOT NEEDED: Per-Voxel Uncertainty Map]
% Suggested Source: `Compute_Uncertainty` (entropy, max probability) from notebook 05
% Plot Type: 2D heatmap (spatial slice) with colorbar
% X-Axis: Label = "Voxel column (pixels)"
% Y-Axis: Label = "Voxel row (pixels)"
% Data Series / Curves:
%   1. Shannon entropy H_i heatmap (colormap: viridis/hot, high entropy = bright)
%   2. Optional second panel: margin M_i heatmap
% Key Trend to Highlight: Entropy/low-margin voxels concentrated at material interfaces (e.g. ink-paper boundaries), confirming the HMRF's targeted use case.
% ==============================================================================

% ==============================================================================
% [NEW PLOT NEEDED: Material Statistics Summary]
% Suggested Source: `Compute_Material_Statistics` / `Print_Material_Report` from notebook 05
% Plot Type: Bar chart
% X-Axis: Label = "Material Class (air/paper/ink/cover)"
% Y-Axis: Label = "Volume Fraction", Range/Scale = [0 to 1]
% Data Series / Curves:
%   1. Volume fraction per class (Color: distinct per bar)
% Key Trend to Highlight: Relative proportion of ink/text-bearing voxels versus bulk paper and background air.
% ==============================================================================

% ==============================================================================
% [NEW PLOT NEEDED: XRF CLR-PCA-GMM Clustering]
% Suggested Source: `Xrf_Gmm_Segmenter.Fit_Predict` outputs from notebook xrf/03
% Plot Type: Scatter plot (2D PCA projection) + reconstructed 2D class map
% X-Axis: Label = "Principal Component 1", Range/Scale = [auto]
% Y-Axis: Label = "Principal Component 2", Range/Scale = [auto]
% Data Series / Curves:
%   1. CLR-transformed, PCA-projected pixels colored by GMM cluster label
% Key Trend to Highlight: Separation of elemental clusters in reduced CLR space; side panel showing the same labels reconstructed onto the physical page layout via `Spatial_Analyzer.Reconstruct_Class_Map`.
% ==============================================================================

% ==============================================================================
% [NEW PLOT NEEDED: Category Signature Comparison]
% Suggested Source: `Category_Signature_Aggregator.Aggregate_By_Category` / `Compute_Category_Spread` from notebook xrf/06
% Plot Type: Radar chart and/or grouped bar chart with error bars
% X-Axis: Label = "Elemental/GMM class index k"
% Y-Axis: Label = "Mean abundance A_k", Range/Scale = [0 to 1]
% Data Series / Curves:
%   1. One series per structural page category, mean abundance vector
%   2. Error bars/spread = per-class MAD
% Key Trend to Highlight: Categories with distinctly different elemental abundance profiles (e.g. text pages vs. blank pages vs. cover pages).
% ==============================================================================

% ==============================================================================
% [NEW PLOT NEEDED: Rarity Ranking]
% Suggested Source: `Rarity_Scorer.Rank_Pages_By_Rarity` from notebook xrf/07
% Plot Type: Horizontal bar chart / lollipop chart, sorted descending
% X-Axis: Label = "Max Absolute Robust Deviation |z|_max"
% Y-Axis: Label = "Page ID (sorted by rarity)"
% Data Series / Curves:
%   1. Bar per page, colored by Is_Flagged (above/below Config.Rarity_Mad_Threshold)
% Key Trend to Highlight: Vertical threshold line at Config.Rarity_Mad_Threshold; identify the small set of outlier pages recommended for human review.
% ==============================================================================

Quantitative outputs of the pipeline are: (1) a selected number of material
components $K$ (both from the plain BIC sweep and the sparse Bayesian
alternative, for cross-checking); (2) per-voxel hard labels and full posterior
probability volumes; (3) per-class material statistics (voxel counts, volume
fraction, mean/std intensity); (4) spatial uncertainty maps identifying
boundary-ambiguous regions; and, on the XRF side, (5) per-page elemental
abundance signatures, per-category aggregate profiles, and a ranked rarity
list flagging pages whose composition is anomalous relative to their
structural category.

Project logs (not independently re-verified against \texttt{data/} for this
report) record that both pipelines have already been executed once on real
scans: the CT pipeline on a micro-CT stack of roughly 431 TIFF slices, and the
XRF pipeline on an 8-element elemental map set (Pb, K, Hg, Fe, Cu, Ca, Au, As)
that produced a 7-component GMM clustering with exported per-cluster masks and
page-level signatures. These figures should be treated as prior reported
results to be reproduced and re-plotted from the notebooks, not as numbers
sourced from this session's own inspection of \texttt{data/}.

\section{Code Structure / Repository Documentation}

The repository is organized as two parallel, independent Python packages
under \texttt{src/}, both consumed primarily through the notebooks in
\texttt{notebooks/}:

\begin{itemize}[nosep]
    \item \textbf{\texttt{research\_ct/}} — the micro-CT pipeline.
    \begin{itemize}[nosep]
        \item \texttt{io/} — \texttt{volume\_loader.py}, \texttt{volume\_saver.py}, \texttt{metadata\_parser.py}, \texttt{dragonfly\_exporter.py}: reading/writing TIFF volumes and exporting to third-party viewers (Dragonfly).
        \item \texttt{preprocessing/} — \texttt{pipeline\_revised.py} (current statistics-first pipeline), \texttt{background\_correction.py}, \texttt{global\_normalization.py}, \texttt{histogram\_diagnostics.py}, \texttt{noise\_reduction.py}, plus legacy/alternate modules \texttt{pipeline.py}, \texttt{contrast.py}, \texttt{diffusion.py}, \texttt{diagnostic.py}, \texttt{config.py}.
        \item \texttt{segmentation/} — \texttt{gmm\_fitter.py}, \texttt{sparse\_bayesian\_gmm.py}, \texttt{hierarchy.py}, \texttt{hmrf.py}, and \texttt{decision\_engine.py}, which orchestrates all three (flat GMM $\to$ hierarchical refinement $\to$ HMRF) behind a single \texttt{Segmentation\_Engine.Run()} call.
        \item \texttt{analysis/} — \texttt{material\_stats.py}, \texttt{uncertainty\_maps.py}, \texttt{page\_extractor.py}: turn labels/probabilities into reportable numbers and connected-component page masks.
        \item \texttt{visualization/} — \texttt{napari\_viewer.py}, \texttt{plot\_distributions.py}, \texttt{export.py}, \texttt{histogram\_diagnostics\_viewer.py}: 3D viewing and diagnostic plotting, imported lazily to avoid overhead in headless runs.
        \item \texttt{processing/dragonfly\_utils.py} — helpers bridging to the Dragonfly desktop tool.
    \end{itemize}
    \item \textbf{\texttt{xrf/}} — the elemental-fluorescence pipeline.
    \begin{itemize}[nosep]
        \item \texttt{io/xrf\_loader.py} — loads elemental TIFFs and builds the valid-pixel mask.
        \item \texttt{preprocessing/bcf\_extractor.py} — extracts elemental maps from raw \texttt{.bcf} detector files.
        \item \texttt{transforms/coda.py} — \texttt{Clr\_Transformer}, the Compositional Data Analysis (CLR) transform.
        \item \texttt{segmentation/xrf\_gmm.py} — \texttt{Xrf\_Gmm\_Segmenter}: PCA + GMM clustering with a BIC sweep.
        \item \texttt{spatial/spatial\_analyzer.py} — \texttt{Spatial\_Analyzer}: 2D class-map reconstruction and connected-component descriptors.
        \item \texttt{signatures/leaf\_signature.py} — \texttt{Leaf\_Signature\_Extractor}: per-page abundance signatures.
        \item \texttt{comparison/} — \texttt{category\_registry.py}, \texttt{category\_signatures.py}, \texttt{rarity\_scoring.py}, \texttt{spatial\_comparison.py}: category tagging, signature aggregation, and rarity triage.
        \item \texttt{fusion/ct\_xrf\_fusion.py} — currently an \textbf{empty placeholder file}; joint CT+XRF material fusion is not yet implemented.
        \item \texttt{config.py} — shared configuration dataclasses (e.g.\ \texttt{Xrf\_Comparison\_Config.Rarity\_Mad\_Threshold}).
    \end{itemize}
\end{itemize}

\textbf{Workflow approach.} Both packages follow the same layering
discipline: I/O and preprocessing modules never import from segmentation or
analysis modules (no circular imports); heavy visualization dependencies are
imported inside functions rather than at module scope; and each notebook
corresponds to exactly one pipeline stage so intermediate artifacts can be
inspected and re-run independently rather than requiring a full end-to-end
script execution. Class and function naming follows a consistent
\texttt{Pascal\_Case\_With\_Underscores} convention across both packages, and
public methods are documented with Google-style docstrings including
\texttt{Args}/\texttt{Returns}/\texttt{Raises}.

\textbf{Notable code-level design decisions worth noting for the report:}
\begin{itemize}[nosep]
    \item In-place array operations (via explicit \texttt{out=} parameters) are used throughout the CT preprocessing chain to control memory footprint on large float64 volumes.
    \item \texttt{Hierarchical\_Gmm} explicitly favors soft path-probability propagation over hard reassignment at each split, so uncertainty is preserved end-to-end into the final leaf posteriors.
    \item \texttt{Rarity\_Scorer} and \texttt{Category\_Signature\_Aggregator} deliberately use median/MAD rather than mean/std, since page-category groups can be small and heavy-tailed.
    \item The XRF fusion module's presence as an empty file signals an explicitly scoped-but-unimplemented integration point between the two pipelines.
\end{itemize}

\section{Conclusion}

The codebase delivers a fully unsupervised, probabilistic segmentation
pipeline for micro-CT volumes of sealed books that removes the two main
weaknesses of prior fixed-$k$/manual-threshold approaches: it estimates the
number of material classes directly from the data (via BIC sweep and,
alternatively, a sparse overcomplete Bayesian GMM), and it produces
calibrated posterior probabilities rather than only hard labels, enabling
principled downstream uncertainty quantification (Shannon entropy, posterior
margin). Hierarchical soft-splitting adds the ability to recover
sub-structure within an initially coarse component (e.g.\ separating ink from
cover material) without discarding global responsibility information, and
spatial HMRF regularization resolves locally ambiguous voxels using 3D
neighborhood context via a Potts-model energy minimized by ICM.

In parallel, the XRF branch establishes a statistically sound elemental
analysis workflow grounded in Compositional Data Analysis (CLR transform),
avoiding the closure-effect pitfalls of treating raw elemental intensities as
Euclidean features. Its page-signature and rarity-scoring tools provide a
practical triage mechanism for directing expert attention to anomalous pages,
explicitly framed as a heuristic rather than a formal statistical test.

Remaining open work, visible directly from the repository state and confirmed
by the project's own tracked next-steps, includes: full-volume execution and
validation of the pipeline (memory scaling for large float64 volumes and ICM
performance at large $K$ and voxel counts remain named risks), cross-validating
CT material labels against XRF compositional clusters where both modalities
cover the same pages, and implementing the currently placeholder CT–XRF fusion
module so that absorption-based and elemental-based material evidence can be
combined into a single joint material catalog. A further open risk explicitly
tracked by the project is that carbon-based inks may remain intensity-invisible
under absorption CT regardless of segmentation quality, which is the primary
argument for the XRF branch as a complementary, non-absorption-based source of
material evidence.
```

---

# Update: Deep-Dive Multi-File Phase (`xrf_pipeline.tex`, `microct_pipeline.tex`, `bcf_processing.tex`)

## New instructions from the user (2026-08-12)
- Split the deep technical pipeline write-up into **3 independent files**, done **sequentially, one at a time**, stopping after each for explicit "Proceed to Phase N" confirmation.
- **Structural shift for these 3 files only:** no `\section{}` at all — use `\subsection{}`, `\subsubsection{}`, `\paragraph{}` only, since they are meant to be `\input{}`ed into a larger document (presumably under the `\section{Methodology}` / `\section{Procedure/Pipeline}` of `report_content.tex`, or the user's own template section — not specified, and not blocking since these files don't declare their own `\section`).
- Same Figure Handling Protocol (Rules 1/2/3) and math formatting as before. Given the user's earlier confirmed decision (all figures via Rule 3 placeholders, never `\includegraphics` from `data/`), that same decision carries forward here.
- High rigor: no skipped math steps; explicit mapping of every mathematical symbol to the actual NumPy/Python variable and data structure in the code; explicit data lifecycle (load/store/transform/save) per notebook step.
- Phase 2 (Micro-CT) has an extra requirement: cover **every** method/algorithm/experiment present in the CT notebooks, not just the final chosen one (e.g. legacy `pipeline.py` visual-enhancement path alongside the active `pipeline_revised.py` statistics path, and both `Gmm_Fitter`/BIC and `Sparse_Bayesian_Gmm` alternatives).
- Phase 3 (BCF) has an extra requirement: explicit library focus (HyperSpy, h5py, NumPy specifics) and how each library call is leveraged.
- **Plan Mode constraint (unchanged):** I can only write to this plan file. I cannot create `xrf_pipeline.tex` (or the other two files) directly. The content below is the complete, ready-to-copy deliverable for Phase 1 — an implementation-capable agent must copy it verbatim into a new file. Output location is assumed to match `report_content.tex`'s sibling location, `C:\Users\gabri\Documento\Mitacs\xrf_pipeline.tex`, unless the user specifies otherwise.
- Per the user's explicit sequencing rule, **stop after Phase 1** and wait for "Proceed to Phase 2" before drafting `microct_pipeline.tex`.

## Source material read for Phase 1 (XRF notebooks 01–07, in addition to the `src/xrf/` modules already read for `report_content.tex`)
| Notebook | File |
|---|---|
| 01 | `notebooks/xrf/01_xrf_loading_and_masking.ipynb` |
| 02 | `notebooks/xrf/02_coda_transformations.ipynb` |
| 03 | `notebooks/xrf/03_gmm_spatial_clustering.ipynb` |
| 04 | `notebooks/xrf/04_leaf_signatures.ipynb` |
| 05 | `notebooks/xrf/05_page_categorization.ipynb` |
| 06 | `notebooks/xrf/06_category_signature_comparison.ipynb` |
| 07 | `notebooks/xrf/07_rarity_review.ipynb` |

Additional `src/xrf/` files read specifically to ground this deep dive precisely (beyond what `report_content.tex` already cites): `io/xrf_loader.py` (`Xrf_Loader`, `Update_Page_Metadata`), `config.py` (all 5 dataclasses), `comparison/category_registry.py` (`Category_Registry`), `comparison/spatial_comparison.py` (`Category_Spatial_Comparator`), `visualization/xrf_plots.py` (`Plot_Category_Signature_Bars`, `Plot_Category_Signature_Radar`, `Build_Category_Montage`).

Note: `notebooks/xrf/xrf_bcf_extraction.ipynb` and `src/xrf/preprocessing/bcf_extractor.py` were intentionally **not** used here — they belong to Phase 3 (`bcf_processing.tex`).

## Notable implementation details surfaced during this deep read (included in the content below as explicit rigor notes, not glossed over)
- `Compute_Intensity_Mask` is called twice in notebook 01 (once immediately after loading, once again after plotting the histogram) and the mask/valid-pixel `.npy` files are saved twice identically — redundant but not incorrect.
- `Compute_Bic_Curve` hardcodes `covariance_type` implicitly to sklearn's default (`"full"`) inside its own `GaussianMixture(n_components=K, random_state=42)` call, ignoring `seg_config.Covariance_Type` — only `Fit_Predict` actually honors the configured `Covariance_Type`.
- The notebook 03 "optimal" $K=8$ is **hardcoded by visual choice**, not `argmin` of the BIC curve just computed — the BIC curve is diagnostic only in this run.
- `Fit_Predict` re-fits a brand-new `PCA` instance rather than reusing the one fit inside `Compute_Bic_Curve` — harmless but duplicated computation.
- `Cluster_Segmentation_Map.tiff` is written to the notebook's current working directory (not `PROCESSED_DATA_DIR`), unlike every other artifact in the same cell — a path inconsistency.
- `Leaf_Signature_Extractor.Compute_Abundances` is implemented as an explicit `for K in range(Num_Classes)` loop, not a vectorized `np.bincount`, despite computing the same quantity.
- `Compute_Weighted_Book_Signature` manually renormalizes `Weights` and then also passes them to `np.average(..., weights=...)`, which renormalizes internally again — a harmless double-normalization.
- Notebook 04's demonstration of `Compute_Weighted_Book_Signature` is run on **synthetic mock data** (`np.random.rand(5, optimal_k)`), not real multi-page data; the real aggregation path is notebook 06's `Category_Signature_Aggregator`, which reuses the identical function with uniform weights.
- Notebooks 06 and 07 both **recompute** `Page_Signatures`/`Page_Categories` from scratch by reloading `labels.npy` + `meta.json` rather than reusing any previously saved abundance vector — the only cross-notebook persisted signal is the `structural_category` field written into `meta.json` by notebook 05.
- `Category_Signature_Aggregator.Aggregate_By_Category` calls `np.stack` across all pages in a category, which silently assumes every page in that category was segmented with the **same** $K$ (`optimal_k`) — since $K$ is chosen manually per page in notebook 03, this is an implicit cross-page consistency assumption, not an enforced invariant.
- `Category_Spatial_Comparator.Aggregate_Region_Stats`'s output is displayed inline in notebook 06 but **never saved to disk** — only the categorical `config` values (not the computed stats) are captured in `category_comparison_summary.json`.
- The `0.6745` constant in `Rarity_Scorer.Compute_Robust_Deviation` is the standard normal-consistency scale for the median absolute deviation ($\approx 1/1.4826$), making the robust deviation an approximation of a z-score under a Gaussian null.
- Rarity ranking aggregates per-class deviations via the $L^\infty$ norm (`np.max(np.abs(...))`), i.e. a single worst-offending class flags a page — not a joint/Mahalanobis-style multivariate outlier statistic.

## Phase 1 Deliverable: `xrf_pipeline.tex` (write verbatim to `Mitacs/xrf_pipeline.tex`)

```latex
% ==============================================================================
% xrf_pipeline.tex
% No \section{} — subsection/subsubsection/paragraph only. Intended for
% \input{} into a larger document (e.g. under the main report's Methodology
% or Procedure/Pipeline section).
% ==============================================================================

\subsection{XRF Elemental Pipeline: Notation and Data-Structure Mapping}

Before detailing each notebook, the mathematical notation used throughout this
pipeline is fixed against the exact NumPy data structures that carry it in
code, since every subsequent step operates on one of these objects:

\begin{center}
\begin{tabular}{lll}
\toprule
\textbf{Symbol} & \textbf{Meaning} & \textbf{Code variable / type} \\
\midrule
$p = (i,j)$ & Pixel index in a page image & Implicit array index into axes 0,1 \\
$n$ & Number of elemental channels & \texttt{stack.shape[-1]} (e.g. 6 in the loaded example) \\
$S \in \mathbb{R}^{M\times N \times n}_{\geq 0}$ & Raw elemental data cube & \texttt{stack}, \texttt{np.ndarray} shape $(M,N,n)$, \texttt{float64} \\
$T(p) = \sum_{k=1}^n S_{i,j,k}$ & Total accumulated intensity & \texttt{total\_intensity}, shape $(M,N)$ \\
$\tau$ & Noise/validity threshold & \texttt{config.Noise\_Threshold} (\texttt{Xrf\_Preprocessing\_Config}) \\
$B \in \{0,1\}^{M\times N}$ & Validity mask & \texttt{mask}, boolean \texttt{np.ndarray} $(M,N)$ \\
$x \in \mathbb{R}^{N_{\text{valid}}\times n}_{\geq 0}$ & Flattened valid raw pixel vectors & \texttt{valid\_pixels} $= $\texttt{stack[mask]} \\
$y \in \Delta^{n-1}$ (simplex) & Closed compositional proportions & \texttt{Proportions}, shape $(N_{\text{valid}}, n)$ \\
$\delta$ & Zero-replacement constant & \texttt{config.Zero\_Replacement\_Delta} $= 10^{-4}$ \\
$z \in \mathbb{R}^n$, $\sum_i z_i = 0$ & CLR-transformed coordinates & \texttt{clr\_data}, shape $(N_{\text{valid}}, n)$ \\
$m$ & Retained PCA dimensionality & inferred at runtime from \texttt{Pca\_Variance\_Ratio} \\
$Z \in \mathbb{R}^{N_{\text{valid}}\times m}$ & PCA-projected coordinates & \texttt{Z\_Data} inside \texttt{Xrf\_Gmm\_Segmenter} \\
$K$ & Number of compositional classes & \texttt{Num\_Components} / \texttt{optimal\_k} \\
$\gamma \in [0,1]^{N_{\text{valid}}\times K}$ & GMM posterior responsibilities & \texttt{probabilities} \\
$\ell \in \{0,\dots,K-1\}^{N_{\text{valid}}}$ & Hard class labels & \texttt{labels} \\
$C \in \{-1,0,\dots,K-1\}^{M\times N}$ & Reconstructed 2D class map & \texttt{class\_map} \\
$A \in \Delta^{K-1}$ & Per-page abundance signature $F_h$ & \texttt{abundances} \\
$w_h$ & Per-page reliability weight & \texttt{mock\_weights} / \texttt{Uniform\_Weights} \\
$\bar F$ & Weighted signature (book- or category-level) & \texttt{global\_signature} / \texttt{Category\_Means[...]} \\
\bottomrule
\end{tabular}
\end{center}

Every quantity above is carried on disk between notebooks as a \texttt{.npy}
(NumPy binary array) or \texttt{.json} (Python dict) artifact under
\texttt{data/xrf/output/processed/}, keyed by a page identifier such as
\texttt{page\_001}; the full lifecycle of each artifact is detailed per
notebook below.

\subsection{Notebook 01 --- Loading and Intensity Masking}

\subsubsection{Purpose and data lifecycle}

\paragraph{Load.} A fixed, manually enumerated list of TIFF file paths (one
per elemental channel, e.g.\ \texttt{Letter\_1\_Au\_La.tiff},
\texttt{Letter\_1\_Fe\_Ka.tiff}, \texttt{Letter\_1\_Cu\_Ka.tiff},
\texttt{Letter\_1\_Hg\_La.tiff}, \texttt{Letter\_1\_Pb\_La.tiff},
\texttt{Letter\_1\_As\_Ka.tiff}) is passed to
\texttt{Xrf\_Loader.Load\_Element\_Stack(File\_Paths, Dtype=config.Compute\_Dtype)}.
Internally, each file is read with \texttt{imageio.v3.imread}, cast to
\texttt{Dtype} (\texttt{float64} by default, per \texttt{Xrf\_Preprocessing\_Config}),
appended to a Python list \texttt{Layers}, and the list is stacked with
\texttt{np.stack(Layers, axis=-1)}, producing the data cube $S$ with shape
$(M,N,n)$ — the new axis is placed \emph{last}, so channel $k$ of pixel
$(i,j)$ is $S_{i,j,k}$, matching the notation table above.

\paragraph{Transform (intensity aggregation and thresholding).} The total
accumulated intensity per pixel is

$$
T(i,j) = \sum_{k=1}^{n} S_{i,j,k}
$$

computed in one call as \texttt{total\_intensity = np.sum(stack, axis=-1)},
reducing the last (channel) axis and leaving a 2D array of shape $(M,N)$. The
validity mask is a pointwise threshold test,

$$
B_{i,j} = \mathbb{1}\!\left[T(i,j) \geq \tau\right], \qquad \tau = \texttt{config.Noise\_Threshold} = 5.0,
$$

realized as the vectorized boolean comparison \texttt{mask = total\_intensity >= Tau\_Noise}
inside \texttt{Xrf\_Loader.Compute\_Intensity\_Mask}. The valid-pixel matrix is
then extracted by \emph{boolean fancy indexing on the leading two axes only}:

$$
x = S[B] \in \mathbb{R}^{N_{\text{valid}} \times n}, \qquad N_{\text{valid}} = \sum_{i,j} B_{i,j}.
$$

In code this is \texttt{Valid\_Pixels = Stack[Mask]}: because \texttt{Mask} has
shape $(M,N)$ matching the first two axes of \texttt{Stack}, NumPy collapses
those two axes into a single axis ordered by row-major (C-order) traversal of
the \texttt{True} entries of \texttt{Mask}, and keeps the trailing channel axis
intact — the result is a strictly 2D array of shape $(N_{\text{valid}}, n)$.
This exact row-major ordering is what later allows
\texttt{Spatial\_Analyzer.Reconstruct\_Class\_Map} (notebook 03) to invert the
operation and scatter a $(N_{\text{valid}},)$ label vector back into the
original $(M,N)$ pixel grid via \texttt{Class\_Map[Mask] = Labels}.

\paragraph{Rigor note: redundant computation.} The notebook calls
\texttt{Xrf\_Loader.Compute\_Intensity\_Mask} \emph{twice} — once immediately
after loading (to report shapes and save artifacts), and a second time after
plotting the total-intensity histogram (purely to reprint the retained-pixel
fraction). Both calls are mathematically identical and produce bit-identical
\texttt{mask}/\texttt{valid\_pixels} arrays; the corresponding
\texttt{np.save} calls are likewise executed twice with identical content.

\paragraph{Save.} \texttt{mask} (boolean, shape $(M,N)$) and
\texttt{valid\_pixels} (\texttt{float64}, shape $(N_{\text{valid}}, n)$) are
persisted with \texttt{np.save} to
\texttt{data/xrf/output/processed/page\_001\_mask.npy} and
\texttt{page\_001\_valid\_pixels.npy} respectively. No image compression or
metadata is attached; these are raw NumPy binary dumps, reloaded verbatim by
notebook 02 and by every later notebook that needs \texttt{mask} to
reconstruct a 2D map from a 1D label vector.

% ==============================================================================
% [NEW PLOT NEEDED: Total Intensity Histogram with Validity Threshold]
% Suggested Source: Inline matplotlib cell in `01_xrf_loading_and_masking.ipynb`
%   (plt.hist(total_intensity.ravel(), ...)); this plot is only ever shown via
%   plt.show(), never persisted to disk in the notebook as written.
% Plot Type: Histogram with a vertical threshold marker
% X-Axis: Label = "Accumulated Intensity T(p)", Range/Scale = [0, max(total_intensity)]
% Y-Axis: Label = "Frequency (Pixels)", Range/Scale = [0, auto]
% Data Series / Curves:
%   1. Histogram of total_intensity.ravel() over 50 bins (Color: Gray, filled bars, alpha=0.7)
%   2. Vertical dashed line at x = tau (Config.Noise_Threshold = 5.0) (Color: Red, dashed)
% Key Trend to Highlight: The fraction of pixels (reported in the console as
%   "Valid pixels retained: N_valid (percentage%)") that fall to the right of
%   the threshold line and are therefore retained as x for the CLR pipeline.
% ==============================================================================

\subsection{Notebook 02 --- Compositional Data Analysis: The Centered Log-Ratio Transform}

\subsubsection{Why a direct transform is invalid}

Each valid pixel's raw channel vector $x = (x_1,\dots,x_n)$, $x_i \geq 0$, is a
vector of counts, not an unconstrained Euclidean observation: only the
\emph{relative} proportions between channels carry compositional information,
and the vector is subject to an arbitrary, instrument-dependent overall scale.
Treating $x$ directly as a point in $\mathbb{R}^n$ for Euclidean-distance-based
methods (PCA, GMM) is invalid because the induced geometry does not respect
the simplex's constraint structure (the "closure problem"). The CLR transform
is applied in three explicit, code-verified sub-steps inside
\texttt{Clr\_Transformer.Apply\_Clr\_Transform}.

\subsubsection{Step 1: Closure to the simplex}

$$
y_i = \frac{x_i}{\sum_{j=1}^n x_j}, \qquad i = 1,\dots,n, \qquad \sum_{i=1}^n y_i = 1, \qquad y \in \Delta^{n-1}.
$$

Code: \texttt{Row\_Sums = np.sum(Valid\_Pixels, axis=1, keepdims=True)} computes
the row-wise (per-pixel) sum, keeping the result as a $(N_{\text{valid}}, 1)$
column so that the subsequent division
\texttt{Proportions = Valid\_Pixels / Row\_Sums} broadcasts correctly across
all $n$ columns without an explicit loop.

\subsubsection{Step 2: Zero replacement and renormalization}

The logarithm in Step 3 is undefined at $y_i = 0$, which occurs whenever an
element's raw signal is exactly zero at a pixel. A simple multiplicative
replacement is applied,

$$
y_i \leftarrow \delta \quad \text{wherever } y_i = 0, \qquad \delta = 10^{-4},
$$

implemented as the elementwise boolean-masked assignment
\texttt{Proportions[Proportions == 0.0] = Delta}. Because this replacement
breaks the unit-sum constraint ($\sum_i y_i$ is no longer exactly 1 after
substitution), the vector is renormalized a second time,

$$
y_i \leftarrow \frac{y_i}{\sum_{j=1}^n y_j},
$$

i.e.\ \texttt{Proportions = Proportions / np.sum(Proportions, axis=1, keepdims=True)},
restoring $y \in \Delta^{n-1}$ exactly before the logarithm is taken.

\subsubsection{Step 3: Centered Log-Ratio projection}

The CLR transform maps the (renormalized) proportion vector $y$ to
$z \in \mathbb{R}^n$ by

$$
z_i = \ln y_i - \frac{1}{n}\sum_{j=1}^n \ln y_j = \ln\!\left(\frac{y_i}{g(y)}\right), \qquad
g(y) = \left(\prod_{j=1}^n y_j\right)^{1/n}
$$

where $g(y)$ is the geometric mean of the composition. The identity
$\frac{1}{n}\sum_j \ln y_j = \ln g(y)$ is exactly why the code never computes
$g(y)$ directly: \texttt{Log\_Proportions = np.log(Proportions)} takes the
elementwise log first, \texttt{Geometric\_Mean = np.mean(Log\_Proportions, axis=1, keepdims=True)}
computes the row-wise arithmetic mean of the logs (which equals $\ln g(y)$ by
the identity above, without ever materializing $g(y)$ itself and thereby
avoiding a separate product-then-root computation that would be numerically
less stable), and \texttt{Clr\_Data = Log\_Proportions - Geometric\_Mean}
performs the subtraction, again broadcasting the $(N_{\text{valid}},1)$ mean
column across all $n$ output columns.

\paragraph{Rigor note: rank deficiency.} By construction,
$\sum_{i=1}^n z_i = \sum_i \ln y_i - n \cdot \frac{1}{n}\sum_j \ln y_j = 0$ for
every row. Consequently \texttt{clr\_data} does not occupy the full
$n$-dimensional Euclidean space: every row lies on the same
$(n-1)$-dimensional hyperplane $\{z : \sum_i z_i = 0\}$, so the covariance
matrix of \texttt{clr\_data} is rank-deficient with exactly one zero
eigenvalue. This directly explains why PCA in notebook 03 (below) is
well-posed and typically needs at most $n-1$ components to capture 100\% of
the variance.

\subsubsection{Data lifecycle for notebook 02}

\textbf{Load:} \texttt{valid\_pixels.npy} ($N_{\text{valid}} \times n$,
\texttt{float64}) from \texttt{data/xrf/output/processed/}.
\textbf{Transform:} the three sub-steps above, executed once via
\texttt{Clr\_Transformer.Apply\_Clr\_Transform(valid\_pixels, Delta=config.Zero\_Replacement\_Delta)}.
\textbf{Save:} \texttt{clr\_data} ($N_{\text{valid}} \times n$,
\texttt{float64}) written to \texttt{page\_001\_clr.npy} in the same processed
directory, to be consumed by notebook 03's PCA step.

% ==============================================================================
% [NEW PLOT NEEDED: Simplex vs. CLR Euclidean Space Comparison]
% Suggested Source: Inline matplotlib cell in `02_coda_transformations.ipynb`
%   (two-panel plt.subplots); not persisted to disk in the notebook as written.
% Plot Type: Side-by-side scatter plots (2 panels)
% X-Axis (left panel): Label = "Proportion Element 0 (y_1)", Range/Scale = [0, 1]
% Y-Axis (left panel): Label = "Proportion Element 1 (y_2)", Range/Scale = [0, 1]
% X-Axis (right panel): Label = "CLR Element 0 (z_1)", Range/Scale = [auto, symmetric around 0]
% Y-Axis (right panel): Label = "CLR Element 1 (z_2)", Range/Scale = [auto, symmetric around 0]
% Data Series / Curves:
%   1. Left: proportions[:, 0] vs proportions[:, 1], alpha=0.3, s=2, blue (default)
%   2. Right: clr_data[:, 0] vs clr_data[:, 1], alpha=0.3, s=2, orange
% Key Trend to Highlight: The left panel's points are visually compressed near
%   the simplex boundary/corner (channels 0-1 dominated by other channels),
%   while the right panel spreads the same pixels more symmetrically around
%   the origin in log-ratio space — the qualitative effect of removing closure.
% ==============================================================================

\subsection{Notebook 03 --- PCA Dimensionality Reduction and Probabilistic GMM Clustering}

\subsubsection{Step 1: PCA on the CLR coordinates}

\texttt{clr\_data} ($N_{\text{valid}} \times n$) is loaded and passed to
\texttt{Xrf\_Gmm\_Segmenter}, configured by \texttt{Xrf\_Segmentation\_Config}
(\texttt{Pca\_Variance\_Ratio=0.95}, \texttt{Gmm\_Min\_K=2},
\texttt{Gmm\_Max\_K=8}, \texttt{Covariance\_Type="full"}). Internally,
\texttt{sklearn.decomposition.PCA(n\_components=Variance\_Ratio, svd\_solver="full")}
first centers the data by subtracting the column means
$\bar z_i = \frac{1}{N_{\text{valid}}}\sum_p z_{p,i}$, forms the empirical
covariance

$$
\Sigma = \frac{1}{N_{\text{valid}}-1} \left(Z_c\right)^\top Z_c, \qquad Z_c = z - \bar z,
$$

and eigendecomposes it, $\Sigma v_j = \lambda_j v_j$, with eigenvalues sorted
$\lambda_1 \geq \lambda_2 \geq \cdots \geq \lambda_n \approx 0$ (the last
eigenvalue is $\approx 0$ precisely because of the rank-deficiency noted at
the end of notebook 02). Passing a \emph{float} `n\_components` in $(0,1]$
tells scikit-learn to automatically select the smallest $m$ such that the
cumulative explained-variance ratio meets the target,

$$
m = \min\left\{ m' : \frac{\sum_{j=1}^{m'} \lambda_j}{\sum_{j=1}^{n} \lambda_j} \geq \texttt{Variance\_Ratio} = 0.95 \right\},
$$

and the projected coordinates are $Z = Z_c V_m \in \mathbb{R}^{N_{\text{valid}} \times m}$,
computed in one call as \texttt{Z\_Data = Pca\_Model.fit\_transform(Clr\_Data)}.

\subsubsection{Step 2: Model-order selection via BIC}

\texttt{Xrf\_Gmm\_Segmenter.Compute\_Bic\_Curve(Clr\_Data, K\_Range, Variance\_Ratio)}
re-runs the PCA projection above once, then for every candidate
$K \in \{2,3,\dots,8\}$ fits a full-covariance multivariate Gaussian mixture
in the $m$-dimensional PCA space,

$$
p(z) = \sum_{k=1}^K \pi_k \, \mathcal{N}_m(Z \mid \mu_k, \Sigma_k), \qquad \mu_k \in \mathbb{R}^m, \ \Sigma_k \in \mathbb{R}^{m\times m} \text{ symmetric positive-definite},
$$

via \texttt{GaussianMixture(n\_components=K, random\_state=42).fit(Z\_Data)},
and records $\text{BIC}(K) = \texttt{Model.bic(Z\_Data)}$. For a full-covariance
$m$-dimensional mixture with $K$ components the parameter count is

$$
p_K = \underbrace{Km}_{\text{means}} + \underbrace{K\frac{m(m+1)}{2}}_{\text{full covariances}} + \underbrace{(K-1)}_{\text{weights}},
$$

so that $\text{BIC}(K) = -2\ln\hat L_K + p_K \ln N_{\text{valid}}$ — structurally
identical to the CT-side BIC formula, but with $p_K$ now scaling with the PCA
dimensionality $m$ rather than being fixed at $3K-1$ for a 1D mixture.

\paragraph{Rigor note: BIC curve is diagnostic-only in this run.} The notebook
plots $\text{BIC}(K)$ for $K=2,\dots,8$ but then sets
\texttt{optimal\_k = 8} by direct assignment (annotated in the notebook as "choose
the optimal $K$ visually") rather than programmatically taking
$\arg\min_K \text{BIC}(K)$. The BIC sweep is therefore evidence presented to a
human, not an automated decision in this notebook, in contrast to the CT
pipeline's \texttt{Gmm\_Fitter}, which does take the automated argmin.

\paragraph{Rigor note: covariance type is not threaded through the BIC sweep.}
\texttt{Compute\_Bic\_Curve}'s internal \texttt{GaussianMixture(n\_components=K, random\_state=42)}
call never passes \texttt{covariance\_type}, so every candidate $K$ in the BIC
curve is fit with scikit-learn's default \texttt{"full"} covariance
regardless of what \texttt{seg\_config.Covariance\_Type} is set to; only the
subsequent \texttt{Fit\_Predict} call (Step 3) actually honors the configured
value.

\subsubsection{Step 3: Final fit and posterior extraction}

With $K$ fixed at \texttt{optimal\_k}, \texttt{Xrf\_Gmm\_Segmenter.Fit\_Predict}
\emph{independently refits} a new PCA instance on \texttt{clr\_data} (not the
one used inside \texttt{Compute\_Bic\_Curve} — a duplicated but harmless
computation) and a new \texttt{GaussianMixture(n\_components=8, covariance\_type="full", random\_state=42)}
on the resulting $Z$, then extracts

$$
\ell_p = \arg\max_k \gamma_{p,k}, \qquad \gamma_{p,k} = P(\text{class}=k \mid Z_p),
$$

via \texttt{Gmm\_Model.predict(Z\_Data)} (hard labels, \texttt{labels}) and
\texttt{Gmm\_Model.predict\_proba(Z\_Data)} (posteriors, \texttt{probabilities}),
both indexed over the same $N_{\text{valid}}$ ordering established when
\texttt{valid\_pixels} was first extracted in notebook 01.

\subsubsection{Step 4: Spatial reconstruction to a 2D class map}

\texttt{Spatial\_Analyzer.Reconstruct\_Class\_Map(labels, mask)} inverts the
boolean-indexing flattening from notebook 01: it allocates
\texttt{Class\_Map = np.full(Mask.shape, Fill\_Value)} (default
\texttt{Fill\_Value=-1}, an $(M,N)$ integer array pre-filled with the
background sentinel), then performs the scatter assignment

$$
C_{i,j} = \ell_p \ \text{ for the } p\text{-th True entry of } B \text{ in row-major order}, \qquad C_{i,j} = -1 \text{ where } B_{i,j} = 0,
$$

i.e.\ \texttt{Class\_Map[Mask] = Labels} — valid precisely because boolean
assignment on the left-hand side traverses \texttt{True} positions in the same
row-major order that \texttt{Stack[Mask]} used to build \texttt{valid\_pixels}
(and hence \texttt{labels}) in the first place.

\subsubsection{Data lifecycle for notebook 03}

\textbf{Load:} \texttt{page\_001\_clr.npy} ($N_{\text{valid}}\times n$) and,
later in the same notebook, \texttt{page\_001\_mask.npy} ($M\times N$
boolean). \textbf{Transform:} PCA $\to$ BIC sweep (diagnostic) $\to$ final
$K=8$ GMM fit $\to$ \texttt{labels}, \texttt{probabilities} $\to$
\texttt{class\_map} via spatial reconstruction. \textbf{Save:}
\texttt{page\_001\_labels.npy} ($N_{\text{valid}}$, \texttt{int}),
\texttt{page\_001\_meta.json} (\texttt{\{"optimal\_k": 8\}}),
\texttt{page\_001\_class\_map.npy} ($M\times N$, \texttt{int}, from
\texttt{class\_map} before the float32/NaN conversion), plus a
\texttt{float32} TIFF export \texttt{Cluster\_Segmentation\_Map.tiff} (written
via \texttt{tifffile.imwrite} after \texttt{np.nan\_to\_num(class\_map, nan=-1.0)}
— a precautionary conversion that is largely redundant here since
\texttt{Reconstruct\_Class\_Map}'s default fill value is already the integer
\texttt{-1}, not \texttt{np.nan}), and, per class $k \in \{0,\dots,7\}$, a
binary Fiji-compatible mask TIFF (\texttt{Cluster\_\{k\}\_Fiji\_Mask.tiff},
values $\{0, 255\}$ from \texttt{(class\_map == k).astype(np.uint8) * 255})
and a colored visualization PNG (\texttt{Cluster\_\{k\}\_Visual.png}).

\paragraph{Rigor note: path inconsistency.} \texttt{Cluster\_Segmentation\_Map.tiff}
is written with a bare relative filename, i.e.\ to the notebook kernel's
current working directory, while every other artifact in the same notebook is
written explicitly under \texttt{PROCESSED\_DATA\_DIR} or \texttt{FIGURES\_DIR}
— an inconsistency in output location for that one file.

% ==============================================================================
% [NEW PLOT NEEDED: BIC Curve for XRF Compositional Classes]
% Suggested Source: Inline matplotlib cell in `03_gmm_spatial_clustering.ipynb`
%   using Xrf_Gmm_Segmenter.Compute_Bic_Curve output (bic_scores dict); shown
%   via plt.show() only, not persisted to disk in the notebook as written.
% Plot Type: Line chart with markers
% X-Axis: Label = "Number of Compositional Classes K", Range/Scale = [Gmm_Min_K=2 to Gmm_Max_K=8]
% Y-Axis: Label = "BIC Score (lower is better)", Range/Scale = [min(bic_scores) to max(bic_scores)]
% Data Series / Curves:
%   1. BIC(K) for K in {2,...,8} (Color: default matplotlib blue, marker='o')
% Key Trend to Highlight: Annotate the manually chosen K=8 even if it is not
%   the argmin, to make explicit that the final K was a visual/human choice
%   overriding (or confirming) the BIC-optimal value.
% ==============================================================================

% ==============================================================================
% [NEW PLOT NEEDED: Reconstructed XRF Class Map]
% Suggested Source: Inline matplotlib cell in `03_gmm_spatial_clustering.ipynb`
%   (ax.imshow(class_map, ...)); also separately exported per-class as
%   Cluster_k_Visual.png under data/xrf/output/figures/ (restricted, not
%   referenced directly per the figure-handling decision for this report).
% Plot Type: Discrete/categorical 2D heatmap with legend
% X-Axis: Label = "Pixel column"
% Y-Axis: Label = "Pixel row"
% Data Series / Curves:
%   1. class_map values in {-1, 0, ..., K-1}, discrete colormap ("tab10" truncated
%      to K colors), background (-1) shown in black via cmap.set_bad or explicit masking.
% Key Trend to Highlight: Spatial coherence (or lack thereof) of each
%   compositional class across the physical page layout, and which classes
%   plausibly correspond to ink strokes vs. substrate vs. background.
% ==============================================================================

\subsection{Notebook 04 --- Per-Page Leaf Signature Extraction ($F_h$)}

\subsubsection{Compositional abundances}

For a page with $N_{\text{valid}}$ labeled pixels and $K = \texttt{optimal\_k}$
classes, the abundance of class $k$ is its area fraction,

$$
A_k = \frac{1}{N_{\text{valid}}} \sum_{p=1}^{N_{\text{valid}}} \mathbb{1}[\ell_p = k], \qquad \sum_{k=0}^{K-1} A_k = 1,
$$

which is a valid compositional vector on the simplex $\Delta^{K-1}$ (a
partition of unity over the $K$ classes, since every valid pixel is assigned
to exactly one class by the $\arg\max$ decision rule in notebook 03).

\paragraph{Rigor note: implementation is a loop, not a vectorized reduction.}
\texttt{Leaf\_Signature\_Extractor.Compute\_Abundances} computes this with an
explicit \texttt{for K in range(Num\_Classes): Abundances[K] = np.sum(Labels == K) / Total\_Valid}
— mathematically equivalent to, but not implemented as, the single vectorized
call \texttt{np.bincount(Labels, minlength=Num\_Classes) / Total\_Valid}.

\subsubsection{Spatial (connected-component) descriptors}

For each class $k$, \texttt{Spatial\_Analyzer.Extract\_Spatial\_Descriptors(class\_map, Target\_Class=k, Min\_Size=10)}
first builds a binary indicator image
$D^{(k)}_{i,j} = \mathbb{1}[C_{i,j} = k]$ (\texttt{Binary\_Mask}), then applies
8-connected-component labeling via \texttt{scipy.ndimage.label} with an
explicit $3\times3$ all-ones structuring element,

$$
\text{Structure} = \begin{pmatrix} 1&1&1\\1&1&1\\1&1&1 \end{pmatrix},
$$

which assigns a unique positive integer $c$ to every maximal 8-connected
component of $D^{(k)}$ (0 reserved for background), producing
\texttt{Labeled\_Array} and \texttt{Num\_Features}. Component areas are
obtained in one vectorized pass,
$|\text{R}_c| = \texttt{np.bincount(Labeled\_Array.ravel())[1:]}$ (the `[1:]`
slice discards the background bin at index 0), and are filtered to
$\mathcal{R} = \{ c : |R_c| \geq \texttt{Min\_Size} = 10 \}$
(\texttt{Valid\_Areas}) via boolean array indexing. The two reported
descriptors are

$$
\text{Num\_Regiones}_k = |\mathcal{R}|, \qquad
\text{Tamano\_Promedio}_k = \frac{1}{|\mathcal{R}|}\sum_{c \in \mathcal{R}} |R_c|
$$

(zero for both if $\mathcal{R} = \emptyset$, guarded explicitly in code).

\subsubsection{Weighted multi-page aggregation (demonstrated, not yet real)}

\texttt{Leaf\_Signature\_Extractor.Compute\_Weighted\_Book\_Signature(Signatures, Weights)}
implements a general weighted mean over a stack of $H$ page signatures,
$\text{Signatures} \in \mathbb{R}^{H\times K}$:

$$
\bar F_k = \sum_{h=1}^H \tilde w_h \, \text{Signatures}_{h,k}, \qquad \tilde w_h = \frac{w_h}{\sum_{h'=1}^H w_{h'}}.
$$

Code first computes \texttt{Normalized\_Weights = Weights / np.sum(Weights)}
and then calls \texttt{np.average(Signatures, axis=0, weights=Normalized\_Weights)}
— which itself renormalizes its \texttt{weights} argument internally, so the
manual normalization is mathematically inert (harmless double normalization,
not a bug, since renormalizing an already-normalized weight vector is the
identity operation).

\paragraph{Rigor note: this call is exercised only on synthetic data here.}
In notebook 04, \texttt{Signatures} is \texttt{mock\_signatures = np.random.rand(5, optimal\_k)}
(5 fabricated pages) with illustrative weights \texttt{mock\_weights = [1.0, 0.8, 0.9, 0.2, 1.0]}
(page index 3, weight 0.2, is annotated in-notebook as "poor quality"). This
is a usage demonstration of the aggregation function only — it is not the
real book-level signature, and the resulting \texttt{book\_global\_signature.npy}
saved at the end of this notebook is therefore a synthetic-input artifact, to
be distinguished from the real per-category aggregation performed on genuine
multi-page data in notebook 06.

\subsubsection{Data lifecycle for notebook 04}

\textbf{Load:} \texttt{page\_001\_labels.npy}, \texttt{page\_001\_class\_map.npy},
\texttt{page\_001\_meta.json} (for \texttt{optimal\_k}).
\textbf{Transform:} \texttt{abundances} ($K$-vector) via \texttt{Compute\_Abundances};
\texttt{spatial\_features} (list of $K$ dicts) via \texttt{Extract\_Spatial\_Descriptors};
\texttt{global\_signature} ($K$-vector) via \texttt{Compute\_Weighted\_Book\_Signature}
on the synthetic mock inputs described above. \textbf{Save:} only
\texttt{global\_signature} is persisted, to
\texttt{data/xrf/output/book\_global\_signature.npy} (note: directly under
\texttt{OUTPUT\_DATA\_DIR}, not \texttt{PROCESSED\_DATA\_DIR}, unlike the
per-page artifacts from notebooks 01--03). \texttt{abundances} and
\texttt{spatial\_features} are computed and printed but not saved to disk in
this notebook — they are recomputed from scratch in notebooks 06 and 07 (see
below) rather than reloaded.

\subsection{Notebook 05 --- Page Categorization (Human-in-the-Loop Tagging)}

\subsubsection{Procedural steps (no numerical transform)}

This notebook performs metadata mutation and human interaction, not
mathematics; every step is stated explicitly for completeness since the
"no skipped steps" rigor requirement applies to procedure as well as math.

\begin{enumerate}[nosep]
    \item \textbf{Discovery:} \texttt{sorted(PROCESSED\_DATA\_DIR.glob("page\_*\_meta.json"))}
    enumerates every page for which notebook 03 has produced a metadata file,
    deriving each \texttt{Page\_Id} from the filename stem with
    \texttt{Meta\_Path.stem.replace("\_meta", "")}.
    \item \textbf{Read current tag:} \texttt{Category\_Registry.Load\_Page\_Category(Meta\_Path)}
    opens the JSON file and returns \texttt{Metadata.get("structural\_category")},
    i.e.\ \texttt{None} if the key is absent (untagged) or the previously
    written string otherwise.
    \item \textbf{Visual context:} for untagged pages whose
    \texttt{\{Page\_Id\}\_class\_map.npy} exists, it is loaded and displayed with
    \texttt{plt.imshow(Class\_Map, cmap="tab10")} to give the human tagger
    visual context before prompting.
    \item \textbf{Prompt and validate:} \texttt{input(...)} collects a free-text
    category string restricted, by convention, to
    \texttt{Xrf\_Comparison\_Config.Allowed\_Categories =}
    \texttt{["text\_only", "chapter\_start", "illustration", "mixed", "unknown"]}.
    \texttt{Category\_Registry.Write\_Page\_Category} calls
    \texttt{Category\_Registry.Validate\_Category\_Tag}, which raises
    \texttt{ValueError} if the string is not in the allowed vocabulary; the
    notebook catches this and skips the page with a message, leaving it
    untagged for a future pass.
    \item \textbf{Persist:} on success, \texttt{Update\_Page\_Metadata} loads
    the existing \texttt{meta.json} dict, merges in four new keys
    (\texttt{structural\_category}, \texttt{structural\_category\_source}
    \texttt{= "manual"}, \texttt{structural\_category\_secondary = []},
    \texttt{structural\_category\_notes = ""}) via a plain
    \texttt{dict.update}, and rewrites the whole JSON object back to the same
    file path — existing keys (e.g.\ \texttt{optimal\_k}) are preserved
    because they are not touched by the update.
    \item \textbf{Summary:} \texttt{Category\_Registry.List\_Tagged\_Pages}
    re-scans all metadata files, groups page ids into a
    \texttt{\{category: [page\_id,\ldots]\}} dictionary (untagged pages fall
    into an explicit \texttt{"untagged"} bucket), and flags any real category
    with fewer than \texttt{Min\_Pages\_Per\_Category = 5} tagged pages as
    "low-confidence" in the printed summary (a display-only flag; the pages
    themselves are still included in every downstream aggregation).
\end{enumerate}

\subsubsection{Data lifecycle for notebook 05}

\textbf{Load:} every \texttt{page\_*\_meta.json} and, opportunistically, the
matching \texttt{*\_class\_map.npy} for visual display only.
\textbf{Transform:} none numerical — a controlled-vocabulary string is
attached to each page's metadata. \textbf{Save:} the same
\texttt{page\_*\_meta.json} files are overwritten in place with the four new
\texttt{structural\_category*} fields merged in.

\subsection{Notebook 06 --- Category-Level Signature Comparison}

\subsubsection{Rebuilding per-page signatures from persisted primitives}

For every tagged page (untagged pages are explicitly skipped with a printed
warning), the notebook reloads \texttt{\{Page\_Id\}\_labels.npy} and
\texttt{\{Page\_Id\}\_class\_map.npy} and the page's \texttt{optimal\_k} from
its \texttt{meta.json}, then \emph{recomputes} both
$A^{(h)} = \texttt{Compute\_Abundances(Labels, Optimal\_K)}$ and the per-class
spatial descriptor dictionary via
\texttt{\{k: Extract\_Spatial\_Descriptors(Class\_Map, k, Min\_Size) for k in range(Optimal\_K)\}}
— rather than reloading any signature previously computed in notebook 04.
The only genuinely cross-notebook \emph{persisted} signal consumed here is the
\texttt{structural\_category} string written by notebook 05.

\paragraph{Rigor note: implicit equal-$K$ assumption across pages in a category.}
\texttt{Category\_Signature\_Aggregator.Aggregate\_By\_Category} groups all
$A^{(h)}$ vectors sharing a category into a Python list and then calls
\texttt{np.stack(Signatures, axis=0)} to form
$M_c \in \mathbb{R}^{H_c \times K}$. Since \texttt{optimal\_k} is chosen
manually per page in notebook 03, \texttt{np.stack} implicitly \emph{requires}
every page sharing a category to have been segmented with the identical $K$;
this is an assumption of the pipeline as written, not a value it checks or
enforces before stacking.

\subsubsection{Category mean signature and spread}

For a category $c$ with pages $h = 1,\dots,H_c$,

$$
\bar F_{c,k} = \frac{1}{H_c}\sum_{h=1}^{H_c} A^{(h)}_k
$$

is computed by calling \texttt{Compute\_Weighted\_Book\_Signature}
(Notebook 04's function, reused verbatim) with
\texttt{Uniform\_Weights = np.ones(H\_c)} — a uniform weighted mean reduces
exactly to the simple arithmetic mean, since $\tilde w_h = 1/H_c$ for all $h$.

Robust spread per class is the median absolute deviation,

$$
\text{med}_{c,k} = \operatorname{median}_h A^{(h)}_k, \qquad
\text{MAD}_{c,k} = \operatorname{median}_h \left| A^{(h)}_k - \text{med}_{c,k} \right|,
$$

via \texttt{Category\_Signature\_Aggregator.Compute\_Category\_Spread}, using
\texttt{np.median} twice (once for the per-class median, once for the median
of absolute deviations from it) — note this is the \emph{unscaled} MAD (no
multiplication by the usual $1.4826$ normal-consistency constant at this
stage; that scaling is applied later, in notebook 07, via the $0.6745$
constant, which is $\approx 1/1.4826$).

\subsubsection{Region-count aggregation (computed but not persisted)}

\texttt{Category\_Spatial\_Comparator.Aggregate\_Region\_Stats} groups the
per-page spatial descriptor dictionaries by category and, for every
class id $k$ observed in that category's pages, averages the two scalar
descriptors across pages:

$$
\overline{\text{Num\_Regiones}}_{c,k} = \frac{1}{|\{h : k \in \text{page } h\}|}\sum_h \text{Num\_Regiones}_{h,k}, \qquad
\overline{\text{Tamano\_Promedio}}_{c,k} \ \text{analogously.}
$$

\paragraph{Rigor note: this result is displayed but never saved to disk.} The
notebook cell simply evaluates \texttt{Category\_Region\_Stats} as its last
expression (Jupyter's automatic display), but no \texttt{np.save}/\texttt{json.dump}
call persists this dictionary anywhere; only the unrelated \texttt{config}
values are written into \texttt{category\_comparison\_summary.json} at the end
of the notebook.

\subsubsection{Data lifecycle for notebook 06}

\textbf{Load:} all tagged pages' \texttt{labels.npy}, \texttt{class\_map.npy},
\texttt{meta.json} (for \texttt{structural\_category} and \texttt{optimal\_k}).
\textbf{Transform:} per-page abundances and spatial descriptors (recomputed);
per-category mean signature, MAD spread, and mean region stats (aggregated).
\textbf{Save:} \texttt{category\_signature\_\{category\}.npy} and
\texttt{category\_spread\_\{category\}.npy} per category under
\texttt{data/xrf/output/comparison/}; two comparison figures (bar chart, radar
chart — see figure specs below); a best-effort illustrative montage per
category built from the shared \emph{book-level} \texttt{Cluster\_k\_Visual.png}
files (explicitly caveated in the notebook's own markdown as not yet a true
per-category set); and \texttt{category\_comparison\_summary.json}
(\texttt{page\_counts}, \texttt{low\_confidence\_categories}, and an echo of
the four relevant \texttt{Xrf\_Comparison\_Config} fields).

% ==============================================================================
% [NEW PLOT NEEDED: Category Signature Bar Chart]
% Suggested Source: `Plot_Category_Signature_Bars` (src/xrf/visualization/xrf_plots.py),
%   invoked in `06_category_signature_comparison.ipynb`; saved by the function
%   itself to data/xrf/output/comparison/category_signature_bars.png (restricted
%   path, not referenced directly here per the figure-handling decision).
% Plot Type: Grouped bar chart with error bars
% X-Axis: Label = "Compositional class (class_0 ... class_{K-1})"
% Y-Axis: Label = "Mean abundance", Range/Scale = [0, max bar height + error]
% Data Series / Curves:
%   1. One bar group per structural category, bar height = Category_Signatures[category][k]
%   2. Error bars = Category_Spread[category][k] (MAD), capsize=3
% Key Trend to Highlight: Classes where categories diverge most strongly in
%   mean abundance, and categories whose error bars are large relative to
%   their mean (indicating unreliable small-H_c estimates).
% ==============================================================================

% ==============================================================================
% [NEW PLOT NEEDED: Category Signature Radar Overlay]
% Suggested Source: `Plot_Category_Signature_Radar` (src/xrf/visualization/xrf_plots.py);
%   saved by the function itself to
%   data/xrf/output/comparison/category_signature_radar.png (restricted path).
% Plot Type: Polar/radar chart, one closed polygon per category
% Axes: K angular spokes at angles = linspace(0, 2*pi, K, endpoint=False), one per class
% Data Series / Curves:
%   1. One filled, semi-transparent (alpha=0.1) polygon line per category,
%      values = Category_Signatures[category] with the first value repeated
%      at the end to close the polygon
% Key Trend to Highlight: Overall "shape" differences between category
%   profiles (e.g. a category dominated by one or two classes vs. one with a
%   flat/uniform profile across classes).
% ==============================================================================

\subsection{Notebook 07 --- Rarity Review (Robust Outlier Triage)}

\subsubsection{Recomputation pattern (consistent with notebook 06)}

Exactly as in notebook 06, \texttt{Page\_Signatures} and \texttt{Page\_Categories}
are rebuilt from scratch by reloading each tagged page's \texttt{labels.npy}
and \texttt{meta.json} and recalling \texttt{Compute\_Abundances} — neither
notebook depends on the other's in-memory results, and the only artifact
truly shared across notebooks 05, 06, and 07 is the \texttt{structural\_category}
field persisted in each page's \texttt{meta.json}.

\subsubsection{Robust per-class deviation score}

For a page with signature $A^{(h)} \in \mathbb{R}^K$ tagged with category $c$,
the per-class robust deviation is

$$
z^{(h)}_k = 0.6745 \cdot \frac{A^{(h)}_k - \text{med}_{c,k}}{\text{MAD}_{c,k}}, \qquad k = 0,\dots,K-1,
$$

computed by \texttt{Rarity\_Scorer.Compute\_Robust\_Deviation}, where
$\text{med}_{c,k}$ and $\text{MAD}_{c,k}$ are exactly notebook 06's category
median/MAD (recomputed here via the same private grouping helper and
\texttt{Category\_Signature\_Aggregator.Compute\_Category\_Spread}). The
constant $0.6745 \approx 1/1.4826$ is the classical normal-consistency scale
factor for the MAD (i.e.\ for data drawn from $\mathcal{N}(\mu,\sigma^2)$,
$\mathbb{E}[\text{MAD}] \approx 0.6745\,\sigma$), which makes $z^{(h)}_k$ a
robust approximation to a standard z-score under an assumed unimodal, roughly
symmetric null distribution per class within a category — explicitly framed
in the code's own docstrings as a triage heuristic, not a formal hypothesis
test, since category groups can be small.

\paragraph{Guard clause.} If $\text{MAD}_{c,k} = 0$ for any class present in a
scored page's signature (which happens when every page currently in a small
category shares an identical value for that class), the division above is
undefined; \texttt{Compute\_Robust\_Deviation} raises \texttt{RuntimeError}
explicitly rather than silently producing \texttt{inf}/\texttt{nan}.

\subsubsection{Ranking rule}

Rather than combining the $K$ per-class deviations into a joint multivariate
statistic (e.g.\ a Mahalanobis-type distance), the pipeline reduces them to a
single scalar via the $L^\infty$ norm — the single worst-offending class
determines a page's overall rarity:

$$
d^{(h)} = \max_{k} \left| z^{(h)}_k \right|, \qquad
\text{Flagged}^{(h)} = \mathbb{1}\!\left[ d^{(h)} > \texttt{Rarity\_Mad\_Threshold} = 3.5 \right].
$$

\texttt{Rarity\_Scorer.Rank\_Pages\_By\_Rarity} returns the list of
$(\text{Page\_Id}, d^{(h)}, \text{Flagged}^{(h)})$ tuples sorted in descending
order of $d^{(h)}$, so the pages most likely to warrant expert review appear
first.

\subsubsection{Human review step}

For every flagged page, the notebook reloads and displays its persisted
\texttt{\{Page\_Id\}\_class\_map.npy} with \texttt{plt.imshow(..., cmap="tab10")}
so a human reviewer can visually inspect exactly which pixels drove the
statistical flag — this display is purely interactive and is not itself
saved to any file. A montage of flagged pages is then assembled from the
shared book-level \texttt{Cluster\_k\_Visual.png} files via
\texttt{Build\_Category\_Montage} (again explicitly caveated in the
notebook's markdown as illustrative, reusing the same book-level visuals as
notebook 06 rather than true per-page-flagged exports).

\subsubsection{Data lifecycle for notebook 07}

\textbf{Load:} all tagged pages' \texttt{labels.npy} and \texttt{meta.json};
for flagged pages only, their \texttt{class\_map.npy}; and the existing
\texttt{Cluster\_*\_Visual.png} files under \texttt{data/xrf/output/figures/}
for the montage step. \textbf{Transform:} per-page abundances (recomputed);
category median/MAD (recomputed); per-page deviation vectors and $L^\infty$
rarity score; ranking. \textbf{Save:} \texttt{rarity\_scores.json} (a list of
\texttt{\{"page\_id", "max\_abs\_deviation", "is\_flagged"\}} records, already
in ranked order) under \texttt{data/xrf/output/comparison/}, and
\texttt{flagged\_pages\_review\_montage.png} under
\texttt{data/xrf/output/comparison/montages/} if at least one page is flagged
and at least one \texttt{Cluster\_*\_Visual.png} exists.

% ==============================================================================
% [NEW PLOT NEEDED: Rarity Ranking with Threshold]
% Suggested Source: `Rarity_Scorer.Rank_Pages_By_Rarity` output, saved as
%   data/xrf/output/comparison/rarity_scores.json (restricted path — regenerate
%   the plot from this JSON rather than referencing any image directly).
% Plot Type: Horizontal lollipop/bar chart, sorted descending by d^(h)
% X-Axis: Label = "Max absolute robust deviation d^(h) = max_k |z_k^(h)|"
% Y-Axis: Label = "Page ID (ranked)"
% Data Series / Curves:
%   1. One marker/bar per page, colored by is_flagged (True/False)
%   2. Vertical reference line at x = Rarity_Mad_Threshold = 3.5
% Key Trend to Highlight: The small subset of pages above the threshold line,
%   annotated with their structural_category so a reviewer can see whether
%   flags cluster within a specific category (possible sign of a
%   too-small/too-tight category group) or are spread across categories.
% ==============================================================================
```

**Status: Phase 1 draft complete. Per the user's explicit sequencing instruction, stop here and wait for "Proceed to Phase 2" before drafting `microct_pipeline.tex`.**
