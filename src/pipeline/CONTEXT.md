# pipeline
> Guide rendering + kit assembly + Blender legacy. Spec: [../../SCENE-CREATION.md](../../SCENE-CREATION.md).
> Status tags: `[OBSOLETE-MESH]` = quarantined legacy (kept only as P-Kit fallback lane — don't extend, don't delete without a cleanup loop). `guide_marks.py`/`scene_anchors.py` = **PARKED at scene scale** (single-pass scene generation killed 2026-07-08); still live at tile/kit-sheet scale.
> Known scale caveat: `tile_guide_render.py::fit_scale` autofits per cell — cross-view px-per-voxel drifts; fix spec'd in SCENE-CREATION.md § Scale-consistency (program P3).

<!-- routing:start -->
## Routing

| Subdirectory | Description |
|--------------|-------------|
| [`prompts/`](prompts/CONTEXT.md) | — |

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`blender_camera.py`](blender_camera.py) | [`blender_camera.pyi`](blender_camera.pyi) | `get_or_create_origin_target`, `create_iso_camera` | [OBSOLETE-MESH] blender_camera.py — Isometric orthographic camera + target-empty creation for blender_iso_rig. |
| [`blender_fbx_import.py`](blender_fbx_import.py) | [`blender_fbx_import.pyi`](blender_fbx_import.pyi) | `import_fbx`, `report` | [OBSOLETE-MESH] blender_fbx_import.py — Mixamo FBX import, normalization, and lighting for blender_iso_rig. |
| [`blender_iso_rig.py`](blender_iso_rig.py) | [`blender_iso_rig.pyi`](blender_iso_rig.pyi) | `parse_args`, `main` | [OBSOLETE-MESH] blender_iso_rig.py — Isometric camera rig for isoroll asset rendering. |
| [`blender_materials.py`](blender_materials.py) | [`blender_materials.pyi`](blender_materials.pyi) | `mesh_z_range`, `mesh_x_range`, `apply_character_materials`, `apply_uv_texture`, `apply_solid_material` | [OBSOLETE-MESH] blender_materials.py — Zone-color and UV-texture materials for blender_iso_rig. |
| [`blender_render.py`](blender_render.py) | [`blender_render.pyi`](blender_render.pyi) | `render_all` | [OBSOLETE-MESH] blender_render.py — Main per-direction, per-frame render loop for blender_iso_rig. |
| [`blender_scene_setup.py`](blender_scene_setup.py) | [`blender_scene_setup.pyi`](blender_scene_setup.pyi) | `setup_render`, `setup_depth_compositor` | [OBSOLETE-MESH] blender_scene_setup.py — Render engine and depth-compositor setup for blender_iso_rig. |
| [`calibrate2.py`](calibrate2.py) | [`calibrate2.pyi`](calibrate2.pyi) | `parse_args`, `setup`, `load_fbx`, `render_one`, `main` | [OBSOLETE-MESH] calibrate2.py — Focused sweep: scale 0.02-0.06, z -0.10 to +0.05, all 4 cardinal views. |
| [`calibrate3.py`](calibrate3.py) | [`calibrate3.pyi`](calibrate3.pyi) | `parse_args`, `load_fbx`, `render_one`, `main`, `report` | [OBSOLETE-MESH] calibrate3.py — Sweep camera Z translation at fixed scale=0.020, no constraint rotation. |
| [`calibrate4.py`](calibrate4.py) | [`calibrate4.pyi`](calibrate4.pyi) | `parse_args`, `load_fbx`, `render_one`, `main`, `report` | [OBSOLETE-MESH] calibrate4.py — Sweep camera shift_y (vertical pan) and ortho_scale (size). |
| [`calibrate_camera.py`](calibrate_camera.py) | [`calibrate_camera.pyi`](calibrate_camera.pyi) | `parse_args`, `import_fbx`, `apply_solid_material`, `setup_scene`, `make_camera` | [OBSOLETE-MESH] calibrate_camera.py — Batch render to find correct ortho_scale + frame_center_z. |
| [`enclosure_masks.py`](enclosure_masks.py) | [`enclosure_masks.pyi`](enclosure_masks.pyi) | `composite_enclosure`, `save_enclosure_masks` | !/usr/bin/env python3 |
| [`face_edges.py`](face_edges.py) | [`face_edges.pyi`](face_edges.pyi) | `stroke_edges`, `edge_width`, `draw_face_edges` | !/usr/bin/env python3 |
| [`face_masks.py`](face_masks.py) | [`face_masks.pyi`](face_masks.pyi) | `face_mask`, `save_mask` | !/usr/bin/env python3 |
| [`face_project.py`](face_project.py) | [`face_project.pyi`](face_project.pyi) | `panel_family`, `yaw_deg`, `panel_cam`, `ordered_front_faces`, `ordered_faces` | ← add first-line comment |
| [`generate_sheet_template.py`](generate_sheet_template.py) | [`generate_sheet_template.pyi`](generate_sheet_template.pyi) | `load_font`, `total_size`, `cell_origin`, `generate` | !/usr/bin/env python3 |
| [`guide_marks.py`](guide_marks.py) | [`guide_marks.pyi`](guide_marks.pyi) | `MarkParams`, `apply_marks`, `residue_count`, `tile_panels`, `main` | guide_marks.py — registration-mark post-pass over guide sheets (muralist technique, A/B parameterized). |
| [`kit_arm_a.py`](kit_arm_a.py) | [`kit_arm_a.pyi`](kit_arm_a.pyi) | `piece_specs`, `shared_px_per_voxel`, `render_piece`, `build_kit`, `build_all` | ← add first-line comment |
| [`kit_assets.py`](kit_assets.py) | [`kit_assets.pyi`](kit_assets.pyi) | `candidates`, `resolve`, `asset_name` | ← add first-line comment |
| [`kit_module_render.py`](kit_module_render.py) | [`kit_module_render.pyi`](kit_module_render.pyi) | `panel_extent`, `shared_scale`, `render_panel`, `render_module`, `enclosure_faces` | !/usr/bin/env python3 |
| [`kit_modules.py`](kit_modules.py) | [`kit_modules.pyi`](kit_modules.pyi) | — | !/usr/bin/env python3 |
| [`kit_modules_face.py`](kit_modules_face.py) | [`kit_modules_face.pyi`](kit_modules_face.pyi) | `Face`, `extrude`, `from_boxes` | ← add first-line comment |
| [`kit_modules_stair.py`](kit_modules_stair.py) | [`kit_modules_stair.pyi`](kit_modules_stair.pyi) | `cover`, `stair_45`, `stair_half` | ← add first-line comment |
| [`kit_render.py`](kit_render.py) | [`kit_render.pyi`](kit_render.pyi) | `piece_boxes`, `render_piece`, `build_kit` | kit_render.py — camera-fixed guide kit: one sprite per piece type (wall/door/window/floor) + alignment manifest. |
| [`layout_dsl_v2.py`](layout_dsl_v2.py) | [`layout_dsl_v2.pyi`](layout_dsl_v2.pyi) | `parse_text_v2`, `cell` | !/usr/bin/env python3 |
| [`layout_groups.py`](layout_groups.py) | [`layout_groups.pyi`](layout_groups.pyi) | `diag_solid`, `grp_base_data`, `grp_cell_voxels`, `solid`, `h_at` | !/usr/bin/env python3 |
| [`layout_massing.py`](layout_massing.py) | [`layout_massing.pyi`](layout_massing.pyi) | `Opening`, `Box`, `massing` | layout_massing.py — Layout grid → box list: merged wall runs with openings, floor strips, stair steps. |
| [`layout_material.py`](layout_material.py) | [`layout_material.pyi`](layout_material.pyi) | `cell_material`, `wall_material`, `level_attrs` | ← add first-line comment |
| [`layout_parse.py`](layout_parse.py) | [`layout_parse.pyi`](layout_parse.pyi) | `Level`, `Group`, `Layout`, `rotate_cw`, `rotate_point` | layout_parse.py — text-grid scene layout DSL → validated Layout model (F1 input). |
| [`layout_rotate.py`](layout_rotate.py) | [`layout_rotate.pyi`](layout_rotate.pyi) | `rotate_arrow`, `rotate_grid_cw`, `rotate_cells`, `rotate_attrs` | ← add first-line comment |
| [`layout_serialize.py`](layout_serialize.py) | [`layout_serialize.pyi`](layout_serialize.pyi) | `to_dsl` | !/usr/bin/env python3 |
| [`linework.py`](linework.py) | [`linework.pyi`](linework.pyi) | `floor_stone`, `wall_wood_side`, `wall_wood_top`, `wall_stone_side`, `wall_stone_top` | !/usr/bin/env python3 |
| [`linework_doors.py`](linework_doors.py) | [`linework_doors.pyi`](linework_doors.pyi) | `door` | !/usr/bin/env python3 |
| [`linework_extra.py`](linework_extra.py) | [`linework_extra.pyi`](linework_extra.pyi) | `floor_wood`, `roof_shingle`, `stair_tread`, `stair_riser`, `grass` | !/usr/bin/env python3 |
| [`make_tile_guide.py`](make_tile_guide.py) | [`make_tile_guide.pyi`](make_tile_guide.pyi) | `generate` | !/usr/bin/env python3 |
| [`paint_faces.py`](paint_faces.py) | [`paint_faces.pyi`](paint_faces.pyi) | `texture_png`, `paint_panel` | ← add first-line comment |
| [`panel_geometry.py`](panel_geometry.py) | [`panel_geometry.pyi`](panel_geometry.pyi) | `fit_scale`, `content_extent`, `panel_fit_scale` | !/usr/bin/env python3 |
| [`preprocess.py`](preprocess.py) | [`preprocess.pyi`](preprocess.pyi) | `remove_background`, `resize_with_padding`, `find_content_root`, `main` | preprocess.py — Step 1 of the art pipeline: background removal + resize for concept art. |
| [`render_iso.py`](render_iso.py) | [`render_iso.pyi`](render_iso.pyi) | `parse_args`, `load_fbx`, `render_one`, `main`, `report` | [OBSOLETE-MESH] render_iso.py — Isometric sprite render (all 8 directions, fixed config). |
| [`render_scene.py`](render_scene.py) | [`render_scene.pyi`](render_scene.pyi) | `kit_dir_for`, `render_scene`, `render_image`, `bake`, `build_kits` | ← add first-line comment |
| [`rotate_mesh.py`](rotate_mesh.py) | [`rotate_mesh.pyi`](rotate_mesh.pyi) | `rotate_y`, `rotate_axis`, `main` | !/usr/bin/env python3 |
| [`run_anatomy_test.py`](run_anatomy_test.py) | [`run_anatomy_test.pyi`](run_anatomy_test.pyi) | `load_workflow`, `submit`, `wait_for_output`, `main` | run_anatomy_test.py — bare-hands anatomy test: dreamshaper, toonyou, lyriel |
| [`run_model_comparison.py`](run_model_comparison.py) | [`run_model_comparison.pyi`](run_model_comparison.pyi) | `load_workflow`, `submit`, `wait_for_output`, `main` | run_model_comparison.py — generates one image per checkpoint, saves to benchmarks/model-comparison/ |
| [`s3_batch.sh`](s3_batch.sh) | — | — | ← add first-line comment |
| [`scene_anchors.py`](scene_anchors.py) | [`scene_anchors.pyi`](scene_anchors.pyi) | `anchors`, `project`, `apply_anchored` | scene_anchors.py — stable 3D anchors on layout geometry, projected per view; attached registration marks. |
| [`scene_assemble.py`](scene_assemble.py) | [`scene_assemble.pyi`](scene_assemble.pyi) | `piece_of`, `load_kit_meta`, `load_kit`, `paint_key`, `assemble` | scene_assemble.py — tinyglade-style deterministic assembly: kit sprites pasted per cell in painter order. |
| [`scene_guide_render.py`](scene_guide_render.py) | [`scene_guide_render.pyi`](scene_guide_render.pyi) | `Cam`, `scene_cam`, `render_boxes`, `render_scene_panel`, `render_plan_panel` | scene_guide_render.py — one guide panel of a whole scene: dimetric view of the massing boxes, or TOP plan. |
| [`scene_guide_sheet.py`](scene_guide_sheet.py) | [`scene_guide_sheet.pyi`](scene_guide_sheet.pyi) | `compose_sheet`, `main` | scene_guide_sheet.py — compose the 6-cell NB scene-guide sheet (views + plan + caption + marks) and CLI. |
| [`scene_manifest.py`](scene_manifest.py) | [`scene_manifest.pyi`](scene_manifest.pyi) | `build_manifest`, `count_hud` | !/usr/bin/env python3 |
| [`scene_plan.py`](scene_plan.py) | [`scene_plan.pyi`](scene_plan.pyi) | `plan`, `sizes_of` | ← add first-line comment |
| [`sheet_to_tpose.py`](sheet_to_tpose.py) | [`sheet_to_tpose.pyi`](sheet_to_tpose.pyi) | `cell_box`, `extract` | !/usr/bin/env python3 |
| [`stage_kit_modules.py`](stage_kit_modules.py) | [`stage_kit_modules.pyi`](stage_kit_modules.pyi) | `sheet_grid`, `arm_b`, `arm_bc`, `arm_a`, `stage` | !/usr/bin/env python3 |
| [`texture_map.py`](texture_map.py) | [`texture_map.pyi`](texture_map.pyi) | `load_textures`, `FAMILY`, `variant`, `face_texture`, `texture_png_path` | !/usr/bin/env python3 |
| [`texture_resample.py`](texture_resample.py) | [`texture_resample.pyi`](texture_resample.pyi) | `tile_source`, `match_source_density`, `supersample_transform` | !/usr/bin/env python3 |
| [`texture_warp.py`](texture_warp.py) | [`texture_warp.pyi`](texture_warp.pyi) | `face_axes`, `warp_tiling`, `warp_decal` | !/usr/bin/env python3 |
| [`tile_guide_matrix.py`](tile_guide_matrix.py) | [`tile_guide_matrix.pyi`](tile_guide_matrix.pyi) | `CellSpec`, `draw_panel`, `draw_caption`, `parse_spec`, `render_cells` | !/usr/bin/env python3 |
| [`tile_guide_render.py`](tile_guide_render.py) | [`tile_guide_render.pyi`](tile_guide_render.pyi) | `draw_iso_panel`, `draw_square_grid`, `draw_flat_grid`, `row_y` | tile_guide_render.py — dimetric box-face geometry and single-panel drawing for tile guides. |
| [`triposr_mesh.py`](triposr_mesh.py) | [`triposr_mesh.pyi`](triposr_mesh.pyi) | `parse_args`, `main` | [OBSOLETE-MESH] triposr_mesh.py — Generate a 3D mesh from a single concept image using TripoSR. |
| [`view_table.py`](view_table.py) | [`view_table.pyi`](view_table.pyi) | `family`, `turns`, `matrix`, `cull_axis`, `project` | ← add first-line comment |
<!-- routing:end -->
