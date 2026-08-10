# Memory Bank — research_ct

> Persistent project context for the **research_ct** project (Unsupervised Material Segmentation for Micro-CT of Sealed Historical Books).
> Author: Gabriel Augusto Gonzalez Lozano — University of Western Ontario.
> Purpose: give the AI coding agent (Kimi 2.6 via Kilo Code) durable, structured memory so you never re-explain the project between sessions.
>
> ⚠️ **These files were merged from three chat exports and are treated as PROPOSALS, not confirmed code.** All 11 original conflicts have been resolved (2026-07-29). Verify claims against real repo.

---

## 1. File Index (read order)

The six files build on each other. An agent should read them top-to-bottom to orient itself:

| # | File | What it holds | Update frequency |
|---|------|---------------|------------------|
| 1 | **projectbrief.md** | Foundation: scope, core requirements, objectives (O1–O6), stretch goals (S1–S4), constraints, success criteria, non-goals | Rarely (only if scope changes) |
| 2 | **productContext.md** | Why it exists, the problem, prior art, users/consumers, inputs/outputs, Charles integration, long-term vision | Rarely |
| 3 | **systemPatterns.md** | Architecture, package layout, math foundations (GMM/EM/BIC, hierarchy/LRT, HMRF/Potts/ICM, preprocessing), design decisions, data structures. **All 6 conflicts resolved** | When architecture/algorithms change |
| 4 | **techContext.md** | Stack + versions, why-not-R, conventions, naming, setup commands, entry points, parameter cheat sheet, tests, notebooks. **All 5 conflicts resolved** | When deps/tooling change |
| 5 | **activeContext.md** | Current focus, recent (claimed) changes, next steps, open questions, risks, assumptions to monitor | **Most frequently — every session** |
| 6 | **progress.md** | Dated lab-notebook log: goals attempted, methods, issues, resolutions, timeline, contingencies, `## Uncategorized` glossary | **Frequently — after each work chunk** |

```
projectbrief.md ──► productContext.md ─┐
                ──► systemPatterns.md ─┤
                ──► techContext.md ────┤
                                       ▼
                                 activeContext.md ──► progress.md
```

---

## 2. Using this with Kilo Code (Kimi 2.6) in VS Code

> This memory bank uses the **modern `.kilo/` directory** (Kilo Code v7, GA April 2026). The older `.kilocode/` name still works as a read-only fallback, but `.kilo/` is current and takes precedence. Do NOT keep both — if `.kilo/` and `.kilocode/` both exist, `.kilo/` silently wins, which causes confusion.

### 2a. Where these files live
```
your-repo/
├── kilo.jsonc                        ← tells Kilo which rule files to load
└── .kilo/
    └── rules/
        ├── memory-bank.md            ← the "always read the bank" instruction
        └── memory-bank/              ← THIS folder (the 6 files + this README)
```

Kilo loads rule files at session start via the `instructions` array in `kilo.jsonc`. A minimal config (place at repo root):
```jsonc
{
  "$schema": "https://app.kilo.ai/config.json",
  "instructions": [".kilo/rules/*.md"]
}
```
> `.kilo/kilo.jsonc` also works and takes priority over a root-level `kilo.jsonc` if both exist — pick one.

### 2b. The rules file (`.kilo/rules/memory-bank.md`)
A companion `memory-bank.md` sits one level up from this folder. It instructs the agent to read ALL six files at the start of every task, print `[Memory Bank: Active]`, treat everything as a proposal until verified, and never edit `projectbrief.md` directly. (A ready-made copy ships alongside this README.)

### 2c. Core commands (type these in the Kilo chat)
| Command | What it does |
|---------|--------------|
| `follow your custom instructions` | Kilo re-reads the memory bank and resumes where you left off (use at the start of a new session) |
| `initialize memory bank` | Builds/refreshes the bank from a full repo scan (content is already written manually — use only to regenerate) |
| `update memory bank` | Full review + update of all files (do this before you run out of context or end a session) |

> Migrating from an older Kilo? If your repo currently has `.kilocode/rules/memory-bank/`, just move it:
> ```bash
> mkdir -p .kilo/rules
> git mv .kilocode/rules/memory-bank .kilo/rules/memory-bank   # (or plain mv)
> git mv .kilocode/rules/memory-bank.md .kilo/rules/memory-bank.md 2>/dev/null || true
> ```
> Then delete the now-empty `.kilocode/` to avoid the "both exist" trap.

### 2d. Recommended session loop
1. **Start:** `follow your custom instructions` → confirm `[Memory Bank: Active]`.
2. **Work:** ask Kilo to do the task (see prompts below).
3. **Before context fills / end of session:** `update memory bank` (or ask it to update only `activeContext.md` + `progress.md`).
4. **Log it:** add a row to the Work Log in §4.

> 💡 Future-proofing: Kilo v7 increasingly favors a root-level `AGENTS.md` over the memory bank. This six-file structure still works today; if you ever want to consolidate, ask Kilo to migrate this content into `AGENTS.md`.

---

## 3. Common prompts for frequent activities

Copy-paste starters, grouped by activity. All assume the bank is loaded.

### 🟢 Orientation / start of session
- `follow your custom instructions and give me a 5-line status: current focus, last change, next step, top risk, and any unresolved conflict.`
- `Read activeContext.md and progress.md. What was I doing last, and what's the single next action?`

### 🔵 Preprocessing (C-PIPE resolved: pipeline_revised.py for GMM, pipeline.py for visualization)
- `Both pipelines are implemented. Use pipeline_revised.py (Preprocess_For_Gmm_Revised) for GMM input; pipeline.py (Preprocess_For_Gmm) for visual comparisons.`
- `Implement the Gmm_Ready preset per techContext.md. NO thresholding. Flag any parameter that conflicts with the cheat sheet.`

### 🟣 Segmentation (GMM / hierarchy / HMRF)
- `Implement Gmm_Fitter.Fit() with BIC-based K selection over K_min=2..K_max=8, k-means++ init, per techContext.md conventions. Add a test in tests/test_segmentation/test_gmm_fitter.py.`
- `Check C-COV before setting covariance_type. Tell me which default (full vs tied) you're using and why.`
- `Draft hmrf.py ICM loop using the energy equation in systemPatterns.md (6-connectivity default). Keep it runnable on a 50-slice subset first.`

### 🟡 Testing & quality
- `Run pytest mentally over gmm_fitter.py: list edge cases missing (empty input, constant image, shape mismatch) and write the missing tests.`
- `Enforce techContext.md conventions: Google-style docstrings, type hints, Black line-length 100, [ModuleName] logging prefix. Flag violations in this file.`

### 🟠 Debugging
- `EM won't converge. Walk the §6.3 checklist from activeContext.md (data range, max_iter, covariance_type, K_max, NaN/Inf) against my code.`
- `HMRF is too slow. Apply the §6.4 fixes and tell me which one you changed.`

### 🔴 Conflict resolution (do these against real code)
- `Show me Conflict <C-ID> verbatim. I'll tell you the real answer; then update that file's My note field and remove the conflict block.`
- `List all 11 conflicts with their current My note status (blank vs resolved).`

### 🟤 Maintenance / end of session
- `update memory bank — but only touch activeContext.md and progress.md. Add today's dated entry: goal, method, issue, resolution.`
- `Summarize what changed in the repo this session in 5 bullets, then append them to progress.md as a dated entry.`

---

## 4. Work tracking

### 4a. Conflict resolution — ALL RESOLVED (2026-07-29)

**systemPatterns.md (6/6 ✅)**
- [x] **C-PIPE** — pipeline_revised.py (C) for GMM; pipeline.py (A/B) for visualization
- [x] **C-NORM** — normalization.py deleted; global_normalization.py is sole module
- [x] **C-PRESET** — config.py kept; Real_Ct is legacy/visualization-only
- [x] **C-DTYPE** — float64 throughout (Option A). pipeline_revised.py casts to float64 at entry.
- [x] **C-MITIG** — Background correction + mild Gaussian smoothing (Option B)
- [x] **C-DPGMM** — dp_gmm.py planned for implementation; Dp_Gmm_Fitter for notebook segmentation

**techContext.md (5/5 ✅)**
- [x] **C-COV** — Covariance_Type default "full" (Option A). Code-verified: gmm_fitter.py line 21.
- [x] **C-MEM** — Flexible approach. Local 32 GB; external up to ~564 GB. Default float64.
- [x] **C-VOXELS** — ~750M voxels (201 slices × ~1900 × ~1900). Other books may be larger.
- [x] **C-ROOTDOC** — LABORATORY_NOTEBOOK.md not in repo root (Option B).
- [x] **C-DIFFPARAM** — Both parameter sets coexist. Option B (GMM) + Option A (visualization).

> Minor (not a formal conflict): Lab Notebook Appendix B targets `src/` for black/mypy/flake8 while AI_CONTEXT §1.4 targets `research_ct/`. Reconcile when convenient.

### 4b. Known gaps to fill (from Merge Report)
- [ ] Verify "Week 0 completed" module list in progress.md against the actual repo (claims, not confirmed).
- [x] Confirm true DP-GMM status — **decided: will be implemented** (ties to C-DPGMM).
- [ ] Add concrete raw volume dimensions / voxel size (~750M voxels, 201 slices per C-VOXELS resolution).
- [ ] Decide `page_extractor.py` scope (currently an intentional placeholder for Charles' integration).
- [ ] Clarify whether "adhesive" is a first-class target class in the K enumeration.

### 4c. Work Log (append newest at top)
Add a row each session so future-you (and the agent) can trace history.

| Date | Focus | What was done | Files touched | Conflicts resolved | Next step |
|------|-------|---------------|---------------|--------------------|-----------|
| 2026-07-29 | Conflict resolution | Resolved all 8 remaining: C-DTYPE, C-MITIG, C-DPGMM, C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM. All 11 done. | systemPatterns.md, techContext.md, activeContext.md, progress.md, README.md | all 11 | Begin DP-GMM implementation |
| 2026-07-29 | Conflict resolution | Resolved C-PIPE, C-NORM, C-PRESET (first batch of 3) | systemPatterns.md, activeContext.md, progress.md, README.md | C-PIPE, C-NORM, C-PRESET | Continue remaining 8 |
| 2026-07-28 | Memory bank setup | Merged 3 sources → 6 files + README; laid out under .kilo/ | all | none yet | Wire into Kilo; start C-PIPE |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

---

## 5. Source provenance
Merged **only** from these three approved files (kimi.md was explicitly excluded):
- `AI_CONTEXT.md` (Last Updated 2026-07-10) — older CLAHE/Perona-Malik pipeline
- `AI_CONTEXT_2.md` (Last Updated 2026-07-28) — revised Gaussian pipeline + DP-GMM
- `LABORATORY_NOTEBOOK.md` — full theory, methodology, bibliography, timeline, status

Rules honored during merge: zero information loss; claims treated as proposals; contradictions preserved verbatim under `## ⚠️ Conflicts to Resolve`; technical specifics kept verbatim; source-tagged; code replaced with one-line summaries.
