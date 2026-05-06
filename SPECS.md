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

The current CLI assumes:

- ComfyUI is already running at `http://127.0.0.1:8188`.
- Python can import `requests`.
- `COMFY_DIR` is set to the local ComfyUI root.
- The ComfyUI output directory is `${COMFY_DIR}/output`.

Do not hardcode the local ComfyUI path in versioned files. If configuration needs to improve, prefer environment variables, a local ignored config file, or CLI flags.

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
