# Plan: Notebook Refactoring for DP-GMM Integration

**Date:** 2026-07-31
**Goal:** Non-destructive refactoring of all Jupyter notebooks — preserve existing content, rename files, add Sparse_Bayesian_Gmm and Hierarchical_Gmm sections to notebook 03.

---

## Naming Mismatch Resolution (Verified Against Actual Files)

| Current File | User Scheme Claimed | Actual Status | Resolution |
|---|---|---|---|
| `01_explore_data.ipynb` | `01_explore_raw_data.ipynb` | Exists | ✅ Rename |
| `02_preprocessing_demo.ipynb` | `02_run_preprocessing.ipynb` | Exists | ✅ Rename |
| `03_gmm_fitting.ipynb` | `03_gmm_and_hierarchical_segmentation.ipynb` | Exists | ✅ Rename + add sections |
| `4_hmrf_spatial.ipynb` | `04_spatial_hmrf.ipynb` (from `05_spatial_hmrf.ipynb`) | Exists as `4_hmrf_` | ✅ Rename to `04_spatial_hmrf.ipynb` |
| `05_visualization.ipynb` | `05_uncertainty_and_visualization.ipynb` (from `06_`) | Exists as `05_` | ✅ Rename |
| `04_hierarchical_segmentation.ipynb` | Mentioned in merge plan | **Does NOT exist** | ❌ No source to merge — create content from `hierarchy.py` module instead |

**Key finding:** There is no `04_hierarchical_segmentation.ipynb`. The "merge" means adding `Hierarchical_Gmm` demonstration content (from `src/research_ct/segmentation/hierarchy.py`) into notebook 03.

---

## Task 1: File Renames (5 files)

Execute in order to maintain notebook references:

1. `01_explore_data.ipynb` → `01_explore_raw_data.ipynb`
2. `02_preprocessing_demo.ipynb` → `02_run_preprocessing.ipynb`
3. `03_gmm_fitting.ipynb` → `03_gmm_and_hierarchical_segmentation.ipynb`
4. `4_hmrf_spatial.ipynb` → `04_spatial_hmrf.ipynb`
5. `05_visualization.ipynb` → `05_uncertainty_and_visualization.ipynb`

**No content changes** for renames — purely file-system operations.

---

## Task 2: Notebook 03 — Add Sparse_Bayesian_Gmm Section

**Location:** Insert AFTER "Material Statistics" section (line 146), BEFORE "Assign Labels to Full Volume" section (line 148).

**New markdown cell:**
```markdown
## Sparse Bayesian GMM (Alternative K Discovery)

Dirichlet-Process GMM automatically discovers the number of components without BIC scanning. Components with negligible weight are pruned.
```

**New code cell:**
```python
from research_ct.segmentation.sparse_bayesian_gmm import Sparse_Bayesian_Gmm

# Fit overcomplete Sparse Bayesian GMM
Sparse_Model = Sparse_Bayesian_Gmm(
    Max_Components=10,
    Weight_Concentration_Prior=1.0,
    Weight_Threshold=1e-3,
    Min_Samples=1000,
    Covariance_Type="full",
)
Sparse_Model.Fit(Sampled, Verbose=True)

# Inspect active component pruning results
Material_Stats = Sparse_Model.Get_Material_Statistics()
print(f"Active components: {Sparse_Model.Num_Active_Components}/{Sparse_Model.Max_Components}")
print("Active Means:", Material_Stats["Means"])
print("Active Weights:", Material_Stats["Weights"])
print("Active Indices:", Material_Stats["Active_Indices"])
```

**New markdown cell:**
```markdown
### Compare BIC-GMM vs Sparse Bayesian GMM

Side-by-side comparison of discovered components.
```

**New code cell:**
```python
print(f"BIC-GMM selected K={Fitter.Num_Components}")
print(f"Sparse Bayesian GMM discovered K_active={Sparse_Model.Num_Active_Components}")

# Tabular comparison
print("\n{'Method':<25} {'K':<5} {'Means'}")
print("-" * 60)
print(f"{'BIC-GMM':<25} {Fitter.Num_Components:<5} {Stats['Means']}")
print(f"{'Sparse Bayesian GMM':<25} {Sparse_Model.Num_Active_Components:<5} {Material_Stats['Means']}")
```

---

## Task 3: Notebook 03 — Add Hierarchical_Gmm Section

**Location:** Insert AFTER Sparse_Bayesian_Gmm section, BEFORE "Assign Labels to Full Volume".

**New markdown cell:**
```markdown
## Hierarchical GMM Refinement

Recursively split components if statistically justified (BIC + LRT). Each split corresponds to a physical material subdivision.
```

**New code cell:**
```python
from research_ct.segmentation.hierarchy import Hierarchical_Gmm

# Build hierarchical tree from BIC-selected GMM
Hgmm = Hierarchical_Gmm(
    Min_Samples=1000,
    Max_Depth=5,
    Significance_Alpha=0.05,
)
Hgmm.Fit(Sampled, Initial_K=Fitter.Num_Components)

Leaves = Hgmm.Get_Leaf_Components()
print(f"Hierarchical refinement: {Fitter.Num_Components} → {len(Leaves)} leaf components")

# Print leaf statistics
for i, Leaf in enumerate(Leaves):
    print(f"Leaf {i}: μ={Leaf['Mean']:.2f}, σ²={Leaf['Variance']:.2f}, "
          f"N_eff={Leaf['Effective_Samples']:.0f}, depth={Leaf['Depth']}")
```

**New markdown cell:**
```markdown
### Hierarchical Leaf Probabilities

Soft path probabilities across the tree. Sum over leaves = 1.0 per voxel.
```

**New code cell:**
```python
Leaf_Probs = Hgmm.Predict_Leaf_Probabilities(Sampled)
print(f"Leaf probabilities shape: {Leaf_Probs.shape}")
print(f"Row sums (should be 1.0): min={Leaf_Probs.sum(axis=1).min():.6f}, max={Leaf_Probs.sum(axis=1).max():.6f}")
```

---

## Task 4: API Alignment Verification

**Status:** All notebooks already use PascalCase API correctly.

| Notebook | Method Calls | Status |
|---|---|---|
| 01 | `Load_Slice_Stack`, `Load_Metadata` | ✅ PascalCase |
| 02 | `Preprocess_For_Gmm_Revised`, `Plot_Histogram_Comparison` | ✅ PascalCase |
| 03 | `Predict_Probabilities`, `Get_Material_Statistics`, `Fit` | ✅ PascalCase |
| 04 | `Hmrf_Segmenter`, `Compute_Labels_From_Probabilities` | ✅ PascalCase |
| 05 | `Compute_Material_Statistics`, `Compute_Uncertainty`, `Compute_Margin` | ✅ PascalCase |

**Action:** No API changes needed. Confirm during validation.

---

## Task 5: Memory Efficiency Verification

**Status:** Notebooks already use 1D memory views where needed.

| Notebook | Line | Pattern | Status |
|---|---|---|---|
| 03 | 55 | `Processed.ravel().reshape(-1, 1)` | ✅ Memory view |
| 03 | 218 | `Processed.ravel().reshape(D, H, W)` | ✅ Reshape back |
| 05 | 162 | `Sample.reshape(-1, 1)` | ✅ Memory view |

**Action:** No changes needed. New sections in notebook 03 must follow same pattern:
- `Sampled.reshape(-1, 1)` when passing to `Sparse_Model.Fit()`
- `Sampled.reshape(-1, 1)` when passing to `Hgmm.Fit()`

---

## Task 6: Notebook 04 Content Check

**Current file:** `4_hmrf_spatial.ipynb` → target `04_spatial_hmrf.ipynb`

**Observation:** Notebook 04 already contains a "Visual Pipeline" section (lines 158-180) that demonstrates the OLD `pipeline.py` (Preprocess_For_Gmm with CLAHE/diffusion). This conflicts with the active `pipeline_revised.py`.

**Decision:** This section is visualization-only and uses the legacy pipeline. Per C-PIPE resolution (pipeline.py retained for visualization), this is correct. **No changes needed.**

---

## Task 7: Notebook 05 Content Check

**Current file:** `05_visualization.ipynb` → target `05_uncertainty_and_visualization.ipynb`

**Observation:** Notebook 05 re-fits GMM for plotting (lines 158-173). This is additive and safe.

**Decision:** No content changes needed. Rename only.

---

## Validation Checklist

- [ ] All 5 files renamed correctly
- [ ] Notebook 03 has new Sparse_Bayesian_Gmm section (after Material Statistics)
- [ ] Notebook 03 has new Hierarchical_Gmm section (after Sparse Bayesian)
- [ ] All existing cells in notebook 03 preserved
- [ ] API calls use PascalCase throughout
- [ ] Memory views (.reshape(-1, 1)) used in new sections
- [ ] Imports work: `from research_ct.segmentation import Sparse_Bayesian_Gmm, Hierarchical_Gmm`
- [ ] Notebook 04 and 05 content unchanged (renames only)

---

## Open Questions (None — plan is implementation-ready)

All naming mismatches resolved. All content decisions made. Plan ready for execution.
