## Carry
slug: scale-consistency | branch: feature/scale-consistency | root: /mnt/workspace/code/isoroll-content
test-cmd: `make verify-fast` | e2e-cmd: regenerate a 9panel guide + run QC dim check on it (Loop 5 scripts)
criticality: normal | verdict: standard
criteria:
  C1 — shared-scale mode: multi-panel guide sheets (`tile_guide_matrix.py` / `make_tile_guide.py` layouts) compute ONE px-per-voxel `s` for the whole sheet (min over panels of each panel's fit_scale, i.e. the largest piece constrains all) instead of per-cell autofit; default ON; `--legacy-autofit` flag preserves old behavior
  C2 — `s` recorded: guide generation writes a JSON sidecar `{stem}.scale.json` (or extends an existing sidecar) with `px_per_voxel` + per-panel content bbox; downstream never re-measures pixels
  C3 — QC cross-view dimension check: new check in `src/cli/sheet_qc.py` — same object's silhouette bbox across view panels, expected ratios derived from the projection (dimetric W/H formulas), tolerance ±2%; nonzero exit on violation
  C4 — corrective doc: for EXISTING autofit sheets, per-cell corrective factor `s_shared/s_cell` derivable from recorded bboxes; short doc section (SPECS.md or SCENE-CREATION.md appendix) with the formula + one worked example
tasks:
  T1 — capture golden PNGs of current autofit output (9panel/6cell/2cell/1cell) into test/fixtures/golden/ — test/fixtures/golden/*, make_tile_guide.py(none) — low
  T2 — render.py: add content_extent(orientation,w,d,h)->(w_u,h_u) [single source of projection dims incl. iso _bbox, cardinal net, TOP MIN_THICK]; give draw_iso_panel/draw_square_grid/draw_flat_grid optional s=None (None=byte-identical autofit) and make each return its content px-bbox — src/pipeline/tile_guide_render.py(+.pyi) — high
  T3 — matrix.py: render_cells gains shared_scale=True; two-pass (fit each panel via content_extent, s=min over non-blank/non-caption panels, redraw all at s), collect per-panel bboxes; return (img, scale_info); --legacy-autofit CLI flag sets shared_scale=False — src/pipeline/tile_guide_matrix.py(+.pyi) — high
  T4 — sidecar JSON: both generate() write {stem}.scale.json {px_per_voxel, panels:[{row,col,orientation,w,d,h,bbox}]}, extend if present — src/pipeline/tile_guide_matrix.py, src/pipeline/make_tile_guide.py(+.pyi) — medium
  T5 — make_tile_guide.py: thread shared_scale + --legacy-autofit through generate() (default ON) via matrix render_cells return — src/pipeline/make_tile_guide.py(+.pyi) — medium
  T6 — sheet_qc.py: cross_view_dims(sidecar)->violations using content_extent(imported from tile_guide_render) to get expected extent per panel; implied px_per_voxel per panel must match sidecar px_per_voxel within ±2%; add argparse __main__ nonzero exit on violation — src/cli/sheet_qc.py(+.pyi) — high
  T7 — SPECS.md appendix: corrective factor s_shared/s_cell formula + one worked numeric example from a real sidecar — SPECS.md — medium
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/SCENE-CREATION.md (§ Scale-consistency spec — the contract for this loop), /mnt/workspace/code/isoroll-content/src/pipeline/CONTEXT.md, /mnt/workspace/core/skills/iso-visual.md

## User Test
scenario: An artist regenerates a real 9-panel wall guide (W5xD2xH3) with the
new default shared-scale mode, trusts the `{stem}.scale.json` sidecar it
writes without re-measuring any pixels, and runs the QC cross-view dimension
check on it before handing the sheet off — it should come back clean. Later
someone reintroduces the old per-cell autofit behavior via `--legacy-autofit`
on the same wall; QC must catch that regression. Finally, since
`--legacy-autofit` claims to be a byte-identical escape hatch to the
pre-change renderer, its output on all four fixture layouts is checked
against the goldens captured before this feature landed.

script: test/e2e_scale_consistency.py (new, follows the test/e2e_scenario.py
convention: no `test_` prefix so `verify-fast`/`verify-full` never
auto-collect it; chains real subprocess CLI calls, not unit-level imports)
run: `python3 test/e2e_scale_consistency.py` (from
/mnt/workspace/code/isoroll-content)

observed:
```
[1/6] make_tile_guide.py (default shared-scale) -> .../9panel_shared.png
Saved: .../9panel_shared.png  (960x960 px, 9panel, W5xH3xD2)
[2/6] verify sidecar: one shared px_per_voxel -> .../9panel_shared.scale.json
  px_per_voxel = 40.57142857142857  panels = 9
[3/6] sheet_qc.py on shared-scale sheet (expect clean, exit 0)
(no violations printed)
  exit=0 clean=True
[4/6] make_tile_guide.py --legacy-autofit -> .../9panel_legacy.png
Saved: .../9panel_legacy.png  (960x960 px, 9panel, W5xH3xD2)
[5/6] sheet_qc.py on legacy sheet (expect violations, nonzero exit)
VIOLATION row=0 col=1 orientation=N   implied=56.8000 expected=40.5714 rel=0.4000
VIOLATION row=1 col=0 orientation=W   implied=51.6364 expected=40.5714 rel=0.2727
VIOLATION row=1 col=1 orientation=TOP implied=56.8000 expected=40.5714 rel=0.4000
VIOLATION row=1 col=2 orientation=E   implied=51.6364 expected=40.5714 rel=0.2727
VIOLATION row=2 col=1 orientation=S   implied=56.8000 expected=40.5714 rel=0.4000
  exit=1 flagged=True
[6/6] byte-compare legacy output vs golden -> test/fixtures/golden/9panel.png
  legacy bytes == golden bytes: True
RESULT sidecar_ok=True qc_shared_clean=True qc_legacy_flagged=True legacy_matches_golden=True
PASS
```

Additional manual check (all 4 golden layouts, not just 9panel, to stress the
byte-identity claim beyond the scripted scenario): regenerated 9panel(5,2,3),
6cell(4,1,3), 2cell(6,2,2), 1cell(3,1,4) with `--legacy-autofit` and `cmp`'d
each against `test/fixtures/golden/{layout}.png` — all 4 BYTE-IDENTICAL.

Ran full suite afterward: `make verify-fast` → `33 passed, 12 warnings
(pre-existing Pillow deprecation, unrelated)` — new e2e script isn't
`test_`-prefixed so it wasn't auto-collected; confirms the scripted scenario
didn't disturb anything.

matches-expected-result: yes — shared-scale mode produces one shared
`px_per_voxel` sidecar (C2) that a QC pass accepts (C3-clean side);
`--legacy-autofit` reproduces the pre-change per-cell renderer byte-for-byte
(C1) while the same QC check now flags it (C3-bidirectional). All observed
behavior matches Loop 0's `expected-result` and C1-C3; C4 (doc appendix) was
already verified by unit test `test_specs_md_has_corrective_factor_appendix`
in Loop 4b and is not re-exercised here since it's a doc-only, non-runtime
criterion outside the scope of an e2e scenario.

executor: loop-medium model=sonnet tier=medium
