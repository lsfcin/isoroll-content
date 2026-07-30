# isoroll-content
> Offline asset generation pipeline for the isoroll Foundry VTT module
> goal: [rpg-isoroll](../../brain/goals/rpg-isoroll.md)

isoroll-content is the art and pipeline side of the isoroll project. It produces 8-direction isometric sprites, tiles, and animations for the isoroll Foundry module.

The long-term product is two things:
1. A Foundry module for Hades-like isometric play: 8-direction sprites, height, partial or total occlusion, and visual sorting from 3D-style bounds. (→ see `isoroll-module` repo)
2. This offline asset pipeline: generates, refines, validates, and packages characters, tiles, animations, spell effects, and metadata for Foundry.

## Read Order

1. `CONTEXT.md`: onboarding and current intent.
2. `ROADMAP.md`: **the only live-state file** — strategy, decisions D1–D7, milestones, gates.
3. `SCENE-CREATION.md`: canonical spec (status-free) — goal, seam, contract, kill-log.
4. `SPECS.md`: current files, code behavior, environment assumptions, and implementation rules.
5. Frozen decision records in `design/`; what happened in `HISTORY.md`; superseded trees in `archive/`.
6. Visual work: load `core/skills/iso-visual.md` (conventions + model failure modes + verification rule) before touching guides/kits/sprites.

## Current Focus

**MVP-first behind a frozen renderer seam** (replan 2026-07-29 — full rationale in ROADMAP.md):
`DSL v2 → [renderer] → cell sprites + manifest → Foundry`. The contract is the structure; the pixels are
swappable between content arms (A kit-sprite, B scene-cell world-uv render, C NB-painted textures). Order:
freeze the seam → ship something playable in Foundry with deliberately ugly pixels and all 8+1 views → then
compare arms as an A/B. Baseline:

- Pixels ship from the **offline Python bake** (supersampled + baked AO + ink). Any browser renderer is a
  painter-latency preview, never a source of shipped art.
- **NB (Gemini Flash Image) generates textures and decals**, not sprites — `src/cli/imagegen_client.py` (API + daily ledger) with manual web-app fallback (`gen-inbox`/`gen-outbox` folder contract).
- ComfyUI is a **utility rail only** (rembg, upscale, SAM2, LaMa) — `iso-cli.py` submits workflow JSONs through `/prompt`; local SD generation is dead as primary (SCENE-CREATION.md kill-log).
- Generated PNGs are gitignored under `assets/`; tracked reference outputs live under `benchmarks/` (each with `manifest.json` — see SPECS.md).

## Core Product Decisions

- Do not build a generic 3D runtime in Foundry.
- Do not globally skew the Foundry canvas as the main architecture.
- Keep runtime and asset generation separate.
- Aim for a **Dead-Cells-like production model**, not a Hades-like one: geometry rendered offline into 2D sprites, then efficient Foundry playback. Hades is hand-painted at artist cost; the achievable look here is Feather-3D / Tiny Glade, held by non-photometric shading (flat per-face ramp, no gradients/speculars) plus always-on linework.
- Treat prompts as an input to a structured asset pipeline, not as the whole pipeline.
- Scene geometry is deterministic; a generator never decides where anything is.
- **Anything that must rotate passes through geometry** — a rotating asset is a render of known geometry (scene cells, or a mesh for props/characters), never a generated view.
- Art cost is paid once at **texture scale** (~40 seamless materials) and via meshes for props — never per tile.
- Geometry is verified by code, never by model eyes; style is verified by human eyeball (`core/skills/iso-visual.md`).
- Blender remains the fallback lane (P-Kit) if the Python renderer proves insufficient — `[OBSOLETE-MESH]` scripts quarantined for that purpose.

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
      make_tile_guide.py, tile_guide_render.py, tile_guide_matrix.py # S0 tile multiview guide (active)
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
| [`design/`](design/CONTEXT.md) | — |
| [`output/`](output/CONTEXT.md) | — |
| [`refs/`](refs/CONTEXT.md) | Captured references for isoroll-content — tier-1 links in [REFS.md](REFS.md); pr |
| [`src/`](src/CONTEXT.md) | Source code for the isoroll-content pipeline — CLI and art-generation scripts. G |
| [`test/`](test/CONTEXT.md) | — |

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`HISTORY.md`](HISTORY.md) | — | — | History |
| [`ROADMAP.md`](ROADMAP.md) | — | — | isoroll-content Roadmap |
| [`SCENE-CREATION.md`](SCENE-CREATION.md) | — | — | SCENE-CREATION — Canonical Spec |
| [`SETUP.md`](SETUP.md) | — | — | isorolling Setup |
| [`SPECS.md`](SPECS.md) | — | — | isorolling Specs |
| [`archive/ROADMAP-2026H1-strategies.md`](archive/ROADMAP-2026H1-strategies.md) | — | — | ROADMAP archive — 2026-H1 strategy tree (SUPERSEDED) |
| [`archive/S4-REVIEW-ROUNDS.md`](archive/S4-REVIEW-ROUNDS.md) | — | — | S4 REVIEW ROUNDS — Lucas's 5 points on arm_a gate (2026-07-16) |
<!-- routing:end -->
