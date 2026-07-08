# cli
> `iso-cli.py` entry point — submits ComfyUI API workflows for character generation, styling, and post-processing

<!-- routing:start -->
## Routing

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`blender_commands.py`](blender_commands.py) | [`blender_commands.pyi`](blender_commands.pyi) | `blender_stylize`, `blender_ipadapter` | blender_commands.py — Blender render stylization commands: Path A and Path A+B hybrid. |
| [`comfy_client.py`](comfy_client.py) | [`comfy_client.pyi`](comfy_client.pyi) | `get_comfy_dir`, `get_output_dir`, `upload_image`, `send_prompt`, `snapshot_pngs` | ComfyUI API client helpers for the isoroll pipeline. |
| [`gen_commands.py`](gen_commands.py) | [`gen_commands.pyi`](gen_commands.pyi) | `gen_character`, `style_concept`, `ipadapter_ref` | gen_commands.py — Generation commands: txt2img, style-concept, IP-Adapter ref. |
| [`image_commands.py`](image_commands.py) | [`image_commands.pyi`](image_commands.pyi) | `detail_image`, `face_restore` | image_commands.py — Image processing commands: upscale, rembg, face restore. |
| [`imagegen_client.py`](imagegen_client.py) | — | `generate`, `drop_manual`, `collect_manual` | !/usr/bin/env python3 |
| [`iso-cli.py`](iso-cli.py) | [`iso-cli.pyi`](iso-cli.pyi) | `get_arg`, `main` | iso-cli — isoroll content pipeline CLI. Run with -h for usage. |
| [`multiview_commands.py`](multiview_commands.py) | [`multiview_commands.pyi`](multiview_commands.pyi) | `run_mv_command` | !/usr/bin/env python3 |
| [`sheet_grid.py`](sheet_grid.py) | [`sheet_grid.pyi`](sheet_grid.pyi) | `magenta_mask`, `white_mask`, `line_mask`, `detect_boundaries`, `detect_grid` | !/usr/bin/env python3 |
| [`sheet_postproc.py`](sheet_postproc.py) | [`sheet_postproc.pyi`](sheet_postproc.pyi) | `parse_watermark_region`, `parse_args`, `run`, `main` | !/usr/bin/env python3 |
| [`sheet_qc.py`](sheet_qc.py) | [`sheet_qc.pyi`](sheet_qc.pyi) | `silhouette_mask`, `mask_iou`, `silhouette_iou` | !/usr/bin/env python3 |
| [`sheet_utils.py`](sheet_utils.py) | [`sheet_utils.pyi`](sheet_utils.pyi) | `SheetLayout`, `load_image`, `split_cells`, `even_boundaries`, `split_grid` | !/usr/bin/env python3 |
| [`sprite_splitter.py`](sprite_splitter.py) | [`sprite_splitter.pyi`](sprite_splitter.pyi) | `parse_args`, `split_sheet`, `remove_bg`, `next_index`, `main` | !/usr/bin/env python3 |
| [`workflow_ops.py`](workflow_ops.py) | [`workflow_ops.pyi`](workflow_ops.pyi) | `apply_random_seeds`, `inject_prompt`, `inject_input_image`, `inject_concept_image`, `set_base_denoise` | workflow_ops.py — Workflow mutation helpers for the isoroll ComfyUI pipeline. |
<!-- routing:end -->
