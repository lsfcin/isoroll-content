## Carry
slug: export-manifest | branch: feature/export-manifest | root: /mnt/workspace/code/isoroll-content
test-cmd: `make verify-fast` (includes pytest) | e2e-cmd: CLI export run on the l-room layout (Loop 5 scripts it)
criticality: normal | verdict: standard
criteria:
  C1 — a CLI verb (in `src/cli/`, wired via `iso-cli.py` dispatch like `multiview_commands.py` verbs) exports a scene manifest JSON from a layout file + kit alignment manifest: scene tiles (kit piece id, facing, grid position, `boundHeight`, `imageOffset`, px-per-voxel scale) + `WallDef[]` derived from the layout's wall runs and openings
  C2 — manifest `WallDef[]` fields structurally validate against `/mnt/workspace/code/isoroll-module/src/walls/wall-types.d.ts` (tileAnchor in [0,1]², door/sense/dir enums) — validation is code in this repo (schema mirror or parser), failure = nonzero exit
  C3 — round-trip: wall-run / door / window / stair counts derived back from the manifest equal counts parsed from the layout DSL for the l-room fixture
  C4 — asset references follow `{name}_{facing}.png` naming (SPECS.md) and resolve against the gray kit output on disk
tasks: <filled by Loop 1>
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/SCENE-CREATION.md (contract §), /mnt/workspace/code/isoroll-content/src/pipeline/CONTEXT.md, /mnt/workspace/code/isoroll-content/src/cli/CONTEXT.md

## Clarify
intent: export a scene manifest JSON (tiles + WallDef[]) from the assembled gray l-room so isoroll-module can import it (program P2 seam, first half).
motivation: closes the generate→play seam; this is the loop-engineering [pilot] — smallest piece testable without Foundry.
refs: SCENE-CREATION.md §Contract + §Program P2; ROADMAP-content-gen.md §export (layer 4) + delegação table row `export-manifest`; module import surface `src/walls/wall-crud.ts::createWallsFromDefs`; existing spine `src/pipeline/{layout_parse,layout_massing,kit_render,scene_assemble}.py`; demo `output/assembled/l-room_{NW,NE,SW,SE}.png`.
scope-files: `src/cli/` (new exporter verb + validation), `src/pipeline/` (only if a small helper is needed), `test/`, `.loop/export-manifest/`, ROADMAP-content-gen.md (plan line).
expected-result: `iso-cli.py <export verb> --layout <l-room> ...` writes `output/manifests/l-room.manifest.json`; validation passes; counts match layout; pytest/make verify-fast green.
ambition: solid
criticality: normal tolerance: manifest format may gain fields later (painter/multiview); wrong geometry is NOT tolerable (counts/anchors must round-trip).
innovation: none — mechanical after the seams exist (per ROADMAP-content-gen execution decision).
verdict: standard
keep-trail: yes (pilot — routing audit feeds loop-engineering [iterate])
note-base-branch: branch from `feature/scene-creation-consolidation` (stacked — carries the spec; develop merge order handled by user later).

executor: orchestrator (Fable session, plan-approved interview) model=claude-fable-5 tier=max
