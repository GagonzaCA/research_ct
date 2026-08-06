#!/usr/bin/env python
"""Generate notebook 05_uncertainty_and_visualization.ipynb.

Run from the project root:

    python scripts/generate_notebook_05.py

This rebuilds the complete notebook including interactive probability
thresholding, rare-region isolation, 3D mesh reconstruction via
marching-cubes + napari surface layers, uncertainty diagnostics,
and conclusion tables/plots.

Two export cells are marked [TO FIX] — paste your corrected code
there before running.
"""

from __future__ import annotations

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _md(source_lines: list[str]) -> dict:
    """Create a markdown cell."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source_lines[:-1]]
        + [source_lines[-1]],
    }


def _code(source_lines: list[str]) -> dict:
    """Create a code cell (no outputs)."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [line + "\n" for line in source_lines[:-1]]
        + [source_lines[-1]],
        "outputs": [],
    }


# ---------------------------------------------------------------------------
# Cell definitions
# ---------------------------------------------------------------------------

CELLS: list[dict] = []

# ---- 1. Title ----------------------------------------------------------------
CELLS.append(
    _md(
        [
            "# 05 \u2014 Visualize Results",
            "",
            "Interactive 3D visualization, probability thresholding, rare-region "
            "isolation, 3D surface reconstruction, uncertainty diagnostics, and "
            "conclusion tables for publication.",
        ]
    )
)

# ---- 2. Imports --------------------------------------------------------------
CELLS.append(
    _code(
        [
            "import csv",
            "import gc",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "from pathlib import Path",
            "",
            "from research_ct.io.volume_saver import Load_From_Numpy, Load_From_Numpy_Slab",
            "from research_ct.analysis.material_stats import Compute_Material_Statistics, Print_Material_Report",
            "from research_ct.analysis.uncertainty_maps import Compute_Uncertainty, Compute_Margin",
        ]
    )
)

# ---- 3. Project paths --------------------------------------------------------
CELLS.append(
    _code(
        [
            "# Project directory and data paths",
            "PROJECT_DIR = Path.cwd()",
            "",
            "# Find project root directory",
            "while not (PROJECT_DIR / \"data\").exists():",
            "    PROJECT_DIR = PROJECT_DIR.parent",
            "",
            "# Data paths",
            "DATA_DIR = PROJECT_DIR / \"data\"",
            "RAW_DATA_DIR = DATA_DIR / \"raw\"",
            "OUTPUT_DATA_DIR = DATA_DIR / \"output\"",
            "FIGURES_DIR = OUTPUT_DATA_DIR / \"figures\"",
            "DIAG_DIR = OUTPUT_DATA_DIR / \"diagnostics\"",
            "PROCESSED_DATA_DIR = OUTPUT_DATA_DIR / \"processed\"",
            "",
            "FIGURES_DIR.mkdir(parents=True, exist_ok=True)",
        ]
    )
)

# ---- 4. Load outputs ---------------------------------------------------------
CELLS.append(
    _code(
        [
            "# Load all outputs (lazy memmap — no data enters RAM until indexed)",
            "Processed = Load_From_Numpy(PROCESSED_DATA_DIR / \"preprocessed_volume.npz\")",
            "Labels = Load_From_Numpy(OUTPUT_DATA_DIR / \"gmm_labels.npy\")",
            "Probs = Load_From_Numpy(OUTPUT_DATA_DIR / \"gmm_probabilities.npy\")",
            "",
            "print(f\"Processed: {Processed.shape}\")",
            "print(f\"Labels: {Labels.shape}\")",
            "print(f\"Probabilities: {Probs.shape}\")",
            "",
            "# Number of material classes",
            "Num_Classes = int(Labels.max() + 1)",
            "print(f\"Number of classes: {Num_Classes}\")",
        ]
    )
)

# ---- 5. Material Statistics Report -------------------------------------------
CELLS.append(
    _md(
        [
            "## Material Statistics Report",
            "",
            "Print quantitative summary of segmented materials and export as CSV.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "Stats = Compute_Material_Statistics(Processed, Labels, Num_Classes)",
            "Print_Material_Report(Stats)",
        ]
    )
)

# ---- 6. CSV export of material stats -----------------------------------------
CELLS.append(
    _code(
        [
            "# Export material statistics as CSV",
            "Csv_Path = OUTPUT_DATA_DIR / \"material_stats.csv\"",
            "with open(Csv_Path, \"w\", newline=\"\") as f:",
            "    writer = csv.writer(f)",
            "    writer.writerow([\"Class\", \"Voxel_Count\", \"Volume_Fraction\",",
            "                     \"Mean_Intensity\", \"Std_Intensity\",",
            "                     \"Min_Intensity\", \"Max_Intensity\"])",
            "    for C in Stats[\"classes\"]:",
            "        writer.writerow([",
            "            C[\"class_id\"],",
            "            C[\"voxel_count\"],",
            "            f\"{C['volume_fraction']:.6f}\",",
            "            f\"{C['mean_intensity']:.2f}\",",
            "            f\"{C['std_intensity']:.2f}\",",
            "            f\"{C['min_intensity']:.2f}\",",
            "            f\"{C['max_intensity']:.2f}\",",
            "        ])",
            "print(f\"Saved material stats CSV \u2192 {Csv_Path}\")",
        ]
    )
)

# ---- 7. Uncertainty Maps -----------------------------------------------------
CELLS.append(
    _md(
        [
            "## Uncertainty Maps",
            "",
            "Identify regions where the segmentation is ambiguous.  "
            "High entropy = high uncertainty; small margin = class ambiguity.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "Entropy, Max_Prob = Compute_Uncertainty(Probs)",
            "Margin = Compute_Margin(Probs, Top_K=2)",
            "",
            "Mid_Z = Processed.shape[0] // 4",
            "",
            "fig, axes = plt.subplots(1, 3, figsize=(18, 5))",
            "",
            "im0 = axes[0].imshow(Entropy[Mid_Z], cmap=\"hot\")",
            "axes[0].set_title(\"Entropy (Uncertainty)\")",
            "axes[0].axis(\"off\")",
            "plt.colorbar(im0, ax=axes[0], fraction=0.046)",
            "",
            "im1 = axes[1].imshow(Max_Prob[Mid_Z], cmap=\"viridis\")",
            "axes[1].set_title(\"Max Probability (Confidence)\")",
            "axes[1].axis(\"off\")",
            "plt.colorbar(im1, ax=axes[1], fraction=0.046)",
            "",
            "im2 = axes[2].imshow(Margin[Mid_Z], cmap=\"coolwarm\")",
            "axes[2].set_title(\"Margin (Top 2 Classes)\")",
            "axes[2].axis(\"off\")",
            "plt.colorbar(im2, ax=axes[2], fraction=0.046)",
            "",
            "plt.suptitle(\"Uncertainty Maps \u2014 Middle Slice\", fontsize=14)",
            "plt.tight_layout()",
            "plt.show()",
        ]
    )
)

# ---- 8. Interactive probability thresholding ---------------------------------
CELLS.append(
    _md(
        [
            "## Interactive Probability Thresholding",
            "",
            "Use the sliders to explore probability maps per class.  Adjust the "
            "threshold and Z-slice to see where each class is confident.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "from ipywidgets import interact, FloatSlider, IntSlider",
            "",
            "def show_probability_threshold(",
            "    class_idx: int = 0,",
            "    threshold: float = 0.5,",
            "    z_slice: int = 0,",
            ") -> None:",
            "    \"\"\"Display probability map and binary threshold mask.\"\"\"",
            "    z_slice = max(0, min(z_slice, Probs.shape[0] - 1))",
            "    # Materialize one slice from memmap",
            "    prob_slice = np.array(Probs[z_slice, :, :, class_idx], copy=True)",
            "    mask = prob_slice > threshold",
            "",
            "    fig, axes = plt.subplots(1, 2, figsize=(14, 6))",
            "    axes[0].imshow(prob_slice, cmap=\"magma\", vmin=0, vmax=1)",
            "    axes[0].set_title(f\"P(class={class_idx}) \u2014 Z={z_slice}\")",
            "    axes[0].axis(\"off\")",
            "    plt.colorbar(",
            "        axes[0].images[0], ax=axes[0], fraction=0.046, label=\"Probability\"",
            "    )",
            "",
            "    axes[1].imshow(mask, cmap=\"gray\")",
            "    axes[1].set_title(",
            "        f\"P(class={class_idx}) > {threshold}  \"",
            "        f\"({mask.sum():,} voxels)\"",
            "    )",
            "    axes[1].axis(\"off\")",
            "    plt.tight_layout()",
            "    plt.show()",
            "",
            "interact(",
            "    show_probability_threshold,",
            "    class_idx=IntSlider(",
            "        min=0, max=Num_Classes - 1, step=1, value=0, description=\"Class\"",
            "    ),",
            "    threshold=FloatSlider(",
            "        min=0.0, max=1.0, step=0.05, value=0.5, description=\"Threshold\"",
            "    ),",
            "    z_slice=IntSlider(",
            "        min=0,",
            "        max=Probs.shape[0] - 1,",
            "        step=1,",
            "        value=Probs.shape[0] // 4,",
            "        description=\"Z Slice\",",
            "    ),",
            ");",
        ]
    )
)

# ---- 9. Rare-region isolation -------------------------------------------------
CELLS.append(
    _md(
        [
            "## Rare-Region Isolation",
            "",
            "Isolate **small connected components** with **low probability** "
            "(the two criteria combined).  Use the sliders to tune the "
            "probability threshold and component-size range.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "from scipy import ndimage",
            "",
            "def isolate_rare_regions(",
            "    class_idx: int = 0,",
            "    prob_threshold: float = 0.3,",
            "    min_size: int = 10,",
            "    max_size: int = 500,",
            "    z_slice: int = 0,",
            ") -> None:",
            "    \"\"\"Display rare-region mask for a class on one Z-slice.\"\"\"",
            "    z_slice = max(0, min(z_slice, Probs.shape[0] - 1))",
            "    prob_slice = np.array(Probs[z_slice, :, :, class_idx], copy=True)",
            "",
            "    binary = prob_slice > prob_threshold",
            "    labeled, n_feat = ndimage.label(binary)",
            "",
            "    # Count component sizes",
            "    sizes = np.bincount(labeled.ravel())[1:]",
            "    in_range = np.where((sizes >= min_size) & (sizes <= max_size))[0] + 1",
            "    rare_mask = np.isin(labeled, in_range)",
            "",
            "    fig, axes = plt.subplots(1, 3, figsize=(21, 6))",
            "    axes[0].imshow(prob_slice, cmap=\"magma\", vmin=0, vmax=1)",
            "    axes[0].set_title(",
            "        f\"P(class={class_idx}) \u2014 Z={z_slice}\"",
            "    )",
            "    axes[0].axis(\"off\")",
            "",
            "    axes[1].imshow(binary, cmap=\"gray\")",
            "    axes[1].set_title(",
            "        f\"P > {prob_threshold} ({n_feat} components)\"",
            "    )",
            "    axes[1].axis(\"off\")",
            "",
            "    axes[2].imshow(rare_mask, cmap=\"Reds\")",
            "    axes[2].set_title(",
            "        f\"Rare [{min_size},{max_size}] ({len(in_range)} components)\"",
            "    )",
            "    axes[2].axis(\"off\")",
            "    plt.tight_layout()",
            "    plt.show()",
            "",
            "interact(",
            "    isolate_rare_regions,",
            "    class_idx=IntSlider(",
            "        min=0, max=Num_Classes - 1, step=1, value=0, description=\"Class\"",
            "    ),",
            "    prob_threshold=FloatSlider(",
            "        min=0.0, max=1.0, step=0.05, value=0.3, description=\"P >\"",
            "    ),",
            "    min_size=IntSlider(",
            "        min=1, max=100, step=1, value=10, description=\"Min size\"",
            "    ),",
            "    max_size=IntSlider(",
            "        min=10, max=2000, step=10, value=500, description=\"Max size\"",
            "    ),",
            "    z_slice=IntSlider(",
            "        min=0,",
            "        max=Probs.shape[0] - 1,",
            "        step=1,",
            "        value=Probs.shape[0] // 4,",
            "        description=\"Z Slice\",",
            "    ),",
            ");",
        ]
    )
)

# ---- 10. Napari 3D -----------------------------------------------------------
CELLS.append(
    _md(
        [
            "## 3D Visualization with Napari",
            "",
            "Launch interactive viewer.  Toggle layers, adjust opacity, "
            "inspect in 3D.  The entropy heatmap is overlaid as a "
            "semi-transparent layer.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "from research_ct.visualization.napari_viewer import launch_napari_viewer",
            "",
            "# Launch napari with volume, labels, probabilities, and entropy overlay",
            "Viewer = launch_napari_viewer(",
            "    Processed,",
            "    Labels=Labels,",
            "    Probabilities=Probs,",
            "    Entropy=Entropy,",
            "    Probability_Threshold=0.3,",
            "    Render_3d=False,",
            ")",
        ]
    )
)

# ---- 11. 3D Mesh Reconstruction ----------------------------------------------
CELLS.append(
    _md(
        [
            "## 3D Surface Reconstruction",
            "",
            "Extract 3D meshes from high-confidence class masks using "
            "marching cubes and add them as napari surface layers.  "
            "Processes a Z-slab to keep memory usage manageable.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "from skimage import measure",
            "",
            "def extract_class_mesh(",
            "    labels: np.ndarray,",
            "    probs: np.ndarray,",
            "    class_idx: int = 0,",
            "    conf_threshold: float = 0.5,",
            "    z_start: int = 0,",
            "    z_stop: int = 50,",
            "    z_step: int = 2,",
            ") -> dict | None:",
            "    \"\"\"Extract a 3D mesh for one class via marching cubes.",
            "",
            "    Args:",
            "        labels: Integer label volume (D, H, W).",
            "        probs: Class probability volume (D, H, W, K).",
            "        class_idx: Which class to extract.",
            "        conf_threshold: Minimum probability for mask inclusion.",
            "        z_start, z_stop: Z-slice range.",
            "        z_step: Downsample factor along Z.",
            "",
            "    Returns:",
            "        Dict with 'vertices', 'faces' keys, or None if empty.",
            "    \"\"\"",
            "    z_stop = min(z_stop, labels.shape[0])",
            "",
            "    slab_labels = np.array(labels[z_start:z_stop:z_step], copy=True)",
            "    slab_probs = np.array(",
            "        probs[z_start:z_stop:z_step, :, :, class_idx], copy=True",
            "    )",
            "",
            "    binary = (slab_labels == class_idx) & (slab_probs > conf_threshold)",
            "",
            "    if binary.sum() < 100:",
            "        print(",
            "            f\"[Mesh] Class {class_idx}: only {binary.sum()} voxels \u2014 ",
            "            \"skipping\"",
            "        )",
            "        return None",
            "",
            "    verts, faces, _, _ = measure.marching_cubes(",
            "        binary.astype(np.float32), level=0.5, step_size=1",
            "    )",
            "    print(",
            "        f\"[Mesh] Class {class_idx}: {len(verts):,} verts, \"",
            "        f\"{len(faces):,} faces\"",
            "    )",
            "    return {\"vertices\": verts, \"faces\": faces}",
            "",
            "",
            "# Extract meshes for all classes in the first 50 Z-slices",
            "Mesh_Surfaces = {}",
            "for k in range(Num_Classes):",
            "    mesh = extract_class_mesh(",
            "        Labels, Probs, class_idx=k,",
            "        conf_threshold=0.5, z_start=0, z_stop=50, z_step=2",
            "    )",
            "    if mesh is not None:",
            "        Mesh_Surfaces[k] = mesh",
            "",
            "print()",
            "print(\"Run the napari cell below to add these surfaces to the viewer.\")",
        ]
    )
)

# ---- 12. Napari with surfaces ------------------------------------------------
CELLS.append(
    _md(
        [
            "## Napari + 3D Surfaces",
            "",
            "Re-launch napari with pre-extracted surface meshes.  Set "
            "``Render_3d=True`` for immediate 3D rendering.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "Viewer = launch_napari_viewer(",
            "    Processed,",
            "    Labels=Labels,",
            "    Probabilities=Probs,",
            "    Entropy=Entropy,",
            "    Mesh_Surfaces=Mesh_Surfaces,",
            "    Surface_Opacity=0.6,",
            "    Render_3d=True,",
            ")",
        ]
    )
)

# ---- 13. Clipping / cropping -------------------------------------------------
CELLS.append(
    _md(
        [
            "## Clipping and Cropping",
            "",
            "Define a bounding-box sub-volume and re-extract the surface "
            "mesh only within that region.  Useful for isolating one "
            "page or cover section.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "# Interactive bounding-box crop and mesh re-extraction",
            "from ipywidgets import interact",
            "",
            "def crop_and_mesh(",
            "    class_idx: int = 0,",
            "    z0: int = 0,",
            "    z1: int = 50,",
            "    y0: int = 0,",
            "    y1: int = 500,",
            "    x0: int = 0,",
            "    x1: int = 500,",
            ") -> None:",
            "    \"\"\"Re-extract mesh from a cropped sub-volume.\"\"\"",
            "    z1 = min(z1, Probs.shape[0])",
            "    y1 = min(y1, Probs.shape[1])",
            "    x1 = min(x1, Probs.shape[2])",
            "",
            "    cropped_labels = np.array(Labels[z0:z1:2, y0:y1, x0:x1], copy=True)",
            "    cropped_probs = np.array(",
            "        Probs[z0:z1:2, y0:y1, x0:x1, class_idx], copy=True",
            "    )",
            "",
            "    binary = (cropped_labels == class_idx) & (cropped_probs > 0.5)",
            "",
            "    if binary.sum() < 100:",
            "        print(f\"Cropped region too small ({binary.sum()} voxels)\")",
            "        return",
            "",
            "    verts, faces, _, _ = measure.marching_cubes(",
            "        binary.astype(np.float32), level=0.5, step_size=1",
            "    )",
            "    print(",
            "        f\"Cropped mesh: {len(verts):,} verts, {len(faces):,} faces \"",
            "        f\"(box [{z0}:{z1}, {y0}:{y1}, {x0}:{x1}])\"",
            "    )",
            "",
            "    # Quick napari view",
            "    import napari",
            "    v = napari.Viewer(title=f\"Crop class {class_idx}\")",
            "    v.add_image(cropped_labels, name=\"Labels (cropped)\")",
            "    v.add_surface(",
            "        (verts, faces),",
            "        name=f\"Mesh class {class_idx} (cropped)\",",
            "        opacity=0.7,",
            "    )",
            "    napari.run()",
            "",
            "# Adjust ranges for your volume dimensions",
            "interact(",
            "    crop_and_mesh,",
            "    class_idx=IntSlider(0, Num_Classes - 1, 1, 0, description=\"Class\"),",
            "    z0=IntSlider(0, Probs.shape[0] - 1, 1, 0, description=\"Z0\"),",
            "    z1=IntSlider(1, Probs.shape[0], 1, min(50, Probs.shape[0]), description=\"Z1\"),",
            "    y0=IntSlider(0, Probs.shape[1] - 1, 50, 0, description=\"Y0\"),",
            "    y1=IntSlider(50, Probs.shape[1], 50, min(500, Probs.shape[1]), description=\"Y1\"),",
            "    x0=IntSlider(0, Probs.shape[2] - 1, 50, 0, description=\"X0\"),",
            "    x1=IntSlider(50, Probs.shape[2], 50, min(500, Probs.shape[2]), description=\"X1\"),",
            ");",
        ]
    )
)

# ---- 14. Export Probability Videos — [TO FIX] --------------------------------
CELLS.append(
    _md(
        [
            "## Export Probability Videos  \u2757 [TO FIX]",
            "",
            "Create videos showing class probability through Z slices.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "# [TO FIX] --- Paste your corrected probability-video export code below ---",
            "# Expected: loop over class indices, call imageio.get_writer with ffmpeg",
            "# backend check, write frames, close writer.",
            "",
            "# from research_ct.visualization.export import export_probability_video",
            "",
            "# for k in range(Num_Classes):",
            "#     output_path = FIGURES_DIR / f\"probability_class_{k}.mp4\"",
            "#     export_probability_video(Probs, str(output_path), Class_Index=k, Fps=15)",
            "",
            "print(\"[TO FIX] Paste your corrected export code above, then re-run this cell.\")",
        ]
    )
)

# ---- 15. Export Colored Label Stacks — [TO FIX] ------------------------------
CELLS.append(
    _md(
        [
            "## Export Colored Label Stacks  \u2757 [TO FIX]",
            "",
            "Save segmentation as colored TIFF stack for external tools (ImageJ, etc.).",
        ]
    )
)

CELLS.append(
    _code(
        [
            "# [TO FIX] --- Paste your corrected colored-stack export code below ---",
            "# Issues to fix in export_label_colors:",
            "#  - Color_Map must match the actual Num_Classes (not hardcoded to 4).",
            "#  - imageio.mimwrite vs Save_Volume_As_Stack path conflict.",
            "#  - Ensure .tif or multi-page TIFF format is correct for ImageJ.",
            "",
            "# from research_ct.visualization.export import export_label_colors",
            "# Color_Map = { ... }  # auto-generate from Num_Classes",
            "# export_label_colors(Labels, str(OUTPUT_DATA_DIR / \"segmentation_colored.tif\"), Color_Map)",
            "",
            "print(\"[TO FIX] Paste your corrected export code above, then re-run this cell.\")",
        ]
    )
)

# ---- 16. Component Distribution Plots ----------------------------------------
CELLS.append(
    _md(
        [
            "## Component Distribution Plots",
            "",
            "Generate publication-quality GMM decomposition figure.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "from research_ct.visualization.plot_distributions import plot_gmm_components",
            "from research_ct.segmentation.gmm_fitter import Gmm_Fitter",
            "",
            "# Re-fit on sample for plotting",
            "sample_flat = np.random.choice(",
            "    Processed.ravel(), 200_000, replace=False",
            ")",
            "Fitter = Gmm_Fitter(Min_Components=Num_Classes, Max_Components=Num_Classes)",
            "Fitter.Fit(sample_flat.reshape(-1, 1), Verbose=False)",
            "",
            "fig = plot_gmm_components(",
            "    sample_flat,",
            "    Fitter.Model,",
            "    Output_Path=FIGURES_DIR / \"gmm_decomposition.png\",",
            ")",
            "plt.show()",
            "print(\"Saved: data/output/figures/gmm_decomposition.png\")",
        ]
    )
)

# ---- 17. Slice-wise uncertainty profile --------------------------------------
CELLS.append(
    _md(
        [
            "## Slice-Wise Uncertainty Profile",
            "",
            "Mean entropy and confidence per Z-slice.  "
            "Detects non-stationary ambiguity across the volume.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "# Compute mean entropy & confidence per Z-slice",
            "z_indices = range(0, Probs.shape[0], 2)  # every other slice",
            "mean_entropy = []",
            "mean_confidence = []",
            "",
            "for z in z_indices:",
            "    slab = np.array(Probs[z : z + 1], copy=True).squeeze(0)  # (H, W, K)",
            "    clipped = np.clip(slab, 1e-10, 1.0)",
            "    ent = -np.sum(clipped * np.log(clipped), axis=2)",
            "    conf = slab.max(axis=2)",
            "    mean_entropy.append(float(ent.mean()))",
            "    mean_confidence.append(float(conf.mean()))",
            "    del slab, clipped, ent, conf",
            "    if z % 20 == 0:",
            "        gc.collect()",
            "        print(f\"  processed Z={z}/{Probs.shape[0]}\")",
            "",
            "fig, ax1 = plt.subplots(figsize=(12, 5))",
            "ax1.plot(list(z_indices), mean_entropy, \"r-\", label=\"Mean entropy\", linewidth=2)",
            "ax1.set_xlabel(\"Z slice\")",
            "ax1.set_ylabel(\"Mean entropy\", color=\"r\")",
            "ax1.tick_params(axis=\"y\", labelcolor=\"r\")",
            "ax1.grid(True, alpha=0.3)",
            "",
            "ax2 = ax1.twinx()",
            "ax2.plot(",
            "    list(z_indices),",
            "    mean_confidence,",
            "    \"b--\",",
            "    label=\"Mean confidence\",",
            "    linewidth=2,",
            ")",
            "ax2.set_ylabel(\"Mean confidence\", color=\"b\")",
            "ax2.tick_params(axis=\"y\", labelcolor=\"b\")",
            "",
            "lines1, labels1 = ax1.get_legend_handles_labels()",
            "lines2, labels2 = ax2.get_legend_handles_labels()",
            "ax1.legend(lines1 + lines2, labels1 + labels2, loc=\"upper right\")",
            "plt.title(\"Slice-Wise Uncertainty Profile\")",
            "plt.tight_layout()",
            "plt.savefig(FIGURES_DIR / \"slice_uncertainty_profile.png\", dpi=150)",
            "plt.show()",
        ]
    )
)

# ---- 18. High-uncertainty component table ------------------------------------
CELLS.append(
    _md(
        [
            "## High-Uncertainty Component Table",
            "",
            "Find and tabulate connected regions of high uncertainty.  "
            "For each region, report centroid, size, mean entropy, and "
            "the two competing classes (from margin).",
        ]
    )
)

CELLS.append(
    _code(
        [
            "# Identify high-uncertainty connected components",
            "# Run on middle slab to limit memory",
            "Z_Slab_Start = max(0, Probs.shape[0] // 2 - 25)",
            "Z_Slab_End = min(Probs.shape[0], Probs.shape[0] // 2 + 25)",
            "gradient_slab = np.array(",
            "    Probs[Z_Slab_Start:Z_Slab_End], copy=True",
            ")  # (Nz, H, W, K)",
            "",
            "entropy_slab = -np.sum(",
            "    np.clip(gradient_slab, 1e-10, 1.0) * np.log(np.clip(gradient_slab, 1e-10, 1.0)),",
            "    axis=3,",
            ")",
            "",
            "# Binary mask: voxels with entropy above median + 1 std",
            "Ent_Threshold = float(entropy_slab.mean() + entropy_slab.std())",
            "high_ent_mask = entropy_slab > Ent_Threshold",
            "",
            "# 3D connected components",
            "labeled, n_feat = ndimage.label(high_ent_mask)",
            "sizes = np.bincount(labeled.ravel())[1:]",
            "",
            "# Only components with >= 100 voxels",
            "valid_labels = np.where(sizes >= 100)[0] + 1",
            "print(f\"{len(valid_labels)} high-uncertainty regions (entropy > {Ent_Threshold:.3f})\")",
            "",
            "# Build table",
            "rows = []",
            "for lbl in valid_labels:",
            "    mask = labeled == lbl",
            "    z, y, x = np.where(mask)",
            "    centroid = (float(z.mean()), float(y.mean()), float(x.mean()))",
            "    mean_ent = float(entropy_slab[mask].mean())",
            "",
            "    # Dominant competing classes (from margin on mean probabilities)",
            "    mean_probs = gradient_slab[mask].mean(axis=0)",
            "    top2 = np.argsort(mean_probs)[-2:][::-1]",
            "",
            "    rows.append({",
            "        \"region_id\": int(lbl),",
            "        \"voxels\": int(mask.sum()),",
            "        \"centroid_z\": centroid[0] + Z_Slab_Start,",
            "        \"centroid_y\": centroid[1],",
            "        \"centroid_x\": centroid[2],",
            "        \"mean_entropy\": mean_ent,",
            "        \"class_1\": int(top2[0]),",
            "        \"class_2\": int(top2[1]),",
            "        \"p_class_1\": float(mean_probs[top2[0]]),",
            "        \"p_class_2\": float(mean_probs[top2[1]]),",
            "    })",
            "",
            "# Export CSV",
            "table_path = OUTPUT_DATA_DIR / \"high_uncertainty_regions.csv\"",
            "with open(table_path, \"w\", newline=\"\") as f:",
            "    writer = csv.DictWriter(f, fieldnames=[\"region_id\", \"voxels\", \"centroid_z\", \"centroid_y\", \"centroid_x\", \"mean_entropy\", \"class_1\", \"class_2\", \"p_class_1\", \"p_class_2\"])",
            "    writer.writeheader()",
            "    writer.writerows(rows)",
            "print(f\"Saved table \u2192 {table_path}\")",
            "",
            "# Display top 10",
            "sorted_rows = sorted(rows, key=lambda r: r[\"voxels\"], reverse=True)",
            "print()",
            "print(f\"{'ID':<8} {'Voxels':<10} {'Centroid (Z,Y,X)':<30} {'Entropy':<10} {'Top 2 classes'}\")",
            "print(\"-\" * 80)",
            "for r in sorted_rows[:10]:",
            "    print(",
            "        f\"{r['region_id']:<8} \"",
            "        f\"{r['voxels']:<10,} \"",
            "        f\"({r['centroid_z']:.0f},{r['centroid_y']:.0f},{r['centroid_x']:.0f}) \".ljust(30)",
            "        f\"{r['mean_entropy']:<10.3f} \"",
            "        f\"{r['class_1']} vs {r['class_2']}\"",
            "    )",
        ]
    )
)

# ---- 19. Per-slice material fractions ----------------------------------------
CELLS.append(
    _md(
        [
            "## Per-Slice Material Fractions",
            "",
            "Class volume fraction vs. Z-slice.  Detects drift or "
            "non-stationarity in material composition.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "# Compute material fractions per Z-slice (every 5th slice)",
            "step = 5",
            "slice_rows = []",
            "",
            "for z in range(0, Probs.shape[0], step):",
            "    slab = np.array(Probs[z : z + 1], copy=True).squeeze(0)  # (H, W, K)",
            "    labels_slab = slab.argmax(axis=-1)",
            "    row = {\"slice\": z}",
            "    for k in range(Num_Classes):",
            "        row[f\"class_{k}_frac\"] = float((labels_slab == k).mean())",
            "    slice_rows.append(row)",
            "    del slab, labels_slab",
            "",
            "# Plot",
            "fig, ax = plt.subplots(figsize=(14, 6))",
            "z_vals = [r[\"slice\"] for r in slice_rows]",
            "for k in range(Num_Classes):",
            "    fracs = [r[f\"class_{k}_frac\"] for r in slice_rows]",
            "    ax.plot(z_vals, fracs, \"o-\", linewidth=2, markersize=3, label=f\"Class {k}\")",
            "ax.set_xlabel(\"Z slice\")",
            "ax.set_ylabel(\"Volume fraction\")",
            "ax.set_title(\"Per-Slice Material Fractions\")",
            "ax.legend()",
            "ax.grid(True, alpha=0.3)",
            "plt.tight_layout()",
            "plt.savefig(FIGURES_DIR / \"per_slice_fractions.png\", dpi=150)",
            "plt.show()",
            "",
            "# Export CSV",
            "frac_csv = OUTPUT_DATA_DIR / \"per_slice_material_fractions.csv\"",
            "fieldnames = [\"slice\"] + [f\"class_{k}_frac\" for k in range(Num_Classes)]",
            "with open(frac_csv, \"w\", newline=\"\") as f:",
            "    writer = csv.DictWriter(f, fieldnames=fieldnames)",
            "    writer.writeheader()",
            "    writer.writerows(slice_rows)",
            "print(f\"Saved \u2192 {frac_csv}\")",
        ]
    )
)

# ---- 20. BIC curve reference -------------------------------------------------
CELLS.append(
    _md(
        [
            "## BIC Curve (from Notebook 03)",
            "",
            "The BIC curve selects the optimal number of GMM components.  "
            "This plot was generated in notebook 03 and is reproduced here "
            "for completeness.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "# Display BIC curve saved from notebook 03",
            "bic_path = FIGURES_DIR / \"BIC-Based Model Selection.png\"",
            "if bic_path.exists():",
            "    from matplotlib.image import imread",
            "    img = imread(str(bic_path))",
            "    fig, ax = plt.subplots(figsize=(8, 6))",
            "    ax.imshow(img)",
            "    ax.axis(\"off\")",
            "    ax.set_title(\"BIC-Based Model Selection (notebook 03)\")",
            "    plt.show()",
            "else:",
            "    print(",
            "        f\"BIC curve not found at {bic_path}.  \"",
            "        \"Run notebook 03 and ensure the BIC plot is saved to data/output/figures/.\"",
            "    )",
        ]
    )
)

# ---- 21. Uncertainty vs intensity scatter ------------------------------------
CELLS.append(
    _md(
        [
            "## Uncertainty vs. Intensity Scatter",
            "",
            "Scatter of entropy vs. voxel intensity, colored by class.  "
            "Helps distinguish boundary ambiguity from intensity-noise ambiguity.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "# Sample from a middle Z-slice for scatter plot",
            "Mid_Z_Single = Processed.shape[0] // 4",
            "slab_probs = np.array(Probs[Mid_Z_Single : Mid_Z_Single + 1], copy=True).squeeze(0)",
            "slab_vol = np.array(Processed[Mid_Z_Single : Mid_Z_Single + 1], copy=True).squeeze(0)",
            "",
            "H, W = slab_vol.shape",
            "n_sample = 50_000",
            "y_rand = np.random.randint(0, H, n_sample)",
            "x_rand = np.random.randint(0, W, n_sample)",
            "",
            "probs_sample = slab_probs[y_rand, x_rand, :]",
            "intensity_sample = slab_vol[y_rand, x_rand]",
            "",
            "entropy_sample = -np.sum(",
            "    probs_sample * np.log(np.clip(probs_sample, 1e-10, 1.0)), axis=1",
            ")",
            "maxprob_sample = probs_sample.max(axis=1)",
            "label_sample = probs_sample.argmax(axis=1)",
            "",
            "fig, axes = plt.subplots(1, 2, figsize=(16, 6))",
            "",
            "sc = axes[0].scatter(",
            "    intensity_sample,",
            "    entropy_sample,",
            "    c=maxprob_sample,",
            "    cmap=\"viridis_r\",",
            "    alpha=0.3,",
            "    s=2,",
            ")",
            "axes[0].set_xlabel(\"Intensity\")",
            "axes[0].set_ylabel(\"Entropy\")",
            "axes[0].set_title(f\"Entropy vs. Intensity (Z={Mid_Z_Single})\")",
            "plt.colorbar(sc, ax=axes[0], label=\"Max Probability\")",
            "",
            "for k in range(Num_Classes):",
            "    mask = label_sample == k",
            "    axes[1].scatter(",
            "        intensity_sample[mask],",
            "        maxprob_sample[mask],",
            "        alpha=0.3,",
            "        s=2,",
            "        label=f\"Class {k}\",",
            "    )",
            "axes[1].set_xlabel(\"Intensity\")",
            "axes[1].set_ylabel(\"Max Probability\")",
            "axes[1].set_title(\"Max Probability vs. Intensity (by class)\")",
            "axes[1].legend(markerscale=5)",
            "",
            "plt.tight_layout()",
            "plt.savefig(FIGURES_DIR / \"uncertainty_vs_intensity.png\", dpi=150)",
            "plt.show()",
        ]
    )
)

# ---- 22. Class co-occurrence adjacency matrix --------------------------------
CELLS.append(
    _md(
        [
            "## Class Co-occurrence Adjacency Matrix",
            "",
            "Count 6-connected voxel-faces where two classes touch.  "
            "Validates physical plausibility: paper should touch air and ink, "
            "not cover directly.",
        ]
    )
)

CELLS.append(
    _code(
        [
            "# Build co-occurrence adjacency matrix",
            "# Process in Z-slabs to manage memory",
            "Adjacency = np.zeros((Num_Classes, Num_Classes), dtype=np.int64)",
            "",
            "Z_Adj_Start = max(0, min(100, Probs.shape[0]))",
            "",
            "for z in range(0, Z_Adj_Start):",
            "    slab = np.array(Probs[z : z + 1], copy=True).squeeze(0)",
            "    label_z = slab.argmax(axis=-1).astype(np.int32)",
            "    del slab",
            "",
            "    # Horizontal neighbors (left-right)",
            "    for a in range(Num_Classes):",
            "        mask_a = label_z[:, :-1] == a",
            "        for b in range(Num_Classes):",
            "            if a == b:",
            "                continue",
            "            count = (mask_a & (label_z[:, 1:] == b)).sum()",
            "            Adjacency[a, b] += np.int64(count)",
            "",
            "    # Vertical neighbors (up-down)",
            "    for a in range(Num_Classes):",
            "        mask_a = label_z[:-1, :] == a",
            "        for b in range(Num_Classes):",
            "            if a == b:",
            "                continue",
            "            count = (mask_a & (label_z[1:, :] == b)).sum()",
            "            Adjacency[a, b] += np.int64(count)",
            "",
            "    del label_z",
            "    if z % 25 == 0:",
            "        gc.collect()",
            "",
            "# Symmetrize",
            "Adjacency = np.maximum(Adjacency, Adjacency.T)",
            "",
            "# Normalize rows to fractions",
            "Row_Sums = Adjacency.sum(axis=1, keepdims=True).astype(np.float64)",
            "Row_Sums[Row_Sums == 0] = 1.0",
            "Adj_Frac = Adjacency.astype(np.float64) / Row_Sums",
            "",
            "# Plot heatmap",
            "fig, ax = plt.subplots(figsize=(8, 7))",
            "im = ax.imshow(Adj_Frac, cmap=\"Blues\", vmin=0, vmax=1)",
            "for i in range(Num_Classes):",
            "    for j in range(Num_Classes):",
            "        ax.text(",
            "            j, i, f\"{Adj_Frac[i, j]:.2f}\",",
            "            ha=\"center\", va=\"center\", fontsize=9,",
            "            color=\"white\" if Adj_Frac[i, j] > 0.5 else \"black\",",
            "        )",
            "ax.set_xticks(range(Num_Classes))",
            "ax.set_yticks(range(Num_Classes))",
            "ax.set_xlabel(\"Class\")",
            "ax.set_ylabel(\"Class\")",
            "ax.set_title(",
            "    f\"Class Co-occurrence (6-connectivity, Z=0-{Z_Adj_Start})\"",
            ")",
            "plt.colorbar(im, ax=ax, label=\"Contact fraction\")",
            "plt.tight_layout()",
            "plt.savefig(FIGURES_DIR / \"class_adjacency.png\", dpi=150)",
            "plt.show()",
        ]
    )
)

# ---- 23. Summary -------------------------------------------------------------
CELLS.append(
    _md(
        [
            "## Summary",
            "",
            "At this point you should have:",
            "- [ ] Segmented labels for the full volume",
            "- [ ] Probability maps for uncertainty quantification",
            "- [ ] Material statistics (console + CSV)",
            "- [ ] Interactive probability thresholding per class",
            "- [ ] Rare-region isolation (small components + low probability)",
            "- [ ] 3D napari viewer with entropy overlay and surface meshes",
            "- [ ] Cropped sub-volume surface extraction",
            "- [ ] Slice-wise uncertainty profiles",
            "- [ ] High-uncertainty component table (CSV)",
            "- [ ] Per-slice material fraction plots (CSV)",
            "- [ ] BIC curve reference",
            "- [ ] Uncertainty vs. intensity scatter",
            "- [ ] Class co-occurrence adjacency matrix",
            "",
            "Next steps:",
            "- Tune HMRF beta if results are too noisy or over-smoothed",
            "- Try hierarchical splitting if ink/paper separation is poor",
            "- Proceed to geometric page extraction (Charles' approach)",
        ]
    )
)


# ---------------------------------------------------------------------------
# Write .ipynb
# ---------------------------------------------------------------------------

def main() -> None:
    notebook = {
        "cells": CELLS,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.10.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    out_path = (
        Path(__file__).resolve().parent.parent
        / "notebooks"
        / "05_uncertainty_and_visualization.ipynb"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
        f.write("\n")

    print(f"Generated notebook -> {out_path}")


if __name__ == "__main__":
    main()