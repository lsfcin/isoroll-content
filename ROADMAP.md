# isorolling Roadmap

This roadmap tracks the content pipeline and the future Foundry runtime. Keep tasks small and test each milestone end to end.

---

## Strategic Context

**Product:** Hades-like isometric Foundry VTT module with offline AI art pipeline.

**Art layers (L1–L4):**
- L1: Scenario tiles — floors, walls, furniture, plants (static or near-static)
- L2: Characters — animated, multi-view (main complexity)
- L3: Items/props — weapons on ground, pickups
- L4: Effects — spells, attack FX

**Aesthetic target:** Drawn/illustrated feel (not 3D-rendered). Reference: Hades, not Pillars of Eternity.

**Hardware:** RTX 3050 6GB VRAM. Overnight batch runs are an asset — use them.

**Two candidate style paths — both must be tested before committing to production (see EXP-A and EXP-B):**

- **Path A — Blender-first:** Blender renders (toon shader) → SD img2img at high denoise. Temporal consistency near-perfect because 3D geometry is the anchor. Risk: may retain 3D feel even at high denoise.
- **Path B — IP-Adapter-first:** External concept art (MidJourney/GPT Image) as identity anchor → IP-Adapter + ControlNet OpenPose in ComfyUI → SD generates from scratch. Drawn feel guaranteed. Risk: temporal consistency weaker — identity may drift between frames without mitigation.

**Temporal consistency mitigation for Path B:** generate keyframes only (key poses per animation state), then interpolate with RIFE (frame interpolation model — no VRAM cost, CPU/GPU). AnimateDiff adds temporal attention across frames (~5GB on SD1.5) and is an alternative.

**Concept art source:** External tools (MidJourney, GPT Image, Nano Banana) produce higher quality single-image concept art than local SD — better hands, faces, weapons, iris detail. Use external tools for 1–5 key concept images per asset. Use local ComfyUI for all production-volume generation (views, animation frames, variants) — production volume would exhaust any external subscription. Plan B: draw concept art manually.

**Model strategy:** Test both SD1.5 and SDXL (--lowvram) side by side. SDXL needs ~5.5–6GB with optimizations (`--lowvram`, `--bf16-unet`). SD1.5 fits more comfortably and runs faster — better for batch overnight. SDXL has higher quality ceiling. Compare and decide per asset type.

**Checkpoint candidates:**
- `lyriel_v16`: dark fantasy illustrated style, strong Hades aesthetic. Spontaneously produces multi-view character sheets from prompts — exploit this.
- `toonyou_beta6`: cartoon/illustrated, flat graphic style, cleaner silhouettes for sprites. Good drawn feel. Test on 3/4 view + weapon in hand.
- `cetusMix_Whalefall2`: anime/semi-realistic hybrid. Clean graphic edges. Solid sprite candidate.

---

## M0 — Repository Baseline ✓

- [x] Create project-local `.gitignore`.
- [x] Keep generated character images out of Git.
- [x] Add `CONTEXT.md`, `SPECS.md`, and `ROADMAP.md`.
- [x] Create `content/benchmark/` for tracked reference images plus prompt/profile metadata.
- [x] Create `content/cli/`, `content/profiles/`, and `foundry/` top-level areas.
- [x] Benchmark model comparison done: lyriel_v16 recommended for dark-fantasy style.
- [ ] Add a short `README.md` once the CLI contract stabilizes.

---

## M1 — Stabilize `iso-cli`

- [ ] Normalize `content/cli/iso-cli.py` encoding and user-facing messages (fix Portuguese mojibake).
- [ ] Replace prompt-injection heuristic with literal `REPLACE_PROMPT` substitution (currently drops positive suffix like `"highly detailed, sharp focus, clean edges"`).
- [ ] Remove duplicate seed randomization (seeds randomized twice; second wins, first is wasted).
- [ ] Add `--seed` for reproducible generations.
- [ ] Make `COMFY_URL` configurable via env var or CLI flag (default `http://127.0.0.1:8188/prompt`).
- [ ] Improve CLI parsing with `argparse`.
- [ ] Validate `COMFY_DIR`, workflow path, profile path, and output path before submitting.
- [ ] Return nonzero exit code on generation failure.
- [ ] Add `doctor` command: checks ComfyUI connectivity, `COMFY_DIR`, and required node classes.
- [ ] Switch output tracking from filesystem snapshot to ComfyUI `/history` API with `prompt_id`.
- [ ] Add batch mode: accept multiple prompts or a seed range, submit all, collect all outputs.

---

## M2 — Workflow and Profile Contract

- [ ] Update all workflow JSONs to use `lyriel_v16.safetensors` as default checkpoint (currently hardcoded to `dreamshaperPixelart_v10.safetensors` which is not downloaded).
- [ ] Decide whether profiles are active configuration or metadata. If active: implement profile-to-node parameter application. If metadata: simplify and document.
- [ ] Add workflow variants for img2img (Path A and Path B both need these — see EXP milestones).
- [ ] Add profile/workflow pairs for `fast`, `balanced`, `quality` only after tested.
- [ ] Preserve `character_quality_x4.json` as legacy reference only.
- [ ] Document expected time and VRAM cost per profile on RTX 3050 6GB.
- [ ] Add SDXL workflow variants alongside SD1.5 variants with `--lowvram` flags documented.

---

## M3 — YOLO and Detailer Upgrade

*(Lower priority now that concept art comes from external tools; still needed for local refinement)*

- [ ] Verify whether Impact Subpack is installed.
- [ ] Verify `UltralyticsDetectorProvider` appears in `/object_info`.
- [ ] Install/verify detector models: `yolov8m-seg.pt`, `face_yolov8m.pt`, `hand_yolov8n.pt`.
- [ ] Add CLI preflight errors for missing detailer nodes or models.
- [ ] Create face-detail workflow derived from `character_quality.json`.
- [ ] Create hand-detail workflow as separate pass after face detail.
- [ ] Compare hand results with/without detector detail.
- [ ] Promote best workflow only after it improves hands without damaging whole image.

---

## M4 — Generation QA and Batch Runs

- [ ] Add batch generation with seed ranges.
- [ ] Save sidecar manifest per output: prompt, workflow, profile, seed, timestamp.
- [ ] Add command to compare recent outputs by profile.
- [ ] Add curated-review folder or manifest separate from raw generations.
- [ ] Track rough runtime per image.
- [ ] Track failures: no detection, timeout, ComfyUI validation errors.
- [ ] Add basic smoke tests for JSON load and CLI argument parsing.

---

## EXP-A — Blender-First Stylization Path (Path A experiment)

**Goal:** Determine if Blender toon-render → SD img2img can produce drawn feel at acceptable quality.

**Setup:**
- [ ] Install Blender (free, no VRAM cost for EEVEE renders).
- [ ] Create test scene: one humanoid character, rough mesh (capsule body + limb cylinders acceptable for Path B; needs decent mesh for Path A).
- [ ] Set up EEVEE toon shader: Principled BSDF with low roughness, Freestyle outline enabled, cel-shading via Color Ramp node on diffuse.
- [ ] Set up isometric camera rig: orthographic projection, 30° elevation (dimetric — matches Hades) OR 35.264° (true isometric). 8 azimuth rotations: 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°. Label directions SE, E, NE, N, NW, W, SW, S (standard for most isometric games — SE = camera facing toward viewer).
- [ ] Add 9th camera: 90° elevation, 0° azimuth (overhead/top-down view).
- [ ] Write Blender Python script: iterate cameras × animation frames × animation states, render each as PNG with alpha channel (`Film > Transparent` in EEVEE).
- [ ] Install `control_v11f1e_sd15_tile.pth` (ControlNet Tile) and `control_v11p_sd15_depth.pth` (ControlNet Depth) in ComfyUI `models/ControlNet/`.
- [ ] Add ComfyUI img2img workflow using ControlNet Tile or Lineart: take Blender render as input, denoise 0.65–0.80, lyriel_v16 checkpoint.
- [ ] Also test ControlNet Lineart (`control_v11p_sd15_lineart.pth`) as alternative — Blender Freestyle output → Lineart ControlNet → SD generates from scratch (this is between Path A and Path B).

**Evaluation criteria:**
- [ ] Does result look drawn or 3D? (subjective assessment — compare to Hades screenshots)
- [ ] Does result look like same character across front/side/back? (temporal/identity consistency)
- [ ] Is there visible "3D bleed" even at denoise 0.75?
- [ ] VRAM usage and generation time per frame on RTX 3050 6GB.
- [ ] Save 3 benchmark images: front, 3/4 SE, side — with prompt + denoise settings in manifest.

---

## EXP-B — IP-Adapter + OpenPose Path (Path B experiment)

**Goal:** Determine if external concept art + IP-Adapter holds character identity across 8 views.

**Setup:**
- [ ] Install IP-Adapter model for SD1.5: `ip-adapter_sd15.bin` or `ip-adapter-plus_sd15.bin` (plus = stronger identity lock) in ComfyUI `models/ipadapter/` or as custom node (`ComfyUI_IPAdapter_plus`).
- [ ] Install `control_v11p_sd15_openpose.pth` (ControlNet OpenPose) in ComfyUI `models/ControlNet/`.
- [ ] Source 1 concept image per test character via MidJourney, GPT Image, or Nano Banana. Prompt for: front-facing, full body, white/transparent background, character type (e.g. "medieval rogue").
- [ ] Build ComfyUI workflow: IP-Adapter (concept image as reference) + ControlNet OpenPose (pose skeleton input). Checkpoint: lyriel_v16 or toonyou_beta6.
- [ ] Source pose skeletons: either (a) use Blender rough mesh → render → extract OpenPose via ComfyUI DWPose detector node, OR (b) use online pose editors (e.g. `pose.ly`, `3dOpenPose editor`) to export isometric-angled skeleton images.
- [ ] Generate: front, 3/4 SE, side E, back N view of same character. Same seed if possible. Compare identity across 4 images.
- [ ] Test toonyou_beta6 separately on same pipeline — evaluate drawn feel vs lyriel_v16.

**Temporal consistency test:**
- [ ] Generate 5 keyframes of idle animation (frames 0, 5, 10, 15, 20 of a breathing cycle). Same IP-Adapter reference, same seed, vary only the OpenPose skeleton slightly.
- [ ] Install RIFE or FILM frame interpolation (ComfyUI node or standalone CLI). Interpolate between keyframes to produce full 20-frame animation.
- [ ] Evaluate: does interpolated animation look stable or does it flicker/drift?

**Evaluation criteria:**
- [ ] Does character identity hold across front/side/back views? (face shape, proportions, color palette)
- [ ] Does temporal consistency hold across 5 keyframes? (acceptable drift threshold: subtle, not flickering)
- [ ] VRAM usage: IP-Adapter + ControlNet OpenPose on SD1.5, RTX 3050 6GB (target: ≤5.5GB).
- [ ] If SDXL needed for acceptable quality: test SDXL IP-Adapter with `--lowvram` — document VRAM and time.
- [ ] Save benchmark images: all 4 views + interpolated animation preview. Add to manifest.

---

## EXP-C — SDXL vs SD1.5 Quality Comparison

- [ ] Add SDXL ComfyUI workflow (use `sdxl_base_1.0` checkpoint or `dreamshaperXL` equivalent).
- [ ] Enable `--lowvram` and `--bf16-unet` flags in ComfyUI launch command for 6GB VRAM.
- [ ] Generate same test character (same prompt, same pose) with SD1.5 (lyriel_v16) and SDXL side-by-side.
- [ ] Measure: quality (subjective), VRAM peak, time per image.
- [ ] Repeat for toonyou-equivalent SDXL model if available.
- [ ] Decision: use SDXL for concept-art-quality passes if VRAM allows, SD1.5 for high-volume overnight batch.

---

## EXP — Decision Gate

After EXP-A, EXP-B, EXP-C:
- [ ] Pick primary style path (A, B, or hybrid) based on drawn-feel and temporal consistency results.
- [ ] Pick primary checkpoints (SD1.5 models, SDXL models) per asset type.
- [ ] Document decision in SPECS.md under `## Chosen Pipeline` section.
- [ ] Commit benchmark results to `content/benchmark/` with manifest entries.

---

## AP0 — Technical Foundations (install before art milestones)

**ComfyUI nodes to install via Manager:**
- [ ] `ComfyUI_IPAdapter_plus` — IP-Adapter support
- [ ] `comfyui-controlnet-aux` — DWPose detector, depth estimator, lineart preprocessors
- [ ] `ComfyUI-AnimateDiff-Evolved` — for effects animation (L4)
- [ ] `comfyui-rembg` — background removal node (wraps `rembg` library)
- [ ] `ComfyUI_RIFE_VFI` — RIFE frame interpolation (temporal consistency for Path B)
- [ ] `ComfyUI-Video-Helper-Suite` — video frame loading/saving utilities

**Models to download:**
- [ ] `lyriel_v16.safetensors` → `models/checkpoints/` (primary dark-fantasy checkpoint)
- [ ] `toonyou_beta6.safetensors` → `models/checkpoints/` (cartoon/illustrated checkpoint)
- [ ] `cetusMix_Whalefall2.safetensors` → `models/checkpoints/` (anime/semi-realistic)
- [ ] `ip-adapter-plus_sd15.bin` → `models/ipadapter/` (stronger identity than base ip-adapter)
- [ ] `control_v11p_sd15_openpose.pth` → `models/ControlNet/`
- [ ] `control_v11f1e_sd15_tile.pth` → `models/ControlNet/`
- [ ] `control_v11p_sd15_depth.pth` → `models/ControlNet/`
- [ ] `control_v11p_sd15_lineart.pth` → `models/ControlNet/`
- [ ] RIFE model weights (auto-downloaded by ComfyUI node or manual from HuggingFace)
- [ ] For SDXL: `sdxl_base_1.0.safetensors` + `ip-adapter-plus_sdxl_vit-h.bin`
- [ ] For YOLO (M3): `yolov8m-seg.pt`, `face_yolov8m.pt`, `hand_yolov8n.pt` → `models/ultralytics/`

**Python dependencies (standalone tools):**
- [ ] `pip install rembg[gpu]` — standalone background removal CLI (GPU-accelerated)
- [ ] `pip install Pillow` — spritesheet packing
- [ ] Verify Blender is installed and launchable from command line (`blender --version`)
- [ ] Verify FFMPEG available for WebM export

**Document in SETUP.md:** all download URLs, exact file destinations, ComfyUI Manager names, and verification commands.

---

## AP1 — Scenario Tiles (Layer 1) — Pipeline Validation

*Start here. Simplest asset type. No animation, no rig. Proves full pipeline end-to-end.*

- [ ] Source concept: external tool (MidJourney/GPT) or SD. Prompt: `"isometric dungeon floor tile, stone cobblestone, dark fantasy, seamless, top-down, no background, game asset"`.
- [ ] Model tile geometry in Blender: simple 2×2 unit flat plane, add stone texture from concept image as material.
- [ ] Render 8 isometric views + 1 overhead using camera rig (see Blender script in AP2).
- [ ] Style pass in ComfyUI (chosen path from EXP decision).
- [ ] rembg background removal on outputs.
- [ ] Pack into spritesheet: 3×3 grid PNG (8 directions + 1 overhead) or individual PNGs.
- [ ] Write tile manifest JSON (see asset format spec in SPECS.md).
- [ ] Import into Foundry VTT manually — verify tile renders correctly at isometric angle.
- [ ] Repeat for: wall segment, furniture piece (table or chair), plant/prop.

---

## AP2 — Character Base (Layer 2) — Core Character Pipeline

*Most complex. Requires completed EXP experiments and decided path.*

**Blender setup:**
- [ ] Write `content/pipeline/blender_iso_rig.py`: Blender Python script that:
  - Creates 9 cameras (8 isometric at 30° elevation, 8 azimuth steps; 1 overhead at 90°)
  - Accepts animation state name + frame range as arguments
  - Iterates all cameras × all frames
  - Renders each as PNG with alpha to `output/{character}/{state}/{direction}/frame_{n:04d}.png`
  - Exports depth pass as separate PNG for Path A ControlNet Depth
  - Exports Freestyle lineart as separate PNG for Path A ControlNet Lineart
- [ ] Create rough base humanoid mesh OR download from Mixamo (Adobe ID required, free). Mixamo auto-rigs on upload.
- [ ] Import Mixamo animations via FBX (download "without skin" for each animation):
  - idle (breathing)
  - walk
  - attack_melee (sword swing or equivalent)
  - attack_ranged (bow or throw)
  - defend (block with shield or dodge)
  - hurt (flinch/impact received)
  - cast (spell casting arms)
  - crouch
  - prone (lying down)
  - death
  - fly_idle (floating, for flying enemies)
- [ ] Apply animations to character rig via NLA editor in Blender.
- [ ] Confirm frame counts per animation and note in `content/pipeline/animation_manifest.json`.

**Generation:**
- [ ] Run `blender_iso_rig.py` for all animation states. Overnight run on RTX 3050 EEVEE.
- [ ] Run ComfyUI batch (chosen path): style all Blender outputs overnight.
- [ ] Run rembg on all outputs.
- [ ] QA: review front-view idle, 3/4 SE idle, side E idle. Accept or regenerate.

**Character concept art:**
- [ ] Source 1–3 concept images per character via external tool. Keep raw file in `content/characters/{name}/concept/`.
- [ ] Prompt strategy for external tools: `"full body character reference, front view, {description}, white background, game art illustration style"`.

**Animation states to generate per character:**
- 11 states × 9 views = 99 render batches. Each batch = N frames (idle ~20, attack ~30, death ~40).
- Total per character (rough): ~2,500–4,000 frames. Plan 1–2 overnight batch runs.

---

## AP3 — Equipment Layers

*Depends on AP2 character rig being set up.*

- [ ] In Blender: add equipment mesh objects (sword, shield, armor) as separate objects parented to relevant armature bones (e.g. sword → hand.R bone, shield → hand.L bone, chest armor → torso).
- [ ] Render equipment pass: hide character body mesh, show only equipment, same cameras × same frames.
- [ ] Style pass on equipment renders (same ComfyUI workflow, same concept IP-Adapter reference if Path B, prompt adds equipment description).
- [ ] rembg on equipment renders.
- [ ] Pack: equipment sprite atlas per animation state, aligned to character atlas frame-for-frame.
- [ ] Runtime compositing test: manually layer character + equipment PNG sequences in GIMP or Python to verify alignment.
- [ ] Document equipment ID system: each character stores list of Mixamo animation IDs used, so equipment can be rigged to same animation IDs.

---

## AP4 — Items and Props (Layer 3)

- [ ] Similar to AP1 (tiles): static objects, 8 views, no animation.
- [ ] Sub-types: weapon pickup (sword on ground), armor piece, potion, chest.
- [ ] Use base-type concept art as template (one sword base → many sword variants via img2img + prompt variation).
- [ ] 8-view render in Blender. Style pass. rembg. Pack.

---

## AP5 — Effects (Layer 4)

**Simple non-directional effects (explosions, impact flashes):**
- [ ] Use AnimateDiff in ComfyUI: prompt-driven animation, SD1.5, ~8–16 frames at 512×512.
- [ ] Overhead view only, or 1–2 key views (most spell effects are symmetric or radial).
- [ ] Export as WebM via FFMPEG or ComfyUI video export node.

**Directional projectiles (arrows, fireballs, bolts):**
- [ ] Model projectile in Blender (simple geometry): animate movement over 10–15 frames along trajectory.
- [ ] Render 8 directional views (camera azimuth only; elevation stays at 30° isometric).
- [ ] Style pass. rembg. Pack.

**Attack FX (slash trails, swing arcs):**
- [ ] Blender: animate a curve or mesh deforming as a slash trail on same character animation frames.
- [ ] Render as separate pass (separate layer from character body).
- [ ] Style pass. Pack aligned to character attack animation.

---

## M5 — Asset Packaging Format

- [ ] Define asset manifest schema (see SPECS.md `## Asset Manifest Schema`).
- [ ] Define naming convention for all sprite files (see SPECS.md `## File Naming Convention`).
- [ ] Write `content/pipeline/pack_atlas.py`: reads a character folder, packs all direction × state frames into spritesheets, writes manifest JSON.
- [ ] Include in manifest: asset id, type, prompt, source workflow, dimensions, frame count, frame rate, anchor/origin, 3D bounds (width/depth/height for visual sorting), tags.
- [ ] Define character view direction naming: `SE`, `E`, `NE`, `N`, `NW`, `W`, `SW`, `S`, `TOP`.
- [ ] Define animation state naming: `idle`, `walk`, `attack_melee`, `attack_ranged`, `defend`, `hurt`, `cast`, `crouch`, `prone`, `death`, `fly_idle`.
- [ ] Add `iso-cli pack` command: validates a character folder, emits manifest.

---

## M6 — Foundry Runtime Prototype

- [ ] Create Foundry module skeleton in `foundry/`.
- [ ] Add `module.json`.
- [ ] Add custom data format for isometric actors, tiles, and bounds.
- [ ] Implement object-level isometric projection (not global canvas skew — see CONTEXT.md product decision).
- [ ] Implement 8-direction sprite switching: on token rotate, select nearest direction sprite using direction naming convention.
- [ ] Implement visual sorting from 3D-style bounds (width/depth/height/anchor in manifest).
- [ ] Prototype height offsets (token elevation → Y pixel offset).
- [ ] Prototype partial occlusion (tile hides token when token is "behind" it using z-buffer logic).
- [ ] Load one generated character asset from AP2 pipeline. Verify direction switching and idle animation play.

---

## M7 — Equipment Compositing in Foundry

- [ ] Implement equipment layer rendering: character base sprite + equipment overlay sprite, composited at runtime.
- [ ] Equipment swap = swap WebM/spritesheet reference, no re-animation.
- [ ] Define equipment slot system: weapon_main, weapon_off, armor_chest, armor_head, etc.
- [ ] Test: equip sword on character → sword overlay animates in sync with character attack animation.

---

## M8 — Top-View Transition

- [ ] In Blender: add camera interpolation sequence (camera elevation animating from 30° → 90° over 10 frames).
- [ ] Render transition clip per animation state (or just idle as first pass).
- [ ] Style pass. Pack as transition spritesheet.
- [ ] In Foundry module: detect "scene switch to top-down" event → play transition clip → swap to TOP view sprites.
- [ ] Implement top-down grid rendering mode (orthographic overhead) alongside isometric mode.

---

## M9 — Release Path

- [ ] Add user-facing documentation for installing the Foundry module.
- [ ] Add developer documentation for the content pipeline.
- [ ] Build sample asset pack (1 character, 1 tile set, 1 prop, 1 effect).
- [ ] Build sample Foundry scene using sample asset pack.
- [ ] Add versioning and release packaging.
- [ ] Publish test release.
