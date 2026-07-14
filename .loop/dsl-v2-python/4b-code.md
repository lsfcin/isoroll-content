# Loop 4b — Code Until Green — dsl-v2-python

## Carry
slug: dsl-v2-python | branch: loop/dsl-v2-python | root: code/isoroll-content
test-cmd: `python3 -m pytest -q` (33 pass on develop @ Loop 1) | e2e-cmd: none
criticality: normal | verdict: standard
criteria:
  C1 parse — all v2 fixtures parse; R/S voxels mismatching group spans → error; voxel double-booking (two chars claiming same voxel via groups vs grids) → error
  C2 round-trip — parse→serialize reproduces fixture verbatim (modulo trailing whitespace) for every fixture
  C3 massing — per-column runs match rig semantics: wallish runs with opening sub-runs (merged contiguous D/W with same side), per-level derived diagonals (diagSolid rule), floor plates with fh, group surfaces via grpBaseData/grpCellVoxels port (stairs stepped 45°=5ft or half=2.5ft only)
  C4 manifest — level→tile elevation, side→WallDef.dir, wallish run length→boundHeight aggregate, group cells→per-cell placements; HUD-count semantics: walls/diags count voxels, openings count RUNS
  C5 guide render — scene_guide_render consumes massing v2; multi-level fixture renders without error; l-room render change (if any) is deliberate and noted
  C6 existing pytest suite stays green
tasks:
  T1 — port group/diag geometry helpers to new layout_groups.py — high
  T2 — parser v2 (levels + attr grids + group lines + rotate) — high
  T3 — v2 validation (R/S vs group span, double-booking, stair incl) — high
  T4 — serializer updateDsl port (round-trip) — high
  T5 — massing v2 (run merge, openings, diagonals, floor fh, groups) — high
  T6 — manifest v2 + scene_assemble._piece_for + HUD counts — high
  T7 — guide render v2 consumes massing v2 — medium
  T8 — fixtures (l-room v2 + multilevel + groups) + golden tests — medium
context: code/CONTEXT.md, code/isoroll-content/CONTEXT.md, code/isoroll-content/SPECS.md, code/isoroll-content/src/pipeline/CONTEXT.md

## Code

**Resume note:** this file did not exist on disk when this executor started, despite a prior
executor session having done substantial implementation work in the working tree (T1-T7 all
appear implemented: `layout_groups.py`, `layout_serialize.py`, `layout_dsl_v2.py` created;
`layout_parse.py`, `layout_massing.py`, `scene_manifest.py`, `scene_guide_render.py` modified;
`CONTEXT.md`/`ROADMAP-content-gen.md` updated). That session apparently died (session limit)
before writing its `4b-code.md` output, per the resume brief received ("last stated next step:
threading z0 through scene_guide_render.py, T7"). Ran `test-cmd` FIRST per instructions to
establish ground truth rather than trusting the stated next-step — result below shows T7 was in
fact already complete in the working tree. Reconstructing an `attempt 1` line for that untracked
prior work, then this session's own verification as `attempt 2`.

attempt 1 (prior session, reconstructed from working-tree state at resume):
  T1-T7 implemented (stub `NotImplementedError`s removed from layout_groups.py/layout_serialize.py;
  layout_parse.py gained Level/Group dataclasses + v2 grammar + validate() union/double-book
  checks; scene_manifest.py gained count_hud + v2 manifest path; scene_guide_render.py `_fit`/
  `_faces` threaded `box.z0` through all three z-coordinate sites for T7) → could not verify red
  count at handoff (no attempt line was written before the session died).

attempt 2 (this session): ran `python3 -m pytest -q` cold, no code changes made first.
  → 50 passed, 0 failed (33 pre-existing + 15 new v2 + 2 previously-vacuous now-real). Zero
  NotImplementedError/TODO/FIXME remain in touched source files (grep clean). Confirmed the C1
  vacuous-pass caveat from 4a-tests.md is resolved for the right reason, not accidentally: manual
  probe of `parse_text()` on the misplaced-marker fixture returns
  `["level 0 (0,0) marker 'R' not covered by any group"]` (semantic union-coverage check) and on
  the hand-built double-booked-cell text returns `['level 1 (0,0) double-booked by 2 groups']`
  (semantic double-book check) — both are v2-grammar-aware errors from `validate()`, not v1
  unknown-cell fallback. Confirmed T7 (z0 threading) via `git diff -- scene_guide_render.py`:
  `_fit` now walks `(b.z0, b.z0 + b.h)` and `_faces` offsets top/long/cap face coordinate
  functions by `z0` — matches the arch seam, and `test_box_has_z0_single_level_wall` +
  `test_multilevel_render_is_non_blank` (C5) both green. C5 l-room note: no v1 golden-image test
  changed (`git diff -- test/fixtures` on tracked fixtures is empty) — z0 defaults to 0.0 for
  single-level v1 boxes, so the T7 change is a verified no-op on existing v1 renders; this *is*
  the "deliberate and noted" disclosure the criterion asks for. No red attempts, no escalation
  needed — nothing left to implement.

green: yes run: `50 passed, 12 warnings in 0.25s`
touched: src/pipeline/layout_groups.py (new), src/pipeline/layout_groups.pyi (new),
  src/pipeline/layout_serialize.py (new), src/pipeline/layout_serialize.pyi (new),
  src/pipeline/layout_dsl_v2.py (new), src/pipeline/layout_dsl_v2.pyi (new),
  src/pipeline/layout_parse.py, src/pipeline/layout_parse.pyi,
  src/pipeline/layout_massing.py, src/pipeline/layout_massing.pyi,
  src/pipeline/scene_manifest.py, src/pipeline/scene_manifest.pyi,
  src/pipeline/scene_guide_render.py, src/pipeline/CONTEXT.md, test/CONTEXT.md,
  ROADMAP-content-gen.md, test/fixtures/golden/dsl_v2_{lroom,multilevel,groups,
  invalid_misplaced_r,invalid_badincl}.txt, test/test_dsl_v2_{parse,serialize,massing,
  manifest,render}.py(+.pyi)

executor: loop-medium model=sonnet tier=medium

## Code (Re-entry, RETURN loop=3 reason=integration-gap → 3-arch.md Amendment → 4a → this loop)

Scope per Amendment (binding ruling: design UNCHANGED, T5/T6 group paths were specified but not
implemented — a seam gap, not a redesign). Implemented the group→Box/manifest/render path until
the 3 new red tests from 4a-tests.md's re-entry section (C3-seam+/C4-seam+/C5-seam+) went green,
without editing any test.

attempt 1: ran `python3 -m pytest -q` cold first to confirm ground truth matched 4a-tests.md's
  claim → 50 passed, 3 failed (the 3 named seam+ tests), matching evidence exactly. Then:
  - `src/pipeline/layout_massing.py` — added `_group_boxes(layout)`: for each `layout.groups`
    entry, calls `grp_base_data`/`grp_cell_voxels` (already-green unit-tested geometry from
    layout_groups.py, untouched) per cell and emits `Box(c, r, 1, 1, vox_hi-vox_lo, "GRP",
    z0=vox_lo)` — position u0=c/v0=r per the arch's `layout.kind(u,v)` convention. Wired into
    `massing()`: appended after the per-level wall/floor/step boxes, independent of `merge` (D0:
    groups have no run-merge concept).
  - `src/pipeline/scene_assemble.py` — `_piece_for` gained a `box.kind == "GRP"` branch → returns
    `"group"` (no kit sprite exists for it yet; `assemble()`'s pre-existing `name not in sprites`
    guard already skips pieces missing from the sprite dict, so this is a safe no-op there).
  - `src/pipeline/scene_manifest.py` — `build_manifest`'s tile loop used `manifest["pieces"][name]`
    (dict subscript), which would `KeyError` for `"group"` since no kit ships a GRP sprite yet.
    Changed to `manifest["pieces"].get(name)` with a neutral `(0,0)`/`(1,1)` origin/size fallback
    so GRP boxes still get a tile entry (z/boundHeight are what the test asserts; imageOffset is
    cosmetic and unused by any kit-backed path since no kit defines "group").
  - `src/pipeline/scene_guide_render.py` — added an empty-massing guard at the top of `_fit`
    (return a neutral scale/origin instead of calling `min()`/`max()` on empty coordinate lists)
    — defense per the Amendment's C5-seam+ note, though with GRP boxes now emitted the groups
    fixture itself is never empty. GRP boxes needed **no** renderer-specific drawing logic:
    `_faces`/`render_boxes` are already generic over `box.kind` (T7's z0-threading from the prior
    session applies uniformly), so GRP boxes render as plain z0..z0+h boxes for free — confirmed
    by re-running the render test after only the massing+manifest changes, before touching this
    file, and it already passed; the guard was added anyway per the Amendment's explicit ask.
  → `python3 -m pytest -q test/test_dsl_v2_massing.py test/test_dsl_v2_manifest.py
  test/test_dsl_v2_render.py` = 22 passed, 0 failed (includes the 3 target tests + all
  pre-existing v2 tests in those 3 files). No red attempts needed — first implementation pass
  went green on all three seams.

Full-suite verification: `python3 -m pytest -q` → 53 passed, 0 failed (50 pre-existing + 3
seam+). Re-ran with `rtk proxy python3 -m pytest -v` to confirm no accidental skips/xfails and
that every one of the 53 names shows PASSED explicitly — 12 pre-existing Pillow
`DeprecationWarning`s only (`Image.getdata`), unrelated to this change, present before this loop.
`grep -rn "NotImplementedError\|TODO\|FIXME"` over the 4 touched source files: clean.

No test file edited this loop (test/test_dsl_v2_{massing,manifest,render}.py untouched — verified
via `git diff --stat` scoped to `test/`).

green: yes run: `53 passed, 12 warnings in 0.26s`
touched: src/pipeline/layout_massing.py, src/pipeline/scene_assemble.py,
  src/pipeline/scene_manifest.py, src/pipeline/scene_guide_render.py (+ auto-generated .pyi
  stubs for the same 4 files, no new public symbols added so stub diffs are additive-only)

executor: loop-medium model=sonnet tier=medium
