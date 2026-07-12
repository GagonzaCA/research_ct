"""Material statistics computation."""

import numpy as np
from typing import Dict, List, Tuple


def Compute_Material_Statistics(
    Volume: np.ndarray,
    Labels: np.ndarray,
    Num_Classes: int,
) -> Dict[str, any]:
    """Compute statistics per material class.
    
    Args:
        Volume: Preprocessed volume (D, H, W).
        Labels: Integer label array (D, H, W).
        Num_Classes: Total number of classes.
    
    Returns:
        Dictionary with per-class and global statistics.
    """
    Total_Voxels = Volume.size
    
    Stats = {
        "num_classes": Num_Classes,
        "total_voxels": Total_Voxels,
        "classes": [],
    }
    
    for K in range(Num_Classes):
        Mask = Labels == K
        Count = Mask.sum()
        
        if Count == 0:
            continue
        
        Class_Voxels = Volume[Mask]
        
        Class_Stats = {
            "class_id": K,
            "voxel_count": int(Count),
            "volume_fraction": float(Count / Total_Voxels),
            "mean_intensity": float(Class_Voxels.mean()),
            "std_intensity": float(Class_Voxels.std()),
            "min_intensity": float(Class_Voxels.min()),
            "max_intensity": float(Class_Voxels.max()),
        }
        
        Stats["classes"].append(Class_Stats)
    
    # Global
    Stats["global_mean"] = float(Volume.mean())
    Stats["global_std"] = float(Volume.std())
    
    return Stats


def Print_Material_Report(Stats: Dict) -> None:
    """Print formatted material statistics to console.
    
    Args:
        Stats: Output from Compute_Material_Statistics.
    """
    print("\n" + "=" * 60)
    print("MATERIAL STATISTICS")
    print("=" * 60)
    print(f"Total voxels: {Stats['total_voxels']:,}")
    print(f"Global mean: {Stats['global_mean']:.2f}")
    print(f"Global std: {Stats['global_std']:.2f}")
    print("-" * 60)
    print(f"{'Class':<8} {'Count':<12} {'Fraction':<12} {'Mean':<10} {'Std':<10}")
    print("-" * 60)
    
    for C in Stats["classes"]:
        print(
            f"{C['class_id']:<8} "
            f"{C['voxel_count']:<12,} "
            f"{C['volume_fraction']:<12.4f} "
            f"{C['mean_intensity']:<10.2f} "
            f"{C['std_intensity']:<10.2f}"
        )
    
    print("=" * 60)