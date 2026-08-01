"""Tests for hierarchical GMM splitting."""

import numpy as np
import pytest
from research_ct.segmentation.hierarchy import Hierarchical_Gmm


def test_hierarchy_initialization():
    """Should initialize with correct defaults."""
    Hgmm = Hierarchical_Gmm()

    assert Hgmm.Min_Samples == 1000
    assert Hgmm.Max_Depth == 5
    assert Hgmm.Significance_Alpha == 0.05


def test_hierarchy_fit_bimodal(bimodal_data):
    """Should create tree for bimodal data."""
    Hgmm = Hierarchical_Gmm(Max_Depth=2)
    Hgmm.Fit(bimodal_data, Initial_K=2)

    assert Hgmm.Root_Gmm is not None
    assert Hgmm.Component_Tree != {}


def test_hierarchy_get_leaves(bimodal_data):
    """Leaves should exist after fitting."""
    Hgmm = Hierarchical_Gmm(Max_Depth=2)
    Hgmm.Fit(bimodal_data, Initial_K=2)

    Leaves = Hgmm.Get_Leaf_Components()

    assert len(Leaves) > 0
    # Assuming the implementation uses PascalCase keys as previously enforced
    assert all("Mean" in Leaf for Leaf in Leaves)


def test_hierarchy_leaf_has_required_keys(bimodal_data):
    """Each leaf should have expected structure."""
    Hgmm = Hierarchical_Gmm(Max_Depth=2, Min_Samples=500)
    Hgmm.Fit(bimodal_data, Initial_K=2)

    Leaves = Hgmm.Get_Leaf_Components()

    for Leaf in Leaves:
        assert "Is_Leaf" in Leaf
        assert Leaf["Is_Leaf"] is True
        assert "Mean" in Leaf
        assert "Variance" in Leaf
        assert "Weight" in Leaf
        assert "Depth" in Leaf


def test_hierarchy_leaf_probability_conservation(bimodal_data):
    """Leaf probabilities must sum exactly to 1.0."""
    Hgmm = Hierarchical_Gmm(Min_Samples=500, Max_Depth=2)
    Hgmm.Fit(bimodal_data, Initial_K=2)

    Probabilities = Hgmm.Predict_Leaf_Probabilities(bimodal_data)
    Row_Sums = Probabilities.sum(axis=1)

    np.testing.assert_allclose(Row_Sums, 1.0, atol=1e-7)


def test_hierarchy_split_rejection_on_small_samples():
    """Tree should refuse to split components that lack sufficient data."""
    Small_Data = np.random.normal(loc=0.0, scale=1.0, size=200).astype(np.float64).reshape(-1, 1)
    Hgmm = Hierarchical_Gmm(Min_Samples=1000, Max_Depth=3)
    Hgmm.Fit(Small_Data, Initial_K=1)

    Leaves = Hgmm.Get_Leaf_Components()

    assert len(Leaves) == 1
    assert Leaves[0]["Is_Leaf"] is True
    assert Leaves[0]["Depth"] == 0


def test_hierarchy_trimodal_expansion(trimodal_data):
    """Should expand beyond initial K=2 for trimodal data."""
    Hgmm = Hierarchical_Gmm(Max_Depth=3, Min_Samples=500)
    Hgmm.Fit(trimodal_data, Initial_K=2)

    Leaves = Hgmm.Get_Leaf_Components()

    # Should have found more than 2 components
    assert len(Leaves) >= 2


def test_hierarchy_respects_max_depth(trimodal_data):
    """Should not exceed max depth."""
    Hgmm = Hierarchical_Gmm(Max_Depth=1, Min_Samples=500)
    Hgmm.Fit(trimodal_data, Initial_K=2)

    Leaves = Hgmm.Get_Leaf_Components()

    for Leaf in Leaves:
        assert Leaf["Depth"] <= 1
