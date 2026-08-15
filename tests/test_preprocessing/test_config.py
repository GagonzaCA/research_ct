"""Tests for preprocessing configuration."""

import pytest
from research_ct.preprocessing.visual.config import Preprocessing_Config


def test_default_config():
    """Default config should have sensible values."""
    Config = Preprocessing_Config()
    
    assert Config.Diffusion_Iterations == 50
    assert Config.Diffusion_Kappa == 75.0
    assert Config.Diffusion_Gamma == 0.1
    assert Config.Saturation_Percentiles == (0.5, 99.5)


def test_preset_real_ct():
    """Real_Ct preset should set thresholding."""
    Config = Preprocessing_Config.From_Preset("Real_Ct")
    
    assert Config.Radius == 15
    assert Config.Threshold_Percentile == 85.0
    assert Config.Clahe_Clip == 0.1


def test_preset_gmm_ready():
    """Gmm_Ready preset should disable thresholding."""
    Config = Preprocessing_Config.From_Preset("Gmm_Ready")
    
    assert Config.Threshold_Percentile is None
    assert Config.Radius == 7


def test_preset_synthetic():
    """Synthetic preset should have low diffusion iterations."""
    Config = Preprocessing_Config.From_Preset("Synthetic")
    
    assert Config.Diffusion_Iterations == 10
    assert Config.Radius is None


def test_unknown_preset_raises():
    """Unknown preset should raise ValueError."""
    with pytest.raises(ValueError, match="Unknown preset"):
        Preprocessing_Config.From_Preset("Nonexistent")