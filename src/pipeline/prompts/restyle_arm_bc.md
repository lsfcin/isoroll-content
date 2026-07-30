# restyle_arm_bc — blank + cyan symbols arm (guidance dial: middle, c < b < a)

TASK: Repaint every cell in this sheet as a finished isometric game asset, restyling ONLY — the
render already gives you exact geometry, do not invent or move volume.

READ THE SHEET (never draw the guide elements below):
- Grid of cells, one KIT V2 module panel per cell, one shared 2:1 dimetric camera (except the
  cells captioned TOP, which are the orthographic plan of that same module).
- Faces are flat-shaded grayscale (light=top, mid=side/slope/gable, dark=bottom) — keep this
  lighting direction and face identity when you restyle.
- Small cyan registration symbols mark orientation/anchor points — READ them to keep faces and
  openings correctly sided, but NEVER draw cyan in your output; it is a guide layer only.

STYLE: consistent stone-and-wood dungeon-kit palette across every cell; neutral top-left daylight;
crisp silhouette; pieces must tile seamlessly when repeated.

OUTPUT: same grid, same cell geometry and scale, pure black background inside cells. The
bottom-right cell is the watermark slot — leave it EMPTY, do not paint into it.
NEGATIVE: no cyan marks or residue, no text or labels, no extra objects, no ground shadows, no
perspective drift (dimetric only), no mirroring, no style drift between cells.
