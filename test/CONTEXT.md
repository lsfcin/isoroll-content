# test
> ← add description

<!-- routing:start -->
## Routing

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`conftest.py`](conftest.py) | [`conftest.pyi`](conftest.pyi) | — | conftest.py — pytest path bootstrap: make src/cli and src/pipeline modules importable. |
| [`e2e_export_manifest.py`](e2e_export_manifest.py) | [`e2e_export_manifest.pyi`](e2e_export_manifest.pyi) | `run_cli`, `main` | !/usr/bin/env python3 |
| [`e2e_scale_consistency.py`](e2e_scale_consistency.py) | [`e2e_scale_consistency.pyi`](e2e_scale_consistency.pyi) | `run_cli`, `main` | !/usr/bin/env python3 |
| [`e2e_scenario.py`](e2e_scenario.py) | [`e2e_scenario.pyi`](e2e_scenario.pyi) | `run_cli`, `recolor_preserve_silhouette`, `inject_residue`, `main` | !/usr/bin/env python3 |
| [`fixtures.py`](fixtures.py) | [`fixtures.pyi`](fixtures.pyi) | `magenta_grid_sheet`, `cyan_squares`, `clean_image`, `filled_mask`, `alpha_blob` | fixtures.py — synthetic PIL image builders shared by the postproc test suite. |
| [`test_arm_a_texture.py`](test_arm_a_texture.py) | [`test_arm_a_texture.pyi`](test_arm_a_texture.pyi) | — | !/usr/bin/env python3 |
| [`test_cabin_golden.py`](test_cabin_golden.py) | [`test_cabin_golden.pyi`](test_cabin_golden.pyi) | `cabin`, `kit_root` | ← add first-line comment |
| [`test_dsl_v2_manifest.py`](test_dsl_v2_manifest.py) | [`test_dsl_v2_manifest.pyi`](test_dsl_v2_manifest.pyi) | — | !/usr/bin/env python3 |
| [`test_dsl_v2_massing.py`](test_dsl_v2_massing.py) | [`test_dsl_v2_massing.pyi`](test_dsl_v2_massing.pyi) | — | !/usr/bin/env python3 |
| [`test_dsl_v2_parse.py`](test_dsl_v2_parse.py) | [`test_dsl_v2_parse.pyi`](test_dsl_v2_parse.pyi) | — | !/usr/bin/env python3 |
| [`test_dsl_v2_render.py`](test_dsl_v2_render.py) | [`test_dsl_v2_render.pyi`](test_dsl_v2_render.pyi) | — | !/usr/bin/env python3 |
| [`test_dsl_v2_serialize.py`](test_dsl_v2_serialize.py) | [`test_dsl_v2_serialize.pyi`](test_dsl_v2_serialize.pyi) | — | !/usr/bin/env python3 |
| [`test_enclosure_masks.py`](test_enclosure_masks.py) | [`test_enclosure_masks.pyi`](test_enclosure_masks.pyi) | — | !/usr/bin/env python3 |
| [`test_export_manifest.py`](test_export_manifest.py) | [`test_export_manifest.pyi`](test_export_manifest.pyi) | `layout`, `manifest` | !/usr/bin/env python3 |
| [`test_face_edges.py`](test_face_edges.py) | [`test_face_edges.pyi`](test_face_edges.pyi) | — | !/usr/bin/env python3 |
| [`test_face_project.py`](test_face_project.py) | [`test_face_project.pyi`](test_face_project.pyi) | — | ← add first-line comment |
| [`test_grid_drift.py`](test_grid_drift.py) | [`test_grid_drift.pyi`](test_grid_drift.pyi) | — | test_grid_drift.py — detect_grid tolerates +-2px grid-line drift (C4). |
| [`test_guide_marks.py`](test_guide_marks.py) | [`test_guide_marks.pyi`](test_guide_marks.pyi) | — | test_guide_marks.py — residue_count on synthetic cyan-mark fixtures (C2). |
| [`test_kit_module_render.py`](test_kit_module_render.py) | [`test_kit_module_render.pyi`](test_kit_module_render.pyi) | — | !/usr/bin/env python3 |
| [`test_kit_modules.py`](test_kit_modules.py) | [`test_kit_modules.pyi`](test_kit_modules.pyi) | `zspan`, `max_z` | !/usr/bin/env python3 |
| [`test_layout_rotate.py`](test_layout_rotate.py) | [`test_layout_rotate.pyi`](test_layout_rotate.pyi) | — | ← add first-line comment |
| [`test_linework.py`](test_linework.py) | [`test_linework.pyi`](test_linework.pyi) | — | ← add first-line comment |
| [`test_scale_consistency.py`](test_scale_consistency.py) | [`test_scale_consistency.pyi`](test_scale_consistency.pyi) | — | !/usr/bin/env python3 |
| [`test_scene_manifest_kit_meta.py`](test_scene_manifest_kit_meta.py) | [`test_scene_manifest_kit_meta.pyi`](test_scene_manifest_kit_meta.pyi) | `layout`, `metadata_only_kit_dir` | !/usr/bin/env python3 |
| [`test_sheet_grid.py`](test_sheet_grid.py) | [`test_sheet_grid.pyi`](test_sheet_grid.pyi) | — | test_sheet_grid.py — detect_grid + strip_linework on synthetic magenta-grid fixtures (C1). |
| [`test_sheet_qc.py`](test_sheet_qc.py) | [`test_sheet_qc.pyi`](test_sheet_qc.pyi) | — | test_sheet_qc.py — silhouette_iou unit tests (C3). |
| [`test_stage_kit_modules.py`](test_stage_kit_modules.py) | [`test_stage_kit_modules.pyi`](test_stage_kit_modules.pyi) | — | !/usr/bin/env python3 |
| [`test_texture_map.py`](test_texture_map.py) | [`test_texture_map.pyi`](test_texture_map.pyi) | — | !/usr/bin/env python3 |
| [`test_texture_map_slab.py`](test_texture_map_slab.py) | [`test_texture_map_slab.pyi`](test_texture_map_slab.pyi) | — | !/usr/bin/env python3 |
| [`test_texture_warp.py`](test_texture_warp.py) | [`test_texture_warp.pyi`](test_texture_warp.pyi) | — | !/usr/bin/env python3 |
| [`test_view_table.py`](test_view_table.py) | [`test_view_table.pyi`](test_view_table.pyi) | — | ← add first-line comment |
<!-- routing:end -->
