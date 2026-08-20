# Loop 1 — Plan — dsl-v2-python

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

## Plan
branch: loop/dsl-v2-python  base: develop

Normative reference (PORT, do not reinvent): `design/feel-rig/rig.frag`. Line refs are to that file.
Vocab consts (rig L184–199): WALLISH={#,D,W}, DIAG={/,\}, ARROW_CW, SIDE_NAME={^:N,>:E,v:S,<:W},
ROOF_FORMS=[flat,shed1,shed2], STAIR_TYPES=[solid,thin], ENCLOSE=[none,edge,inset],
TYPES={#:[stone,wood], .:[stone,grass,road], D:[wood,iron], W:[bars,glass]}, NLVL=10.
Hook gates (repo): every .py ≤200 LOC + 1 responsibility (stubgen `.pyi` required, jscpd no-clone) —
so v2 lands as SPLIT modules, never by fattening existing files.

| id | task | files | done-when | tier | effort |
|----|------|-------|-----------|------|--------|
| T1 | New pure-geometry module: `diag_solid` (rig L365–372: N/S/W/E wallish neighbor mask → NE/NW/SE/SW/None), `grp_base_data` (L423–435: aOf/aLow/aHigh/rise=incl/5/hAt per form), `grp_cell_voxels` (L437–443: 4-corner h → [voxLo,voxHi)), shared vocab consts | new `src/pipeline/layout_groups.py` (+`.pyi`) | unit test: grp_cell_voxels of a shed1 roof matches hand-computed span; diag_solid returns correct corner or None for a hand-built mask | high | med |
| T2 | Parser v2: consume `level N:` blocks (voxel grid + `layer side:/type:/wmat:/fh:` attr grids, 1 char/cell) and `roof:`/`stair:` group lines (form/dir/incl/z/enclose). New model `Layout{name, levels:[{g,side,type,wmat,fh}], groups:[...], rows, cols}`. Bare grid w/ no `level` header → single level 0 (v1 back-compat, so old l-room.txt still parses). Port rotate to v2: rotate every level grid (rig L264 rotateGridCW), remap group cells, rotate arrows+diags (chRot L263) | `src/pipeline/layout_parse.py`, `.pyi` | l-room v2 + 2 goldens parse errors==[]; bare-grid l-room.txt still parses to 1 level; rotate_cw of a 2-level fixture keeps level count and remaps a group cell | high | high |
| T3 | Validation in parser: (a) R/S voxels authored in level grids must equal the union of `grp_cell_voxels` over each group's cells — mismatch → error; (b) double-booking: any voxel claimed by two chars (group vs wall/floor, or two groups) → error; (c) stair `incl` must be 5 (45°) or 2.5 (half) else error | `src/pipeline/layout_parse.py` | fixture with a misplaced R rejected w/ clear msg; fixture with stair incl=3 rejected; valid fixtures pass | high | med |
| T4 | Serializer: `updateDsl` port (rig L1088–1119) — Layout→canonical text: `name:`, per level emit grid with R/S overlaid from group span map (gvox L1090–1093), then `layer side/type/wmat/fh:` lines only when a grid has any non-`.` (L1101–1111), then `roof:`/`stair:` lines w/ form=/dir=/incl=Nft/z=/enclose= | `src/pipeline/layout_serialize.py` (new, keeps layout_parse ≤200 LOC) + `.pyi`; re-export from layout_parse if callers expect it | parse→serialize == input verbatim (modulo trailing ws) for all 3 fixtures | high | med |
| T5 | Massing v2: per-COLUMN contiguous-voxel run merge → wall runs (rig L483–501) with merged opening sub-runs by equal side (L610–618); per-level derived diagonals via diag_solid; floor plates w/ fh thickness (fh*0.2 voxel, L488); group surfaces via grp_cell_voxels — stairs stepped 5 treads riser=incl/25 solid|thin (L535–552), roofs sloped patch. Keep merge flag: merge=False → 1-voxel boxes (render lane) | `src/pipeline/layout_massing.py`, `.pyi` (use layout_groups; split helpers if >200 LOC) | massing(l-room v2) == golden box list; multilevel fixture yields per-voxel wall runs; groups fixture yields stepped stair + roof boxes | high | high |
| T6 | Manifest v2 + `_piece_for`: level index→tile z/elevation, `side`→WallDef `dir`, wallish run length→`boundHeight` aggregate, group cells→per-cell placements; counts (rig updateHud L1073–1084): walls+diags count VOXELS, openings count RUNS (a D/W voxel whose below-neighbor is same char is not a new run). Update `_piece_for` for new box kinds (diag, group) | `src/pipeline/scene_manifest.py`, `scene_assemble.py`, `.pyi`s | manifest for multilevel fixture has per-level tile z + wall dir from side; count fields match updateHud rule on the groups fixture | high | med |
| T7 | Guide render v2: `scene_guide_render` consumes massing v2 (multi-level boxes, diagonals, group surfaces) without new geometry math; render the 3 fixtures. Note any l-room panel delta in a code comment | `src/pipeline/scene_guide_render.py`, `.pyi` | render_scene_panel on all 3 fixtures returns a non-blank RGB image, no exception; l-room delta (if any) noted | medium | med |
| T8 | Fixtures + golden tests. Author 3 DSL v2 fixtures BY HAND to the updateDsl format (see Review R1), canonicalize each once via the T4 serializer, freeze: `layouts/l-room.txt` (v2 migrate, keep single-level), `test/fixtures/golden/multilevel.txt` (≥2 levels), `.../groups.txt` (1 roof + 1 stair w/ derived R/S). Golden tests: parse-errors (C1 incl 2 invalid fixtures), round-trip (C2), massing box list (C3), manifest fields+counts (C4), guide-render smoke (C5). Migrate the ≤3 existing tests that assert v1 massing shape (test_export_manifest, test_scene_manifest_kit_meta, e2e_*) to v2 | `test/fixtures/golden/*.txt`, `src/pipeline/layouts/l-room.txt`, `test/test_dsl_v2_*.py`, migrate existing v1-shape tests | `python3 -m pytest -q` green incl new goldens (C6) | medium | high |

## Plan Review (adversarial, assume small executors)
- R1 FATAL: clarify says fixtures "exported verbatim from the rig DSL panel" — the rig is an HTML/JS prototype no loop executor can run. → FIXED: T8 redefines fixtures as hand-authored to the documented updateDsl format (grammar spelled out in Plan header + T4), then canonicalized once through the ported serializer and frozen. Round-trip (C2) stays a real regression guard; provenance recorded in a fixture comment. No human/browser step required.
- R2 FATAL: C6 "existing suite green" breaks if the Layout model is replaced (5 importers + 33 tests assume v1 single-grid + uniform wall_h). → FIXED: T2 back-compat path parses a bare grid as level 0, so l-room.txt and rotate keep working; but v2 massing is per-voxel not uniform-wall_h, so the ≤3 tests that assert v1 box shape are explicitly migrated in T8 (named). Loop 3 must ratify replace-vs-extend for `Layout`; both T2 and T5 are high tier so the model has headroom.
- R3 FATAL: 200-LOC hook gate would fail the commit if parser+serializer+massing grow monolithic. → FIXED: geometry split to new `layout_groups.py` (T1), serializer to new `layout_serialize.py` (T4); each row names its file and the ≤200-LOC + `.pyi` + jscpd rule is stated in the Plan header.
- R4: rotate_cw for v2 must rotate ALL level grids, remap group cells, and rotate arrows AND diagonals (chRot) — v1 only turns one grid + arrows. Silent drop of a level/group under rotation would corrupt every non-SW view. → FIXED: T2 done-when asserts rotate preserves level count and remaps a group cell; explicit rig L263/L264 refs.
- R5: `scene_manifest` imports `_piece_for` from `scene_assemble`; new box kinds (diag, group/GRP) would fall through and drop tiles silently. → FIXED: scene_assemble is in T6 scope with an explicit `_piece_for` update; done-when checks group cells produce placements.
- R6: opening-run count semantics are non-obvious (a D voxel stacked above another D is the SAME run) — a naive per-voxel count fails C4. → FIXED: T6 states the below-neighbor rule with rig L1079–1080 ref; groups fixture in T8 exercises a ≥2-voxel door.
verdict: PASS

executor: loop-high model=opus tier=high

## Plan Correction (orchestrator, append-only)
branch base OVERRIDDEN: base=develop → base=loop/isoroll-help-export (current tip 6d73670).
Reason: develop contains NO design/ tree (verified `git ls-tree develop design/` = empty) — the normative
reference (design/feel-rig/rig.frag), PAINTER-UX rounds 12–19, and the frozen SCENE-CREATION spec exist
only on this lineage. Nothing is merged to develop (gitflow: Lucas eyeballs). Loop 2: create
loop/dsl-v2-python from loop/isoroll-help-export.
executor: orchestrator model=claude-fable-5 tier=max
