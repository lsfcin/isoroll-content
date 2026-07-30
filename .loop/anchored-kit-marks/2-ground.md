# Loop 2 — Ground: anchored-kit-marks

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

## Ground
branch-created: loop/anchored-kit-marks base: 4759923
paths: 6/6 ok | missing: none
test-cmd-runs: yes (82 passed)

executor: loop-low model=haiku tier=low

## Plan Correction (orchestrator, 2026-07-15) — overrides where it conflicts
Landed outside this loop, commit f7b6b02 (Lucas-directed, step-by-step mode):
- `stage()` signature/layout changed: masks + faces.json + sheet_manifest.json now go to
  sibling `masks/` dir (`out_masks` param, default derives `Path(out).parent/"masks"`);
  gen-inbox holds ONLY 3 arm sheets + 3 restyle prompts.
- `face_masks.py`: mask pixel = MASK_BASE(40) + MASK_STEP(8) * paint index; meta
  `color_idx` stores the painted VALUE. uint8 guard asserts ≤26 faces/panel.
- Staging test amended to this contract; suite 82/82 green at f7b6b02.
Impact on this loop: arm_bc task rows unchanged; any restage step regenerates into the
NEW layout; do not "fix back" the moved manifest/masks. Pre-existing dirty fence now:
M CONTEXT.md, M ROADMAP-content-gen.md, M design/RENDER-RESTYLE-MEMO.md,
D assets/tiles/dungeon_floor/concept/floor_dungeon_concept_raw.png — never commit these.
NEW GATE (Lucas, mandatory): after regenerating arm sheets, STOP before any further step —
the orchestrator shows the sheets to Lucas (visual board) and waits for his OK.
executor: orchestrator model=fable-5 tier=max
