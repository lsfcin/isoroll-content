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

## User Test
scenario: As the person wiring the module import seam, I export the l-room scene twice through the real `iso-cli.py export-manifest` entrypoint (default NW, then SW after reviewing the first), confirm the written manifest independently re-validates clean against the wall schema and its geometry round-trips against the layout DSL source, confirm every referenced tile asset actually resolves in the real gray kit on disk — then, because the kit is still being painted by hand and pieces routinely go missing mid-development, I point the exporter at a kit copy with `wall.png` deleted and expect it to refuse gracefully (nonzero exit, readable error) rather than blow up.
script: test/e2e_export_manifest.py (new, `e2e_` prefix — not pytest-collected, mirrors the existing `test/e2e_scenario.py` convention from a prior loop) run: `/mnt/workspace/.venv/bin/python3 test/e2e_export_manifest.py`
observed:
```
[1/6] iso-cli.py export-manifest --view NW -> .../l-room-NW.manifest.json
Saved: .../l-room-NW.manifest.json
[2/6] C1 shape + C2 independent re-validation of the written file
  shape_ok=True reval_errors=[]
[3/6] C3 round-trip: counts re-derived from the layout DSL
  walls=6/6 doors=1/1 windows=1/1 stairs=0
[4/6] C4 asset resolution against the real gray kit   (no missing assets, loop passed silently)
[5/6] second real export, different view (SW), same seam
Saved: .../l-room-SW.manifest.json
  sw_ok=True
[6/6] negative path: kit missing an asset -> real CLI must exit nonzero
  broken_ok=False exit=1
FAIL: exporter did not refuse a manifest with a missing asset
```
Manually captured stderr of the step-6 subprocess for evidence (script only checks exit code + stdout):
```
Traceback (most recent call last):
  File ".../src/cli/iso-cli.py", line 198, in <module>
    main()
  File ".../src/cli/iso-cli.py", line 190, in main
    elif command == "export-manifest": from export_commands import run_export; run_export(args[1:])
  File ".../src/cli/export_commands.py", line 31, in run_export
    manifest = build_manifest(layout, args.kit, args.view)
  File ".../src/pipeline/scene_manifest.py", line 18, in build_manifest
    manifest, _sprites = load_kit(kit_dir)
  File ".../src/pipeline/scene_assemble.py", line 35, in load_kit
    sprites[name] = Image.open(kit / f"{name}.png").convert("RGBA")
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/broken-kit/wall.png'
```
matches-expected-result: no — steps 1-5 (happy path: real CLI export for two views, C1/C2/C3/C4 all hold against the actual written file, not re-derived unit fixtures) fully match Loop 0's `expected-result`. Step 6 does not: `build_manifest` (T1) calls `scene_assemble.load_kit`, which unconditionally opens every `kit.json` piece's PNG via PIL *before* `validate_manifest` (T2) ever runs. `load_kit` was written for pixel assembly (`scene_assemble.assemble`) and was reused as-is for manifest export, which only needs kit.json's `origin`/`size` metadata — it never needed decoded image bytes. Because of this, a missing kit asset (a routine mid-development state — the kit is hand-painted piece by piece) crashes with an uncaught `FileNotFoundError` traceback instead of reaching T2's intended "skip pieces absent from kit.json pieces" / graceful `[FAIL] manifest validation errors:` path. C2's "failure = nonzero exit" is technically true only because Python's default uncaught-exception behavior happens to exit 1 — not because the exporter designed for it. Units are green (T4's C2 test only feeds `validate_manifest` a manually-broken in-memory dict; it never drives `build_manifest` against a kit_dir with a genuinely missing PNG), so this is an integration gap the unit suite structurally cannot see.

FLAG: RETURN loop=3 reason=integration-gap evidence=build_manifest→scene_assemble.load_kit eagerly opens every kit.json piece PNG via PIL before validate_manifest runs, so a missing kit asset raises an uncaught FileNotFoundError instead of T2's designed graceful validation-error exit; architecture should either give manifest export a metadata-only kit reader (no PIL decode needed for tiles[]/walls[] output) or wrap load_kit's call site to route FileNotFoundError into the same [FAIL] reporting path as validate_manifest.

executor: loop-medium model=sonnet tier=medium

## User Test (re-run — after 3-arch.md "Architecture (re-run)" / 4a-tests.md "Tests (re-run)" / 4b-code.md "Code (re-run)" closed the integration gap via `scene_assemble.load_kit_meta`)

scenario: same scenario as the first run, unchanged — export the l-room scene twice through the real `iso-cli.py export-manifest` entrypoint (NW then SW), independently re-validate the written manifest and round-trip its geometry against the layout DSL, confirm every referenced tile asset resolves against the real gray kit, then point the exporter at a kit copy with `wall.png` deleted and expect a graceful refusal instead of a crash.
script: test/e2e_export_manifest.py (unchanged file, run as-is — no edits made to the script for this re-run) run: `/mnt/workspace/.venv/bin/python3 test/e2e_export_manifest.py`
observed:
```
[1/6] iso-cli.py export-manifest --view NW -> /tmp/e2e-export-manifest-xkeskcs0/l-room-NW.manifest.json
Saved: /tmp/e2e-export-manifest-xkeskcs0/l-room-NW.manifest.json
[2/6] C1 shape + C2 independent re-validation of the written file
  shape_ok=True reval_errors=[]
[3/6] C3 round-trip: counts re-derived from the layout DSL
  walls=6/6 doors=1/1 windows=1/1 stairs=0
[4/6] C4 asset resolution against the real gray kit
[5/6] second real export, different view (SW), same seam
Saved: /tmp/e2e-export-manifest-xkeskcs0/l-room-SW.manifest.json
  sw_ok=True
[6/6] negative path: kit missing an asset -> real CLI must exit nonzero
[FAIL] manifest validation errors:
  tiles[6].asset does not resolve in kit_dir: 'wall.png'
  ... (25 tile entries total, all naming 'wall.png', elided here for brevity)
  broken_ok=True exit=1
RESULT shape_ok=True counts_ok=True c4_ok=True sw_ok=True broken_ok=True
PASS
```
Exit code 0. Also ran `make verify-fast` for regression coverage: `19 passed, 0 failed` (12 pre-existing Pillow-deprecation warnings, unrelated to this loop) — no regressions from the `load_kit_meta` split.

matches-expected-result: yes — all 6 steps now hold, including step 6: the CLI exits 1 and prints `[FAIL] manifest validation errors:` naming `wall.png` for every affected tile instead of raising an uncaught `FileNotFoundError` traceback. This confirms T2's designed graceful-validation-error path is actually reached: `build_manifest` now calls `scene_assemble.load_kit_meta` (kit.json metadata only, no PIL decode), so a missing PNG no longer aborts before `validate_manifest` runs — `validate_manifest`'s own asset-resolution check is what now catches the missing `wall.png` and produces the readable `[FAIL]` report. The previously flagged integration gap (`FLAG: RETURN loop=3 reason=integration-gap` above) is closed; C1–C4 all hold against the real CLI entrypoint, not just against unit fixtures.

executor: loop-medium model=sonnet tier=medium
