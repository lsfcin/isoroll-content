# Loop 4a — postproc-tests

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

## Tests

Worktree: `/tmp/claude-1000/-mnt-workspace/bb9b9715-4ea6-4628-9115-ce47ee08dba4/scratchpad/wt-postproc-tests` (branch feature/postproc-tests). T1–T4 written and exercised against the **existing** sheet_grid/sheet_utils/guide_marks implementations (no new prod code — those modules already exist). T5's test targets the not-yet-written `sheet_qc` module only; its implementation was intentionally left for Loop 4b (an earlier attempt in this loop wrote `sheet_qc.py` too — that was scope creep for a tests-first loop and was reverted, along with the T6 Makefile wiring, since wiring pytest into `verify-fast` before the suite is green would make the repo's pre-commit gate red for a deliberately-red TDD commit). T6 (Makefile wiring) is deferred to Loop 4b, once T5 makes the suite green.

| test file | covers | asserts |
|-----------|--------|---------|
| test/pytest.ini, test/conftest.py | T1 | pytest discovers test/, src/cli + src/pipeline importable |
| test/fixtures.py | T1 | synthetic builders: magenta_grid_sheet, cyan_squares, clean_image, filled_mask, alpha_blob |
| test/test_sheet_grid.py | C1, T2 | detect_grid within ±1px of even division (no drift); strip_linework removes all magenta and preserves cell-body blob pixels; near-white pixel outside EDGE_BAND survives strip |
| test/test_grid_drift.py | C4, T3 | detect_grid snaps drifted (±2px) interior boundaries within ±1px of true drifted position; split_cells on detected bounds yields correct cell count |
| test/test_guide_marks.py | C2, T4 | residue_count in [0.95×exact, exact] band for K solid cyan squares; residue_count == 0 on a clean image |
| test/test_sheet_qc.py | C3, T5 | silhouette_iou > 0.99 on identical masks; silhouette_iou < 0.5 on disjoint masks — **red**: `sheet_qc` module does not exist yet |

red-run: 1 failed as expected (test_sheet_qc.py — collection ERROR, ModuleNotFoundError: No module named 'sheet_qc') | wrong-failures: none

Full detail: `python3 -m pytest test/ -q` (plain, no `--continue-on-collection-errors`) reports `1 error in 0.08s` and stops at the collection error, per pytest's default behavior on an import error. Run with `--continue-on-collection-errors` to see the rest of the suite: **6 passed** (all of T1–T4, i.e. C1/C2/C4, exercising the real existing sheet_grid/sheet_utils/guide_marks behavior — genuine pass, not a stub) **+ 1 collection error** (test_sheet_qc.py, expected). No syntax errors anywhere; only DeprecationWarnings (Pillow `Image.getdata`, non-fatal, pre-existing in sheet_grid.py/guide_marks.py, not introduced here).

All new files: shebang+description first line, ≤200 LOC (largest: fixtures.py at 85 lines). Tests are pure PIL/synthetic — no network, no GPU, no rembg/NB/API calls (sheet_utils.remove_background and sheet_postproc.run are never invoked).

Committed on `feature/postproc-tests` in the worktree: commit `01490d4` — "test: pytest suite for postproc grid/mark QC (Loop 4a, red)". Makefile/CONTEXT.md doc-sync touched only as auto-generated routing-table entries for the new files (src/cli/CONTEXT.md's premature sheet_qc.py row was reverted along with the file itself).

executor: loop-medium model=sonnet tier=medium
