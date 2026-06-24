# Segmentation of Micro-CT Scanned Books

An unsupervised hierarchical GMM-HMRF pipeline to segment arbitrary materials in historical book scans.

## Setup Instructions
1. Initialize virtual environment: `python -m venv .venv`
2. Activate environment: `source .venv/bin/activate`
3. Install requirements: `pip install -r requirements.txt`

## Pipeline Execution
Place raw image stacks inside `data/raw/` and execute the master wrapper:
```bash
python main.py --input data/raw/reco_stack --run-preprocessing

