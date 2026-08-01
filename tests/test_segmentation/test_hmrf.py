"""Unit tests for spatial regularisation with HMRF."""

import numpy as np
import pytest
from research_ct.segmentation.hmrf import Hmrf_Segmenter


def test_hmrf_execution_and_shape():
    """Should return correctly shaped 3D integer label array."""
    np.random.seed(42)
    D, H, W, K = 10, 10, 10, 3
    Log_Probs = np.random.randn(D, H, W, K).astype(np.float64)

    Segmenter = Hmrf_Segmenter(Beta=0.5, Max_Iterations=3)
    Labels = Segmenter.Fit(Log_Probs)

    assert Labels.shape == (D, H, W)
    assert Labels.dtype == np.int32


def test_smoothing_effect():
    """Spatial regularisation MUST decrease total neighborhood label disagreements."""
    D, H, W, K = 12, 12, 12, 2
    Log_Probs = np.zeros((D, H, W, K), dtype=np.float64)

    # Base state: favor Class 0
    Log_Probs[..., 0] = -0.1
    Log_Probs[..., 1] = -1.0

    # Insert a cube preferring Class 1
    Log_Probs[4:8, 4:8, 4:8, 0] = -1.0
    Log_Probs[4:8, 4:8, 4:8, 1] = -0.1

    # Corrupt volume with random Gaussian noise (simulate CT speckles)
    np.random.seed(42)
    Log_Probs += np.random.normal(0, 0.4, Log_Probs.shape)

    Map_Labels = np.argmax(Log_Probs, axis=3).astype(np.int32)

    Segmenter = Hmrf_Segmenter(Beta=1.5, Max_Iterations=10)
    Hmrf_Labels = Segmenter.Fit(Log_Probs)

    def Count_Disagreements(Volume: np.ndarray) -> int:
        """Calculate total number of non-matching adjacent voxels."""
        Disagreements = 0
        for Dz, Dy, Dx in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
            Shifted = np.roll(Volume, shift=(Dz, Dy, Dx), axis=(0, 1, 2))
            Disagreements += np.sum(Volume != Shifted)
        return Disagreements

    Map_Errors = Count_Disagreements(Map_Labels)
    Hmrf_Errors = Count_Disagreements(Hmrf_Labels)

    assert Hmrf_Errors < Map_Errors
