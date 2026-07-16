# Loop 4a — Tests First: arm-a-homography

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

## Recovery note
A previous Loop 4a executor died mid-run (session limit) after writing
`test/test_texture_map.py` (+ `.pyi`) on this branch and nothing else. This
session verified the branch (`loop/arm-a-homography`), read the recovery
file, and judged it sound (real `kit_modules` geometry, lazy per-test
imports for clean-FAILED collection, public-seam-only assertions, correct
red for `ModuleNotFoundError: texture_map`) — kept as-is, no rewrite. This
session then wrote the remainder: `test_texture_warp.py`, `test_arm_a_texture.py`,
and amended `test_stage_kit_modules.py` per Carry ruling R2/R3
(`.loop/arm-a-homography/1-plan.md`).

## Tests
| test file | covers | asserts |
|-----------|--------|---------|
| test_texture_map.py (recovery, kept as-is) | C2, C8 (unit level) | `load_textures`/`face_texture` FAMILY table incl. wood/stair-riser‖±u/roof/stair-bottom; `recess_decals` pinned ids+quads; `variant()` column-only dependence (z-invariance proxy — variant() takes no yaw input by construction, so this *is* the view-invariance proof at the pure-function level) + ≥2 distinct ids across 12 world columns + id-is-real-key |
| test_texture_warp.py (NEW) | C3, C4, and the "not-mirrored" corner-correspondence risk | `face_axes` south/north wall chirality matches 3-arch.md's pinned anti-mirror example exactly (Ah=-x̂/+x̂, hand-verified independently before pinning); `warp_tiling` solid-fill is mask-tight vs an independent polygon rasterization; wall face (h=3, dims_voxels z-slot 0→fallback 1.0) tiles vertically with a rep-count invariant to cell_px/scale (>=4 transitions of a 2-band stripe, same count at 1x and 2x scale); 3-corner gable face runs the AFFINE path without error and paints something; a corner-marked PNG lands on the same face_axes-derived corner across y45 and y225 (self-derived expected corner, not hand-picked — avoids pinning a possibly-wrong manual chirality guess); `warp_decal` single-placement is mask-tight |
| test_arm_a_texture.py (NEW) | C1, C7 | `paint_panel(module,view,ordered,s,cell_px,pad,origin)` (named in 3-arch.md's Architecture prose) painted at every ordered face's centroid is non-transparent and never one of `MAT_COLORS`'s flat RGB values, across 4 fixture modules (wall_band/roof_cell/stair_45/recess_door) and across all 9 VIEWS for wall_band; face_masks idmap>0 pixels are never left with alpha==0 in the paint_panel output (pixel-aligned by construction — same ordered/origin/s/cell_px/pad feed both), across the 4 fixtures and 3 more views of roof_cell |
| test_stage_kit_modules.py (AMENDED per R2/R3 — sanctioned, not fudged) | C5, C6, and R3's grid/gutter contract | grid is 5-col x 2-row (bounded numerically to discriminate from the old 9-col mega-sheet grid, verified this bound correctly fails against the pre-Loop-4b code today) with a blank bottom-right cell; magenta (255,0,255) separators present on the composed sheet; `stage()` writes exactly `{module}__{arm}.png` + `{module}__{arm}_prompt.txt` stem pairs for every module x arm∈{a,b,bc} and nothing else in gen-inbox; masks/manifest still land per (module,view) in the sibling masks/ dir (unchanged, still green). Preserved from the original file: arm_b zero-cyan-residue, arm_bc positive-residue, arm_a/sheet_grid size agreement — all still hold under either grid shape so they're kept passing, not forced red. |

red-run: 30 failed as expected (17 test_texture_map.py [recovery] + 6 test_texture_warp.py + 4 test_arm_a_texture.py + 3 test_stage_kit_modules.py amended) | wrong-failures: none

Verified reasons for every red: `ModuleNotFoundError: texture_map` / `texture_warp` (T1/T2 don't exist yet), `AttributeError: module 'kit_module_render' has no attribute 'project_face'` (T3 additive, not yet added), `AttributeError: module 'stage_kit_modules' has no attribute 'paint_panel'` (T4), and for the 3 amended stage tests: measured grid width 864px > the 5-col upper bound 672px (old 9-col grid still in place), no magenta pixel found (T4b gutter/separator not yet drawn), old `stage()` still writes `arm_a.png`/`arm_b.png`/`arm_bc.png` instead of per-module stems (T4b restage contract not yet applied) — all missing-behavior, none are import typos or syntax errors.

`make verify-fast` today: 92 passed, 30 failed (compileall clean, exit 0). Independently reran with the 4 architecture-scoped files excluded (`--ignore=test_texture_map.py --ignore=test_texture_warp.py --ignore=test_arm_a_texture.py --ignore=test_stage_kit_modules.py`): **88 passed, 0 failed** — confirms zero regression in the untouched pre-existing suite; the apparent drop from the Carry's "93/93 green at base" to "92 passed" here is fully accounted for by the sanctioned R2 amendment (old `test_stage_kit_modules.py` had 5/5 passing under the old contract; the amended file has 7 tests, 4 still passing as legitimate shape-independent invariants, 3 now correctly red pending Loop 4b's T4b).

executor: loop-medium model=sonnet tier=medium
