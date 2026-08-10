# Research CT — Book Segmentation

Unsupervised material segmentation for micro-CT and XRF scans of sealed historical books.

Two independent pipelines:

- **`research_ct`** — hierarchical GMM + HMRF pipeline that segments micro-CT volumes into material classes (air, paper, ink, cover, adhesive) without labeled training data.
- **`xrf`** — X-Ray Fluorescence elemental analysis pipeline (BCF extraction → CLR transform → PCA+GMM clustering → per-page leaf signatures → category comparison).

Full documentation (guides + auto-generated API reference) lives in `docs/` and is built with MkDocs — see [Documentation](#documentation) below.

## Installation

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install the package in editable mode
pip install -e .

# Install runtime + dev dependencies
pip install -r requirements.txt
```

Steps only need to be run once per environment.

### Verify installation

```bash
python -c "from research_ct.segmentation.gmm_fitter import Gmm_Fitter; print('CT OK')"
python -c "from xrf.io.xrf_loader import Xrf_Loader; print('XRF OK')"
pytest
```

## Pipeline Execution

Place raw CT TIFF stacks inside `data/raw/` and raw XRF elemental TIFFs inside `data/xrf/raw/` (or `.bcf` files inside `data/xrf/bcf/`), then run the notebooks in order. Notebooks are the primary way to run and debug the pipelines — they isolate each step for testing functions, files, and libraries individually.

| Notebook | Purpose |
| --- | --- |
| `01_explore_raw_data.ipynb` | Load raw TIFF, inspect histograms, metadata |
| `02_run_preprocessing.ipynb` | Run preprocessing pipeline, histogram diagnostics |
| `03_gmm_and_hierarchical_segmentation.ipynb` | BIC-GMM, Sparse Bayesian GMM, hierarchy, streaming export |
| `04_spatial_hmrf.ipynb` | HMRF on test region, GMM vs HMRF comparison |
| `05_uncertainty_and_visualization.ipynb` | Material stats, uncertainty maps, napari 3D, video export |

XRF notebooks live in `notebooks/xrf/` (`01_xrf_loading_and_masking.ipynb` → `07_rarity_review.ipynb`, plus `xrf_bcf_extraction.ipynb`). See `docs/guides/notebooks.md` for the full table.

## Structure

```
src/research_ct/
├── io/               volume_loader.py, volume_saver.py, metadata_parser.py, dragonfly_exporter.py
├── preprocessing/    config.py, pipeline_revised.py, background_correction.py, noise_reduction.py,
│                     global_normalization.py, histogram_diagnostics.py, contrast.py, diffusion.py
├── processing/       dragonfly_utils.py
├── segmentation/     gmm_fitter.py, sparse_bayesian_gmm.py, hierarchy.py, hmrf.py, decision_engine.py
├── analysis/         material_stats.py, uncertainty_maps.py, page_extractor.py
└── visualization/    napari_viewer.py, plot_distributions.py, export.py, histogram_diagnostics_viewer.py

src/xrf/
├── config.py
├── io/               xrf_loader.py
├── preprocessing/    bcf_extractor.py
├── segmentation/     xrf_gmm.py
├── transforms/       coda.py
├── spatial/          spatial_analyzer.py
├── signatures/       leaf_signature.py
├── comparison/       category_registry.py, category_signatures.py, rarity_scoring.py, spatial_comparison.py
└── fusion/           ct_xrf_fusion.py   (placeholder — not yet implemented)

notebooks/            CT notebooks (01-05) + notebooks/xrf/ (XRF notebooks)
tests/                pytest suite: test_io/, test_preprocessing/, test_segmentation/, test_analysis/, test_xrf/
docs/                 MkDocs site (guides + auto-generated API reference)
data/                 raw/, processed/, output/, xrf/  (all git-ignored except .gitkeep)
```

## Documentation

Full guides and auto-generated API reference are built with [MkDocs](https://www.mkdocs.org/):

```bash
pip install -e ".[docs]"    # or: pip install -r requirements.txt

mkdocs serve                # live preview at http://127.0.0.1:8000
mkdocs build                # build static site into site/
```

API reference pages (`docs/api/research_ct.md`, `docs/api/xrf.md`) pull directly from source docstrings via `mkdocstrings`, so they stay in sync with the code automatically.

## Testing

```bash
pytest                # run full suite
pytest --cov          # with coverage report
black src/ tests/     # format
mypy src/             # type check
```

## License

MIT — see `docs/license.md`.
