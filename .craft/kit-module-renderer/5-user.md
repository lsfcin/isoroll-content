# Loop 5 — User Test — kit-module-renderer

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

## User Test

scenario: Lucas is about to kick off a P5 test-to-kill run. He wants the real
staging step run end-to-end — not the unit-test mocks — so the three arm
sheets, the shared-scale manifest, and every per-face mask actually land in
`output/gen-inbox/` where his NB web runs pick them up, and he wants it
checked by opening the files, not by trusting green pytest alone.

script: none (no CLI wrapper exists yet for stage_kit_modules.stage() — the
function itself, called with its real default `out="output/gen-inbox"`, is
the staging entrypoint per its own docstring; T5/C4 name no separate CLI
seam). Invoked directly via the same sys.path bootstrap `test/conftest.py`
uses (src/pipeline on path), calling `stage_kit_modules.stage()` with no
mocks — the identical code path pytest's `_skm()` exercises, but run for
its real side effect (writing to the real `output/gen-inbox/`, gitignored)
instead of assertions on an in-memory object.
run: `python3 -c "import sys; sys.path.insert(0,'src/pipeline'); import stage_kit_modules; stage_kit_modules.stage()"` (cwd = code/isoroll-content)

observed:
- run printed no errors; `output/gen-inbox/` now holds arm_a.png, arm_b.png,
  arm_bc.png, sheet_manifest.json, 81 `<module>_<view>_facemask.png` +
  `<module>_<view>_faces.json` pairs (9 modules × 9 views), and
  restyle_arm_{a,b,bc}.md.
- `file` on all 3 sheets: `PNG image data, 576 x 640, 8-bit/color RGB,
  non-interlaced` — valid, openable. `file` on a sample facemask:
  `PNG image data, 64 x 64, 8-bit grayscale, non-interlaced` — valid.
- bottom-right CELL_PX(64) cell checked pixel-by-pixel on all 3 opened
  sheets: `(0,0,0)` for every pixel on arm_a, arm_b, arm_bc alike (grid is
  9 cols × 10 rows = 90 cells for 81 panels, so the trailing cells incl.
  bottom-right stay canvas-black).
- `sheet_manifest.json` (18KB) parsed: single top-level `px_per_voxel: 14.0`
  scalar shared by all 81 `panels` entries (not per-panel) — one manifest
  file covers all 3 sheets since they share the identical panel layout, so
  "recorded in each manifest" holds trivially (one manifest, one shared
  value, referenced by every panel row).
- re-derived the 81 (module, view) panels via the same `kmr.render_module`
  call `stage()` uses internally and compared each panel's rendered RGBA
  size to its on-disk facemask size: 81/81 match (64×64 == 64×64) — masks
  align with their sheet's per-cell dimensions. Went one step further on a
  sample panel (wall_band/y0): computed the panel's alpha-silhouette pixel
  set vs the facemask's nonzero pixel set — 1429/1429 identical pixels,
  overlap ratio 1.0, mask ⊆ render silhouette — pixel-exact spatial
  alignment, not just matching dimensions.
- `guide_marks.residue_count()` (cyan-pixel QC used by the project's own
  tests) on the 3 opened sheets: arm_b=0, arm_bc=76788, arm_a=0 — cyan
  symbols present on arm-bc only, confirmed by direct pixel inspection of
  the real staged files (not the test's in-memory copy).
- re-ran `python3 -m pytest -q` after staging: `82 passed` — no regression
  from exercising the real entrypoint.

matches-expected-result: yes — Loop 0's expected-result ("pytest green; 3
sheets + manifests + face masks in output/gen-inbox/ ready for Lucas's NB
web runs; sheet layout keeps bottom-right cell empty") holds under direct
observation of the real staged files: valid PNGs, blank bottom-right cell
on every sheet, one shared px-per-voxel value covering every panel in the
one manifest, masks dimensionally and pixel-spatially aligned with their
renders, cyan only on arm-bc, pytest 82 passed.

executor: loop-medium model=sonnet tier=medium
