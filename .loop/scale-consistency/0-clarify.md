## Carry
slug: scale-consistency | branch: feature/scale-consistency | root: /mnt/workspace/code/isoroll-content
test-cmd: `make verify-fast` | e2e-cmd: regenerate a 9panel guide + run QC dim check on it (Loop 5 scripts)
criticality: normal | verdict: standard
criteria:
  C1 — shared-scale mode: multi-panel guide sheets (`tile_guide_matrix.py` / `make_tile_guide.py` layouts) compute ONE px-per-voxel `s` for the whole sheet (min over panels of each panel's fit_scale, i.e. the largest piece constrains all) instead of per-cell autofit; default ON; `--legacy-autofit` flag preserves old behavior
  C2 — `s` recorded: guide generation writes a JSON sidecar `{stem}.scale.json` (or extends an existing sidecar) with `px_per_voxel` + per-panel content bbox; downstream never re-measures pixels
  C3 — QC cross-view dimension check: new check in `src/cli/sheet_qc.py` — same object's silhouette bbox across view panels, expected ratios derived from the projection (dimetric W/H formulas), tolerance ±2%; nonzero exit on violation
  C4 — corrective doc: for EXISTING autofit sheets, per-cell corrective factor `s_shared/s_cell` derivable from recorded bboxes; short doc section (SPECS.md or SCENE-CREATION.md appendix) with the formula + one worked example
tasks: <filled by Loop 1>
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/SCENE-CREATION.md (§ Scale-consistency spec — the contract for this loop), /mnt/workspace/code/isoroll-content/src/pipeline/CONTEXT.md, /mnt/workspace/core/skills/iso-visual.md

## Clarify
intent: kill cross-view px-per-voxel drift in guide sheets (program P3): one shared scale per sheet, recorded, QC-checked.
motivation: `fit_scale` autofits per cell → same piece renders at different scales in different views, breaking cross-view visual consistency (essential requirement). Hand-drawn reference deck kept proportions consistent — restore that property. NB kit painting (P5) must consume consistent guides.
refs: SCENE-CREATION.md § Scale-consistency spec; `src/pipeline/tile_guide_render.py` (fit_scale L46, _origin_for_cell), `tile_guide_matrix.py` (draw_panel/render_cells), `make_tile_guide.py`; reference deck `src/pipeline/prompts/reference/isometric_images.pdf`; kit_render.py is ALREADY camera-fixed (out of scope — don't touch).
scope-files: `src/pipeline/tile_guide_render.py`, `src/pipeline/tile_guide_matrix.py`, `src/pipeline/make_tile_guide.py` (flag wiring), `src/cli/sheet_qc.py`, `test/`, SPECS.md (C4 section).
expected-result: regenerating any 6cell/9panel guide yields identical px-per-voxel in every panel (assert via sidecar + QC); legacy flag reproduces old output byte-identical; verify-fast green.
ambition: solid
criticality: normal tolerance: legacy sheets stay as-is (corrective doc covers them); breaking change to default output is INTENDED (guides regenerate cheaply).
innovation: none — mechanical per spec.
verdict: standard
keep-trail: yes
note-base-branch: branch from `feature/export-manifest` (stack tip — carries SCENE-CREATION.md spec + latest pipeline state; develop merge order is user's call later).

executor: orchestrator (Fable session, plan-approved) model=claude-fable-5 tier=max
