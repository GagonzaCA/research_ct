"""Export rendered outputs."""

import numpy as np
from pathlib import Path
from typing import Optional, Dict


def export_probability_video(
    Probabilities: np.ndarray,
    Output_Path: str,
    Class_Index: int = 0,
    Fps: int = 10,
) -> None:
    """Export probability map as video.
    
    Args:
        Probabilities: Shape (D, H, W, K).
        Output_Path: Output file path (.mp4 or .gif).
        Class_Index: Which class probability to visualize.
        Fps: Frames per second.
    """
    try:
        import imageio
    except ImportError:
        print("[export] imageio not available for video export")
        return
    
    Frames = (Probabilities[..., Class_Index] * 255).astype(np.uint8)
    
    Writer = imageio.get_writer(Output_Path, fps=Fps)
    
    for Z in range(Frames.shape[0]):
        Writer.append_data(Frames[Z])
    
    Writer.close()
    print(f"[export] Saved video → {Output_Path}")


def export_label_colors(
    Labels: np.ndarray,
    Output_Path: str,
    Color_Map: Optional[Dict[int, tuple]] = None,
) -> None:
    """Export colored label volume.
    
    Args:
        Labels: Integer labels (D, H, W).
        Output_Path: Output file path.
        Color_Map: Dict mapping label to (R, G, B).
    """
    if Color_Map is None:
        # Default colors
        Color_Map = {
            0: (0, 0, 0),       # Background/air
            1: (255, 228, 181), # Paper
            2: (47, 79, 79),    # Ink
            3: (139, 69, 19),   # Cover
        }
    
    D, H, W = Labels.shape
    Colored = np.zeros((D, H, W, 3), dtype=np.uint8)
    
    for Label, Color in Color_Map.items():
        Mask = Labels == Label
        Colored[Mask] = Color
    
    # Save as stack
    from .volume_saver import Save_Volume_As_Stack
    # Or use imageio for multi-page TIFF
    import imageio
    imageio.mimwrite(Output_Path, [Colored[i] for i in range(D)])