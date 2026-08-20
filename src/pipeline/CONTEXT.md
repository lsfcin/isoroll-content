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
| [`enclosure_masks.py`](enclosure_masks.py) | [`enclosure_masks.pyi`](enclosure_masks.pyi) | `composite_enclosure`, `save_enclosure_masks` | enclosure_masks.py — one `enclosure` mask per module+view = the wall-fill |
| [`face_edges.py`](face_edges.py) | [`face_edges.pyi`](face_edges.pyi) | `stroke_edges`, `edge_width`, `draw_face_edges` | face_edges.py — thin dark ink edge lines along face-polygon boundaries |
| [`face_masks.py`](face_masks.py) | [`face_masks.pyi`](face_masks.pyi) | `face_mask`, `save_mask` | face_masks.py — id-indexed occlusion masks from the SAME ordered faces |
| [`face_project.py`](face_project.py) | [`face_project.pyi`](face_project.pyi) | `panel_family`, `yaw_deg`, `panel_cam`, `ordered_front_faces`, `ordered_faces` | face_project.py — the projected-face seam: yaw a module's faces, project them through a camera |
| [`generate_sheet_template.py`](generate_sheet_template.py) | [`generate_sheet_template.pyi`](generate_sheet_template.pyi) | `load_font`, `total_size`, `cell_origin`, `generate` | generate_sheet_template.py — Generate the character sheet template PNG. |
| [`guide_marks.py`](guide_marks.py) | [`guide_marks.pyi`](guide_marks.pyi) | `MarkParams`, `apply_marks`, `residue_count`, `tile_panels`, `main` | guide_marks.py — registration-mark post-pass over guide sheets (muralist technique, A/B parameterized). |
| [`kit_arm_a.py`](kit_arm_a.py) | [`kit_arm_a.pyi`](kit_arm_a.pyi) | `piece_specs`, `shared_px_per_voxel`, `render_piece`, `build_kit`, `build_all` | kit_arm_a.py — arm A's cell sprites: one textured sprite per assembly piece, per camera family. |
| [`kit_assets.py`](kit_assets.py) | [`kit_assets.pyi`](kit_assets.pyi) | `candidates`, `resolve`, `asset_name` | kit_assets.py — resolve a tile's sprite name against whatever kit is in play. |
| [`kit_module_render.py`](kit_module_render.py) | [`kit_module_render.pyi`](kit_module_render.pyi) | `panel_extent`, `shared_scale`, `render_panel`, `render_module`, `enclosure_faces` | kit_module_render.py — flat panel render + one shared px-per-voxel scale across a sheet (T2/T3). |
| [`kit_modules.py`](kit_modules.py) | [`kit_modules.pyi`](kit_modules.pyi) | — | kit_modules.py — the KIT V2 module catalogue: one builder per piece, at world origin (T1). |
| [`kit_modules_face.py`](kit_modules_face.py) | [`kit_modules_face.pyi`](kit_modules_face.pyi) | `Face`, `extrude`, `from_boxes` | kit_modules_face.py — what a kit face IS, and the two ways to build one. |
| [`kit_modules_stair.py`](kit_modules_stair.py) | [`kit_modules_stair.pyi`](kit_modules_stair.pyi) | `cover`, `stair_45`, `stair_half` | kit_modules_stair.py — the stair module's zigzag solid, as faces at world origin. |
| [`kit_render.py`](kit_render.py) | [`kit_render.pyi`](kit_render.pyi) | `piece_boxes`, `render_piece`, `build_kit` | kit_render.py — camera-fixed guide kit: one sprite per piece type (wall/door/window/floor) + alignment manifest. |
| [`layout_dsl_v2.py`](layout_dsl_v2.py) | [`layout_dsl_v2.pyi`](layout_dsl_v2.pyi) | `parse_text_v2` | layout_dsl_v2.py — v2 grammar: "level N:"/"layer X:"/"roof:"/"stair:" blocks -> Layout. |
| [`layout_groups.py`](layout_groups.py) | [`layout_groups.pyi`](layout_groups.pyi) | `diag_solid`, `grp_base_data`, `grp_cell_voxels` | layout_groups.py — pure geometry helpers for sloped-surface GROUPS (roofs/stairs), ported from |
| [`layout_massing.py`](layout_massing.py) | [`layout_massing.pyi`](layout_massing.pyi) | `Opening`, `Box`, `massing` | layout_massing.py — Layout grid → box list: merged wall runs with openings, floor strips, stair steps. |
| [`layout_material.py`](layout_material.py) | [`layout_material.pyi`](layout_material.pyi) | `cell_material`, `wall_material`, `level_attrs` | layout_material.py — which material a cell is made of, per the v2 attr overlays. |
| [`layout_parse.py`](layout_parse.py) | [`layout_parse.pyi`](layout_parse.pyi) | `Level`, `Group`, `Layout`, `rotate_cw`, `rotate_point` | layout_parse.py — text-grid scene layout DSL → validated Layout model (F1 input). |
| [`layout_rotate.py`](layout_rotate.py) | [`layout_rotate.pyi`](layout_rotate.pyi) | `rotate_arrow`, `rotate_grid_cw`, `rotate_cells`, `rotate_attrs` | layout_rotate.py — clockwise grid rotation primitives, on plain data (no Layout dataclasses, so |
| [`layout_serialize.py`](layout_serialize.py) | [`layout_serialize.pyi`](layout_serialize.pyi) | `to_dsl` | layout_serialize.py — Layout -> canonical DSL v2 text, ported from rig.frag updateDsl (L1088-1119). |
| [`layouts/cabin.txt`](layouts/cabin.txt) | — | — | ← add first-line comment |
| [`layouts/l-room.txt`](layouts/l-room.txt) | — | — | ← add first-line comment |
| [`layouts/one-cell.txt`](layouts/one-cell.txt) | — | — | ← add first-line comment |
| [`layouts/open-room.txt`](layouts/open-room.txt) | — | — | ← add first-line comment |
| [`linework.py`](linework.py) | [`linework.pyi`](linework.pyi) | `floor_stone`, `wall_wood_side`, `wall_wood_top`, `wall_stone_side`, `wall_stone_top` | linework.py — seeded SVG texture generator in the technical-linework |
| [`linework_doors.py`](linework_doors.py) | [`linework_doors.pyi`](linework_doors.pyi) | `door` | linework_doors.py — door decals for the /linework set (Lucas's door-sheet |
| [`linework_extra.py`](linework_extra.py) | [`linework_extra.pyi`](linework_extra.pyi) | `floor_wood`, `roof_shingle`, `stair_tread`, `stair_riser`, `grass` | linework_extra.py — remaining painter-vocabulary materials for /linework: |
| [`make_tile_guide.py`](make_tile_guide.py) | [`make_tile_guide.pyi`](make_tile_guide.pyi) | `generate` | make_tile_guide.py — Generate the color-coded multiview schematic guide for a wall tile (S0-E1). |
| [`paint_faces.py`](paint_faces.py) | [`paint_faces.pyi`](paint_faces.pyi) | `texture_png`, `paint_panel` | paint_faces.py — arm A's painter: warp real textures onto one panel's ordered face quads. |
| [`panel_geometry.py`](panel_geometry.py) | [`panel_geometry.pyi`](panel_geometry.pyi) | `fit_scale`, `content_extent`, `panel_fit_scale` | panel_geometry.py — pure dimetric/orthographic geometry math shared by |
| [`preprocess.py`](preprocess.py) | [`preprocess.pyi`](preprocess.pyi) | `remove_background`, `resize_with_padding`, `find_content_root`, `main` | preprocess.py — Step 1 of the art pipeline: background removal + resize for concept art. |
| [`render_iso.py`](render_iso.py) | [`render_iso.pyi`](render_iso.pyi) | `parse_args`, `load_fbx`, `render_one`, `main`, `report` | [OBSOLETE-MESH] render_iso.py — Isometric sprite render (all 8 directions, fixed config). |
| [`render_scene.py`](render_scene.py) | [`render_scene.pyi`](render_scene.pyi) | `kit_dir_for`, `render_scene`, `render_image`, `bake`, `build_kits` | render_scene.py — THE SEAM. `render_scene(layout, view) -> {cell sprites, manifest}`. |
| [`rotate_mesh.py`](rotate_mesh.py) | [`rotate_mesh.pyi`](rotate_mesh.pyi) | `rotate_y`, `rotate_axis`, `main` | [OBSOLETE-MESH] |
| [`run_anatomy_test.py`](run_anatomy_test.py) | [`run_anatomy_test.pyi`](run_anatomy_test.pyi) | `load_workflow`, `submit`, `wait_for_output`, `main` | run_anatomy_test.py — bare-hands anatomy test: dreamshaper, toonyou, lyriel |
| [`run_model_comparison.py`](run_model_comparison.py) | [`run_model_comparison.pyi`](run_model_comparison.pyi) | `load_workflow`, `submit`, `wait_for_output`, `main` | run_model_comparison.py — generates one image per checkpoint, saves to benchmarks/model-comparison/ |
| [`s3_batch.sh`](s3_batch.sh) | — | — | [OBSOLETE-MESH] s3_batch.sh — S3 full pipeline: TripoSR mesh → Blender renders → ComfyUI style pass |
| [`scene_anchors.py`](scene_anchors.py) | [`scene_anchors.pyi`](scene_anchors.pyi) | `anchors`, `project`, `apply_anchored` | scene_anchors.py — stable 3D anchors on layout geometry, projected per view; attached registration marks. |
| [`scene_assemble.py`](scene_assemble.py) | [`scene_assemble.pyi`](scene_assemble.pyi) | `piece_of`, `load_kit_meta`, `load_kit`, `paint_key`, `assemble` | scene_assemble.py — tinyglade-style deterministic assembly: kit sprites pasted per cell in painter order. |
| [`scene_guide_render.py`](scene_guide_render.py) | [`scene_guide_render.pyi`](scene_guide_render.pyi) | `Cam`, `scene_cam`, `render_boxes`, `render_scene_panel`, `render_plan_panel` | scene_guide_render.py — one guide panel of a whole scene: dimetric view of the massing boxes, or TOP plan. |
| [`scene_guide_sheet.py`](scene_guide_sheet.py) | [`scene_guide_sheet.pyi`](scene_guide_sheet.pyi) | `compose_sheet`, `main` | scene_guide_sheet.py — compose the 6-cell NB scene-guide sheet (views + plan + caption + marks) and CLI. |
| [`scene_manifest.py`](scene_manifest.py) | [`scene_manifest.pyi`](scene_manifest.pyi) | `build_manifest`, `count_hud` | scene_manifest.py — build_manifest: layout + kit alignment → scene manifest dict. |
| [`scene_plan.py`](scene_plan.py) | [`scene_plan.pyi`](scene_plan.pyi) | `plan`, `sizes_of` | scene_plan.py — WHERE every sprite goes, as data. The parity ground truth. |
| [`sheet_to_tpose.py`](sheet_to_tpose.py) | [`sheet_to_tpose.pyi`](sheet_to_tpose.pyi) | `cell_box`, `extract` | sheet_to_tpose.py — Crop panels from a GPT-generated character sheet. |
| [`stage_kit_modules.py`](stage_kit_modules.py) | [`stage_kit_modules.pyi`](stage_kit_modules.pyi) | `sheet_grid`, `arm_b`, `arm_bc`, `arm_a`, `stage` | stage_kit_modules.py — compose one 5x2 sheet PER MODULE per arm |
| [`texture_map.py`](texture_map.py) | [`texture_map.pyi`](texture_map.pyi) | `load_textures`, `FAMILY`, `variant`, `face_texture`, `texture_png_path` | texture_map.py — face(kind,mat) -> texture FAMILY/variant lookup (T1, C2, |
| [`texture_resample.py`](texture_resample.py) | [`texture_resample.pyi`](texture_resample.pyi) | `tile_source`, `match_source_density`, `supersample_transform` | texture_resample.py — resampling/density policy for texture_warp.py (P2, |
| [`texture_warp.py`](texture_warp.py) | [`texture_warp.pyi`](texture_warp.pyi) | `face_axes`, `warp_tiling`, `warp_decal` | texture_warp.py — warp a texture PNG onto a projected face quad/tri (T2, |
| [`tile_guide_matrix.py`](tile_guide_matrix.py) | [`tile_guide_matrix.pyi`](tile_guide_matrix.pyi) | `CellSpec`, `draw_panel`, `draw_caption`, `parse_spec`, `render_cells` | tile_guide_matrix.py — generic per-cell orientation/dims tile guide matrix renderer. |
| [`tile_guide_render.py`](tile_guide_render.py) | [`tile_guide_render.pyi`](tile_guide_render.pyi) | `draw_iso_panel`, `draw_square_grid`, `draw_flat_grid` | tile_guide_render.py — dimetric box-face geometry and single-panel drawing for tile guides. |
| [`triposr_mesh.py`](triposr_mesh.py) | [`triposr_mesh.pyi`](triposr_mesh.pyi) | `parse_args`, `main` | [OBSOLETE-MESH] triposr_mesh.py — Generate a 3D mesh from a single concept image using TripoSR. |
| [`view_table.py`](view_table.py) | [`view_table.pyi`](view_table.pyi) | `family`, `turns`, `matrix`, `cull_axis`, `project` | view_table.py — the 8+1 view table: one entry per view (projection matrix + backface-cull axis). |
<!-- routing:end -->
