# Loop 0 — Clarify — kit-module-renderer

## Carry
slug: kit-module-renderer | branch: loop/kit-module-renderer (TBD Loop 1; stack AFTER dsl-v2-python ships — same repo, sequential) | root: code/isoroll-content
test-cmd: `python3 -m pytest -q` (verify in Loop 2) | e2e-cmd: none
criticality: normal | verdict: standard
criteria:
  C1 renders KIT V2 voxel modules flat-shaded: wall band, top cap, base, per-side recess band (door/window variants), diagonal half-band, roof cell, stair treads (45° and half slope) — 8 yaws + TOP each
  C2 one shared px-per-voxel scale across ALL panels of a sheet (P3 scale-consistency spec), recorded in a sheet manifest json
  C3 per-face masks emitted alongside each render (face id → pixel region) — enables the Foundry-lighting option (faces known by construction)
  C4 three arm sheets staged to output/gen-inbox/: arm-b (blank technical), arm-bc (blank + cyan symbols via guide_marks), arm-a (real textures mapped flat) — bottom-right cell EMPTY (NB watermark slot)
  C5 existing pytest suite stays green; new golden tests for module geometry (silhouette bbox per yaw)
tasks: TBD (Loop 1)
context: code/CONTEXT.md, code/isoroll-content/CONTEXT.md, code/isoroll-content/SPECS.md, code/isoroll-content/src/pipeline/CONTEXT.md

## Clarify
intent: Flat-shaded Python renderer for KIT V2 voxel modules + staging of the three P5 test-to-kill arm sheets (render→restyle lane R).
motivation: P5 lane per approved post-freeze plan (2026-07-13); Lucas decided flat-shaded python backend, whole-sheet restyle, arms (b), (b+c), (a); test-to-kill pre-registered in design/RENDER-RESTYLE-MEMO.md. Sheets must reach gen-inbox so Lucas can run the NB web app at his own pace — this lane gates P8.
refs: design/RENDER-RESTYLE-MEMO.md (lane spec + decision rule), SCENE-CREATION.md P5 row + scale-consistency section, PAINTER-UX round 15 (KIT V2 = voxel modules: band/cap/base/per-side recess), round 18b (stair slopes 45°/2.5ft only). Reuse: src/pipeline/kit_render.py, tile_guide_render.py (dimetric 2:1 conventions, grayscale face ramp), guide_marks.py (cyan symbols), scene_guide_render.py, design/feel-rig/stage_kit_paint.py (gen-inbox staging pattern). Blender NOT used (flat-shaded decision).
scope-files: src/pipeline/ (new kit_modules renderer + face-mask emitter; touch kit_render.py/tile_guide_render.py only for reuse extraction), src/pipeline/prompts/ (whole-sheet restyle prompt text per arm), output/gen-inbox/ (staged sheets, gitignored), test/
expected-result: pytest green; 3 sheets + manifests + face masks in output/gen-inbox/ ready for Lucas's NB web runs; sheet layout keeps bottom-right cell empty.
ambition: solid
criticality: normal tolerance: visual style of flat shading = Lucas eyeball later; NO tolerance for per-panel scale drift (C2)
innovation: none (spec is fixed; geometry by construction)
verdict: standard
keep-trail: yes

executor: orchestrator(fable, Loop 0 interactive — fields from Lucas-approved plan + RENDER-RESTYLE-MEMO decisions, same session) model=claude-fable-5 tier=max
