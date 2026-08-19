# Render rig and budget
> The Blender camera rig, the VRAM budget, and the style path it has to hold.
> governs: src/pipeline/

## Blender Camera Rig Specification

- **Projection:** Orthographic (not perspective)
- **Primary elevation — 26.57°** (2:1 dimetric, Hades/Diablo standard). Tile diamond is 2× wide as
  tall in screen space. Camera is low — characters show mostly frontal view with slight overhead.
- **Alternative elevation — 35.264°** (true isometric). Tile edges appear at 30° from horizontal in
  screen space (the "30°" commonly cited in isometric art discussions refers to this screen-space
  edge angle, NOT the camera elevation). Higher camera, more top surface visible, better tactical
  grid readability for VTT use.
- **Note on the "30°" confusion:** 30° camera elevation is neither standard. 26.57° = 2:1 dimetric.
  35.264° = true isometric. Pick one of these two.
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
- **Output resolution per frame:** 256×384px for L1/L3 tiles/props; 256×384px for L2 characters at
  base; upscale to 512×768 after SD style pass.
- **Alpha:** enable `Film > Transparent` in EEVEE render settings. Render to PNG with alpha.
- **Blender script path:** `src/pipeline/blender_iso_rig.py`

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

**Recommended batch strategy:** Blender renders everything first (low VRAM), then queue all SD jobs
in ComfyUI overnight. SD jobs do not compete with Blender for VRAM.

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
- Temporal consistency: weaker — mitigate with seed locking + RIFE frame interpolation (generate
  keyframes, interpolate between)
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
