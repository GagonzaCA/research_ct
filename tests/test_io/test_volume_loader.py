"""Tests for volume loading."""

import numpy as np
import pytest
from research_ct.io.volume_loader import Load_Slice_Stack, Save_Volume_As_Stack


def test_load_nonexistent_folder(tmp_path):
    """Should raise FileNotFoundError for empty folder."""
    with pytest.raises(FileNotFoundError):
        Load_Slice_Stack(tmp_path)


def test_save_and_load_roundtrip(tmp_path):
    """Save volume and reload should match."""
    Volume = np.random.rand(5, 32, 32) * 255
    
    Save_Volume_As_Stack(Volume, tmp_path, Prefix="test")
    
    Loaded = Load_Slice_Stack(tmp_path, Pattern="test_*.tiff")
    
    assert Loaded.shape == Volume.shape
    np.testing.assert_allclose(Loaded, Volume, rtol=0.02)  # uint8 precision


def test_load_shape_consistency(tmp_path):
    """All slices should have same shape."""
    import imageio.v3 as iio
    
    iio.imwrite(tmp_path / "slice_0000.tiff", np.zeros((32, 32), dtype=np.uint8))
    iio.imwrite(tmp_path / "slice_0001.tiff", np.zeros((64, 64), dtype=np.uint8))
    
    with pytest.raises(ValueError, match="Shape mismatch"):
        Load_Slice_Stack(tmp_path)