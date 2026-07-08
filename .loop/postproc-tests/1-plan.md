# Loop 1 — postproc-tests

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

## Plan
branch: feature/postproc-tests (base: feature/f1-procedural-spine)

Grounding facts every executor must honor (from source, not memory):
- Modules use FLAT absolute imports (`from sheet_grid import ...`, `from sheet_utils import ...`). `sheet_grid.py`, `sheet_utils.py`, `sheet_postproc.py`, new `sheet_qc.py` live in `src/cli/`; `guide_marks.py` lives in `src/pipeline/`. conftest MUST insert BOTH dirs into `sys.path` or every import fails.
- Magenta = R≥170 AND B≥170 AND G≤100 → use pure `(255,0,255)`. Near-white = all channels ≥232. Cyan residue target = `(0,255,255)`, `residue_count` tol=60.
- `detect_grid(img, rows, cols)` → (xs, ys), len cols+1 / rows+1, ends fixed at 0 and size. An interior boundary snaps to the strongest magenta/white line within `window = max(2, int(size/count*SEARCH_FRAC))` px (SEARCH_FRAC=0.25) of the even division, only if that line's mean profile value ≥ LINE_STRENGTH_MIN=24. So a magenta line must span the FULL image height (vertical) / width (horizontal) to register.
- `strip_linework(img, band=12)` → RGBA; magenta blanked everywhere, near-white blanked only within 12px of the border.
- Hooks on NEW .py: first line must be `#`-comment or shebang description; file ≤200 LOC.

| id | task | files | done-when | tier | effort |
|----|------|-------|-----------|------|--------|
| T1 | pytest bootstrap: `pytest.ini` (testpaths=test, quiet); `test/conftest.py` prepending `<root>/src/cli` and `<root>/src/pipeline` to `sys.path`; `test/fixtures.py` helpers building synthetic PIL images (full-height magenta grid line; K solid cyan rects; two L silhouette masks) | pytest.ini, test/conftest.py, test/fixtures.py | `<venv> -m pytest test/ -q` collects with 0 import/collection errors (0 tests is acceptable at this step) | medium | medium |
| T2 | test detect_grid + strip_linework on synthetic 2-col×1-row magenta grid (C1) | test/test_sheet_grid.py | image 200×100, full-height magenta line at x=100: `detect_grid(img,1,2)` → len(xs)==3, xs[0]==0, xs[2]==200, xs[1] within 1px of 100; `strip_linework` sets alpha 0 on the magenta line and keeps a near-white pixel placed at cell centre (>12px from all borders) | medium | medium |
| T3 | test ±2px drift snap (C4) | test/test_grid_drift.py | for offset in {-2,+2}: full-height magenta line at x=100+offset in a 200×100 image → `detect_grid(img,1,2)` interior xs[1] within 1px of 100+offset (proves it snaps to the drifted line, not the even division) | medium | medium |
| T4 | test residue_count (C2) | test/test_guide_marks.py | black RGB image with K=5 solid `(0,255,255)` rects of known area A each → `residue_count(img)` in [K*A*0.9, K*A]; all-black image → 0 | medium | medium |
| T5 | new QC module + tests (C3) | src/cli/sheet_qc.py, test/test_sheet_qc.py | `sheet_qc.py` first-line desc comment, ≤200 LOC, defines `silhouette_iou(cell_img, guide_mask, bg_max=12) -> float` (cell foreground = pixels with any RGB channel > bg_max OR alpha>0; guide_mask = L image, >0 = inside; IoU = |∩|/|∪|). Tests: identical masks → ≥0.99; disjoint masks → <0.5 | medium | medium |
| T6 | wire pytest into verify-fast + full gate (C5); harden split only if a T3 test goes red against current code | Makefile, src/cli/sheet_postproc.py (only if needed) | `verify-fast` target runs compileall AND `pytest test/ -q`; `make verify-fast` green; every touched/new .py ≤200 LOC; no import of NB/imagegen/comfy/requests/urllib in any test file | medium | medium |

## Plan Review (adversarial, assume sonnet/haiku executors)
- FLAT imports would break a repo-root-only conftest → **fixed**: T1 done-when names both `src/cli` and `src/pipeline` explicitly; grounding block restates it.
- `guide_marks` sits in `src/pipeline` while `sheet_*` sit in `src/cli` — split path could be missed → **fixed**: both dirs in conftest; T4 relies on it.
- rows=1 axis has NO interior boundary (only [0,size]); a tester expecting a horizontal line would assert wrongly → **fixed**: T2/T3 use cols=2 for the interior assertion and rows=1 (no horizontal-line claim).
- A partial-height magenta line may fall below LINE_STRENGTH_MIN=24 and not snap → **fixed**: grounding + T2/T3 require FULL-height lines.
- `strip_linework` preserves near-white only inside the band-free interior; a white test pixel near the edge would be wrongly blanked → **fixed**: T2 places the preserved pixel at cell centre (>12px from borders).
- `residue_count` on anti-aliased cyan edges is fuzzy → **fixed**: T4 uses solid rects and asserts a band [0.9·area, area], not equality.
- `silhouette_iou` signature/foreground rule ambiguous for a small model → **fixed**: T5 pins the exact signature and the foreground/mask definitions in done-when.
- New-file hooks (≤200 LOC, first-line desc) could trip 4b → **fixed**: grounding block + T5 call them out; sheet_postproc.py is already 159 LOC, so any T6 harden edit must stay under 200.
- C4 may need NO code change (detect window already 25px ≫ 2px) → **fixed**: T6 makes the split-harden conditional on an actual red test; TDD Loop 4a/4b will confirm C4 is met by existing behavior or add the minimal fix.
- Changing verify-fast to run pytest satisfies C1+C5 and honors the Makefile's own "promote to real pytest coverage" TODO; tests are pure-PIL/synthetic so still fast → acceptable, no network/GPU.

verdict: PASS

executor: loop-high model=opus tier=high
