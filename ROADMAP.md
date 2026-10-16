# isoroll-content Roadmap
> **The only live-state file for scene creation.** What's next lives here and nowhere else.
> Spec (status-free): [SCENE-CREATION.md](SCENE-CREATION.md) — goal, seam, contract, kill-log.
> Frozen decision records: [`design/`](design/CONTEXT.md).
> Superseded strategy trees were deleted 2026-08-19 under the `.md` cap; git holds them. Consult the
> kill-log in [`SCENE-CREATION.md`](SCENE-CREATION.md) before resurrecting anything.

## Strategy — MVP-first behind a frozen seam (replan 2026-07-29, Lucas + inline)

```
DSL v2  →  [ RENDERER ]  →  cell sprites + manifest (WallDefs, boundHeight, imageOffset)  →  Foundry
              ^^^^^^^^
   swappable arms:  A kit-sprite (exists)  |  B scene-cell world-uv render  |  C NB-painted textures
```

The **contract is the structure; the pixels are swappable**. Freeze the seam, ship something playable in
Foundry with the ugliest legitimate pixels, then compare content arms behind the seam as an A/B — never
as an architecture decision. This replaces the P0–P9 program and the S1–S8 lane table (both retired
below): those made the content strategy a prerequisite for a playable product, which is what stalled
the project on per-module enclosure masks for four review rounds.

**Why the pivot:** world-absolute texture coordinates do not prevent repetition when pieces render at a module-local origin and one sprite is reused in every cell. Arm B renders each cell at its real world position; arm A′ tests matched variant sets. A playable product lets the bake-off price continuity against reusable sprites and latency.

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

## PLAYABLE — ugly, complete, in Foundry (zero generation, absorbs the old SEAM milestone)

Single user-visible outcome. The seam gets frozen by carrying the cabin all the way into Foundry.

**The user action, restated under D8 (2026-07-31):** Lucas *authors a layout as text DSL*, bakes it with
one command, imports it into Foundry, walks a token, and rotates through all 9 views with walls, vision,
fog and z-order correct. It is no longer "paints a room in live Foundry" — painting is not assumed to be
how scenes get built, so a milestone defined on it would be testing an unchosen premise.

- [ ] module: **view switching = instant in-place swap, 9 preloaded** (D9) — rotate re-textures and
      repositions each tile without a rebuild pause; walls/vision re-derived per view.
- [~] module: manifest → walls/vision/fog (`createWallsFromDefs`) on the cabin. **Import half done and
      verified live** (2026-07-30): `test/e2e/import-cabin.spec.mjs` imports the cabin manifest for all
      9 views against a running Foundry — tile and wall counts round-trip, and wall CELLS are constant
      at 51 across every view (the number isoroll-content asserts independently). Segment geometry
      is settled at CP-4; what nothing asserts yet is vision and fog behaviour on those walls — CP-6.
      Dimetric = cell remap; cardinal = projection preset via the existing `customRotation`/
      `customSkewX`/`customSkewY`/`customRatio` flags.
- [ ] module: activate `DepthSorter` (exists, not wired — module CONTEXT.md § Known Limitations).
- [ ] module: 8-direction token sprite selection (placeholder in `object-transform.ts`).
- ☐ **Gate (Lucas), touchpoint 1 of 2:** author a layout as DSL, bake it, import it, walk a token, rotate
      through all 9 views (D8). Walls, vision, fog and z-order correct. **Look is explicitly not judged
      here.**
- Before that gate can be called, agents must have verified the chain themselves: `verify:full` e2e green
  against live Foundry, `dumpZOrderJSON()` stable across all 9 view switches, wall count round-tripping
  from the layout. Lucas's gate is for *feel*, never for finding broken plumbing.
## BAKEOFF — content arms compared behind the frozen seam

- [ ] arm A: as-is (baseline, already baked by PLAYABLE).
- [ ] arm A′: **Wang/corner-tiled arm A** — arm A with a corner-matched variant SET per piece instead
      of one sprite. Added 2026-07-30 after the Wang-tile research below: this is the option that
      keeps arm A's reusable sprite (and its painter latency: pick a variant by neighbour colours, no
      re-render on a paint stroke) while making patterns cross cell joins. Cost is a bake multiplier
      (~16 variants per piece per material per family), not artist time — D6 still holds. Scope it
      against arm B *before* building it: if arm B's re-render latency turns out acceptable, A′ is
      redundant.
- [ ] arm B: scene-cell world-uv render — each cell rendered at its **real world position**, cropped by
      its own face mask. Continuity exact by construction. Invariant test: crop-and-recompose ==
      full-scene render, pixel-identical.
- [ ] arm C: NB-restyled textures (~3 first: wall stone, floor wood, roof shingle) dropped into whichever
      arm wins geometry. Code gate before eyeball: half-shift wrap-seam energy test per texture.
- [ ] Pre-registered decision rule (touchpoint 2 of 2): Lucas style score 1–5 **and** a code continuity check (cross-cell
      seam energy). Winner becomes the default arm; losers get a kill-log line.
- ☐ **Gate (Lucas):** three arms boarded side by side on the identical cabin geometry.

## RICHNESS — after a winner exists

- [ ] Props + characters: image→3D (Hunyuan3D 2.1 / TripoSR, see refs/REFS.md) → render 9 views with the
      **same** camera/light/palette as the scene. Multiview by geometry, never by generation.
- [ ] Lighting/atmosphere pass: baked AO, ink linework, edge highlight, colour grade, clutter density —
      this is where the perceived style budget actually lives (D5).
- [ ] Normal maps as a module option (S8 lane, unchanged rationale) — only if the lighting pass wants it.
- [ ] Scene generators (HunyuanWorld / NB scene images) as **art bible, not asset**: harvest palette,
      crop material patches → make tileable, extract prop inventory, use as the eyeball target. Never
      extract tiles from them (kill-log).

## Parked

- S1 anchored-kit-marks and S0-E4/E5/E6a/E6b/E6c batches wait with the NB-sheet regime; the 8+1 view decision survives as D2.
- S4 enclosure masks, S4t and S4b dimensional vocabulary are container-specific to arm A; work is preserved at 92b6c50 and resumes only if arm A wins BAKEOFF.
- S6 slice/stitch, seam alpha ramps and ground transitions return only if arm A wins. Cross-view sprite checks stay with the arm A baseline; rendered arm B is consistent by construction.

## Research finding — Wang tiles apply, and they qualify a kill-log row (2026-07-30, Lucas asked)

**Wang tiles** (square tiles with coloured EDGES, laid so touching edges match) are the standard way
to get boundless, non-periodic pattern out of a *finite, reusable* tile set. **Corner tiles** (Lagae &
Dutré 2006) colour the CORNERS instead and fix the *corner problem* — edge-coloured tiles leave
diagonal neighbours unconstrained, so continuity breaks near tile corners; corner tiles also halve
texture memory and are easier to tile. Sources in [refs/REFS.md](refs/REFS.md).

**What this means for us — the honest version:** the kill-log's "reusable sprite + true cross-tile
continuity are mutually exclusive → IMPOSSIBLE" is true for a **one-sprite-per-piece** set, which is
what arm A is today. It is **not** true for a *set*: that is precisely the problem Wang/corner tiling
solves, and it has been solved for our exact case — Derouet-Jourdan et al. build a Wang tile set for
**stochastic stone/brick wall patterns** with procedural hash-based placement, boundless, with
explicit control over "no cross" and "no long lines". Our `wall_band` is that problem. The kill-log
row is amended accordingly in SCENE-CREATION.md rather than left overstated.

Why it is a real contender and not just theory:
- **Painter latency.** A Wang/corner variant is picked from neighbour colours at paint time — O(1),
  no re-render. Arm B has to re-render the affected region on every stroke. This is the one axis
  where arm A′ can beat arm B outright, and it is an MVP-visible axis.
- **Cost stays at texture scale (D6).** Variants are *rendered*, not painted — bake multiplier, not
  artist time. Same order as the blob-47 → dual-grid ~16 reduction already in the painter grammar.
- **Corner, not edge, for us.** Floors are a 2D field where diagonal neighbours are visible, so the
  corner problem would show. Corner tiles are also what the "dual-grid" technique already in
  SCENE-CREATION.md § Painter grammar *is*.

Limits to state up front: Wang tiling gives **structural** continuity (courses line up, no seam), not
**global registration** (one mural spanning many cells) — murals stay decals. And a variant set must
be baked per projection family (×3), so D7's unique-pixel guard applies harder.

Open work (not scheduled — BAKEOFF-time, listed so it is not re-derived):
- [ ] Decide the matching unit for a 3D cell: our "edge" is a vertical seam between wall-band faces
      (1×3 voxels), not a flat square side. Corner colours would live on the module's face corners.
- [ ] The bake must be able to *produce* a variant that meets a given boundary colour. Two candidate
      routes: Cohen-2003-style graphcut from a source texture, or the Derouet-Jourdan route of
      generating the brick STRUCTURE procedurally and painting bricks — the latter fits our linework
      look and D6 better.
- [ ] Reuse the BAKEOFF cross-cell seam-energy oracle as the falsifier: it can *measure* whether A′
      reaches arm B's continuity, which is what turns this from an argument into a result.

## Backlog

- **[animater] Assess Animater** — compatibility with Isoroll projection, elevation, occlusion and asset requirements; refs/REFS.md (backlog).
- **[modder-patterns] Assess Universal Modder** — transferable discovery, asset production, live-game verification and field-note patterns against our workflow; refs/REFS.md (backlog). Respect geometry-to-sprite exports and the frozen pipeline.
- **[object-brush] Compare the demonstrated object-brush controls** with the frozen painter grammar; identify compatible improvements for Lucas to choose; refs/REFS.md (backlog).
- **[unimate] Assess UniMate** — availability, license, rig inputs, hardware, contact quality and baked-animation export requirements; refs/REFS.md (backlog). Check the geometry-based bake for eight directional views plus top.

- **Assess CapCut and Drift separately for promotional/devlog edits and table-session capture** — scope these uses before testing; neither changes sprite generation. References in refs/REFS.md; shared comparison in ../../core/ROADMAP.md (INBOX 18 Sep / 14 Oct).
- **Assess Beakman level-creation process** (INBOX 2026-07-23, ref in refs/REFS.md) — watch the
  Barrow-and-Blade reel, decide what transfers. Small scoping pass, not a build.
- **Assess PixelLab** (Lucas 2026-07-30; refs/REFS.md) — compare main/transition/lower tiles and Wang/dual-grid-15/3×3 exports with painter grammar and arm A′. Separately assess its pixel-art generation tools against the frozen geometry rule; generated rotating views cannot ship as scene cells, props or characters.
- **Assess Sprite Sheet Creator** (INBOX 2026-07-31, Lucas: “tenho que olhar isso!”; refs/REFS.md) — compare sheet layout and walk/attack/idle × eight-direction indexing with our manifest. Its prompt-generated pixel art fails the frozen geometry rule for shipped rotating assets; layout evidence remains useful. Scoping only.
- **Assess Craft RPGs as an AI VTT / RPG platform** (INBOX 2026-09-29, ref in refs/REFS.md) — check UI/UX patterns (battle maps with 5ft grid, party tokens, and AI Game Master dialogues) as design inspiration for isoroll module and content; confirmed proprietary SaaS (not open source, does not replace our offline isometric pipeline).
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
