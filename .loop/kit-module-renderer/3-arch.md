# Loop 3 — Architecture — kit-module-renderer

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

## Architecture

AMENDMENT to Loop-1 plan (binding — overrides stale plan text; medium executors follow THIS):
The plan's "builders return `list[Box]`" and T2's "project through `render_boxes`" are NOT
buildable as written. `layout_massing.Box` is axis-aligned (u0,v0,l,d,h) and `render_boxes`/`_faces`
only emit the 3 faces visible to the FIXED 4-view camera. A 45°·k yaw (odd k) makes boxes
non-axis-aligned, and the diagonal-half-band + sloped roof have non-rectangular footprints. So the
shared representation is a FACE, not a Box. Box-shaped modules use an `extrude()` helper; `render_boxes`
is NOT reused for yaw panels. T1 return type and T7 assertions change accordingly (see below). No
criterion is affected — only the internal seam. Reuse-note: `layout_massing`/`layout_groups` are still
read for the stair-step math (STEPS/STAIR_RISE) and diagonal direction (`diag_solid`), but their Box
output is converted to faces via `from_boxes`.

- src/pipeline/kit_modules.py (+.pyi) — T1 — module geometry as faces at world origin (unit cell, yaw NOT baked).
  - `@dataclass Face`: `pts: list[tuple[float,float,float]]` (3–4 CCW corners in u,v,z), `kind: str`
    (one of "top"|"side"|"bottom"|"tread"|"riser"|"slope"|"gable"), `mat: str` (arm-a material tag:
    "stone"|"wood"|"thatch"|"blank"; default "blank").
  - `extrude(footprint, z0, h, mat="blank") -> list[Face]` — footprint = list[(u,v)] (any polygon):
    emits top face (z0+h, kind="top"), bottom (z0, kind="bottom"), one "side" per footprint edge.
  - `from_boxes(boxes) -> list[Face]` — convert `layout_massing.Box` rectangles via `extrude`
    (footprint = the 4 corners); used only where box seams already exist (stairs).
  - `MODULES: dict[str, () -> list[Face]]` with EXACTLY these 9 builders (C1; "recess" and "stair"
    are the two variant-types → "8 module types"): `wall_band` (1u×1u×wall_h thin slab), `top_cap`
    (thin z-band at top of a cell), `base` (thin z-band at bottom), `recess_door` / `recess_window`
    (wall_band minus an `Opening`-shaped hole on ONE side face — carve by splitting that side into
    border faces, matching `_draw_openings` door=1w×2h / window=1×1@z1..2), `diag_half` (thin rotated
    rectangle footprint corner→corner, extruded to wall_h — 45° in the module's own frame),
    `roof_cell` (triangular-prism wedge: two "gable" end triangles + two "slope" rect tops + bottom),
    `stair_45` (STEPS treads full rise via `from_boxes(_stair_boxes-style)`), `stair_half` (same, rise
    halved). Every builder returns a non-empty `list[Face]`.

- src/pipeline/kit_module_render.py (+.pyi) — T2+T3 — the SHARED projected-face seam + flat render + scale.
  - `YAWS = [0,45,90,135,180,225,270,315]`; `VIEWS = [*("y0".."y315"), "TOP"]` (9 panels/module).
  - `_yaw(pt, deg, cu, cv) -> pt` — rotate (u,v) about module centre (cu,cv) by deg; z unchanged.
  - `ordered_faces(faces, view, cam) -> list[(face_id, kind, mat, screen_poly)]` — THE canonical seam,
    consumed by BOTH render and mask. For yaw views: rotate every Face by its yaw, project each corner
    through a fixed-scale dimetric `scene_guide_render.Cam` (scale=s, per-panel origin), sort faces
    far→near by painter key `(centroid_u+centroid_v, centroid_z)` ascending. For "TOP": orthographic
    top projector `(u*s, v*s)` sorted by centroid_z ascending. `face_id = f"{i}:{kind}"` (i = builder
    face index) — stable, deterministic. Last-painter-wins gives occlusion by construction.
  - `panel_extent(faces, view, s=1.0) -> (w,h)` — projected bbox of a panel at scale s (for T3).
  - `shared_scale(module_names, cell_px, pad) -> float` — s = min(avail/max_w, avail/max_h) over the
    LARGEST panel across ALL module×view combos (P3: one s per sheet, never per-cell); avail=cell_px-2*pad.
  - `render_panel(faces, view, s, cell_px, pad) -> (RGBA, origin, ordered)` — build a fixed-scale Cam
    centring this panel's bbox in the cell; fill each ordered poly flat (kind→colour: top=FACE_TOP,
    side/slope/gable/tread/riser=FACE_LONG, bottom=FACE_CAP); alpha via `kit_render._black_to_alpha`;
    RETURN `ordered` so mask/arm-a reuse identical geometry (no recompute → guaranteed pixel alignment).
  - `render_module(name, s, cell_px, pad) -> dict[view -> (RGBA, ordered, origin)]` (9 entries).
  - `build_sheet_manifest(panels, s) -> dict` — `{px_per_voxel: s, panels:[{module,view,bbox,origin}]}`.

- src/pipeline/face_masks.py (+.pyi) — T4 — id-indexed occlusion masks from the SAME ordered faces.
  - `face_mask(ordered, size) -> (Image "L", dict{face_id:{color_idx,bbox,pixels}})` — rasterise each
    ordered poly IN ORDER into a single-channel id map (fill value = 1-based paint index); last write
    wins → regions are single-valued (pairwise non-overlap by construction) and union ⊆ silhouette.
    Takes the `ordered` list produced by `render_panel` (do NOT recompute geometry).
  - `save_mask(idmap, meta, path)` — write `<panel>_facemask.png` + `<panel>_faces.json`.

- src/pipeline/stage_kit_modules.py (+.pyi) — T5 — compose 3 arm sheets → output/gen-inbox/ (gitignored).
  - `sheet_grid(panels) -> Image` — cols=len(VIEWS)=9, total_cells=len(panels)+1, rows=ceil(total/cols);
    paste panels row-major centred in each cell; the trailing cell(s) incl. BOTTOM-RIGHT stay black
    (NB watermark slot — C4). Reuse `stage_kit_paint.py` centre-paste math (replicate; don't import
    from design/ into src/).
  - `arm_b(panels)` = grayscale sheet; `arm_bc(panels)` = arm_b + `guide_marks.apply_marks(sheet,
    [(view,(x,y,w,h))…])`; `arm_a(panels, ordered_by_panel)` = per-face procedural fill (deterministic
    self-contained texture keyed by `face.mat`; grayscale fallback on unknown mat).
  - `stage(out="output/gen-inbox") -> None` — one s via `shared_scale`; write 3 sheets + per-sheet
    manifest json + facemasks + copy the 3 restyle prompts.

- src/pipeline/prompts/restyle_arm_{b,bc,a}.md — T6 — whole-sheet restyle text; guidance dial c<b<a
  (memo); each states: keep geometry / restyle only, bottom-right = watermark (leave empty), dimetric.

- test/test_kit_modules.py (+.pyi) — T7a — each MODULES builder returns non-empty faces with expected
  kinds present (AMENDED from box-count: assert face kinds/counts per module, deterministic).
- test/test_kit_module_render.py (+.pyi) — T7b — `render_module` yields 9 panels; per-yaw silhouette
  bbox (via `sheet_qc.silhouette_mask` → getbbox) is deterministic AND differs across ≥4 of 8 yaws
  (no mirror chirality); shared-scale invariant: every panel manifest records the identical px_per_voxel;
  `face_mask` regions single-valued (non-overlap) and union ⊆ `silhouette_mask`.

## Evaluation
criteria-coverage:
  C1 → kit_modules.MODULES (9 builders, all C1 items) + render_module flat-shade over YAWS+TOP.
  C2 → shared_scale (single s from global-max panel) + build_sheet_manifest.px_per_voxel; every
       render_panel/TOP is forced with that s (no autofit path reached).
  C3 → face_masks.face_mask fed the SAME `ordered` list render_panel used → pixel-aligned id map.
  C4 → stage_kit_modules.{arm_b,arm_bc,arm_a} + sheet_grid trailing-cell-blank → output/gen-inbox/.
  C5 → test_kit_modules + test_kit_module_render; existing 53 untouched (all-new files/tests).
seams:
  C1 → per-builder face-kind/count asserts (deterministic geometry).
  C2 → assert all manifest panels share one px_per_voxel; assert no panel extent > cell at s.
  C3 → assert id map single-valued (each pixel one id) and union-mask ⊆ silhouette_mask.
  C4 → assert 3 sheet files exist, bottom-right cell all-black, residue(arm_bc)>0 & residue(arm_b)==0.
  C5 → `python3 -m pytest -q` ≥ 53 + new, fully green.
edge-cases resolved (no downstream guess):
  - 8 yaws = continuous 45°·k about module centre (NOT rotate_cw / NOT render_boxes); depth key given.
  - non-Box geometry (diag_half, roof_cell) expressed via `extrude`/explicit faces, not Box.
  - watermark: cols=9, rows=ceil((N+1)/9) → last cell (bottom-right) guaranteed blank.
  - arm-a has no repo texture assets → deterministic procedural fill keyed by face.mat (in-scope,
    self-contained), grayscale fallback — matches Loop-1 plan-review resolution.
verdict: PASS

executor: loop-high model=opus tier=high
