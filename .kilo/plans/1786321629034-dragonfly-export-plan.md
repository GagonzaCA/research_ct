# Dragonfly Export Modules — Implementation Plan

## Context

Notebook `05_uncertainty_and_visualization.ipynb` contains several sections (3D Visualization, 3D Surface Reconstruction, Napari + 3D Surfaces, Clipping and Cropping) that are experimental, memory-heavy, and their outputs are not useful for downstream analysis. The professor uses **Dragonfly** for professional 3D visualization. The goal is to replace those sections with a pair of focused, independent library modules that export TO Dragonfly-compatible formats (multi-page TIFF stacks), and add thin notebook cells that call them.

## Decisions made

| Decision | Choice |
|---|---|
| **Format** | Multi-page TIFF stack (one `.tif` per slice) — chosen because it is the most compatible with Dragonfly and avoids large single-file bottlenecks. |
| **Channels** | Grayscale (raw volume), Labels (segmentation), Entropy (uncertainty heatmap). |
| **Dtype strategy** | Labels: `uint16`, Entropy: `float32`, Grayscale: preserve or `float32`. Never normalized to `uint8`. |
| **Big-tiff** | Use `tifffile` with `bigtiff=True` if individual slices exceed 4 GB. |
| **Voxel spacing** | Injected from user-provided `Voxel_Spacing` tuple (default `(1.0, 1.0, 1.0)`). |
| **Notebook cells** | Replace the 4 removed sections with **1 cell** for metadata JSON + **1 cell** for volume channel export. |
| **Quality check** | Optional per-channel TIFF stack integrity verification inside the notebook. |
| **Material colors** | Generated as a Dragonfly-readable `.csv` mapping `label_id` to `(R,G,B,name)`. |

## Modules to create

### 1. `research_ct/io/dragonfly_exporter.py`

Handles low-level TIFF I/O for Dragonfly:

```python
# Functions
save_volume_as_tiff(
    volume: np.ndarray,
    output_path: Path,
    *,
    resolution: tuple[float, float, float] = (1.0, 1.0, 1.0),
    units: str = "um",
    compression: str | None = None,
    bigtiff: bool = False,
) -> Path
"""Save a 3D volume as a multi-page TIFF stack compatible with Dragonfly.

Injects ImageJ-style metadata ( Fiji / ImageJ / Dragonfly compatible)
so the stack is recognized as a calibrated 3D image.
"""
```

- Uses `tifffile` (already in `requirements.txt`).
- Resolution handled via `resolution` + `imagej=True` or explicit tag `X_RESOLUTION` / `Y_RESOLUTION`.
- `compression=None` (lossless, fast). Optional `compression="zlib"` for disk savings.
- `bigtiff=True` when slice size warrants it.

```python
# Helper
_write_tiff_page(
    writer: tifffile.TiffWriter,
    page: np.ndarray,
    page_index: int,
    total_pages: int,
    resolution: tuple,
    units: str,
    ...
)
```

### 2. `research_ct/processing/dragonfly_utils.py`

Handles high-level channel preparation and metadata generation:

```python
# Data class
@dataclass
class DragonflyExportConfig:
    output_dir: Path
    voxel_spacing: tuple[float, float, float] = (1.0, 1.0, 1.0)
    spacing_units: str = "um"
    label_colors: dict[int, tuple[int, int, int]] | None = None
    label_names: dict[int, str] | None = None
    bigtiff_threshold_gb: float = 2.0
```

```python
# Functions
prepare_label_volume(
    labels: np.ndarray,
    class_colors: dict[int, tuple[int, int, int]],
) -> np.ndarray
"""Convert integer labels to RGB label volume for Dragonfly."""

save_label_colors_csv(
    config: DragonflyExportConfig,
    output_path: Path,
) -> Path
"""Write a .csv file mapping label_id -> (R,G,B,Name) for Dragonfly import."""

export_dragonfly_channels(
    processed: np.ndarray,
    labels: np.ndarray,
    entropy: np.ndarray,
    config: DragonflyExportConfig,
) -> dict[str, Path]
"""Export all three channels (grayscale, labels, entropy) to TIFF stacks.

Returns a dict mapping channel name -> file path.
"""
```

- `prepare_label_volume` creates an `(D, H, W, 3)` uint8 RGB volume if `class_colors` is provided.
- `save_dragonfly_metadata_json` writes a sidecar JSON with `voxel_spacing`, `shape`, `dtype`, `channels`, `label_colors` and `label_names`.
- `export_dragonfly_channels` calls `save_volume_as_tiff` three times and returns the paths.

## Notebook changes

Replace notebook 05 sections:

| Section (old) | Action |
|---|---|
| `## 3D Visualization with Napari` | **Remove** |
| `## 3D Surface Reconstruction` | **Remove** |
| `## Napari + 3D Surfaces` | **Remove** |
| `## Clipping and Cropping` | **Remove** |

Insert **two new cells** after the *Uncertainty Maps* section (or wherever the data `Processed`, `Labels`, `Entropy` are already in scope):

**Cell A — Save Dragonfly Metadata:**
```python
from research_ct.processing.dragonfly_utils import (
    DragonflyExportConfig, export_dragonfly_channels,
)

# --- Optional: define voxel spacing if known from scanner metadata ---
# Example: (z_spacing, y_spacing, x_spacing) in micrometers
Voxel_Spacing = (1.0, 1.0, 1.0)  # Replace with actual values if available

Config = DragonflyExportConfig(
    output_dir=OUTPUT_DATA_DIR / "dragonfly_export",
    voxel_spacing=Voxel_Spacing,
    label_colors={0: (0, 0, 0), 1: (255, 228, 181), 2: (47, 79, 79), 3: (139, 69, 19)},
    label_names={0: "Background", 1: "Paper", 2: "Ink", 3: "Cover"},
)

Paths = export_dragonfly_channels(Processed, Labels, Entropy, Config)
print("Dragonfly export paths:")
for k, p in Paths.items():
    print(f"  {k}: {p}")
```

**Cell B — Verify Exported Stacks:**
```python
from research_ct.io.dragonfly_exporter import verify_dragonfly_channels

# Optional integrity check before sending to Dragonfly
Status = verify_dragonfly_channels(Paths)
print(Status)
```

## Implementation order

1. Create `src/research_ct/io/dragonfly_exporter.py` with `save_volume_as_tiff` and `verify_dragonfly_channels`.
2. Create `src/research_ct/processing/dragonfly_utils.py` with `DragonflyExportConfig`, `prepare_label_volume`, `save_label_colors_csv`, `export_dragonfly_channels`.
3. Add exports to package `__init__.py` files so notebook imports stay short.
4. Edit `notebooks/05_uncertainty_and_visualization.ipynb` — remove the 4 obsolete sections, insert Cells A & B.
5. Run notebook smoke test (or a short Python script that exercises the modules) to ensure:
   - TIFF stacks are written without dtype normalization.
   - Metadata JSON is valid.
   - Label color CSV matches Dragonfly import expectations.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| `tifffile` version mismatch | `tifffile>=2021.0.0` is already in `requirements.txt`; use `imagej=True` for broad compatibility. |
| Slices > 4 GB | `bigtiff=True` threshold set to 2 GB in config; export raises an informative error if threshold exceeded without bigtiff. |
| Wrong voxel spacing | Documented as user-editable value in notebook Cell A. Default `(1.0, 1.0, 1.0)` is safe but uncalibrated. |
| Label colors are subjective | Exposed via `DragonflyExportConfig.label_colors`; user can override before export. |

## Open questions (none blocking)

- Should the module also write an OME-TIFF XML header? (Future enhancement; ImageJ-style TIFF is sufficient for Dragonfly today.)
- Should we provide a CLI entry-point (e.g., `python -m research_ct.export_to_dragonfly`) for batch runs outside notebooks? (Out of scope for this plan; notebook-driven workflow is sufficient.)

## Files to create / modify

### Create
- `src/research_ct/io/dragonfly_exporter.py`
- `src/research_ct/processing/dragonfly_utils.py`
- `src/research_ct/processing/__init__.py` (if missing; currently absent from repo layout)

### Modify
- `src/research_ct/io/__init__.py` — add `save_volume_as_tiff` to public API.
- `notebooks/05_uncertainty_and_visualization.ipynb` — remove 4 sections, add 2 cells.

## Validation checklist

- [ ] `export_dragonfly_channels(...)` finishes without error on a test slab.
- [ ] Output `.tif` contains 3 or 4 channels (grayscale, labels, entropy) and loads cleanly into Dragonfly.
- [ ] Metadata JSON contains the same `voxel_spacing` passed in config.
- [ ] Label color CSV uses exact hex values and correct number of rows (`num_classes`).
- [ ] Notebook runs top-to-bottom after the edit (all imports resolve, no NameError from removed variables).
