"""Tests for anisotropic diffusion."""

import numpy as np
import pytest
from research_ct.preprocessing.diffusion import Apply_Anisotropic_Diffusion


def test_diffusion_preserves_shape():
    """Output shape matches input."""
    Img = np.random.rand(64, 64) * 255
    Result = Apply_Anisotropic_Diffusion(Img, Num_Iterations=10)
    assert Result.shape == Img.shape


def test_diffusion_reduces_noise():
    """Diffusion should reduce variance in flat regions."""
    np.random.seed(42)
    Img = np.ones((32, 32)) * 128 + np.random.normal(0, 10, (32, 32))
    
    Result = Apply_Anisotropic_Diffusion(Img, Num_Iterations=50, Kappa=50)
    
    # Variance should decrease
    assert Result.std() < Img.std()


def test_diffusion_stability_check():
    """Should raise ValueError for unstable gamma."""
    Img = np.random.rand(32, 32)
    
    with pytest.raises(ValueError, match="stability limit"):
        Apply_Anisotropic_Diffusion(Img, Gamma=0.5)


def test_diffusion_modes():
    """Both conduction modes should run."""
    Img = np.random.rand(32, 32) * 255
    
    Result_1 = Apply_Anisotropic_Diffusion(Img, Num_Iterations=5, Conduction_Mode=1)
    Result_2 = Apply_Anisotropic_Diffusion(Img, Num_Iterations=5, Conduction_Mode=2)
    
    assert Result_1.shape == Img.shape
    assert Result_2.shape == Img.shape