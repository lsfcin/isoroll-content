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

## Tests

Executed T1 (golden capture, low-tier fixture setup, needed before the byte-identical
seam can be written) + wrote the full Loop 4a test file at the seams named in
Architecture's `seams:` block. All new tests call/assert on symbols the architecture
specifies but that do not exist on this branch yet — every red is a missing-behavior
signal (AttributeError/TypeError naming the absent symbol, or AssertionError on an
absent doc section), never a syntax/import error. Pre-existing suite (19 tests)
stays green untouched.

T1: `test/fixtures/golden/{9panel,6cell,2cell,1cell}.png` captured from current
(pre-change) `make_tile_guide.generate()` at fixed W/D/H (5,2,3 / 4,1,3 / 6,2,2 /
3,1,4) — the byte-identical target for `--legacy-autofit`.

| test file | covers | asserts |
|-----------|--------|---------|
| test/test_scale_consistency.py::test_content_extent_oblique_matches_bbox_extent | C1/T2 | `content_extent("NE",…)` == `_bbox` extent (w_u,h_u) |
| ::test_content_extent_top_zero_dim_uses_min_thick | C1/T2 | TOP w/d=0 → `(w, MIN_THICK)` |
| ::test_content_extent_cardinal_ns_folds_top | C1/T2 | N/S → `(w, h+d*TOP_FOLD_RATIO)` |
| ::test_panel_fit_scale_matches_legacy_fit_scale | C1/T2 | `panel_fit_scale` == legacy `fit_scale` at same avail |
| ::test_draw_iso_panel_accepts_forced_scale_and_returns_bbox | C1/T2 | `draw_iso_panel(s=…)` returns 4-tuple bbox |
| ::test_render_cells_shared_scale_uniform_px_per_voxel | C1(b)/T3 | every panel bbox implies same px_per_voxel as `scale_info["px_per_voxel"]` (±1e-6) |
| ::test_legacy_autofit_flag_reproduces_golden_bytes | C1(a)/T3,T5 | `generate(…, shared_scale=False)` bytes == golden PNGs, all 4 layouts |
| ::test_write_scale_sidecar_creates_expected_keys | C2/T4 | sidecar path = `{stem}.scale.json`; keys `px_per_voxel`, `panels[].bbox` |
| ::test_write_scale_sidecar_extends_existing_file | C2/T4 | pre-existing unrelated key survives; `px_per_voxel`/`panels` updated |
| ::test_make_tile_guide_generate_writes_sidecar | C2/T4,T5 | `generate()` end-to-end writes a sidecar with both keys |
| ::test_cross_view_dims_clean_on_shared_scale | C3/T6 | uniform-scale panels → `cross_view_dims == []` |
| ::test_cross_view_dims_flags_legacy_mismatch | C3/T6 | per-cell-scale panel (implied ≠ recorded) → 1 violation, right orientation |
| ::test_sheet_qc_cli_exit_codes | C3/T6 | CLI: clean sidecar → exit 0; violating sidecar → exit 1 |
| ::test_specs_md_has_corrective_factor_appendix | C4/T7 | SPECS.md contains "Scale corrective factor" + "px_per_voxel" |

red-run: 14 failed as expected (`pytest test/test_scale_consistency.py -q` → 14 failed;
full `pytest test/ -q` → 14 failed, 19 passed) | wrong-failures: none — every failure
traced to a named not-yet-implemented symbol (`content_extent`, `panel_fit_scale`,
`draw_iso_panel(s=)`, `render_cells(shared_scale=)`, `write_scale_sidecar`,
`generate(shared_scale=)`, `cross_view_dims`) or the missing SPECS.md appendix; no
collection errors, no unrelated regressions.

executor: loop-medium model=sonnet tier=medium
