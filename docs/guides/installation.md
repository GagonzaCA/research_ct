# Installation

## Requirements

- Python 3.10+
- Windows, macOS, or Linux
- 32 GB RAM minimum for CT pipeline (larger volumes use chunked processing)

## Setup from source

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/macOS

pip install -e .
pip install -r requirements.txt
```

## Documentation dependencies (optional)

```bash
pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-jupyter
```

## Verify installation

```bash
python -c "from research_ct.segmentation.gmm_fitter import Gmm_Fitter; print('CT OK')"
python -c "from xrf.io.xrf_loader import Xrf_Loader; print('XRF OK')"
pytest
```
