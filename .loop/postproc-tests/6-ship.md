# Loop 6 — postproc-tests

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

## Ship

diff-scope: clean — all files match plan scope (test/**, src/cli/sheet_qc.py + .pyi, Makefile hardening, documentation syncs in CONTEXT.md); 0 extras
roadmap: updated /mnt/workspace/code/isoroll-content/ROADMAP-content-gen.md § Estado
commit: (pushed to worktree on ship) pushed: no (no remote configured)
leftovers: none

executor: loop-low model=haiku tier=low
