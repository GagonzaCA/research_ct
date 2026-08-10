# Notebooks

All interactive demos live in `notebooks/`.

## CT Notebooks

| File | Purpose |
| --- | --- |
| `01_explore_raw_data.ipynb` | Load raw TIFF, inspect histograms, metadata |
| `02_run_preprocessing.ipynb` | Run pipeline_revised, histogram diagnostics |
| `03_gmm_and_hierarchical_segmentation.ipynb` | BIC-GMM, Sparse Bayesian GMM, hierarchy, streaming export |
| `04_spatial_hmrf.ipynb` | HMRF on test region, GMM vs HMRF comparison |
| `05_uncertainty_and_visualization.ipynb` | Material stats, uncertainty maps, napari 3D, video export |

## XRF Notebooks

| File | Purpose |
| --- | --- |
| `01_xrf_loading_and_masking.ipynb` | Load elemental TIFFs, compute intensity mask |
| `02_coda_transformations.ipynb` | CLR transformation, zero replacement |
| `03_gmm_spatial_clustering.ipynb` | PCA reduction, GMM clustering, 2D class map |
| `04_leaf_signatures.ipynb` | Per-page leaf signature F_h computation |
| `05_page_categorization.ipynb` | Structural category assignment |
| `06_category_signature_comparison.ipynb` | Category-level compositional norms |
| `07_rarity_review.ipynb` | Robust z-score rarity flagging |
| `xrf_bcf_extraction.ipynb` | Bruker BCF hypercube to elemental TIFF extraction |

## View in docs site

Notebooks are rendered automatically by `mkdocs-jupyter` when the docs site is built.
