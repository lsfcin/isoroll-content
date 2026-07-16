# Loop 6 — Ship: arm-a-homography

## Carry
slug: arm-a-homography | branch: loop/arm-a-homography | root: /mnt/workspace/code/isoroll-content
base: loop/anchored-kit-marks @ 4126704 (PIN — doc lineage lives here, NOT develop)
test-cmd: `make verify-fast` (= /mnt/workspace/.venv/bin/python3 -m compileall -q . && pytest test/ -q; 93/93 green at base) | e2e-cmd: none (Loop 5 scripts stage → gen-inbox render + QC)
criticality: normal | verdict: standard
criteria:
  C1 arm_a paints every projected face quad of ALL kit modules in stage_kit_modules by homography-warping a texture PNG from assets/textures/ — no flat MAT_COLORS fills remain in arm_a output
  C2 mapping face(kind,mat) → texture FAMILY via textures.json (wall band stone → wall_stone_side, wood → wall_wood_side, tops → wall_{mat}_top, floor → floor_{mat}, roof_cell → roof_shingle, stair top → stair_tread, stair riser (side ‖±u) → stair_riser, stair side ‖±v/back → wall stone side clipped by face polygon; door/window recess → matching decal); VARIANT within a family selected deterministically from stable world column index — all variants exercised, same column = same variant in all 9 views
  C3 tiling semantics honored: texture tile spans exactly dims_voxels in world units; adjacent voxels continue the pattern horizontally (continuity=horizontal — sample offset from world position, no per-voxel restart); decals placed once per opening, aligned to the opening quad, no tiling
  C4 px-per-voxel scale comes from the module manifest (shared_scale), never re-measured from pixels; one s per sheet
  C5 restage writes ONE sheet PER MODULE per arm to output/gen-inbox/ (`{module}__{arm}.png` + `{module}__{arm}_prompt.txt` stem pairs); 9 views per sheet; packed per R3 (gutter+magenta separators, bottom-right cell empty, no per-panel autofit)
  C6 `make verify-fast` fully green: pre-existing tests (stage-contract tests amended per R2, never deleted) + new tests for C1–C4, C8
  C7 code-verified coverage: for a fixture module, every face-mask pixel (face_masks.py) is non-background in the arm_a render (no unpainted face), asserted in a test — geometry by code, never model eyes
  C8 variant coverage: a multi-column fixture face shows ≥2 distinct variants; variant choice is view-invariant (same column, same variant across yaws), asserted in a test
tasks:
  T1 — texture_map.py (NEW): textures.json loader + MAPPING (module,kind,orientation)→family, mat blank→stone default, stair-face classify by world normal, recess opening→decal id+world quad, deterministic variant-from-world-column (R1) — src/pipeline/texture_map.py — medium
  T2 — texture_warp.py (NEW): warp_tiling + warp_decal; per-corner texture-px coords from world axes (orientation-safe, dot products, never index maps), tiled source builder, polygon mask; PERSPECTIVE (4-corner) + AFFINE (3-corner) — src/pipeline/texture_warp.py — medium(→high if warp math fights)
  T3 — project_face(pts,view,s,cell_px,pad,origin) public helper (additive, mirrors ordered_faces transform) — src/pipeline/kit_module_render.py — low
  T4 — arm_a rewrite: per-panel textured paint_panel via T1+T2+T3; rebuild faces=km.MODULES[module]() index by builder-i from face_id; decals for recess; KEEP arm_a(panels,ordered_by_panel) signature — src/pipeline/stage_kit_modules.py — medium
  T4b — per-module sheet composer + stage() restage contract per R2/R3 (stem pairs, gutter, magenta separators, empty bottom-right cell); amend existing stage-contract tests — src/pipeline/stage_kit_modules.py, test/ — medium
  T5 — tests: test_texture_map.py(C2), test_texture_warp.py(C3,C4), test_arm_a_texture.py(C1+C7), variant coverage+view-invariance(C8) — test/ — medium
  T6 — restage stage() → gen-inbox per-module sheets; make verify-fast green (C5,C6) — low
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/src/pipeline/CONTEXT.md, /mnt/workspace/code/CONTEXT.md, /mnt/workspace/core/skills/iso-visual.md

## Ship
diff-scope: clean — `git status --short` shows exactly: T1/T2 new source+stub
(`texture_map.py(.pyi)`, `texture_warp.py(.pyi)`), T3 diff
(`kit_module_render.py(.pyi)`), T4/T4b diff (`stage_kit_modules.py(.pyi)`),
T5 new/amended tests (`test_texture_map.py`, `test_texture_warp.py`,
`test_arm_a_texture.py`, amended `test_stage_kit_modules.py(.pyi)`), the
hook-auto-regenerated routing tables (`CONTEXT.md`, `src/pipeline/CONTEXT.md`,
`test/CONTEXT.md` — not hand-edited, side effect of the touched dirs per
4b-code.md's own note), `ROADMAP-content-gen.md` (this loop's S4/S4b update),
and `.loop/arm-a-homography/` (the chain trail, keep-trail: yes). No files
outside the plan's `files` columns + `.loop/` + `ROADMAP-content-gen.md`. No
pre-existing dirty paths at branch start (verified via `git status --short`
at Loop 5 session start — tree was clean before this loop's own edits). No
secrets. `output/gen-inbox/` restage artifacts from Loop 5 are gitignored
(`output/` in `.gitignore`) and correctly absent from `git status`.
extras: none

roadmap: updated /mnt/workspace/code/isoroll-content/ROADMAP-content-gen.md —
S4 row → outcome "done — homography warp shipped, `make verify-fast` 122/122
green, real restage produced 27 per-module sheets in `output/gen-inbox/`,
branch pushed, awaiting merge + Lucas eyeball gate"; added S4b row for the
follow-on chain `kit-dimensional-vocabulary` (wall-height variants, full door
set 1x1x0..2x3x0, slice middle/edge parts — deliberately NOT absorbed into
this chain per `1-plan.md:58,86`, routed pending Lucas board gate).

commit: 9be2298 pushed: yes (loop/arm-a-homography → origin/loop/arm-a-homography)

leftovers:
- `kit-dimensional-vocabulary` (S4b in ROADMAP-content-gen.md): wall-height
  variants, door set 1x1x0..2x3x0, slice middle/edge parts — pending Lucas
  board gate before a new /loops chain opens it.
- Merge of `loop/arm-a-homography` into its base/develop is explicitly NOT
  done by this loop (user's call per flow policy) — branch is pushed and
  ready for review/eyeball.
- 6 pre-existing global mega-sheet files in the gitignored `output/gen-inbox/`
  (`arm_a.png`, `arm_b.png`, `arm_bc.png`, `restyle_arm_{a,b,bc}.md`, from
  before this loop's per-module rewrite) are stale leftovers of the old
  contract; harmless (gitignored, not shipped), but worth a manual `rm` before
  Lucas's eyeball pass so only the new 54 per-module files are visible in the
  hand-off folder — not done here since `output/` is out of this loop's diff
  scope and Loop 5's job was to verify the new files exist, not clean old ones.

executor: loop-medium model=sonnet tier=medium
