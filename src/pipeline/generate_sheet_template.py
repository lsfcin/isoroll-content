#!/usr/bin/env python3
"""
generate_sheet_template.py — Generate the character sheet template PNG.

One file serves both purposes:
  - Upload to GPT as layout guide (GPT reads labels, respects cell boundaries)
  - Human reference (shows what each panel should contain)

True black (#000000) cell backgrounds. Labels in top safe zone only — never near character bodies.

Grid spec (also used by sheet_to_tpose.py):
  3 columns × 2 rows, each cell 512×512 px, 4px borders, 48px outer margin
  Total: 1640×1124 px

Panel layout:
  [0,0] FRONT FULL     [1,0] T-POSE 3D ★    [2,0] BACK VIEW
  [0,1] 3/4 VIEW       [1,1] EQUIPMENT       [2,1] PALETTE

Usage:
  python src/pipeline/generate_sheet_template.py
  python src/pipeline/generate_sheet_template.py --output path/to/out.png
"""

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTER_MARGIN = 48
CELL_W       = 512
CELL_H       = 512
BORDER       = 4
COLS         = 3
ROWS         = 2

BG           = (0,   0,   0)    # true black outer margin
CELL_BG      = (0,   0,   0)    # true black cells
BORDER_COLOR = (55,  55,  55)   # dark gray cell separators (visible on black)
MARKER_COLOR = (60,  60,  60)   # corner markers
LABEL_TITLE  = (200, 200, 200)  # main label text
LABEL_TPOSE  = (255, 210,  60)  # gold — T-pose cell is the key output
LABEL_SUB    = (90,  90,  90)   # subtitle text
SAFE_DIVIDER = (35,  35,  35)   # dotted safe-zone line

LABEL_TOP_PAD  = 14   # px from top of cell to first text line
SAFE_ZONE_Y    = 75   # px from cell top — character body must stay below this

PANEL_LABELS = [
    [
        ("T-POSE FRONT  ★",  "Light-gray bodysuit · arms out",    LABEL_TPOSE),
        ("T-POSE BACK   ★",  "Light-gray bodysuit · from behind", LABEL_TPOSE),
        ("FRONT",            "Full detail · all accessories",      LABEL_TITLE),
    ],
    [
        ("3/4 VIEW",   "~30–45° diagonal · full detail",          LABEL_TITLE),
        ("EQUIPMENT",  "Weapons & items isolated",                 LABEL_TITLE),
        ("PALETTE",    "8 swatches · label below each",           LABEL_TITLE),
    ],
]

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]


def load_font(size):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def total_size():
    w = OUTER_MARGIN + COLS * CELL_W + (COLS - 1) * BORDER + OUTER_MARGIN
    h = OUTER_MARGIN + ROWS * CELL_H + (ROWS - 1) * BORDER + OUTER_MARGIN
    return w, h


def cell_origin(col, row):
    return (
        OUTER_MARGIN + col * (CELL_W + BORDER),
        OUTER_MARGIN + row * (CELL_H + BORDER),
    )


def generate(out_path: Path):
    w, h = total_size()
    img  = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)

    # Fill cells (explicitly, so they're true black even on black bg)
    for row in range(ROWS):
        for col in range(COLS):
            cx, cy = cell_origin(col, row)
            draw.rectangle([cx, cy, cx + CELL_W - 1, cy + CELL_H - 1], fill=CELL_BG)

    # Cell separators
    for col in range(1, COLS):
        x = OUTER_MARGIN + col * (CELL_W + BORDER) - BORDER
        draw.rectangle([x, OUTER_MARGIN, x + BORDER - 1, h - OUTER_MARGIN - 1], fill=BORDER_COLOR)
    for row in range(1, ROWS):
        y = OUTER_MARGIN + row * (CELL_H + BORDER) - BORDER
        draw.rectangle([OUTER_MARGIN, y, w - OUTER_MARGIN - 1, y + BORDER - 1], fill=BORDER_COLOR)

    # Corner markers (L-brackets)
    arm, inset = 28, 10
    for row in range(ROWS):
        for col in range(COLS):
            cx, cy = cell_origin(col, row)
            corners = [
                (cx + inset,          cy + inset,           +1, +1),
                (cx + CELL_W - inset, cy + inset,           -1, +1),
                (cx + inset,          cy + CELL_H - inset,  +1, -1),
                (cx + CELL_W - inset, cy + CELL_H - inset,  -1, -1),
            ]
            for ax, ay, dx, dy in corners:
                draw.line([(ax, ay), (ax + dx * arm, ay)], fill=MARKER_COLOR, width=2)
                draw.line([(ax, ay), (ax, ay + dy * arm)], fill=MARKER_COLOR, width=2)

    font_title = load_font(20)
    font_sub   = load_font(13)

    for row in range(ROWS):
        for col in range(COLS):
            cx, cy = cell_origin(col, row)
            title, subtitle, title_color = PANEL_LABELS[row][col]

            draw.text((cx + 16, cy + LABEL_TOP_PAD), title, font=font_title, fill=title_color)
            draw.text((cx + 16, cy + LABEL_TOP_PAD + 26), subtitle, font=font_sub, fill=LABEL_SUB)

            # Dotted safe-zone divider — character body must stay below this line
            sy = cy + SAFE_ZONE_Y
            for sx in range(cx + 6, cx + CELL_W - 6, 12):
                draw.rectangle([sx, sy, sx + 5, sy], fill=SAFE_DIVIDER)

    # Footer note
    footer_font = load_font(12)
    draw.text(
        (OUTER_MARGIN, h - OUTER_MARGIN + 12),
        "★ = T-pose — used as TripoSR mesh input   ·   dotted line = safe zone, character body stays below",
        font=footer_font,
        fill=(55, 55, 55),
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"Saved: {out_path}  ({w}×{h} px)")
    print(f"Upload this file to GPT as layout guide. Same file is human reference.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="src/pipeline/prompts/sheet_template.png")
    args = parser.parse_args()
    generate(Path(args.output))
