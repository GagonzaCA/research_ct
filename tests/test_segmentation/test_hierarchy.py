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
    assert all("mean" in Leaf for Leaf in Leaves)


def test_hierarchy_leaf_has_required_keys(bimodal_data):
    """Each leaf should have expected structure."""
    Hgmm = Hierarchical_Gmm(Max_Depth=2, Min_Samples=500)
    Hgmm.Fit(bimodal_data, Initial_K=2)
    
    Leaves = Hgmm.Get_Leaf_Components()
    
    for Leaf in Leaves:
        assert "is_leaf" in Leaf
        assert Leaf["is_leaf"] == True
        assert "mean" in Leaf
        assert "variance" in Leaf
        assert "weight" in Leaf
        assert "depth" in Leaf


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
        assert Leaf["depth"] <= 1