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

- `content/chars/`
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
  "source_concept": "content/chars/warrior/concept/warrior_concept_01.png",
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

## Tile Variant Naming Convention

```
content/outputs/tiles/{terrain}/
  concept/
    ...
  atlas/
    floor_{terrain}_inner.png
    floor_{terrain}_edge_N.png      # open edge north (no neighbor to north)
    floor_{terrain}_edge_E.png
    floor_{terrain}_edge_S.png
    floor_{terrain}_edge_W.png
    floor_{terrain}_corner_NE.png   # convex open corner NE
    floor_{terrain}_corner_NW.png
    floor_{terrain}_corner_SE.png
    floor_{terrain}_corner_SW.png
    floor_{terrain}_corner_in_NE.png  # concave inner corner (v2)
    floor_{terrainA}_x_{terrainB}_edge_N.png  # cross-type transition
    wall_{type}_straight.png
    wall_{type}_corner_in.png       # concave wall corner
    wall_{type}_corner_out.png      # convex wall corner
    wall_{type}_end_N.png           # wall end cap
    wall_{type}_T.png               # T-junction
```

Seam strategy summary:
- **Same-type seams**: Blender UV repeating texture eliminates seams geometrically. Make-seamless filter for 2D-only tiles.
- **Cross-type transitions**: Pre-rendered blend tiles (8 per pair). Blender gradient UV mask between two terrain textures.
- **Wall/floor junctions**: Z-sorting via 3D bounds + transparent wall base alpha. No blend texture needed.
- **Autotile**: 4-bit bitmask → look up variant table. 9 variants per terrain covers ~90% layouts. See AP1-T in ROADMAP.

---

## File Naming Convention

```
content/chars/{name}/
  concept/
    {name}_concept_{n:02d}.png          # external tool concept art (source of truth)
  sheet/
    tpose_front.png  tpose_back.png  front_full.png
    view_3q.png      equipment.png    palette.png
  _renders/
    {state}/
      frame_{n:04d}_{direction}.png         # raw Blender/intermediate render (RGBA)
      frame_{n:04d}_depth_{direction}.png   # depth pass (ControlNet)
  stances/
    {state}/
      frame_{n:04d}_{direction}.png         # final sprite after SD style pass + rembg
      {prefix}_{n:05d}_{direction}.png      # sprites from external tools (S4 path)
  equipment/{slot}/
    {state}/
      frame_{n:04d}_{direction}.png         # equipment overlay (alpha PNG)
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

### Tiles (L1) — decided 2026-07-03 (S0 design session)

**Route: NB-5G — Nano Banana guided 5-view grid.** Nano Banana is the primary
generator because it is the only route accessible to every user tier (essential /
important / desired). Local 3D-lift and Blender routes are fallback only.
Paid cloud GPU is not acceptable; NB via free Gemini access is.

**View count: 4+1.** The module camera is fixed (or rotates in 90° steps), so
grid-aligned walls only ever appear as `NW`, `NE`, `SW`, `SE` + `TOP`. The
cardinal views (N/S/E/W) — NB's systematic failure mode (panels collapse to flat
orthographic elevation, top face dropped) — are excluded by design, not worked
around. Tokens still need 8 facings; token pipeline is a separate decision
(next design session).

**Two-faced walls.** Walls have distinct faces (e.g. decorated interior vs plain
exterior). Guide schematic colors are face IDs, bound in the prompt:

| Color | Meaning |
|-------|---------|
| red | top surface |
| green | face A (e.g. decorated/interior) — visible in SW, SE |
| gray | face B (e.g. plain/exterior) — visible in NW, NE |
| blue | west end cap |
| purple | east end cap |

**Steps:**
1. **Hero view** — NB generates one best single view (SE-style) from text prompt.
   Human approves. This image is the identity anchor for everything after.
2. **Guide** — script-generated 5-panel schematic grid (colored blocks at correct
   26.57° dimetric proportions for the wall's L×H×T grid units).
3. **Grid call** — NB input: hero image + guide + prompt template binding
   colors→face descriptions. Output: filled 5-panel grid.
4. **Split** — `cli/sprite_splitter.py` (extended) → `tiles/{name}/{name}_{facing}.png`,
   facing ∈ {NW, NE, SW, SE, TOP}.
5. **QC + regen** — human checklist: top surface visible in all diagonals; face IDs
   correct; component counts (pillars, niches) match hero; no sticker border.
   Failed view → per-view regen (hero + that panel's schematic), max 2 per view.

**Reliability gate (go/no-go):** benchmark of 10 varied wall assets. Pass =
≥8/10 assets fully accepted within ≤2 per-view regens. Fail → activate fallback:
Blender parametric wall kit (box geometry + NB texture projection,
`pipeline/blender_iso_rig.py` as base) — consistency and seamless joins by
construction, but breaks the important/desired tiers.

**Floors:** flat — no multiview problem. One iso-diamond view (+ optional TOP).
Rotation variants derivable from texture rotation later.

**Props/furniture (irregular L1):** same NB-5G route. TripoSR lift (local, fits
6GB) stays as fallback for shapes NB can't keep consistent.

**Modular join sets (AP1-T4 corner/T/end pieces):** NB-only first; joins masked by
columns at junctions (T4 trick). Blender kit only if the benchmark fails.

**Desired-tier deliverable (v1):** recipe only — guide PNG template + copy-paste
prompt + short instructions shipped with module/docs. No API integration in module yet.

### Characters (L2) — TBD (next design session)

- Primary path: TBD (S3 3D-lift vs NB-based — token facings are 8, so NB's
  cardinal-view weakness returns; decide separately)
- Primary checkpoint (dark-fantasy): TBD
- SD version (SD1.5 / SDXL): TBD
- Temporal consistency strategy: TBD
- Frame rate target: TBD (current assumption: 12 fps)

---

## Concept Art Prompts (External Tools)

Use these prompts in GPT Image, Nano Banana, MidJourney, or similar external generators.
Do NOT specify camera angles in degrees — generators ignore them. Use visual descriptions and game references instead.

### Dungeon Floor Tile

```
Single isometric dungeon floor tile, classic 2:1 isometric game projection,
diamond shape twice as wide as it is tall, low camera angle showing the tile
face with slight top surface visible, dark grey and charcoal stone cobblestone,
subtle cracks and shallow worn grooves, faint teal-green moss in the crevices,
rough hand-cut stone edges, painterly illustrated style with visible brushwork,
strong clean silhouette, pure white background, no shadows cast onto the
background, no characters, no furniture, no other objects in frame, square
composition centered, dark fantasy game art, Diablo II isometric perspective,
Hades video game aesthetic.
```
Format: PNG, square (1:1).

### Character — Rogue/Assassin (first test character)

```
Full body character concept art, dark fantasy rogue assassin, front-facing
view with very slight overhead angle matching classic 2:1 isometric game
perspective, neutral relaxed standing pose with arms hanging slightly away
from body at sides, complete figure visible from head to toe, dark hooded
cloak with teal inner lining, light leather armor with gold metallic buckles
and accents, two daggers sheathed at hip, dark teal and black color palette
with gold highlights, face partially visible beneath hood, sharp intense eyes,
strong readable silhouette, pure white background, no drop shadow on
background, no environment, portrait orientation, digital illustration,
painterly brushwork, Hades video game art aesthetic, game character reference
art, full figure.
```
Format: PNG, portrait (2:3).

---

## Pipeline Current State (as of 2026-05-26)

### What exists and works

**`content/pipeline/preprocess.py`** — Step 1 of art pipeline.
- Input: raw concept PNG from external tool
- Removes background via rembg
- Resizes with padding to canonical dimensions (512×512 tiles, 512×768 characters)
- Saves `{name}_concept_raw.png` + `{name}_concept_clean.png` in `content/outputs/{type}s/{name}/concept/`
- Usage: `python content/pipeline/preprocess.py --input image.png --type tile --name dungeon_floor`
- Requires: `pip install "rembg[gpu]" Pillow`

**`content/cli/iso-cli.py`** — CLI entry point. Commands:
- `gen-character` — txt2img via ComfyUI (existing, now with REPLACE_PROMPT fixed)
- `style-concept` — img2img style pass on preprocessed concept art (new)
  - Uploads image to ComfyUI via `/upload/image` API
  - Runs `concept_img2img.json` workflow (base + refine pass, lyriel_v16)
  - Usage: `python iso-cli.py style-concept path/concept_clean.png --prompt "..." --denoise 0.55 --out path/styled`

**`content/cli/comfy_client.py`** — ComfyUI API helpers (extracted from iso-cli.py for line-count reasons).

**`content/cli/workflows/concept_img2img.json`** — img2img workflow. Checkpoint: lyriel_v16. Denoise overridden by CLI flag.

### Known bugs fixed in this session
- REPLACE_PROMPT injection: was using CLIP heuristic (dropped positive prompt suffix). Now literal substitution.
- Double seed randomization: seeds were set twice. Fixed — single randomization.

### Still pending from M1
- `argparse` (still using manual index parsing)
- `doctor` command
- Output tracking via `/history` API instead of filesystem snapshot
- Batch mode
- Nonzero exit codes (partial)

### Folder structure
```
content/
  cli/
    iso-cli.py
    comfy_client.py
    workflows/
      character_fast.json
      character_balanced.json
      character_quality.json
      character_quality_x4.json     (legacy)
      character_quality_yolo.json   (draft, untested)
      concept_img2img.json          (new — img2img style pass)
  pipeline/
    preprocess.py                   (new — rembg + resize)
  profiles/
    *.json
  outputs/
    benchmark/                      (moved from content/benchmark/)
    characters/
    tiles/
    items/
    effects/
```
