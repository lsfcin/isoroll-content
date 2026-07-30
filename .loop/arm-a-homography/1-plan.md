# Loop 1 — Plan: arm-a-homography

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
tasks:
  T1 — texture_map.py (NEW): textures.json loader + MAPPING (module,kind,orientation)→texture role+variant, mat blank→stone default, stair-face classify by world normal, recess opening→decal id+world quad — src/pipeline/texture_map.py — medium
  T2 — texture_warp.py (NEW): warp_tiling + warp_decal; per-corner texture-px coords from world axes (orientation-safe), tiled source builder, polygon mask; PERSPECTIVE (4-corner) + AFFINE (3-corner) — src/pipeline/texture_warp.py — medium(→high if warp math fights)
  T3 — project_face(pts,view,s,cell_px,pad,origin) public helper (additive, mirrors ordered_faces transform) — src/pipeline/kit_module_render.py — low
  T4 — arm_a rewrite: per-panel textured paint_panel via T1+T2+T3; rebuild faces=km.MODULES[module]() index by builder-i from face_id; decals for recess; KEEP arm_a(panels,ordered_by_panel) signature + stage() output contract — src/pipeline/stage_kit_modules.py — medium
  T5 — tests: test_texture_map.py(C2), test_texture_warp.py(C3), test_arm_a_texture.py(C1+C4+C7) — test/ — medium
  T6 — restage stage() → gen-inbox 3 arm sheets; make verify-fast green (C5,C6) — no new files in out — low
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/src/pipeline/CONTEXT.md, /mnt/workspace/code/CONTEXT.md, /mnt/workspace/core/skills/iso-visual.md

## Plan
branch: loop/arm-a-homography (base loop/anchored-kit-marks @ 4126704 — PIN)

| id | task | files | done-when | tier | effort |
|----|------|-------|-----------|------|--------|
| T1 | New `texture_map.py`. Load `assets/textures/textures.json`. `face_texture(module, kind, world_pts, mat="blank") -> {id, type, dims_voxels}` via an explicit table: wall_band/top_cap/diag_half side→wall_{m}_side_v1, top→wall_{m}_top; base top→floor_{m}_v1, base/other bottom→floor_{m}_v1; recess_* kept faces same as wall_band; roof_cell slope+gable→roof_shingle_v1, bottom→floor_{m}_v1; stair_* top→stair_tread_v1, side w/ normal along ±u (world x)→stair_riser_v1, side w/ normal along ±v→wall_{m}_side_v1, bottom→floor_{m}_v1. `m` = `{blank:stone, stone:stone, wood:wood, thatch:stone}[mat]`. Separate `recess_decals(module) -> [(decal_id, world_quad_pts)]`: door u∈[.15,.85] z∈[0,2]→door_1x2x0, window u∈[.15,.85] z∈[1,2]→window_1x1x0; quad on v=1 plane. | src/pipeline/texture_map.py | `face_texture` returns the C2 id for every (module,kind) pair; `recess_decals` returns 1 quad for recess_door/window, [] otherwise; no KeyError on any module | medium | medium |
| T2 | New `texture_warp.py`. `warp_tiling(tex_img, world_pts, screen_poly, dims_voxels)`: (a) build face texture axes from world_pts — horiz axis = first world edge in u/v plane, vert axis = z (or 2nd u/v edge for flat top/floor faces); (b) per corner compute tex-px coords = (proj onto axes)/dims_voxels·tile_px, giving reps from world extent only (NOT pixels); (c) tile `tex_img` to ceil(reps) each axis; (d) map tiled-source 4 corners→screen_poly 4 corners via PIL `Image.transform(PERSPECTIVE)` solving 8 coeffs, or `AFFINE` when len(poly)==3; (e) paste through a polygon mask of screen_poly onto a transparent cell. `warp_decal(tex_img, screen_quad)`: same map, no tiling, single image. Return RGBA cell-size tile. | src/pipeline/texture_warp.py | warping a solid-color test PNG fills exactly the screen_poly interior (mask-tight); a wall side z0..3 tiles 3× vertically, 1× horizontally; 3-corner gable warps without error | medium | high |
| T3 | Add public `project_face(pts, view, s, cell_px, pad, origin)` to `kit_module_render.py` returning the screen poly for arbitrary world pts under the SAME transform `ordered_faces` uses (yaw about (0.5,0.5)+`Cam(...,scale=s,origin=origin).pt` for yN; ortho for TOP). Additive only — do not alter `ordered_faces`/`render_panel`/`render_module` or any existing return shape. | src/pipeline/kit_module_render.py | `project_face(f.pts,view,s,CELL,PAD,origin)` == that face's poly in `ordered_faces` output for the same view/cam; existing kit_module_render tests still green | low | medium |
| T4 | Rewrite `arm_a` in `stage_kit_modules.py`. Add `paint_panel(module, view, ordered, s, cell_px, pad, origin) -> RGBA`: for each `(face_id,kind,mat,poly)` in `ordered`, parse builder index `i=int(face_id.split(':')[0])`, get `world_pts=km.MODULES[module]()[i].pts`, `spec=texture_map.face_texture(module,kind,world_pts,mat)`, load+cache the PNG, `texture_warp.warp_tiling(...)`, composite onto the cell; then for `texture_map.recess_decals(module)` project the opening quad with `kmr.project_face` and `warp_decal`. `arm_a(panels, ordered_by_panel)` keeps its signature: loops panels, calls `paint_panel` with `p["origin"]`+shared `s` (thread `s` in via a module-level constant read or recompute once), pastes each cell at `(col*cell_w,row*cell_h)`. Delete `MAT_COLORS` reliance in arm_a (may keep constant unused elsewhere). stage() output contract unchanged (still 3 pngs+3 prompts to out, masks to masks/). | src/pipeline/stage_kit_modules.py | `test_arm_a_matches_the_sheet_grid_size` still green; arm_a output has zero pixels of any single MAT_COLORS RGB across a face interior (texture, not flat); stage() still writes exactly 3 pngs + 3 prompts | medium | high |
| T5 | Tests. `test_texture_map.py`: assert C2 ids for a representative face of each module + wood-variant path (`face_texture('wall_band','side',pts,'wood')==wall_wood_side_v1`) + recess decal ids. `test_texture_warp.py`: solid-PNG warp fills screen_poly & leaves outside transparent; vertical tile count for a z0..3 wall == 3 and is INVARIANT to cell_px (C4); 3-corner warp runs. `test_arm_a_texture.py`: (C1) for a fixture module+view every ordered face's interior sample is non-black & not a flat MAT_COLORS constant; (C7) render arm_a, crop the fixture cell, and for every pixel where `face_masks.face_mask(ordered,size)` idmap>0 assert the cropped render pixel is non-background. | test/test_texture_map.py, test/test_texture_warp.py, test/test_arm_a_texture.py | 3 new test files fail RED for missing-behavior at Loop 4a, then GREEN at 4b | medium | medium |
| T6 | Run `python -m stage_kit_modules`/`stage()` to restage gen-inbox (3 arm sheets, arm_a now textured); confirm `make verify-fast` fully green (93 old + new). Do NOT add files to output/gen-inbox beyond the existing contract. | output/gen-inbox/ (gitignored), — | verify-fast green; gen-inbox holds exactly 3 arm pngs + 3 prompts; arm_a.png visibly textured | low | low |

## Plan Review (adversarial, assume small executors)
- FATAL: every module is `mat="blank"`; no `wall_blank_*`/`floor_blank_*` texture exists → naive lookup KeyErrors → pinned `m` default map (blank→stone) in T1, so integration resolves to stone everywhere; wood path kept only as a tested mapping branch.
- FATAL: stair modules emit kinds `top/bottom/side` (via `from_boxes`→`extrude`), NEVER `tread`/`riser` → a `kind=='tread'` lookup gets nothing. Fixed: T1 classifies stair `top`→tread, `side` normal‖±u→riser, `side` normal‖±v→wall side, gated by `module.startswith('stair')`.
- FATAL: `arm_a` only receives screen polys (`ordered_by_panel`); tiling reps + decal need WORLD pts. Fixed: T4 rebuilds `km.MODULES[module]()` and indexes builder-`i` parsed from `face_id="{i}:{kind}"` (i is pre-sort, stable) — no change to the `ordered_faces` seam or face_masks.
- FATAL: decal opening quad is NOT a Face; adding it to `kit_modules` would break face-count tests (`test_kit_modules`, mask "every id survives"). Fixed: T1 synthesizes the opening world quad from `OPENING_MARGIN`+z-span; T3 `project_face` projects it; kit_modules.py untouched.
- FATAL: texture↔screen corner correspondence — a hardcoded index map warps some faces upside-down/mirrored (geometric wrongness = NOT acceptable per tolerance). Fixed: T2 derives per-corner texture coords by projecting world corners onto the face's world axes (dot products), never by literal index; Loop 3 must pin the two texture axes per face-kind. T2 tier raised to high if the corner-math review is not airtight.
- FATAL: 3-corner faces (roof gables) can't use a 4-point PERSPECTIVE solve. Fixed: T2 branches to AFFINE when `len(screen_poly)==3`.
- risk: `arm_a` signature/`stage()` contract are asserted by existing tests (`test_arm_a_matches_the_sheet_grid_size`, `test_stage_writes_three_arm_sheets...`) → T4 keeps `arm_a(panels, ordered_by_panel)` and writes no extra files; textures are READ from assets/, never written to out.
- risk: which module's top = "floor" vs "wall top" is underspecified in C2 → pinned in T1 (base.top→floor_stone; wall_band/top_cap/diag_half.top→wall_stone_top). Defensible, mechanical, testable; if Loop 3 disputes, adjust the T1 table only (no seam change).
- risk: texture variant (`v1..v8`) selection unspecified → pinned deterministic `v1` (tolerance allows visual imperfection; each view restyled independently, so cross-view variant identity is not required).
- scope: 6 rows, all ≤2 new-or-touched files each, no criterion orphaned (C1→T4, C2→T1, C3→T2, C4→T2/T4, C5→T6, C6→T5/T6, C7→T5). Within the 10-row / 80-line cap.
verdict: PASS

executor: loop-high model=opus tier=high

## Plan Correction (orchestrator — user input 2026-07-16, OVERRIDES the sections above; Loop 2 copies the Carry BELOW)

Lucas raised 3 concerns mid-flow; rulings binding on all later loops:

R1 — ALL texture variants, not pinned v1 (overrides review line "pinned deterministic v1"). If the guide shows no variation, NB reproduces none. `face_texture` selects variant deterministically from the face's stable world column index (e.g. `v = variants[hash((family, u_col, v_col)) % n]`) — same physical column ⇒ same variant in ALL 9 views (iso-visual: same spot = same appearance; per-view restyle does NOT relax this). T1 gains variant selection; T5 asserts a multi-column face shows ≥2 distinct variants and that variant choice is view-invariant.

R2 — ONE SHEET PER MODULE per arm (sheet-per-object), replaces the 3 mega-sheets. stage() writes per-module stems `{module}__{arm}.png` + `{module}__{arm}_prompt.txt` (gen-inbox stem-pair contract kept); masks stay per module. Existing "exactly 3 arm sheets" stage tests are AMENDED, not fudged — sanctioned contract change by user input. Dimensional vocabulary (wall heights, door sizes 1x1x0..2x3x0, middle/edge slice parts, per Lucas "render all we need to crop slices") is NOT absorbed into this chain — it multiplies kit_modules and would blow the cap; routed as follow-on chain proposal `kit-dimensional-vocabulary` (S4b, before S5) — Lucas confirms at the board gate.

R3 — sheet packing: minimal empty space BUT uniform gutter + magenta panel separators (existing grid convention) so NB never blends adjacent panels; bottom-right cell left empty (watermark absorber); panel bounds from the ONE shared per-sheet `s` (C4) — no per-panel autofit. Exact grid layout (3×3+caption vs 2×5) = Loop 3 decision within these constraints.

### Carry (AMENDED — copy THIS block verbatim from Loop 2 on)
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

leftover→ROADMAP (Loop 6): follow-on chain `kit-dimensional-vocabulary` (S4b, pre-S5): wall-height variants, full door set 1x1x0..2x3x0, middle/edge slice parts — pending Lucas confirm at board gate.
verdict: PASS (correction applied; plan still ≤10 rows)

executor: orchestrator model=claude-fable-5 tier=max (inline ruling — user input at plan seam, field-practice override)
