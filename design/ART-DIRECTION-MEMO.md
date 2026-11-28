# Art Direction — Player Artwork & Style Lab
> Decision memo for [art-direction] (2026-11-28): translated player-image target, option costs, outside panel verdicts, 3D customizer boundary, and conditional D4 reopen gate.

## Readings of "doing justice to the player's image"

| Reading | What walks on the board | Precedent | Verdict (Lucas, 2026-11-28) |
|---|---|---|---|
| **(a) Literal** | The player's own pixels move | Paper Mario, Octopath, Wildermyth | Floor only (T4 reference) |
| **(b) Translated** | Original portrait stays in UI; character is redrawn in Isoroll's house style | **Hades** (Jen Zee portraits + 3D models → sprites) | **Selected target** |
| **(c) Mixed** | Each character keeps its own visual style | Spider-Verse | Deferred |

## Options × effort × outside panel (Codex + Argon, 2026-11-28)

| Option | Scope | Est. effort | Panel verdict & key risk |
|---|---|---|---|
| **T1** External reference taste wall | Pairwise A/B HTML of external works | ~1 h | **Demote/fold:** commercial art inflates expectations without testing our pipeline; kept only as Tab 2 alongside live code lenses |
| **T2** Live shader + temporal lenses on Observatório | Code-only GLSL lenses × cadence (60 vs 12 fps on 2s + acting/hitstop) × VFX | 1–2 sessions | **Focus on phone-readable lenses:** at 50–90 px character height, heavy Kuwahara/halftone can blur faces; **built in `lab.html`** |
| **T3a** 2D puppet from portrait | Animated-Drawings-style cutout rig | 2+ sessions | **Drop:** mirror fails 8+1 views; busts and cloaks break 2D rigging |
| **T3b** Parametric 3D miniature / customizer | Rigid articulated parts + sockets + VLM-extracted palette/preset from portrait | 1–2 sessions | **Both prioritize:** 8+1 views free by geometry; 2nd character drops to seconds |
| **T3c** Image → 3D mesh + auto-rig | Hunyuan3D / TRELLIS / DrawingSpinUp + Mixamo + toon | Several sessions | **Drop for now:** ~24 GB VRAM exceeds 6 GB 3050, dirty topology breaks toon normals/outlines |
| **T4** Living card / standee | Portrait billboard with base, jump/squash walk | ~2 h | **Keep as literal floor** if needed: risks ambiguous spell facing & MUGEN collage |

## Baseline verdict & architectural boundaries

- **Observatório baseline:** spatial feel and fluidity approved on PC & phone; **flat low-poly shading and continuous 60 fps motion are explicitly insufficient**. Needs shader/paint pass + 12 fps stepped acting + graphic VFX.
- **3D customizer + CSG:** use rigid articulated parts and parametric sockets for humanoids and monsters (different base rigs per body plan); reserve Constructive Solid Geometry (CSG) / Signed Distance Fields (SDF) for rigid armor/gear/props, never deforming joints.
- **D4 (offline Python bake) reopen gate:** keep "anything that rotates passes through known geometry"; reopen D4 for standalone play only if live 3D + shaders + stepped acting pass Lucas's visual bar at real phone scale and frame time.
