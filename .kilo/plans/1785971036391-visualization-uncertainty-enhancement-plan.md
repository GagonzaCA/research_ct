# Plan: Micro-CT Visualization, Uncertainty & 3D Reconstruction Enhancement

## Context

Notebook `05_uncertainty_and_visualization.ipynb` is the final pipeline phase. It loads preprocessed volume, GMM labels, and probabilities; prints material statistics; generates static uncertainty heatmaps (entropy, confidence, margin); launches a basic napari viewer; exports videos and colored stacks; and re-fits GMM on a sample for publication plots.

### What currently works
- Material statistics report (`material_stats.py`)
- Static uncertainty maps: entropy, max probability, margin (`uncertainty_maps.py`)
- Basic napari viewer with volume, labels, and 4 probability layers (`napari_viewer.py`)
- Probability video export (`export.py`)
- Colored label TIFF export (`export.py`)
- GMM component overlay plot (`plot_distributions.py`)

### What is broken / missing
- `Export Probability Videos` and `Export Colored Label Stacks` cells in notebook 05 have path/export conflicts (marked [TO FIX] — user will paste corrected code)
- Napari viewer has no interactive class toggles, no probability thresholding, no entropy overlay, no rare-region isolation
- No 3D reconstruction or surface extraction capability
- No slice-wise uncertainty profile or CSV/table export for conclusions
- Data path inconsistency: notebook 03 uses `PROJECT_DIR / "data"`, while 04/05 use `PROJECT_DIR / "src" / "research_ct" / "data"` — user confirmed data lives at root `data/`

## Design Decisions (confirmed)

| Decision | Chosen Option | Rationale |
|---|---|---|
| Data directory | `PROJECT_DIR / "data"` (root level) | User confirmed; notebooks 04/05 must match notebook 03 |
| 3D reconstruction tool | Napari surface layers (`add_surface`) | Unified viewer — volume, labels, probabilities, uncertainty, and 3D surfaces all in one napari window. Pyvista kept for offline publication figures |
| Interactivity mechanism | Static `ipywidgets.interact` sliders in notebook cells | Simpler, reproducible in notebook, avoids memory leaks from repeated napari layer mutations. Reserve napari widgets only for final integrated viewer if needed |
| Rare region definition | Combine: (1) small connected components AND (2) low probability regions | Isolates both tiny spatial outliers and ambiguous boundary voxels |

## Task List (ordered — user will implement and test)

### Phase 1: Path Fixes (no new features)
1. **Fix notebook 04** — change `DATA_DIR = PROJECT_DIR / "src" / "research_ct" / "data"` to `PROJECT_DIR / "data"` in cell 2
2. **Fix notebook 05** — same path change in cell 2
3. **Verify** — ensure all notebooks point to the same directory tree where `preprocessed_volume.npz`, `gmm_probabilities.npy`, and `gmm_labels.npy` exist

### Phase 2: Broken Export Sections ([TO FIX] — user pastes own code)
4. **Fix `Export Probability Videos` cell** — user will provide corrected `imageio` backend check and loop code
5. **Fix `Export Colored Label Stacks` cell** — user will provide corrected `export_label_colors` call (resolve conflict between `imageio.mimwrite` and `Save_Volume_As_Stack` overwriting same path; ensure color map length matches actual `Num_Classes`)

### Phase 3: Napari Viewer Enhancement
6. **Extend `napari_viewer.py`** — add parameters to `launch_napari_viewer`:
   - `Entropy: Optional[np.ndarray]` — add as semi-transparent heatmap overlay on volume layer
   - `Probability_Threshold: float` — for each class probability layer, add a contrast limit so only voxels above threshold are visible
   - `Render_3d: bool` — set viewer to 3D mode if requested
   - Keep existing layers: volume (gray), labels (tab10), probabilities (magma, max 4 classes)
7. **Update notebook 05** — cell calling `launch_napari_viewer` should now pass `Entropy` computed earlier

### Phase 4: Interactive Probability & Class Controls
8. **Add `ipywidgets.interact` cell in notebook 05** — interactive probability threshold per class:
   - Slider `threshold` range [0.0, 1.0] (default 0.5)
   - Dropdown `class_index` [0..K-1]
   - Display `np.where(Probs[..., class_index] > threshold)` as a binary overlay image
   - Optional: connected-component size filter — slider `min_voxels` to show only components larger than threshold
9. **Add `ipywidgets.interact` cell for rare-region isolation** — combine probability threshold + connected-component size:
   - Two sliders: `prob_threshold` and `min_component_size`
   - Compute binary mask: `Probs[..., k] > prob_threshold`
   - Run `scipy.ndimage.label` on mask
   - Filter labels by component size
   - Display filtered mask overlay

### Phase 5: 3D Reconstruction Region
10. **Add `extract_high_confidence_mesh()` helper** in notebook 05 (or new `.py` script) —:
    - Input: label volume + class index + confidence/probability volume + confidence threshold
    - Compute binary mask: `(Labels == class_index) & (Confidence > threshold)`
    - Run `skimage.measure.marching_cubes` on mask to get vertices + faces
    - Return mesh dict compatible with `napari.add_surface`
11. **Add napari surface layer cell in notebook 05** —:
    - Extract mesh for each class (or selected class)
    - Add `viewer.add_surface(mesh, name=f"Class {k} surface")`
    - Add sliders to control surface opacity and color
12. **Add clipping / cropping helper** — cell with `ipywidgets.interact` to define a bounding box `[z0, z1, y0, y1, x0, x1]` and crop + re-extract surface from sub-volume

### Phase 6: Uncertainty Interactivity & Diagnostics
13. **Add entropy overlay to napari** — pass `Entropy` to `launch_napari_viewer` as a separate semi-transparent image layer (colormap "hot", opacity 0.3–0.5)
14. **Add slice-wise uncertainty profile plot** — matplotlib line plot:
    - X-axis: Z slice index
    - Y-axis: mean entropy per slice + mean confidence per slice
    - Helps detect non-stationary ambiguity (e.g., middle slices more uncertain)
15. **Add high-uncertainty component table** —:
    - Threshold entropy map at user-defined level
    - Run `scipy.ndimage.label` on high-entropy regions
    - Build pandas DataFrame: component ID, centroid (z,y,x), volume (voxels), mean entropy, dominant competing class (from margin map)
    - Display as HTML table in notebook
16. **Add CSV export cell** — export the above table + material stats report to `.csv` for downstream analysis

### Phase 7: Conclusion Tables & Plots
17. **Add per-slice material fraction table** — loop over Z slices, compute `Compute_Material_Statistics` per slice, assemble into DataFrame, export CSV
18. **Copy BIC curve figure from notebook 03** — embed or reference the BIC plot in notebook 05 for completeness
19. **Add uncertainty vs. intensity scatter** — sample 100k voxels, scatter entropy vs. raw intensity; helps conclude whether ambiguity is boundary-only or noise-driven
20. **Add class co-occurrence adjacency matrix** — count voxel faces where label A touches label B (6-connectivity); validate physical plausibility

## Files to Modify

| File | Action | Phase |
|---|---|---|
| `notebooks/04_spatial_hmrf.ipynb` | Fix `DATA_DIR` path (cell 2) | 1 |
| `notebooks/05_uncertainty_and_visualization.ipynb` | Fix `DATA_DIR` path (cell 2); add all new cells (Phases 3–7) | 1, 3–7 |
| `src/research_ct/visualization/napari_viewer.py` | Add `Entropy`, `Probability_Threshold`, `Render_3d` parameters | 3 |
| `src/research_ct/visualization/export.py` | Fix `export_label_colors` path conflict (user provides code) | 2 |
| `src/research_ct/analysis/uncertainty_maps.py` | May need helper: `Compute_High_Uncertainty_Components` | 6 |
| `src/research_ct/analysis/material_stats.py` | Add CSV-export variant or per-slice stats wrapper | 6, 7 |

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| `napari[all]` may fail to launch on Windows/headless environments | Ensure `%gui qt` or `napari.run()` is called; if napari window freezes, try `jupyter lab` with `ipympl` backend |
| `skimage.measure.marching_cubes` on full volume is memory-heavy | Use `Load_From_Numpy_Slab` to crop sub-volume before mesh extraction; default to 50-slice subset |
| `ipywidgets` sliders unresponsive with large arrays | Pre-compute binary masks once, then slider only toggles display; do not re-run label on every slider movement |
| Probability threshold + connected-component filter yields empty mask | Guard clause: if no components survive filter, print warning and show original mask |
| Data path fix breaks existing saved outputs | After fixing path in 04/05, verify `gmm_probabilities.npy` and `gmm_labels.npy` are discoverable; if not, re-run notebook 03 |

## Validation Steps (user runs after implementation)

1. Run notebook 05 top-to-bottom after path fix — confirm all `Load_From_Numpy` calls succeed
2. Open napari viewer — confirm volume, labels, probability layers, and entropy overlay all render
3. Interact with probability threshold slider — confirm binary mask updates for each class
4. Interact with rare-region slider — confirm small/low-probability components are isolated
5. Extract 3D surface for one class — confirm mesh appears as napari surface layer
6. Crop to sub-volume — confirm marching cubes runs on slab and surface updates
7. Export CSV — confirm `material_stats_per_slice.csv` and `high_uncertainty_components.csv` are written
8. Run export video cell (user-provided fix) — confirm `.mp4` files written
9. Run colored label export cell (user-provided fix) — confirm colored TIFF written

## Dependencies

- Already present: `napari[all]`, `pyvista`, `scikit-image`, `matplotlib`, `ipywidgets`, `imageio`
- **Verify installed:** `pip install -e .` from project root before testing notebook 05
- Optional for CSV tables: `pandas` (or use plain `csv` module if not installed)

## Out of Scope

- **Napari custom `magicgui` widgets** — deferred; static `ipywidgets` in notebook cells is the agreed approach
- **Full pyvista publication figure pipeline** — deferred; only surface extraction for napari is in scope
- **Charles’ geometric integration (page surface normals)** — deferred to future work; only high-confidence ink mask export is added
- **Synthetic validation data** — not in scope for visualization phase

## Open Questions

1. **Does `pandas` need to be added to `requirements.txt`?** The per-slice material table and high-uncertainty component table are easiest with `pandas.DataFrame`. If the user prefers no new dependency, implement using plain `csv` module + dictionaries. **Recommendation:** add `pandas>=2.0.0` to `requirements.txt` and `pyproject.toml` under dependencies.
2. **Notebook execution order after path fix:** If notebook 04/05 path fix means they now look in `data/output/` but previous runs saved to `src/research_ct/data/output/`, user may need to either move files or re-run notebook 03. Plan assumes user will handle this.
