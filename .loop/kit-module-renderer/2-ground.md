# Loop 2 — Ground — kit-module-renderer

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

## Ground
branch-created: loop/kit-module-renderer base: 45a2f97
paths: 14/14 ok (parent directories verified: src/pipeline, src/pipeline/prompts, test, output/gen-inbox all present; 14 new files to create)
test-cmd-runs: yes (53 passed)

executor: loop-low model=haiku tier=low
