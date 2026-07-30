# Loop 4a — Tests First — kit-module-renderer

## Carry
slug: kit-module-renderer | branch: loop/kit-module-renderer (base loop/dsl-v2-python @45a2f97) | root: code/isoroll-content
test-cmd: `python3 -m pytest -q` (baseline 53 passed 2026-07-14) | e2e-cmd: none
criticality: normal | verdict: standard
criteria:
  C1 renders KIT V2 voxel modules flat-shaded: wall band, top cap, base, per-side recess band (door/window variants), diagonal half-band, roof cell, stair treads (45° and half slope) — 8 yaws + TOP each
  C2 one shared px-per-voxel scale across ALL panels of a sheet (P3 scale-consistency spec), recorded in a sheet manifest json
  C3 per-face masks emitted alongside each render (face id → pixel region) — enables the Foundry-lighting option (faces known by construction)
  C4 three arm sheets staged to output/gen-inbox/: arm-b (blank technical), arm-bc (blank + cyan symbols via guide_marks), arm-a (real textures mapped flat) — bottom-right cell EMPTY (NB watermark slot)
  C5 existing pytest suite stays green; new golden tests for module geometry (silhouette bbox per yaw)
tasks:
  T1 — KIT V2 module geometry builders (8 module types → Box/voxel sets) — src/pipeline/kit_modules.py — medium
  T2 — render module across 8 yaws + TOP, flat-shaded, at a FORCED shared scale — src/pipeline/kit_module_render.py — high
  T3 — compute one px-per-voxel from max bbox across ALL panels + write sheet manifest json — src/pipeline/kit_module_render.py — medium
  T4 — per-face occlusion-aware mask emitter (face id → pixel region) — src/pipeline/face_masks.py — high
  T5 — stage 3 arm sheets to output/gen-inbox (b/bc/a, bottom-right cell empty) — src/pipeline/stage_kit_modules.py — medium
  T6 — per-arm whole-sheet restyle prompt text — src/pipeline/prompts/restyle_arm_{b,bc,a}.md — low
  T7 — golden tests: silhouette bbox per yaw + shared-scale invariant — test/test_kit_modules.py, test/test_kit_module_render.py — medium
context: code/CONTEXT.md, code/isoroll-content/CONTEXT.md, code/isoroll-content/SPECS.md, code/isoroll-content/src/pipeline/CONTEXT.md, design/RENDER-RESTYLE-MEMO.md, SCENE-CREATION.md §Scale-consistency

## Tests

Amendment to the Carry `tasks:` T7 file list: a third file, `test/test_stage_kit_modules.py`,
was added. 3-arch.md's own Evaluation > seams section requires a C4 assertion ("3 sheet files
exist, bottom-right cell all-black, residue(arm_bc)>0 & residue(arm_b)==0") that has no home in
the two files T7 names — this is that home. Not a criterion/scope change, just giving an
architecture-mandated assertion a file.

Technique note (verified locally, see below): a brand-new module (kit_modules.py,
kit_module_render.py, face_masks.py, stage_kit_modules.py — none exist yet on this branch) can't
be imported at test-file top level the way this repo's existing tests import already-existing
modules (e.g. `from layout_massing import massing`) — a top-level `import` of a genuinely missing
module raises `ModuleNotFoundError` during pytest **collection**, which aborts the whole session
(`Interrupted: N errors during collection`) and prevents even the unrelated, already-green
baseline from running. Confirmed by running the suite with plain top-level imports first: 0 tests
ran, 3 collection errors, baseline invisible. Fixed by deferring each new-module import into a
small helper (`_km()`/`_kmr()`/`_fm()`/`_skm()`) called from *inside* each test's call phase —
this reports one isolated `FAILED` per test (correct "red", not a collection abort) and leaves
the rest of the suite — including the 53-test baseline — to run and pass normally. Already-existing
modules (`sheet_qc`, `guide_marks`, `layout_massing`, `PIL`) are imported normally at top level.

| test file | covers | asserts |
|-----------|--------|---------|
| test/test_kit_modules.py | C1 (kit_modules.py: Face, extrude, from_boxes, MODULES) | extrude/from_boxes face kind+count math (top/bottom/side); all 9 MODULES builders present, non-empty, deterministic; top_cap/base thinner than wall_band; recess_door/recess_window split the opening side into more faces than plain wall_band and differ from each other; diag_half is a thin quad extrusion (top:1,bottom:1,side:4); roof_cell is a 5-face wedge (gable:2,slope:2,bottom:1); stair_45/stair_half are STEPS×6-face box conversions, stair_half rises to half stair_45's max z |
| test/test_kit_module_render.py | C1 (yaws/views/render_module), C2 (shared_scale, build_sheet_manifest), C3 (face_masks.face_mask, save_mask) | YAWS==8 values, VIEWS==9 (TOP last); render_module returns all 9 views as deterministic RGBA + non-empty ordered-face list; silhouette bbox (via sheet_qc.silhouette_mask.getbbox) differs across ≥4/8 yaws for an asymmetric module (roof_cell) — no mirror chirality; ordered_faces ids unique + `"{i}:{kind}"`-shaped; shared_scale fits every panel of every module within cell_px-2·pad; build_sheet_manifest records px_per_voxel once at sheet level, never per-panel; face_mask idmap is L-mode, same size as render, its painted region ⊆ the render's own silhouette, and its meta keys == the ordered face ids; meta records bbox+positive pixel count per face; save_mask writes the documented `<panel>_facemask.png` + `<panel>_faces.json` pair |
| test/test_stage_kit_modules.py | C4 (stage_kit_modules.py: sheet_grid, arm_b, arm_bc, arm_a, stage) | sheet_grid leaves the bottom-right cell all-black (NB watermark slot); arm_b has zero cyan residue (guide_marks.residue_count); arm_bc has positive cyan residue (adds the guide marks); arm_a matches the sheet_grid's own size; stage() writes exactly 3 arm-sheet PNGs + ≥1 manifest json + the 3 restyle_arm_{a,b,bc}.md prompts to its out dir |

Documented seam decisions not pinned by 3-arch.md (Loop 4b: if your natural shape differs, raise
`RETURN loop=4a reason=test-wrong` rather than hand-editing a test):
- `build_sheet_manifest(panels, s)`'s input `panels`: list of dicts `{module, view, bbox, origin}`,
  mirroring the stated output shape.
- `sheet_grid`/`arm_b`/`arm_bc`/`arm_a`'s shared `panels` argument: list of dicts
  `{module, view, img, ordered, origin}`, one entry per rendered panel.
- `arm_a(panels, ordered_by_panel)`'s `ordered_by_panel`: dict keyed `(module, view)` → that
  panel's `ordered` face list (the same list `render_panel`/`render_module` returned).

Architecture inconsistency flagged for Loop 4b (not blocking, no seam is infeasible): 3-arch.md
gives `render_panel(...) -> (RGBA, origin, ordered)` but `render_module(...) -> dict[view ->
(RGBA, ordered, origin)]` — opposite tuple order between the two lines. Tests here only exercise
`render_module`'s own stated order directly; Loop 4b should reconcile the two to agree.

red-run: 29 failed as expected (all four target modules genuinely absent — every failure is
`ModuleNotFoundError: No module named '{kit_modules|kit_module_render|face_masks|
stage_kit_modules}'` raised from inside each test's call-phase helper, nothing else) | 53 passed
(existing baseline, C5, untouched and still green) | wrong-failures: none — grepped the full run
log: exactly 29 `ModuleNotFoundError` occurrences, 29 failures, no other exception type, no
AssertionError from a bad expectation, no collection error.

verified: `python3 -m pytest -q` at repo root (code/isoroll-content) → `29 failed, 53 passed, 12
warnings in 0.41s`. Full log inspected line-by-line for wrong-failures (see above).

executor: loop-medium model=sonnet tier=medium
