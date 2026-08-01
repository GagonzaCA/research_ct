"""Unit tests for Sparse Finite Bayesian GMM."""

import numpy as np
import pytest
from research_ct.segmentation.sparse_bayesian_gmm import Sparse_Bayesian_Gmm


def test_active_component_pruning(bimodal_data):
    """Should automatically prune unneeded components on simple bimodal data."""
    Model = Sparse_Bayesian_Gmm(Max_Components=8, Min_Samples=500)
    Model.Fit(bimodal_data, Verbose=False)

    # Expected to collapse from 8 down to roughly 2
    assert Model.Num_Active_Components < 8
    assert Model.Num_Active_Components >= 1


def test_probability_normalization(bimodal_data):
    """Active responsibilities must sum exactly to 1.0 across rows."""
    Model = Sparse_Bayesian_Gmm(Max_Components=5, Min_Samples=500)
    Model.Fit(bimodal_data, Verbose=False)

    Probabilities = Model.Predict_Probabilities(bimodal_data)
    Row_Sums = Probabilities.sum(axis=1)

    np.testing.assert_allclose(Row_Sums, 1.0, atol=1e-7)


def test_output_shapes(bimodal_data):
    """Probability and label arrays should match expected dynamic dimensions."""
    Model = Sparse_Bayesian_Gmm(Max_Components=5, Min_Samples=500)
    Model.Fit(bimodal_data, Verbose=False)

    Probabilities = Model.Predict_Probabilities(bimodal_data)
    Labels = Model.Predict_Labels(bimodal_data)

    N_Samples = len(bimodal_data)
    assert Probabilities.shape == (N_Samples, Model.Num_Active_Components)
    assert Labels.shape == (N_Samples,)
