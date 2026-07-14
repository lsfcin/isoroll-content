# Loop 0 — Clarify — dsl-v2-python

## Carry
slug: dsl-v2-python | branch: loop/dsl-v2-python (TBD confirm Loop 1) | root: code/isoroll-content
test-cmd: `python3 -m pytest -q` (verify in Loop 2) | e2e-cmd: none
criticality: normal | verdict: standard
criteria:
  C1 parse — all v2 fixtures parse; R/S voxels mismatching group spans → error; voxel double-booking (two chars claiming same voxel via groups vs grids) → error
  C2 round-trip — parse→serialize reproduces fixture verbatim (modulo trailing whitespace) for every fixture
  C3 massing — per-column runs match rig semantics: wallish runs with opening sub-runs (merged contiguous D/W with same side), per-level derived diagonals (diagSolid rule), floor plates with fh, group surfaces via grpBaseData/grpCellVoxels port (stairs stepped 45°=5ft or half=2.5ft only)
  C4 manifest — level→tile elevation, side→WallDef.dir, wallish run length→boundHeight aggregate, group cells→per-cell placements; HUD-count semantics: walls/diags count voxels, openings count RUNS
  C5 guide render — scene_guide_render consumes massing v2; multi-level fixture renders without error; l-room render change (if any) is deliberate and noted
  C6 existing pytest suite stays green
tasks: TBD (Loop 1)
context: code/CONTEXT.md, code/isoroll-content/CONTEXT.md, code/isoroll-content/SPECS.md, code/isoroll-content/src/pipeline/CONTEXT.md

## Clarify
intent: Implement DSL v2 (frozen 2026-07-13 @ feel-rig v16.2) in the Python pipeline: parser, massing, manifest/assembler mapping, guide-render consumption.
motivation: Grammar froze after 19 design rounds; the module TS twin (loop D2) and P7 painter both depend on this parser landing first. Post-freeze plan approved by Lucas 2026-07-13.
refs: SCENE-CREATION.md § "The contract" (DSL v2 spec para), design/PAINTER-UX.md rounds 12–19 (decisions), design/feel-rig/rig.frag = NORMATIVE reference implementation — PORT its logic, do not reinvent: `updateDsl` (serialization), `grpBaseData`/`grpCellVoxels` (group span math), render collection loop (per-column run merging), `diagSolid` (derived diagonals), opening sub-run merging (drawOneCell subs). Groups: `roof:`/`stair:` lines are authoritative; R/S grid voxels are DERIVED (validate, never author).
scope-files: src/pipeline/layout_parse.py, layout_massing.py, scene_manifest.py, scene_assemble.py, scene_guide_render.py, layouts/ (l-room v2 migration + 2 new golden fixtures exported verbatim from the rig DSL panel: one multi-level, one with roof+stair groups), test/ (new golden tests)
expected-result: `python3 -m pytest -q` green including new golden tests; v2 fixtures parse→massing→manifest producing outputs that match rig-derived goldens; invalid inputs (R/S mismatch, double-booked voxel) rejected with clear errors.
ambition: solid
criticality: normal tolerance: guide-render pixel changes acceptable if noted; NO tolerance for silent acceptance of invalid DSL
innovation: none (port of frozen reference)
verdict: standard
keep-trail: yes

executor: orchestrator(fable, Loop 0 interactive — fields filled from Lucas-approved post-freeze plan, same session) model=claude-fable-5 tier=max
