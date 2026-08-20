# Loop 5 — postproc-tests

## Carry
slug: postproc-tests | branch: feature/postproc-tests (base: feature/f1-procedural-spine — F1 core not yet merged to develop) | root: /mnt/workspace/code/isoroll-content
test-cmd: `/mnt/workspace/.venv/bin/python3 -m pytest test/ -q` | e2e-cmd: none
criticality: normal | verdict: standard
criteria: C1 — pytest suite exists, green, covering sheet_grid.detect_grid + strip_linework on synthetic magenta-grid fixtures
  C2 — guide_marks.residue_count tested: synthetic image with K cyan symbols → count in expected band; 0 on clean image
  C3 — new silhouette-IoU QC function (own file ≤200 LOC) comparing an NB output cell's silhouette vs the guide box mask; unit tests: ≈1.0 identical masks, <0.5 disjoint
  C4 — sheet_postproc split tolerates ±2px grid-line drift on a synthetic sheet (test proves it)
  C5 — `make verify-fast` still green; every file ≤200 LOC; no NB/API calls in tests
tasks: T1 — pytest bootstrap (pytest.ini + conftest sys.path src/cli+src/pipeline + fixtures.py) — pytest.ini,test/conftest.py,test/fixtures.py — medium
  T2 — test detect_grid+strip_linework (C1) — test/test_sheet_grid.py — medium
  T3 — test ±2px drift snap (C4) — test/test_grid_drift.py — medium
  T4 — test residue_count (C2) — test/test_guide_marks.py — medium
  T5 — new QC module silhouette_iou + tests (C3) — src/cli/sheet_qc.py,test/test_sheet_qc.py — medium
  T6 — wire pytest into verify-fast, full gate green (C5), harden split only if T3 red — Makefile,src/cli/sheet_postproc.py(if needed) — medium
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, src/cli/CONTEXT.md, src/pipeline/CONTEXT.md, ROADMAP-content-gen.md

## User Test

scenario: As the isoroll artist, I generate a tile guide for a 3x2 wall, overlay
the cyan registration marks, send it off, and get back an NB render. NB mostly
repaints the sheet but leaves a few registration marks un-keyed in one corner
panel. I run the guide through the postproc pipeline: split the sheet into its
cells, check that no cyan residue survived (it did, in that one panel — QC
should catch it), and check that each cell's silhouette still lines up with
the guide's own box for that cell (it should, everywhere, since NB followed
the guide even where it left marks behind).

script: test/e2e_scenario.py run: `/mnt/workspace/.venv/bin/python3 test/e2e_scenario.py`

Chains: make_tile_guide.py (subprocess, cwd=src/pipeline, real 6cell 3x2 guide)
→ guide_marks.py CLI (subprocess, cwd=src/pipeline, overlays marks) → in-process
simulated "NB output" (silhouette-preserving recolor of the guide + a patch of
the real cyan marks pasted back into the NW panel as leaked residue) →
sheet_postproc.py CLI (subprocess, cwd=src/cli, --keep-bg so no rembg/network
call per C5 — the real detect_grid + split_cells + strip_linework path) run
against both the dirty output and the clean guide → guide_marks.residue_count
and sheet_qc.silhouette_iou (RGB/luminance path, so it scores drawn content
rather than the strip_linework alpha channel) evaluated on the split cells.

observed:
```
[1/5] make_tile_guide.py -> .../guide.png
Saved: .../guide.png  (960x640 px, 6cell, W3xH2xD1)
[2/5] guide_marks.py -> .../marked.png
Saved: .../marked.png
[3/5] simulating NB output: recolor + leave residue in NW panel
[4/5] sheet_postproc.py grid split (--keep-bg: no rembg/network call)
[5/5] sheet_qc + guide_marks metrics
  residue_count(dirty nb output) = 2078
  residue_count(clean guide)     = 0
  silhouette_iou[NW] = 0.9599
  silhouette_iou[NE] = 0.9999
  silhouette_iou[TOP] = 0.9997
  silhouette_iou[SW] = 0.9998
  silhouette_iou[SE] = 0.9998
RESULT residue_detected=True iou_high=True
PASS
```
Exit code: 0. `make verify-fast` re-checked after the commit: `8 passed, 14 warnings in 0.02s`, `✓ verify:fast green` — the new script is not `test_*.py`-named so pytest does not collect it, confirmed via `pytest --collect-only` (still 8 tests).

matches-expected-result: yes — residue detected exactly on the dirty output and
nowhere on the clean guide (chains C2's residue_count against a real pipeline
output instead of a synthetic fixture); silhouette IoU stays high across all
five non-caption panels (chains C3's silhouette_iou against real split_cells
output) while visibly (but survivably) dipping on the one panel carrying
injected residue — demonstrating the two QC metrics are independent and
compose correctly on the same real split-cell artifact, exercising the grid
split itself (C1/C4's detect_grid + strip_linework, real CLI, no synthetic
fixture) end-to-end in one realistic artist scenario.

Committed on `feature/postproc-tests` in the worktree
(`/tmp/claude-1000/-mnt-workspace/bb9b9715-4ea6-4628-9115-ce47ee08dba4/scratchpad/wt-postproc-tests`):
commit `331d184` — "test(e2e): Loop 5 user scenario — dirty NB output through
the full postproc QC chain". Pre-commit hook: one non-blocking advisory
(`⚠ WARN: test/e2e_scenario.py (162 lines)` — over the 150-line warn
threshold, under the 200-LOC hard cap from C5), `verify:fast` green,
`test/e2e_scenario.pyi` stub auto-generated by the commit-time stubgen hook.

executor: loop-medium model=sonnet tier=medium
