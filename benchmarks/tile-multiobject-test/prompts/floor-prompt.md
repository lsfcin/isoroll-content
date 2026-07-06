# Floor / background — big floor tile

Guide images: `../guides/floor_{N}.png` (N = 2,3,5,10,20,40). Use the guide whose CAPTION matches
the footprint you want. One prompt covers every size. Sizes stop at 40: NB paints at most ~40
stones across before they mush, so a floor spanning more than ~40 cells would show giant stones
(stone size ≈ footprint_cells / ~40). For a large ground area, tile/repeat the 20 or 40 floor
rather than generating one huge tile.

```
I'm providing one image: a layout guide for a single object — a dungeon stone floor. The guide is
a GRAYSCALE VALUE STUDY, not a color image. It has two panels: an SW panel (the floor seen at a
26.57-degree dimetric isometric angle, its top surface lightest, its thin edge darker in shadow)
and a TOP panel (the same floor seen from directly overhead). A third CAPTION panel gives the
floor's size in grid cells — it is NOT part of the floor, leave it plain background. All magenta
lines, borders, and labels are LAYOUT MARKERS ONLY — never draw them, and no magenta may appear in
your output. The grid of squares inside each panel indicates the paving layout; it is a guide, not
something to trace.

Render a dungeon stone floor covering the whole tile: MANY small cobblestones / flagstones — each
individual stone should read much smaller than a standing figure, so the floor never looks like a
few giant slabs. Vary the stone shapes and sizes naturally, with irregular mortar joints, so it
does not read as a mechanical repeating texture. Render it with full painterly material depth in
BOTH the SW oblique panel and the TOP panel — this is refined game art, not a flat tiling swatch.

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

Output aspect ratio must match the guide image exactly. Do not add any text, watermark-looking
element, sticker border, decorative frame, walls, characters, or props anywhere in the output.
```
```
