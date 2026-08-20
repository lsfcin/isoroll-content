# test
> ← add description

<!-- routing:start -->
## Routing

| Subdirectory | Description |
|--------------|-------------|
| [`fixtures/`](fixtures/CONTEXT.md) | — |

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`conftest.py`](conftest.py) | [`conftest.pyi`](conftest.pyi) | — | conftest.py — pytest path bootstrap: make src/cli and src/pipeline modules importable. |
| [`e2e_export_manifest.py`](e2e_export_manifest.py) | [`e2e_export_manifest.pyi`](e2e_export_manifest.pyi) | `run_cli`, `main` | e2e_export_manifest.py — Loop 5 user scenario: export-manifest CLI verb, full round-trip. |
| [`e2e_scale_consistency.py`](e2e_scale_consistency.py) | [`e2e_scale_consistency.pyi`](e2e_scale_consistency.pyi) | `run_cli`, `main` | e2e_scale_consistency.py — Loop 5 user scenario: an artist regenerates a |
| [`e2e_scenario.py`](e2e_scenario.py) | [`e2e_scenario.pyi`](e2e_scenario.pyi) | `run_cli`, `recolor_preserve_silhouette`, `inject_residue`, `main` | e2e_scenario.py — Loop 5 user scenario: full postproc QC pipeline, one dirty NB output. |
| [`fixtures.py`](fixtures.py) | [`fixtures.pyi`](fixtures.pyi) | `magenta_grid_sheet`, `cyan_squares`, `clean_image`, `filled_mask`, `alpha_blob` | fixtures.py — synthetic PIL image builders shared by the postproc test suite. |
| [`test_arm_a_texture.py`](test_arm_a_texture.py) | [`test_arm_a_texture.pyi`](test_arm_a_texture.pyi) | — | test_arm_a_texture.py — arm_a paints every projected face with a warped |
| [`test_cabin_golden.py`](test_cabin_golden.py) | [`test_cabin_golden.pyi`](test_cabin_golden.pyi) | `cabin`, `kit_root` | test_cabin_golden.py — the PLAYABLE fixture, end to end through the seam, for all 9 views. |
| [`test_dsl_v2_manifest.py`](test_dsl_v2_manifest.py) | [`test_dsl_v2_manifest.pyi`](test_dsl_v2_manifest.pyi) | — | test_dsl_v2_manifest.py — C4 (manifest): tile.z / wall.dir / boundHeight + HUD counts. |
| [`test_dsl_v2_massing.py`](test_dsl_v2_massing.py) | [`test_dsl_v2_massing.pyi`](test_dsl_v2_massing.pyi) | — | test_dsl_v2_massing.py — C3 (massing): per-cell Z-run boxes match rig semantics. |
| [`test_dsl_v2_parse.py`](test_dsl_v2_parse.py) | [`test_dsl_v2_parse.pyi`](test_dsl_v2_parse.pyi) | — | test_dsl_v2_parse.py — C1 (parse): v2 fixtures parse clean; invalid fixtures raise errors. |
| [`test_dsl_v2_render.py`](test_dsl_v2_render.py) | [`test_dsl_v2_render.pyi`](test_dsl_v2_render.pyi) | — | test_dsl_v2_render.py — C5 (guide render): scene_guide_render consumes massing v2 (multi-level). |
| [`test_dsl_v2_serialize.py`](test_dsl_v2_serialize.py) | [`test_dsl_v2_serialize.pyi`](test_dsl_v2_serialize.pyi) | — | test_dsl_v2_serialize.py — C2 (round-trip): to_dsl(parse_text(text)) == text, per fixture. |
| [`test_enclosure_masks.py`](test_enclosure_masks.py) | [`test_enclosure_masks.pyi`](test_enclosure_masks.pyi) | — | test_enclosure_masks.py — Lucas 2026-07-19 union enclosure mask |
| [`test_export_manifest.py`](test_export_manifest.py) | [`test_export_manifest.pyi`](test_export_manifest.pyi) | `layout`, `manifest` | test_export_manifest.py — Loop 4a tests for the export-manifest CLI verb. |
| [`test_face_edges.py`](test_face_edges.py) | [`test_face_edges.pyi`](test_face_edges.pyi) | — | test_face_edges.py — R2-2 edge-ink contract (design/S4-REVIEW-ROUNDS.md |
| [`test_face_project.py`](test_face_project.py) | [`test_face_project.pyi`](test_face_project.pyi) | — | test_face_project.py — the projection seam after the family parameter replaced the TOP branches. |
| [`test_grid_drift.py`](test_grid_drift.py) | [`test_grid_drift.pyi`](test_grid_drift.pyi) | — | test_grid_drift.py — detect_grid tolerates +-2px grid-line drift (C4). |
| [`test_guide_marks.py`](test_guide_marks.py) | [`test_guide_marks.pyi`](test_guide_marks.pyi) | — | test_guide_marks.py — residue_count on synthetic cyan-mark fixtures (C2). |
| [`test_kit_module_render.py`](test_kit_module_render.py) | [`test_kit_module_render.pyi`](test_kit_module_render.pyi) | — | test_kit_module_render.py — shared projected-face seam, flat render, one |
| [`test_kit_modules.py`](test_kit_modules.py) | [`test_kit_modules.pyi`](test_kit_modules.pyi) | — | test_kit_modules.py — KIT V2 module geometry as faces (C1). |
| [`test_layout_rotate.py`](test_layout_rotate.py) | [`test_layout_rotate.pyi`](test_layout_rotate.pyi) | — | test_layout_rotate.py — rotation is a remap of the SAME physical scene, for all 9 views. |
| [`test_linework.py`](test_linework.py) | [`test_linework.pyi`](test_linework.pyi) | — | Seams for /linework (S3): floor grammar per Lucas 2026-07-15 — |
| [`test_scale_consistency.py`](test_scale_consistency.py) | [`test_scale_consistency.pyi`](test_scale_consistency.pyi) | — | test_scale_consistency.py — shared-scale (px-per-voxel) tests for the |
| [`test_scene_manifest_kit_meta.py`](test_scene_manifest_kit_meta.py) | [`test_scene_manifest_kit_meta.pyi`](test_scene_manifest_kit_meta.pyi) | `layout`, `metadata_only_kit_dir` | test_scene_manifest_kit_meta.py — Loop 4a (re-run) tests for the metadata-only kit seam. |
| [`test_sheet_grid.py`](test_sheet_grid.py) | [`test_sheet_grid.pyi`](test_sheet_grid.pyi) | — | test_sheet_grid.py — detect_grid + strip_linework on synthetic magenta-grid fixtures (C1). |
| [`test_sheet_qc.py`](test_sheet_qc.py) | [`test_sheet_qc.pyi`](test_sheet_qc.pyi) | — | test_sheet_qc.py — silhouette_iou unit tests (C3). |
| [`test_stage_kit_modules.py`](test_stage_kit_modules.py) | [`test_stage_kit_modules.pyi`](test_stage_kit_modules.pyi) | — | test_stage_kit_modules.py — per-module arm sheets staged to |
| [`test_texture_map.py`](test_texture_map.py) | [`test_texture_map.pyi`](test_texture_map.pyi) | — | test_texture_map.py — face(kind,mat) -> texture family/variant lookup (T1, C2, C8). |
| [`test_texture_map_slab.py`](test_texture_map_slab.py) | [`test_texture_map_slab.pyi`](test_texture_map_slab.pyi) | — | test_texture_map_slab.py — R2-5 door_1x2/window_1x1 slab FAMILY/flip_h |
| [`test_texture_warp.py`](test_texture_warp.py) | [`test_texture_warp.pyi`](test_texture_warp.pyi) | — | test_texture_warp.py — homography/affine texture warp onto a projected |
| [`test_view_table.py`](test_view_table.py) | [`test_view_table.pyi`](test_view_table.pyi) | — | test_view_table.py — invariants of the 8+1 view table (view_table.py). |
<!-- routing:end -->
