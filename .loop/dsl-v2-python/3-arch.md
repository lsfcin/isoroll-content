# Loop 3 — Architecture — dsl-v2-python

## Carry
slug: dsl-v2-python | branch: loop/dsl-v2-python | root: code/isoroll-content
test-cmd: `python3 -m pytest -q` (33 pass on develop @ Loop 1) | e2e-cmd: none
criticality: normal | verdict: standard
criteria:
  C1 parse — all v2 fixtures parse; R/S voxels mismatching group spans → error; voxel double-booking (two chars claiming same voxel via groups vs grids) → error
  C2 round-trip — parse→serialize reproduces fixture verbatim (modulo trailing whitespace) for every fixture
  C3 massing — per-column runs match rig semantics: wallish runs with opening sub-runs (merged contiguous D/W with same side), per-level derived diagonals (diagSolid rule), floor plates with fh, group surfaces via grpBaseData/grpCellVoxels port (stairs stepped 45°=5ft or half=2.5ft only)
  C4 manifest — level→tile elevation, side→WallDef.dir, wallish run length→boundHeight aggregate, group cells→per-cell placements; HUD-count semantics: walls/diags count voxels, openings count RUNS
  C5 guide render — scene_guide_render consumes massing v2; multi-level fixture renders without error; l-room render change (if any) is deliberate and noted
  C6 existing pytest suite stays green
tasks:
  T1 — port group/diag geometry helpers to new layout_groups.py — high
  T2 — parser v2 (levels + attr grids + group lines + rotate) — high
  T3 — v2 validation (R/S vs group span, double-booking, stair incl) — high
  T4 — serializer updateDsl port (round-trip) — high
  T5 — massing v2 (run merge, openings, diagonals, floor fh, groups) — high
  T6 — manifest v2 + scene_assemble._piece_for + HUD counts — high
  T7 — guide render v2 consumes massing v2 — medium
  T8 — fixtures (l-room v2 + multilevel + groups) + golden tests — medium
context: code/CONTEXT.md, code/isoroll-content/CONTEXT.md, code/isoroll-content/SPECS.md, code/isoroll-content/src/pipeline/CONTEXT.md

## Architecture
Reference is `design/feel-rig/rig.frag` (line refs below); PORT, do not reinvent. NLVL=10.

**DECISION D0 — Z-merge, not u/v-merge (the #1 wrong-guess risk).** v1 `massing` merged wall cells
*along the ground plane* (a row of `#` → one long box). v2 does NOT. rig L483–501 iterates each
ground cell `(r,c)` and walks UP the levels, merging contiguous same-family voxels into a vertical run
`zBot..zTop`. So every v2 Box footprint is 1×1 in u/v (`l=d=1`); the only extent that varies is Z.
`merge=True` = merge contiguous same-family voxels along Z into one run; `merge=False` = one box per
voxel (render lane). u/v segment-merging for module WallDefs is OUT OF SCOPE this loop.

**DECISION D1 — Box gains `z0`.** Add `z0: float = 0.0` (run base = zBot) to `Box`. Default 0.0 keeps
single-level back-compat. Every renderer projection/fit/sort MUST thread z0 (see T7).

**DECISION D2 — Opening model changes.** v1 `Opening{kind, offset}` (u/v offset) → v2
`Opening{kind, z_lo, z_hi, side}`: a vertical sub-run of contiguous D/W of equal `side` inside a wall
column (rig L610–618). Openings count as RUNS not voxels (C4). `scene_guide_render._draw_openings` and
`scene_assemble._piece_for` both read the old shape → both migrate in T7/T6.

**DECISION D3 — Group cells reconstructed from R/S markers on parse.** `updateDsl` (L1088–1119) overlays
`R`(roof)/`S`(stair) onto the level grids where a group surface passes, and writes each group line with
only its bbox `r0,c0 r1,c1` + params. On parse, a group's `cells` = the set of `(r,c)` inside its bbox
carrying its own marker (R for roof, S for stair) in ≥1 level grid. Validation (C1) then asserts the
union of `grp_cell_voxels` over those cells equals the authored R/S voxels.

Per file:
- `src/pipeline/layout_groups.py` (NEW, T1) — pure geometry, no PIL. Vocab consts (rig L184–199:
  WALLISH,DIAG,STAIRS,ARROW_CW,DIAG_CW,ASCENT,SIDE_NAME,ROOF_FORMS,STAIR_TYPES,ENCLOSE,TYPES,NLVL).
  `diag_solid(grid,r,c,ch)->"NE"|"NW"|"SE"|"SW"|None` (L365–372). `grp_base_data(group)->` object with
  `aOf,aLow,aHigh,rise,form,hAt` (L423–435). `grp_cell_voxels(B,group,r,c)->(voxLo,voxHi)` (L437–443).
- `src/pipeline/layout_parse.py` (MODIFY, T2/T3) — new models: `Level{g:list[str],side,type,wmat,fh:dict}`,
  `Group{kind,cells,form,dir,incl,z,enclose}`, `Layout{name,levels:list[Level],groups:list[Group],rows,
  cols,errors,warnings}`. Back-compat props over `levels[0]`: `.grid`, `.wall_h`(=DEFAULT_WALL_H),
  `.kind(u,v)`. `parse_text`: `level N:` blocks + `layer side:/type:/wmat:/fh:` attr grids (1 char/cell)
  + `roof:`/`stair:` lines; BARE grid (no `level`) → single Level 0 (v1 l-room.txt still parses).
  `rotate_cw`: rotate ALL level grids via chRot (arrows+diags, L263–264), remap every group cell + rotate
  group.dir. `validate`: (a) R/S union == grp_cell_voxels; (b) double-booking (any voxel claimed twice);
  (c) stair `incl` ∈ {2.5, 5} else error. Keep parser ≤200 LOC — split helpers to layout_groups if tight.
- `src/pipeline/layout_serialize.py` (NEW, T4) — `to_dsl(layout)->str`, updateDsl port (L1088–1119):
  `name:`; per non-empty level emit grid with R/S overlaid from gvox span map, then `layer side/type/
  wmat/fh:` blocks only when that grid has a non-`.` cell; then `roof:`/`stair:` lines
  `r0,c0 r1,c1 form= dir=<N|E|S|W> incl=<n>ft z=<n> [enclose=]`. Re-export from layout_parse for callers.
- `src/pipeline/layout_massing.py` (MODIFY, T5) — v2 per-cell Z-run massing (D0/D1/D2): wall runs w/
  opening sub-runs (L610–618), per-level derived diagonals via `diag_solid` (L386–393), floor plates
  `zTop=lvl+fh*0.2` (L488), group surfaces via `grp_cell_voxels` — stairs 5 stepped treads riser=incl/25
  solid|thin (L535–552), roofs sloped/flat patch (L509). Box gets `z0`,`kind∈{wall,floor,step,diag,GRP}`.
  If >200 LOC, split group-box emission to `layout_massing_groups.py`.
- `src/pipeline/scene_manifest.py` + `scene_assemble.py` (MODIFY, T6) — manifest v2: tile `z`/elevation =
  box.z0; wall `dir` from opening/side; wall `boundHeight` = z-run height (box.h); group cells → per-cell
  placements; walls[] bottomOffset=box.z0, topOffset=box.z0+box.h. New `count_hud(layout)->{walls,doors,
  windows,floors,stairs,roofs}` (L1073–1084: walls/diags count voxels, D/W count runs — a D whose
  below-neighbor is D is not a new run; stairs = stair-group count). `_piece_for` handles diag + GRP kinds
  (return None for now if no kit piece), opening→piece keyed by side.
- `src/pipeline/scene_guide_render.py` (MODIFY, T7) — thread z0: `_proj` unchanged but `_faces`/`_fit`/
  `_quad` callers use z0..z0+h; painter sort key `(b.u0+b.v0, b.z0, b.h>0)`. `_draw_openings` reads new
  Opening(z_lo,z_hi,side). `render_plan_panel` stays level-0 view — note the delta in a code comment.
- `test/` (T8) — 3 hand-authored fixtures canonicalized once via T4 then frozen:
  `src/pipeline/layouts/l-room.txt` (v2, single level), `test/fixtures/golden/multilevel.txt` (≥2 levels),
  `test/fixtures/golden/groups.txt` (1 roof + 1 stair). New `test/test_dsl_v2_*.py`. Migrate v1-shape
  assertions in `test_export_manifest.py`, `test_scene_manifest_kit_meta.py`, `e2e_export_manifest.py`.

## Evaluation
criteria-coverage:
  C1 → layout_parse.parse_text().errors (T2/T3); D3 R/S-union + double-booking + stair-incl checks
  C2 → layout_serialize.to_dsl(parse(text)) == text per-line-rstripped (T4)
  C3 → layout_massing.massing(layout) box list (T5) w/ layout_groups geometry (T1)
  C4 → scene_manifest.build_manifest fields + count_hud() (T6)
  C5 → scene_guide_render.render_scene_panel non-blank RGB, multi-level (T7)
  C6 → full `python3 -m pytest -q` incl migrated v1 tests (T8)
seams:
  C1 — assert `.errors == []` on 3 valid fixtures; `!= []` w/ message on 2 invalid (misplaced R, incl=3)
  C2 — golden .txt files diffed byte-for-byte (trailing-ws-normalized) against re-serialized parse
  C3 — frozen golden box list (sorted tuples of u0,v0,z0,l,d,h,kind) per fixture; grp_cell_voxels unit test
  C4 — assert manifest tile.z / wall.dir / boundHeight fields + count_hud dict on groups+multilevel fixtures
  C5 — `render_scene_panel(...).getextrema()` shows non-uniform channel (not all-black) on multilevel
  C6 — pytest exit 0; the 3 named v1-shape tests migrated to v2 box shape, not deleted
back-compat ratified (R2): Layout REPLACED but `.grid/.wall_h/.kind` are level-0 property views, so the 5
importers + single-level v1 tests keep working; multi-level consumers already route through massing().
verdict: PASS

executor: loop-high model=opus tier=high

## Amendment (RETURN loop=3 reason=integration-gap, received at max tier)
Loop 5 evidence: groups fixture → manifest tiles=0 walls=0; scene_guide_render crashes
(`min() empty`); massing/build_manifest never call grp_base_data/grp_cell_voxels; stair
shortcut matches v1 arrow set, never v2 R/S markers.
RULING: design UNCHANGED — T5/T6 group paths were specified above and simply not implemented;
the escape was a seam gap. Seams sharpened (binding for 4a/4b re-entry):
  C3-seam+ — golden BOX LIST test runs on the GROUPS fixture too: massing() must emit GRP boxes,
    one per group cell, z0/h == grp_cell_voxels span (stairs: stepped treads per D0/T5 spec).
  C4-seam+ — manifest test runs on the GROUPS fixture: len(tiles)>0; per-cell placements with
    tile.z == voxLo and h == voxHi-voxLo for every group cell; count_hud stairs/roofs correct.
  C5-seam+ — render test runs on the GROUPS fixture: render_scene_panel returns non-blank RGB,
    no exception on group-only scenes (GRP boxes drawn as plain z0..z0+h boxes; empty-massing
    guard added).
Route: 4a adds the missing RED tests at these seams (append section to 4a-tests.md), then 4b
implements until green (append to 4b-code.md). Downstream tiers unchanged (medium).
executor: orchestrator-as-loop3-receiver model=claude-fable-5 tier=max
