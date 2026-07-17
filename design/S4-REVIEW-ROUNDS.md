# S4 REVIEW ROUNDS — Lucas's 5 points on arm_a gate (2026-07-16)
> Status: ROUND 1 open. Protocol: discuss → agree strategy per point → solve point by point,
> Lucas checks each result before next. NO bulk execution.
> Source: Lucas review of board (arm-a-homography @ 9d8d3d6). Supersedes conflicting prior decisions where noted.

## P1 — drop arms b/bc (DECIDED, mechanical)
Focus = arm a only. Stop staging b/bc; delete their sheets from gen-inbox.
Keep arm_b/arm_bc CODE parked (cheap, tested; S5 test-to-kill may want a comparison arm) — delete only output.
Supersedes: D2 "3 arms together" (RENDER-RESTYLE-MEMO).
Effort: trivial, folds into P2 session.

## P2 — resolution + subpixel policy (DECIDED, mechanical)
Sheets 352×136 unusable: textures read as noise. Root cause: linework PNGs warped onto tiny quads,
no resampling policy → aliasing.
Strategy: cell_px 64 → 256 (4× linear, 16× pixels); warp with bicubic resampling; supersample 2×
then area-downsample if bicubic alone still noisy. One light session, re-gate on board.

## P3 — doors/windows = separate thin objects (DESIGN CHANGE, discuss)
Lucas's model (supersedes recess_door/recess_window modules):
- Door/window occupies its voxel — NO wall there. Wall gets a HOLE; door/window object placed in it.
- Sprite generation independent: walls never multiply by opening combinatorics.
- Painter placement: object inset 15% into the voxel (not skinned on the face plane).
Wins: kills wall×opening combination explosion (helps P5); door sizes become their own object family.
OPEN QUESTIONS (round 1, for Lucas):
  Q1 hole borders: wall run interrupted by hole exposes CUT faces (jamb sides, lintel underside).
     Textured as wall material? Rendered as part of the wall module (wall_hole variant) or emerge
     from assembly of 1-voxel wall columns?
  Q2 door thickness: thin slab (~0.15–0.3 voxel, visible edge at oblique yaws, real 3D box) or
     flat quad (no edge)? 15% inset suggests slab — confirm.
  Q3 windows: opening is z1..2 only → wall remains BELOW and ABOVE. Is the window voxel a full
     column hole too (simpler, window object carries blank top/bottom filler) or partial hole
     (wall keeps under/over segments — reintroduces wall-with-opening geometry)?
Effort after answers: kit_modules (remove recess_*, add hole handling + door/window objects),
texture_map remap, massing/manifest placement rule (15% inset), painter/module side later (S7).

## P4 — slicing/stitching prototype BEFORE NB (VALID, = S4t extended)
Lucas wants: guide sheets as fake NB output → slice (visualize cuts as dashed orange lines on image)
→ stitch/assemble test scene. Prove adaptive compounding (4-voxel walls, big doors) BEFORE any generation.
Honest state: S4t dry-run was already planned (roadmap row); slice/costura spec exists only as one
line (S6: crop + horizontal margin + ~20px alpha-ramp). NOT yet thought through: slice vocabulary
for arbitrary run lengths (cap-left / middle-repeat / cap-right), seam policy between repeated
module crops, multi-voxel door interplay. Lucas's concern is right — sheets may need extra pieces.
Strategy: after P2 (readable sheets) + P3 decision, run S4t prototype: assemble 1 test scene from
current sheets, emit cut-line overlay board (dashed orange), derive the missing-piece list from what
breaks. Prototype answers P4 and feeds P5 inventory. Gate: assembled scene on board.

## P5 — missing components (YES — inventory in round 2)
Current set: base, wall_band, top_cap, diag_half, roof_cell, stair_45, stair_half (+recess_* dying per P3).
Known missing (first pass): wall corners/L, T-junctions, wall end caps, wall heights (1,2,4),
multi-voxel wall runs (or slice-vocab per P4), door family 1x1..2x3 as objects (P3), window family,
ground tiles (grass/road/dirt exist as TEXTURES, no module), curbs (S6 masks), roof ridge/edge/hip,
columns/pillars. Inventory finalized in round 2 AFTER P3+P4 decisions (both change what a
"component" is). = S4b scope.

## Execution order (agreed protocol: check-in after each)
1. P1+P2 one light session → re-gate board (Lucas eyeball).
2. P3 round-1 answers (Q1–Q3) → design memo update → implement module changes → gate.
3. P4 S4t prototype with cut-line board → gate.
4. P5 inventory from prototype findings → S4b list → Lucas approves → build.

## ROUND 1 ANSWERS (Lucas 2026-07-16)
- Q1: hole is EMERGENT — wall assembles from 1-voxel columns, hole = column not placed. Hole may stay
  empty; DM/user optionally places a door/window object there.
- Q2: door = real thin slab, thickness 0.1 voxel, placed 10% inwards of the hole voxel (placement and
  thickness are separate; both 10% = "feet" measurement system). Texture pasted on front AND back
  faces, back FLIPPED so handle/keyhole sits on the same physical edge — physically correct continuity
  of one object seen from both sides, NOT the forbidden sprite-mirror (orientation band still applies).
- Q3: windows identical mechanics to doors — full-voxel hole, own slab object, 10% in / 0.1 thick.
- P4: detail when reached; Lucas anticipates tile-sheet adaptations. P5: inventory after P3+P4.

## P6 (NEW) — normal maps perf + TEXTURE-FIRST strategic fork (Lucas question, round 1)
Question: (a) normal-map shader too costly for Foundry? (b) if cheap → point NB at TEXTURES instead of
final sprites — simpler content generation?
Assessment (a): feasible, moderate risk. Cost drivers: extra texture memory (albedo+normal) and DRAW
CALLS — naive per-sprite shader breaks PIXI batching. Mitigations: ONE shared shader for the whole
layer + texture atlas (PIXI batches by shader+texture), cap shader lights at 4-8 nearest, ship as
module OPTION with plain-sprite fallback (already the S8 plan). Typical VTT scene (hundreds of sprites,
few lights) is light load vs what Foundry's own lighting layer already does per-pixel.
Assessment (b): texture-first does NOT require normal maps — grayscale face ramp (FACE_TOP/LONG/CAP)
is baked flat shading at zero runtime cost; normal maps = optional enhancement (B28 world-normal fix
rides the same machinery). Texture-first wins: cross-view consistency problem disappears (one texture
reused everywhere), no silhouette QC, P4 slicing largely DISSOLVES (assembly warps textures directly,
seams correct by construction), NB task = restyle a flat tiling texture = easiest regime, continuity
testable by code. Style-ceiling risk: loses NB per-view painterly light/AO; mitigable via painterly
texture style + baked per-face AO (geometry known at render time) + linework overlay.
Key fact: arm_a machinery just built IS the texture-first engine — NB-painted textures drop in 1:1 via
textures.json, replacing linework PNGs. S5 becomes "NB paints ~20 textures" instead of "27 sheets + QC".
Proposed cheap fork test (post P1/P2): NB restyles 2-3 textures → warp → board, next to a sheet-restyle
arm. Decision by eyeball + code QC. NOT decided — discussion open.

## P1+P2 executed (2026-07-16)
P1: `stage_kit_modules.stage()` now writes ONLY `{module}__a.png` / `{module}__a_prompt.txt`
(9 stem pairs, one per module) — arm_b/arm_bc functions stay in code, still unit-tested directly
in test_stage_kit_modules.py, just no longer called from `stage()`. Deleted the 36 stale
`*__b.png`/`*__bc.png` sheets + prompt txts from output/gen-inbox/ (gitignored) and restaged fresh.

P2: `CELL_PX` 64 → 256 (4× linear) in stage_kit_modules.py; `s` is still recovered from the
manifest-derived shared scale, never re-measured. Sheets are now 1312×520 (was 352×136) —
GUTTER stayed at 8px so the total isn't an exact 4×, but the cell itself (the thing that was
unreadable) is.

Resample policy chosen (texture_warp.py, split into new `texture_resample.py` to stay under the
per-file line gate): PIL `Image.transform(..., resample=BICUBIC)` everywhere (was BILINEAR), plus
a source-density guard (`match_source_density`) that BICUBIC-upscales the tiled/decal source before
the perspective/affine warp whenever the destination screen quad would otherwise force the warp to
magnify a too-small source (<1 source px per output px) — this was the actual root cause of the
352×136 "noise" sheets, not just the small cell size.

Linework PNGs were below the 256 px/voxel-unit floor (128 px/voxel-unit, from `linework.T=128` at
1:1 raster). Added `linework.RASTER_SCALE = 2` and pass `scale=RASTER_SCALE` to `cairosvg.svg2png` —
SVG design coordinates (courses, joints, door/window proportions) are untouched, only the raster
density doubled to 256 px/voxel-unit. Regenerated all 50 textures via `linework.build_set()`; only
`assets/textures/png/*.png` changed (svg/ and textures.json are byte-identical — dims aren't
recorded in the manifest, so no schema bump needed).

Self-check: rendered `wall_band` and `roof_cell` arm-a sheets at full 256px cell and eyeballed
(via image read, not model judgment of geometry — iso-visual HARD RULE respected, this was only a
resample-artifact check). BICUBIC + density-matched source was sufficient: brick coursing and
shingle tiling read cleanly at both a straight (`y0`) and a sloped/gable (AFFINE) face, no visible
stair-stepping in the texture content itself. The only jaggedness left is the hard-edged polygon
mask silhouette (`_apply_polygon_mask`, pinned C7 — must stay pixel-exact with `face_masks.py`),
which is a separate, intentional contract, not a resample artifact. Decision: did NOT wire in the
2× supersample→LANCZOS-downsample escalation path — it's written and available
(`texture_resample.supersample_transform`) but unused, since the conditional trigger ("bicubic
alone still leaves visible stair-stepping") wasn't met. Re-open if a future sheet still reads noisy.

Tests: amended `test_stage_kit_modules.py`'s stage-contract test for arm-a-only (9 stem pairs, not
27) and added a sheet-dimensions test pinning `CELL_PX == 256`. `make verify-fast`: 123 passed.

Commit: see git log (this section was written into the same commit as the code/asset changes).

## ROUND 2 (Lucas 2026-07-16, board review of 78e08a0 + NB door reference image)
- R2-1 ALL: aliasing persists → cell 256→512 (4× pixels again) + ENABLE the 2× supersample→LANCZOS
  path (written in P2, was off). Aliasing is warp stair-stepping more than source res — supersample
  is the real fix; resolution bump per Lucas's call anyway.
- R2-2 ALL: draw thin edge lines where adjacent faces have different normals (+ silhouette) — several
  modules read confusing without face separation. Spec: dark ink stroke ~2px@512 over the warped
  composite, edges known by construction from face polygons.
- R2-3 ROOF: Lucas strategy (ADOPTED) — roof modules become COVER ONLY (sloped + flat ridge parts);
  gable/enclosure = WALL material, composed at assembly as wall modules placed BEHIND the cover and
  CROPPED by the cover's under-silhouette (mask by construction — we know cover geometry per view;
  triangular cover over rectangular wall would otherwise show wall tips). Bonus: kills the
  line-matching problem between sloped shingle courses and gable courses (different materials by
  design). Crop machinery lands with S4t assembly prototype.
- R2-4 STAIRS: same 2-stage treatment — stair modules = treads/risers only; side/back enclosure =
  wall modules behind, cropped along the stair diagonal at assembly.
- R2-5 DOORS/WINDOWS: standalone slab sheets, NO wall behind (P3 as decided round 1 — was not yet
  implemented when board was reviewed; Lucas's NB reference image = target spec). Slab 0.1 voxel
  thick; door 1×2, window 1×1 first; texture front + back (back FLIPPED so hardware matches side);
  TOP view = thin bar. 10% inset = painter placement metadata, not the sprite.
- Reference image layout note: Lucas's NB sheet uses a COMPASS 3×3 (NW N NE / W TOP E / SW S SE,
  numbered labels) — intuitive, but has NO empty cell: the NB watermark landed ON view 9 (SE) in his
  own example. FLAG raised to Lucas: adopt compass layout + extra caption strip below (watermark
  absorber), or keep 5×2 with empty cell. Awaiting call; sheets stay 5×2 meanwhile.

## Step 2 scope (executor): R2-1 + R2-2 + R2-5 + cover-only roof/stair modules (R2-3/R2-4 render side).
Assembly-side crop = S4t.

## Step 2 executed (2026-07-16)

R2-1 (resolution + supersample): `CELL_PX` 256 -> 512 (stage_kit_modules.py).
The 2x supersample->LANCZOS path (`texture_resample.supersample_transform`,
written but unwired since P2) is now the ONLY resample path inside
`texture_warp._warp_to_screen` — both PERSPECTIVE and AFFINE warps route
through it instead of a single BICUBIC sample. `s` is still recovered once
from the manifest-derived shared scale, never re-measured. Sheets are now
2592x1032 (5x2 grid at the 512px cell, gutter unchanged).

R2-2 (edge lines): new module `src/pipeline/face_edges.py`. `stroke_edges
(faces)` walks every face's polygon edges, matches shared 3D corner-pairs
across faces (geometry by construction, never pixel/silhouette detection),
and returns the edges to stroke per face: any edge with NO matching
neighbour (silhouette — open covers like roof_cell/stairs aren't closed
solids anymore under R2-3/R2-4) or matched to a neighbour with a different
world normal (a real fold). `paint_panel` strokes a face's edges (dark ink,
~2px@512, `INK` = linework.py's `#3a3a3a`) right after that face's own
texture paste, in the SAME far->near `ordered_faces` sequence the painter
already composites in — a nearer face pasted later naturally overpaints ink
under it, matching the existing last-write-wins occlusion convention
instead of a second, inconsistent occlusion test.

R2-5 (standalone door/window slabs): `kit_modules.py` drops recess_door/
recess_window (wall-carve openings) and `_carve_side`/`_wall_with_opening`/
`OPENING_MARGIN` with them; adds `door_1x2`/`window_1x1` as standalone
thin-slab objects (`_slab`: extrude of a w x `SLAB_THICK`=0.1 footprint).
`texture_map.py` gives the two LARGE v-normal faces (front v=0, back
v=SLAB_THICK) the object's own decal family (`door_1x2x0`/`window_1x1x0`,
both already present in textures.json); every other face (thin u-normal
edges + top/bottom caps) gets plain wood tone + edge lines. `face_texture`
now also returns `flip_h` (True only on a slab's back face) —
`stage_kit_modules.paint_panel` mirrors the source PNG (`ImageOps.mirror`)
before `warp_decal` on that face only, so real-world hardware (handle/
keyhole) sits on the same physical edge seen from either side
(physically-correct object continuity, not a sprite mirror). `recess_
decals()` is gone from texture_map.py; `paint_panel`'s old "composite any
recess decal" loop is gone too — decal vs tiling texture type now branches
inside the SAME per-face loop via `spec["type"]`.

R2-3/R2-4 (cover-only roof/stairs, render side): `_roof_cell` keeps only
the two sloped cover quads (gable end triangles + underside soffit struck);
`_stair_cover` (replaces the from_boxes-based `_stair_treads`) keeps tread
+ the single uphill riser per step (side-triangle envelope + the back face
buried against the next step struck). Both become WALL material composed
behind the cover and cropped to its silhouette at assembly — that crop
machinery is S4t, out of scope here. `from_boxes`/`extrude` stay untouched,
independently-tested public seams; nothing calls `from_boxes` internally
anymore.

Tests: amended test_kit_modules.py (EXPECTED_MODULES, roof/stair
face-count contracts — comments point at R2-3/R2-4; door/window replace
the recess tests), test_texture_map.py (roof gable/bottom + stair-sides
amended, recess_decals tests removed — comment points at
test_texture_map_slab.py), test_texture_warp.py (`_gable_pts` synthesizes
a triangle now that no MODULES builder emits a 3-corner face, keeping the
AFFINE path under test), test_stage_kit_modules.py (`CELL_PX == 512`),
test_arm_a_texture.py (FIXTURES: recess_door -> door_1x2). New:
test_texture_map_slab.py (door/window decal id resolution + flip_h
contract, split out to stay under the per-file line gate), test_face_edges.py
(stroke_edges geometry contract + one pixel-level integration check that a
real different-normal boundary paints dark ink — code-asserted, not
eyeballed, per iso-visual's HARD RULE).

`make verify-fast`: 131 passed.

Restaged gen-inbox: base, diag_half, roof_cell, stair_45, stair_half,
top_cap, wall_band, door_1x2, window_1x1 (9 stem pairs, arm-a only, sheets
2592x1032). Deleted the stale recess_door/recess_window sheets + masks.

Not done here (explicitly out of scope, S4t): the roof/stair enclosure
walls, cropped to the cover's under-silhouette, and the wall-column
emergent-hole mechanics doors/windows sit in. The compass-vs-5x2 sheet
layout question (end of ROUND 2 above) is still awaiting Lucas's call.

## ROUND 3 (Lucas 2026-07-17, stairs image: rows 1-2 current, 3-4 target, 5-6 orange masks)
- Verdict on step 2: "this is progress". Stairs = the only real issue: vertical-box construction
  renders INTERNAL parts between steps.
- Lucas plan (ADOPTED, with simplification): render ONLY the steps (treads+risers floating in space);
  enclosure filled at assembly via MASKS occupying exactly the enclosure-face space (his orange
  regions), computed vs the wall voxel sharing the stair's cell. Roofs same, masks for BOTH cases:
  edge (gable at run end) and inset enclosures.
- Simplification (agreed direction): the mask regions ARE the stripped enclosure faces — keep them as
  mask-only geometry; render emits per-view enclosure-mask PNGs via the existing face_masks machinery
  (tagged stair_enclosure / roof_edge / roof_inset); assembly warps wall texture DIRECTLY into those
  polygons with the arm_a homography engine. No wall-sprite-behind + crop; no phantom-voxel
  intersection needed (faces sit inside the voxel by construction). NB never sees enclosures.
- Also step 3: fix dangling silhouette stroke past roof plane (edge lines must stroke only edges of
  faces actually RENDERED, not stripped ones).
