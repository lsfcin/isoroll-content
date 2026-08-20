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

## Ship
diff-scope: clean
roadmap: updated /mnt/workspace/code/isoroll-content/ROADMAP.md line 11 — "Scale-consistency in guide sheets (P3)" marked done with outcome
commit: a6f4dd2 pushed: yes
leftovers: none

executor: loop-low model=haiku tier=low
