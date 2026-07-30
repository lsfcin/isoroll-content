# stage_kit_paint.py — one-off: stage P5 kit-painting inputs into output/gen-inbox (arm A + arm B)
import sys, pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path("/mnt/workspace/code/isoroll-content")
KIT = ROOT / "output/kit-guide"
INBOX = ROOT / "output/gen-inbox"
MAGENTA = (255, 0, 255)
PIECES = ["floor", "wall", "door_u", "door_v", "window_u", "window_v"]

STYLE = ("hand-painted dark-fantasy dungeon, aged stone blocks with moss in the cracks, "
         "warm torchlight accents, drawn/illustrated feel like the game Hades, "
         "painterly texture, crisp silhouette, NOT 3D-rendered, NOT cel-shaded")

SHEET_PROMPT = f"""TASK: Repaint each schematic piece in this kit sheet as a finished isometric game asset. One piece per cell, all cells share ONE style.

READ THE SHEET (never draw guide elements):
- 3x2 grid of cells split by magenta lines; small corner tags name each piece (ignore, never draw text).
- Every cell shows ONE modular dungeon kit piece from the SAME fixed camera (2:1 dimetric).
- Grayscale faces encode light: light gray = top face, mid gray = long faces, dark gray = end caps. Keep this lighting direction.
- Dark recesses are door/window openings: render them as real openings at exactly those spots (door cell gets a wooden door leaf inside the recess; window cell gets a barred window).
- Cells: 1 floor slab, 2 solid wall, 3 wall with door opening (u), 4 wall with door opening (v), 5 wall with window (u), 6 wall with window (v).

SUBJECT: modular dungeon construction kit — floor slab and wall segments
STYLE: {STYLE}; identical palette and materials in ALL cells; neutral top-left daylight; pieces must tile seamlessly when repeated side by side (no unique blemishes at cell edges).

OUTPUT: same 3x2 grid, same cell geometry and scale, keep each piece exactly inside its cell, pure black background inside cells.
NEGATIVE: no magenta lines, no text or labels, no extra objects, no ground shadows, no perspective (dimetric only), no mirroring, no style drift between cells.
"""

PIECE_PROMPT = """TASK: Repaint this schematic kit piece as a finished isometric game asset. Same geometry, same camera.

READ THE GUIDE (never draw guide elements):
- One modular dungeon kit piece, fixed 2:1 dimetric camera.
- Grayscale faces encode light: light gray = top, mid gray = long faces, dark gray = end caps. Keep this lighting.
- Dark recesses are door/window openings: render them as real openings at exactly those spots.

SUBJECT: {piece}
STYLE: {style}; crisp silhouette; neutral top-left daylight; must tile seamlessly when repeated.

OUTPUT: same single piece, same position and scale, pure black background.
NEGATIVE: no magenta lines, no text, no extra objects, no ground shadows, no perspective (dimetric only), no mirroring.
"""

PIECE_DESC = {
    "floor": "stone floor slab, one grid cell",
    "wall": "solid stone wall segment, 3 units tall",
    "door_u": "stone wall segment with a door opening (door leaf inside the recess), run along u",
    "door_v": "stone wall segment with a door opening (door leaf inside the recess), run along v",
    "window_u": "stone wall segment with a barred window opening, run along u",
    "window_v": "stone wall segment with a barred window opening, run along v",
}

INBOX.mkdir(parents=True, exist_ok=True)
imgs = {p: Image.open(KIT / f"{p}.png").convert("RGBA") for p in PIECES}
cw = max(i.width for i in imgs.values()) + 24
chh = max(i.height for i in imgs.values()) + 24
sheet = Image.new("RGB", (cw * 3 + 4, chh * 2 + 4), (0, 0, 0))
d = ImageDraw.Draw(sheet)
for idx, p in enumerate(PIECES):
    r, c = divmod(idx, 3)
    x0, y0 = c * cw + 2, r * chh + 2
    im = imgs[p]
    sheet.paste(im, (x0 + (cw - im.width) // 2, y0 + (chh - im.height) // 2), im)
    d.text((x0 + 6, y0 + 4), str(idx + 1), fill=MAGENTA)
for c in range(1, 3):
    d.line([(c * cw + 2, 0), (c * cw + 2, sheet.height)], fill=MAGENTA, width=3)
d.line([(0, chh + 2), (sheet.width, chh + 2)], fill=MAGENTA, width=3)
sheet.save(INBOX / "kit-dimetric-sheet_guide.png")
(INBOX / "kit-dimetric-sheet_prompt.txt").write_text(SHEET_PROMPT)
for p in PIECES:
    imgs[p].convert("RGB").save(INBOX / f"kit-{p}_guide.png")
    (INBOX / f"kit-{p}_prompt.txt").write_text(
        PIECE_PROMPT.format(piece=PIECE_DESC[p], style=STYLE))
print("staged:", sorted(f.name for f in INBOX.glob("kit-*")))
