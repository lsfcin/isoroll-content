# RENDER→RESTYLE — P5 strategy revision memo
> Status: ☐ DISCUSSION with Lucas — no execution before his call. Outcome lands in SCENE-CREATION.md (P5 + kill-log/promotion) and ROADMAP-content-gen lanes.
> Requested 2026-07-13: Lucas flags the 3D-texturize-render-restyle idea as "most promising", notes it got lost/ditched — revise and discuss.

## The idea (Lucas's recap, faithful)

Place simplified meshes in a scene (voxels for walls; adapted meshes for stairs, windows, doors, roofs), texturize with ONE of:
- **(a) real textures** — an actual door/wall texture;
- **(b) blank/technical textures** — a "white door", "blank window", like a technical drawing, no identity;
- **(c) cyan symbols** — semantic positioning marks only (color negotiable);

then **render**, and ask NB (or any image tool) to **restyle** the render — instead of creating the sprite from box-guide images. Rationale: restyle is an easier regime for image models than creation, and models are bad at identifying sides — which the cyan-symbols strategy mitigated, but a render solves structurally.

## Where the idea survives in the docs (it was fragmented, never assembled as candidate-primary)

| Fragment | File | What it kept |
|---|---|---|
| Path A "Blender-first": toon render → img2img (denoise 0.65–0.80) + ControlNet Tile/Lineart; "temporal consistency near-perfect (geometry is anchor)" | `archive/ROADMAP-2026H1-strategies.md` | the full recipe — archived with the 2026-H1 tree |
| P-Kit lane: Blender parametric kit, `[OBSOLETE-MESH]` scripts quarantined | `ROADMAP.md`, CONTEXT.md | the mesh backend, demoted to fallback-if-NB-fails |
| P-CTRL lane: hosted Flux+ControlNet conditioned on massing-derived depth/lineart | `ROADMAP-content-gen.md` (lane P-CTRL) | the conditioning insight — depth/contours are trivial to emit from the guide renderer |
| F4 `mv-restyle` verb: existing sheet + marks + style prompt → NB | `ROADMAP-content-gen.md` | the restyle seam in the CLI |

**Why it got lost**: the archive kill was *local SD as generator* (horrible character artifacts). Path A died with that tree, but its render→restyle STRUCTURE was never falsified — with NB as the restyler it is untested. The kill-log has no entry against it.

## Reconstruction for the KIT regime (not characters)

```
massing (layout DSL / rig export)                       ← exists (P2/P3 shipped; rig v15 is the twin)
  → module meshes/boxes: KIT V2 voxel modules            ← matches painter render units 1:1
    (wall band, cap, base, per-side recess band,           (band/cap/base derived exactly like the
     diag half-band, wedge, roof cells)                     rig merges column runs — same vocabulary)
  → texturize: arm (a) real | (b) blank-technical | (c) symbols
  → render 8 yaws (+TOP), one shared px-per-voxel s      ← scale-consistency spec (P3) applies as-is
  → NB restyle (web app, chosen route) per sheet
  → QC: silhouette IoU vs SOURCE RENDER (≥0.9), residue, cross-view dims   ← QC gets CHEAPER:
                                                            the ground truth image exists by construction
```

Render backend options:
1. **Python flat-shaded** — extend `tile_guide_render.py` / port the rig's drawers; grayscale face ramp already encodes lit-from-above. Nearly exists; zero new deps.
2. **Blender parametric** — revive `[OBSOLETE-MESH]` scripts (P-Kit lane); real AO, real texture mapping (needed for arm (a)); heavier standup.

## Comparison vs current primary (NB paints from box-guide + marks)

| Dimension | NB-from-guide (current) | Render→restyle (lane R) |
|---|---|---|
| Geometry | model must INVENT volume from boxes+marks; round-15 evidence: door side replicated ignoring rotation | geometry GIVEN in the input image; model only re-skins. Side identification solved structurally, not symbolically |
| QC cost | needs guide-vs-output registration | near-free: IoU against the source render |
| Restyle risk | n/a | model may drift geometry while restyling (the denoise dial in the old recipe); IoU catches it |
| Style ceiling | NB free to compose (style PASS on first web run) | style constrained by input shading; arm choice (a/b/c) is a guidance-strength dial: c < b < a |
| Cost/route | 1 NB call per sheet (web app manual) | same NB calls + a deterministic offline render step (cheap) |
| Standup | exists | backend 1: days; backend 2: revive quarantined scripts |
| Watermark | bottom-right cell must stay empty | same (sheet layout fix applies to both) |

## Proposed test-to-kill (pre-registered, cheap: ~6–8 web-app images)

- **Fixture**: same dimetric kit-sheet vocabulary as Lucas's first NB run; bottom-right cell empty/caption.
- **Arms**: `A0` = existing NB-from-guide sheet (already generated — free baseline); `R-b` = blank-technical render restyled; `R-c` = symbols-on-gray render restyled. (`R-a` real-texture only in a second round, and only if (b) shows NB clinging to input shading.)
- **Protocol**: 1 variable per round, 2 seeds/arm, fixed style prompt (ROADMAP-content-gen protocol).
- **Metrics**: silhouette IoU ≥ 0.9 vs source render; **door/window side correctness across 2 yaws** (the criterion that killed round-15's sheet); mark residue; Lucas style 1–5.
- **Decision rule (pre-registered)**: R-arm beats A0 on side-correctness AND IoU with style ≥ (A0 − 1) → **promote lane R to P5 primary** (P-CTRL becomes a sibling conditioning arm, P-Kit its mesh backend — no longer fallbacks). Otherwise → kill-log entry with the sheets as evidence.

## Lucas decided (2026-07-13)

1. **Backend: python flat-shaded** — "even better". Original intent: leave lighting to Foundry, since we know by construction which sprite portions belong to which voxel faces (render step can emit per-face masks for free — the parked per-face-relighting item becomes tractable in THIS lane because segmentation exists at render time, no post-hoc problem). If Foundry-side lighting doesn't pan out, ignore it and keep whatever NB's stylization gives.
2. **Arms: (b), (b+c), and (a)** — huge uncertainty, compare all three: blank-technical, blank-technical+cyan-symbols, real textures. (Clarified 2026-07-13: "(d)" meant (a).)
3. **Whole-sheet single pass** ✓.
4. **Web app manual route** ✓.

Next step once (d) is clarified: fold this memo into SCENE-CREATION P5 + ROADMAP-content-gen lane update, stage the test sheets (`design/feel-rig/stage_kit_paint.py` + guide renderer extension), Lucas runs the web-app batch.
