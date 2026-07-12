"""Tests for diagnostic tools."""

import numpy as np
from research_ct.preprocessing.diagnostics import (
    Compute_Edge_Strength,
    Find_Book_Bounds,
    Find_Page_Peaks,
)


def test_edge_strength_shape():
    """Should return one score per slice."""
    Volume = np.random.rand(10, 32, 32) * 255
    Scores = Compute_Edge_Strength(Volume)
    
    assert len(Scores) == 10
    assert all(isinstance(s, float) for s in Scores)


def test_find_book_bounds():
    """Should detect book interior from edge strength."""
    # Simulate: low edges at start/end, high in middle
    Edge_Strength = [1, 2, 5, 8, 9, 8, 5, 2, 1, 0]
    
    Start, End = Find_Book_Bounds(Edge_Strength, Threshold_Ratio=0.3)
    
    assert Start < End
    assert Start >= 0
    assert End < len(Edge_Strength)


def test_find_page_peaks():
    """Should detect peaks in edge profile."""
    # Create periodic peaks
    Edge_Strength = [1, 3, 1, 3, 1, 3, 1, 3, 1, 3]
    
    Peaks = Find_Page_Peaks(
        Edge_Strength,
        Book_Start=0,
        Book_End=9,
        Min_Distance=2,
        Min_Prominence=1.0,
    )
    
    assert len(Peaks) > 0
    assert all(0 <= p < 10 for p in Peaks)


def test_find_page_peaks_with_expected():
    """Should adapt to expected page count."""
    Edge_Strength = [1, 5, 1, 5, 1, 5, 1, 5, 1, 5]
    
    Peaks = Find_Page_Peaks(
        Edge_Strength,
        Book_Start=0,
        Book_End=9,
        Min_Distance=2,
        Min_Prominence=2.0,
        Expected_Pages=4,
    )
    
    assert len(Peaks) >= 2