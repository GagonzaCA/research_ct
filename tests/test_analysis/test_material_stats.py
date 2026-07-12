"""Tests for material statistics computation."""

import numpy as np
from research_ct.analysis.material_stats import (
    Compute_Material_Statistics,
    Print_Material_Report,
)


def test_compute_stats_basic():
    """Should compute correct counts for simple labels."""
    Volume = np.array([
        [[10, 10], [20, 20]],
        [[10, 30], [20, 20]],
    ], dtype=np.float64)
    
    Labels = np.array([
        [[0, 0], [1, 1]],
        [[0, 2], [1, 1]],
    ])
    
    Stats = Compute_Material_Statistics(Volume, Labels, Num_Classes=3)
    
    assert Stats["num_classes"] == 3
    assert Stats["total_voxels"] == 8
    
    # Class 0: 3 voxels with values [10, 10, 10]
    Class_0 = [C for C in Stats["classes"] if C["class_id"] == 0][0]
    assert Class_0["voxel_count"] == 3
    assert Class_0["mean_intensity"] == 10.0
    
    # Class 1: 3 voxels with values [20, 20, 20]
    Class_1 = [C for C in Stats["classes"] if C["class_id"] == 1][0]
    assert Class_1["voxel_count"] == 3
    assert Class_1["mean_intensity"] == 20.0
    
    # Class 2: 1 voxel with value 30
    Class_2 = [C for C in Stats["classes"] if C["class_id"] == 2][0]
    assert Class_2["voxel_count"] == 1
    assert Class_2["mean_intensity"] == 30.0


def test_compute_stats_empty_class():
    """Should handle classes with zero voxels."""
    Volume = np.ones((2, 2, 2))
    Labels = np.zeros((2, 2, 2), dtype=int)
    
    Stats = Compute_Material_Statistics(Volume, Labels, Num_Classes=3)
    
    # Only class 0 should exist
    assert len(Stats["classes"]) == 1
    assert Stats["classes"][0]["class_id"] == 0


def test_compute_stats_volume_fraction():
    """Volume fractions should sum to 1."""
    Volume = np.random.rand(10, 10, 10) * 255
    Labels = np.random.randint(0, 3, (10, 10, 10))
    
    Stats = Compute_Material_Statistics(Volume, Labels, Num_Classes=3)
    
    Total_Fraction = sum(C["volume_fraction"] for C in Stats["classes"])
    np.testing.assert_allclose(Total_Fraction, 1.0, atol=1e-10)


def test_print_report_runs(capsys):
    """Should print without error."""
    Volume = np.ones((2, 2, 2))
    Labels = np.zeros((2, 2, 2), dtype=int)
    
    Stats = Compute_Material_Statistics(Volume, Labels, Num_Classes=1)
    
    Print_Material_Report(Stats)
    
    Captured = capsys.readouterr()
    assert "MATERIAL STATISTICS" in Captured.out