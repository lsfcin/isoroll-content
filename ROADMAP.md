# isorolling Roadmap

Content pipeline roadmap. Keep tasks small and test each milestone end to end.

> **Canonical spec: [SCENE-CREATION.md](SCENE-CREATION.md)** — architecture, contract, kill-log, phase program (P0–P9).
> **Live execution state: [ROADMAP-content-gen.md](ROADMAP-content-gen.md)** — F1 kit assembly + multiview spine.
> **Superseded strategies: [archive/ROADMAP-2026H1-strategies.md](archive/ROADMAP-2026H1-strategies.md)** — Phase C, S1–S4, EXP-A/B/C, AP0–AP5, M2–M9 (pre-pivot SD/ComfyUI/Blender tree). Consult kill-log before resurrecting.

## Backlog / Ideas

- **Env utility repair (2026-07-08, padaria, done)** — `$HOME/ComfyUI/models/{checkpoints,embeddings,loras,upscale_models}` symlinks pointed at `/mnt/workspace/Models/diffusion/*`, which didn't exist (every local CLI command failed at ComfyUI runtime). Created the four target dirs so all symlinks resolve, and downloaded `4xUltrasharp_4xUltrasharpV10.pt` into `upscale_models`. No SD checkpoint downloaded, no service started. Trail: `.loop/env-utility-repair/`.
- **Multiview via registration marks — mural-painter technique** (INBOX 2026-07) → EXECUTING: sub-roadmap [ROADMAP-content-gen.md](ROADMAP-content-gen.md) (Fable 2026-07-07). STATUS UPDATE 2026-07-09: at SCENE scale the technique is PARKED (single-pass scene generation killed by test — see SCENE-CREATION.md kill-log); marks/anchors remain in use at TILE/kit-sheet scale. The short-paper idea (research the technique in literature) stays alive.
- ~~**Single-pass full tilemap generation** (INBOX 2026-07)~~ — **DEAD 2026-07-08**: same failure mode as single-pass scene (geometry diverges at scene scale). See SCENE-CREATION.md kill-log. Superseded by kit assembly.

---

## Strategic Context

**Product:** Hades-like isometric Foundry VTT module (`isoroll-module`) with offline AI art pipeline (this repo).

**Art layers (L1–L4):**
- L1: Scenario tiles — floors, walls, furniture, plants (static or near-static)
- L2: Characters — animated, multi-view (main complexity)
- L3: Items/props — weapons on ground, pickups
- L4: Effects — spells, attack FX

**Aesthetic target:** Drawn/illustrated feel (not 3D-rendered, not cel-shaded 3D). Reference: Hades, Bastion, Transistor; not Pillars of Eternity.

**Generator strategy (verified web 2026-07):** NB (Gemini Flash Image, free ~500/day) = primary generation; NB2 (~20/day) reserve. ComfyUI = **utility rail only** (rembg, upscale 4xUltrasharp, SAM2, LaMa) — local SD generation is dead as primary (kill-log). Fallbacks if NB fails a gate: Hunyuan3D-2mini / TripoSR for mesh (P-Kit lane, reuses `[OBSOLETE-MESH]` blender scripts), Qwen-Image-Edit / Flux Kontext GGUF for edit, Colab/Kaggle for big jobs.

**Scene creation:** kit assembly — NB paints tile-sized kit pieces only; scenes composed deterministically from layout. Full spec: [SCENE-CREATION.md](SCENE-CREATION.md).

**Hardware:** RTX 3050 6GB VRAM. Overnight batch runs are an asset — use them.

---

## S0 — Multiview Pipeline Decision ✓ DECIDED for tiles (2026-07-03; extended to 8+1 2026-07-09)

**Decision (full spec: `SPECS.md → ## Chosen Pipeline`):**
- [x] Tile view count: base **4+1** (NW/NE/SW/SE + TOP), **extended 2026-07-09 to 8+1 program** (user decision, plan rev.3): dimetric regime first (existing), **cardinal regime (N/E/S/W) as a second art batch** — new kit art per piece (walls face-on) + cardinal projection preset in the module. Cardinal proportions anchored on the reference deck (`pipeline/prompts/reference/isometric_images.pdf`); scale-consistency spec applies to both regimes (SCENE-CREATION.md).
- [x] Route: **NB-5G** — Nano Banana guided 5-view grid. Concept view (approved) + script-generated schematic guide + prompt → 5-panel grid → split → QC with ≤2 per-view regens. NB primary because accessible to all user tiers; paid cloud GPU rejected.
- [x] 3D-lift evaluated: TripoSR/Hunyuan demoted to fallback. For boxy walls, Blender parametric kit + texture projection beats mesh reconstruction anyway — but activates only if NB benchmark fails.
- [x] Walls are two-faced; guide encodes faces via grayscale screen-role ramp (S0-E1c).
- [x] Reliability gate: 10-asset benchmark, pass = ≥8/10 accepted within ≤2 per-view regens.
- [ ] Tokens (8 facings) — separate design session; NB cardinal weakness returns there.

**Execution tasks (done log — details in git history / HISTORY.md):**
- [x] S0-E1a 6-cell layout decided; S0-E1 `make_tile_guide.py` + `tile_guide_render.py` (unfolded-net cardinal convention from the deck, verified vs 2 reference pages); S0-E1b explicit TOP cells; S0-E1c grayscale value ramp + magenta linework; S0-E2 prompt templates.
- [x] S0-E6 multi-object batch design (pillar over L-corner; abut on cell edges, never co-cell); S0-E6-fix door/window → jambs + LINTEL + flat leaves (`d=0`); S0-E6-floors sizes 2/3/5/10/20/40; S0-E6-fix2/3/4 chirality: orientation band on pivot edge for all chiral tiles (door hinge, stairs spiral), "rotate never mirror"; S0-E6-fix5 NB sheet postproc rework (`sheet_grid.py` + `sheet_utils.py` + `nb_sheet_processor.py`).
- [ ] S0-E3 extend `cli/sprite_splitter.py` — 5-panel layouts → `tiles/{name}/{name}_{facing}.png` + rembg.
- [ ] S0-E6a run NB calls: batch A (structure, 9), B (openings, 12) — verify hinge-band handedness holds; escalate to engine-side rotation if not.
- [ ] S0-E6b run NB calls: batch C (stairs, 10), D (furniture, 15), E (decorative, 11) + floor set.
- [ ] S0-E6c go/no-go: does the text-only style paragraph hold consistency across separately-generated batches, or is an image anchor needed despite bleed risk.
- [ ] **S0-E7 (NEW, 8+1): cardinal batch** — cardinal guide camera mode in the guide renderer (deck-anchored proportions) → NB batches A–E for N/E/S/W → same postproc/QC. After dimetric batches prove the process (P8 of the program).
- [ ] S0-E4 benchmark: 10 varied wall assets. User runs NB calls, session prepares inputs + records per-view pass/fail in `benchmarks/multiview-nb/manifest.json`.
- [ ] S0-E5 go/no-go writeup. Pass → NB-5G confirmed + desired-tier recipe. Fail → Blender parametric wall kit design session (P-Kit).
- [ ] (engine-side, isoroll-module repo) door/window leaf-swing rotation+pivot + big-floor-tile placement — tracked in module ROADMAP Scene Painter track.

---

## M0 — Repository Baseline ✓ (completed items → HISTORY.md)

- [ ] Add a short `README.md` once the CLI contract stabilizes.

## M1 — Stabilize `iso-cli` (partially done → HISTORY.md)

- [ ] Add `--seed` for reproducible generations.
- [ ] Improve CLI parsing with `argparse` (the `iso-cli.py` dispatcher still uses manual `sys.argv` indexing via `get_arg()`).
- [ ] Add `doctor` command: checks ComfyUI connectivity, `COMFY_DIR`, and required node classes.
- [ ] Switch output tracking from filesystem snapshot to ComfyUI `/history` API with `prompt_id`.
- [ ] Add batch mode: accept multiple prompts or a seed range, submit all, collect all outputs.

---

## Pointers

- Asset packaging / manifest schema work (was M5) → lives in the `export-manifest` loop + SCENE-CREATION.md contract.
- Foundry runtime (was M6–M8: projection, 8-direction switching, sorting, occlusion, top-view) → **built or tracked in `isoroll-module`** (slicing/depth-sort done; multiview = program P8).
- Autotile piece taxonomy + junction rules (was AP1-T) → absorbed into SCENE-CREATION.md § Painter grammar; details in archive.
- Characters/animations (was AP2–AP3, S1–S4 order table) → next design session after tiles ship; NB cardinal weakness returns for tokens (S0 last item).
