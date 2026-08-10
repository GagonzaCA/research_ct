# CT Pipeline Guide

End-to-end walkthrough of the micro-CT segmentation pipeline.

## Overview

1. **Raw data loading** — TIFF stacks to 3D numpy array
2. **Preprocessing** — Background correction, Gaussian smoothing, Percentile normalization
3. **Segmentation** — Flat GMM (BIC), Hierarchical refinement, HMRF spatial regularization
4. **Analysis** — Material statistics, uncertainty maps, entropy, margin
5. **Export** — Labels, probabilities, napari, Dragonfly TIFF

## Notebooks

| Notebook | Purpose |
| --- | --- |
| `01_explore_raw_data.ipynb` | Inspect raw slices and histograms |
| `02_run_preprocessing.ipynb` | Run pipeline_revised, diagnostics |
| `03_gmm_and_hierarchical_segmentation.ipynb` | GMM fitting, BIC, hierarchy |
| `04_spatial_hmrf.ipynb` | HMRF parameter tuning |
| `05_uncertainty_and_visualization.ipynb` | Material stats, napari, exports |

See the interactive notebooks in the `notebooks/` directory.
