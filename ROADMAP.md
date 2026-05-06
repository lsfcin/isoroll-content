# isorolling Roadmap

This roadmap tracks the content pipeline and the future Foundry runtime. Keep tasks small and test each milestone end to end.

## M0 - Repository Baseline

- [x] Create project-local `.gitignore`.
- [x] Keep generated character images out of Git.
- [x] Add `CONTEXT.md`, `SPECS.md`, and `ROADMAP.md`.
- [x] Decide whether curated sample outputs should live in a separate tracked folder.
- [x] Create `content/benchmark/` for tracked reference images plus prompt/profile metadata.
- [x] Create `content/cli/`, `content/profiles/`, and `foundry/` top-level areas.
- [ ] Add a short `README.md` once the CLI contract stabilizes.

## M1 - Stabilize `iso-cli`

- [ ] Normalize `content/cli/iso-cli.py` encoding and user-facing messages.
- [ ] Replace the prompt-injection heuristic with literal `REPLACE_PROMPT` substitution.
- [ ] Remove duplicate seed randomization.
- [ ] Add `--seed` for reproducible generations.
- [ ] Make `COMFY_URL` configurable with a default of `http://127.0.0.1:8188/prompt`.
- [ ] Improve CLI parsing with `argparse`.
- [ ] Validate `COMFY_DIR`, workflow path, profile path, and output path before submitting.
- [ ] Return a nonzero process exit code on generation failure.
- [ ] Add a `doctor` command that checks ComfyUI connectivity, `COMFY_DIR`, and required node classes.

## M2 - Define Workflow and Profile Contract

- [ ] Decide whether profiles are active configuration or metadata.
- [ ] If profiles are active, implement profile-to-node parameter application.
- [ ] If profiles are metadata, simplify them and document that workflows are authoritative.
- [ ] Add a workflow validation helper for required node classes.
- [ ] Add profile/workflow pairs for `fast`, `balanced`, and `quality` only after they are tested.
- [ ] Preserve `character_quality_x4.json` as a legacy reference unless a better reference replaces it.
- [ ] Document expected time and resolution for each profile on the current GPU class.

## M3 - YOLO and Detailer Upgrade

- [ ] Verify whether Impact Subpack is installed in the active ComfyUI instance.
- [ ] If missing, install Impact Subpack outside this repo and restart ComfyUI.
- [ ] Verify `UltralyticsDetectorProvider` appears in `/object_info`.
- [ ] Install or verify detector models:
  - [ ] `models/ultralytics/segm/yolov8m-seg.pt`
  - [ ] `models/ultralytics/bbox/face_yolov8m.pt` or selected face detector
  - [ ] `models/ultralytics/bbox/hand_yolov8n.pt` or `hand_yolov8s.pt`
- [ ] Add CLI preflight errors for missing detailer nodes or models.
- [ ] Create a face-detail workflow derived from the current `character_quality.json`.
- [ ] Test face detail on prompts with clear faces.
- [ ] Create a hand-detail workflow as a separate pass after face detail.
- [ ] Compare hand results with and without detector detail.
- [ ] Promote the best workflow only after it improves hands without damaging the whole image.

## M4 - Generation QA and Batch Runs

- [ ] Add batch generation with seed ranges.
- [ ] Save a sidecar manifest per output with prompt, workflow, profile, seed, and timestamp.
- [ ] Add a command to compare recent outputs by profile.
- [ ] Add a curated-review folder or manifest separate from ignored raw generations.
- [ ] Track rough runtime per image.
- [ ] Track failures such as no detection, timeout, and ComfyUI validation errors.
- [ ] Add basic smoke tests for JSON load and CLI argument parsing.

## M5 - Asset Packaging Format

- [ ] Define an asset manifest schema for Foundry export.
- [ ] Include asset id, type, prompt, source workflow, dimensions, origin, scale, and tags.
- [ ] Define 3D-style bounds for visual sorting and collision:
  - [ ] width
  - [ ] depth
  - [ ] height
  - [ ] anchor/origin
- [ ] Define character view naming for 8 directions.
- [ ] Define animation naming for idle, attack, defend, hurt, cast, crouch/prone, and down.
- [ ] Add `iso-cli pack` as a stub that validates a folder and emits a manifest.

## M6 - Foundry Runtime Prototype

- [ ] Create Foundry module skeleton.
- [ ] Add `module.json`.
- [ ] Add a custom data format for isometric actors, tiles, and bounds.
- [ ] Implement object-level isometric projection instead of global canvas skew.
- [ ] Implement 8-direction sprite switching for tokens.
- [ ] Implement visual sorting from 3D-style bounds.
- [ ] Prototype height offsets.
- [ ] Prototype partial occlusion.
- [ ] Load one generated character asset from the content pipeline.

## M7 - Hades-Like Production Pipeline

- [ ] Decide the representation for consistent multi-view assets: Blender, pseudo-3D, or another controlled renderer.
- [ ] Prototype one character rendered to 8 directions.
- [ ] Prototype one animation rendered to 8 directions.
- [ ] Preserve alpha at render/export time.
- [ ] Add `iso-cli render` for deterministic renders.
- [ ] Add sprite atlas generation.
- [ ] Add validation for view consistency, transparent background, and frame bounds.

## M8 - Release Path

- [ ] Add user-facing documentation for installing the Foundry module.
- [ ] Add developer documentation for the content pipeline.
- [ ] Build a sample asset pack.
- [ ] Build a sample Foundry scene.
- [ ] Add versioning and release packaging.
- [ ] Publish a test release.
