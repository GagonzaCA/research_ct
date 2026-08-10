# XRF BCF Preprocessing Integration Plan

## Goal
Absorb `bcd_io.py` — a Bruker `.bcf` hypercube extractor that performs dynamic emission-line lookup and dual-window Bremsstrahlung subtraction — into the `research_ct` project as the first XRF preprocessing step. Provide a clear data layout for BCF inputs / TIFF outputs, enforce a uniform output nomenclature, and add a non-numeric notebook that demonstrates end-to-end BCF → elemental TIFF extraction.

---

## Context & Current State
- The XRF sub-package already lives under `src/xrf/` and consumes elemental TIFFs (see `src/xrf/io/xrf_loader.py`).
- Existing XRF notebooks are numbered (`01_xrf_loading_and_masking.ipynb` … `07_rarity_review.ipynb`). The new notebook must **not** receive a numeric prefix.
- `bcd_io.py` uses `hyperspy`, `exspy`, `numpy`, and `tifffile`. Only `numpy` and `tifffile` are currently declared in `requirements.txt` / `pyproject.toml`.
- `data/xrf/raw/` already exists and contains mixed-casing TIFFs from earlier extractions (e.g. `Letter_1_Fe_Ka.tiff`, `letter_1_Fe.tif`). The new extractor must produce **exactly** one predictable schema.
- `data/xrf/bcf/` does **not** exist yet and must be created for incoming raw instrument files.

---

## Decisions Already Confirmed with User

| Question | Decision |
|---|---|
| Notebook naming | New notebook **must not** have a numeric prefix (e.g. `xrf_bcf_extraction.ipynb`). |
| Data layout | Project-level `data/xrf/` tree: `data/xrf/bcf/` for inputs, `data/xrf/raw/` for extracted element TIFFs. |
| Output filename schema | `{sample_name}_{element_line}_raw.tiff` — always includes the sample/page name derived from the BCF stem, the resolved element line, and the literal suffix `raw`. |
| Module placement | Treat BCF extraction as **preprocessing** inside `src/xrf/preprocessing/` (new sub-package). |

---

## Detailed Action List

### 1. Directory scaffolding
- Create `data/xrf/bcf/` and drop a `.gitkeep` inside it so git preserves the folder.
- Ensure `data/xrf/raw/` also contains a `.gitkeep` (it may already exist but may lack the marker).

### 2. Dependency updates
- Add `hyperspy>=2.0.0` and `exspy` to:
  - `requirements.txt`
  - `pyproject.toml` under `[project] dependencies`
- Rationale: `bcd_io.py` imports `hyperspy.api` and `exspy.material.elements`.

### 3. Refactor `bcd_io.py` into the XRF package
Create `src/xrf/preprocessing/bcf_extractor.py` with the following refactor checklist:
- **Class name:** `Bcf_Element_Extractor` (Pascal_Case_With_Underscores per project convention).
- **Method names:**
  - `__init__(…)` with extraction hyperparameters.
  - `Resolve_Emission_Line(Element_Input: str) -> Tuple[float, str]`
  - `Extract_And_Save(Bcf_File_Path, Output_Dir, Target_Elements)` — runs the full pipeline.
- **Filename formatting:**
  - `sample_name` = `Path(Bcf_File_Path).stem`
  - `resolved_tag` = symbol + underscore + line (e.g. `Fe_Ka`)
  - Output file: `f"{sample_name}_{resolved_tag}_raw.tiff"`
- **Output path logic:** default `Output_Dir` should resolve to `data/xrf/raw/` relative to the project root (use a Path constant or accept an explicit argument).
- **Code style:**
  - Google-style docstrings on every public method/class.
  - Type hints throughout (`Path_Like = Union[str, Path]`).
  - `[Bcf_Extractor]` logging prefix for print/progress statements.
  - Keep dual-window Bremsstrahlung subtraction and dynamic K-alpha/L-alpha logic unchanged.
  - Preserve TIFF metadata tags: `{"element": resolved_tag, "energy_kev": center_energy}`.
  - Remove the `if __name__ == "__main__":` block from the module file (it belongs in the notebook or a CLI script, not in a library module).

### 4. Add configuration dataclass
Extend `src/xrf/config.py` with a new dataclass:
```python
@dataclass
class Bcf_Extraction_Config:
    Cutoff_At_Kv: float = 40.0
    Peak_Width_Kev: float = 0.20
    Bg_Width_Kev: float = 0.10
    Bg_Offset_Kev: float = 0.25
    Output_Dir: Path = field(default_factory=lambda: Path("data/xrf/raw"))
```
Ensure `Bcf_Element_Extractor` can optionally accept a `Bcf_Extraction_Config` instance.

### 5. Register the new sub-package
- Create `src/xrf/preprocessing/__init__.py` that exports `Bcf_Element_Extractor`.
- Update `src/xrf/__init__.py` to import `Bcf_Element_Extractor` so it is reachable via `from xrf import Bcf_Element_Extractor`.

### 6. Create the preprocessing notebook
- **Location:** `notebooks/xrf/xrf_bcf_extraction.ipynb`
- **Naming rule:** Must contain no numeric prefix or ordinal index.
- **Contents (cell group outline):**
  1. Imports (`Bcf_Element_Extractor`, `Bcf_Extraction_Config`, `Path`).
  2. Constants / paths: point to `data/xrf/bcf/` for input and `data/xrf/raw/` for output.
  3. Discover available `.bcf` files in the input directory.
  4. Define a human-readable element list using **string symbols only** (e.g. `["Fe", "Cu", "Au", "Hg", "Pb", "Ca", "K", "As"]`).
  5. Instantiate `Bcf_Element_Extractor` with default or custom config.
  6. Run `Extract_And_Save` in a loop over discovered BCF files.
  7. Verification cell: glob `data/xrf/raw/` and assert every output filename matches `{*}_{*}_raw.tiff` (no legacy `.tif`, no missing `_raw` tag).
  8. Optional: display the first extracted map with `matplotlib` for sanity checking.
- **Constraint:** No hard-coded numeric indices anywhere (no `files[0]`, no element selection by position). Iterate over lists by value or use dictionary mapping by element name.

### 7. Update `.gitignore`
- Add explicit rules to keep BCF files out of git:
  ```
  data/xrf/bcf/*
  !data/xrf/bcf/.gitkeep
  ```
- `*.tif` and `*.tiff` are already ignored globally, so the output TIFFs in `data/xrf/raw/` are already protected.
- `*.bcf` may also be added globally if desired.

### 8. Validation steps
After implementation, verify in order:
1. `python -c "from xrf import Bcf_Element_Extractor; print('OK')"`
2. `python -c "from xrf.config import Bcf_Extraction_Config; print('OK')"`
3. Confirm `hyperspy` and `exspy` import without error in the activated venv.
4. Run the `xrf_bcf_extraction.ipynb` notebook top-to-bottom on a sample BCF.
5. Inspect `data/xrf/raw/` and confirm every new TIFF follows `{sample}_{element_line}_raw.tiff`.
6. Confirm existing mixed-case legacy files (e.g. `letter_1_Fe.tif`) are **not** overwritten by the new extractor; the new explicit `_raw.tiff` suffix prevents collision.

### 9. Optional cleanup (post-validation)
- Consider a migration helper or one-off script to rename/delete legacy TIFFs in `data/xrf/raw/` that do **not** follow the agreed schema, so downstream notebooks load a clean, predictable directory.

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| `hyperspy` / `exspy` unavailable on Windows or install fails | High | Pin tested versions in `requirements.txt`; add `[Bcf_Extractor]` lazy import note so the rest of `xrf` loads even if hyperspy is missing. |
| BCF file size causes memory exhaustion | Medium | `bcd_io.py` already streams through the hypercube per-element; document in the notebook that extraction runs one element at a time, not requiring full cube in RAM. |
| Existing legacy TIFFs (`.tif`, mixed case) confuse downstream loaders | Medium | Validation step #6 checks for collisions; optional cleanup script standardizes the directory. |
| `data/xrf/bcf/` not ignored by git | Low | Explicit `.gitignore` entry added in step 7. |

---

## Out of Scope
- Does **not** modify the seven existing numbered XRF notebooks.
- Does **not** refactor the CT pipeline in `src/research_ct/`.
- Does **not** create a CLI wrapper or `__main__` entry point for `bcd_io.py`.

---

## Successful Outcome
- `data/xrf/bcf/` exists with `.gitkeep`.
- `src/xrf/preprocessing/bcf_extractor.py` is importable and tested.
- `notebooks/xrf/xrf_bcf_extraction.ipynb` runs end-to-end and produces files like `Letter_1_Fe_Ka_raw.tiff`.
- Project dependencies include `hyperspy` and `exspy`.
