"""Tests for metadata inference."""

import numpy as np
from research_ct.io.metadata_parser import Load_Metadata, Scan_Metadata


def test_load_metadata_default():
    """Should infer from uint16 volume."""
    Volume = np.random.randint(0, 65535, (50, 64, 64), dtype=np.uint16)
    
    Meta = Load_Metadata(Volume)
    
    assert Meta.Volume_Shape == (50, 64, 64)
    assert Meta.Bit_Depth == 16
    assert Meta.Intensity_Range[0] >= 0
    assert Meta.Intensity_Range[1] <= 65535
    assert Meta.Scanner_Model == "Unknown"


def test_load_metadata_uint8():
    """Should detect 8-bit depth."""
    Volume = np.random.randint(0, 255, (10, 32, 32), dtype=np.uint8)
    
    Meta = Load_Metadata(Volume)
    
    assert Meta.Bit_Depth == 8
    assert Meta.Intensity_Range[1] == 255.0


def test_load_metadata_with_pages():
    """Should accept manual page count."""
    Volume = np.zeros((100, 64, 64), dtype=np.uint16)
    
    Meta = Load_Metadata(Volume, Num_Pages=200)
    
    assert Meta.Num_Pages == 200


def test_load_metadata_voxel_size():
    """Should accept voxel size override."""
    Volume = np.zeros((10, 32, 32), dtype=np.float32)
    
    Meta = Load_Metadata(Volume, Voxel_Size_Um=40.0)
    
    assert Meta.Voxel_Size_Um == (40.0, 40.0, 40.0)