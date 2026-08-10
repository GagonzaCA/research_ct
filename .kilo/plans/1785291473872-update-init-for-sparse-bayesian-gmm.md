# Plan: Update __init__.py for Sparse_Bayesian_Gmm Export

**Date:** 2026-07-31
**Context:** User created `sparse_bayesian_gmm.py` with `Sparse_Bayesian_Gmm` class in the segmentation folder. This is a parallel/independent method to `Gmm_Fitter`, not a drop-in replacement.

---

## Decision Log

| Decision | Status | Rationale |
|----------|--------|-----------|
| Keep file name `sparse_bayesian_gmm.py` | ✅ Confirmed | User explicitly said "Keep names as established, do not change" |
| Keep class name `Sparse_Bayesian_Gmm` | ✅ Confirmed | User explicitly said "do not change" |
| Do NOT rename to `dp_gmm.py` / `Dp_Gmm_Fitter` | ✅ Confirmed | Original memory-bank plan for interface parity is abandoned |
| Do NOT modify notebooks 03 and 04 | ✅ Confirmed | User explicitly said "Do not change anything in notebooks" |
| New method is independent/parallel to Gmm_Fitter | ✅ Confirmed | User explicitly said "this new methods is independent form GMM_fitter, is parallel" |

---

## Task 1: Update `segmentation/__init__.py`

**File:** `src/research_ct/segmentation/__init__.py`

**Current state (6 lines):**
```python
"""Core segmentation algorithms."""

from .gmm_fitter import Gmm_Fitter
from .decision_engine import Segmentation_Engine

__all__ = ["Gmm_Fitter", "Segmentation_Engine"]
```

**Required change:** Add import and export for `Sparse_Bayesian_Gmm`.

**Target state:**
```python
"""Core segmentation algorithms."""

from .gmm_fitter import Gmm_Fitter
from .sparse_bayesian_gmm import Sparse_Bayesian_Gmm
from .decision_engine import Segmentation_Engine

__all__ = ["Gmm_Fitter", "Sparse_Bayesian_Gmm", "Segmentation_Engine"]
```

**Validation:**
```bash
python -c "from research_ct.segmentation import Sparse_Bayesian_Gmm; print('OK')"
```

---

## Task 2: Notebooks — No Changes Required

**Notebooks 03 (`03_gmm_fitting.ipynb`) and 04 (`4_hmrf_spatial.ipynb`):**

- **03** uses `Gmm_Fitter` with BIC-based K selection. The `Sparse_Bayesian_Gmm` is a parallel method, not a replacement.
- **04** loads GMM probabilities and applies HMRF. No dependency on the new class.
- **User explicitly instructed:** "Do not change anything in notebooks."

**Rationale for no changes:**
- `Sparse_Bayesian_Gmm` has a different interface from `Gmm_Fitter` (no `Bic_Scores`, no `Num_Components`, has `Active_Indices`, `Num_Active_Components`).
- It cannot be dropped into the existing notebook cells without interface modifications.
- The user confirmed it is an independent/parallel method, not a replacement.

---

## Optional Future Work (Out of Scope for This Plan)

If the user later wants a dedicated notebook for `Sparse_Bayesian_Gmm`:

- **Suggested file:** `notebooks/03b_bayesian_gmm.ipynb` (parallel to 03)
- **Content:** Fit `Sparse_Bayesian_Gmm` on the same preprocessed data, compare discovered K with BIC-selected K, visualize component distributions.
- **This is NOT part of the current plan.**

---

## Validation Checklist

- [ ] `segmentation/__init__.py` imports `Sparse_Bayesian_Gmm`
- [ ] `segmentation/__init__.py` exports `Sparse_Bayesian_Gmm` in `__all__`
- [ ] `python -c "from research_ct.segmentation import Sparse_Bayesian_Gmm"` succeeds
- [ ] Notebooks 03 and 04 remain unchanged
