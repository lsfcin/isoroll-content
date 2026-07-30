# Loop 4a — Tests First — dsl-v2-python

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

## Tests
| test file | covers | asserts |
|-----------|--------|---------|
| test/test_dsl_v2_parse.py | C1 | 3 valid fixtures `.errors==[]`; misplaced-R, bad-incl, double-booked-voxel each `.errors!=[]` |
| test/test_dsl_v2_serialize.py | C2 | `to_dsl(parse_text(text))` == fixture text, per-line-rstripped, for all 3 valid fixtures |
| test/test_dsl_v2_massing.py | C3 | `grp_base_data`/`grp_cell_voxels` unit tests (flat roof → 1-level span; shed1 stair → rise-with-position span); `Box.z0==0.0` on a lone level-0 wall |
| test/test_dsl_v2_manifest.py | C4 | `count_hud()` dict on multilevel + groups fixtures; every tile has `z`; every wall has `dir` + `boundHeight>0` |
| test/test_dsl_v2_render.py | C5 | `render_scene_panel(...).getextrema()` non-uniform (not all-black) on multilevel fixture |

New fixtures (test/fixtures/golden/): `dsl_v2_lroom.txt` (single level), `dsl_v2_multilevel.txt` (2
levels, 1 door run), `dsl_v2_groups.txt` (1 flat roof r0..r3 z=1 + 1 shed1 stair (1,0)-(1,1) z=0
incl=5, R/S levels hand-derived from rig.frag grpBaseData/grpCellVoxels — see massing test
docstrings for the derivation), `dsl_v2_invalid_misplaced_r.txt`, `dsl_v2_invalid_badincl.txt`.

New/modified source (stub-only, no logic — Loop 4b implements): `layout_groups.py` (NEW —
vocab consts real, `diag_solid`/`grp_base_data`/`grp_cell_voxels` raise `NotImplementedError`),
`layout_serialize.py` (NEW — `to_dsl` raises `NotImplementedError`), `layout_parse.py` (additive
`Level`/`Group` dataclasses, no change to existing `Layout`/`parse_text`/`validate`/`rotate_cw`),
`scene_manifest.py` (additive `count_hud` stub, raises `NotImplementedError`).

red-run: 15 failed as expected | wrong-failures: none (all `AssertionError`/`NotImplementedError`,
zero `ImportError`/`SyntaxError` — verified via `rtk proxy python3 -m pytest -v`)

Caveat: `test_misplaced_marker_is_an_error` and `test_double_booked_voxel_is_an_error` currently
pass **vacuously** — the v1 parser doesn't understand `level N:`/`roof:` syntax yet, so it flags
those lines as unknown-cell errors regardless of the intended semantic (union/double-booking)
check. Not a wrong-failure (still red for a real reason — v2 grammar absent), but Loop 4b should
re-verify these two go green **for the right reason** once T2/T3 land, not just stay accidentally
red-turned-green.

C6 gate: full suite = 35 passed (33 pre-existing + 2 vacuous-pass above), 15 failed (all new v2
tests) — pre-existing suite unaffected by the additive stubs. `python3 -m pytest -q` from repo
root.

executor: loop-medium model=sonnet tier=medium

## Tests (Amendment re-entry, RETURN loop=3 reason=integration-gap → 4a)

Scope per Amendment: ONLY missing red tests at C3-seam+/C4-seam+/C5-seam+ (groups fixture through
massing→manifest→render). No existing test edited — 3 fns appended to the seam files above.

| test file::fn | covers | asserts |
|-----------|--------|---------|
| test_dsl_v2_massing.py::test_groups_fixture_emits_one_grp_box_per_group_cell_matching_voxel_span | C3-seam+ | `massing()` on `dsl_v2_groups.txt` emits one `Box(kind="GRP")` per group cell (v0=r,u0=c); `(z0,z0+h)`==`grp_cell_voxels` span (6 cells: roof→(1,2)×4, stair (1,0)→(0,1),(1,1)→(1,2)) |
| test_dsl_v2_manifest.py::test_manifest_group_cell_placements_groups_fixture | C4-seam+ | `build_manifest(groups,view="SW")["tiles"]` non-empty; per-cell tile `z==voxLo`, `z+boundHeight==voxHi` |
| test_dsl_v2_render.py::test_groups_only_scene_renders_without_crashing | C5-seam+ | `render_scene_panel(groups,"SW",256)` returns w/o raising; `.getextrema()` non-uniform |

`view="SW"` (identity rotation) used deliberately for C4/C5: `rotate_cw` doesn't re-orient
`Group.cells` (documented limitation in `layout_parse.rotate_cw`) — any other view desyncs tile
(u,v) from groups' un-rotated (c,r); that's a separate out-of-scope gap.

red-run: 3 failed as expected | wrong-failures: none. Verified `python3 -m pytest -v
test/test_dsl_v2_{massing,manifest,render}.py`:
- C3-seam+: `AssertionError: expected 6 GRP boxes ... got 0` (massing() never touches
  `layout.groups` — matches Loop 5 evidence)
- C4-seam+: `AssertionError: expected at least one tile` (cascades from C3 — `_piece_for` never
  sees a GRP box)
- C5-seam+: `ValueError: min() iterable argument is empty` at `_fit`←`render_boxes`←`Cam.__init__`
  (matches Loop 5 evidence verbatim: "min() empty")

All three: `AssertionError`/`ValueError` for missing-behavior — zero `ImportError`/`SyntaxError`.

C6 gate: 53 tests, 50 passed (pre-existing unaffected), 3 failed (new tests only). 12
pre-existing Pillow `DeprecationWarning`s, unrelated.

No source touched this loop — tests only. Loop 4b implements GRP-box emission (T5), manifest
tile wiring (T6), empty-massing guard (T7) until green.

executor: loop-medium model=sonnet tier=medium
