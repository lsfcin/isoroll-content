# Loop 3 — Architecture: anchored-kit-marks

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

## Architecture

This is a DELTA on already-shipped, green code (kit render + guide marks exist; 82 pass). Contract shapes (confirmed by reading source, binding for executors):
- `kit_modules.Face`: `.pts` = 3–4 CCW `(u,v,z)` corners (ring order from `extrude`); `.kind`; `.mat`. Quads=4 pts, tris=3 pts.
- `kit_module_render.ordered_faces(faces,view,cam) -> [(face_id, kind, mat, poly)]`; `poly` = same-length ring of screen `(x,y)`, ALREADY projected (yaw about (0.5,0.5) + `Cam.pt`); `face_id=f"{i}:{kind}"` stable across all 9 views (assigned pre-sort, no back-face culling → every face present in every view).
- `render_panel(...)->(rgba, ordered, origin)`; `stage()` stores this list as `p["ordered"]`; poly coords are PANEL-LOCAL (0..cell_px). Tests import bare (`conftest.py` adds src/pipeline to sys.path).

**src/pipeline/kit_module_render.py — ADD `face_anchors(ordered) -> [(anchor_id, x, y)]` [T1].**
Input is the projected `ordered` list (NOT raw faces — C1: sample the ALREADY-PROJECTED poly). For each `(face_id,kind,mat,poly)`, sample a FIXED parametric lattice and map each sample onto `poly` by CONVEX interpolation:
  - quad (len(poly)==4, ring p0,p1,p2,p3): bilinear `lerp(lerp(p0,p1,a), lerp(p3,p2,a), b)`; reference `LATTICE_QUAD=[(.25,.25),(.75,.25),(.75,.75),(.25,.75)]` → 4 anchors.
  - tri (len(poly)==3, corners A,B,C): barycentric `wa*A+wb*B+wc*C`; reference `LATTICE_TRI=[(.5,.25,.25),(.25,.5,.25),(.25,.25,.5)]` → 3 anchors.
  `anchor_id=f"{face_id}#{k}"`, k=lattice index (stable). INVARIANTS the executor must preserve (the criteria depend on them): lattice is fixed by face-arity, chosen WITHOUT reading cell_px → count/ids identical at any sheet scale (C1); ≥2 samples spread across each face's parametric axes → x-spread is view-dependent (C3); convex combo (weights in (0,1), sum 1) → every anchor inside its face's convex poly/bbox (C1). Exact lattice values are the executor's to keep so long as these hold.

**src/pipeline/guide_marks.py — RECEIVE `apply_anchored(img, panel_specs, params=None)` + `_stable_symbols(ids)` [T2].**
Move both VERBATIM from scene_anchors.py (behavior unchanged): `panel_specs=[(view,(x0,y0,w,h),[(id,px,py)])]`, one GLOBAL `_stable_symbols` map over ALL ids (`sorted(set(ids))` → `SYMBOLS[i%len]`), so a given id → same glyph in every panel. No new imports (uses local Image/ImageDraw/CYAN/MarkParams/SYMBOLS) → no cycle with scene_anchors.

**src/pipeline/scene_anchors.py — DELEGATE [T2].**
Delete its local `apply_anchored`/`_stable_symbols`; `from guide_marks import apply_anchored` (re-export). MUST keep `scene_anchors.apply_anchored` resolvable — `scene_guide_sheet.py:57` calls it. `anchors`/`project` stay; the now-unused `SYMBOLS` import may be dropped (non-critical).

**src/pipeline/stage_kit_modules.py — REWRITE `arm_bc(panels)` [T3].**
Replace the pixel-column `guide_marks.apply_marks(sheet, rects)` path with anchored placement:
```
sheet = arm_b(panels); cols,_,cw,ch = _grid_dims(panels)
specs = [(p["view"], (col*cw, row*ch, cw, ch),
         [(f'{p["module"]}:{aid}', x, y) for aid,x,y in kmr.face_anchors(p["ordered"])])
        for idx,p in enumerate(panels) for row,col in [divmod(idx,cols)]]
return guide_marks.apply_anchored(sheet, specs)
```
Id = `f"{module}:{face_id}#{k}"` — module-namespaced (avoids `0:top` collision across modules), VIEW-INDEPENDENT (view NOT in id — this is what makes C2 hold). face_anchors coords are panel-local; apply_anchored draws at (px,py) then composites at (x0,y0). Trailing black watermark cell gets no spec → stays black (C4/watermark test unaffected). `arm_b`/`arm_a`/manifest/facemasks UNCHANGED (all read `p["ordered"]`, which this loop does not alter → C5 consistency free).

**test/test_face_anchors.py (NEW) + test/test_stage_kit_modules.py [T4/T5].** See seams below. Lazy attribute-access import (`def _kmr(): import kit_module_render; return kit_module_render`) per repo pattern.

Note (non-blocking, Loop 4b/6): a pre-read hook enforces `.pyi` currency — regenerate stubs for the 3 edited source files so later reads aren't blocked; `.pyi` staleness does not fail tests.

## Evaluation
criteria-coverage:
  C1 → kit_module_render.face_anchors (fixed UV lattice on projected poly, cell_px-independent) — test_face_anchors.py
  C2 → module-namespaced, view-independent id + one global _stable_symbols (guide_marks) — test_face_anchors.py
  C3 → anchors sampled on projected poly collapse with it edge-on — test_face_anchors.py
  C4 → arm_bc=arm_b+apply_anchored(cyan) → residue>0; arm_b grayscale → residue==0 — test_stage_kit_modules.py (kept)
  C5 → stage() rewrites 3 arms; ordered/manifest/facemasks untouched — test_stage_kit_modules.py (test_stage_writes...)
  C6 → `python3 -m pytest -q` — Loop 5/T5
seams:
  C1 → render one module+view at cell_px 64 AND 96; `face_anchors` on each; MUST-HAVE: anchor-id SET equal across the two sizes (old pixel-lattice's row count scaled with cell height → fails this); AND every (x,y) within its own face's projected bbox (min/max of its poly). SHARPER (optional): face-bbox-normalized positions equal within 1e-6 across sizes (uniform-scale-invariant).
  C2 → for a fixed module, the anchor-id set of each `face_id` is IDENTICAL across all 9 views (id stability); build the symbol map from the FULL sheet id set via ONE `_stable_symbols`/`apply_anchored` call (a PER-VIEW map would re-rank ids and falsely fail C2 — pin this in the test).
  C3 → for wall_band, group a chosen side face's anchors by `face_id` (split id on `#`); over the 8 yaws take max x-spread (frontal) and min x-spread (edge-on); assert min/max < 0.5 for ≥1 side face (a vertical planar quad always goes near-edge-on at some 45° yaw).
  C4 → guide_marks.residue_count on arm_bc>0 and arm_b==0 (existing).
  C5 → stage(tmp) writes 3 arm PNGs + manifest json + 3 restyle prompts; facemask png/json pairs per panel (existing test_stage_writes...).
verdict: PASS

executor: loop-high model=opus tier=high

## Amendment (orchestrator, 2026-07-15) — overrides C5 seam wording above
Staging contract changed at f7b6b02 (Lucas-directed, outside-loop): gen-inbox now holds
ONLY 3 arm sheets + 3 restyle prompts; manifest + facemask/faces pairs land in sibling
masks/ dir (stage(out, out_masks=None) derives Path(out).parent/"masks"). Facemask pixel
encoding = MASK_BASE(40)+MASK_STEP(8)*index, meta color_idx = painted value.
C5 seam = test_stage_kit_modules.test_stage_writes... AS AMENDED at f7b6b02 (already
asserts the new layout) — extend it for arm_bc content only, do not revert layout asserts.
Suite baseline at this branch tip: 82/82 green.
MANDATORY GATE: after 4b regenerates sheets, flow STOPS — orchestrator shows sheets to
Lucas before Loop 5. Fence (never commit): M CONTEXT.md, M ROADMAP-content-gen.md,
M design/RENDER-RESTYLE-MEMO.md, D assets/tiles/.../floor_dungeon_concept_raw.png.
executor: orchestrator model=fable-5 tier=max
