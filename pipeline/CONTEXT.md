# pipeline
> ← add description

<!-- routing:start -->
## Routing

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`blender_iso_rig.py`](blender_iso_rig.py) | — | `parse_args`, `setup_render`, `setup_depth_compositor`, `apply_character_materials`, `apply_uv_texture` | ← add first-line comment |
| [`calibrate2.py`](calibrate2.py) | [`calibrate2.pyi`](calibrate2.pyi) | `parse_args`, `setup`, `load_fbx`, `render_one`, `main` | [OBSOLETE-MESH] calibrate2.py — Focused sweep: scale 0.02-0.06, z -0.10 to +0.05, all 4 cardinal views. |
| [`calibrate3.py`](calibrate3.py) | [`calibrate3.pyi`](calibrate3.pyi) | `parse_args`, `load_fbx`, `render_one`, `main`, `report` | ← add first-line comment |
| [`calibrate4.py`](calibrate4.py) | [`calibrate4.pyi`](calibrate4.pyi) | `parse_args`, `load_fbx`, `render_one`, `main`, `report` | ← add first-line comment |
| [`calibrate_camera.py`](calibrate_camera.py) | [`calibrate_camera.pyi`](calibrate_camera.pyi) | `parse_args`, `import_fbx`, `apply_solid_material`, `setup_scene`, `make_camera` | ← add first-line comment |
| [`generate_sheet_template.py`](generate_sheet_template.py) | [`generate_sheet_template.pyi`](generate_sheet_template.pyi) | `load_font`, `total_size`, `cell_origin`, `generate` | !/usr/bin/env python3 |
| [`make_tile_guide.py`](make_tile_guide.py) | [`make_tile_guide.pyi`](make_tile_guide.pyi) | `generate` | !/usr/bin/env python3 |
| [`preprocess.py`](preprocess.py) | [`preprocess.pyi`](preprocess.pyi) | `remove_background`, `resize_with_padding`, `find_content_root`, `main` | ← add first-line comment |
| [`prompts/concept_art_prompt.md`](prompts/concept_art_prompt.md) | — | — | Phase 1 — Concept Art Prompt |
| [`prompts/sheet_prompt.md`](prompts/sheet_prompt.md) | — | — | Phase 2 — Character Sheet Prompt |
| [`render_iso.py`](render_iso.py) | [`render_iso.pyi`](render_iso.pyi) | `parse_args`, `apply_uv_texture`, `load_fbx`, `render_one`, `main` | [OBSOLETE-MESH] render_iso.py — Isometric sprite render (all 8 directions, fixed config). |
| [`rotate_mesh.py`](rotate_mesh.py) | [`rotate_mesh.pyi`](rotate_mesh.pyi) | `rotate_y`, `rotate_axis`, `main` | !/usr/bin/env python3 |
| [`sheet_to_tpose.py`](sheet_to_tpose.py) | [`sheet_to_tpose.pyi`](sheet_to_tpose.pyi) | `cell_box`, `extract` | !/usr/bin/env python3 |
| [`tile_guide_render.py`](tile_guide_render.py) | [`tile_guide_render.pyi`](tile_guide_render.pyi) | `fit_scale`, `draw_iso_panel`, `draw_flat_grid`, `tr`, `scr` | !/usr/bin/env python3 |
| [`triposr_mesh.py`](triposr_mesh.py) | [`triposr_mesh.pyi`](triposr_mesh.pyi) | `parse_args`, `main` | ← add first-line comment |
<!-- routing:end -->
