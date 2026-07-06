# Batch A — structure: wall-straight / pillar / lintel

Guide image: `../guides/guide_a.png`

Doorways and windows are NOT their own frame tiles — a doorway is built from wall segments on each
side (jambs) + a LINTEL block bridging the gap on top + a flat door leaf (batch B) in the opening; a
window adds a lintel on top and a sill on the bottom + a flat shutter. This batch is just the solid
stone pieces the openings are assembled from.

```
I'm providing one image: a layout guide — a grid of labeled panels. The guide is a GRAYSCALE
VALUE STUDY, not a color image: the flat gray tones encode which face of each object a panel shows,
and they also pre-shade every object as if lit from the upper-left. Read the values as lighting and
match them:
- LIGHTEST gray = the object's TOP surface (catches the most light).
- MID gray = the broad face turned toward the viewer.
- DARKEST gray = the receding side / end face (in shadow).
All magenta lines, borders, panel numbers and text labels are LAYOUT MARKERS ONLY — never draw
them, and no magenta may appear in your output. Do not render any letters, words, or labels
anywhere; the guide's labels are instructions to you, never content to draw. Every panel must
contain finished, fully rendered game art, not a flat gray block and not a line drawing.

Each object floats alone, centered in its own panel, on the flat dark background — do not extend it
to fill the panel, and do not add any surrounding wall, floor, ground, or environment around it.

This sheet contains THREE separate, unrelated objects, stacked top to bottom as row-bands:
1. WALL-STRAIGHT — a plain straight wall segment (row 1)
2. PILLAR — a free-standing stone column (row 2)
3. LINTEL — a short stone header block (row 3)

Every panel is labeled in its top-left corner with its object name and face (e.g. "PILLAR SW",
"LINTEL TOP"). Use that label to know which object a panel belongs to. The value scheme above is
LOCAL to each object's own row-band. Each object is a fully separate item that only shares this
dungeon's style, not a shared physical object.

Panels labeled SW are 26.57-degree dimetric isometric views — match that exact camera angle in
every one, across every object, do not vary it. A panel labeled TOP is that same object seen from
directly overhead. A panel labeled CAPTION is not part of any object — leave it plain background,
no text, border, or object.

Per-object notes:
- WALL-STRAIGHT: a plain load-bearing dungeon wall segment — no door, window, or decoration. Front
  and back are the same plain stonework. Its left and right ENDS are flat, clean vertical faces on
  a mortar line (the wall will butt against a pillar or a doorway in-game, so do not round, taper,
  or cap the ends — just cut the courses flat at the edge).
- PILLAR: a free-standing stone column/post, fully self-contained and finished on all sides. It
  stands at wall corners and junctions and wall segments butt against it; render it a little
  stouter/thicker than a wall segment so it reads as a distinct post.
- LINTEL: a single short stone header block, one grid cell, that bridges the gap above a doorway or
  window and ties into the wall segments on either side. Same stone as the wall. Its left and right
  ends are flat vertical faces (they abut the flanking walls, like a wall end) — a plain spanning
  block, not an arch, not decorated.

Render every object in the following style, applied identically across all three objects:

Illustrated, painterly dark-fantasy dungeon style, matching Supergiant Games' Hades — bold
graphic brushwork, not photorealistic, not a 3D render, and not a flat vector/cartoon style
either. Palette: cool charcoal-gray stone in a desaturated blue-gray family, deep near-black
shadow pools, warm amber-gold highlight accents reserved only for metal edges and light-facing
surfaces, aged wood in a dry desaturated umber-brown, iron fittings in matte gunmetal charcoal
with rust-orange oxidation only at joints and edges. Materials: rough-cut, hand-hewn granite
blocks with visible chisel marks and irregular mortar joints — never a smooth or uniform tile
texture. Wood is aged, grain-visible, dry, slightly split at exposed edges — never glossy or new.
Metal is worn matte, pitted, hand-forged-looking, with dark patina and spot rust at contact
points — never chrome, never polished. Weathering: moss and grime accumulate only in recesses,
corners, and low contact areas, never on flat exposed faces; chips and cracks sit exactly at the
edges/corners of stone blocks and wood joints, never mid-face. Lighting: one dominant light
source from upper-left/front, matching this scene's fixed 26.57-degree camera — hard-edged cast
shadows, strong core-shadow-to-highlight separation on every form, no soft ambient-occlusion
wash, no flat even lighting. Line and edge treatment: a confident, soft-edged painterly dark
outline (not a hard black vector line) around every silhouette and major interior form break;
interior surfaces modeled with visible directional brushstrokes, never smooth gradients or
airbrush blending. Overall value structure: high contrast, most of every panel reads as
midtone-to-shadow, with highlights reserved strictly for edges, metal, and the one light-facing
surface. Apply this same palette, material finish, lighting direction, and line treatment
identically to every object in this image and to every other image in this set — this is one
continuous dungeon tileset, not several unrelated illustrations. Plain stone only — no carved
runes, glyphs, inscriptions, symbols, sigils, or writing of any kind on any surface.

Keep proportions and silhouette faithful to each panel's guide geometry. Output aspect ratio must
match the guide image exactly. Do not add any text, watermark-looking element, sticker border,
decorative frame, ground plane, characters, or props anywhere in the output.
```
