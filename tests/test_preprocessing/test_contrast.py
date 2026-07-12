"""Tests for contrast enhancement."""

"""Tests for contrast enhancement."""

import numpy as np
from research_ct.preprocessing.contrast import (
    Apply_White_Tophat,
    Apply_Clahe,
    Saturate_Percentiles,
    Enhance_Slice_Contrast,
)


def test_white_tophat_preserves_shape():
    """Output shape matches input."""
    Img = np.random.rand(64, 64) * 255
    Result = Apply_White_Tophat(Img, Radius=5)
    assert Result.shape == Img.shape


def test_clahe_output_range():
    """CLAHE output is in [0, 255]."""
    Img = np.random.rand(64, 64) * 100
    Result = Apply_Clahe(Img, Kernel_Size=(8, 8), Clip_Limit=0.1)
    assert Result.min() >= 0
    assert Result.max() <= 255


def test_saturate_percentiles_clips():
    """Extreme values should be clipped."""
    Img = np.array([0, 50, 100, 150, 200, 255], dtype=np.float64).reshape(2, 3)
    Result = Saturate_Percentiles(Img, Low_Percentile=10, High_Percentile=90)
    assert Result.min() >= 0
    assert Result.max() <= 255


def test_enhance_slice_contrast_runs():
    """Full pipeline should execute without error."""
    Img = np.random.rand(64, 64) * 255
    Result = Enhance_Slice_Contrast(
        Img,
        Radius=3,
        Clahe_Kernel=(8, 8),
        Clahe_Clip=0.1,
        Saturation_Percentiles=(1, 99),
    )
    assert Result.shape == Img.shape
    assert not np.isnan(Result).any()


def test_enhance_on_constant_image():
    """Constant image should not crash."""
    Img = np.ones((32, 32)) * 128
    Result = Enhance_Slice_Contrast(
        Img,
        Radius=3,
        Clahe_Kernel=(8, 8),
        Clahe_Clip=0.1,
        Saturation_Percentiles=(1, 99),
    )
    assert Result.shape == Img.shape