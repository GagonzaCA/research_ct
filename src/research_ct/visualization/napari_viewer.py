"""Interactive 3D visualization with napari."""

import numpy as np
from typing import Optional, Dict, Any


def launch_napari_viewer(
    Volume: np.ndarray,
    Labels: Optional[np.ndarray] = None,
    Probabilities: Optional[np.ndarray] = None,
    Entropy: Optional[np.ndarray] = None,
    Probability_Threshold: float = 0.3,
    Render_3d: bool = False,
    Mesh_Surfaces: Optional[Dict[int, Dict[str, Any]]] = None,
    Surface_Opacity: float = 0.6,
    Title: str = "micro-CT Segmentation Results",
) -> Any:
    """Launch napari with volume and optional segmentation overlays.

    Args:
        Volume: Raw or preprocessed volume (D, H, W).
        Labels: Integer labels (D, H, W).
        Probabilities: Class probabilities (D, H, W, K).
        Entropy: Shannon entropy map (D, H, W) — added as semi-transparent heatmap.
        Probability_Threshold: Contrast lower limit for probability layers.
        Render_3d: If True, enable 3D rendering on launch.
        Mesh_Surfaces: Dict mapping class index to mesh dict with ``vertices``
            and ``faces`` keys.  Each mesh is added as a surface layer.
        Surface_Opacity: Opacity for surface layers (0.0–1.0).
        Title: Viewer window title.

    Returns:
        napari.Viewer instance (caller can add further layers after return).
    """
    import napari

    Viewer = napari.Viewer(title=Title)

    # --- Core volume -----------------------------------------------------------
    Viewer.add_image(Volume, name="Volume", colormap="gray")

    # --- Hard labels -----------------------------------------------------------
    if Labels is not None:
        Viewer.add_labels(Labels, name="Segmentation", opacity=0.6)

    # --- Probability layers (all classes) --------------------------------------
    if Probabilities is not None:
        K_Classes = Probabilities.shape[-1]
        for K in range(K_Classes):
            Viewer.add_image(
                Probabilities[..., K],
                name=f"P(class={K})",
                visible=False,
                colormap="magma",
                contrast_limits=(Probability_Threshold, 1.0),
                blending="additive",
            )

    # --- Entropy overlay (semi-transparent heatmap) ----------------------------
    if Entropy is not None:
        Entropy_Max = np.log(K_Classes) if Probabilities is not None else Entropy.max()
        Viewer.add_image(
            Entropy,
            name="Entropy (uncertainty)",
            colormap="hot",
            opacity=0.35,
            blending="additive",
            contrast_limits=(0.0, Entropy_Max),
        )

    # --- Surface meshes (3D reconstruction) ------------------------------------
    if Mesh_Surfaces is not None:
        # Pre-define class colors via matplotlib tab10
        try:
            import matplotlib.pyplot as plt

            Tab10 = plt.cm.tab10(np.linspace(0, 1, max(K_Classes, 1)))
        except Exception:  # noqa
            Tab10 = np.array(
                [
                    [0.12, 0.47, 0.71],
                    [1.00, 0.50, 0.05],
                    [0.17, 0.63, 0.17],
                    [0.84, 0.15, 0.16],
                    [0.58, 0.40, 0.74],
                ]
            )

        for Class_Idx, Mesh in Mesh_Surfaces.items():
            Vertices = Mesh.get("vertices")
            Faces = Mesh.get("faces")
            if Vertices is None or Faces is None or len(Vertices) == 0:
                continue

            Color = Tab10[Class_Idx % len(Tab10)][:3]
            Viewer.add_surface(
                (Vertices, Faces),
                name=f"Surface class {Class_Idx}",
                colormap=[tuple(Color.tolist())],
                opacity=Surface_Opacity,
                blending="translucent",
            )

    # --- 3D rendering mode -----------------------------------------------------
    if Render_3d:
        Viewer.dims.ndisplay = 3

    napari.run()
    return Viewer
