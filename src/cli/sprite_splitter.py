#!/usr/bin/env python3
"""sprite_splitter.py — Split external sprite sheets into individual direction sprites.

Handles sheets from GPT-4o, SpriteFlow, PixelLab, Scenario, etc.
Applies rembg background removal and saves to canonical isoroll directory structure.

Usage:
    python src/cli/sprite_splitter.py sheet.png \\
        --grid 4x2 \\
        --output-dir assets/chars/rogue/stances/neutral-idle \\
        [--directions SE E NE N NW W SW S] \\
        [--no-rembg] \\
        [--prefix extern] \\
        [--padding 4]

Grid conventions (reading order, left→right, top→bottom):
    4x2  (4 cols, 2 rows)  — landscape sheet, common from GPT-4o
    2x4  (2 cols, 4 rows)  — portrait sheet
    8x1  (8 cols, 1 row)   — single strip
    1x8  (1 col,  8 rows)  — vertical strip

Default direction order (canonical isometric): SE E NE N NW W SW S
"""

import argparse
import sys
from pathlib import Path


CANONICAL_DIRS = ["SE", "E", "NE", "N", "NW", "W", "SW", "S"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Split sprite sheet into 8 direction sprites.")
    p.add_argument("sheet",        help="Input sprite sheet image path")
    p.add_argument("--grid",       required=True,
                   help="Grid layout as ROWSxCOLS, e.g. 2x4 or 4x2")
    p.add_argument("--output-dir", required=True,
                   help="Output root; each direction gets its own subdirectory")
    p.add_argument("--directions", nargs=8, default=CANONICAL_DIRS,
                   metavar="DIR",
                   help="8 direction names in reading order (default: SE E NE N NW W SW S)")
    p.add_argument("--no-rembg",   action="store_true",
                   help="Skip background removal (useful if sheet already has transparency)")
    p.add_argument("--prefix",     default="extern",
                   help="Output filename prefix (default: extern)")
    p.add_argument("--padding",    type=int, default=0,
                   help="Pixels to trim from each cell edge before saving")
    return p.parse_args()


def split_sheet(sheet_path: Path, rows: int, cols: int, padding: int = 0):
    """Split image into rows×cols cells and return list in reading order."""
    from PIL import Image
    img = Image.open(sheet_path).convert("RGBA")
    w, h = img.size
    cell_w = w // cols
    cell_h = h // rows
    cells = []
    for row in range(rows):
        for col in range(cols):
            x1 = col * cell_w + padding
            y1 = row * cell_h + padding
            x2 = (col + 1) * cell_w - padding
            y2 = (row + 1) * cell_h - padding
            cells.append(img.crop((x1, y1, x2, y2)))
    return cells


def remove_bg(img):
    try:
        from rembg import remove
        return remove(img)
    except ImportError:
        print("  [warn] rembg not installed — skipping background removal")
        print("         Install: pip install rembg  or  pip install rembg[gpu]")
        return img
    except Exception as e:
        print(f"  [warn] rembg failed ({e}) — saving without background removal")
        return img


def next_index(out_root: Path, prefix: str, direction: str) -> int:
    existing = sorted(out_root.glob(f"{prefix}_*_{direction}.png"))
    return len(existing) + 1


def main() -> None:
    args = parse_args()

    try:
        rows_str, cols_str = args.grid.lower().split("x")
        rows, cols = int(rows_str), int(cols_str)
    except ValueError:
        print(f"Error: --grid must be ROWSxCOLS (e.g. 2x4 or 4x2), got '{args.grid}'")
        sys.exit(1)

    if rows * cols < 8:
        print(f"Error: grid {rows}x{cols} = {rows * cols} cells, need at least 8 for 8 directions")
        sys.exit(1)

    sheet_path = Path(args.sheet)
    if not sheet_path.exists():
        print(f"Error: sheet not found: {sheet_path}")
        sys.exit(1)

    out_root   = Path(args.output_dir)
    directions = list(args.directions)[:8]

    print(f"sheet    : {sheet_path}")
    print(f"grid     : {rows} rows × {cols} cols")
    print(f"dirs     : {' '.join(directions)}")
    print(f"rembg    : {'off' if args.no_rembg else 'on'}")
    print(f"output   : {out_root}")
    print()

    cells = split_sheet(sheet_path, rows, cols, args.padding)[:8]

    out_root.mkdir(parents=True, exist_ok=True)

    for i, (direction, cell) in enumerate(zip(directions, cells)):
        if not args.no_rembg:
            print(f"  [{i + 1}/8] {direction}: removing background...")
            cell = remove_bg(cell)
        else:
            print(f"  [{i + 1}/8] {direction}: saving...")

        idx      = next_index(out_root, args.prefix, direction)
        out_path = out_root / f"{args.prefix}_{idx:05d}_{direction}.png"
        cell.save(out_path)
        print(f"           → {out_path}")

    print()
    print(f"Done. {len(directions)} sprites saved under {out_root}")


if __name__ == "__main__":
    main()
