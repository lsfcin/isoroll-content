# Loop 3 — Architecture: arm-a-homography

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

## Architecture

Data flow (view-invariant texture, view-dependent screen): canonical un-yawed
`world_pts` per face → texcoords (T2, from WORLD only) → homography → `screen_poly`
(already yawed+projected by `ordered_faces`). `world_pts[k] ↔ screen_poly[k]` are
index-aligned (both share Face.pts corner order; ordered_faces yaws+projects in place),
so corner correspondence is by INDEX — never by a hand-authored index map.

**src/pipeline/texture_map.py** (NEW, T1) — pure lookup, no PIL geometry.
- `load_textures() -> dict` : parse `assets/textures/textures.json` (cached). Each entry: `{png, type, dims_voxels, continuity}`.
- `FAMILY(module, kind, normal) -> family_str` : table. blank/thatch mat→stone. Horizontal top of base→`floor_stone`; top of wall_band/top_cap/diag_half→`wall_{mat}_top`; any `side`→`wall_{mat}_side`; roof slope/gable→`roof_shingle`, roof bottom→`floor_stone`. Stair (module.startswith("stair")): `top`→`stair_tread`; `side` with |normal·x̂|>0.9 (‖±u)→`stair_riser`; `side` ‖±v/back→`wall_stone_side`; `bottom`→`floor_stone`.
- `variant(family, world_pts) -> texture_id` : n = #variants in family; `col=(round(min_u*4), round(min_v*4))`; `id = f"{family}_v{1+ hash((family,col))%n}"`. Depends ONLY on canonical world column ⇒ identical across all 9 yaw views (R1 / iso-visual: same spot=same look). Guarantees ≥2 variants appear on a multi-column face (C8).
- `face_texture(module, kind, world_pts, mat) -> {id, type, dims_voxels}` : FAMILY∘variant∘load. No KeyError on any module (blank default).
- `recess_decals(module) -> [(decal_id, world_quad)]` : recess_door→(`door_1x2x0`, quad u∈[0.15,0.85] v=1 z∈[0,2]); recess_window→(`window_1x1x0`, u∈[0.15,0.85] v=1 z∈[1,2]); else []. Quad order pinned **[BL,BR,TR,TL]** = [(u0,1,z0),(u1,1,z0),(u1,1,z1),(u0,1,z1)] (z0 bottom).

**src/pipeline/texture_warp.py** (NEW, T2) — the geometric core; PINNED AXES below.
- `face_axes(world_pts) -> (Ah, Av, dims_h, dims_v)` : normal `N=norm((W1-W0)×(W2-W0))`. Regime by `|N·ẑ|`:
  - HORIZONTAL `|N·ẑ|>0.9` (top/bottom/tread/floor): `Ah=+x̂`, `Av=+ŷ`. No z; image-y→+v (no flip).
  - VERTICAL `|N·ẑ|<0.1` (side/riser/wall): `Av=+ẑ`, `Ah=norm(ẑ×N)`. Image-up=world-up (FLIP y).
  - SLOPED else (roof slope quads AND roof gable tris — verified `|N·ẑ|≈0.17..0.71`, so gables route HERE, not VERTICAL): `Ah=norm(ẑ×N)` (across-slope, ‖ridge), `Av=norm(N×Ah)` sign-fixed to `Av·ẑ>0` (up-slope). FLIP y. len==3 → AFFINE.
  - `dims_h = dims_voxels[argmax|Ah_xyz|] or 1.0`; `dims_v = dims_voxels[argmax|Av_xyz|] or 1.0`.
  - Anti-mirror: `Ah=norm(ẑ×N)` is image-RIGHT in the outside-viewer frame (e.g. south wall N=+ŷ → Ah=-x̂, correct: looking -y, +x is viewer-left). Chirality preserved, never a raw index map.
- `_texcoords(world_pts, Ah, Av, dims_h, dims_v) -> [(sx,sy)]` per corner: `a=dot(W,Ah)/dims_h` (absolute world → continuity/determinism, C3), `b=dot(W,Av)/dims_v`; `sx=(a-⌊min a⌋)*tile_w`, `sy=(⌈max b⌉-b)*tile_h` (flip: high z→small y). ≥0.
- `warp_tiling(tex_img, world_pts, screen_poly, dims_voxels) -> RGBA cell tile` : axes→texcoords→tile `tex_img` to (⌈max sx⌉,⌈max sy⌉)→map tiled-source corners→screen_poly via `Image.transform(PERSPECTIVE)` (len==4) / `AFFINE` (len==3)→paste through polygon mask of screen_poly.
- `warp_decal(tex_img, world_quad, screen_quad) -> RGBA` : same corner machinery with `dims_voxels`=opening world dims ⇒ exactly 1 tile, source NOT tiled/wrapped (outside→transparent). Reuses the anti-mirror path so decals can't flip.

**src/pipeline/kit_module_render.py** (T3, additive only): `project_face(pts, view, s, cell_px, pad, origin) -> screen_poly` — yaw about (0.5,0.5)+`Cam(scale=s,origin=origin).pt` for yN, ortho `(ox+u*s, oy+v*s)` for TOP. Byte-identical transform to `ordered_faces`; does NOT touch ordered_faces/render_panel/render_module.

**src/pipeline/stage_kit_modules.py** (T4/T4b):
- `paint_panel(module, view, ordered, s, cell_px, pad, origin) -> RGBA` : for each `(face_id,kind,mat,poly)` in `ordered` (FAR→NEAR order preserved, so composite = correct occlusion): `i=int(face_id.split(':')[0])`; `world_pts=km.MODULES[module]()[i].pts`; `spec=texture_map.face_texture(...)`; load+cache PNG; `warp_tiling`; alpha-composite onto cell. Then `recess_decals(module)`: `project_face(quad)`→`warp_decal`→composite. Zero MAT_COLORS fills remain (C1).
- `arm_a(panels, ordered_by_panel)` : signature KEPT; loops panels, calls `paint_panel` with `p["origin"]` + the shared `s`; returns the SAME per-module 9-view sheet layout arm_b/arm_bc produce (via the shared composer).
- `module_sheet(arm_fn, module, module_panels, cell_px, pad) -> Image` (shared by all arms) : grid `_module_grid(9)=(cols=5,rows=2)` → 10 cells, views 0..8 in VIEWS order, cell 9 (bottom-right) left EMPTY (watermark). Uniform `pad` gutter; MAGENTA=(255,0,255) width-3 separators on gutter lines (existing convention). No per-panel autofit — one shared `s` (R3/C4).
- `stage(out, out_masks)` : ONE global `s=shared_scale(all_modules)` (C4). For each module × arm∈{a,b,bc}: write `{module}__{arm}.png` + `{module}__{arm}_prompt.txt` (=`prompts/restyle_arm_{arm}.md` body, module name prepended). Masks/meta/manifest still to `masks/` (unchanged). Amend `test_stage_kit_modules.py` per R2 (stem-pair contract replaces "exactly 3 sheets").

## Evaluation
criteria-coverage:
  C1→paint_panel (warp fills every ordered face, no MAT_COLORS) · C2→texture_map.FAMILY+variant · C3→texture_warp._texcoords (world-absolute reps) + warp_decal (1 tile) · C4→one global shared_scale, reps ÷dims_voxels not pixels · C5→module_sheet + stage stem pairs · C6→T5 amended+new tests · C7→paint_panel vs face_masks idmap · C8→variant() view-invariant
seams (testable):
  - test_texture_map: face_texture id per module/kind (incl wood + stair riser‖±u + roof); recess_decals ids/quads; variant() ≥2 distinct on a multi-col face and equal across 2 yaws (C8).
  - test_texture_warp: solid-PNG fills screen_poly interior mask-tight, outside transparent; z0..3 wall tiles vertically 3× and rep-count INVARIANT to cell_px (C3/C4); 3-corner gable AFFINE runs; **not-mirrored**: chiral/marked PNG on a vertical face keeps top-marker at min-y screen corner AND same physical corner across y45/y225 (corner-correspondence guard — the pinned-axes risk).
  - test_arm_a_texture: (C1) every ordered-face interior sample non-black & not a single MAT_COLORS RGB; (C7) crop fixture cell, ∀ pixel where face_masks idmap>0 assert render pixel non-background.
  - test_stage_kit_modules (amended): per-module stem pairs exist, count = n_modules per arm, bottom-right cell region background, magenta separators present.
verdict: PASS
- No criterion orphaned; every seam is code-asserted (iso-visual HARD RULE — geometry by code, human eyeballs only the final style gate). Corner-correspondence (top geometric risk) is closed by the unified normal-derived axis table + the not-mirrored test, not by any hand index map.

executor: loop-high model=opus tier=high
