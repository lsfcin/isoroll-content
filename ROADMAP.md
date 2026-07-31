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

### Decisions taken 2026-07-31 (Lucas, asked mid-PLAYABLE)

| # | Decision | Consequence |
|---|---|---|
| D8 | **No painter in the MVP — scenes are authored as text DSL**, baked by CLI, imported into Foundry | The in-Foundry painter is not assumed to be the way scenes get built. `loop/painter-mvp-1` is **PARKED, not closed** (work preserved at `3987979`); P7a leaves the critical path. This *changes the PLAYABLE user action* — see the milestone below — and removes the largest remaining module task. Revisit the painter only after the play loop has been felt, when it is a convenience question rather than an architecture one |
| D9 | Rotation = **instant in-place swap, all 9 views preloaded** | No rebuild pause on rotate: every family's sprites load up front, a rotate re-textures + repositions each tile in place, and walls/vision are re-derived per view. Cardinal views stay in the same rotation cycle as dimetric (not a separate mode). Prices D7's guard immediately — memory = map area × 3 sprite families — so `chunk`/`px_per_voxel` stop being theoretical the moment maps grow |
| D10 | **Walls are THIN — 1 ft, on a cell EDGE, not a 5 ft cell-filling block** | Deferred to after the PARITY ladder (Lucas, 2026-07-31), but decided now so nothing is built assuming otherwise. A wall stops being "this cell is solid" and becomes "this cell edge carries a wall", which touches the DSL's meaning, massing, the kit's `wall_band` geometry, tile placement, and the Foundry wall segment. Corner rule Lucas gave: at a junction, render each wall's **large face**; the thin end faces are not rendered. Sequencing note: everything on the ladder survives this **except the wall-sprite placement checkpoint (CP-4)**, which is placement work on geometry that is about to change — so CP-4 stays deliberately shallow (prove the mechanism on ONE wall, do not tune) and the real wall pass happens after |

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
   first. Agents must never route a judgement to him that a test could make. *Amendment 2026-07-31:*
   this budgets **judgements**, not **premises**. D8/D9 are design forks no test could settle — whether
   scenes are painted in Foundry at all, and how rotation should feel — and asking cost far less than
   building P7a under an unchosen premise would have. Ask about premises early; never ask about
   anything a test can decide.

Agent self-knowledge to plan around, not wish away: **Claude is not a Foundry expert and has a weak visual
eye.** Therefore — load `/foundry` before touching module code; never assert Foundry behavior, verify it
against the live instance (`verify:full` e2e + the `isoroll.dumpZOrderJSON()` oracle); never assert geometry
from looking at an image (`core/skills/iso-visual.md` hard rule). And prototype interactions in a throwaway
rig before coding them in the module — `design/feel-rig/` is what made the frozen painter grammar cheap, and
that grammar is already bought: **reuse rig v16.2, do not re-derive it.**

## PARITY LADDER — how the rest of PLAYABLE gets built (2026-07-31)

Lucas, after the first live cabin import: *"visuals is a hard thing for you Opus… we cannot rely on your
visual/spatial reasoning without guardrails."* He is right, and the evidence is in this repo's own rule
(`core/skills/iso-visual.md`: **model eyes never assert geometry**) which the previous session broke — a
screenshot was read as "the cabin composes" while the tiles were mis-sized, the walls mis-placed, the roofs
at floor level and the z-order wrong. All five causes were readable in code. None needed eyes.

**The guardrail: the Python assembler is ground truth, and the module must agree with it numerically.**
`scene_assemble.assemble()` already computes the exact rect every sprite occupies. The module can report the
rect every sprite actually got. Diffing those per tile catches wrong size, wrong position, wrong sprite and
missing tile — and would have caught 3 of the 5 bugs above before Foundry was ever opened.

**Working agreement (Lucas, 2026-07-31):**
1. **One checkpoint at a time.** Oracle green → board → stop → he approves → next. No chaining.
2. **Fixture ladder**: 1 cell → l-room → cabin. Each fix is proven on the smallest fixture that can show
   it. A single tile has one thing that can be wrong; the cabin has eighty-six.
3. **Board, not a hunt**: each checkpoint ships a side-by-side (Python reference | Foundry actual) plus the
   parity numbers. He glances and says go / no-go; he is never asked to find the bug.
4. **He never looks at red.** A checkpoint reaches him only with its oracle already green. His eye is for
   what numbers cannot judge — never for finding broken plumbing.
5. **Every catch of his becomes a parity assertion**, in the same commit as the fix. Nothing he has already
   caught may come back.

**The frame contract, settled by CP-2 (2026-07-31).** A baked sprite lands in Foundry by three
rules, and the first live cabin import broke all three at once:

1. **Scale by density, not by box fit.** `a * gridSize / pxPerVoxel`, where `a = cos(rotation +
   skewY) ≈ 0.894` is what a world px spends of screen width. The module used to fit the texture to
   `max(docW, docH, boundHeight)`, so tall pieces inflated past their cell — and the tile document
   was being sized from the sprite, which confused the piece's VOLUME with its picture.
2. **Anchor on `originPx`, at the footprint's screen-top corner.** The module used to put the
   texture's centre on the volume box's centre; the bake measures every sprite from the box's
   `(u0, v0, z0)` corner. The taller the sprite, the further apart those are — 149 px for a 2-high
   wall, which is what the pinned CP-2 gap was.
3. **The manifest grid is a quarter turn off the module's.** isoroll-content projects `x = u - v`,
   the module's stage projects `x = a(X + Y)`; equal pictures require `Y = u, X = -v`. Importing
   `(u,v)` straight into `(x,y)` laid every scene out a quarter turn wrong, which no per-piece nudge
   can undo. The bake cell is now carried as `flags.isoroll.cell`, since the position no longer
   spells it out.

Anything comparing a projected image (the bake, a screenshot) to world units and omitting `a` is
off by √5/2 = 1.118. CP-1's harness did exactly that and still reported sizes GREEN, because the
importer sized tiles with the same wrong number — a false green worth remembering: **two sides of a
comparison that share a derivation cannot check that derivation.**

| CP | Fixture | What it fixes | Oracle that proves it |
|----|---------|---------------|------------------------|
| 3 | l-room | Tile **position** — grid alignment across a whole flat layer. Also the first fixture with **multi-cell massing boxes**, which the manifest cannot express yet: it carries no footprint, so the importer gives every tile a 1×1 cell volume. Emit `cells: [l, d]` beside `sizePx`. | every floor tile matches; count matches |
| 4 | l-room | **One** wall placed correctly (shallow on purpose — D10 is about to change wall geometry). | one wall's rect matches |
| 5 | cabin | **Elevation** — `baseElevation` is a flag the renderer never reads; position comes from native `document.elevation`, which the importer never sets. This is why roofs sit on the floor. | platform + roof rects match the Python render |
| 6 | cabin | **Foundry wall segments** — the importer anchors every wall to an arbitrary `createdTiles[0]` in a frame one tile wide, and its normalized anchors have not been through the quarter turn. (`manifest.chunk` is read now: CP-2 needed `rows` to place anything.) | wall endpoints in world px vs layout-derived expectation; token vision blocked where the layout says |
| 7 | cabin | **Z-order** — `DepthSorter.activate()` is an empty body; the live sort is per-slice and unsliced tiles never appear in the dump. | `zOrderViolations()` empty; token occludes and is occluded correctly |
| 8 | cabin | **Rotation** (D9) — instant in-place swap. | parity green in all 9 views |

Then D10 (thin walls), then the PLAYABLE gate.

**Kit height ≠ layout height (found at CP-2, unowned).** `kit.json` bakes `wall_h: 3.0` while
`one-cell.txt` (and `cabin.txt`) declare `wall_h: 2`, so a wall SPRITE is a voxel taller than the
`boundHeight` its own manifest entry carries. Parity does not see it — both sides use the same
sprite — but the volume box, occlusion and depth sort all read `boundHeight`, so CP-7 will. Either
the kit renders at the layout's wall height, or the manifest reports the sprite's height and the
box follows it.

## PLAYABLE — ugly, complete, in Foundry (zero generation, absorbs the old SEAM milestone)

Single user-visible outcome. The seam gets frozen by carrying the cabin all the way into Foundry.

**The user action, restated under D8 (2026-07-31):** Lucas *authors a layout as text DSL*, bakes it with
one command, imports it into Foundry, walks a token, and rotates through all 9 views with walls, vision,
fog and z-order correct. It is no longer "paints a room in live Foundry" — painting is not assumed to be
how scenes get built, so a milestone defined on it would be testing an unchosen premise.

- [x] content: `render_scene(layout, view) -> {cell sprites, manifest}` as the single entry (`src/pipeline/
      render_scene.py`); arm A is implementation A behind it, in `ARMS`. Sprite sets are per projection
      FAMILY, not per view — the 4 dimetric views are cell remaps of one set, the 4 cardinal ones of
      another, so 3 sets cover all 9. CLI: `iso-cli.py bake-scene --layout <file> [--preview]`.
- [x] content: manifest gains `chunk` (index + cols/rows) beside the existing `pxPerVoxel` (D7 guard) —
      a chunked bake changes those numbers, never the file's shape.
- [x] content: fixture upgrade bare l-room → **cabin** (`src/pipeline/layouts/cabin.txt`): 2 rooms,
      interior + exterior door, window, stair up to a platform, flat roof section, stone + wood walls.
- [x] content: golden test on the cabin (`test/test_cabin_golden.py`) — manifest goldened exactly, one
      view per family; the assembled PNG is held by invariants + determinism rather than a brittle
      multi-megabyte pixel golden (it is a QC preview, not a shipped asset).
- [x] content: cardinal camera entries in the view table (`src/pipeline/view_table.py`: projection matrix
      + cull axis per family) → cabin baked in all **9 views** (D2) from arm A with the 50 linework
      textures. Three rotation loose ends had to be fixed first — group cells/ascent arrows, the
      per-cell attr overlays (materials) and ragged level frames were not being rotated, so any view
      but SW was quietly wrong.
- [—] module: ~~close painter MVP~~ — **PARKED by D8** (work preserved at `loop/painter-mvp-1@3987979`).
- [x] module: **sprite alignment** — settled at CP-2, and it was a derivation after all, not a
      measurement: density × the projection's ground factor for size, `originPx` on the footprint's
      screen-top corner for offset, plus the quarter turn between the two grids (§ PARITY LADDER,
      frame contract). Proven twice — offline in `test/unit/parity-placement.test.ts` and live in
      `test/e2e/parity-one-cell.spec.mjs`, both at 0 px error. Still open above it: multi-cell
      footprints (CP-3) and elevation (CP-5).
- [ ] module: **view switching = instant in-place swap, 9 preloaded** (D9) — rotate re-textures and
      repositions each tile without a rebuild pause; walls/vision re-derived per view.
- [~] module: manifest → walls/vision/fog (`createWallsFromDefs`) on the cabin. **Import half done and
      verified live** (2026-07-30): `test/e2e/import-cabin.spec.mjs` imports the cabin manifest for all
      9 views against a running Foundry — tile and wall counts round-trip, and wall CELLS are constant
      at 51 across every view (the number isoroll-content asserts independently). Still open: vision
      and fog behaviour on the imported walls is not asserted by anything yet, and wall anchors have
      not been through the quarter turn that CP-2 put the tiles through — see CP-6.
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
- Chain status 2026-07-30: `verify:full` **green** (127 unit + 9 e2e, 0 failed) and wall count
  **round-trips** (51 cells, every view). `dumpZOrderJSON()` across 9 view switches is **not yet
  exercised** — that needs view switching to exist first (task above). Two traps found and removed on
  the way, both worth knowing about: the e2e golden gate had been reporting a false ~10% mismatch that
  was entirely the GAME PAUSED banner over the capture (fixed in `test/e2e/golden.mjs`), and the
  manifest's `imageOffset` was never the module's quantity (see the entry above). Foundry is started
  with `--world=isoroll-test`; without the world the e2e login selector never appears.

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
