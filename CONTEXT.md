# isoroll-content
> Offline asset generation pipeline for the isoroll Foundry VTT module

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

The immediate work is `cli/iso-cli.py`, a small CLI that submits ComfyUI API workflows for character image generation.

The current generation baseline is:

- ComfyUI receives a workflow JSON through `/prompt`.
- `iso-cli.py` picks a workflow by profile name.
- The workflow handles the real node graph.
- Render profiles exist, but are currently mostly metadata and not applied as tunable parameters.
- Generated PNGs are gitignored under `chars/`.
- Tracked reference outputs belong in `outputs/benchmark/images/` with metadata in `outputs/benchmark/manifest.json`.

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
  cli/
    iso-cli.py
    iso-cli.bat
    workflows/        # ComfyUI workflow JSONs
    batch_rembg.sh
    batch_stylize.sh
    sprite_splitter.py
  pipeline/           # art pipeline scripts
    preprocess.py
    sheet_to_tpose.py
    generate_sheet_template.py
    prompts/
  pipeline/           # mesh/3D scripts (may be obsolete)
    triposr_mesh.py, blender_iso_rig.py, calibrate*.py
  profiles/           # generation quality profiles
  outputs/benchmark/  # tracked benchmark images + manifests
  chars/              # per-character outputs (gitignored)
    {name}/
      concept/
      sheet/
      {name}_{stance}_{facing}.png  # final sprites
      _renders/{stance}/            # intermediate renders (gitignored)
  tiles/              # tile assets
    {name}/
      {name}_{facing}.png
```

## File Map

- `cli/iso-cli.py` — CLI entry point; submits ComfyUI API workflows; selects workflow by profile name
- `cli/workflows/` — named workflow variants (`character_fast`, `character_balanced`, `character_quality`, etc.)
- `cli/sprite_splitter.py` — splits external sprite sheets into per-direction flat files
- `pipeline/preprocess.py` — background removal + resize for concept art → `chars/{name}/concept/`
- `pipeline/sheet_to_tpose.py` — crop GPT character sheet → panels in `chars/{name}/sheet/`
- `profiles/` — render profile JSONs (fast, balanced, quality, character, props, environment, photos)
- `outputs/benchmark/manifest.json` — metadata for curated benchmark outputs
- `outputs/benchmark/images/` — tracked benchmark images (promoted from raw generation)

## Working Rules

- Keep source files portable. Do not commit local absolute ComfyUI paths.
- Use `COMFY_DIR` for the local ComfyUI root. `cli/iso-cli.py` expects it.
- Workflow JSON defines the graph. Profiles should not pretend to enable nodes that the workflow does not contain.
- Add new workflows beside the old ones when testing major pipeline changes.
- Use `outputs/benchmark/` for curated visual comparisons. Do not promote raw generations without adding metadata.
- Treat `character_quality_x4.json` as a legacy reference: it produced good texture but was slow/heavy and still had hand problems.
- Treat the current `character_quality.json` as the working quality baseline: higher base resolution plus light refine, no latent x2 upscale.
- Before adding YOLO/detailers, verify ComfyUI actually exposes the required node classes through `/object_info`.

<!-- routing:start -->
## Routing

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`ROADMAP.md`](ROADMAP.md) | — | — | isoroll-content Roadmap |
| [`SPECS.md`](SPECS.md) | — | — | isoroll-content Specs |
<!-- routing:end -->
