#!/usr/bin/env python3
"""nb_sheet_processor.py — CLI for Nano Banana tile-sheet processing.

Processes NB PNG tile-sheets: removes black background (transparent via rembg),
optionally removes a watermark region, splits the sheet into grid cells,
groups multi-view tiles (NW/NE/SW/SE/TOP), and outputs individual transparent PNGs.

Usage examples:
    # 6-cell layout (default: 2 rows × 3 cols)
    python nb_sheet_processor.py sheet.png --layout 6cell --prefix wall_stone --output tiles/wall_stone/

    # 2-cell layout with explicit rows/cols
    python nb_sheet_processor.py sheet.png --layout 2cell --rows 1 --cols 4 --prefix floor_temple

    # With watermark removal (bottom-right caption cell) and padding trim
    python nb_sheet_processor.py sheet.png --layout 6cell --watermark-region 0.65,0.65,1.0,1.0 --padding 2

Multi-view grouping logic:
    The layout template (6cell, 2cell, 1cell) defines the cell labels in a grid.
    Each non-CAPTION cell becomes one viewpoint. The script outputs one PNG per
    viewpoint, named {prefix}_{viewpoint}.png.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from sheet_utils import (
    SheetLayout,
    load_image,
    remove_background,
    remove_watermark,
    split_grid,
)


def parse_watermark_region(text: str | None) -> tuple[float, float, float, float] | None:
    """Parse 'x1,y1,x2,y2' into a 4-tuple, or return None."""
    if text is None:
        return None
    try:
        parts = [float(p.strip()) for p in text.split(",")]

        if len(parts) != 4:
            raise ValueError
    except ValueError as exc:
        msg = "--watermark-region must be x1,y1,x2,y2"
        raise argparse.ArgumentTypeError(msg) from exc

    return (parts[0], parts[1], parts[2], parts[3])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process Nano Banana tile-sheets into transparent per-view."
    )
    parser.add_argument("input", help="Path to input tile-sheet PNG")
    parser.add_argument(
        "--rows", type=int, default=None,
        help="Grid rows (optional; defaults from --layout)",
    )
    parser.add_argument(
        "--cols", type=int, default=None,
        help="Grid columns (optional; defaults from --layout)",
    )
    parser.add_argument(
        "--layout", choices=["6cell", "2cell", "1cell"], default="6cell",
        help="NB tile-sheet layout template (default: 6cell)",
    )
    parser.add_argument(
        "-o", "--output", default=".",
        help="Output directory (default: cwd)",
    )
    parser.add_argument(
        "--prefix", default="tile",
        help="Output filename prefix (default: tile)",
    )
    parser.add_argument(
        "--watermark-region", default=None,
        help="Watermark region as x1,y1,x2,y2 in 0..1 relative coords (e.g. 0.65,0.65,1.0,1.0). "
             "None disables watermark removal.",
    )
    parser.add_argument(
        "--padding", type=int, default=0,
        help="Pixels to trim from each cell edge (default: 0)",
    )
    return parser.parse_args()


def run(args: argparse.Namespace) -> list[Path]:
    """Main processing pipeline."""
    input_path = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    layout = SheetLayout.get(args.layout)
    rows = args.rows if args.rows is not None else layout.rows
    cols = args.cols if args.cols is not None else layout.cols

    print(f"input   : {input_path}")
    print(f"layout  : {layout.name} ({layout.expected_cells()} labels)")
    print(f"grid    : {rows} rows × {cols} cols")
    print(f"output  : {out_dir}")
    print(f"prefix  : {args.prefix}")
    print()

    # 1. Load
    img = load_image(input_path)

    # 2. Background removal (rembg, mandatory)
    print("Removing background with rembg...")
    img = remove_background(img)

    # 3. Watermark removal (optional)
    watermark_region = parse_watermark_region(getattr(args, "watermark_region", None))
    if watermark_region is not None:
        print("Removing watermark region...")
        w, h = img.size
        abs_region = (
            int(w * watermark_region[0]),
            int(h * watermark_region[1]),
            int(w * watermark_region[2]),
            int(h * watermark_region[3]),
        )
        img = remove_watermark(img, region=abs_region)

    # 4. Grid split
    cells = split_grid(img, rows, cols, padding=args.padding)
    if len(cells) != layout.expected_cells():
        msg = (
            f"Grid mismatch: {rows}×{cols}={len(cells)} cells, "
            f"but layout '{layout.name}' expects {layout.expected_cells()}"
        )
        raise ValueError(msg)

    # 5. Group multi-view tiles by layout label
    labels = layout.labels()
    saved: list[Path] = []

    for label, cell_img in zip(labels, cells):
        if label == "CAPTION":
            print("  [skip] CAPTION cell")
            continue
        filename = f"{args.prefix}_{label}.png"
        out_path = out_dir / filename
        cell_img.save(out_path)
        saved.append(out_path)
        print(f"  → {out_path}")

    print()
    print(f"Done. {len(saved)} view(s) saved under {out_dir}")
    return saved


def main() -> None:
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()
