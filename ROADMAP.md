# isoroll-content Roadmap
> **The only live-state file for scene creation.** What's next lives here and nowhere else.
> Spec (status-free): [SCENE-CREATION.md](SCENE-CREATION.md) — goal, seam, contract, kill-log.
> Frozen decision records: [`design/`](design/CONTEXT.md).
> Superseded strategy trees: [`archive/`](archive/) — consult the kill-log before resurrecting anything.

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

**Why the pivot** (evidence, not preference): the renderer already uses world-absolute texcoords
(`texture_warp.py`), but modules are rendered at a module-local origin (`stage_kit_modules.py`) and one
sprite is pasted at every cell (`scene_assemble.py`), with `texture_map.variant()` keyed on the module's
own world column. So every `wall_band` in a scene shows identical stones and no pattern can cross a cell
join. **Reusable sprite and true cross-tile continuity are mutually exclusive** — arm A cannot deliver
continuity, arm B can, and only a bake-off with a playable product already in hand can price that
trade-off honestly.

### Decisions taken 2026-07-29 (Lucas)

| # | Decision | Consequence |
|---|---|---|
| D1 | MVP ships knowingly-ugly pixels (arm A: repeated stones, joins don't flow) | PLAYABLE needs no in-browser renderer and no bake round-trip; look is judged in BAKEOFF, not before |
| D2 | **Full 8+1 views in the MVP** (not 4+1) | cheap under a deterministic renderer: cardinal = one view-table entry (projection + backface-cull axis) + the module's existing custom-projection flags. The "new art regime" price was an NB-paints-sheets cost and does not apply |
| D3 | Merge the arm_a renderer engine to `develop` | done (2026-07-29, tag `pre-arm-a`); style-verdict gate moot since the S4t/enclosure lane is parked |
| D4 | Quality lane = **offline Python bake**; any browser renderer is preview-only | kills the "bad-quality-3D" risk: shipped pixels are always supersampled + AO + ink from the offline renderer |
| D5 | Aesthetic target = **Feather-3D / Tiny Glade**, not literal Hades | Hades is hand-painted at artist cost. Style rule to hold: non-photometric shading (flat per-face ramp, no gradients/speculars) + linework always on |
| D6 | Art cost is paid **once at texture scale** (~40 materials), never per tile | ~40 painted materials is AI-able or commissionable; 500 stitched tiles is not. Same logic for props: mesh once, render 9 views |
| D7 | Perf deferred, with one guard | unique-pixel memory scales with map area × views (draw calls do NOT change between arms). Keep `px_per_voxel` and `chunk` as manifest fields so chunking + per-view lazy bake stay possible without a format break |

## How this gets used — the workflow is the spec (read before planning any task)

Failure pattern this project keeps hitting (Lucas, 2026-07-29): agents make progress but leave **loose
ends — results that don't connect to the next step**. Three rules exist to prevent it, and they bind every
task below:

1. **Milestones are user actions, never artifacts.** A milestone is "Lucas paints a room and walks a token",
   never "the renderer interface exists". An interface is frozen *by being used end to end*, not before —
   which is why the old SEAM milestone was folded into PLAYABLE rather than kept as its own gate. Any task
   that cannot name the user action it serves is a loose end by definition.
2. **Every eye-catch becomes a code invariant.** When Lucas catches something by looking (orange mask over
   air, hairlines, phantom plates), the fix is not just the fix — it's an invariant test so it can never
   come back to him. Precedent that this works: ROUND 4's `render ∪ mask == silhouette` test made that whole
   bug class unshippable. This is the mechanism that turns 19 review rounds into 3.
3. **The user's touchpoints are budgeted and enumerated.** Lucas appears exactly twice below (PLAYABLE
   usability gate, BAKEOFF style verdict). Anything that would add a third touchpoint needs a code oracle
   first. Agents must never route a judgement to him that a test could make.

Agent self-knowledge to plan around, not wish away: **Claude is not a Foundry expert and has a weak visual
eye.** Therefore — load `/foundry` before touching module code; never assert Foundry behavior, verify it
against the live instance (`verify:full` e2e + the `isoroll.dumpZOrderJSON()` oracle); never assert geometry
from looking at an image (`core/skills/iso-visual.md` hard rule). And prototype interactions in a throwaway
rig before coding them in the module — `design/feel-rig/` is what made the frozen painter grammar cheap, and
that grammar is already bought: **reuse rig v16.2, do not re-derive it.**

## PLAYABLE — ugly, complete, in Foundry (zero generation, absorbs the old SEAM milestone)

Single user-visible outcome. The seam gets frozen by carrying the cabin all the way into Foundry.

- [ ] content: `render_scene(layout, view) -> {cell sprites, manifest}` as the single entry; arm A (today's
      kit assembly) becomes implementation A behind it, code untouched.
- [ ] content: manifest gains `px_per_voxel` + `chunk` fields (D7 guard).
- [ ] content: fixture upgrade bare l-room → **cabin** (2 rooms, door, window, stair to a platform, roof
      section, 2 materials). The l-room cannot produce a meaningful style verdict — no stairs, no roof,
      one material.
- [ ] content: golden test on the cabin (manifest + assembled PNG).
- [ ] content: cardinal camera entries in the view table (projection + cull axis) → bake the cabin sprite
      set + manifest, all **9 views** (D2), from arm A with the existing 50 linework textures.
- [ ] module: close painter MVP (`loop/painter-mvp-1@3987979`, WIP, 16 dirty).
- [ ] module: manifest → walls/vision/fog (`createWallsFromDefs`) on the cabin.
- [ ] module: view switching across 8+1 (dimetric = cell remap; cardinal = projection preset via the
      existing `customRotation`/`customSkewX`/`customSkewY`/`customRatio` flags).
- [ ] module: activate `DepthSorter` (exists, not wired — module CONTEXT.md § Known Limitations).
- [ ] module: 8-direction token sprite selection (placeholder in `object-transform.ts`).
- ☐ **Gate (Lucas), touchpoint 1 of 2:** paint a room in live Foundry, walk a token, rotate through all 9
      views. Walls, vision, fog and z-order correct. **Look is explicitly not judged here.**
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

## Parked / rerouted by this replan

| Was | Where it went |
|---|---|
| P0–P9 program (SCENE-CREATION) | retired → milestones above; the spec keeps only goal/seam/contract/kill-log |
| S1–S8 lane table (ROADMAP-content-gen.md) | file deleted, absorbed here; per-lane fates below |
| S1 `anchored-kit-marks` | stays PARKED (was already) — marks only ever mattered for NB-paints-sheets |
| S4 enclosure masks / S4t / S4b dimensional vocabulary | **PARKED, container-specific to arm A.** Work committed intact (`92b6c50`) so the lane resumes whole if arm A wins BAKEOFF |
| S5 NB round on 27 sheets | superseded by arm C (~20–40 textures instead of 27 sheets + cross-view QC) |
| S6 slice/stitch vocabulary + seam alpha ramps + per-pair ground transitions | dissolves under arm B; revisit only if arm A wins |
| S7 painter close + P7b (9 views, world-normal lighting bug) | folded into PLAYABLE |
| S8 normal maps | folded into RICHNESS |
| S0-E4/E5/E6a/E6b/E6c NB tile batches | parked with the NB-sheet regime; the S0 8+1 decision itself survives as D2 |
| Cross-view sprite QC (IoU, cross-view dims) | dissolves under arm B (a render is consistent by construction); arm A keeps it while it is the baseline |

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

- **Assess Beakman level-creation process** (INBOX 2026-07-23, ref in refs/REFS.md) — watch the
  Barrow-and-Blade reel, decide what transfers. Small scoping pass, not a build.
- **Assess PixelLab as a tool** (Lucas 2026-07-30, refs in refs/REFS.md) — two separable questions,
  do not conflate them: (1) its **tileset structure** (main / transition / lower tile, transition
  size, export to Wang / dual-grid-15 / 3x3) is a working reference for our painter grammar and for
  arm A′'s variant set — read it as design evidence, not as an asset source; (2) its **generation
  tools** (`Create isometric tile`, `Create 8-directional sprite`, `Rotate`) are pixel-art scale
  (16/32px) and therefore off-target for our Feather-3D look, and any 8-direction *generated* view
  hits the frozen rule "anything that must rotate passes through geometry" — evaluate only against
  that gate, for props/characters, never for scene cells.
- ~~**Content strategy review**~~ (INBOX 2026-07-20) — **RESOLVED by this replan** (2026-07-29): the
  structure audit is the seam + doc restructure; the stitching re-check is arm B vs arm A in BAKEOFF.
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

`make verify-fast` green (142 tests at the replan). Geometry by code, never by model eyes; style by Lucas's
eyeball on a board before any step that produced images advances — both rules in `core/skills/iso-visual.md`.
Gitflow: `main` ← `develop` ← `feature/*`; every image-producing step ends on a board.
