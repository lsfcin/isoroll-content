# Loop 1 — Plan — kit-module-renderer

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

## Plan
branch: loop/kit-module-renderer (base: loop/dsl-v2-python @45a2f97 — has design/ tree + frozen docs; NOT develop)

| id | task | files | done-when | tier | effort |
|----|------|-------|-----------|------|--------|
| T1 | Define the 8 KIT V2 module types as Box/voxel builders. Reuse `layout_massing.Box`/`Opening` (band=1u wall run; cap/base=sub-voxel z-bands via `z0`/`h`; recess bands=door/window `Opening`; stairs via massing `STEPS`/`STAIR_RISE` for 45° and half-slope), and `layout_groups.diag_solid`/`grp_cell_voxels` for the diagonal half-band. One builder per type returning a `list[Box]` at world origin (rotation NOT baked — T2 rotates). | src/pipeline/kit_modules.py (+.pyi) | each of the 8 builders imports clean and returns a non-empty `list[Box]`; a MODULES registry maps name→builder; unit test asserts box counts/kinds per type | medium | medium |
| T2 | Render one module across 8 yaws + TOP, flat-shaded (grayscale FACE_TOP/LONG/CAP ramp). 8 yaws = rotate module Box corners in CONTINUOUS space by 45°·k (k=0..7) — NOT `rotate_cw` (integer grid = only 4). Project through fixed dimetric `scene_guide_render.Cam`/`render_boxes` with an explicit `scale=` (never autofit). TOP = orthographic plan (top face only) honoring the SAME forced `scale`. Alpha via `kit_render._black_to_alpha`. | src/pipeline/kit_module_render.py (+.pyi) | `render_module(name, scale)` returns 9 RGBA sprites (8 yaw + TOP); each non-blank; silhouette bbox differs across ≥4 of the 8 yaws (no mirror-chirality) | high | high |
| T3 | Compute one shared `s` (px per world unit) from the LARGEST module×view bbox across ALL panels of the sheet (measure via `kit_render._bbox`-style corner projection at s=1; pick s so max panel fits cell). Feed the same `s` into every T2 render (dimetric + TOP). Write sheet manifest json: `px_per_voxel`, per-panel `{module,view,bbox,origin}`. | src/pipeline/kit_module_render.py | manifest json emitted; every panel records the identical `px_per_voxel`; assertion that no panel exceeds cell at `s` | medium | medium |
| T4 | Emit a per-face mask beside each render. Reuse the visible-face polygon generator in `scene_guide_render` (yields top/long/cap polygons per box in painter order). Rasterize each face polygon into a face-id map in the SAME draw order → last-painter-wins gives occlusion-correct, non-overlapping regions. Emit `<panel>_facemask.png` (id-indexed) + json `{face_id: [pixel count / bbox]}` per panel. | src/pipeline/face_masks.py (+.pyi) | each rendered panel has a companion facemask; mask regions are pairwise non-overlapping; union ⊆ sprite silhouette; ≥ top+one-side face ids present per non-TOP panel | high | high |
| T5 | Stage 3 arm sheets to output/gen-inbox (gitignored). Reuse `stage_kit_paint.py` grid/paste pattern. arm-b = grayscale panels; arm-bc = arm-b + cyan symbols via `guide_marks.apply_marks`; arm-a = flat-fill each face polygon (from T4 masks) with a per-material PROCEDURAL texture (self-contained, no external assets; stone/wood/thatch by module face-kind; missing→grayscale fallback). All three: one sheet per arm, shared scale (T3), BOTTOM-RIGHT cell left EMPTY. Also copy facemasks + sheet manifest into gen-inbox. | src/pipeline/stage_kit_modules.py (+.pyi), output/gen-inbox/ | running the staging script writes 3 arm sheets + per-sheet manifest + facemasks under output/gen-inbox/; bottom-right cell of each sheet is blank (all-black); arm-bc has cyan residue > 0, arm-b has 0 | medium | medium |
| T6 | Author whole-sheet restyle prompt text per arm (guidance-strength dial c<b<a per memo): arm-b blank-technical, arm-bc blank+cyan-symbols, arm-a real-texture. Keep "bottom-right cell = watermark, leave empty" + "keep geometry, restyle only" instructions. | src/pipeline/prompts/restyle_arm_b.md, restyle_arm_bc.md, restyle_arm_a.md | 3 prompt files exist; each names its arm's guidance strength + the empty-cell + geometry-preservation rules; T5 writes each beside its sheet | low | low |
| T7 | Golden tests. (a) geometry: per module, per yaw — silhouette bbox is stable/deterministic (assert against recorded goldens) and shared-scale invariant holds (all panels one `s`); reuse `src/cli/sheet_qc.silhouette_iou` for silhouette checks. (b) mask: facemask regions non-overlapping ⊆ silhouette. Keep full existing suite green. | test/test_kit_modules.py, test/test_kit_module_render.py (+.pyi) | new tests pass; `python3 -m pytest -q` fully green (≥ prior 53 + new) | medium | medium |

## Plan Review (adversarial, assume small executors)
- "8 yaws" is undefined vs the 4-view dimetric renderer (`VIEW_TURNS` = SW/SE/NE/NW only; `rotate_cw` is 90° integer-grid). A medium executor would wrongly reuse `rotate_cw` and get 4 views + mirror chirality (killed strategy). → FIXED: T2 row mandates CONTINUOUS 45°·k rotation of Box corners through the fixed dimetric Cam, no `rotate_cw`, no mirroring; T2 raised to **high**; done-when asserts ≥4 distinct silhouettes.
- arm-a "real textures mapped flat" has NO source-texture assets in the repo (grep confirmed none) — an unstated intent gap that would block a medium executor. → FIXED in-plan (not an intent gap): T5 specifies self-contained PROCEDURAL per-material fill of the face polygons (from T4 masks), swappable later, grayscale fallback on miss. No external dependency, deterministic, testable.
- Per-face masks could naively be raw polygons that overlap where a cap sits behind the top face (occlusion). → FIXED: T4 rasterizes in the renderer's painter order, last-painter-wins → occlusion-correct non-overlapping regions by construction; T4 raised to **high**; done-when asserts pairwise non-overlap ⊆ silhouette. The visible-face generator already exists in `scene_guide_render`, so the seam is real.
- C2 across BOTH regimes: TOP is an orthographic plan (different projection) — a per-cell autofit there would silently break the shared-scale guarantee. → FIXED: T3+T2 force the SAME `s` into the TOP render; done-when asserts one `px_per_voxel` for every panel incl. TOP.
- Diagonal half-band / stairs / roof geometry is subtle; T1 might guess wrong. → MITIGATED: T1 names the exact reuse seams (`layout_groups.diag_solid`/`grp_cell_voxels`, massing `STEPS`/`STAIR_RISE`, `Box.z0`/`h` sub-bands); T1 stays medium but may ESCALATE to high if a builder can't be expressed via those seams (escalation rule available).
- File-size/R1-R6 hooks (200 LOC hard block, 40 LOC/func, single-responsibility). → HANDLED by splitting into 4 small source files (kit_modules / kit_module_render / face_masks / stage_kit_modules) rather than one renderer; Loop 3 assigns responsibilities.
- Base-branch trap (repeat of sibling loop): building on `develop` loses the `design/` tree + frozen docs. → FIXED: Carry + Plan pin base = loop/dsl-v2-python @45a2f97; Loop 2 must branch from that ref, verified present in git log (0a4d990 + 45a2f97).
- Size check: 7 rows (≤10), strong reuse spine (Cam/render_boxes, layout_massing/groups, panel_geometry, guide_marks, sheet_qc, stage_kit_paint). Heaviest = T1/T2; both bounded and escalation-guarded. No split needed.

verdict: PASS

executor: loop-high model=opus tier=high
