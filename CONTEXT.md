# isorolling Context

isorolling is a Foundry VTT isometric-play project with a separate content-generation pipeline. The long-term product is two things:

1. A Foundry module for Hades-like isometric play: 8-direction sprites, height, partial or total occlusion, and visual sorting from 3D-style bounds.
2. An offline asset pipeline that can generate, refine, validate, and package characters, tiles, animations, spell effects, and metadata for Foundry.

The current repository is still mostly the content-pipeline prototype. `foundry/` is reserved for the future Foundry module implementation.

## Read Order

1. `CONTEXT.md`: onboarding and current intent.
2. `SPECS.md`: current files, code behavior, environment assumptions, and implementation rules.
3. `ROADMAP.md`: milestones and next tasks.
4. `.gitignore`: shows what is source versus generated output.

## Current Focus

The immediate work is `content/cli/iso-cli.py`, a small CLI that submits ComfyUI API workflows for character image generation.

The current generation baseline is:

- ComfyUI receives a workflow JSON through `/prompt`.
- `iso-cli.py` picks a workflow by profile name.
- The workflow handles the real node graph.
- Render profiles exist, but are currently mostly metadata and not applied as tunable parameters.
- Generated PNGs are ignored by Git under `content/characters/`.
- Tracked reference outputs belong in `content/benchmark/images/` with prompt/profile metadata in `content/benchmark/manifest.json`.

The next technical goal is YOLO/detailer support for faces and hands without regressing the working quality workflow.

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
isorolling/
  .gitignore
  CONTEXT.md
  SPECS.md
  ROADMAP.md
  content/
    benchmark/
      README.md
      manifest.json
      images/         # tracked benchmark images only
    cli/
      iso-cli.py
      iso-cli.bat
      workflow_api.json
      workflows/
        character_fast.json
        character_balanced.json
        character_quality.json
        character_quality_x4.json
    profiles/
      fast.json
      balanced.json
      quality.json
      character.json
      props.json
      environment.json
      photos.json
    characters/        # raw generated output, ignored
  foundry/             # future Foundry VTT module
```

## File Map

- `content/cli/iso-cli.py` — CLI entry point; submits ComfyUI API workflows for character image generation; selects workflow by profile name
- `content/cli/workflow_api.json` — default ComfyUI workflow (baseline reference)
- `content/cli/workflows/` — named workflow variants (`character_fast`, `character_balanced`, `character_quality`, `character_quality_x4`)
- `content/profiles/` — render profile JSONs (fast, balanced, quality, character, props, environment, photos)
- `content/benchmark/manifest.json` — metadata for curated benchmark outputs (prompt + profile per image)
- `content/benchmark/images/` — tracked benchmark images (promoted from raw generation)
- `foundry/` — reserved for future Foundry VTT module implementation (currently empty)

## Working Rules

- Keep source files portable. Do not commit local absolute ComfyUI paths.
- Use `COMFY_DIR` for the local ComfyUI root. `content/cli/iso-cli.py` expects it.
- Workflow JSON defines the graph. Profiles should not pretend to enable nodes that the workflow does not contain.
- Add new workflows beside the old ones when testing major pipeline changes.
- Use `content/benchmark/` for curated visual comparisons. Do not promote raw generations without adding metadata.
- Treat `character_quality_x4.json` as a legacy reference: it produced good texture but was slow/heavy and still had hand problems.
- Treat the current `character_quality.json` as the working quality baseline: higher base resolution plus light refine, no latent x2 upscale.
- Before adding YOLO/detailers, verify ComfyUI actually exposes the required node classes through `/object_info`.
