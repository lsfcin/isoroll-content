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

## Step 3 executed (2026-07-17)

Floating steps + enclosure masks (stairs/roofs) + edge-stroke fix, per ROUND 3's ADOPTED plan.

`kit_modules.Face` gains a 4th field, `enclosure: str = ""` — "" means rendered normally; a
non-empty value ("stair_enclosure" | "roof_edge" | "roof_inset") means the Face is real geometry
(kit_modules stays its single source of truth) but mask-only: never painted, never stroked. `_stair_
cover` is back to emitting the full 6-face box per step (top, bottom, side0/1/2, riser) — same as
before R2-4 — but tags bottom/side0/side1/side2 `enclosure="stair_enclosure"`; only tread (top) and
riser render, so steps read as floating in space. `_roof_cell` is back to 5 faces (2 render slopes +
2 gable end triangles tagged `"roof_edge"` + 1 horizontal under-eave soffit tagged `"roof_inset"`);
winding was hand-chosen (not copied from the pre-R2-3 ROOF_EAVE version) so every face's shared edge
with its neighbour is a correctly-matched, opposite-order pair — the 5 faces now form a closed
watertight shell (a "tent with a floor"), which made the old ROOF_EAVE anti-subsumption overhang
unnecessary (nothing renders alongside the slopes anymore, so there's nothing left to subsume).

`kit_module_render.py`: `ordered_faces` and the new `ordered_enclosure_faces` both route through a
shared private `_project` (same yaw/project/sort as before, now also carrying `f.enclosure` through);
`ordered_faces` keeps only `enclosure == ""` (render-visible — this is the single choke point that
keeps mask-only geometry out of render_panel/paint_panel/the existing per-face masks), `ordered_
enclosure_faces` keeps the complement, returning 5-tuples with the trailing tag. New `enclosure_
faces(name, s, cell_px, pad, origins)` reprojects a module's mask-only faces per view using the SAME
per-view origin `render_module` already computed, so an enclosure mask lands pixel-aligned to its
rendered panel.

New `src/pipeline/enclosure_masks.py` (kept separate from stage_kit_modules.py to stay under the
per-file line gate): `save_enclosure_masks(module, view, enc_ordered, cell_px, masks_path)` groups
the tagged faces by `enclosure` kind and writes one `{module}_{view}_{tag}_facemask.png`/`_faces.json`
pair per non-empty group through the SAME `face_masks.face_mask`/`save_mask` the render-visible masks
already use — no changes needed to face_masks.py itself. `stage_kit_modules.stage()` calls this right
after writing each module's arm_a sheet, so enclosure masks land in `masks/` alongside the existing
per-face masks, tagged by kind exactly as specified (stair_enclosure / roof_edge / roof_inset).

Edge-stroke fix (task 3): no code change was needed in face_edges.py itself — `stroke_edges(faces)`
is still called with the FULL face list (render + enclosure) so adjacency matching stays geometrically
correct (a rendered face's edge against a same-normal-but-hidden neighbour, if one existed, would
correctly stay unstroked), but `paint_panel`'s draw loop only ever iterates `ordered` — which, via the
`ordered_faces` filter above, only ever contains rendered face ids — so a stripped face's own edges are
now structurally impossible to draw. The dangling-past-the-roof-plane failure mode (an enclosure face's
boundary getting stroked into a region with no texture behind it) is closed by construction.

Tests: amended `test_kit_modules.py` (roof_cell/stair face-count + kind Counters, now asserting the
render/enclosure split and enclosure tags — comments point at ROUND 3), `test_texture_map.py` (gable
face-kind test now sources real `roof_cell` geometry instead of a synthetic triangle since gable faces
exist again; stair-sides test filters to render-visible faces before asserting all-riser, since the
full per-step face list now includes the 3 enclosure sides too), `test_face_edges.py` (open-cover test
comment updated — roof_cell's 5 faces now form a closed shell, same all-edges-stroked tally for a
different underlying reason). Added: `test_kit_module_render.py` (`ordered_faces`/`ordered_enclosure_
faces` partition a module's faces with no overlap; enclosure tags; `enclosure_faces` reuses render_
module's per-view origin), `test_arm_a_texture.py::test_stair_arm_a_paints_nothing_outside_the_tread_
and_riser_mask_union` (mirrors the existing "no unpainted pixel inside mask" test in the other
direction — together they pin painted == mask exactly), `test_face_edges.py::test_no_edge_stroke_
pixel_lies_outside_the_rendered_faces_dilated_by_stroke_width` (dilates the render-only face-mask
union by `edge_width` and asserts every INK-colored pixel falls inside it), new `test_enclosure_masks.
py` (split out for the line gate: enclosure-mask PNGs exist per view for stair_45/stair_half/roof_cell
with nonzero coverage, tagged correctly; a module with no enclosure faces — wall_band — writes none).

`make verify-fast`: 138 passed.

Restaged gen-inbox: same 9 modules (base, diag_half, door_1x2, roof_cell, stair_45, stair_half,
top_cap, wall_band, window_1x1), arm-a only, 2592x1032 sheets. New: 36 enclosure-mask PNG/JSON pairs
in `masks/` (18 stair_enclosure — stair_45 + stair_half x 9 views; 9 roof_edge + 9 roof_inset for
roof_cell x 9 views), every one checked non-empty (nonzero `getbbox()`).

## ROUND 4 (Lucas 2026-07-17 — stairs still wrong; diagnosis confirmed by comparison)
Render bugs: (1) steps = disconnected plates (derived from stacked boxes); (2) NO backface culling —
faces painted even when normal points away (phantom plates in behind views); (3) box side faces leak
white into render (sides are enclosure territory).
Mask bug: per-face projection of box sides/back/bottom → thin stepped bands; target = FULL region
between step surface and voxel envelope.
ADOPTED fixes:
- Stair geometry = ONE zigzag profile polygon (2D step outline) extruded across width — treads/risers
  are strips of a single solid; connectivity by construction.
- Backface culling by world normal · camera direction in the module renderer (all modules benefit).
- Mask definition = wall_voxel_silhouette(view) − rendered_alpha(view), for stairs AND roofs. One
  enclosure mask per module+view (roof edge/inset split deferred to assembly if still needed).
- INVARIANT TEST (code, per view): render_alpha ∪ enclosure_mask == voxel_silhouette exactly — zero
  gap pixels, zero overlap beyond stroke tolerance. Makes this bug class unshippable blind.
- Hairlines expected to die with the box construction; edge strokes only on rendered (culled-in) faces.

## Step 4 executed (2026-07-17)

All four ROUND 4 fixes, per the ADOPTED plan.

`kit_modules._stair_cover` rebuilds each stair as ONE zigzag profile polygon (`_stair_profile`: STEPS
risers alternating STEPS treads in the u-z rise plane, closed by a back edge and an implicit bottom
edge) extruded across the full stair width (v: 0->1) via a bespoke per-edge extrusion (mirrors
`extrude`'s axis roles with v standing in for z). Each profile EDGE becomes one v-spanning quad strip —
risers/treads render, the two profile end-caps (v=0/v=1) plus the back-wall and bottom strips stay
`enclosure="stair_enclosure"` (self-occlusion/silhouette geometry only). Faces per stair: 2*STEPS+4 (was
STEPS*6 under R2-4's per-step-box scheme) — 2*STEPS render (STEPS risers + STEPS treads, edge-to-edge by
construction since they're strips of one shared polygon, closing the ROUND-4 "disconnected plates" bug),
4 stay enclosure. Kind vocabulary reused ("top" for treads, "side" for risers) instead of introducing
"tread"/"riser" kinds — this lines up with `texture_map.FAMILY`'s existing stair branch (kind=="top" ->
stair_tread, kind=="side" + normal check -> stair_riser) with zero changes needed to texture_map.py.

`kit_module_render.py`: new `_face_normal`/`_front_facing` — backface cull by world normal · a fixed
dimetric-camera axis, derived from (and cross-checked against) `scene_guide_render.Cam`/`_faces`, which
only ever draws a box's max-u/max-v/top faces: that's exactly what dotting against `(1,1,1)` picks out
for the 8 `y{deg}` views (camera fixed at the +u+v+z octant, yaw rotates the FACE not the camera); TOP is
a separate straight-down camera, axis `(0,0,1)`. `_project` now threads a `front_facing` bool through
every row alongside the existing `enclosure` tag. `ordered_faces` (the single choke point already used
for render/paint/per-face-mask emission) now filters `not enc and front` instead of just `not enc` — this
is where "all modules benefit" happens: closed boxes (wall_band, top_cap, base, door/window slabs,
diag_half) drop from painting all 6 faces to painting only the 2-3 that were ever visible anyway (verified
unchanged output via the existing test suite — hidden faces were previously just overpainted by nearer
ones, so the visible pixels don't change), stairs/roofs drop faces that have nothing left to overpaint
them (the actual bug: phantom risers/gables showing through in behind views). `ordered_enclosure_faces`
is deliberately NOT backface-culled (self-occlusion/silhouette bookkeeping wants the full mask-only
geometry regardless of facing) — kept as public API, but no longer called anywhere in the mask pipeline.

New `enclosure_masks.voxel_silhouette(view, s, cell_px, pad, origin)`: projects a fresh full-height wall
voxel (`km.extrude(km.UNIT_SQUARE, 0.0, km.WALL_H)`, i.e. the same shape as `wall_band`) through
`kit_module_render.ordered_faces` (so it's backface-culled too) at the SAME scale/origin a module's own
panel was rendered with, then rasterises via `face_masks.face_mask` — pixel-exact with the render-visible
per-face masks. `save_enclosure_masks(module, view, ordered, s, cell_px, pad, origin, masks_path)` (new
signature — the old `enc_ordered`-from-`ordered_enclosure_faces` parameter is gone) subtracts the
module's own rendered silhouette from `voxel_silhouette` via `ImageChops.subtract` on the two binary
images, writes `{module}_{view}_enclosure_facemask.png`/`_faces.json` through the same `face_masks.
save_mask` seam, and skips writing when the gap is empty (e.g. every module's TOP view: stairs/roofs
both cover their full unit footprint from directly above, gap == 0, confirmed empirically). Drops the
old `stair_enclosure`/`roof_edge`/`roof_inset` tag split entirely — one `enclosure` mask per module+view,
computed purely geometrically (never from `Face.enclosure` tags, though those tags still exist and still
keep the geometry out of render — `enclosure_masks.py` doesn't read them at all anymore).
`stage_kit_modules.stage()` gates the call on `any(f.enclosure for f in km.MODULES[name]())` per module
(so wall_band/base/top_cap/diag_half/door_1x2/window_1x1 never call it, matching the old "no enclosure
faces -> nothing written" contract) and threads `ordered`/`s`/`origin` straight from the same
`render_module` loop already producing the arm_a sheet — no second render pass.

Tests: amended `test_kit_modules.py` (`test_stair_45_and_stair_half_are_one_zigzag_solid_tread_riser_
render_only` — face counts 2*STEPS+4/2*STEPS/4, comment points at ROUND 4), `test_kit_module_render.py`
(`test_ordered_faces_and_ordered_enclosure_faces_partition_stair_45_modulo_backface_culling` — the old
strict 2-way partition is now 3-way: {rendered, enclosure, backface-culled}). Rewrote
`test_enclosure_masks.py` for the single `enclosure` tag (drops the `stair_enclosure`/`roof_edge`/
`roof_inset` glob checks) and added the two ROUND-4-mandatory tests:
`test_round4_rendered_union_enclosure_equals_voxel_silhouette_exactly` (per view, for stair_45/
stair_half/roof_cell: no rendered pixel lies outside `voxel_silhouette`, and the actual `{enclosure}`
PNG written by the real `stage()` pipeline unioned with the rendered silhouette reproduces
`voxel_silhouette` exactly, zero overlap — an end-to-end wiring check, not just the tautological
subtract-by-construction) and `test_stair_behind_view_paints_a_near_zero_sliver_relative_to_the_front_
view` (relative min-vs-max painted-area comparison across the 8 yaw views, not a hardcoded pixel count —
empirically the minimum view paints ~19% of the maximum view's area, comfortably under the 30% bar,
since all 4 risers share one normal and vanish together in the views that look from the up-stair end,
leaving only the tread strips). `test_texture_map.py`/`test_texture_warp.py` needed ZERO changes — the
stair kind-vocabulary choice ("top"/"side", not "tread"/"riser") was chosen specifically to land inside
their existing FAMILY-table branches.

`make verify-fast`: 140 passed (was 138 after Step 3; net +2 from the two new invariant tests, the
partition-test rename is a like-for-like swap).

Restaged gen-inbox (same 9 stem pairs, arm-a only) and masks/ (per-face masks unchanged in kind/count;
enclosure masks now single-tagged — 8 `{module}_{view}_enclosure_facemask.png`/`_faces.json` pairs each
for stair_45/stair_half/roof_cell, TOP view excluded per module since its gap is empty by construction).

## ROUND 4b (Lucas mid-run clarifications, 2026-07-17)
- MASKS: simply the LATERAL faces of stairs AND roofs (stairs: two stepped-wedge profile sides;
  roofs: gable triangles). Supersedes step-4's voxel-minus-render definition (which paints air
  regions orange in some views). Mask = projected lateral faces, by construction.
- RENDER: stairs = the SAME tread+riser rectangle pair repeated with diagonal offset — confirmed
  in a944a30 output (big vertical rectangles gone). Side-on views show treads corner-connected
  (correct for strips; reads solid after assembly mask fill).
- Invariant amended: enclosure_mask == lateral-face projection; render ∩ mask ≈ ∅ (stroke tolerance);
  render ∪ mask ⊆ solid silhouette.

## Step 4b executed (2026-07-17)

Mask definition redefined from voxel-silhouette-minus-render to LATERAL-FACE projection, per ROUND 4b.

`kit_modules.py`: `_stair_cover`'s two profile-envelope-cap faces (v=0/v=1 — the two stepped-wedge
profile side faces of the zigzag solid) are now tagged `STAIR_LATERAL` ("stair_lateral"), split out
from the back-wall/floor faces, which keep `STAIR_ENCLOSURE` ("stair_enclosure") — self-occlusion
geometry only, never masked. `roof_cell`'s gable faces already carried their own distinct tag
("roof_edge", separate from the soffit's "roof_inset") since ROUND 3, so no roof_cell change was
needed — the split just needed to exist for stairs too.

`enclosure_masks.py` rewritten: new `lateral_faces(module, view, s, cell_px, pad, origin)` projects
only the tagged mask-source faces (`{km.STAIR_LATERAL, "roof_edge"}`) via `kit_module_render.
ordered_enclosure_faces` — deliberately NOT backface-culled (a lateral face contributes from both
sides; edge-on views correctly yield a near-empty or fully-culled-by-subtraction mask). `voxel_
silhouette`/`_wall_voxel_faces` are gone.

Empirical finding during implementation (not assumed from the design note): raw lateral-face
projections substantially OVERLAP the module's own render footprint in oblique dimetric views (up to
~50% of the mask area, and at some views — e.g. stair_45 y225 — the render fully covers the lateral
footprint, overlap == mask area). This is inherent to projecting a 3D solid's side faces under a
view where depth collapses onto shared screen pixels; pure "project and rasterize" is NOT disjoint
from render by itself. `save_enclosure_masks` therefore keeps a subtraction step, unchanged in shape
from ROUND 4's — `lateral_silhouette MINUS rendered_silhouette` (was `voxel_silhouette MINUS
rendered_silhouette`) — swapping only the minuend from a synthetic full-height wall voxel (which
over-covers roof_cell/stairs, painting air) to the solid's own real lateral-face footprint (which by
construction never extends past the real solid). Verified numerically across all 9 views x 3 modules:
render ∩ mask == 0 pixels EXACTLY (PIL `ImageChops.subtract` on binary images guarantees this — a
subtracted pixel is nonzero only where the render is zero), and render ∪ mask ⊆ solid silhouette
with zero leaks, at every view.

`stage_kit_modules.py`: `save_enclosure_masks` call site unchanged in shape (`ordered` still passed —
it's the render silhouette to subtract), only the docstring/comment updated to ROUND 4b language.

Tests: amended `test_kit_modules.py` (`test_stair_45_and_stair_half_are_one_zigzag_solid_tread_riser_
render_only` — enclosure faces now assert `Counter == {"stair_lateral": 2, "stair_enclosure": 2}`
instead of a flat `{"stair_enclosure"}` x4), `test_kit_module_render.py`
(`test_ordered_enclosure_faces_are_tagged_stair_enclosure_and_stair_lateral_for_stairs`, renamed from
the old ROUND-4 test name, asserts both tags now present). Rewrote `test_enclosure_masks.py`'s
ROUND-4-mandatory invariant test into the three ROUND-4b invariants: (a)
`test_round4b_enclosure_mask_equals_the_lateral_minus_render_rasterization_by_construction` — an
end-to-end wiring check, independently recomputing `lateral_faces(...) minus render` and comparing
pixel-for-pixel against the actual file `stage()` wrote (or its absence, when the recomputed gap is
empty); (b) `test_round4b_render_and_enclosure_mask_do_not_overlap_beyond_stroke_tolerance` — erodes
the render silhouette inward by `face_edges.edge_width` and asserts the written mask never bleeds into
that deep interior; (c) `test_round4b_render_union_enclosure_mask_is_contained_in_the_solid_
silhouette` — "solid silhouette" = every face of the module projected with NO filtering at all
(neither backface cull nor render/enclosure split), via the public `kit_module_render.project_face`
seam, asserting render ∪ mask never leaks past it. `test_stair_behind_view_paints_a_near_zero_sliver_
relative_to_the_front_view` (render-only, unrelated to the mask redefinition) kept as-is with a
freshened comment.

`make verify-fast`: 142 passed (was 140 after Step 4; net +2 — one old invariant test replaced by
three new ones).

Restaged `output/gen-inbox` (unchanged: same 9 stem pairs, arm-a only) and `output/masks`: 20
`{module}_{view}_enclosure_facemask.png`/`_faces.json` pairs (was up to 24 possible under the old
per-module x 8-view scheme; 7 views now correctly write nothing — render already fully covers the
lateral footprint there, e.g. every module's TOP view and each module's two most edge-on/occluded
yaws — zero-area gaps are the correct output, not missing coverage).
