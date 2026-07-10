# test
> ← add description

<!-- routing:start -->
## Routing

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`conftest.py`](conftest.py) | [`conftest.pyi`](conftest.pyi) | — | !/usr/bin/env python3 |
| [`e2e_export_manifest.py`](e2e_export_manifest.py) | [`e2e_export_manifest.pyi`](e2e_export_manifest.pyi) | `run_cli`, `main` | !/usr/bin/env python3 |
| [`e2e_scale_consistency.py`](e2e_scale_consistency.py) | [`e2e_scale_consistency.pyi`](e2e_scale_consistency.pyi) | `run_cli`, `main` | !/usr/bin/env python3 |
| [`e2e_scenario.py`](e2e_scenario.py) | [`e2e_scenario.pyi`](e2e_scenario.pyi) | `run_cli`, `recolor_preserve_silhouette`, `inject_residue`, `main` | !/usr/bin/env python3 |
| [`fixtures.py`](fixtures.py) | [`fixtures.pyi`](fixtures.pyi) | `magenta_grid_sheet`, `cyan_squares`, `clean_image`, `filled_mask`, `alpha_blob` | !/usr/bin/env python3 |
| [`test_export_manifest.py`](test_export_manifest.py) | [`test_export_manifest.pyi`](test_export_manifest.pyi) | `layout`, `manifest`, `test_tiles_have_all_fields`, `test_walls_are_walldefs`, `test_run_export_cli_verb` | !/usr/bin/env python3 |
| [`test_grid_drift.py`](test_grid_drift.py) | [`test_grid_drift.pyi`](test_grid_drift.pyi) | `test_detect_grid_snaps_to_drifted_interior_lines` | !/usr/bin/env python3 |
| [`test_guide_marks.py`](test_guide_marks.py) | [`test_guide_marks.pyi`](test_guide_marks.pyi) | `test_residue_count_in_expected_band_for_k_squares`, `test_residue_count_zero_on_clean_image` | !/usr/bin/env python3 |
| [`test_scale_consistency.py`](test_scale_consistency.py) | [`test_scale_consistency.pyi`](test_scale_consistency.pyi) | `test_content_extent_oblique_matches_bbox_extent`, `test_content_extent_top_zero_dim_uses_min_thick`, `test_content_extent_cardinal_ns_folds_top`, `test_panel_fit_scale_matches_legacy_fit_scale`, `test_draw_iso_panel_accepts_forced_scale_and_returns_bbox` | !/usr/bin/env python3 |
| [`test_scene_manifest_kit_meta.py`](test_scene_manifest_kit_meta.py) | [`test_scene_manifest_kit_meta.pyi`](test_scene_manifest_kit_meta.pyi) | `layout`, `metadata_only_kit_dir`, `test_load_kit_meta_reads_json_without_pngs`, `test_build_manifest_succeeds_against_metadata_only_kit` | !/usr/bin/env python3 |
| [`test_sheet_grid.py`](test_sheet_grid.py) | [`test_sheet_grid.pyi`](test_sheet_grid.pyi) | `test_detect_grid_matches_even_division_no_drift`, `test_strip_linework_removes_magenta_keeps_blob_body`, `test_strip_linework_keeps_interior_near_white_pixel` | !/usr/bin/env python3 |
| [`test_sheet_qc.py`](test_sheet_qc.py) | [`test_sheet_qc.pyi`](test_sheet_qc.pyi) | `test_silhouette_iou_identical_masks_near_one`, `test_silhouette_iou_disjoint_masks_low` | !/usr/bin/env python3 |
<!-- routing:end -->
