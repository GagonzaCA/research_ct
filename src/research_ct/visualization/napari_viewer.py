"""Interactive 3D visualization with napari."""

import numpy as np
from typing import  Optional

def launch_napari_viewer(
    Volume: np.ndarray,
    Labels: Optional[np.ndarray] = None,
    Probabilities: Optional[np.ndarray] = None,
) -> None:
    """Launch napari with volume and optional segmentation overlays.
    
    Args:
        Volume: Raw or preprocessed volume (D, H, W).
        Labels: Integer labels (D, H, W).
        Probabilities: Class probabilities (D, H, W, K).
    """
    import napari
    
    Viewer = napari.Viewer()
    
    # Add volume
    Viewer.add_image(Volume, name="Volume", colormap="gray")
    
    # Add labels
    if Labels is not None:
        Viewer.add_labels(Labels, name="Segmentation")
    
    # Add probability for first class as example
    if Probabilities is not None:
        for K in range(min(Probabilities.shape[3], 4)):  # Max 4 classes
            Viewer.add_image(
                Probabilities[..., K],
                name=f"P(class={K})",
                visible=False,
                colormap="magma",
            )
    
    napari.run()
