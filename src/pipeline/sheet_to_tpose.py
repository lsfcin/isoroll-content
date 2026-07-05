#!/usr/bin/env python3
"""
sheet_to_tpose.py — Crop panels from a GPT-generated character sheet.

Grid layout (must match generate_sheet_template.py):
  [0,0] Full character front (detailed)   [1,0] 3D-ready T-pose (clean)   [2,0] Back view
  [0,1] 3/4 angle view                    [1,1] Equipment breakdown        [2,1] Color palette

Usage:
  python src/pipeline/sheet_to_tpose.py sheet.png --character rogue
  python src/pipeline/sheet_to_tpose.py sheet.png --character rogue --debug
  python src/pipeline/sheet_to_tpose.py sheet.png --character rogue --offset-x 12 --offset-y -8

After cropping, the 3D-ready T-pose (panel [1,0]) is copied to:
  assets/chars/{character}/concept/{character}_front_tpose_sheet.png
"""

import argparse
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

OUTER_MARGIN = 48
CELL_W = 512
CELL_H = 512
BORDER = 4
COLS = 3
ROWS = 2

PANEL_NAMES = [
    ["tpose_front", "tpose_back", "front_full"],
    ["view_3q",     "equipment",  "palette"],
]

TPOSE_COL, TPOSE_ROW = 0, 0  # tpose_front → canonical TripoSR input


def cell_box(col, row):
    x = OUTER_MARGIN + col * (CELL_W + BORDER)
    y = OUTER_MARGIN + row * (CELL_H + BORDER)
    return (x, y, x + CELL_W, y + CELL_H)


def extract(sheet_path: Path, char: str, out_dir: Path, offset_x: int, offset_y: int, debug: bool):
    img = Image.open(sheet_path)
    img_w, img_h = img.size

    expected_w = OUTER_MARGIN + COLS * (CELL_W + BORDER) - BORDER + OUTER_MARGIN
    expected_h = OUTER_MARGIN + ROWS * (CELL_H + BORDER) - BORDER + OUTER_MARGIN
    sx = img_w / expected_w
    sy = img_h / expected_h

    if abs(sx - 1.0) > 0.05 or abs(sy - 1.0) > 0.05:
        print(f"Sheet {img_w}×{img_h} vs expected {expected_w}×{expected_h}")
        print(f"Scale factor applied: {sx:.3f} × {sy:.3f}")

    panel_dir = out_dir / "sheet"
    panel_dir.mkdir(parents=True, exist_ok=True)

    debug_img = img.convert("RGB") if debug else None
    debug_draw = ImageDraw.Draw(debug_img) if debug else None

    for row in range(ROWS):
        for col in range(COLS):
            raw = cell_box(col, row)
            box = (
                max(0, int(raw[0] * sx) + offset_x),
                max(0, int(raw[1] * sy) + offset_y),
                min(img_w, int(raw[2] * sx) + offset_x),
                min(img_h, int(raw[3] * sy) + offset_y),
            )
            name = PANEL_NAMES[row][col]
            panel_path = panel_dir / f"{name}.png"
            img.crop(box).save(panel_path)
            print(f"  [{col},{row}] {name:15s} box={box}")

            if debug_draw:
                debug_draw.rectangle(box, outline=(255, 0, 0), width=3)
                debug_draw.text((box[0] + 6, box[1] + 6), name, fill=(255, 0, 0))

    if debug:
        dbg_path = panel_dir / "_debug_crop.png"
        debug_img.save(dbg_path)
        print(f"\n  Debug overlay → {dbg_path}")

    concept_dir = out_dir / "concept"
    concept_dir.mkdir(parents=True, exist_ok=True)

    for panel, dst_name in [("tpose_front", f"{char}_tpose_front.png"),
                             ("tpose_back",  f"{char}_tpose_back.png")]:
        src = panel_dir / f"{panel}.png"
        if src.exists():
            shutil.copy(src, concept_dir / dst_name)

    tpose_dst = concept_dir / f"{char}_tpose_front.png"
    print(f"\nT-pose front → {tpose_dst}")
    print(f"T-pose back  → {concept_dir / f'{char}_tpose_back.png'}")
    print(f"\nNext: feed {tpose_dst} to your multi-view generation pipeline (Zero123++, S4 external, etc.)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract panels from GPT character sheet")
    parser.add_argument("sheet", type=Path, help="Path to GPT sheet PNG")
    parser.add_argument("--character", "-c", required=True, help="Character name (e.g. rogue)")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Base character directory (default: assets/chars/{character})",
    )
    parser.add_argument("--offset-x", type=int, default=0, help="Horizontal pixel offset for all crops")
    parser.add_argument("--offset-y", type=int, default=0, help="Vertical pixel offset for all crops")
    parser.add_argument("--debug", action="store_true", help="Save debug image with crop bounds overlaid")
    args = parser.parse_args()

    out_dir = args.output_dir or Path(f"assets/chars/{args.character}")
    extract(args.sheet, args.character, out_dir, args.offset_x, args.offset_y, args.debug)
