# Batch E — carpet / painting / candle / torch

Guide image: `../guides/guide_e.png`

```
I'm providing one image: a layout guide — a grid of labeled panels. The guide is a GRAYSCALE
VALUE STUDY, not a color image: the flat gray tones encode which face of each object a panel shows,
and they also pre-shade every object as if lit from the upper-left. Read the values as lighting and
match them:
- LIGHTEST gray = the object's TOP surface (catches the most light).
- MID gray = the broad face turned toward the viewer.
- DARKEST gray = the receding side / end face (in shadow).
All magenta lines, borders, panel numbers and text labels are LAYOUT MARKERS ONLY — never draw
them, and no magenta may appear in your output. Every panel must contain finished, fully rendered
game art, not a flat gray block and not a line drawing.

This sheet contains FOUR separate, unrelated objects, stacked top to bottom as row-bands:
1. CARPET — a decorative floor rug (row 1)
2. PAINTING — a small framed wall painting (row 2)
3. CANDLE — a table candle (row 3)
4. TORCH — a wall-mounted torch/lamp (row 4)

Every panel is labeled in its top-left corner with its object name and face (e.g. "CARPET TOP",
"TORCH SW"). Use that label to know which object a panel belongs to. The value scheme above is
LOCAL to each object's own row-band. Each object is a fully separate item that only shares this
dungeon's style, not a shared physical object.

Panels labeled NW/NE/SW/SE are 26.57-degree dimetric isometric views — match that exact camera
angle in every one of them, across every object, do not vary it. A panel labeled TOP is that same
object seen from directly overhead. A panel labeled CAPTION is not part of any object — leave it
plain background, no text, border, or object.

Per-object notes:
- CARPET: a decorative rug lying flat on the floor. Render it with full material depth in both the
  oblique and top views — pattern, weave, and worn/frayed edges reading clearly; refined game art,
  not a flat repeating texture swatch.
- PAINTING: a small framed painting or tapestry that hangs flush on a dungeon wall. Its single
  oblique (SW) panel shows the framed picture at the standard camera angle — a simple dark-fantasy
  subject (a crest, a landscape, or a portrait — your choice), in a worn frame matching this set's
  materials.
- CANDLE: a single table candle in a simple holder, small, roughly cylindrical.
- TORCH: a wall-mounted torch or lamp bracket with a lit flame. It protrudes from the wall (real 3D
  depth to the bracket) — render the bracket and flame with genuine form, not a flat icon.

Render every object in the following style, applied identically across all four objects:

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
wash, no flat even lighting (the TORCH's own flame is the one element allowed to glow). Line and
edge treatment: a confident, soft-edged painterly dark outline (not a hard black vector line)
around every silhouette and major interior form break; interior surfaces modeled with visible
directional brushstrokes, never smooth gradients or airbrush blending. Overall value structure:
high contrast, most of every panel reads as midtone-to-shadow, with highlights reserved strictly
for edges, metal, and the one light-facing surface. Apply this same palette, material finish,
lighting direction, and line treatment identically to every object in this image and to every
other image in this set — this is one continuous dungeon tileset, not several unrelated
illustrations. Plain stone only — no carved runes, glyphs, inscriptions, symbols, sigils, or
writing of any kind on any surface.

Keep proportions and silhouette faithful to each panel's guide geometry. Output aspect ratio must
match the guide image exactly. Do not add any text, watermark-looking element, sticker border,
decorative frame, ground plane, characters, or other props anywhere in the output.
```
