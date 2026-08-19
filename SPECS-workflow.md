# Workflow contract
> What a ComfyUI workflow must expose, the render profiles, the detailer state.
> governs: src/cli/workflows/

## Current Workflow Contract

Workflow file names must follow:

```text
src/cli/workflows/character_{profile}.json
```

The profile selected on the CLI selects the workflow file by name only. There
is no profile-JSON tuning layer (see `## Render Profiles` below — that layer
was deleted as dead weight).

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

There is no `profiles/*.json` and no profile-to-node parameter layer. Workflow
selection is entirely by filename (`character_{profile_name}.json`). Per-category
settings metadata was tried and nothing in the CLI ever read it, so do not
reintroduce it without a reader.

If profile-driven tuning is revisited: only add it back once the CLI actually
applies fields to workflow nodes. Don't reintroduce inert metadata.

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

`character_quality_yolo.json` exists in `workflows/` as a **draft** — designed but never tested.
Requires Impact Subpack and `yolov8m-seg.pt`. Verify YOLO nodes via `/object_info` before using it
(see `SETUP.md §7`).
