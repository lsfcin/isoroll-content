# Batch D — table / chair / cabinet / chest

Guide image: `../guides/guide_d.png`

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
1. TABLE — a plain dungeon table (row 1)
2. CHAIR — a simple wooden chair (row 2)
3. CABINET — a wooden cabinet/bookshelf (row 3)
4. CHEST — a storage chest (row 4)

Every panel is labeled in its top-left corner with its object name and face (e.g. "CHAIR SW",
"CABINET NE"). Use that label to know which object a panel belongs to. The value scheme above is
LOCAL to each object's own row-band. Each object is a fully separate item that only shares this
dungeon's style, not a shared physical object.

Panels labeled NW/NE/SW/SE are 26.57-degree dimetric isometric views — match that exact camera
angle in every one of them, across every object, do not vary it. A panel labeled TOP is that same
object seen from directly overhead. A panel labeled CAPTION is not part of any object — leave it
plain background, no text, border, or object.

Per-object notes:
- TABLE: a plain rectangular dungeon table, aged wood, no drawers or asymmetric features — front,
  back, and both ends read the same.
- CHAIR: a simple wooden chair. The SW panel shows the front (seat, front legs, front of the
  backrest); the NE panel shows the back (rear of the backrest, back legs). Same single chair.
- CABINET: a wooden storage cabinet or bookshelf. The SW panel shows the front (doors, or open
  shelves with visible contents); the NE panel shows the back (plain wood panel, no shelves or
  doors). Same single cabinet.
- CHEST: a storage chest with a hinged lid. The SW panel shows the front (iron lock plate, latch,
  banding); the NE panel shows the back (plain wood, hinge mechanisms, no lock). Same single chest.

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
