# Loop 0 — Clarify: anchored-kit-marks

## Carry
slug: anchored-kit-marks | branch: loop/anchored-kit-marks | root: /mnt/workspace/code/isoroll-content
test-cmd: `python3 -m pytest -q` (verify in Loop 2) | e2e-cmd: none (Loop 5 scripts the real staging entrypoint)
criticality: normal | verdict: standard
criteria:
  C1 anchors-projected: cyan symbol anchor points are a UV-lattice per module face (face-plane coords), projected through the SAME transform as the geometry (`_yaw` + `Cam.pt` in kit_module_render.py) — placement is a function of geometry+view, never of cell pixel size.
  C2 cross-view-stability: same physical anchor (stable face_id + lattice index) renders the SAME symbol glyph in all 9 views (8 yaws + TOP).
  C3 edge-on-collapse: in an edge-on yaw view, projected anchors of the edge-on faces collapse toward the silhouette line (testable: anchor x-spread across the face << spread in the frontal view of the same face).
  C4 residue-invariant: residue(arm_bc) > 0 AND residue(arm_b) == 0 stay green (existing test contract).
  C5 restage: arm sheets regenerated + restaged into output/gen-inbox/ via the real staging entrypoint; facemasks and manifest remain consistent.
  C6 suite-green: full pytest suite green (was 82 passing at branch tip).
tasks: TBD (Loop 1)
context: CONTEXT.md, src/CONTEXT.md, design/RENDER-RESTYLE-MEMO.md, core/skills/iso-visual.md (visual work rule)

## Clarify
intent: Replace the screen-space symbol grid on arm-bc kit sheets with geometry-anchored cyan registration marks (UV-lattice per face, projected per view, stable symbol identity across views).
motivation: User rejected current staged sheets — symbols must read as attached to voxel/module geometry ("same symbol = same physical spot"); NB web runs are BLOCKED until sheets are regenerated correctly.
refs: user example /mnt/workspace/Downloads/"Isometric Images (7).png" (correct behavior: lattice tracks face, skews oblique, collapses edge-on, glyph size screen-space); src/pipeline/scene_anchors.py (parked correct pattern — borrow `_stable_symbols` idea, NOT its layout-scoped call surface); src/pipeline/guide_marks.py `_symbol_layer` lines 65-75 (current wrong grid); src/pipeline/stage_kit_modules.py arm_bc lines 56-62 (wrong wiring) + arm_a lines 71-77 (per-face loop to mirror); src/pipeline/kit_module_render.py ordered_faces lines 45-70 (`_yaw` + `Cam.pt`, stable face_id); prompts/restyle_arm_bc.md lines 11-12 (contract); design/RENDER-RESTYLE-MEMO.md.
scope-files: src/pipeline/kit_module_render.py (new face-anchor projector), src/pipeline/stage_kit_modules.py (arm_bc rewrite), test/test_stage_kit_modules.py (+ new placement tests, possibly new test file), output/gen-inbox/ (regenerated artifacts, gitignored).
expected-result: Regenerated arm_bc.png in output/gen-inbox/ where every cyan symbol sits on a projected face anchor: identical lattice tracks each face across all 9 views, skews with obliquity, collapses to the silhouette in edge-on views; arm_b stays symbol-free; suite green.
ambition: solid
criticality: normal tolerance: symbol density/aesthetics may be tuned later; placement semantics (C1-C3) must hold exactly.
innovation: none — pattern exists parked in scene_anchors.py; this is a placement swap.
verdict: standard (3+ files, new helper function = new internal API → fails bakery gate)
keep-trail: yes (match kit-module-renderer precedent)

## Orchestrator notes (fence + base)
- BASE BRANCH: create loop/anchored-kit-marks from loop/kit-module-renderer tip 4759923 (doc-branch lineage — develop lacks design/ tree; field-note rule).
- DIRTY-TREE FENCE: pre-existing `M CONTEXT.md` in the working tree is NOT part of this loop. Never commit, revert, or modify it. Loop 6 lists it under `extras: pre-existing-dirty`.
- gen-inbox artifacts are gitignored; "restage" means files on disk, not commits.
- Symbol glyph size stays screen-space (labels don't scale with distance/foreshortening; only anchor positions transform).

executor: orchestrator (inline Loop 0, context hot) model=fable-5 tier=max
