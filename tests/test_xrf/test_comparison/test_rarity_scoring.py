"""Tests for xrf.comparison.rarity_scoring.Rarity_Scorer."""

import numpy as np
import pytest

from xrf.config import Xrf_Comparison_Config
from xrf.comparison.rarity_scoring import Rarity_Scorer


def test_compute_robust_deviation_matches_hand_computed_formula():
    Page_Signature = np.array([0.2, 0.8])
    Category_Median = np.array([0.35, 0.65])
    Category_Mad = np.array([0.10, 0.10])

    Deviation = Rarity_Scorer.Compute_Robust_Deviation(
        Page_Signature, Category_Median, Category_Mad
    )

    np.testing.assert_allclose(Deviation, [-1.01175, 1.01175], atol=1e-6)


def test_compute_robust_deviation_raises_on_zero_mad():
    Page_Signature = np.array([0.5, 0.5])
    Category_Median = np.array([0.5, 0.4])
    Category_Mad = np.array([0.1, 0.0])

    with pytest.raises(RuntimeError):
        Rarity_Scorer.Compute_Robust_Deviation(
            Page_Signature, Category_Median, Category_Mad
        )


def test_rank_pages_by_rarity_orders_descending_by_deviation(Page_Signatures, Page_Categories):
    Config = Xrf_Comparison_Config()
    Rankings = Rarity_Scorer.Rank_Pages_By_Rarity(Page_Signatures, Page_Categories, Config)

    Deviations = [Deviation for _, Deviation, _ in Rankings]
    assert Deviations == sorted(Deviations, reverse=True)

    assert Rankings[0][0] == "page_007"
    assert Rankings[0][1] == pytest.approx(1.68625, abs=1e-5)


def test_rank_pages_by_rarity_flags_above_threshold(Page_Signatures, Page_Categories):
    Config = Xrf_Comparison_Config(Rarity_Mad_Threshold=0.5)
    Rankings = Rarity_Scorer.Rank_Pages_By_Rarity(Page_Signatures, Page_Categories, Config)

    Flags = {Page_Id: Is_Flagged for Page_Id, _, Is_Flagged in Rankings}
    assert Flags["page_007"] is True
    assert Flags["page_001"] is True
    assert Flags["page_005"] is False


def test_rank_pages_by_rarity_no_flags_when_threshold_high(Page_Signatures, Page_Categories):
    Config = Xrf_Comparison_Config(Rarity_Mad_Threshold=3.5)
    Rankings = Rarity_Scorer.Rank_Pages_By_Rarity(Page_Signatures, Page_Categories, Config)

    assert all(Is_Flagged is False for _, _, Is_Flagged in Rankings)


def test_rank_pages_by_rarity_raises_on_missing_page(Page_Signatures):
    Config = Xrf_Comparison_Config()
    Bad_Categories = {"page_999": "text_only"}
    with pytest.raises(ValueError):
        Rarity_Scorer.Rank_Pages_By_Rarity(Page_Signatures, Bad_Categories, Config)
