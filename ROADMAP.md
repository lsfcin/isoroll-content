# isoroll-content Roadmap
> Live scene-creation plan. Spec and kill-log: [SCENE-CREATION.md](SCENE-CREATION.md); frozen decisions: [design/](design/CONTEXT.md). Read the kill-log before reviving retired work; git holds superseded strategies.

## Agora

- [art-direction] — choose how a player brings their own art to the table.

## Art direction

**🔵 [art-direction] Player artwork in nine views**

Compare playable treatments in the Observatório das Marés encounter. Lucas approved its spatial feel and fluidity, judged the current flat low-poly style and continuous 60 fps motion insufficient, and locked the **translated** reading (Hades model: player's portrait stays in UI; character is translated into Isoroll's house style). Options, effort & panel verdicts: [design/art-direction-memo.md](design/art-direction-memo.md). [src: agent 2026-11-28]
  - **[art-direction-lab] Taste & shader lab first:** live A/B web lab at `../../outputs/isoroll-travessia/dist/lab.html` (`http://localhost:8765/lab.html`) comparing 6 code-only lenses (baseline, Hades ink/gouache, Arcane Kuwahara paint, Spider-Verse halftone, t3ssel8r/DrunkyFrog 340p pixel-3D, Moebius ligne-claire) × 3 temporal cadences (60 fps, 12 fps on 2s, 12 fps + acting/hitstop) × 2 VFX styles, beside Hades/Arcane portraits (or live uploaded portrait palette extraction) + curated Reference Wall.
  - **3D customizer candidate:** parametric articulated parts + sockets for humanoids and monsters (VLM-assisted portrait→preset translation; CSG/SDF reserved for rigid gear/props, never deforming joints).
  - **D4 (offline bake) reopen gate:** conditional on live 3D + shaders + temporal rendering crossing Lucas's visual bar at real phone scale and frame time; keep "anything that rotates passes through known geometry".
  - **Next after taste filter:** price the *second* asset (player character + narrator creature/prop) across hands-on minutes, free-tool limits, repairs, download size and phone/PC frame times before adopting a renderer. Platform comparison: `../isoroll-module/ROADMAP.md` [isoroll-2].

## Foundry production baseline (2026-07-29)

The Foundry baseline exports cell sprites and a manifest from one layout. PLAYABLE validates mechanics; BAKEOFF compares kits, world-position rendering and painted textures. Module-local textures repeat at joins.

### Decisions taken 2026-07-29 (Lucas)

| # | Decision | Consequence |
|---|---|---|
| D1 | MVP ships knowingly-ugly pixels (arm A: repeated stones, joins don't flow) | PLAYABLE needs no in-browser renderer and no bake round-trip; look is judged in BAKEOFF, not before |
| D2 | **Full 8+1 views in the MVP** (not 4+1) | cheap under a deterministic renderer: cardinal = one view-table entry (projection + backface-cull axis) + the module's existing custom-projection flags. The "new art regime" price was an NB-paints-sheets cost and does not apply |
| D4 | Quality lane = **offline Python bake**; any browser renderer is preview-only | kills the "bad-quality-3D" risk: shipped pixels are always supersampled + AO + ink from the offline renderer |
| D5 | Aesthetic target = **Feather-3D / Tiny Glade**, not literal Hades | Hades is hand-painted at artist cost. Style rule to hold: non-photometric shading (flat per-face ramp, no gradients/speculars) + linework always on |
| D6 | Art cost is paid **once at texture scale** (~40 materials), never per tile | ~40 painted materials is AI-able or commissionable; 500 stitched tiles is not. Same logic for props: mesh once, render 9 views |
| D7 | Perf deferred, with one guard | unique-pixel memory scales with map area × views (draw calls do NOT change between arms). Keep `px_per_voxel` and `chunk` as manifest fields so chunking + per-view lazy bake stay possible without a format break |

### Decisions taken 2026-07-31 (Lucas, asked mid-PLAYABLE)

| # | Decision | Consequence |
|---|---|---|
| D8 | **No painter in the MVP — scenes are authored as text DSL**, baked by CLI, imported into Foundry | The in-Foundry painter is not assumed to be the way scenes get built. `loop/painter-mvp-1` is **PARKED, not closed** (work preserved at `3987979`); P7a leaves the critical path. This *changes the PLAYABLE user action* — see the milestone below — and removes the largest remaining module task. Revisit the painter only after the play loop has been felt, when it is a convenience question rather than an architecture one |
| D9 | Rotation = **instant in-place swap, all 9 views preloaded** | No rebuild pause on rotate: every family's sprites load up front, a rotate re-textures + repositions each tile in place, and walls/vision are re-derived per view. Cardinal views stay in the same rotation cycle as dimetric (not a separate mode). Prices D7's guard immediately — memory = map area × 3 sprite families — so `chunk`/`px_per_voxel` stop being theoretical the moment maps grow |
| D10 | **Walls are THIN — 1 ft, on a cell EDGE, not a 5 ft cell-filling block** | After PARITY: change DSL, massing, kit geometry, tile placement and wall segments. At junctions render each wall's large face, never its thin end faces |

## Workflow and parity

Milestones are user actions. Every visual catch becomes a code invariant. Lucas judges PLAYABLE usability and BAKEOFF style; ask about design premises early, use tests for what tests can decide. Reuse feel-rig v16.2. Load /foundry before module code and iso-visual before visual work; verify behavior live and geometry numerically.

Python scene_assemble.assemble() is the ground truth: compare each module sprite's rect, position, identity and presence. One checkpoint at a time: smallest fixture (one cell → l-room → cabin), green oracle → side-by-side Python/Foundry board → Lucas approval. Never present a red board; each catch joins the parity tests.

Frame contract: scale by `a * gridSize / pxPerVoxel`, `a = cos(rotation + skewY)`; anchor on `originPx` at the footprint's screen-top corner; map `Y = u, X = -v`. `cells: [l,d]` transposes: l is world height, d world width. Wall definitions are bounding boxes: derive centerline along dir, apply the same turn, and assert axis alignment plus sampled points on wall tiles. A shared derivation can hide a shared error; retain independent checks and the human style gate.

Open divergence: the TypeScript massing.ts twin still strip-merges render-lane floors; its old Python goldens conceal it. Open height mismatch: kit wall_h=3 versus layout wall_h=2; align rendering or make the manifest's boundHeight describe the actual sprite.

| Checkpoint | Fixture | Pending behavior | Oracle |
|---|---|---|---|
| Elevation | cabin | Import native document.elevation rather than an unread baseElevation flag | platform/roof rects match Python |
| Walls | cabin | Verify vision, fog and movement; remove arbitrary createdTiles[0] frame dependency | blocking matches layout; walls survive frame-tile movement |
| Z-order | cabin | Activate DepthSorter; include unsliced tiles in dump | no violations; token occludes/is occluded correctly |
| Rotation | cabin | Instant in-place swap, all nine views | parity green in every view |

Then D10 thin walls, then PLAYABLE.

## PLAYABLE — walk the cabin in Foundry

- [ ] D9: preload nine views, swap tile textures and positions in place, and derive walls and vision per view. Dimetric uses cell remapping; cardinal uses the custom projection flags.
- [ ] CP-6: verify cabin vision, fog and movement. The live import test `test/e2e/import-cabin.spec.mjs` round-trips tile/wall counts at 51 wall cells in every view. CP-4 covers segment geometry.
- [ ] Activate `DepthSorter` and implement eight-direction token selection in `object-transform.ts`.
- [ ] Gate (Lucas, D8): write a layout, bake with one command, import, walk and rotate. First run `verify:full` live, check `dumpZOrderJSON()` across all views and compare wall counts with the layout. Lucas judges the interaction.
## BAKEOFF — content variants behind the export contract

- [ ] [vertex-paint] At BAKEOFF, compare per-instance mortar/efflorescence/grime masks with Wang variants and world-position baking on one repeated wall. Check cross-cell joins, nine-view consistency and variant memory; keep the frozen export contract. Ref: [refs/REFS.md](refs/REFS.md) [vertex-paint].

- [ ] arm A: as-is (baseline, already baked by PLAYABLE).
- [ ] A′: corner-matched sets (~16 variants per piece/material/family) keep neighbour-based lookup and continuous joins. Compare B's edit latency before investing in variant baking.
- [ ] arm B: scene-cell world-uv render — each cell rendered at its **real world position**, cropped by
      its own face mask. Continuity exact by construction. Invariant test: crop-and-recompose ==
      full-scene render, pixel-identical.
- [ ] arm C: NB-restyled textures (~3 first: wall stone, floor wood, roof shingle) dropped into whichever
      arm wins geometry. Code gate before eyeball: half-shift wrap-edge energy test per texture.
- [ ] Pre-registered decision rule (touchpoint 2 of 2): Lucas style score 1–5 **and** a code continuity check (cross-cell
      edge energy). Winner becomes the default arm; losers get a kill-log line.
- ☐ **Gate (Lucas):** three arms boarded side by side on the identical cabin geometry.

## RICHNESS — after a winner exists

- [ ] Props + characters: image→3D (Hunyuan3D 2.1 / TripoSR, see refs/REFS.md) → render 9 views with the
      **same** camera/light/palette as the scene. Multiview by geometry, never by generation.
- [ ] Lighting/atmosphere pass: baked AO, ink linework, edge highlight, colour grade, clutter density —
      this is where the perceived style budget actually lives (D5).
- [ ] [spritefusion-normals] Planned (Lucas, 2026-11-16): emit normal+depth maps from known bake geometry for a moving light. Compare Sprite Fusion and Pixel Art Lighter's editable normals/light masks; check channels, alpha and facing across nine views. Inferred maps are candidates, not geometric truth. [style-tests] Same bake: brush shader; low-res 3D upscaled to pixel art. Refs: [refs/REFS.md](refs/REFS.md); runtime: ../isoroll-module/ROADMAP.md.
- [ ] Scene generators (HunyuanWorld / NB scene images) as **art bible, not asset**: harvest palette,
      crop material patches → make tileable, extract prop inventory, use as the eyeball target. Never
      extract tiles from them (kill-log).

## Parked

- S1 anchored-kit-marks and S0-E4/E5/E6a/E6b/E6c batches wait with the NB-sheet regime; the 8+1 view decision survives as D2.
- S4 enclosure masks, S4t and S4b dimensional vocabulary are container-specific to arm A; work is preserved at 92b6c50 and resumes only if arm A wins BAKEOFF.
- S6 slice/stitch, edge alpha ramps and ground transitions return only if arm A wins. Cross-view sprite checks stay with the arm A baseline; rendered arm B is consistent by construction.

## Research finding — Wang tiles apply, and they qualify a kill-log row (2026-07-30, Lucas asked)

Finite Wang sets match edge colours; corner tiles also constrain diagonal neighbours, fixing corner joins, halving texture memory and simplifying tiling (Lagae & Dutré 2006). Floors need this diagonal constraint; the painter grammar's dual-grid is the same idea, including its blob-47 → ~16 reduction. Sources: [refs/REFS.md](refs/REFS.md).

The kill-log's impossibility applies to one sprite per piece, not variant sets; SCENE-CREATION.md already qualifies it. Derouet-Jourdan et al. cover our stone/brick `wall_band`: boundless, hash-placed stochastic patterns with "no cross" and "no long lines" controls.

A′ selects a neighbour-matched variant in O(1), without a paint-stroke re-render; B re-renders the affected region. This is A′'s painter-latency advantage, not a reason to restore the parked painter. Variants are rendered rather than painted, preserving D6's texture-scale art cost. Wang tiling gives structural continuity, not a globally registered mural: murals stay decals. Bake variants per projection family (×3), pricing D7's unique-pixel memory guard.

Open work (not scheduled — BAKEOFF-time, listed so it is not re-derived):
- [ ] Decide the matching unit for a 3D cell: our "edge" is a vertical edge between wall-band faces
      (1×3 voxels), not a flat square side. Corner colours would live on the module's face corners.
- [ ] The bake must be able to *produce* a variant that meets a given boundary colour. Two candidate
      routes: Cohen-2003-style graphcut from a source texture, or the Derouet-Jourdan route of
      generating the brick STRUCTURE procedurally and painting bricks — the latter fits our linework
      look and D6 better.
- [ ] Reuse the BAKEOFF cross-cell edge-energy oracle as the falsifier: it can *measure* whether A′
      reaches arm B's continuity, which is what turns this from an argument into a result.

## Backlog

- [ ] [ludo-directional] Seriously assess Ludo's concept → 3D → rig → directional-sheet method for characters: licences/usage rights, exports/API, public code and reproducible implementation or reverse engineering of the demonstrated workflow. Compare eight views, animation indexing, scale and alpha with our geometry-based bake; top view remains to verify. Ref: [refs/REFS.md](refs/REFS.md) [ludo-directional].
- [ ] [diorama] Assess Diorama's palette/dither/ink, joint animation and per-entity frame checks on one offline-bake example. Separate transferable techniques from its browser runtime; preserve nine-view geometry and export requirements. Ref: [refs/REFS.md](refs/REFS.md) [diorama]; platform comparison: ../isoroll-module/ROADMAP.md [isoroll-2].

- [ ] [t3-video] Assess T3-Video hardware requirements, licence, runtime and usefulness for visual assets and teaching before selecting a trial. Preserve the frozen geometry-to-sprite contract. Ref: refs/REFS.md [t3-video] (Instagram lead).

- [ ] [soundbox] Assess Soundbox for offline sound effects and ambience assets, checking machine compatibility, model licenses and export workflow. Ref: refs/REFS.md [soundbox].
- [ ] [idol] Assess Gaussian-splat offline prop views against the frozen contract: hidden surfaces, transparency, scale, renderer, hardware and licences. Splats are not meshes or verified collision geometry. Ref: refs/REFS.md [idol].

- [ ] [scenario-3d-os] Avaliar 3D OS (Scenario) e suas 80 skills de agentes para acelerar o pipeline de geração offline de assets e sprites 3D/isométricos. Ref: refs/REFS.md [scenario-3d-os].

- [ ] [isoroll-environment-life] Compare one bounded environmental-life example with our geometry, sprite, animation and playback constraints before Lucas judges the achievable style. Ref: refs/REFS.md [isoroll-environment-life].

- [ ] [gpu-unlock] Assess whether any supported compute-bound workload transfers to our actual GPU and pipeline, keeping hardware, precision, power and whole-task results distinct. Ref: refs/REFS.md [gpu-unlock].

- [ ] [anatomy] Assess Anatomy on one bounded isometric/temporal example, separating editable browser geometry from verified scene semantics, offline sprites and Foundry playback. Ref: refs/REFS.md [anatomy].

- [ ] [rated-tools] Assess Higgsfield media export, rights, retention and reproducibility for illustrations; it does not establish the sprite/geometry contract. Ref: refs/REFS.md [rated-tools].

- [ ] [web-motion] Assess web-motion preview/playback fit, preserving deterministic geometry and the offline sprite pipeline. Ref: refs/REFS.md [web-motion].

- [ ] [pixelfx-sheets] Avaliar o exportador de sprite sheets e o vocabulário de acting (wind-up, freeze on contact, recovery) do patch-gg/pixelfx para a pipeline de animações do isoroll (ref em refs/REFS.md).
- [ ] [nvidia-motionbricks] Avaliar transferibilidade do NVIDIA MotionBricks para rig e animação de personagens na pipeline offline (ref em refs/REFS.md).
- [ ] [qwen-turbo-comfy] Avaliar compatibilidade e consumo de VRAM do encoder GGUF do Qwen-Image-2.1-Turbo na lane utilitária do ComfyUI vs SDXL/NanoBanana (ref em refs/REFS.md).

- **[animater] Assess Animater** — compatibility with Isoroll projection, elevation, occlusion and asset requirements; refs/REFS.md (backlog).
- **[modder-patterns] Assess Universal Modder** — transferable discovery, asset production, live-game verification and field-note patterns against our workflow; refs/REFS.md (backlog). Respect geometry-to-sprite exports and the frozen pipeline.
- **[object-brush] Compare the demonstrated object-brush controls** with the frozen painter grammar; identify compatible improvements for Lucas to choose; refs/REFS.md (backlog).
- **[unimate] Assess UniMate** — availability, license, rig inputs, hardware, contact quality and baked-animation export requirements; refs/REFS.md (backlog). Check the geometry-based bake for eight directional views plus top.

- **Assess CapCut and Drift separately for promotional/devlog edits and table-session capture** — scope these uses before testing; neither changes sprite generation. References in refs/REFS.md; shared comparison in ../../core/ROADMAP.md (INBOX 18 Sep / 14 Oct).
- **Assess Beakman level-creation process** (INBOX 2026-07-23, ref in refs/REFS.md) — watch the
  Barrow-and-Blade reel, decide what transfers. Small scoping pass, not a build.
- **Assess PixelLab** (Lucas 2026-07-30; refs/REFS.md) — compare main/transition/lower tiles and Wang/dual-grid-15/3×3 exports with painter grammar and arm A′. Separately assess its pixel-art generation tools against the frozen geometry rule; generated rotating views cannot ship as scene cells, props or characters.
- **Assess Sprite Sheet Creator** (Lucas, 31 Jul; refs/REFS.md) — compare layout and walk/attack/idle × eight-direction indexing with our manifest. Generated rotating views fail the frozen geometry rule; assess layout only.
- **Assess Craft RPGs** (29 Sep; refs/REFS.md) — assess 5ft maps, party tokens and AI Game Master dialogues for module/content design. Proprietary hosted service; preserves our offline pipeline.
- **Brightness QC post-batch** — opaque-mean < 10 → flag (PIL, cheap). Would have caught the 32 black
  frames of 2026-05-27 immediately.
- **`getdata` deprecated (Pillow 14)** — `sheet_grid.py:63`, `sheet_qc.py:34`, and the test suite.

## Chores (independent of scene creation)

- [ ] `README.md` once the CLI contract stabilizes.
- [ ] `iso-cli`: `--seed` for reproducible generations; `argparse` instead of manual `sys.argv` indexing;
      `doctor` command (ComfyUI connectivity, `COMFY_DIR`, required node classes); output tracking via
      ComfyUI `/history` + `prompt_id`; batch mode (multiple prompts / seed range).
- [ ] `cli/sprite_splitter.py`: 5-panel layouts → `tiles/{name}/{name}_{facing}.png` + rembg (character
      lane, unaffected by the replan).

## Verification

`make verify-fast`. Geometry by code, never by model eyes; style by Lucas's
eyeball on a board before any step that produced images advances — both rules in `core/skills/iso-visual.md`.
Gitflow: `main` ← `develop` ← `feature/*`; every image-producing step ends on a board.
