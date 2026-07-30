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

## Code

Implemented T2-T7 per `3-arch.md` in one pass (T1 golden fixtures already landed
in Loop 4a). One deviation from the architecture doc, forced by the repo's
per-file 200-line size gate (`.hooks/pre-edit.py`): T2's `content_extent` /
`panel_fit_scale` (and the pure geometry `_bbox`/`fit_scale`/`_corner`/
`MIN_THICK`/`TOP_FOLD_RATIO`/`PAD` they depend on) were split out of
`tile_guide_render.py` into a new sibling module `src/pipeline/panel_geometry.py`
(no PIL, pure math) — `tile_guide_render.py` re-exports them (`from
panel_geometry import ...`) so `tgr.content_extent`, `tgr._bbox`, `tgr.MIN_THICK`
etc. still resolve exactly as the Loop 4a tests call them. `tile_guide_matrix.py`
and `sheet_qc.py` import `panel_fit_scale`/`content_extent` from `panel_geometry`
directly (cleaner than routing through the drawing module). All symbol names,
signatures, and behavior match the architecture; only the file that owns the
geometry math moved. `sheet_qc.py` also gained a `sys.path.insert` for the
`pipeline` dir (mirrors the existing `export_commands.py` pattern) since its new
CLI entrypoint is invoked as a subprocess with cwd=`src/cli`, outside pytest's
`conftest.py` path bootstrap.

T2 (`tile_guide_render.py` + new `panel_geometry.py`): `content_extent`
dispatches oblique via `_bbox`, TOP via `(w or MIN_THICK, d or MIN_THICK)`,
N/S via `(w, h+d*TOP_FOLD_RATIO)`, W/E via `(d, h+w*TOP_FOLD_RATIO)` — verified
against `draw_panel`'s w/d/h mapping, not swapped. `_origin_for_cell` takes
`s=None` (autofit, unchanged numeric path) or a forced scale. `draw_iso_panel`
returns the sheet-absolute GEOMETRIC bbox (mirror-aware); `draw_square_grid` /
`draw_flat_grid` return their already-absolute grid bbox.

T3/T4 (`tile_guide_matrix.py`): `render_cells(..., shared_scale=True)` — pass 1
computes `s_shared = min(panel_fit_scale(...) for non-caption cells)`; pass 2
draws every panel at `s_shared` (shared) or `None` (legacy, byte-identical);
returns `(img, scale_info)` with `scale_info["px_per_voxel"]` always `s_shared`
even in legacy mode (that mismatch is what QC flags). `write_scale_sidecar`
extends-not-clobbers an existing `{stem}.scale.json`. `--legacy-autofit` CLI
flag added.

T5 (`make_tile_guide.py`): `generate(..., shared_scale=True)` threads through
to `render_cells` + calls `write_scale_sidecar`; `--legacy-autofit` CLI flag
added.

T6 (`sheet_qc.py`): `cross_view_dims(scale_info, tol=0.02)` computes each
panel's implied px-per-voxel from its bbox width / `content_extent` width,
flags `rel > tol`. `__main__` added: positional `sidecar` path + `--tolerance`,
prints violations, `sys.exit(1 if violations else 0)`.

T7 (`SPECS.md`): new "Scale corrective factor" subsection under Chosen Pipeline
→ Tiles (L1), formula `corrective = s_shared / s_cell = px_per_voxel / s_cell`,
worked example using a REAL sidecar generated via `make_tile_guide.py --width 4
--height 3 --depth 1 --layout 6cell --legacy-autofit` (numbers read from the
actual `guide.scale.json`, not fabricated — NE panel happens to be the
constraining panel here so its corrective is 1.0; TOP's is ≈0.727).

attempt 1: implemented T2-T7 in full (per architecture, with the panel_geometry
split above) before first test run → `pytest test/test_scale_consistency.py -q`
→ 14 passed, 0 red. No escalation needed.

green: yes run: `pytest test/ -q` → `33 passed, 12 warnings in 0.21s` (19
pre-existing + 14 new). `make verify-fast` (compileall + pytest) exits 0.
touched: src/pipeline/tile_guide_render.py(+.pyi), src/pipeline/tile_guide_matrix.py(+.pyi),
src/pipeline/make_tile_guide.py(+.pyi), src/pipeline/panel_geometry.py(+.pyi, new),
src/cli/sheet_qc.py(+.pyi), SPECS.md

executor: loop-medium model=sonnet tier=medium
