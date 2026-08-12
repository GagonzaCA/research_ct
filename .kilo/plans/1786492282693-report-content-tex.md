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
