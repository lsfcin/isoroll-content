# Loop 0 — Clarify: arm-a-homography

## Carry
slug: arm-a-homography | branch: loop/arm-a-homography | root: /mnt/workspace/code/isoroll-content
base: loop/anchored-kit-marks @ 4126704 (PIN — doc lineage lives here, NOT develop)
test-cmd: `make verify-fast` (= /mnt/workspace/.venv/bin/python3 -m compileall -q . && pytest test/ -q; 93/93 green at base) | e2e-cmd: none (Loop 5 scripts stage → gen-inbox render + QC)
criticality: normal | verdict: standard
criteria:
  C1 arm_a paints every projected face quad of ALL kit modules in stage_kit_modules by homography-warping a texture PNG from assets/textures/ — no flat MAT_COLORS fills remain in arm_a output
  C2 mapping face(kind,mat) → texture id via textures.json: wall band stone → wall_stone_side_v*, wall band wood → wall_wood_side_v*, wall/band top → wall_{mat}_top, floor → floor_{mat}_v*, roof_cell → roof_shingle_v*, stair tread → stair_tread_v*, stair riser → stair_riser_v*; stair sides/back reuse wall stone side (clipped by the face polygon); door/window recess faces get the matching decal (door_WxHx0 by opening dims, window_1x1x0)
  C3 tiling semantics honored: texture tile spans exactly dims_voxels in world units; adjacent voxels continue the pattern horizontally (continuity=horizontal — sample offset from world position, no per-voxel restart); decals placed once per opening, aligned to the opening quad, no tiling
  C4 px-per-voxel scale comes from the module manifest (shared_scale), never re-measured from pixels; one s per sheet
  C5 restage writes the arm_a sheets (9 views per module) to output/gen-inbox/ under the existing gen-inbox file contract (same stems/manifest as current stage())
  C6 `make verify-fast` fully green: all pre-existing tests (93) + new tests for C1–C4
  C7 code-verified coverage: for a fixture module, every face-mask pixel (face_masks.py) is non-background in the arm_a render (no unpainted face), asserted in a test — geometry by code, never model eyes
tasks: TBD (Loop 1)
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/src/pipeline/CONTEXT.md, /mnt/workspace/code/CONTEXT.md, /mnt/workspace/core/skills/iso-visual.md

## Clarify
intent: replace arm_a's flat per-material fills with real per-face homography texturization from the /linework texture set, then restage the arm sheets for the NB round.
motivation: Lucas 2026-07-14 decision — "first NB round waits for real arm (a)"; texturization is the core of the render→restyle lane (design/RENDER-RESTYLE-MEMO.md § addendum). S4 row in ROADMAP-content-gen.md § Plano refinado.
refs: design/RENDER-RESTYLE-MEMO.md; ROADMAP-content-gen.md S4 row; assets/textures/textures.json (50 ids); src/pipeline/stage_kit_modules.py (arm_a current), kit_module_render.py (ordered_faces/render, per-face projected polys), kit_modules.py (Face), face_masks.py; SCENE-CREATION.md § Scale-consistency.
scope-files: src/pipeline/stage_kit_modules.py, src/pipeline/ (new texture_warp / texture_map modules), test/ (new specs), output/gen-inbox/ (restaged, gitignored)
expected-result: `stage()` emits arm_a sheets where every face shows the correct linework texture warped in perspective; suite green; sheets ready for board eyeball. Lucas's 5 hand-drawn PNGs NOT dropped yet — UV-map-JSON ingestion seam may be stubbed but not populated (S2 pending).
ambition: solid
criticality: normal tolerance: visual style imperfections OK (Lucas eyeballs on board); geometric wrongness (wrong face, wrong side, seam restarts) NOT acceptable
criteria: C1..C7 above
innovation: some — warp math is standard (projective map unit-square→quad), mapping table is mechanical; judgment already spent at clarify
verdict: standard (new public seam, >2 files, no existing homography pattern in repo → not padaria)
keep-trail: yes (visual-gate chain; board pending Lucas)

## Constraints (iso-visual hard rule — binding on all loops)
- Geometry verified by CODE (C7 mask-coverage test, seam-continuity assert); model eyes only for coarse sanity (file renders, not blank).
- Never mirror sprites; rotation = cell remapping. Never re-measure scale from pixels.
- Cyan is reserved (registration marks), magenta is reserved (grid): textures must not introduce those keys.
- Eyeball gate: after ship, sheets go on the board artifact; NOTHING advances to S4t before Lucas's OK. Orchestrator handles the board, not executors.

executor: orchestrator model=claude-fable-5 tier=max (Loop 0 inline — context hot, field-practice override)
