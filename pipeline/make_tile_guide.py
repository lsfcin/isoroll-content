#!/usr/bin/env python3
"""
make_tile_guide.py — Generate the color-coded multiview schematic guide for a wall tile (S0-E1).

Face-ID colors (bound to these meanings in the NB prompt, see SPECS.md → Chosen Pipeline):
  red = top · gray = north/back · green = south/front · blue = west end · purple = east end

Two layouts:
  9panel — all cardinal + diagonal + TOP, dev/QC reference (matches hand-drawn prototype deck)
  6cell  — NW/NE/TOP over SW/SE/caption, 3x2 aspect — the actual Nano Banana input format

Cardinal (N/S/W/E) panels are drawn "unfolded-net" style: the TOP face is folded
flat above the body, so N/S panels are W cols x (D+H) rows and W/E panels are
D cols x (W+H) rows — verified against the reference deck (pipeline/prompts/reference).

Usage:
  python pipeline/make_tile_guide.py --width 5 --height 4 --layout 6cell --output out.png
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from generate_sheet_template import load_font
from tile_guide_render import (
    TOP_RED, BACK_GRAY, FRONT_GREEN, WEST_BLUE, EAST_PURPLE,
    draw_iso_panel, draw_flat_grid, draw_square_grid,
)

BG = (0, 0, 0)
MAGENTA = (255, 0, 255)
CELL_PX = 320

LAYOUTS = {
    "9panel": [["NW", "N", "NE"], ["W", "TOP", "E"], ["SW", "S", "SE"]],
    "6cell": [["NW", "NE", "TOP"], ["SW", "SE", "CAPTION"]],
}


def _draw_panel(img, draw, kind, w, d, h, box):
    if kind in ("NW", "NE", "SW", "SE"):
        draw_iso_panel(img, w, d, h, kind, box)
    elif kind == "N":
        draw_flat_grid(draw, w, d + h, BACK_GRAY, d, box)
    elif kind == "S":
        draw_flat_grid(draw, w, d + h, FRONT_GREEN, d, box)
    elif kind == "W":
        draw_flat_grid(draw, d, w + h, WEST_BLUE, w, box)
    elif kind == "E":
        draw_flat_grid(draw, d, w + h, EAST_PURPLE, w, box)
    elif kind == "TOP":
        draw_square_grid(draw, w, d, TOP_RED, box)


def _draw_caption(draw, box, font, w, d, h):
    cx, cy, cw, ch = box
    draw.text((cx + cw / 2 - 40, cy + ch / 2 - 8), f"W{w} H{h} D{d}", font=font, fill=MAGENTA)


def _panel_label(row, col, kind):
    index = row * 3 + col + 1
    suffix = " ▼" if kind == "TOP" else ""
    return f"{index} {kind}{suffix}"


def generate(w, d, h, layout, out_path: Path):
    rows = LAYOUTS[layout]
    cols = len(rows[0])
    img_w, img_h = cols * CELL_PX, len(rows) * CELL_PX
    img = Image.new("RGB", (img_w, img_h), BG)
    draw = ImageDraw.Draw(img)
    font = load_font(16)

    for r, row_kinds in enumerate(rows):
        for c, kind in enumerate(row_kinds):
            box = (c * CELL_PX, r * CELL_PX, CELL_PX, CELL_PX)
            if kind == "CAPTION":
                _draw_caption(draw, box, font, w, d, h)
            else:
                _draw_panel(img, draw, kind, w, d, h, box)
            draw.text((box[0] + 6, box[1] + 4), _panel_label(r, c, kind), font=font, fill=MAGENTA)

    for c in range(1, cols):
        x = c * CELL_PX
        draw.line([(x, 0), (x, img_h)], fill=MAGENTA, width=2)
    for r in range(1, len(rows)):
        y = r * CELL_PX
        draw.line([(0, y), (img_w, y)], fill=MAGENTA, width=2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"Saved: {out_path}  ({img_w}x{img_h} px, {layout}, W{w}xH{h}xD{d})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, required=True, help="wall width, grid units (east-west)")
    parser.add_argument("--height", type=int, required=True, help="wall height, grid units")
    parser.add_argument("--depth", type=int, default=1, help="wall thickness, grid units (default 1)")
    parser.add_argument("--layout", choices=list(LAYOUTS), default="6cell")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    generate(args.width, args.depth, args.height, args.layout, args.output)
