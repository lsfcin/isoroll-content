# restyle_arm_a — real-texture arm (guidance dial: highest, c < b < a)

TASK: Repaint every cell in this sheet as a finished isometric game asset, restyling ONLY — the
render already gives you exact geometry AND a first pass at material color, do not invent or move
volume.

READ THE SHEET (never draw guide elements):
- Grid of cells, one KIT V2 module panel per cell, one shared 2:1 dimetric camera (except the
  cells captioned TOP, which are the orthographic plan of that same module).
- Faces already carry a procedural material tint per face (stone/wood/thatch) as a starting
  point — refine into real, painterly materials, but keep every silhouette, opening, and face
  boundary exactly where the render puts it.

STYLE: consistent stone-and-wood dungeon-kit palette across every cell; neutral top-left daylight;
crisp silhouette; pieces must tile seamlessly when repeated.

OUTPUT: same grid, same cell geometry and scale, pure black background inside cells. The
bottom-right cell is the watermark slot — leave it EMPTY, do not paint into it.
NEGATIVE: no text or labels, no extra objects, no ground shadows, no perspective drift (dimetric
only), no mirroring, no style drift between cells.
