"""Shared pytest fixtures for the XRF comparison test suite."""

import json
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def Page_Signatures():
    """Synthetic per-page leaf signatures: 2 categories x 3-4 pages each.

    Hand-computable expected means/MADs (2-class abundance vectors).
    """
    return {
        "page_001": np.array([0.2, 0.8]),
        "page_002": np.array([0.3, 0.7]),
        "page_003": np.array([0.4, 0.6]),
        "page_004": np.array([0.9, 0.1]),
        "page_005": np.array([0.8, 0.2]),
        "page_006": np.array([0.7, 0.3]),
        "page_007": np.array([0.6, 0.4]),
    }


@pytest.fixture
def Page_Categories():
    """Category assignment matching Page_Signatures: 4 text_only, 3 illustration."""
    return {
        "page_001": "text_only",
        "page_002": "text_only",
        "page_003": "text_only",
        "page_004": "illustration",
        "page_005": "illustration",
        "page_006": "illustration",
        "page_007": "text_only",
    }


@pytest.fixture
def Page_Spatial_Descriptors():
    """Synthetic per-page Spatial_Analyzer.Extract_Spatial_Descriptors output.

    Keyed by page id, then by target class id, matching the real
    Spatial_Analyzer return schema ({"Num_Regiones", "Tamano_Promedio"}).
    """
    return {
        "page_001": {0: {"Num_Regiones": 2.0, "Tamano_Promedio": 50.0}},
        "page_002": {0: {"Num_Regiones": 3.0, "Tamano_Promedio": 40.0}},
        "page_003": {0: {"Num_Regiones": 4.0, "Tamano_Promedio": 30.0}},
        "page_004": {0: {"Num_Regiones": 1.0, "Tamano_Promedio": 200.0}},
        "page_005": {0: {"Num_Regiones": 2.0, "Tamano_Promedio": 180.0}},
        "page_006": {0: {"Num_Regiones": 1.0, "Tamano_Promedio": 220.0}},
    }


@pytest.fixture
def Temp_Meta_Path(tmp_path: Path) -> Path:
    """Create a temporary page_NNN_meta.json with minimal existing fields."""
    Meta_Path = tmp_path / "page_001_meta.json"
    Meta_Path.write_text(json.dumps({"optimal_k": 8}), encoding="utf-8")
    return Meta_Path
