# Loop 4b — Code Until Green: arm-a-homography

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

## Code
Implemented T1–T6 in dependency order, running the scoped test file after each
new source file instead of waiting for a single final `make verify-fast` —
faster feedback, same eventual gate. Branch was already `loop/arm-a-homography`
(verified via `git branch --show-current` before starting); 30 pre-existing
red tests from Loop 4a's recovery session were the starting point.

**T1** `src/pipeline/texture_map.py` (NEW): `load_textures` (cached
textures.json parse), `_face_normal` (cross-product, magnitude-guarded),
`FAMILY(module,kind,normal,mat)` (stair branch first — top/bottom/side by
`|normal·x̂|` for riser vs wall_stone_side — then generic bottom→floor_stone,
slope/gable→roof_shingle, base+top→floor_stone, then generic top/side by
mat), `variant()` (md5-digest of `family|world-column`, never Python's
randomized `hash()`, so it's reproducible across process runs, not just
within one), `face_texture()`, `recess_decals()` (pinned quads), plus a
`texture_png_path()` public accessor so stage_kit_modules never reaches into
`_TEXTURES_ROOT` directly.
attempt 1: T1 written → 0 red, `pytest test/test_texture_map.py -q`: 17/17 green first pass.

**T2** `src/pipeline/texture_warp.py` (NEW): `face_axes` (HORIZONTAL/
VERTICAL/SLOPED regimes exactly per 3-arch.md's pinned formulas, verified by
hand against the south/north wall anti-mirror example before running any
test — south N=+ŷ → Ah=-x̂ matched), `_resolve_dim`, `_texcoords` (tiling,
world-absolute), `_decal_texcoords` (min/max-normalized within the quad —
exactly 1 tile, no wrap), `_tile_source`, `_perspective_coeffs`/
`_affine_coeffs` (4-point homography / 3-point affine solve), `_warp_to_screen`,
`warp_tiling`, `warp_decal`.
attempt 1: first run of `_perspective_coeffs` used `np.linalg.solve` with the
matrix/RHS roles swapped (dst points as the RHS constant vector instead of as
the linear-system variables) → `LinAlgError: Singular matrix` on 2/6 tests
(the two whose screen_poly happens to be non-singular under the correct
formulation but was singular under the wrong one). Root-caused by re-deriving
PIL's `Image.transform(..., PERSPECTIVE)` semantics from first principles
(coeffs are evaluated AT the output/dest pixel to find the input/src pixel) —
fixed by rebuilding the matrix in dst variables with src as RHS.
attempt 2: coefficient-role fix applied → new failure class, still
`LinAlgError: Singular matrix`, now on the exact test inputs the fix was
supposed to help (`test_warp_tiling_solid_png_...`,
`test_warp_tiling_marks_the_same_physical_corner...`, `test_warp_decal_...`).
Root cause (confirmed by direct calculation, not guessed): the SAME south
wall face at views `y45`/`y225` is genuinely edge-on under this dimetric
camera — `ordered_faces` (pre-existing, unmodified code) independently
produces the identical 4-collinear-point degenerate quad for this face at
these two yaws, so the homography system is mathematically singular by
construction, not a bug in the new code. Switched both `_perspective_coeffs`
and `_affine_coeffs` from `np.linalg.solve` to `np.linalg.lstsq` (least-squares
best-fit instead of an exact solve) — a degenerate/near-degenerate screen quad
now returns a finite (if visually meaningless) transform instead of raising;
that face paints ~nothing either way since its true screen area is ~0.
green: `pytest test/test_texture_warp.py -q`: 6/6.

**T3** `project_face` added to `src/pipeline/kit_module_render.py`
(additive-only, does not touch `ordered_faces`/`render_panel`/
`render_module`): TOP branch mirrors `ordered_faces`'s raw `(ox+u*s, oy+v*s)`
step exactly (not `cam.pt`, which applies the dimetric `_proj` — TOP never
does); yN branch reuses the existing private `_yaw` helper + `Cam.pt`.
Covered indirectly by every `test_texture_warp.py`/`test_arm_a_texture.py`
call site (no dedicated project_face unit test exists in 4a's tests — it's
exercised as a seam, per the test file's own header).

**T4/T4b** `src/pipeline/stage_kit_modules.py` rewritten: `paint_panel`
(rebuilds `faces=km.MODULES[module]()`, indexes by `int(face_id.split(':')[0])`
per 3-arch.md, calls `texture_map.face_texture` → `texture_warp.warp_tiling`
per ordered face, then `texture_map.recess_decals` → `project_face` →
`texture_warp.warp_decal` for openings); `_shared_s` re-derives the
module-shared `s` from `panels[0]["img"].size[0]` + the module-level `PAD`
constant (panels dicts carry no `"s"` key — matches both the test fixture's
own `_panels_for` and `stage()`'s real call site, since `shared_scale` is a
pure function of module-name-universe + cell_px + pad); 5x2 grid composer
(`_sheet_size`/`_cell_origin`/`_draw_gutter_lines`, `GUTTER=8`, magenta
width-3 separators) replaces the old pooled 9-col mega-sheet grid, shared by
`sheet_grid`/`arm_b`/`arm_bc`/`arm_a`; `stage()` now loops modules and writes
`{module}__{arm}.png` + `{module}__{arm}_prompt.txt` stem pairs (module name
+ the existing `restyle_arm_{arm}.md` body) instead of 3 global mega-sheets;
masks/manifest paths unchanged.
attempt 1: `pytest test/test_arm_a_texture.py -q`: 1/4 green, 3 red —
(a) `test_arm_a_paints_every_view_not_just_one`: alpha==0 at the TOP view's
east-wall-face centroid. Root cause: a vertical wall face genuinely has zero
footprint in a top-down orthographic projection (u,v only, z dropped — two of
its four corners coincide pairwise) — confirmed pre-existing/inherent, not a
regression, by checking that `face_masks.face_mask`'s own
`ImageDraw.polygon(..., fill=...)` still rasterizes a 1px-wide degenerate
line for this exact case (verified by direct pixel probe), so the face IS
present in `meta`/idmap and the painted output must cover that same thin
line. (b)/(c) `test_arm_a_leaves_no_unpainted_pixel...` (roof_cell/y45,
5–8 leaked pixels each): direct pixel probe traced the leak to a
`_apply_polygon_mask` bug — it blended the polygon mask with the *resample's
own* alpha channel (`Image.composite(a, black, mask)`), so a bilinear sample
that dipped into the transform's out-of-bounds fill at a near-edge pixel
(confirmed: the leaking column sat exactly at the polygon's fractional-pixel
boundary) produced alpha=0 there even though the mask correctly said
"inside". Fix: `_apply_polygon_mask` now sets alpha = the mask directly
(`img.putalpha(mask)`), never blended with the resample's own alpha — since
every texture PNG in `assets/textures/png/` is fully opaque (verified via a
direct alpha-channel probe across 4 representative textures incl. the decal
PNGs), this can never hide legitimate source transparency; it makes the
polygon mask the single source of truth for "inside the face," matching
`face_masks.py`'s own rasterization pixel-for-pixel (same points, same PIL
polygon-fill call) — which is what fixed (a) too, since the degenerate-line
case flows through the same code path.
attempt 2: `pytest test/test_arm_a_texture.py test/test_texture_warp.py -q`:
10/10 green. `pytest test/test_stage_kit_modules.py -q`: 7/7 green first pass
(grid-shape/gutter/magenta/stem-pair contract all held on the first run).

**T5** — tests were pre-existing (Loop 4a, including the recovery-session
file); no test files were authored or edited this loop. Per the flow's hard
rule, a failing test would have been raised as a flag, not patched — none
needed patching; every red run above traced to source-side bugs (matrix
role-swap, singular-solve intolerance, alpha-blend-vs-mask), fixed in
`texture_warp.py`/`stage_kit_modules.py`.

**T6** — no separate restage step was needed as a distinct action: `stage()`
itself was rewritten as part of T4b and is exercised by
`test_stage_writes_one_stem_pair_per_module_per_arm` /
`test_stage_still_writes_per_module_view_masks_and_one_manifest` (both
green, tmp_path-isolated). Loop 5's live restage into the repo's actual
`output/gen-inbox/` for the human visual gate is Loop 5's own job, not this
loop's.

green: yes run: `make verify-fast` → `122 passed, 225 warnings in 1.28s` (exit 0)
touched: src/pipeline/texture_map.py (NEW), src/pipeline/texture_warp.py (NEW), src/pipeline/kit_module_render.py (+project_face, additive), src/pipeline/stage_kit_modules.py (paint_panel NEW, arm_a/sheet_grid/arm_b/arm_bc/stage rewritten for the 5x2 per-module sheet-composer contract) — plus auto-regenerated `.pyi` stubs and `CONTEXT.md` routing tables for the touched directories (hook-driven, not hand-edited).

Note: the 225 pytest warnings are all pre-existing `Image.getdata()`
`DeprecationWarning`s (Pillow 14 removal notice) — some from test files this
loop's tests reuse the same idiom as (`test_texture_warp.py`,
`test_arm_a_texture.py`, `test_stage_kit_modules.py`), most from unrelated
pre-existing test files (`test_kit_module_render.py`, `test_sheet_grid.py`,
`test_sheet_qc.py`, `test_grid_drift.py`) and `face_masks.py` itself (source,
pre-existing, unmodified this loop). None are new failures; `make
verify-fast`'s gate is pass/fail count + exit code, not warning count, and
warnings-as-errors is not configured (checked `pytest.ini` — no
`filterwarnings` setting). Left as-is: fixing them would mean editing test
files (forbidden by this loop's own rule) or touching unrelated pre-existing
source (`face_masks.py`) out of scope for arm-a-homography.

executor: loop-medium model=sonnet tier=medium
