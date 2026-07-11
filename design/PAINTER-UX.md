# Painter UX — P6.5 interaction design
> Living doc for the "feels like magic" requirement. Prototype-first: iterate here + in the feel rig BEFORE any Foundry painter code (P7 implements what this doc approves).

## Feel rig (clickable prototype)

**Play it: https://claude.ai/code/artifact/fce5e565-f376-4912-8ca7-7c19f6932ad4** (🧱, private artifact)

- Paints directly on the **isometric view** (inverse dimetric projection hit-testing) — and on TOP view; uses the REAL gray kit sprites + the same projection (`Cam.pt` twin), painter order (`scene_assemble` twin), and rotation-as-cell-remapping as the pipeline.
- Exports **real layout DSL** live — what you paint is literally `src/pipeline/layouts/*.txt` input. Copy button → run it through guide/assembly/manifest.
- Source: session scratchpad `feel-rig/` (rig.frag + build.py injects kit base64; kept out of repo — the 200-line hook gate is for product code, the rig is a design artifact hosted on the Artifact URL). Regenerable on request; update = republish same URL.

## Interaction grammar (v1 — validate in the rig)

| Interaction | Behavior | Why it feels like magic |
|---|---|---|
| Paint wall/floor (drag) | continuous strokes; runs merge by construction (massing) | no tile-picking — one tool per intent |
| Paint door/window | ONLY accepted on wall cells; axis (door_u/door_v) auto from wall-run direction, horizontal wins ties | tool refuses nonsense + orients itself; user never chooses a variant |
| Paint on non-wall with door tool | gentle hint "doors live on walls" (no error modal) | teaches the grammar in-flow |
| Rotate Q/E | true rotation (cell remap, NEVER mirror — chirality) | room "turns" in your head; hinges stay on the same side |
| TOP view (T) | orthographic plan, same paint tools | the 9th view is also an editor |
| Erase | dedicated tool + right-click anywhere | redundancy: keyboard/mouse/HUD all reach every action |
| Undo ⌃Z | full stroke granularity | fearless experimentation |
| HUD counts | walls/doors/windows/floor live | the mechanics registration made visible |

Input redundancy matrix: every action reachable by (a) tool rail click, (b) keyboard (1-5, X, Q/E, T, ⌃Z), (c) mouse gesture where natural (RMB erase). This triple-redundancy is a P7 acceptance criterion.

## Open feel-questions (Lucas iterates in the rig, answers land here)

1. Iso-paint vs TOP-paint — which is the primary editing surface in practice?
2. Rotation: instant vs short tween (~150ms)? (Tiny Glade tweens; instant may read as "teleport".)
3. Per-stroke instant re-render: enough, or do pieces want a settle/pop micro-animation?
4. First missing affordance: flood-fill floor / rectangle wall drag / shift-straight-line?
5. Stairs: rig renders procedural steps (no kit piece yet) — good enough placeholder for P7 or does S need kit art earlier?

## Decisions log

- 2026-07-10 — rig v1 published; grammar table above is the P7 baseline pending Lucas feel-session (☐ checkpoint).
- 2026-07-10 — **Lucas round 1 feedback → rig v2** (same URL):
  1. Foundry integration trust — noted; rig validates grammar only, P7 implements it as an isoroll canvas layer over the same contract.
  2. Camera control missing → ADDED: wheel zoom at cursor, MMB/Space pan, C reset. **P7 requirement: painter must never fight Foundry's own pan/zoom — reuse canvas navigation, add nothing.**
  3. Camera auto-moved on edit → FIXED: camera is user-owned; fit only on load/rotate/top/reset. **P7 rule: no camera moves on edit operations, ever.**
  4. Couldn't paint top of scene → FIXED: full-board faint diamond grid = paintable-area affordance. **P7 rule: editable extent always visible in paint mode.**
  5. Door/window unreadable in gray kit → MITIGATED: amber/cyan cell badges (editor overlay, not art). Art-level legibility = P5 painted-kit question + a "paint-mode overlays" toggle in P7.
  6. Stairs wrong shape + no orientation → FIXED: true massing wedge (4 rising slices, `_stair_boxes` twin) + directional glyphs `^>v<` (real DSL vocabulary, arrows follow view rotation); paint-again spins, R rotates hovered. **Grammar addition: re-applying a directional tool on its own cell rotates it.**
- 2026-07-10 — **Lucas rounds 2–4 → rig v3** (same URL):
  1. Magenta → cyan: kit linework remapped at load. Display-only; pipeline key-out stays magenta for now — flipping the pipeline convention would collide with cyan registration marks, needs its own decision.
  2. **Drag gestures**: wall/roof drag = straight LINE (dominant axis); floor/erase drag = RECTANGLE; ghost preview, commit on release, one undo per stroke. P7 baseline gesture set.
  3. **Openings have a SIDE**: nearest wall face under cursor (live edge highlight), re-click moves it, side rotates with view. CONTRACT GAP: layout DSL has no side field (manifest `WallDef.dir` can carry it) → queued: DSL extension `sides:` directive + massing/export wiring.
  4. **Configurable height + elevation** (UX-skill rationale: brush defaults live with the tool, property edits happen ON the object, wheel+modifier = level-editor convention): wall brush height stepper on rail; Alt+wheel over wall/stair/roof = height/rise in place; Shift+Alt+wheel = base elevation → holes/floating segments, dashed footprint marks gaps. CONTRACT GAP: DSL `wall_h` is global — queued: per-cell h/z overrides.
  5. **Stairs rise configurable** (default 1 cube) — massing already parameterizes `STAIR_RISE`; per-cell rise joins the same DSL extension.
  6. **ROOFS** (Lucas: strongly wanted, cheap on current base — CONFIRMED): tool 6; procedural gable prism; **ridge axis auto from the roof run** (same contextual rule as door axis); base defaults to wall-top z=3; Alt+wheel ridge height, Shift+Alt base. Pipeline path: roof kit pieces = 2 new NB pieces (`roof_u`/`roof_v` + gable ends) reusing the wall-piece process; runtime path: roofs = overhead tiles fading via existing occluder when tokens go inside. CONTRACT GAP: `R` char + roof dims → same DSL extension batch.

- 2026-07-10 — **Lucas round 5 (15 items) → rig v4 + design memo** (`DSL-V2-MEMO.md`, consultant agent):
  | # | Item | Decision |
  |---|---|---|
  | 1 | wall height rescaled sprite (bug) | FIX: voxel stacking — piece sprite sliced into base/unit-band/top-face; extra units tiled from wall band; no vertical scaling ever |
  | 2 | height/elevation hotkeys | ADOPTED: `+`/`-` height, `[`/`]` elevation on hovered cell; Ctrl+wheel height, Shift+wheel elevation (replaces Alt combos) |
  | 3 | drop 0.5 step | ADOPTED: integer steps |
  | 4 | stair height = stair atop (h−1) cubes | ADOPTED: render cube pedestal + wedge; mechanics = boundHeight h |
  | 5 | stairs drag as rect growing in height | ADOPTED: drag along ascent = rows rise 1,2,3…; across = wider staircase |
  | 6 | grid resize | ADOPTED: rail steppers cols/rows |
  | 7 | 4-char cells in DSL | COUNTER-PROPOSAL (memo decides): named aligned layer grids (`kind` + optional `h`/`z`/`side`/`mat`), 1 char/cell each — same expressiveness, hand-editable, unlimited layers; positional 4-char caps fields and hurts readability. NOT for implementation ease — for editability |
  | 8 | opening side renders on wrong face (bug) | FIX: openings now drawn procedurally as recess on the CHOSEN face over a plain wall stack (door/window sprites retired in rig); hidden-face sides show dimmed badge. Contract: kit needs per-face recess compositing or piece variants |
  | 9 | roofs drag-rect + configurable h/z | ADOPTED (h/z already were; drag becomes rect) |
  | 10 | stair cosmetic lines + 5 steps/voxel | ADOPTED: STEPS=5 (1 step = 1 foot @1.5m voxel…≈), no strokes on co-planar slice seams (silhouette-only outline) |
  | 11 | active elevation level (slicing grid) | ADOPTED — strong idea: editing plane at level E (PgUp/PgDn + HUD), grid drawn at z=E, new pieces default z=E, off-level pieces 20% opacity; solves roofs + multi-story. Memo defines data model |
  | 12 | hover-behind transparency | ADOPTED: occluders in front of hovered cell drop to 20% |
  | 13 | diagonal 45° walls | ACCEPTED as IMPORTANT requirement (user insists, aware of content-gen cost). Rig: procedural diagonal wall tools `/` `\`. Kit: new diagonal piece family (memo counts). Foundry walls handle angles natively |
  | 14 | component types/materials (road vs grass floor) | ACCEPTED: `mat` layer in DSL v2; kit = piece×material batches (honest multiplication — memo tables it); rig placeholder: material tint cycle |
  | 15 | adjacent openings merge (no jamb between two D) | ACCEPTED: massing merges same-kind adjacent openings into one wide recess; rig's procedural recess spans contiguous runs already |

- 2026-07-10 — **Lucas round 6 (10 items) → rig v5** (single-shot, no micro-cycles):
  1. Diagonal buttons removed → wall drag snaps 8-way (H/V/45°); corner smoothing is DERIVED at render (two wallish orthogonal neighbors forming a corner → sliced half-cube prism at min(neighbor heights)); erase a wall, smoothing follows. Derived diagonals never enter the DSL — massing owns the rule.
  2. Hover = selection: +/−, [/], Ctrl/Shift+wheel edit hovered piece AND sync the brush steppers (elevation adjust also moves the editing slice).
  3. Openings pierce the wall: hole on both faces; front face = leaf/bars (type-styled), back = dark hole; dimmed badge when front faces away.
  4. Rotation discoverability: R = spin hovered stair / toggle hovered roof ridge-axis (gable) or slope-direction (shed); tool buttons cycle brush arrow / roof form.
  5. Roof forms v1: **gable / shed (45° ramp) / flat slab**, cycled on the roof button; hip/pyramid deferred (corner kit art). Open to smarter parametric forms — discussion lives here.
  6. Slice rules v2: pieces reaching or piercing the plane render NORMAL; only pieces floating ABOVE ghost (20%) + dashed drop-line to their footprint on the plane; TOP view also slice-filtered (roofs stop hiding interiors). PgUp/PgDn = slice hotkeys.
  7. Cyan retired from art: kit linework remapped to neutral dark at load; cyan = selection/highlight only. (Pipeline linework color decision still separate.)
  8. Type cycling: M cycles the ACTIVE tool's type (floor stone/grass/road, wall stone/wood, door wood/iron, window bars/glass) with a rail chip; `layer type:` joins the DSL v2 draft.
  9. Default wall height = 2 voxels (10 ft).
  10. Q/E rotation directions inverted.

- 2026-07-10 — **Lucas round 6b → rig v5.1/v5.2**:
  - **Group-scope selection** (Lucas idea, adopted): Space toggles cell ↔ connected-group scope (HUD chip); height/elevation edits apply to the whole flood-filled component (walls+diagonals / stairs / roofs / floors families); group outlined cyan on hover. Conflict resolved: pan moved to MMB-only, Space freed for scope.
  - **Diagonals in TOP view**: stored AND derived smoothing diagonals render in plan (stroke + solid-half fill), slice-filtered like everything else.
  - **Diagonals coexist with floor**: corner smoothing derives over floor cells too (floor beneath, prism above). Stored-diag-over-floor = DSL v2 layer separation (structure vs floor layers) — memo scope.

- 2026-07-10 — **Lucas round 7 → rig v6**:
  a. Corner rule: smoothing derives ONLY when the two diagonal walls are not already joined through the cross cell (`#./.#` smooths; `##/.#` stays a corner). MASSING RULE for DSL-v2 loop.
  b. Wall groups flood 8-neighbor (diagonally-touching walls = one group).
  c. Group rotation: R in group scope rotates the whole block 90° CW around the hovered cell (positions + arrows + ridge axes + opening sides all spin); blocked with a hint if occupied/out of bounds.
  d. Shed roofs climb like stair runs (+1 z per row along slope) on drag.
  e. Type feedback: hover readout shows `ch·type h z`; tints already visible (Lucas confirmed wood).
  f. BUG fix: opening cell has TWO materials — wall's + leaf's; placing a window was overwriting the wall material (wood wall went stone). Wall material now preserved in its own map. CONTRACT NOTE: DSL v2 opening cells need both `type` (leaf) and wall-material inheritance from the run.

- 2026-07-11 — **Lucas round 8 (roof redesign) → rig v7**:
  Roofs = GROUP OBJECTS on their own layer (coexist with walls/floors — never eat grid cells). Group params: form (flat/shed1/shed2 — gable removed as a form; odd-length shed2 middle cell is the gable case, emerges from the surface formula), direction (like stairs; R rotates), inclination 1–5 ft/cell (float elevations, 0.2-voxel steps; group edit re-derives all cells from the same base → always contiguous), base z ([/] ±1 ft), enclosure none/edge/inset (V cycles; inset = EAVES: skirts on the inner contour, 1-cell overhang ring — Lucas confirmed interpretation). Surface = single formula h(u,v)=z+min(a−aLow,aHigh−a)·rise (shed2) — midline peak + odd-gable for free. Erase removes roof group first, structure second. DSL v2: roofs serialize as `roof:` group directives, not a char layer. Kills the v6 z-fighting class (roofs no longer inside the painter cell sort).
  Also this round: GEMINI key received (stored 0600, rotate later — it touched chat); quota 429 → batch armed to fire at Pacific-midnight reset (7 calls: kit sheet + 6 pieces). P6 floor=tiles recorded. P-CTRL fallback lane logged.

- 2026-07-11 — **Lucas round 9 → rig v8 (painter grammar candidate-final)** — THE SLICE IS THE SINGLE SOURCE OF TRUTH:
  0. Bug (stacked roofs at same cells + walls unreachable under roofs) → fixed structurally by 1:
  1. Roofs place AT the current slice (no +2 magic) and REPLACE overlapping roofs — same placement semantics as every other component; walls stay reachable by moving the slice.
  2. Editing plane renders as translucent sheet (bg color @50%) + grid lines.
  3. Erase is slice-scoped: only removes pieces BASED at the current elevation (hint when nothing matches).
  4. Shift+wheel over empty ground moves the slice; over a piece still adjusts its elevation.

- 2026-07-11 — **Lucas round 10 → rig v9**:
  1. TWO-PASS RENDER: pieces fully below the slice → translucent plane sheet + grid lines → everything else. The slice visually cuts the scene (grid in front of below-voxels).
  2. Roof base elevation steps whole voxels (keys/wheel).
  3. Roof groups painter-sorted by depth (min u+v) — skirts no longer jump in front of nearer roofs regardless of creation order.
  4. Slice/elevation range up to 9.
  5. PER-SIDE enclosure: V near a roof's outer edge (door-style pick, <0.3 cell) toggles that side's skirt only; V mid-roof cycles all sides (clears overrides). Data: rf.sideOv{N/E/S/W}.

- 2026-07-11 — **Lucas round 11 → rig v10**:
  1. Roof edge-hover feedback: amber thick edge segment marks the V target (door-style pick).
  2. Per-side enclosure now full 3-mode (none/edge/inset per side). Mixed-contour corners SELF-FILL: skirts are rect segments whose ends extend to the neighbor side's contour line (CSS-border-corner joining) — exact because roofs are rects by construction.
  3. TRUE SLICE CLIPPING: all drawers take (clipB,clipT]; wall sprite bands, stair pedestal voxels + wedge, diagonal prisms, opening recesses, tints all split at the plane — a 2-high wall with the slice mid-way renders 1 voxel behind the sheet, 1 in front.
  4. Elevation/slice range to 9. (round 10 item, shipped here together)

- 2026-07-11 — **Lucas round 12 → rig v11 — SCENE LAYERS (accepted, big)**:
  - Grid elevation = LAYER: the scene is a stack of independent maps (0..9), each with its own grid + attributes. Building at layer 2 never touches layer 0; walls stack (2h@0 + 2h@2 = 4 voxels). Multi-story real. All placements (walls, floors-as-platforms, doors, windows, stairs, roofs) land at the current layer; erase/hover/groups layer-scoped; [/] MOVES a piece between layers.
  - Slice cut fixed properly: instead of sprite band splitting (horizontal seams), each piece renders in both passes under a DIAGONAL ISO CLIP POLYGON at the plane (below: under the back edges; above: over the front edges; the cut diamond overlaps correctly). Works for every component type incl. wedges/prisms/recesses.
  - CONTRACT: DSL v2 becomes multi-level (`level N:` blocks, each with kind grid + attr layers); per-cell z dies (z = level). Manifest: tile elevation = level. Memo update queued.

- 2026-07-11 — **Lucas round 12b → rig v11.1 — opacity window (unifies visibility rules)**:
  Below the slice: naturally occluded by the plane's own transparency. Above the slice: fully opaque within an OPAQUE WINDOW of N voxels (default 2, min 1, stepper) above the plane; beyond it, configurable fade opacity 0–100% (default 20%, stepper; 0 = hidden). Replaces the special roof-ghost rule — one rule for everything. Droplines only for faded pieces.

- 2026-07-11 — **Lucas round 13 → rig v12 — VOXEL SEMANTICS (Minecraft-underneath, explicit)**:
  Strategy reframe confirmed: the scene's ground truth is a voxel grid; tools are brushes writing voxels; kit sprites are voxel skins. Consequences shipped: roofs claim their voxels (placing over a wall erases it at that layer); roofs render PER-CELL inside the global painter sort (fixes inter-roof z-ordering for good); the opaque-window/fade rule applies PER VOXEL (2h wall with win=1 shows exactly 1 voxel opaque) — walls, tints, openings, stairs pedestals, prisms all decompose per voxel band at render.
  CONTRACT: assembler/manifest should adopt voxel-level decomposition where mechanics need it (fog/vision already per-cell; boundHeight stays the aggregate).

- 2026-07-11 — **Lucas round 14 → rig v12.1 (two bug fixes)**:
  1. Per-voxel opacity REDONE: sprite band crops cut across diagonal face boundaries (horizontal seams + misplaced pieces Lucas caught). Now the FULL piece is drawn once per alpha-run, clipped to an ISO HEXAGON between voxel planes (back edges at top, front edges at bottom) — diagonal-perfect boundaries for every piece type. Off-by-one fixed: opaque window is strict (win=1 = exactly the plane's voxel).
  2. Voxel claiming made BIDIRECTIONAL: painting structure over a roof cell (same layer) evicts the roof group, matching roof-over-wall.
  - P5 status: API key has limit:0 for image models (no free tier on the project — same root cause as the 07-07 smoke test). Routes: AI Studio web app (free, 1 image = whole dimetric kit sheet), Google billing (~$0.04/img), OpenRouter test. ☐ Lucas picks.

**Queued contract extension (one loop, after P3/P4 ship): DSL v2** — `sides:`/`dims:` directives (or per-cell attribute block) carrying opening side, per-cell h/z, stair rise, roof cells; massing consumes; manifest export maps side→`WallDef.dir`, h/z→`boundHeight`/elevation. Feel-rig already produces the data; parser twin lands in both Python and the module's TS layout parser.
