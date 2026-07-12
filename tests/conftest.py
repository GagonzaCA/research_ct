
"""Shared pytest fixtures."""

import numpy as np
import pytest


@pytest.fixture
def synthetic_volume():
    """Create a small synthetic volume for testing."""
    np.random.seed(42)
    D, H, W = 10, 64, 64
    
    Volume = np.zeros((D, H, W), dtype=np.float64)
    
    # Air region (dark)
    Volume[:2] = np.random.normal(20, 5, (2, H, W))
    
    # Paper region (medium)
    Volume[2:7] = np.random.normal(100, 15, (5, H, W))
    
    # Ink spots (bright)
    Ink_Mask = np.random.rand(5, H, W) < 0.05
    Volume[2:7][Ink_Mask] = np.random.normal(150, 10, Ink_Mask.sum())
    
    # Cover (brightest)
    Volume[7:] = np.random.normal(180, 20, (3, H, W))
    
    return np.clip(Volume, 0, 255)


@pytest.fixture
def flat_intensities():
    """1D array of intensities for GMM testing."""
    np.random.seed(42)
    
    Air = np.random.normal(30, 5, 1000)
    Paper = np.random.normal(100, 15, 5000)
    Ink = np.random.normal(150, 10, 500)
    Cover = np.random.normal(190, 20, 500)
    
    return np.concatenate([Air, Paper, Ink, Cover])


@pytest.fixture
def bimodal_data():
    """Data with two clear modes — should not split further."""
    np.random.seed(42)
    Mode_1 = np.random.normal(50, 5, 2000)
    Mode_2 = np.random.normal(150, 10, 3000)
    return np.concatenate([Mode_1, Mode_2]).reshape(-1, 1)


@pytest.fixture
def trimodal_data():
    """Data with three modes — hierarchy should find them."""
    np.random.seed(42)
    Mode_1 = np.random.normal(30, 5, 1000)
    Mode_2 = np.random.normal(100, 10, 2000)
    Mode_3 = np.random.normal(180, 15, 1500)
    return np.concatenate([Mode_1, Mode_2, Mode_3]).reshape(-1, 1)





