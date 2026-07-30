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

## Ship
diff-scope: clean | extras: .loop/export-manifest/ (kept per keep-trail=yes)
roadmap: updated /mnt/workspace/code/isoroll-content/ROADMAP-content-gen.md (delegation row export-manifest marked ✓ done with outcome)
commit: ce81655 pushed: yes (to origin/feature/export-manifest)
leftovers: none — all Carry criteria satisfied; next step is user review then merge to develop per gitflow protocol

executor: loop-low model=haiku tier=low
