"""Tests for GMM fitting."""

import numpy as np
import pytest
from research_ct.segmentation.gmm_fitter import Gmm_Fitter


def test_gmm_fitter_initialization():
    """Gmm_Fitter should initialize with correct defaults."""
    Fitter = Gmm_Fitter()
    
    assert Fitter.Min_Components == 1
    assert Fitter.Max_Components == 10
    assert Fitter.Covariance_Type == "full"
    assert Fitter.Model is None


def test_gmm_fit_on_multimodal_data(flat_intensities):
    """Should find multiple components for multimodal data."""
    Fitter = Gmm_Fitter(Min_Components=2, Max_Components=6)
    Fitter.Fit(flat_intensities, Verbose=False)
    
    assert Fitter.Model is not None
    assert Fitter.Num_Components is not None
    assert Fitter.Num_Components >= 2
    assert len(Fitter.Bic_Scores) == 5  # K=2,3,4,5,6


def test_gmm_predict_labels(flat_intensities):
    """Predictions should match input shape."""
    Fitter = Gmm_Fitter(Min_Components=2, Max_Components=4)
    Fitter.Fit(flat_intensities, Verbose=False)
    
    Labels = Fitter.Predict_Labels(flat_intensities)
    
    assert Labels.shape == (flat_intensities.shape[0],)
    assert len(np.unique(Labels)) == Fitter.Num_Components


def test_gmm_predict_probabilities(flat_intensities):
    """Probabilities should sum to 1."""
    Fitter = Gmm_Fitter(Min_Components=2, Max_Components=4)
    Fitter.Fit(flat_intensities, Verbose=False)
    
    Probs = Fitter.Predict_Probabilities(flat_intensities)
    
    assert Probs.shape == (flat_intensities.shape[0], Fitter.Num_Components)
    np.testing.assert_allclose(Probs.sum(axis=1), 1.0, atol=1e-6)


def test_gmm_get_statistics(flat_intensities):
    """Statistics should have correct keys and shapes."""
    Fitter = Gmm_Fitter(Min_Components=2, Max_Components=4)
    Fitter.Fit(flat_intensities, Verbose=False)
    
    Stats = Fitter.Get_Material_Statistics()
    
    assert "Means" in Stats
    assert "Variances" in Stats
    assert "Weights" in Stats
    assert len(Stats["Means"]) == Fitter.Num_Components
    np.testing.assert_allclose(Stats["Weights"].sum(), 1.0, atol=1e-6)


def test_gmm_not_fitted_error():
    """Should raise RuntimeError if methods called before Fit."""
    Fitter = Gmm_Fitter()
    
    Dummy_Data = np.array([1, 2, 3])
    
    with pytest.raises(RuntimeError):
        Fitter.Predict_Labels(Dummy_Data)
    
    with pytest.raises(RuntimeError):
        Fitter.Predict_Probabilities(Dummy_Data)
    
    with pytest.raises(RuntimeError):
        Fitter.Get_Material_Statistics()