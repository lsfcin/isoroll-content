# isorolling Specs

This file documents the current code and source structure so future agents can modify the project without rediscovering the same constraints.

## Source Boundaries

Versioned source should include:

- CLI code: `content/cli/iso-cli.py`, `content/cli/iso-cli.bat`
- ComfyUI API workflows: `content/cli/workflows/*.json`
- Render/profile metadata: `content/profiles/*.json`
- Curated benchmark references: `content/benchmark/README.md`, `content/benchmark/manifest.json`, and selected images under `content/benchmark/images/`
- Future Foundry module code under `foundry/`
- Project docs: `CONTEXT.md`, `SPECS.md`, `ROADMAP.md`

Generated or local-only artifacts should not be committed by default:

- `content/characters/`
- generated images under `content/**/*.png`, `content/**/*.jpg`, `content/**/*.jpeg`, `content/**/*.webp`
- local experiment bundles such as `content/*.zip`
- local ComfyUI outputs and temp folders
- `.env`, logs, Python caches, virtualenvs

Benchmark images are the only generated images intended to be tracked in this repository. They are manually promoted from raw outputs and must have metadata in `content/benchmark/manifest.json`.

## Benchmark Manifest

`content/benchmark/manifest.json` is the index for tracked reference outputs. Each sample should use this shape:

```json
{
  "id": "short-stable-id",
  "file": "content/benchmark/images/example.png",
  "prompt": "prompt used to generate the image",
  "profile": "quality",
  "workflow": "content/cli/workflows/character_quality.json",
  "seed": 123456,
  "date": "2026-04-30",
  "purpose": "why this image is useful as a benchmark",
  "notes": "optional observations, including known defects"
}
```

Use `null` for unknown values such as seed. Keep the manifest human-readable and sorted by sample id once there are multiple entries.

## Runtime Requirements

See [`SETUP.md`](SETUP.md) for full environment setup: ComfyUI install, required models, extensions, and `COMFY_DIR` configuration.

Runtime expectations (enforced by code):

- ComfyUI running at `http://127.0.0.1:8188` (not yet configurable via flag — see M1)
- `COMFY_DIR` env var pointing to local ComfyUI root
- `requests` importable in Python
- ComfyUI output dir: `${COMFY_DIR}/output`

Do not hardcode local paths in versioned files — always use `COMFY_DIR` or CLI flags.

## CLI Entry Points

From the repository root:

```powershell
.\content\cli\iso-cli.bat gen-character "medieval rogue with red cloak" --profile quality --out content\characters\rogue-test
```

From inside `content/cli/`:

```powershell
.\iso-cli.bat gen-character "medieval rogue with red cloak" --profile quality --out ..\characters\rogue-test
```

## `content/cli/iso-cli.py`

Current constants:

- `COMFY_URL`: fixed as `http://127.0.0.1:8188/prompt`
- `BASE_DIR`: directory containing `iso-cli.py`
- `CONTENT_DIR`: parent content directory
- `PROFILE_DIR`: `content/profiles`
- `WORKFLOW_DIR`: `content/cli/workflows`

Current functions:

- `get_comfy_dir()`
  - Reads `COMFY_DIR`.
  - Raises if missing.

- `get_output_dir()`
  - Returns `${COMFY_DIR}/output`.

- `copy_to_destination(src, dst)`
  - Creates the destination parent directory and copies one generated file.

- `get_latest_image(output_dir=None)`
  - Returns newest PNG under the output directory.
  - Legacy helper. Current generation uses a before/after snapshot instead.

- `apply_output_path(workflow, output_path)`
  - Sets `SaveImage.filename_prefix` in a workflow.
  - Currently unused by `gen_character()`.

- `load_profile(profile_name)`
  - Reads `content/profiles/{profile_name}.json`.
  - Current limitation: the returned profile object is loaded but not applied to workflow parameters.

- `load_workflow(prompt_text, profile_name)`
  - Reads `content/cli/workflows/character_{profile_name}.json`.
  - Randomizes every `KSampler.seed`.
  - Replaces positive `CLIPTextEncode` text using a heuristic: any CLIP text that does not contain `low quality` is replaced by the user prompt.
  - Current limitation: this heuristic drops any positive prompt suffix stored in workflow JSON, such as `highly detailed` or `clean edges`. Prefer future replacement of the literal `REPLACE_PROMPT` token.

- `send_prompt(workflow)`
  - POSTs `{"prompt": workflow, "client_id": uuid}` to ComfyUI.
  - Prints debug HTTP status and response text.
  - Returns parsed JSON or `None`.

- `gen_character(prompt, profile_name, output_path)`
  - Loads the profile and workflow.
  - Snapshots existing ComfyUI output PNGs.
  - Randomizes every `KSampler.seed` again. The second randomization wins.
  - Submits the prompt.
  - Polls up to 600 seconds for new PNGs.
  - Copies the newest new PNG to `--out` when provided.

- `main()`
  - Minimal argument parser.
  - Supports `gen-character`, `--profile`, and `--out`.

## Current Workflow Contract

Workflow file names must follow:

```text
content/cli/workflows/character_{profile}.json
```

The profile selected on the CLI currently selects the workflow file. It does not reliably tune the workflow from `content/profiles/{profile}.json`.

Current workflows:

- `character_fast.json`
  - 512x768
  - One `KSampler`
  - Direct decode and save
  - Fast preview baseline

- `character_balanced.json`
  - 640x960
  - Base sample, decode, encode, light refine, decode, save
  - Refine: 10 steps, cfg 6.0, denoise 0.28
  - Main balanced baseline

- `character_quality.json`
  - 640x960
  - Base sample, decode, encode, lighter refine, decode, save
  - Base: 36 steps, cfg 7.5
  - Refine: 12 steps, cfg 6.5, denoise 0.20
  - Current quality baseline

- `character_quality_x4.json`
  - 512x768
  - Base sample, pixel upscale with `4xUltrasharp_4xUltrasharpV10.pt`, encode, refine, decode, save
  - Legacy reference. Good texture, but expensive and still weak on hands.

## Render Profiles

Files in `content/profiles/` describe intended settings for asset categories or quality levels. They currently serve as metadata and naming references more than active configuration.

Do not add profile fields unless the CLI either:

- applies them to workflow nodes, or
- documents them as inactive metadata.

## ComfyUI and Detailer Status

Known local state from recent inspection:

- ComfyUI is reachable on `127.0.0.1:8188`.
- Impact Pack appears installed.
- Nodes such as `BboxDetectorSEGS`, `SegmDetectorSEGS`, `SEGSDetailer`, and `SAMLoader` are available.
- `UltralyticsDetectorProvider` was not available in `/object_info`.
- Embedded ComfyUI Python did not report the `ultralytics` package installed.
- A segmentation model existed locally as `models/ultralytics/segm/yolov8m-seg.pt`, but do not assume this in code.

Before implementing YOLO workflows, verify:

```powershell
Invoke-RestMethod http://127.0.0.1:8188/object_info
```

Required for Impact YOLO detailers:

- Impact Pack
- Impact Subpack, which provides `UltralyticsDetectorProvider`
- detector models under ComfyUI `models/ultralytics/`
  - segmentation models under `segm/`
  - bbox models under `bbox/`

Likely model targets:

- `segm/yolov8m-seg.pt` for general segmentation experiments
- `bbox/face_yolov8m.pt` or related face model for face detail
- `bbox/hand_yolov8n.pt` or `bbox/hand_yolov8s.pt` for hand detail

Do not add a workflow that depends on missing nodes without also adding a clear preflight check or error message.

`character_quality_yolo.json` exists in `workflows/` as a **draft** — designed but never tested. Requires Impact Subpack and `yolov8m-seg.pt`. Verify YOLO nodes via `/object_info` before using it (see `SETUP.md §7`).

## Preferred Implementation Pattern

For major generation changes:

1. Add a new workflow JSON instead of overwriting the working baseline.
2. Add a profile only if the CLI can select and validate it.
3. Preflight required ComfyUI node classes and model names.
4. Run one end-to-end generation.
5. Compare output quality against `balanced`, `quality`, and `quality_x4`.
6. Only promote the workflow after it improves quality without unacceptable time or VRAM cost.

## Known Technical Debt

- CLI strings show mojibake in Portuguese messages. Normalize file encoding and messages later.
- `load_profile()` is currently underused.
- Prompt injection should replace `REPLACE_PROMPT` specifically.
- Seeds are randomized twice.
- `COMFY_URL` is not configurable.
- The CLI should use `argparse` or similar instead of manual index parsing.
- Output tracking should ideally use ComfyUI `prompt_id` and `/history` instead of filesystem snapshots.
- There are no automated tests.
- All workflow JSONs still hardcode `dreamshaperPixelart_v10.safetensors` — update to `lyriel_v16.safetensors`.

---

## Asset Manifest Schema

Each packed asset folder emits a `manifest.json` with this shape:

```json
{
  "id": "warrior-base",
  "type": "character",
  "layer": 2,
  "source_concept": "content/characters/warrior/concept/warrior_concept_01.png",
  "source_workflow": "content/cli/workflows/character_quality.json",
  "checkpoint": "lyriel_v16.safetensors",
  "style_path": "A",
  "dimensions": { "w": 256, "h": 384 },
  "anchor": { "x": 0.5, "y": 0.9 },
  "bounds_3d": { "width": 1.0, "depth": 1.0, "height": 2.0 },
  "directions": ["SE", "E", "NE", "N", "NW", "W", "SW", "S", "TOP"],
  "animations": {
    "idle":         { "frames": 20, "fps": 12, "loop": true },
    "walk":         { "frames": 24, "fps": 12, "loop": true },
    "attack_melee": { "frames": 30, "fps": 12, "loop": false },
    "attack_ranged":{ "frames": 28, "fps": 12, "loop": false },
    "defend":       { "frames": 20, "fps": 12, "loop": false },
    "hurt":         { "frames": 15, "fps": 12, "loop": false },
    "cast":         { "frames": 30, "fps": 12, "loop": false },
    "crouch":       { "frames": 15, "fps": 12, "loop": false },
    "prone":        { "frames": 10, "fps": 12, "loop": false },
    "death":        { "frames": 40, "fps": 12, "loop": false },
    "fly_idle":     { "frames": 20, "fps": 12, "loop": true }
  },
  "equipment_slots": ["weapon_main", "weapon_off", "armor_chest", "armor_head"],
  "tags": ["humanoid", "warrior", "dark-fantasy"],
  "date": "2026-05-26",
  "notes": ""
}
```

---

## File Naming Convention

```
content/characters/{name}/
  concept/
    {name}_concept_{n:02d}.png          # external tool concept art (source of truth)
  blender/
    {state}/{direction}/
      frame_{n:04d}.png                 # raw Blender render (alpha PNG)
      frame_{n:04d}_depth.png           # depth pass (Path A ControlNet)
      frame_{n:04d}_lineart.png         # Freestyle lineart (Path A ControlNet)
  styled/
    {state}/{direction}/
      frame_{n:04d}.png                 # after SD style pass + rembg
  equipment/{slot}/
    {state}/{direction}/
      frame_{n:04d}.png                 # equipment overlay (alpha PNG)
  atlas/
    {name}_{direction}_{state}.png      # packed spritesheet per direction × state
    manifest.json
```

Direction labels: `SE`, `E`, `NE`, `N`, `NW`, `W`, `SW`, `S`, `TOP`

Animation state labels: `idle`, `walk`, `attack_melee`, `attack_ranged`, `defend`, `hurt`, `cast`, `crouch`, `prone`, `death`, `fly_idle`

---

## Blender Camera Rig Specification

- **Projection:** Orthographic (not perspective)
- **Primary elevation — 26.57°** (2:1 dimetric, Hades/Diablo standard). Tile diamond is 2× wide as tall in screen space. Camera is low — characters show mostly frontal view with slight overhead.
- **Alternative elevation — 35.264°** (true isometric). Tile edges appear at 30° from horizontal in screen space (the "30°" commonly cited in isometric art discussions refers to this screen-space edge angle, NOT the camera elevation). Higher camera, more top surface visible, better tactical grid readability for VTT use.
- **Note on the "30°" confusion:** 30° camera elevation is neither standard. 26.57° = 2:1 dimetric. 35.264° = true isometric. Pick one of these two.
- **Azimuth rotations (8 directions):**

| Label | Camera azimuth | Description |
|-------|----------------|-------------|
| SE    | 0°             | Camera facing NW, character faces viewer (front-facing view) |
| E     | 45°            | |
| NE    | 90°            | |
| N     | 135°           | |
| NW    | 180°           | |
| W     | 225°           | |
| SW    | 270°           | |
| S     | 315°           | |
| TOP   | 0° (elevation 90°) | Overhead orthographic |

- **Orthographic scale:** ~2.5–3.5 units (adjust so character fills ~80% of frame)
- **Output resolution per frame:** 256×384px for L1/L3 tiles/props; 256×384px for L2 characters at base; upscale to 512×768 after SD style pass.
- **Alpha:** enable `Film > Transparent` in EEVEE render settings. Render to PNG with alpha.
- **Blender script path:** `content/pipeline/blender_iso_rig.py`

---

## VRAM Budget — RTX 3050 6GB

| Workload | Estimated VRAM | Fits? |
|----------|----------------|-------|
| Blender EEVEE render (toon) | ~1.5–2.5GB | Yes |
| SD1.5 base generation | ~3.0–3.5GB | Yes |
| SD1.5 + 1× ControlNet | ~3.8–4.5GB | Yes |
| SD1.5 + IP-Adapter + 1× ControlNet | ~4.5–5.2GB | Yes (tight) |
| SD1.5 + IP-Adapter + 2× ControlNet | ~5.2–5.8GB | Marginal — test with `--lowvram` |
| SDXL base | ~5.5–6.5GB | Needs `--lowvram` + `--bf16-unet` |
| SDXL + IP-Adapter | ~7.0GB+ | Likely OOM — test |
| AnimateDiff SD1.5 (8 frames) | ~4.5–5.5GB | Tight — use small batch |
| Wan 2.1 video model | ~14GB+ | Not viable on 3050 |
| SVD (Stable Video Diffusion) | ~8–10GB | Not viable on 3050 |

**Recommended batch strategy:** Blender renders everything first (low VRAM), then queue all SD jobs in ComfyUI overnight. SD jobs do not compete with Blender for VRAM.

---

## Style Path Summary

**Path A — Blender-first:**
- Blender toon render → ComfyUI img2img (denoise 0.65–0.80) + ControlNet Tile or Lineart
- Temporal consistency: near-perfect (geometry is anchor)
- Drawn-feel risk: medium — depends on shader + denoise strength
- Equipment: separate Blender render pass, frame-aligned
- Best for: if visual consistency across 1,600+ frames is paramount

**Path B — IP-Adapter-first:**
- External concept art → IP-Adapter (identity) + ControlNet OpenPose (pose) → SD from scratch
- Temporal consistency: weaker — mitigate with seed locking + RIFE frame interpolation (generate keyframes, interpolate between)
- Drawn-feel: guaranteed (SD does all rendering)
- Equipment: harder — prompt-driven variant or separate Blender equipment render composited with Path B character
- Best for: if drawn aesthetic is non-negotiable

**Hybrid (possible outcome after experiments):**
- Blender renders to extract OpenPose skeleton only (rough mesh fine)
- SD generates from scratch using IP-Adapter (concept) + ControlNet OpenPose (skeleton)
- Gives drawn feel of Path B + more geometric control than prompt-only
- Equipment: Blender separate render for equipment overlay; character body from SD

**Decision:** run EXP-A and EXP-B, compare results, document chosen path in `## Chosen Pipeline` below.

---

## Chosen Pipeline

*(Fill in after EXP-A / EXP-B / EXP-C experiments are complete)*

- Primary path: TBD
- Primary checkpoint (dark-fantasy): TBD
- Primary checkpoint (cartoon/illustrated): TBD
- SD version (SD1.5 / SDXL): TBD
- Temporal consistency strategy: TBD
- Frame rate target: TBD (current assumption: 12 fps)
