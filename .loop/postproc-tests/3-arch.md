# Loop 3 — postproc-tests

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

## Architecture

Every new `.py` file (incl. conftest/fixtures/test_*) starts with `#!/usr/bin/env python3` + one-line description docstring, ≤200 LOC, one responsibility. Tests are pure PIL/synthetic: no network, no GPU, no rembg — never call `sheet_utils.remove_background` or `sheet_postproc.run` (they invoke rembg / I/O). Exercise pure functions only.

- `pytest.ini` (repo root) — pytest config. `[pytest]` + `testpaths = test`. Not a .py file → no shebang. **[T1]**
- `test/conftest.py` — make `import sheet_grid / sheet_qc / sheet_utils / sheet_postproc` (src/cli) and `import guide_marks` (src/pipeline) work. Body: `sys.path.insert(0, <abspath src/cli>)` and `src/pipeline`, resolved from `Path(__file__).resolve().parents[1]/"src"/...`. No fixtures needed here; helpers live in fixtures.py (pytest prepend-mode puts `test/` on sys.path, so `from fixtures import ...` resolves). **[T1]**
- `test/fixtures.py` — synthetic-image builders (plain functions, not pytest fixtures):
  - `magenta_grid_sheet(rows:int, cols:int, cell:int=100, drift:dict|None=None) -> tuple[Image, list[int], list[int]]` — RGBA sheet, magenta (255,0,255) 1px lines at cell boundaries, a solid colored blob inside each cell; `drift` maps interior-boundary index→±px offset applied to that magenta line; returns `(img, true_xs, true_ys)` where true_* embed the drift. **[T1]**
  - `cyan_squares(n:int, side:int=10, bg=(0,0,0)) -> Image` — RGB image with `n` disjoint SOLID cyan (0,255,255) squares (no AA) → exactly `n*side*side` cyan px. **[T1]**
  - `clean_image() -> Image` — RGB, no cyan. **[T1]**
  - `filled_mask(size:tuple[int,int], box:tuple[int,int,int,int]) -> Image` — L mask, 255 inside box else 0. **[T1]**
  - `alpha_blob(size, box) -> Image` — RGBA cell, opaque colored blob in box, transparent elsewhere (silhouette source for C3). **[T1]**
- `src/cli/sheet_qc.py` (+ `sheet_qc.pyi` via stubgen) — silhouette QC. Decisions the executor must NOT re-guess: silhouette = alpha channel ≥ `ALPHA_MIN` when img has alpha, else luminance ≥ threshold; empty-union IoU returns 1.0 (avoids /0). **[T5]**
  - `ALPHA_MIN: int = 8`
  - `silhouette_mask(img: Image.Image, alpha_min: int = ALPHA_MIN) -> Image.Image` — binary L (255 = foreground).
  - `mask_iou(a: Image.Image, b: Image.Image) -> float` — |a∧b| / |a∨b|; union==0 → 1.0.
  - `silhouette_iou(cell: Image.Image, box_mask: Image.Image, alpha_min: int = ALPHA_MIN) -> float` — `mask_iou(silhouette_mask(cell), box_mask)`.
- `test/test_sheet_grid.py` — **[T2, C1]** `magenta_grid_sheet(2,3)` (no drift) → `detect_grid(img,2,3)` xs/ys within ±1px of even boundaries; `strip_linework(cell_with_magenta_line)` → `magenta_mask(out)` has 0 set px AND cell-body blob pixels survive (alpha preserved). Second case: near-white pixel in cell body (outside `EDGE_BAND`) survives strip.
- `test/test_grid_drift.py` — **[T3, C4]** `magenta_grid_sheet(2,3, drift={interior x-idx:+2, other x-idx:-2, interior y-idx:+2})` → `detect_grid` returns each interior boundary within ±1px of the drifted (true) position, i.e. it snapped to the drifted line, not the even division. Then `split_cells(img, xs, ys)` with detected bounds yields the right cell count. detect_boundaries window = `max(2,int(cell*0.25))` = 25px ≫ 2px drift, so this is expected GREEN with no source edit.
- `test/test_guide_marks.py` — **[T4, C2]** `cyan_squares(K=3, side=10)` → `residue_count(img)` in band `[0.95*3*100, 3*100]` (solid, no-AA → exact 300); `clean_image()` → `residue_count == 0`.
- `test/test_sheet_qc.py` — **[T5, C3]** identical `filled_mask` (or `alpha_blob`+matching box) → `silhouette_iou ≈ 1.0` (>0.99); two disjoint boxes → `< 0.5` (0.0); optional half-overlap → in (0.3,0.7).
- `Makefile` — **[T6, C5]** append `$(PY) -m pytest test/ -q` to `verify-fast` and `verify-full` after the compileall line. Only touch `src/cli/sheet_postproc.py` IF T3 is red (window already covers ±2px → not expected).

## Evaluation
criteria-coverage:
  C1 → test/test_sheet_grid.py (detect_grid + strip_linework) on fixtures.magenta_grid_sheet.
  C2 → test/test_guide_marks.py (residue_count band + zero) on fixtures.cyan_squares / clean_image.
  C3 → src/cli/sheet_qc.silhouette_iou + test/test_sheet_qc.py (1.0 identical / <0.5 disjoint).
  C4 → test/test_grid_drift.py proving detect_grid snaps ±2px-drifted interior lines; sheet_postproc split uses the same detect_grid→split_cells path.
  C5 → Makefile verify-fast runs pytest; all new files ≤200 LOC (largest is fixtures.py ~120); no rembg/NB/API in tests (only pure funcs exercised).
seams:
  - detect_grid / strip_linework / detect_boundaries: pure Image→value functions, called directly on synthetic PIL images — no I/O.
  - residue_count: pure Image→int.
  - silhouette QC: mask_iou/silhouette_iou take PIL images and return float — fully deterministic, synthetic masks.
  - drift snap: seam is detect_boundaries' search window; fixture embeds known drifted truth, assert against it.
  - verify gate: `make verify-fast` shells the exact test-cmd; green == C5.
adversarial notes (resolved before verdict):
  - shebang+docstring required on conftest.py/fixtures.py/test_*.py too — stated so executor won't omit it and trip the file hook.
  - silhouette definition + empty-union IoU convention pinned in sheet_qc so a medium executor can't guess wrong.
  - C4/T6 hardening is conditional; design predicts GREEN-without-source-edit (window 25px ≫ 2px), so T6 normally edits only the Makefile — no scope creep into sheet_postproc unless a red run proves otherwise.
  - fixtures use solid, non-antialiased fills → exact pixel counts → residue band is deterministic, not flaky.
  - new src module gets a .pyi (repo convention: all src/*.py have stubs) — folded into T5.
verdict: PASS

executor: loop-high model=opus tier=high
