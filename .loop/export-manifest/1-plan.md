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

## Plan
branch: feature/export-manifest (base: feature/scene-creation-consolidation — carries the spec, per Loop 0 note-base-branch)

| id | task | files | done-when | tier | effort |
|----|------|-------|-----------|------|--------|
| T1 | build_manifest: tiles (per-cell merge=False) + walls (WallDef[] merged runs) — formulas pinned in Carry tasks | src/pipeline/scene_manifest.py | build_manifest(load('layouts/l-room.txt'),'output/kit-guide') returns dict with non-empty tiles[] (each w/ 7 fields) + walls[]; no exception | medium | medium |
| T2 | validate_manifest: schema mirror of wall-types.d.ts + asset resolution | src/cli/wall_schema.py | returns [] for the l-room manifest; returns ≥1 err when a WallDef anchor forced out of [0,1] | medium | low |
| T3 | export-manifest CLI verb + iso-cli dispatch wire | src/cli/export_commands.py, src/cli/iso-cli.py | `python iso-cli.py export-manifest --layout ../pipeline/layouts/l-room.txt` writes output/manifests/l-room.manifest.json, exit 0; corrupt kit → exit 1 | medium | medium |
| T4 | pytest covering C1–C4 on l-room | test/test_export_manifest.py | 4 tests present, red before T1–T3 for missing-behavior reason, green after | medium | medium |
| T5 | ROADMAP row done + plan pointer | ROADMAP-content-gen.md | export-manifest row marked done, links `.loop/export-manifest/` | low | low |

## Plan Review (adversarial, assume small executors)
- **C4 naming vs on-disk kit (FATAL if unresolved).** SPECS `{name}_{facing}.png` is flagged "Aspirational — not implemented" and refers to split per-direction SPRITES; the gray kit on disk is camera-fixed `{piece}.png` (floor/wall/door_u/door_v/window_u/window_v — dimetric, rotation = cell remap, no per-facing files). A medium executor would build `wall_NW.png`, fail resolution, and stall. → RESOLVED in Carry: manifest `asset` = `f"{piece}.png"` (the real on-disk name); `facing` is a SEPARATE tile field (= view); C4 test resolves `{piece}.png` in kit dir. Facing-in-filename is deferred to the cardinal art regime. **User-confirm flag (non-blocking): C4's literal filename form is reinterpreted; if the user insists on `_{facing}` in the filename, RETURN loop=0.**
- **WallDef anchor space (per-tile vs scene).** wall-types.d.ts says anchors are [0,1]² relative to a tile's top-left; the pilot emits SCENE-level WallDef[] normalized to the grid bbox (ax=u0/cols …). This is structurally valid (C2) and count-correct (C3). Per-tile re-anchoring is the `module-walls-import` loop's concern. → Formula pinned in Carry so no executor guess; noted as a seam boundary for the next loop.
- **Door-gap vision not modeled at WallDef level.** One WallDef per merged run (door=0) keeps `len(walls)` == wall-run count for C3. Door/window openings live as separate per-cell tiles (door_u/window_v), which carry door behavior downstream. Vision-through-doorway wiring is explicitly the `module-walls-import` loop, not this pilot. No criterion tests door-gap geometry; documented limitation, not wrong-geometry.
- **merge=True vs merge=False.** Ambiguity killed by splitting lanes in Carry: tiles use merge=False (matches scene_assemble / module assembler paste order), walls use merge=True (one line per run). C3 counts derive unambiguously: wall_runs=len(walls), doors/windows/stairs from tile piece prefix.
- **Stairs with no kit art.** l-room has 0 stairs so C3 stair count = 0 trivially; builder still emits stair tiles from STAIRS cells (piece `stair`, no PNG yet) and validation skips pieces absent from kit.json — keeps derivation general without breaking C4.
- **Geometry math is the only subtle part → Loop 3 (high) MUST confirm the pinned anchor/imageOffset/boundHeight formulas before Loop 4b; if Loop 3 leaves any formula open, escalate T1 to high.** All formulas are stated concretely in Carry, so the default medium tier is executable.
- **Infra:** conftest.py already puts src/cli + src/pipeline on sys.path (no test bootstrap needed). New .py files get .pyi stubs auto-generated by the post-edit hook (facade-gate) — no manual stubgen. output/manifests/ is created by run_export (parent output/ exists). All new files < 200 LOC (hook limit).
- **PLANS-LIVE-IN-ROADMAPS:** satisfied by T5 (pointer added on the feature branch), deliberately NOT written to base branch now to keep the Loop 2 diff clean.

verdict: PASS

executor: loop-high model=opus tier=high
