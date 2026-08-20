# SCENE-CREATION — Canonical Spec
> Single source of truth for isoroll scene creation: goal, architecture, seam, contract, kill-log.
> **Status-free by rule** — no phases, no task state, no "current focus". What's next lives only in
> [ROADMAP.md](ROADMAP.md). The superseded 2026-H1 strategy tree was deleted 2026-08-19 under the
> `.md` cap — git holds it, and the one recipe anything still pointed at is inlined in
> [design/RENDER-RESTYLE-MEMO.md](design/RENDER-RESTYLE-MEMO.md).
> Runtime counterpart: `../isoroll-module/` (see its ROADMAP.md § Scene Painter track).

## Goal

Tiny Glade-feel scene creation for isometric VTT maps: the DM paints grid cells (wall / floor / door / window / stairs), the scene re-renders instantly in a Hades-like drawn style, and mechanics (walls, height, vision, fog) register automatically. Views: **8+1** (N, NE, E, SE, S, SW, W, NW + TOP).

References: Tiny Glade (few tools + contextual grammar = the magic), Townscaper/WFC lineage, Crosshead/Dungeon Alchemist (market), AoE2 (classic grid autotiling), Hades/Bastion/Transistor (art target — drawn, not 3D-ish, not cel-shaded 3D).

## Requirements

| Tier | Requirement | How it's met |
|------|-------------|--------------|
| essential | 8+1 views | one view-table entry per view (projection + backface-cull axis) + the module's cardinal projection preset; dimetric rotation = cell remapping of the same art |
| essential | cross-view consistency (geometric AND visual) | geometry: deterministic assembly from layout. Visual: free in any render-based arm (a render is consistent by construction); arm A pays for it with cross-view QC (IoU, cross-view dims) |
| essential | cross-tile continuity (patterns flow across cell joins) | requires cells rendered at their real world position (arm B) — unreachable with reusable sprites, see kill-log |
| important | outstanding usability ("feels like magic") | painter grammar (below), input redundancy, polish pass |
| important | content generated without artists | art cost paid once at texture scale (~40 seamless materials, code-verifiable by wrap-seam test) + props as meshes rendered to 9 views; never per-tile painting |
| desired | door animations | door secondary image (open/closed) first; webm tiles later |

## Architecture

```
isoroll-content (Python, generator)         CONTRACT                    isoroll-module (TS, runtime + painter)
───────────────────────────────────         ────────────────            ──────────────────────────────────────
guide: DSL → massing → guide render         layout grid JSON            walls-import: manifest → createWallsFromDefs
kit: NB paints kit sheets (8 yaws:          kit manifest:                 + tile placement
  dimetric remap + cardinal new art)          piece, yaw, anchor,       TS assembler (per-cell paste, port of
QC: code not eyes (IoU, residue,              px-per-voxel scale,         scene_assemble.py)
  cross-view dimension check)                 boundHeight,              Painter UI (canvas layer): paint/erase →
export: kit + scene manifest                  imageOffset, WallDef[]      autotile → live re-assembly → WallDefs
                                                                        views: dimetric = cell remap;
                                                                          cardinal = 2nd projection preset
```

**Deterministic geometry is the model** (pivot 2026-07-08, see kill-log): a generator never decides where
anything is. Scenes are composed from the layout by code; geometry is exact by construction, with zero
generator calls per scene.

### The seam (frozen 2026-07-29)

```
DSL v2  →  [ RENDERER ]  →  cell sprites + manifest  →  Foundry
              ^^^^^^^^
   arms:  A kit-sprite  |  B scene-cell world-uv render  |  C NB-painted textures into A or B
```

`render_scene(layout, view) -> {cell sprites, manifest}` is the single entry every arm implements. **The
contract is the structure; the pixels are swappable** — choosing a content arm is an A/B behind this seam,
never an architecture change. Arm selection state lives in ROADMAP.md, not here.

Two properties are seam-level, not arm-level:
- **Quality lane = offline bake.** Shipped pixels always come from the offline renderer (supersampled, baked
  AO, ink). Any in-browser renderer is a preview for painter latency only, never a source of shipped art.
- **Anything that must rotate passes through geometry.** No exceptions: a rotating asset is a render of
  known geometry (scene cells, or a mesh for props/characters), never a generated view.

Arm A (kit-sprite) reuses one sprite per module at every cell. Consequence, confirmed in code and not
negotiable: **reusable sprite and true cross-tile continuity are mutually exclusive** — see kill-log.

### The contract (scene format)

Any painter (in-Foundry, standalone, text DSL) targets the same two artifacts:
1. **Layout grid JSON** — **DSL v2, FROZEN 2026-07-13 @ rig v16.2**: multi-level `level N:` blocks (one char per VOXEL: `#` wall, `.` floor, `D`/`W` opening voxels, `/`/`\` diagonals; `R`/`S` group voxels DERIVED, never authored), attr grids `layer side:/type:/wmat:/fh:` (1 char/cell), `roof:`/`stair:` group lines (authoritative: form, dir, incl, z, enclose). Normative reference = `design/feel-rig/rig.frag` (`updateDsl`, `grpBaseData`/`grpCellVoxels`, run merging) + `design/PAINTER-UX.md` rounds 12–19. v1 single-grid syntax (`layout_parse.py`) is superseded — parser v2 lands via loop D1.
2. **Kit + scene manifest JSON** — per piece: id, yaw/facing (8+1 vocabulary, matches module `Facing`), anchor point, px-per-voxel scale, `boundHeight`, `imageOffset`; per scene: tile placements + `WallDef[]` (validated against module `src/walls/wall-types.d.ts`).

### Scale-consistency spec

Problem (confirmed in code): `tile_guide_render.py::fit_scale` autofits each cell independently → px-per-voxel drifts between views/pieces, breaking cross-view size consistency. The hand-drawn reference deck (`src/pipeline/prompts/reference/isometric_images.pdf`) kept voxel proportions consistent across views — that property must be restored:
- One shared px-per-voxel `s` per sheet, computed from the largest piece bbox across ALL panels (never per-cell).
- `s` recorded in the kit manifest; assemblers scale by manifest value, never re-measure pixels.
- QC gains a cross-view dimension check: same piece silhouette dims across views must agree within tolerance.
- For already-generated autofit sheets: corrective per-cell scale = `s_shared / s_cell`, derivable from recorded dims — document per sheet rather than regenerate.

### 8+1 views

- **Dimetric (NW/NE/SW/SE + TOP)**: rotation = cell remapping of the same art (`kit_render.py`); never sprite mirroring (chirality — see kill-log).
- **Cardinal (N/E/S/W)**: walls seen face-on. Under a **deterministic renderer** this is one entry in the view table (projection matrix + backface-cull axis, both already per-view parameters) plus the module's cardinal projection preset, which the existing `customRotation`/`customSkewX`/`customSkewY`/`customRatio` flags already cover. Proportions anchored on the reference deck's conventions (unfolded net reverse-engineered in `make_tile_guide.py`/`tile_guide_render.py`, verified vs 2 deck pages).
- Cardinal is only a **new art regime** where the pixels come from generated per-piece sheets (arm A + NB). It is nearly free in any render-based arm — which is why 8+1 is in scope from the MVP onward.

### Floor / background — OPEN design item (spiked, decision still with Lucas)

Constraint: floor must participate in **isoroll's own fog/visibility stack** (module `src/render/fog-apply.ts`, `fog-state.ts`, `iso-tile-fog-sync.ts` — isoroll sprites sit above Foundry default fog and are darkened by isoroll's strategy; Foundry-native underfoot tiles or plain scene background would sit below the fog model). Candidates:
- (a) floor as isoroll tiles built from merged massing strips (not per-cell — slice-count sanity);
- (b) live background-image regeneration on edit (module has `transformBackground`, `backgroundYScale`, background gizmos) with fog implications prototyped.

**Spiked** (`isoroll-module/.craft/floor-fog-spike`, live-Foundry e2e, l-room fixture, SW view, oracle-verified via sprite tint — not eyeballed):

| Metric | (a) floor-as-iso-tiles | (b) background regen |
|---|---|---|
| Tile / slice count (sort-tick load proxy) | 6 tiles / 24 slices | 0 / 0 (not part of the tile stack) |
| Fog participation | full — reads isoroll's tint/alpha model | **0** — measured `fogParticipation` = 0 extra fog-stack rows on bg swap |
| Fog-state correctness | unseen 0 / explored 18 / visible 6 / total 24 (darkenedFraction 0.75) across a visible→explored transition, oracle-verified | n/a — renders at full clarity regardless of fog/token-vision state (structural gap, not partial) |
| Edit latency | not isolated (tile create + fog-sync settled inside fixed waits) | ~670ms mean of 3 runs (`canvas.scene.update` + settle) |

**Evidence-based recommendation:** (a) is the only fog-correct option — verified, not assumed. (b) has a complete fog gap (background floor stays fully lit under unexplored fog), so it is not viable as a *substitute* for the floor; it could only be considered as a decorative layer *under* (a)'s fog-tiled floor, which was not prototyped and is not part of this evidence. Full write-up: `isoroll-module/.craft/floor-fog-spike/5-user.md`.

**DECIDED 2026-07-10 (Lucas): floor = iso-tiles (a).** Caveat accepted with a guard: P7 adds a slice-count perf gate (merged massing strips keep counts low — l-room floor = 6 tiles/24 slices; if large maps degrade, fall back to chunked mega-strips before reconsidering).

### Lighting

Kit art is painted flat-lit / neutral (the guide's grayscale face ramp pre-shades lit-from-above). Scene shading comes from isoroll fog stack + Foundry lighting (Wall Height ecosystem). Pre-baked AO in pieces allowed. **Per-face relighting of painted sprites is PARKED** — faces can't be separated post-hoc without a segmentation problem; revisit only with evidence.

### Props (tables, chairs, paintings…)

Separate layer from the structural kit: single sprites with a grid footprint and a defined size range; optional free-scale override for outliers (the GIANT chair for a GIANT character) — plain scale, no grid plumbing.

### Painter grammar (design principles for the module painter)

- FEW tools, contextual reactions: painting `D` on a wall run = opening by construction (massing already models openings as recesses); wall meeting wall = junction piece auto-picked.
- Autotiling is a solved problem — reuse: blob/Wang bitmask (neighbors → variant), dual-grid technique cuts the blob-47 set to ~16 pieces per terrain. Piece taxonomy (from 2026-05 design, still valid): `straight, corner_in, corner_out, end, T, cross` + standalone PILLAR covering junction joins (pieces abut on cell edges, never share a cell — depth sort can't disambiguate co-cell z).
- Input redundancy: keyboard shortcuts + mouse interactions + HUD buttons for every action; view rotation always available.
- WFC/grammar: optional later layer for procedural decoration, not required for the painter MVP.

## LLM-spatial rule (hard rule for all agents/models in this program)

Confirmed empirically (kill-log): image models hold geometry at TILE scale, not SCENE scale; LLM agents misjudge spatial/visual relations (which thing is on top, E↔W flips).
- **Geometry lives in TEXT** (layout DSL, massing boxes, manifests) and is **verified by CODE** (silhouette IoU ≥ 0.9, mark residue, cross-view dims, wall-count round-trips).
- Model eyes never assert geometry. Read-image is allowed only for coarse sanity (does a file render, is it obviously blank/rotated).
- **Style is judged by human eyeball** — a gitflow gate before visual merges.
- Conventions + failure modes for agents: `core/skills/iso-visual.md`.

## Kill-log (dead ends — do not resurrect without new evidence)

| What | Verdict | Evidence |
|------|---------|----------|
| Single-pass whole-scene NB generation | **DEAD** (2026-07-08 test-to-kill, pre-registered) | style PASS, geometry FAIL: footprint diverged between panels (NE was a different room), floating registration symbols re-read as legend/callouts + hallucinated caption |
| Scene-scale registration marks / anchors apparatus | **PARKED at scene scale** — keep at tile/kit-sheet scale (validated regime) | built for the killed single-pass approach; kit assembly solves scene geometry by construction |
| Single-pass full tilemap generation (Backlog idea 2026-07) | **DEAD** — same failure mode as above at even larger scale | superseded by kit assembly |
| Sprite mirroring for view rotation | **DEAD** | mirror flips chirality (door hinges, stair spirals — S0-E6-fix2/3/4); rotation = cell remapping only |
| Local SD1.5/SDXL as primary generator | **DEAD** — ComfyUI demoted to utility rail (rembg, upscale, SAM2, LaMa) | horrible artifacts for characters; architecturally wrong for viewpoint (ROADMAP S, archive) |
| Per-face sprite relighting at render time | **PARKED** | requires post-hoc face segmentation; flat-lit art + runtime fog/lighting covers it |
| opencode/external models writing repo code | **BANNED** | kimi 2026-07 corrupted-stub precedent; allowed only for notebooks/disposable experiments |
| ONE reusable sprite per piece + true cross-tile continuity, together | **IMPOSSIBLE for a single sprite; NOT impossible for a tile SET** (2026-07-29, read from the code; amended 2026-07-30 by the Wang-tile research) | `texture_warp.py` uses world-absolute texcoords, but `stage_kit_modules.py` renders each module at a module-local origin and `scene_assemble.py` pastes that one sprite at every cell, with `texture_map.variant()` keyed on the module's own world column. Every `wall_band` therefore shows identical stones and no pattern crosses a cell join. Two ways out, not one: render each cell at its **real world position** (arm B), or give each piece a **corner-matched variant set** so the boundary pattern is what a neighbour agrees on (arm A′ — Wang/corner tiles, and the exact case of stochastic wall patterns has published prior art; see ROADMAP § Research finding + refs/REFS.md). The original row overstated "impossible" by generalizing from a one-sprite set |
| Per-module enclosure masks (stair lateral wedges, roof gables handed to assembly) | **PARKED — container artefact** (2026-07-29) | exists only because a module is rendered in isolation, so enclosure geometry has no wall behind it. In a scene render the stair's lateral face is an ordinary face at its world position, occluded by whatever is actually there. Four review rounds (R2-3 → R4b) were spent on this. Work preserved intact at `92b6c50`; resume only if arm A wins the bake-off |
| Slice/stitch vocabulary (cap-left / middle-repeat / cap-right), seam alpha ramps, per-material-pair ground transitions | **PARKED — same cause** (2026-07-29) | bookkeeping generated by "reusable sprite" as the unit; dissolves when cells are rendered in place |
| Tile extraction from a generated whole-scene image | **DEAD** (reaffirmed 2026-07-29) | baked light + perspective won't recombine, no grid registration, no rotation path. Scene generators are an **art bible** (palette, material patches, prop inventory, eyeball target), never an asset source |

## Program

Retired 2026-07-29. The P0–P9 phase table made the content strategy a prerequisite for a playable product,
which stalled the project on arm-A container artefacts. Milestones, gates and arm state now live only in
[ROADMAP.md](ROADMAP.md). The frozen decisions those phases
produced are still normative here (seam, contract, floor=iso-tiles, painter grammar, LLM-spatial rule) and in
[`design/`](design/CONTEXT.md) (painter UX grammar @ rig v16.2, render→restyle, S4 rounds in `archive/`).

**Definition of "solved"** (unchanged): paint a room inside Foundry → the scene re-renders in any of 8+1 views
→ walls/vision/fog/movement correct → assets produced by this pipeline with QC green — one spec, one live
roadmap, zero contradicting docs.
