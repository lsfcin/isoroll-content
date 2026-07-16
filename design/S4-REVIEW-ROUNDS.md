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
