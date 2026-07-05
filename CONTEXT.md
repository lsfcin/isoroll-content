# isoroll-content
> Offline asset generation pipeline for the isoroll Foundry VTT module
> goal: [rpg-isoroll](../../brain/goals/rpg-isoroll.md)

isoroll-content is the art and pipeline side of the isoroll project. It produces 8-direction isometric sprites, tiles, and animations for the isoroll Foundry module.

The long-term product is two things:
1. A Foundry module for Hades-like isometric play: 8-direction sprites, height, partial or total occlusion, and visual sorting from 3D-style bounds. (→ see `isoroll-module` repo)
2. This offline asset pipeline: generates, refines, validates, and packages characters, tiles, animations, spell effects, and metadata for Foundry.

## Read Order

1. `CONTEXT.md`: onboarding and current intent.
2. `SPECS.md`: current files, code behavior, environment assumptions, and implementation rules.
3. `ROADMAP.md`: milestones and next tasks.
4. `.gitignore`: shows what is source versus generated output.

## Current Focus

The immediate work is `src/cli/iso-cli.py`, a small CLI that submits ComfyUI API workflows for character image generation.

The current generation baseline is:

- ComfyUI receives a workflow JSON through `/prompt`.
- `iso-cli.py` picks a workflow by profile name — filename selection only, no profile-JSON tuning layer (see SPECS.md `## Render Profiles`).
- The workflow handles the real node graph.
- Generated PNGs are gitignored under `assets/chars/`.
- Tracked reference outputs live directly in per-comparison folders under `benchmarks/` (each with its own `manifest.json` — see SPECS.md).

## Core Product Decisions

- Do not build a generic 3D runtime in Foundry.
- Do not globally skew the Foundry canvas as the main architecture.
- Keep runtime and asset generation separate.
- Aim for a Hades-like production model: controlled offline generation/rendering into 2D sprites, then efficient Foundry playback.
- Treat prompts as an input to a structured asset pipeline, not as the whole pipeline.
- Use ComfyUI as the local image-generation hub for now.
- Later, introduce Blender or another controlled renderer for consistent 8-direction and animation output.

## Repository Shape

```text
isoroll-content/
  .gitignore
  CONTEXT.md
  SPECS.md
  ROADMAP.md
  src/
    cli/
      iso-cli.py            # entry point — argument parsing + dispatch only
      iso-cli.bat
      comfy_client.py       # ComfyUI API primitives
      workflow_ops.py       # workflow-JSON mutation helpers
      gen_commands.py       # gen-character, style-concept, ipadapter-ref
      image_commands.py     # detail-image, face-restore
      blender_commands.py   # blender-stylize, blender-ipadapter
      sprite_splitter.py    # split external sprite sheets into per-direction files
      workflows/            # ComfyUI workflow JSONs
      batch_rembg.sh
      batch_stylize.sh
    pipeline/
      preprocess.py, sheet_to_tpose.py, generate_sheet_template.py  # concept/sheet intake
      make_tile_guide.py, tile_guide_render.py                      # S0 tile multiview guide (active)
      triposr_mesh.py, blender_iso_rig.py, rotate_mesh.py,
      calibrate2/3/4.py, calibrate_camera.py, s3_batch.sh           # S3 mesh pipeline — several
                                                                     # self-tagged [OBSOLETE-MESH],
                                                                     # not yet consolidated (see ROADMAP S3)
      prompts/
  assets/                # generated art output — see assets/CONTEXT.md
    chars/               # per-character outputs (gitignored)
      {name}/
        concept/
        sheet/
        {name}_{stance}_{facing}.png  # final sprites
        _renders/{stance}/            # intermediate renders (gitignored)
    tiles/               # tracked tile assets
      {name}/
        {name}_{facing}.png
  benchmarks/            # curated comparisons + tile-guide QC sweeps — see benchmarks/CONTEXT.md
```

## File Map

- `src/cli/iso-cli.py` — CLI entry point; submits ComfyUI API workflows; selects workflow by profile name
- `src/cli/workflows/` — named workflow variants (`character_fast`, `character_balanced`, `character_quality`, etc.)
- `src/cli/sprite_splitter.py` — splits external sprite sheets into per-direction flat files
- `src/pipeline/preprocess.py` — background removal + resize for concept art → `assets/{chars,tiles}/{name}/concept/`
- `src/pipeline/sheet_to_tpose.py` — crop GPT character sheet → panels in `assets/chars/{name}/sheet/`
- `benchmarks/` — each comparison folder carries its own `manifest.json` (see SPECS.md `## Benchmark Manifest`)

## Working Rules

- Keep source files portable. Do not commit local absolute ComfyUI paths.
- Use `COMFY_DIR` for the local ComfyUI root. `src/cli/iso-cli.py` expects it.
- Workflow JSON defines the graph. Profiles should not pretend to enable nodes that the workflow does not contain.
- Add new workflows beside the old ones when testing major pipeline changes.
- Use `benchmarks/` for curated visual comparisons. Do not promote raw generations without adding metadata.
- Treat `character_quality_x4.json` as a legacy reference: it produced good texture but was slow/heavy and still had hand problems.
- Treat the current `character_quality.json` as the working quality baseline: higher base resolution plus light refine, no latent x2 upscale.
- Before adding YOLO/detailers, verify ComfyUI actually exposes the required node classes through `/object_info`.

<!-- routing:start -->
## Routing

| Subdirectory | Description |
|--------------|-------------|
| [`assets/`](assets/CONTEXT.md) | Generated art output — characters and tiles. Not curated reference material (see |
| [`benchmarks/`](benchmarks/CONTEXT.md) | Curated, tracked comparison images (checkpoint/anatomy/model tests) and QC dev o |
| [`refs/`](refs/CONTEXT.md) | Captured references for isoroll-content — tier-1 links in [REFS.md](REFS.md); pr |
| [`src/`](src/CONTEXT.md) | Source code for the isoroll-content pipeline — CLI and art-generation scripts. G |

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`HISTORY.md`](HISTORY.md) | — | — | History |
| [`ROADMAP.md`](ROADMAP.md) | — | — | isorolling Roadmap |
| [`SETUP.md`](SETUP.md) | — | — | isorolling Setup |
| [`SPECS.md`](SPECS.md) | — | — | isorolling Specs |
<!-- routing:end -->
