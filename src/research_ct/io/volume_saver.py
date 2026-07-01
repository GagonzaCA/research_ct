"""Additional volume export formats."""

import numpy as np
from pathlib import Path
from typing import Union


Path_Like = Union[str, Path]


def Save_As_Numpy(
    Volume: np.ndarray,
    File_Path: Path_Like,
) -> Path:
    """Save volume as compressed .npz file.
    
    Args:
        Volume: 3D array.
        File_Path: Output path with .npz extension.
    """
    File_Path = Path(File_Path)
    File_Path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(File_Path, volume=Volume)
    print(f"[Save_As_Numpy] Saved → {File_Path}")
    return File_Path

def Load_From_Numpy(File_Path: Path_Like) -> np.ndarray:
    """Load volume from .npz file.
    
    Args:
        File_Path: Path to .npz file.
    
    Returns:
        Volume array.
    """
    Data = np.load(File_Path)
    Volume = Data["volume"]
    print(f"[Load_From_Numpy] Loaded: {Volume.shape}")
    return Volume