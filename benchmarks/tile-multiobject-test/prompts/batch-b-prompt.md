# Batch B — openings: door-leaf / window (flat)

Guide image: `../guides/guide_b.png`

Both objects are FLAT panels (zero thickness) that fill a doorway/window opening. The engine orients
the flat sprite per scene-rotation. The guide draws each as a single flat parallelogram (not a box),
on purpose.

```
I'm providing one image: a layout guide — a grid of labeled panels. The guide is a GRAYSCALE
VALUE STUDY, not a color image: each panel is a single flat mid-gray parallelogram, pre-shaded as
if lit from the upper-left. All magenta lines, borders, panel numbers and text labels are LAYOUT
MARKERS ONLY — never draw them, and no magenta may appear in your output. Do not render any
letters, words, or labels anywhere; the guide's labels are instructions to you, never content to
draw. Every panel must contain finished, fully rendered game art, not a flat gray shape and not a
line drawing.

Each object floats alone, centered in its own panel, on the flat dark background — do not extend it
to fill the panel, and do not add any frame, wall, floor, ground, or environment around it.

This sheet contains TWO separate, unrelated objects, stacked top to bottom as row-bands:
1. DOOR-LEAF — a single flat wooden door leaf, shown from four rotations (rows 1-2)
2. WINDOW — a single flat dungeon window, shown from four rotations (rows 3-4)

Every panel is labeled in its top-left corner with its object name and face (e.g. "DOOR-LEAF SW",
"WINDOW NE"). Use that label to know which object a panel belongs to. Each object is a fully
separate item that only shares this dungeon's style, not a shared physical object.

CRITICAL — each panel shows ONE SINGLE FLAT panel with NO thickness:
- It is a thin flat door/window, like a plank card. Do NOT draw two doors. Do NOT draw two panels
  meeting at a corner or forming an L or a V. Do NOT draw a 3D box or give it a visible side/edge
  face. Exactly ONE flat panel per cell, seen slightly angled (26.57-degree dimetric).
- The four oblique panels (NW / NE / SW / SE) are the SAME single object seen from the four
  isometric rotations — render one consistent object across all four (same wood, same ironwork,
  same proportions), only the viewing angle changes.
- SW and SE show the room-facing FRONT; NW and NE show the BACK.
- The panel labeled TOP is the object seen from directly overhead: it is a long, THIN bar — the
  panel has only a slight thickness, so render its top edge as a thin strip of the same material,
  not a wide slab and not a full door/window.
- A panel labeled CAPTION is not part of any object — leave it plain background, no text or border.

Per-object notes:
- DOOR-LEAF: a tall flat wooden door leaf — aged oak planks, two horizontal iron reinforcing bands
  with rivets. FRONT (SW/SE) also has a black iron ring handle and visible strap hinges; BACK
  (NW/NE) is the same planks and bands with no handle.
  HANDEDNESS — this is ONE consistent door. Place the pivot (strap-hinge) side and the ring-handle
  side EXACTLY as specified for each panel below, regardless of how that panel leans. Never
  mirror-flip the door.
    · DOOR-LEAF SW (front): pivot / strap hinges on the LEFT edge, iron ring handle on the RIGHT.
    · DOOR-LEAF SE (front): pivot / strap hinges on the LEFT edge, iron ring handle on the RIGHT.
    · DOOR-LEAF NE (back):  pivot / strap hinges on the RIGHT edge, iron ring handle on the LEFT.
    · DOOR-LEAF NW (back):  pivot / strap hinges on the RIGHT edge, iron ring handle on the LEFT.
  The two FRONT panels (SW, SE) are identical in handedness; the two BACK panels (NE, NW) are
  identical in handedness and are the reverse side of the same door. Do NOT swap the hinge/handle
  sides between SW and SE, or between NE and NW — only the lean/viewing angle changes.
- WINDOW: a dungeon window that fills the opening — vertical wrought-iron bars (optionally with a
  small leaded-glass lattice behind them) in a simple iron/wood frame. It reads the SAME from front
  and back (the bars are symmetric), so there is no handle and no handedness — the four obliques are
  purely different viewing angles of the same symmetric window. TOP is a thin bar.

Render both objects in the following style, applied identically:

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
