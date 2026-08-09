"""Tests for xrf.comparison.category_signatures.Category_Signature_Aggregator."""

import numpy as np
import pytest

from xrf.comparison.category_signatures import Category_Signature_Aggregator


def test_aggregate_by_category_matches_hand_computed_means(Page_Signatures, Page_Categories):
    Means = Category_Signature_Aggregator.Aggregate_By_Category(
        Page_Signatures, Page_Categories
    )

    assert set(Means.keys()) == {"text_only", "illustration"}
    np.testing.assert_allclose(Means["text_only"], [0.375, 0.625])
    np.testing.assert_allclose(Means["illustration"], [0.8, 0.2])


def test_compute_category_spread_matches_hand_computed_mad(Page_Signatures, Page_Categories):
    Spread = Category_Signature_Aggregator.Compute_Category_Spread(
        Page_Signatures, Page_Categories
    )

    assert set(Spread.keys()) == {"text_only", "illustration"}
    np.testing.assert_allclose(Spread["text_only"], [0.10, 0.10])
    np.testing.assert_allclose(Spread["illustration"], [0.1, 0.1])


def test_aggregate_by_category_raises_on_missing_page(Page_Signatures):
    Bad_Categories = {"page_999": "text_only"}
    with pytest.raises(ValueError):
        Category_Signature_Aggregator.Aggregate_By_Category(Page_Signatures, Bad_Categories)


def test_compute_category_spread_raises_on_missing_page(Page_Signatures):
    Bad_Categories = {"page_999": "text_only"}
    with pytest.raises(ValueError):
        Category_Signature_Aggregator.Compute_Category_Spread(Page_Signatures, Bad_Categories)
