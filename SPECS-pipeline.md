# The chosen pipeline
> The pipeline that was chosen, and the concept-art prompts fed into it.
> governs: src/pipeline/

## Chosen Pipeline

### Tiles (L1) — decided 2026-07-03 (S0 design session)

**Route: NB-5G — Nano Banana guided 5-view grid.** Nano Banana is the primary
generator because it is the only route accessible to every user tier (essential /
important / desired). Local 3D-lift and Blender routes are fallback only.
Paid cloud GPU is not acceptable; NB via free Gemini access is.

**View count: 4+1.** The module camera is fixed (or rotates in 90° steps), so
grid-aligned walls only ever appear as `NW`, `NE`, `SW`, `SE` + `TOP`. The
cardinal views (N/S/E/W) — NB's systematic failure mode (panels collapse to flat
orthographic elevation, top face dropped) — are excluded by design, not worked
around. Tokens still need 8 facings; token pipeline is a separate decision
(next design session).

**Two-faced walls.** Walls have distinct faces (e.g. decorated interior vs plain
exterior). Guide schematic colors are face IDs, bound in the prompt:

| Color | Meaning |
|-------|---------|
| red | top surface |
| green | face A (e.g. decorated/interior) — visible in SW, SE |
| gray | face B (e.g. plain/exterior) — visible in NW, NE |
| blue | west end cap |
| purple | east end cap |

**Grid layout: 6-cell, 3×2 aspect ratio** (confirmed: NB can generate 3×2
directly). Top row `NW | NE | TOP`, bottom row `SW | SE | caption`. The
caption cell (bottom-right) is the one NB stamps its watermark on, so
essential art never lands there. It carries only a small dimension tag
(`W5 H4 D1`) for human/QC tracking — deliberately NOT the color→face
legend. That binding lives in the text prompt (S0-E2) only; baking it into
the guide image risks NB treating rendered legend text as content to
reproduce or extend elsewhere in the output.

**Simplified layouts, for assets that don't need all 5 views** (same caption-cell
watermark trick, just fewer content cells — `make_tile_guide.py --layout`):
- `2cell` — `SW | NE | TOP | caption`, one row, 4×1. One corner view per long
  face (green via SW, gray via NE), for assets where the end caps don't
  matter — SW stands in for SE and NE stands in for NW since the cap color is
  ignored. Cardinal N/S/E/W panels are never used standalone; the module only
  ever renders corner views (see "View count: 4+1" above). TOP is always
  included even here — isoroll's top-down view mode needs a real top
  reference on every asset, not just the oblique-implicit sliver in the
  SW/NE panels.
- `1cell` — `SW | TOP | caption`, one row, 3×1. Fully symmetric content
  (identical front/back **and** identical west/east caps) — one iso view +
  its own cap implies everything else. TOP still included for the same
  top-down-view-mode reason as `2cell`.

Which layout applies is a per-asset judgment call (does this wall's back face
differ from its front? do its end caps differ from each other?), not a fixed
rule — `6cell` is the default/safe choice when unsure.

**Steps:**
1. **Hero view** — NB generates one best single view (SE-style) from text prompt.
   Human approves. This image is the identity anchor for everything after.
2. **Guide** — script-generated 6-cell schematic grid, 3×2, per the layout above
   (colored blocks at correct 26.57° dimetric proportions for the wall's
   L×H×T grid units).
3. **Grid call** — NB input: hero image + guide + prompt template binding
   colors→face descriptions. Output: filled 6-cell grid.
4. **Split** — `cli/sprite_splitter.py` (extended) → `tiles/{name}/{name}_{facing}.png`,
   facing ∈ {NW, NE, SW, SE, TOP} (caption cell discarded on split).
5. **QC + regen** — human checklist: top surface visible in all diagonals; face IDs
   correct; component counts (pillars, niches) match hero; no sticker border.
   Failed view → per-view regen (hero + that panel's schematic), max 2 per view.

**Reliability gate (go/no-go):** benchmark of 10 varied wall assets. Pass =
≥8/10 assets fully accepted within ≤2 per-view regens. Fail → activate fallback:
Blender parametric wall kit (box geometry + NB texture projection,
`pipeline/blender_iso_rig.py` as base) — consistency and seamless joins by
construction, but breaks the important/desired tiers.

**Floors:** flat — no multiview problem. One iso-diamond view (+ optional TOP).
Rotation variants derivable from texture rotation later.

**Props/furniture (irregular L1):** same NB-5G route. TripoSR lift (local, fits
6GB) stays as fallback for shapes NB can't keep consistent.

**Modular join sets (AP1-T4 corner/T/end pieces):** NB-only first; joins masked by
columns at junctions (T4 trick). Blender kit only if the benchmark fails.

**Desired-tier deliverable (v1):** recipe only — guide PNG template + copy-paste
prompt + short instructions shipped with module/docs. No API integration in module yet.

### Scale corrective factor (for pre-scale-consistency sheets)

Sheets generated before shared-scale mode landed (scale-consistency loop) used
**per-cell autofit**: each panel picked its own `s_cell` = px-per-voxel that
best fills its 320×320 cell. That means the SAME wall reads at different
apparent sizes across panels (a 5×3×2 wall's `NE` face and its `TOP` face are
each individually maximized, not drawn at one shared scale) — the defect this
loop fixes going forward via `render_cells(shared_scale=True)`.

For an EXISTING autofit sheet, a **per-cell corrective factor** lets you rescale
any panel to what it would have been under shared-scale, using only the
recorded `{stem}.scale.json` sidecar (no re-measuring pixels):

```
s_cell = bbox_w / content_extent_w        # panel's own implied px-per-voxel
corrective = s_shared / s_cell            # = px_per_voxel / s_cell
```

where `bbox_w = bbox[2] - bbox[0]` (the panel's recorded content bbox width),
`content_extent_w` is that panel's voxel-unit content width (`content_extent()`
in `panel_geometry.py`, keyed by orientation), and `s_shared` is the sidecar's
top-level `px_per_voxel` (recorded as `s_shared` even on legacy sheets — see
`sheet_qc.cross_view_dims`). Multiply the panel's pixel content by `corrective`
to bring it onto the sheet's shared scale.

**Worked example** — a real `guide.scale.json` from `make_tile_guide.py --width 4
--height 3 --depth 1 --layout 6cell --legacy-autofit` (per-cell autofit, so the
sidecar's panel bboxes disagree — the exact case this factor corrects):

```
px_per_voxel (s_shared): 51.6364
panel NE: bbox=[350.909, 18.0, 609.091, 302.0], orientation=NE, w=4, d=1, h=3
  content_extent("NE", 4, 1, 3) -> (w_u=5.0, h_u=5.5)
  s_cell = (609.091-350.909) / 5.0 = 51.6364
  corrective = 51.6364 / 51.6364 = 1.0   # NE happens to be the constraining
                                          # panel here, so it's already at s_shared
panel TOP: bbox=[658.0, 124.5, 942.0, 195.5], orientation=TOP, w=4, d=1, h=3
  content_extent("TOP", 4, 1, 3) -> (w_u=4, h_u=1)
  s_cell = (942.0-658.0) / 4 = 71.0
  corrective = 51.6364 / 71.0 ≈ 0.7272   # TOP autofit bigger than shared scale
                                          # (thin content, little to constrain
                                          # it) — its pixels must shrink by this
                                          # factor to read at the sheet's scale
```

Each panel needs its own corrective factor — this is exactly the inconsistency
shared-scale mode (default ON) eliminates for new sheets.

### Characters (L2) — TBD (next design session)

- Primary path: TBD (S3 3D-lift vs NB-based — token facings are 8, so NB's
  cardinal-view weakness returns; decide separately)
- Primary checkpoint (dark-fantasy): TBD
- SD version (SD1.5 / SDXL): TBD
- Temporal consistency strategy: TBD
- Frame rate target: TBD (current assumption: 12 fps)

---

## Concept Art Prompts (External Tools)

Use these prompts in GPT Image, Nano Banana, MidJourney, or similar external generators.
Do NOT specify camera angles in degrees — generators ignore them. Use visual descriptions and game references instead.

### Dungeon Floor Tile

```
Single isometric dungeon floor tile, classic 2:1 isometric game projection,
diamond shape twice as wide as it is tall, low camera angle showing the tile
face with slight top surface visible, dark grey and charcoal stone cobblestone,
subtle cracks and shallow worn grooves, faint teal-green moss in the crevices,
rough hand-cut stone edges, painterly illustrated style with visible brushwork,
strong clean silhouette, pure white background, no shadows cast onto the
background, no characters, no furniture, no other objects in frame, square
composition centered, dark fantasy game art, Diablo II isometric perspective,
Hades video game aesthetic.
```
Format: PNG, square (1:1).

### Character — Rogue/Assassin (first test character)

```
Full body character concept art, dark fantasy rogue assassin, front-facing
view with very slight overhead angle matching classic 2:1 isometric game
perspective, neutral relaxed standing pose with arms hanging slightly away
from body at sides, complete figure visible from head to toe, dark hooded
cloak with teal inner lining, light leather armor with gold metallic buckles
and accents, two daggers sheathed at hip, dark teal and black color palette
with gold highlights, face partially visible beneath hood, sharp intense eyes,
strong readable silhouette, pure white background, no drop shadow on
background, no environment, portrait orientation, digital illustration,
painterly brushwork, Hades video game art aesthetic, game character reference
art, full figure.
```
Format: PNG, portrait (2:3).

---
