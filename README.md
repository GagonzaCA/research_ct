# Segmentation of Micro-CT Scanned Books

An unsupervised hierarchical GMM-HMRF pipeline to segment arbitrary materials in historical book scans.

## Setup Instructions
1. Initialize virtual environment: `python -m venv .venv`
2. Activate environment: `source .venv/bin/activate`
3. Install requirements: `pip install -r requirements.txt`
4. Install dpeendencies and package : `pip install -e .`

Once steps 3 and 4 are run, no need to repeat. Uninstall commands are not written , but can be search or be written in future. 

## Pipeline Execution
Place raw image stacks inside `data/raw/` and execute the notebooks realted. Notebooks are better for draft and error handling , testing function, files and libraries individualy

# Book Segmentation

Unsupervised material segmentation for micro-CT scans of sealed historical books.

## Structure

- `src/preprocessing/` — Contrast enhancement, anisotropic diffusion, diagnostics
- `src/segmentation/` — GMM fitting, hierarchical splitting, HMRF regularization
- `src/analysis/` — Material statistics, uncertainty quantification
- `src/visualization/` — 3D rendering with napari
- `notebooks/` — Interactive demos and parameter exploration
- `tests/` — pytest suite

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

