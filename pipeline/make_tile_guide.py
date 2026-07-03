#!/usr/bin/env python3
"""
make_tile_guide.py — Generate the color-coded multiview schematic guide for a wall tile (S0-E1).

Face-ID colors (bound to these meanings in the NB prompt, see SPECS.md → Chosen Pipeline):
  red = top · gray = north/back · green = south/front · blue = west end · purple = east end

Two layouts:
  9panel — all cardinal + diagonal + TOP, dev/QC reference (matches hand-drawn prototype deck)
  6cell  — NW/NE/TOP over SW/SE/caption, 3x2 aspect — the actual Nano Banana input format

Usage:
  python pipeline/make_tile_guide.py --length 5 --height 4 --layout 6cell --output out.png
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from generate_sheet_template import load_font, FONT_PATHS  # noqa: F401 (reused, not redefined)
from tile_guide_render import (
    TOP_RED, BACK_GRAY, FRONT_GREEN, WEST_BLUE, EAST_PURPLE,
    draw_iso_panel, draw_flat_grid,
)

BG = (0, 0, 0)
MAGENTA = (255, 0, 255)
CELL_PX = 320

LEGEND = [
    (TOP_RED, "RED - TOP FACE"),
    (BACK_GRAY, "GREY - NORTH BACK FACE"),
    (FRONT_GREEN, "GREEN - SOUTH FRONT FACE"),
    (WEST_BLUE, "BLUE - WEST END FACE"),
    (EAST_PURPLE, "PURPLE - EAST END FACE"),
]

LAYOUTS = {
    "9panel": [["NW", "N", "NE"], ["W", "TOP", "E"], ["SW", "S", "SE"]],
    "6cell": [["NW", "NE", "TOP"], ["SW", "SE", "CAPTION"]],
}


def _draw_panel(draw, kind, l, d, h, box):
    if kind in ("NW", "NE", "SW", "SE"):
        draw_iso_panel(draw, l, d, h, kind, box)
    elif kind == "N":
        draw_flat_grid(draw, l, h, BACK_GRAY, 1, box)
    elif kind == "S":
        draw_flat_grid(draw, l, h, FRONT_GREEN, 1, box)
    elif kind == "W":
        draw_flat_grid(draw, d, h, WEST_BLUE, 1, box)
    elif kind == "E":
        draw_flat_grid(draw, d, h, EAST_PURPLE, 1, box)
    elif kind == "TOP":
        draw_flat_grid(draw, l, d, TOP_RED, d, box)


def _draw_caption(draw, box, font):
    cx, cy, cw, ch = box
    row_h = min(28, (ch - 20) // len(LEGEND))
    x, y = cx + 14, cy + 14
    for color, text in LEGEND:
        draw.rectangle([x, y, x + 18, y + 18], fill=color, outline=MAGENTA)
        draw.text((x + 26, y), text, font=font, fill=MAGENTA)
        y += row_h


def _panel_label(row, col, kind):
    index = row * 3 + col + 1
    suffix = " ▼" if kind == "TOP" else ""
    return f"{index} {kind}{suffix}"


def generate(l, d, h, layout, out_path: Path):
    rows = LAYOUTS[layout]
    cols = len(rows[0])
    w, hpx = cols * CELL_PX, len(rows) * CELL_PX
    img = Image.new("RGB", (w, hpx), BG)
    draw = ImageDraw.Draw(img)
    font = load_font(16)

    for r, row_kinds in enumerate(rows):
        for c, kind in enumerate(row_kinds):
            box = (c * CELL_PX, r * CELL_PX, CELL_PX, CELL_PX)
            if kind == "CAPTION":
                _draw_caption(draw, box, font)
            else:
                _draw_panel(draw, kind, l, d, h, box)
            draw.text((box[0] + 6, box[1] + 4), _panel_label(r, c, kind), font=font, fill=MAGENTA)

    for c in range(1, cols):
        x = c * CELL_PX
        draw.line([(x, 0), (x, hpx)], fill=MAGENTA, width=2)
    for r in range(1, len(rows)):
        y = r * CELL_PX
        draw.line([(0, y), (w, y)], fill=MAGENTA, width=2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"Saved: {out_path}  ({w}x{hpx} px, {layout}, L{l}xH{h}xD{d})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", type=int, required=True, help="wall length, grid units (east-west)")
    parser.add_argument("--height", type=int, required=True, help="wall height, grid units")
    parser.add_argument("--depth", type=int, default=1, help="wall thickness, grid units (default 1)")
    parser.add_argument("--layout", choices=list(LAYOUTS), default="6cell")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    generate(args.length, args.depth, args.height, args.layout, args.output)
