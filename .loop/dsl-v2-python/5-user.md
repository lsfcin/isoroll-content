# Loop 5 — User Test — dsl-v2-python

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

## User Test

scenario: I'm a scene designer prototyping a small outdoor set in one sitting. I author
two v2 DSL structures — a walled multi-level gatehouse with a door, and a stair-up-to-
flat-roof platform using the new group syntax (`roof:`/`stair:` lines + R/S markers) — and
for each one I: open/parse it, let the editor round-trip-save it, run the real
`export-manifest` CLI to get a kit-assembly manifest, glance at the HUD counts I'd see in
Foundry, and render a guide preview before handing off to painting.

script: /tmp/claude-1000/-mnt-workspace/5559cfa7-90c5-44c2-83a7-549ee8bcf492/scratchpad/loop5_scene_designer_scenario.py (ephemeral, outside repo — not part of touched-files scope)
run: `python3 loop5_scene_designer_scenario.py` (drives fixtures/golden/dsl_v2_multilevel.txt and dsl_v2_groups.txt through parse_text → to_dsl → massing → real `iso-cli.py export-manifest` subprocess → count_hud → render_scene_panel)

observed (dsl_v2_multilevel.txt — walls/door structure): all green — C1 parse clean, C2
round-trip exact, C3 massing 13 boxes all carry z0, C4 CLI exits 0 with 29 tiles/9 walls
all carrying z/dir/boundHeight, HUD `{walls:24,doors:1,windows:0,floors:7,stairs:0,roofs:0}`,
C5 render non-blank.

observed (dsl_v2_groups.txt — roof+stair group structure): C1 parse clean, C2 round-trip
exact. C4 CLI exits 0 but manifest is **empty**: `tiles=0 walls=0` — the R/S group cells the
user authored produce zero placements, even though HUD correctly reports
`{stairs:1, roofs:1}`. C3 `massing(layout)` also returns 0 boxes for this structure. C5
then **crashes**: `render_scene_panel` → `_fit` → `ValueError: min() iterable argument is
empty` (ordered box list is empty, so `_fit` can't compute extents).

Root cause traced (not a script bug): `scene_manifest.build_manifest`'s per-cell stair
shortcut checks `ch in STAIRS`, where `STAIRS = {"^",">","v","<"}` (v1 directional arrow
chars) — it never matches the v2 group markers `{"R","S"}`. `layout_massing.massing()` and
`scene_manifest.py` never import or call `grp_base_data`/`grp_cell_voxels`
(`grep -n "groups\|MARKERS\|grp_" scene_manifest.py layout_massing.py` → only hit is
`count_hud`'s `layout.groups` count). So group geometry is fully wired for parsing,
round-trip, and HUD counting, but never wired into the Box/tile pipeline that actually
produces placeable kit pieces — this is exactly the C4 sub-criterion "group cells →
per-cell placements", confirmed unimplemented. Existing unit suite doesn't catch this
because `test_dsl_v2_manifest.py` only calls `build_manifest` on the multilevel fixture
(no groups) and only asserts generic field presence — no test exercises `build_manifest`
against `dsl_v2_groups.txt` at all.

matches-expected-result: no — C4's "group cells → per-cell placements" and (as a direct
consequence) C5's "renders without error" are not met for any structure that includes
group-authored geometry. Units are green (C6 holds) but the integration path fails on
real group content, per the flow's own definition of an integration gap.

FLAG: RETURN loop=3 reason=integration-gap evidence=build_manifest/massing never call grp_base_data/grp_cell_voxels or match v2 MARKERS {R,S} — group cells produce 0 manifest tiles (dsl_v2_groups.txt: tiles=0, walls=0) and crash scene_guide_render on empty massing (ValueError: min() iterable argument is empty); architecture seam for Group→Box/tile placement was never specified (3-arch.md's seam list stops at grp_base_data/grp_cell_voxels as pure functions consumed only by count_hud)

executor: loop-medium model=sonnet tier=medium

## User Test (Re-run — 4b-code.md re-entry closed the groups→massing/manifest/render gap)

scenario: same as above, unchanged — reused verbatim, script preserved on disk rather than
rewritten (workspace instruction: re-execute the SAME scenario to isolate whether the fix,
not a new test, closed the gap).

script: /tmp/claude-1000/-mnt-workspace/5559cfa7-90c5-44c2-83a7-549ee8bcf492/scratchpad/loop5_scene_designer_scenario.py (unchanged since prior run)
run: `python3 -m pytest -q` first (ground truth) then `python3 loop5_scene_designer_scenario.py`

pytest ground truth: 53 passed, 0 failed (matches 4b-code.md re-entry's reported green).

observed (dsl_v2_multilevel.txt): unchanged from prior run, still all green — C1 clean, C2
exact round-trip, C3 13 boxes all with z0, C4 CLI exits 0 with tiles=29/walls=9 all
carrying z/dir/boundHeight, HUD `{walls:24,doors:1,windows:0,floors:7,stairs:0,roofs:0}`,
C5 non-blank. This structure has no group content, so it was never expected to change —
confirms the fix didn't regress the non-group path.

observed (dsl_v2_groups.txt — the previously-failing path): C1 parse clean, C2 round-trip
exact. C3 `massing(layout)` now returns **6 boxes** (was 0), each carrying z0. C4 CLI
export-manifest now exits 0 with **tiles=6, walls=0** (was tiles=0) — inspected the manifest
JSON directly: 6 `piece:"group"` tile entries, one per authored R/S cell, `u`/`v` matching
grid position and `z` varying per cell (1,1,1,1,0,1 — reflects the stepped-stair/roof
elevation, not a flat fallback), `boundHeight:1` on all. `asset:"group.png"` is a placeholder
name since no kit ships a "group" sprite yet — expected per 4b-code.md's note that
`_piece_for`'s GRP branch has no kit-backed sprite; not a criterion violation since C4 only
requires per-cell placements, not a final asset. HUD unchanged and correct:
`{stairs:1, roofs:1}`. C5 `render_scene_panel` no longer crashes: renders non-blank
(previously `ValueError: min() iterable argument is empty` because massing was empty).

matches-expected-result: yes — the C4 sub-criterion "group cells → per-cell placements" and
C5 "renders without error" now both hold for group-authored geometry, closing exactly the
gap the prior Loop 5 run flagged (`FLAG: RETURN loop=3 reason=integration-gap`). C1/C2/C3/C6
continue to hold as before. No new gap found in this re-run.

verdict: PASS — flow may proceed to Loop 6.

executor: loop-medium model=sonnet tier=medium
