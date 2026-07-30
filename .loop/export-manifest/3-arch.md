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

## Architecture

### src/pipeline/scene_manifest.py — build the manifest dict (T1)
Imports (all in pipeline): `massing` (layout_massing), `STAIR_RISE` (layout_massing),
`rotate_cw`, `load`, `STAIRS` (layout_parse), `VIEW_TURNS` (scene_guide_render),
`_piece_for`, `load_kit` (scene_assemble). Reuse `scene_assemble.load_kit(kit_dir)` for
`manifest["px_per_unit"]` and `manifest["pieces"]` (each `{origin:[ox,oy], size:[w,h]}`) —
do NOT re-open kit.json by hand.
- `build_manifest(layout, kit_dir, view="NW") -> dict`:
  `turned = rotate_cw(layout, VIEW_TURNS[view])`; `cols,rows = turned.cols,turned.rows`.
  tiles: iterate `massing(turned, merge=False)`; `name=_piece_for(box)`; skip when `name is None`
  (this drops the 4 kind=="step" sub-boxes stairs emit). For kept boxes emit tile with
  `piece=name`, `asset=f"{name}.png"`, `facing=view`, `u=box.u0`, `v=box.v0`,
  `boundHeight=box.h`, `pxPerVoxel=px_per_unit`, and `imageOffset` computed from
  `pieces[name]`: `[ox/w, oy/h]` (name IS in kit.json for every _piece_for output).
  THEN a second pass over `turned` grid cells where `turned.kind(u,v) in STAIRS`: one tile per
  cell, `piece="stair"`, `asset="stair.png"`, `u,v`=cell, `boundHeight=float(STAIR_RISE)`,
  `imageOffset=[0.0,0.0]` (stair absent from kit), `pxPerVoxel=px_per_unit`.
  walls: iterate `massing(turned, merge=True)` where `box.kind=="wall"`; one WallDef each:
  `ax=u0/cols, ay=v0/rows, bx=(u0+l)/cols, by=(v0+d)/rows, topOffset=box.h, bottomOffset=0,
  config={"move":1,"sense":1,"sound":1,"light":1,"door":0,"dir":0}`.
  Return `{"scene": layout.name, "view": view, "pxPerVoxel": px_per_unit, "tiles":[...], "walls":[...]}`.
- DECISION (floors): `massing` merges FLOOR runs regardless of `merge`, so floor tiles are
  per-RUN not per-cell — mirrors scene_assemble; C3 does not count floors, leave as-is.
- DECISION (stair boundHeight/offset): no single massing box exists per stair cell, so use
  `STAIR_RISE` (1.0) and `[0.0,0.0]`. Only affects stair-bearing layouts (l-room has none).

### src/cli/wall_schema.py — validate_manifest (T2)
- `validate_manifest(m, kit_dir=None) -> list[str]` — one-arg call stays structural-only
  (T4/C2 uses it that way); `kit_dir` given enables asset-resolution. Errors accumulate.
  walls[]: `ax,ay,bx,by` each numeric and `0 <= x <= 1`; `topOffset,bottomOffset` numeric;
  `config` keys ⊆ {move,sense,sound,light,door,dir}; each config value `int` in `[0,2]`.
  tiles[] (only when kit_dir): read `kit.json` pieces set once; for each tile, if
  `tile["piece"]` in that set → assert `(Path(kit_dir)/tile["asset"]).exists()` else error;
  if piece NOT in kit set → skip (intentional non-kit piece, e.g. stair). Pure stdlib.

### src/cli/export_commands.py — run_export + wiring (T3)
- MUST insert pipeline on sys.path before importing scene_manifest (script run of iso-cli.py
  only has src/cli on path; conftest covers tests only): at module top
  `sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))`, then
  `from scene_manifest import build_manifest`; `from wall_schema import validate_manifest`;
  `from layout_parse import load`. Without this the CLI + Loop 5 e2e import-fail.
- `run_export(argv)`: argparse `--layout`(req), `--kit`(default `output/kit-guide`),
  `--view`(default NW, choices SW/SE/NE/NW), `--out`(default `output/manifests/{layout.name}.manifest.json`).
  `layout=load(args.layout)`; if `layout.errors`: print + `sys.exit(1)`. `m=build_manifest(layout,args.kit,args.view)`;
  `errs=validate_manifest(m,args.kit)`; if errs: print each + `sys.exit(1)`; else mkdir out
  parent, `json.dump` (indent=2), print out path.
- iso-cli.py: add `elif command == "export-manifest": from export_commands import run_export; run_export(args[1:])`
  before the final `else`. (Add a HELP stanza line — cosmetic, not gating.)

### test/test_export_manifest.py (T4)
Build once against l-room + output/kit-guide (view default NW). C3 counting seam:
door-tile = `tile["piece"].startswith("door")`, window-tile = `.startswith("window")`,
stair-tile = `piece=="stair"`; wall count = `len(m["walls"])`.

## Evaluation
criteria-coverage:
  C1 → build_manifest tiles[] (all 7 fields) + walls[] WallDef[]; verb wired T3 → test C1.
  C2 → wall_schema.validate_manifest structural rules mirror wall-types.d.ts; run_export exit(1) → test C2.
  C3 → build_manifest walls (merge=True) / door_/window_ pieces / stair pass vs DSL counts → test C3.
  C4 → asset `f"{piece}.png"` + validate_manifest asset-resolution against kit_dir → test C4.
seams:
  C1 — dict-field assertions on every tile; verb dispatch reachable via run_export(argv).
  C2 — validate_manifest([]-clean) then mutate walls[0]["ax"]=-0.1/1.1 → len(errs)>=1.
  C3 — recompute `len([b for b in massing(load('layouts/l-room.txt'),merge=True) if b.kind=="wall"])`
       == 6 (VERIFIED rotation-invariant across SW/SE/NE/NW so NW build matches unrotated recompute);
       DOOR=1, WINDOW=1, STAIR=0 are per-cell → rotation-invariant. All seams concrete.
  C4 — `(output/kit-guide / tile["asset"]).exists()` for tiles whose piece ∈ kit.json pieces.
notes: kit pieces present = floor,wall,door_u,door_v,window_u,window_v; only non-kit piece
  emitted is `stair` (skipped by C4/T2) — no unknown-piece guessing for a medium executor.
  .pyi stubs for the 3 new modules are stubgen tooling (Loop 4b/6), not an arch concern.
verdict: PASS

executor: loop-high model=opus tier=high

## Architecture (re-run after RETURN loop=3 reason=integration-gap from Loop 5)

ESCALATED from=high to=max reason=flow-rule-return-reruns-one-tier-above (executed inline by orchestrator, no new max spawn)

Gap: `build_manifest` imports `scene_assemble.load_kit`, which PIL-opens every kit PNG. A missing
asset therefore raises uncaught `FileNotFoundError` BEFORE `wall_schema.validate_manifest` can emit
the designed graceful `[FAIL]` + nonzero exit (e2e step 6).

Design change (decoupling, one seam):
- `src/pipeline/scene_assemble.py` — split kit loading:
  - NEW `load_kit_meta(kit_dir) -> dict` — reads and returns `kit.json` ONLY. No PIL, no file-existence
    requirements beyond kit.json itself.
  - `load_kit(kit_dir)` becomes `meta = load_kit_meta(kit_dir)` + sprite loading loop (behavior for the
    render lane unchanged — assemble() still eagerly loads sprites, correctly: it needs pixels).
- `src/pipeline/scene_manifest.py` — `build_manifest` switches `load_kit` → `load_kit_meta`; drops the
  unused `_sprites` binding. Manifest building is metadata-only by construction.
- Asset EXISTENCE stays where designed: `wall_schema.validate_manifest(..., kit_dir=...)` (C4) checks
  each `tiles[].asset` resolves on disk and reports `[FAIL] missing asset: <name>` + nonzero exit.
  No change needed there — it was unreachable, not wrong.

Criteria impact: C1–C4 homes unchanged. New testable seam: `build_manifest` succeeds against a kit dir
containing ONLY kit.json (no PNGs); `export-manifest` CLI against missing-asset kit exits nonzero with
`[FAIL]`, no traceback.

## Evaluation (re-run)
criteria-coverage: unchanged (C1 scene_manifest, C2+C4 wall_schema, C3 round-trip test); gap closed at the C1/C4 seam boundary.
seams: unit — build_manifest with metadata-only kit dir; e2e step 6 — CLI graceful fail (already authored in test/e2e_export_manifest.py).
verdict: PASS

executor: orchestrator model=claude-fable-5 tier=max
