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

## Ground
branch-created: feature/scale-consistency base: feature/export-manifest
paths: 14/15 ok | missing: test/fixtures (parent dir absent; test/ exists so will create in T1)
test-cmd-runs: yes (19 passed, 0 failed)

executor: loop-low model=haiku tier=low

## Architecture

Shared quantity `s` = **px-per-voxel**, comparable across ALL three projections because
each draw fn's autofit scale multiplies unit voxel offsets (iso `_corner` _UX/_UY/_UZ,
TOP cell_s, cardinal cell_s). Verified numerically: `content_extent` reproduces every
projection's current autofit `fit_scale` to <1e-9 → legacy path stays byte-identical.
`pad=18`, `cell_px=320` for all cells → single `avail = cell_px - 2*pad` sheet-wide.

**src/pipeline/tile_guide_render.py** (T2) — projection math + optional forced scale.
- `PAD = 18` module const; replace the three `pad: int = 18` defaults with `pad=PAD`.
- `content_extent(orientation, w, d, h) -> (w_u, h_u)` — SINGLE source of voxel-unit
  content dims per projection. Formulas (all verified == current fit inputs):
  · OBLIQUE NW/NE/SW/SE: `mnx,mxx,mny,mxy=_bbox(w,d,h); return (mxx-mnx, mxy-mny)`
  · TOP: `(w or MIN_THICK, d or MIN_THICK)`
  · N/S: `(w, h + d*TOP_FOLD_RATIO)`   · W/E: `(d, h + w*TOP_FOLD_RATIO)`
  (dispatch matches draw_panel's w/d/h→cols/rows mapping in matrix — do NOT swap.)
- `panel_fit_scale(orientation, w, d, h, cell_px, pad=PAD) -> float` — autofit s for one
  panel: `wu,hu=content_extent(...); avail=cell_px-2*pad; return min(avail/wu, avail/hu)`.
- `_origin_for_cell(l,d,h,cell_box,pad,s=None)` — when `s is None` compute via `fit_scale`
  (unchanged); else use passed `s`. Centering formula already works for any s ≤ fit.
- `draw_iso_panel(..., s=None)` → **returns** content px-bbox `(x0,y0,x1,y1)` sheet-absolute,
  GEOMETRIC extent (polygon extremes, NOT silhouette-stroke pixels — avoids SIL_WIDTH=5
  noise vs ±2% QC). Local bbox = `(ox+mnx*s, oy+mny*s, ox+mxx*s, oy+mxy*s)`; if `needs_mirror`
  flip x within cw (`x'=cw-x`, swap x0/x1); then offset by `(cx,cy)`.
- `draw_square_grid(..., s=None)` / `draw_flat_grid(..., s=None)` → when `s` given use it as
  cell_s (skip the `min(...)` fit); center as now; **return** `(ox,oy,ox+grid_w,oy+grid_h)`
  (already sheet-absolute — these draw into the real `draw`, no scratch/mirror).
- s=None path everywhere = current numeric path → byte-identical (T1 golden guards).

**src/pipeline/tile_guide_matrix.py** (T3, T4) — two-pass + sidecar.
- `render_cells(rows, cols, grid, cell_px=320, shared_scale=True) -> (img, scale_info)`.
  Pass 1: `fits = [panel_fit_scale(cell.orientation, cell.w, cell.d, cell.h, cell_px)
  for cell in grid.values() if cell.orientation != "CAPTION"]`; `s_shared = min(fits)`.
  Pass 2: draw each cell; `panel_s = s_shared if shared_scale else None`; pass `s=panel_s`
  to draw_panel→draw fns; collect returned bbox. draw_panel gains `s=None` passthrough.
  scale_info = `{"px_per_voxel": s_shared, "panels":[{"row","col","orientation","w","d","h",
  "bbox":[x0,y0,x1,y1]}...]}`. NOTE: px_per_voxel is ALWAYS s_shared even in legacy mode —
  that is what makes QC flag legacy sheets (their per-cell bboxes imply ≠ s_shared).
- `write_scale_sidecar(out_path: Path, scale_info: dict) -> Path` — writes `{stem}.scale.json`
  next to the PNG; if it exists, load + update only `px_per_voxel`/`panels` keys (extend).
  Shared helper (jscpd gate) — make_tile_guide imports it, no dup.
- `generate(...)`: unpack `img, scale_info = render_cells(...)`; save img; `write_scale_sidecar`.
- `__main__`: add `--legacy-autofit` (store_true) → `render_cells(..., shared_scale=not legacy)`.

**src/pipeline/make_tile_guide.py** (T5, T4) — thread flag + sidecar.
- `generate(w,d,h,layout,out_path, shared_scale=True)`: `img, scale_info =
  tile_guide_matrix.render_cells(rows,cols,grid,CELL_PX, shared_scale)`; save;
  `tile_guide_matrix.write_scale_sidecar(out_path, scale_info)`.
- `__main__`: add `--legacy-autofit` (store_true) → pass `shared_scale=not args.legacy_autofit`.

**src/cli/sheet_qc.py** (T6) — cross-view dim check (conftest puts pipeline on sys.path).
- `from tile_guide_render import content_extent`.
- `cross_view_dims(scale_info: dict, tol: float = 0.02) -> list[dict]` — for each panel:
  `wu,hu = content_extent(p["orientation"], p["w"], p["d"], p["h"])`;
  `x0,y0,x1,y1 = p["bbox"]`; `implied = (x1-x0)/wu`; `rel = abs(implied - px_per_voxel)/px_per_voxel`;
  if `rel > tol` append `{row,col,orientation,implied,expected:px_per_voxel,rel}`.
  (Sanity: also assert `(y1-y0)/hu` agrees; use x-derived as primary.)
- `__main__`: argparse `sidecar` (path, positional) + `--tolerance 0.02`; load JSON;
  `v = cross_view_dims(data, tol)`; print each; `sys.exit(1 if v else 0)`.

**SPECS.md** (T7) — appendix "Scale corrective factor": per-panel `s_cell = bbox_w / content_extent_w`
(= implied px-per-voxel); corrective `= s_shared / s_cell = px_per_voxel / s_cell`; one worked
numeric example read from a real generated `*.scale.json`.

## Evaluation
criteria-coverage:
  C1 → T2 content_extent+panel_fit_scale+s params; T3 render_cells shared_scale=True default + --legacy-autofit
  C2 → T3 scale_info + T4 write_scale_sidecar (both generate() paths, extend-if-present)
  C3 → T6 cross_view_dims + __main__ nonzero exit, expected extents from content_extent (projection formulas)
  C4 → T7 SPECS appendix: s_shared/s_cell = px_per_voxel/implied_s + worked example from a sidecar
seams:
  C1 → (a) golden byte-identical: `make_tile_guide --legacy-autofit` output == test/fixtures/golden/*.png
       (b) shared mode: every panel bbox in scale_info implies the SAME px_per_voxel (±1e-6)
  C2 → assert `{stem}.scale.json` exists with keys px_per_voxel (float) + panels[].bbox (4-int); re-run extends not clobbers
  C3 → BIDIRECTIONAL: shared-scale sheet → `cross_view_dims`==[] / CLI exit 0; legacy sheet (per-cell s) → violations / exit 1
  C4 → doc-only; numeric example checkable by re-deriving px_per_voxel/implied_s from the cited sidecar (manual/doctest seam)
notes-for-executors:
  - content_extent w/d/h→projection mapping must mirror draw_panel exactly (N/S use w,d+h,top=d; W/E use d,w+h,top=w). Swapping breaks QC silently.
  - record GEOMETRIC bbox (polygon extremes), never silhouette-stroke pixels — stroke width would blow the ±2% budget.
  - px_per_voxel is s_shared in BOTH modes; legacy panels are drawn at per-cell s, so QC is a real (failing) check on legacy sheets — this is the C3 seam, not a bug.
  - .pyi regen required for tile_guide_render, tile_guide_matrix, make_tile_guide, sheet_qc (interface-first hook).
verdict: PASS

executor: loop-high model=opus tier=high
