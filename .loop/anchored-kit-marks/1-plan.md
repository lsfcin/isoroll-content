# Loop 1 — Plan: anchored-kit-marks

## Carry
slug: anchored-kit-marks | branch: loop/anchored-kit-marks | root: /mnt/workspace/code/isoroll-content
test-cmd: `python3 -m pytest -q` | e2e-cmd: none (Loop 5 scripts `stage_kit_modules.stage()` — the real staging entrypoint)
criticality: normal | verdict: standard
criteria:
  C1 anchors-projected: cyan anchors = a UV-lattice per module face, SAMPLED on each face's ALREADY-PROJECTED polygon (the poly already carries `_yaw`+`Cam.pt`); placement is a function of geometry+view, never of cell pixel size.
  C2 cross-view-stability: same physical anchor (stable `face_id` + lattice index) renders the SAME symbol glyph in all 9 views (8 yaws + TOP).
  C3 edge-on-collapse: in an edge-on yaw, a face's projected-anchor x-spread << that face's x-spread in its frontal yaw.
  C4 residue-invariant: residue(arm_bc) > 0 AND residue(arm_b) == 0 (existing test contract).
  C5 restage: arm sheets regenerated + restaged into output/gen-inbox/ via `stage()`; facemasks + manifest stay consistent.
  C6 suite-green: full pytest green (82 baseline + new placement tests).
tasks:
  T1 — face_anchors projector (sample projected poly; stable id=face_id#k; quads+tris) — src/pipeline/kit_module_render.py — high
  T2 — lift canonical apply_anchored overlay into guide_marks; scene_anchors delegates — src/pipeline/guide_marks.py, src/pipeline/scene_anchors.py — low
  T3 — arm_bc rewrite: build panel_specs from p["ordered"] anchors, module-namespaced ids, call guide_marks.apply_anchored — src/pipeline/stage_kit_modules.py — medium
  T4 — C1/C2/C3 placement tests (attribute-access, not top-import) + keep C4 — test/test_face_anchors.py, test/test_stage_kit_modules.py — medium
  T5 — restage gen-inbox via stage() + full suite green — output/gen-inbox/ (gitignored) — medium
context: CONTEXT.md, src/CONTEXT.md, design/RENDER-RESTYLE-MEMO.md, core/skills/iso-visual.md

## Orchestrator notes (carried verbatim from 0-clarify — bind Loop 2 & Loop 6)
- BASE: create `loop/anchored-kit-marks` from `loop/kit-module-renderer` tip **4759923** (doc-branch lineage; develop lacks design/ tree). Confirmed: HEAD is at 4759923.
- DIRTY-TREE FENCE: pre-existing `M CONTEXT.md` AND `D assets/tiles/dungeon_floor/concept/floor_dungeon_concept_raw.png` are NOT part of this loop. Never commit/revert/modify them. Loop 6 lists both under `extras: pre-existing-dirty`.
- gen-inbox artifacts are gitignored (`output/` in .gitignore); "restage" = files on disk, not commits.
- Symbol glyph size stays SCREEN-SPACE (fixed radius); only anchor POSITIONS transform.

## Plan
branch: loop/anchored-kit-marks  base: 4759923

Key design fact (pins T1, removes the main drift risk): the dimetric projection is AFFINE — `_proj(u,v,z) = ((u-v)·UX, (u+v)·UY − z·UZ)`, `_yaw` is a rotation, `Cam.pt` is scale+offset; no perspective divide. Affine maps commute with bilinear/barycentric corner combinations, so sampling a fixed lattice param on a face's already-projected `poly` EQUALS projecting the 3D face-plane lattice. T1 therefore samples the projected `poly` (from `ordered_faces`) directly — it must NOT re-implement `_yaw`/`Cam.pt`.

| id | task | files | done-when | tier | effort |
|----|------|-------|-----------|------|--------|
| T1 | `face_anchors(ordered, ...) -> [(anchor_id, x, y)]`: for each `(face_id, kind, mat, poly)` emit a deterministic UV-lattice sampled on `poly` (4-corner→bilinear, 3-corner→barycentric; interior params so points land ON the face). `anchor_id = f"{face_id}#{k}"`, `k` = fixed lattice index. Screen-space glyph radius stays a caller concern. | src/pipeline/kit_module_render.py | every returned anchor lies inside its face's projected `poly`; the multiset of `face_id`s (hence anchor ids) is identical across all 9 VIEWS of a module; no re-implementation of the projection transform | high | medium |
| T2 | Move the generic stable-symbol overlay to guide_marks as `apply_anchored(img, panel_specs, params)` — `panel_specs: [(view, (x0,y0,w,h), [(id,px,py)])]`, `_stable_symbols(all_ids)` → one glyph per id across every panel, fixed screen-space radius, faded alpha. Refactor scene_anchors to `from guide_marks import apply_anchored` and delete its local copy (behavior-preserving verbatim move; keeps DRY). | src/pipeline/guide_marks.py, src/pipeline/scene_anchors.py | `guide_marks.apply_anchored` exists; `python3 -c "import scene_anchors, scene_guide_sheet"` OK; suite still 82 green | low | low |
| T3 | Rewrite `arm_bc(panels)` (keep signature `-> RGB sheet`): for each panel take `p["ordered"]`, call `kmr.face_anchors(...)`, offset each anchor by cell origin `(col*cell_w, row*cell_h)`, namespace ids with `p["module"]` (so cross-module anchors never share a glyph), build `panel_specs`, call `guide_marks.apply_anchored`. Mirror arm_a's per-face loop shape (stage_kit_modules.py L65-77). Drop the old full-cell `rects` + `apply_marks` path for arm_bc. | src/pipeline/stage_kit_modules.py | residue(arm_bc)>0, residue(arm_b)==0; symbols sit on projected faces per T4; arm_b path untouched | medium | medium |
| T4 | New `test/test_face_anchors.py`: C1 (each anchor within its projected `poly`), C2 (anchor-id set identical across the 9 views of a module + `_stable_symbols` gives one glyph per id), C3 (for a `wall_band` side face, min-over-yaws x-spread < 0.3 × max-over-yaws x-spread). Import via `import kit_module_render` + attribute access INSIDE test bodies (missing fn → clean FAILED, not collection abort — repo convention). Keep C4 residue tests in test_stage_kit_modules.py green. | test/test_face_anchors.py, test/test_stage_kit_modules.py | red-run: new tests fail for missing behavior (not import/syntax); C4 tests still pass | medium | medium |
| T5 | Run `stage()` to regenerate output/gen-inbox/ (3 arm sheets + facemasks + manifest); run full pytest. | output/gen-inbox/ (gitignored) | arm_bc.png regenerated with anchored marks; arm_b symbol-free; facemasks+manifest consistent; `python3 -m pytest -q` green (≥82 + new) | medium | low |

## Plan Review (adversarial, assume small executors)
- R1 (FATAL if unmanaged) — a medium executor re-derives `_yaw`/`Cam.pt` inside `face_anchors` and drifts from the drawn geometry → C1 breaks. FIX: T1 pinned to sample the ALREADY-PROJECTED `poly`; affine-commutes rationale stated in `## Plan`; done-when forbids re-implementing the transform.
- R2 — 4-corner bilinear applied to a 3-corner face (roof gables are triangles) → IndexError / off-face point. FIX: T1 done-when + row text require quad→bilinear, tri→barycentric.
- R3 — `face_id` (`"0:top"`) repeats across modules → wall_band and roof_cell share a glyph. FIX: T3 namespaces ids by `p["module"]`.
- R4 — C3 test hardcodes a yaw guessed as "edge-on" → flaky/false. FIX: T4 compares min-over-yaws vs max-over-yaws spread of one face; no hardcoded edge-on yaw.
- R5 — glyph size scaled by face/projection → violates "screen-space glyph" note. FIX: T2 fixed screen-space radius (the moved scene_anchors body already does this).
- R6 — `arm_bc` signature/return changed → uneditable `test_arm_bc_...` breaks. FIX: T3 keeps `arm_bc(panels) -> RGB sheet`; test_stage header already routes a shape mismatch to `RETURN loop=4a`.
- R7 — scene_anchors is untested by the suite; moving its fn could silently break scene_guide_sheet. FIX: T2 is a verbatim, behavior-preserving move (identical body) + import smoke of scene_guide_sheet + green suite as ground truth. Residual risk low.
- R8 — Loop 4a red-run aborts collection because `from kit_module_render import face_anchors` fails on a missing name. FIX: T4 pins attribute access inside test bodies (repo's lazy-import convention).
- Scope note: guide_marks.py is added to scope beyond 0-clarify's scope-files list — it is the mark library and the correct, DRY home for `apply_anchored`; not creep. Verdict stays `standard` (4 src files, new internal API `face_anchors`).
verdict: PASS

executor: loop-high model=opus tier=high
