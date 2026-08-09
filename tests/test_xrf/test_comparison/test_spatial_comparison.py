"""Tests for xrf.comparison.spatial_comparison.Category_Spatial_Comparator."""

import pytest

from xrf.comparison.spatial_comparison import Category_Spatial_Comparator


def test_aggregate_region_stats_matches_hand_computed_values(
    Page_Spatial_Descriptors, Page_Categories
):
    Filtered_Categories = {
        Page_Id: Category
        for Page_Id, Category in Page_Categories.items()
        if Page_Id in Page_Spatial_Descriptors
    }

    Stats = Category_Spatial_Comparator.Aggregate_Region_Stats(
        Page_Spatial_Descriptors, Filtered_Categories
    )

    assert set(Stats.keys()) == {"text_only", "illustration"}

    assert Stats["text_only"][0]["mean_region_count"] == pytest.approx(3.0)
    assert Stats["text_only"][0]["mean_region_size"] == pytest.approx(40.0)

    assert Stats["illustration"][0]["mean_region_count"] == pytest.approx(4.0 / 3.0)
    assert Stats["illustration"][0]["mean_region_size"] == pytest.approx(200.0)


def test_aggregate_region_stats_raises_on_missing_page(Page_Spatial_Descriptors):
    Bad_Categories = {"page_999": "text_only"}
    with pytest.raises(ValueError):
        Category_Spatial_Comparator.Aggregate_Region_Stats(
            Page_Spatial_Descriptors, Bad_Categories
        )
