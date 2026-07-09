# SCENE-CREATION — Canonical Spec
> Single source of truth for isoroll scene creation: goal, architecture, contract, kill-log, program.
> Live execution state: [ROADMAP-content-gen.md](ROADMAP-content-gen.md). Superseded strategies: [archive/ROADMAP-2026H1-strategies.md](archive/ROADMAP-2026H1-strategies.md).
> Runtime counterpart: `../isoroll-module/` (see its ROADMAP.md § Scene Painter track).

## Goal

Tiny Glade-feel scene creation for isometric VTT maps: the DM paints grid cells (wall / floor / door / window / stairs), the scene re-renders instantly in a Hades-like drawn style, and mechanics (walls, height, vision, fog) register automatically. Views: **8+1** (N, NE, E, SE, S, SW, W, NW + TOP).

References: Tiny Glade (few tools + contextual grammar = the magic), Townscaper/WFC lineage, Crosshead/Dungeon Alchemist (market), AoE2 (classic grid autotiling), Hades/Bastion/Transistor (art target — drawn, not 3D-ish, not cel-shaded 3D).

## Requirements

| Tier | Requirement | How it's met |
|------|-------------|--------------|
| essential | 4+1 views | dimetric kit batch (rotation = cell remapping of same art) |
| essential | cross-view consistency (geometric AND visual) | geometry: deterministic assembly from layout; visual: kit-sheet single-pass painting + QC (IoU, cross-view dims) |
| important | outstanding usability ("feels like magic") | painter grammar (below), input redundancy, P9 polish pass |
| important | 8+1 views | cardinal kit batch (new art regime) + module cardinal projection preset |
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

**Kit assembly is the model** (pivot 2026-07-08, see kill-log): the generator (NB) only ever paints tile-sized kit pieces — the regime where it holds geometry. Scenes are composed deterministically from the layout by code (`scene_assemble.py`, later its TS port). Geometry is exact by construction; zero generator calls per scene.

### The contract (scene format)

Any painter (in-Foundry, standalone, text DSL) targets the same two artifacts:
1. **Layout grid JSON** — cells: `#` wall, `.` floor, `D` door, `W` window, `S` stairs; directives (`name`, `wall_h`, `cell`). Text DSL in `layout_parse.py` is the reference serialization.
2. **Kit + scene manifest JSON** — per piece: id, yaw/facing (8+1 vocabulary, matches module `Facing`), anchor point, px-per-voxel scale, `boundHeight`, `imageOffset`; per scene: tile placements + `WallDef[]` (validated against module `src/walls/wall-types.d.ts`).

### Scale-consistency spec

Problem (confirmed in code): `tile_guide_render.py::fit_scale` autofits each cell independently → px-per-voxel drifts between views/pieces, breaking cross-view size consistency. The hand-drawn reference deck (`src/pipeline/prompts/reference/isometric_images.pdf`) kept voxel proportions consistent across views — that property must be restored:
- One shared px-per-voxel `s` per sheet, computed from the largest piece bbox across ALL panels (never per-cell).
- `s` recorded in the kit manifest; assemblers scale by manifest value, never re-measure pixels.
- QC gains a cross-view dimension check: same piece silhouette dims across views must agree within tolerance.
- For already-generated autofit sheets: corrective per-cell scale = `s_shared / s_cell`, derivable from recorded dims — document per sheet rather than regenerate.

### 8+1 views — two art regimes

- **Dimetric regime (NW/NE/SW/SE + TOP)**: exists. Rotation = cell remapping of the same kit art (`kit_render.py`); never sprite mirroring (chirality — see kill-log).
- **Cardinal regime (N/E/S/W)**: walls seen face-on → NEW kit art per piece + a cardinal projection preset in the module (custom projection flags exist). Proportions anchored on the reference deck's conventions (unfolded-net already reverse-engineered in `make_tile_guide.py`/`tile_guide_render.py`, verified vs 2 deck pages). Guide renderer needs a cardinal camera mode; NB batch mirrors the dimetric batch process.

### Floor / background — OPEN design item (decide in P6 spike, not before)

Constraint: floor must participate in **isoroll's own fog/visibility stack** (module `src/render/fog-apply.ts`, `fog-state.ts`, `iso-tile-fog-sync.ts` — isoroll sprites sit above Foundry default fog and are darkened by isoroll's strategy; Foundry-native underfoot tiles or plain scene background would sit below the fog model). Candidates:
- (a) floor as isoroll tiles built from merged massing strips (not per-cell — slice-count sanity);
- (b) live background-image regeneration on edit (module has `transformBackground`, `backgroundYScale`, background gizmos) with fog implications prototyped.
Both get prototyped and measured (slice count / perf / fog correctness) before deciding.

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

## Program — phases (single Fable session oversees; ☐ = Lucas checkpoint)

Full plan approved 2026-07-09 (plan file: `~/.claude/plans/prompts-txt-lately-i-ve-been-witty-valiant.md`; canonical home = here + ROADMAP-content-gen.md, per PLANS-LIVE-IN-ROADMAPS).

| Ph | What | Repo | Verify | ☐ Lucas |
|----|------|------|--------|---------|
| P0 | Docs consolidation (this file, ROADMAP prune→archive, S0→8+1, goals refresh) | both + brain | links resolve; dead claims only in archive/kill-log | ☐ eyeball pending merge queue |
| P1 | `core/skills/iso-visual.md` | core | skill loads, referenced by both repos | — |
| P2 | Seam: `/loops export-manifest` → `/loops module-walls-import` (= loop-engineering `[pilot]`) | content→module | gray l-room live in Foundry: wall count matches layout, vision blocked, `verify:full` green | ☐ eyeball l-room in Foundry |
| P3 | Scale-consistency fix (shared `s`, manifest field, QC dim check) | content | pytest + QC on existing 4-view demo | — |
| P4 | TS assembler port of `scene_assemble.py` | module | golden diff TS == Python on l-room | — |
| P5 | NB kit painting, dimetric batch → postproc → painted l-room | content | IoU ≥ 0.9, residue 0, cross-view dims | ☐ run NB, drop `gen-outbox/`; style 1–5 |
| P6 | Floor/fog spike: (a) floor-tiles vs (b) background regen → DECIDE here | module | both prototypes render, fog correct, decision logged | ☐ eyeball, co-decide |
| P7 | Painter MVP: paint/erase + autotile + live re-assembly + auto WallDefs + props basic | module | paint a room in live Foundry → walls/vision/fog correct without reload | ☐ usability session |
| P8 | Multiview: dimetric view switch (cell remap + resolver facing) → cardinal (guide cams + ☐ NB batch + projection preset) | both | view toggle stable z-order (`dumpZOrderJSON`); cross-view QC | ☐ NB cardinal batch; eyeball 8 views |
| P9 | Polish: magic-feel pass, door secondary image, door webm | module | e2e + ☐ | ☐ final usability + style verdict |

Order: P0→P1→P2 strict; P3 ∥ P4 after P2; P5 after P3; P6 after P2; P7 after P4+P6 (gray kit OK if P5 lags); P8 after P5+P7; P9 last.

**Definition of "solved"**: paint a room inside Foundry → painted-style scene re-renders live in any of 8+1 views → walls/vision/fog/movement correct → assets generated by this pipeline with QC green — one spec, consistent roadmaps, zero contradicting docs.
