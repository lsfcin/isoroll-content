## Carry
slug: export-manifest | branch: feature/export-manifest | root: /mnt/workspace/code/isoroll-content
test-cmd: `make verify-fast` (includes pytest) | e2e-cmd: CLI export run on the l-room layout (Loop 5 scripts it)
criticality: normal | verdict: standard
criteria:
  C1 — a CLI verb (in `src/cli/`, wired via `iso-cli.py` dispatch like `multiview_commands.py` verbs) exports a scene manifest JSON from a layout file + kit alignment manifest: scene tiles (kit piece id, facing, grid position, `boundHeight`, `imageOffset`, px-per-voxel scale) + `WallDef[]` derived from the layout's wall runs and openings
  C2 — manifest `WallDef[]` fields structurally validate against `/mnt/workspace/code/isoroll-module/src/walls/wall-types.d.ts` (tileAnchor in [0,1]², door/sense/dir enums) — validation is code in this repo (schema mirror or parser), failure = nonzero exit
  C3 — round-trip: wall-run / door / window / stair counts derived back from the manifest equal counts parsed from the layout DSL for the l-room fixture
  C4 — asset references follow `{name}_{facing}.png` naming (SPECS.md) and resolve against the gray kit output on disk
tasks:
  T1 — `build_manifest(layout, kit_dir, view="NW") -> dict{scene,view,pxPerVoxel,tiles[],walls[]}`. tiles = PER-CELL (`massing(layout_rotated, merge=False)`, piece via `scene_assemble._piece_for`, plus stair cells → piece `stair`); each tile fields: `piece`, `asset`=`f"{piece}.png"`, `facing`=view, `u`,`v` (rotated-grid cell), `boundHeight`=box.h, `imageOffset`=[ox/w, oy/h] from kit.json origin/size, `pxPerVoxel`=kit `px_per_unit`. walls = WallDef[], ONE per MERGED run (`massing(merge=True)`, kind=="wall"): ax=u0/cols, ay=v0/rows, bx=(u0+l)/cols, by=(v0+d)/rows, topOffset=box.h, bottomOffset=0, config={move:1,sense:1,sound:1,light:1,door:0,dir:0}. — src/pipeline/scene_manifest.py — medium
  T2 — `validate_manifest(m) -> list[str]` mirroring wall-types.d.ts: each walls[] entry ax/ay/bx/by ∈ [0,1]; topOffset/bottomOffset numeric; config keys ⊆ {move,sense,sound,light,door,dir} and int in [0,2]; each tile `asset` resolves in kit_dir (skip pieces absent from kit.json `pieces`, e.g. `stair`). — src/cli/wall_schema.py — medium
  T3 — `run_export(argv)`: argparse `--layout` (req), `--kit` (dir with kit.json, default `output/kit-guide`), `--view` (default NW, choices SW/SE/NE/NW), `--out` (default `output/manifests/{layout.name}.manifest.json`); build → validate → mkdir+write JSON; if validate returns errors print them + `sys.exit(1)`. Wire `elif command == "export-manifest": from export_commands import run_export; run_export(args[1:])` in iso-cli.py. — src/cli/export_commands.py, src/cli/iso-cli.py — medium
  T4 — `test/test_export_manifest.py` (pytest, conftest already puts src/cli+src/pipeline on path): C1 every tile has piece/facing/u/v/boundHeight/imageOffset/pxPerVoxel; C2 validate() passes clean manifest and returns ≥1 error when a WallDef ax set to -0.1 or 1.1; C3 on l-room fixture — `len(walls)` == count of `massing(load(l-room),merge=True)` wall boxes, door-tile count == DOOR cells, window-tile count == WINDOW cells, stair-tile count == STAIR cells; C4 every tile.asset (present-in-kit) exists under output/kit-guide. — test/test_export_manifest.py — medium
  T5 — mark export-manifest row done + add pointer to `.loop/export-manifest/` plan in ROADMAP-content-gen.md (Loop 6, on feature branch). — ROADMAP-content-gen.md — low
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/SCENE-CREATION.md (contract §), /mnt/workspace/code/isoroll-content/src/pipeline/CONTEXT.md, /mnt/workspace/code/isoroll-content/src/cli/CONTEXT.md

## Tests
| test file | covers | asserts |
|-----------|--------|---------|
| test/test_export_manifest.py::test_tiles_have_all_fields | C1 | every tile dict has piece/asset/facing/u/v/boundHeight/imageOffset/pxPerVoxel |
| test/test_export_manifest.py::test_walls_are_walldefs | C1 | every wall dict has ax/ay/bx/by/topOffset/bottomOffset/config |
| test/test_export_manifest.py::test_run_export_cli_verb | C1 | `export_commands.run_export(argv)` writes a manifest JSON to `--out` with scene/view/tiles/walls populated (verb reachable, T3 wiring) |
| test/test_export_manifest.py::test_validate_clean_manifest_passes | C2 | `validate_manifest(manifest) == []` on a structurally clean manifest |
| test/test_export_manifest.py::test_validate_catches_out_of_range_ax | C2 | mutating `walls[0]["ax"]` to -0.1 or 1.1 each yield `len(errs) >= 1` |
| test/test_export_manifest.py::test_wall_count_matches_dsl | C3 | `len(manifest["walls"])` == count of `kind=="wall"` boxes from `massing(load(l-room), merge=True)` (pinned at 6, recomputed via massing not just hardcoded) |
| test/test_export_manifest.py::test_door_window_stair_tile_counts | C3 | door-piece tile count == 1, window-piece tile count == 1, stair-piece tile count == 0, matching l-room's DOOR/WINDOW/STAIR cell counts |
| test/test_export_manifest.py::test_tile_assets_resolve_in_kit | C4 | every tile whose piece ∈ kit.json `pieces` has `(kit_dir/tile["asset"]).exists()` |
| test/test_export_manifest.py::test_validate_manifest_flags_missing_asset | C4 | `validate_manifest(m, kit_dir=...)` returns ≥1 error when a kit-present tile's asset is swapped to a nonexistent filename |

red-run: 1 collection error (all 9 tests blocked) as expected | wrong-failures: none

Ran `python3 -m pytest test/test_export_manifest.py -v` from repo root. Result: `ModuleNotFoundError: No module named 'scene_manifest'` at the test file's top-level import (`from scene_manifest import build_manifest`, line 17) — pytest reports "collected 0 items / 1 error" (a collection error, not per-test failures, since the missing import blocks the whole module). This is the correct red state: `conftest.py`'s `sys.path` bootstrap works fine (the preceding `from layout_parse import load` / `from layout_massing import massing` imports at lines 15-16 resolved without error — failure is specifically at the not-yet-created `scene_manifest` module), and the failure traces to missing implementation (T1/T2/T3 modules `src/pipeline/scene_manifest.py`, `src/cli/wall_schema.py`, `src/cli/export_commands.py` don't exist yet), not to a syntax/naming error in the test file itself. Verified the l-room fixture facts the tests hard-code independently before writing them: `massing(load('src/pipeline/layouts/l-room.txt'), merge=True)` gives exactly 6 `kind=="wall"` boxes, 1 DOOR cell, 1 WINDOW cell, 0 STAIR cells — matches the arch doc's seam note (C3).

Seam coverage check against 3-arch.md `## Evaluation`: C1 (tile/wall field-shape + verb reachability) → `test_tiles_have_all_fields`, `test_walls_are_walldefs`, `test_run_export_cli_verb`. C2 (structural validation mirroring wall-types.d.ts) → `test_validate_clean_manifest_passes`, `test_validate_catches_out_of_range_ax`. C3 (round-trip counts) → `test_wall_count_matches_dsl`, `test_door_window_stair_tile_counts`. C4 (asset resolution) → `test_tile_assets_resolve_in_kit`, `test_validate_manifest_flags_missing_asset`. All 4 criteria have ≥1 test at the seam the architecture named; no criterion is untestable as designed.

executor: loop-medium model=sonnet tier=medium

## Tests (re-run — new seam only, from 3-arch.md "Architecture (re-run)")

Scope: this re-run adds tests **only** for the new seam the architecture re-run
introduced to close the RETURN loop=3 reason=integration-gap flagged in
`5-user.md` — `build_manifest` must work against a metadata-only kit dir (no
PNGs), via a new `scene_assemble.load_kit_meta(kit_dir)`. The CLI-level
graceful-fail path (nonzero exit, no traceback, real subprocess) is already
authored in `test/e2e_export_manifest.py` step 6 — not touched. Existing
`test/test_export_manifest.py` (9 tests, all green) is untouched — new tests
live in a new file so the untouched-existing-tests constraint is structural,
not just intentional.

| test file | covers | asserts |
|-----------|--------|---------|
| test/test_scene_manifest_kit_meta.py::test_load_kit_meta_reads_json_without_pngs | new seam | `scene_assemble.load_kit_meta(kit_dir)` on a dir containing only `kit.json` returns the parsed dict (`pieces`, `px_per_unit`) — no PIL, no PNG existence required |
| test/test_scene_manifest_kit_meta.py::test_build_manifest_succeeds_against_metadata_only_kit | new seam (closes integration-gap) | `build_manifest(layout, kit_dir, view="NW")` against a kit dir with only `kit.json` (no PNGs) returns non-empty `tiles`/`walls` and correct `pxPerVoxel` — proves manifest building no longer eagerly opens piece PNGs |

red-run: 2 failed as expected (of 2 new; 17 pre-existing pass unchanged) | wrong-failures: none

Ran `python3 -m pytest test/ -v` from repo root. Result: 17 passed (all pre-existing
tests, including all 9 in `test/test_export_manifest.py`, untouched and still
green — no regression from adding this file), 2 failed (both new).
`test_load_kit_meta_reads_json_without_pngs` fails with
`ImportError: cannot import name 'load_kit_meta' from 'scene_assemble'` at the
test's own `from scene_assemble import load_kit_meta` line — correct red
state, `load_kit_meta` is exactly the function the architecture re-run
designs but hasn't been implemented yet.
`test_build_manifest_succeeds_against_metadata_only_kit` fails inside
`build_manifest` → `load_kit` → `Image.open(kit / "floor.png")` with
`FileNotFoundError: ... kit-meta-only/floor.png` — correct red state,
`build_manifest` still calls the PIL-eager `load_kit` (not yet switched to
`load_kit_meta` per the architecture), so it cannot yet tolerate a
metadata-only kit dir; this is precisely the gap `5-user.md` flagged
(`build_manifest`→`scene_assemble.load_kit` eagerly opens every kit.json
piece PNG before `validate_manifest` ever runs).

Seam coverage check against 3-arch.md `## Evaluation (re-run)`: "unit — build_manifest
with metadata-only kit dir" → both new tests in `test/test_scene_manifest_kit_meta.py`.
"e2e step 6 — CLI graceful fail" → already authored in `test/e2e_export_manifest.py`
(step 6, `broken_ok` check), unchanged this loop — 4b will need to make that step's
`"wall.png" in result_broken.stdout` assertion pass too once `load_kit_meta` + the
`[FAIL]` reporting path land, but no new e2e test file was needed for it.

executor: loop-medium model=sonnet tier=medium
