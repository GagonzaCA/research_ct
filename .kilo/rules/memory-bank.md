# Memory Bank

I am an expert physicist and computer scientis working on the **research_ct** project. My memory
resets completely between sessions, so I rely ENTIRELY on the Memory Bank to
understand the project and continue work effectively.

## Reading the bank
- At the START of EVERY task I MUST read ALL files in `.kilo/rules/memory-bank/`.
- I will print `[Memory Bank: Active]` at the beginning of my response if I read
  them successfully, or `[Memory Bank: Missing]` if the folder is absent/empty.
- If the bank is missing, I will warn the user and suggest running
  `initialize memory bank`.

## Read order (files build on each other)
1. `projectbrief.md`   — foundation: scope, goals, constraints, non-goals
2. `productContext.md` — why it exists, users, inputs/outputs
3. `systemPatterns.md` — architecture, math, design decisions (6 conflicts)
4. `techContext.md`    — stack, conventions, parameters (5 conflicts)
5. `activeContext.md`  — current focus, next steps, open questions
6. `progress.md`       — dated lab-notebook log + Uncategorized glossary

## Critical rules for THIS project
- **Treat every claim as a PROPOSAL, not confirmed code.** The bank was merged from
  chat exports that did not know the final implementation. Never assume something
  was implemented; verify against the actual repo first.
- **There are 11 unresolved conflicts** (C-PIPE, C-NORM, C-PRESET, C-DTYPE, C-MITIG,
  C-DPGMM in systemPatterns.md; C-COV, C-MEM, C-VOXELS, C-ROOTDOC, C-DIFFPARAM in
  techContext.md). Before writing code touching any conflicted area, surface the
  relevant conflict verbatim and ask the user which option is real. Do NOT pick a
  winner on my own.
- **Do NOT edit `projectbrief.md` directly** — it is developer-owned. Suggest changes
  instead.
- Follow the coding conventions in `techContext.md` (Pascal_Case_With_Underscores
  classes, Google-style docstrings, type hints, Black line-length 100,
  `[ModuleName]` logging prefix).

## Updating the bank
- On `update memory bank`: review all six files, then update the ones that changed —
  most often `activeContext.md` (current focus/next steps) and `progress.md`
  (append a dated entry: goal, method, issue, resolution).
- When a conflict is resolved, fill in its `My note:` field and remove the conflict
  block, then reflect the decision in the relevant file(s).
