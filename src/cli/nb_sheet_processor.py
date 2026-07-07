#!/usr/bin/env python3
"""nb_sheet_processor.py — CLI for Nano Banana tile-sheet processing.

Processes NB PNG tile-sheets: detects the real cell grid from the magenta
linework (NB drifts it a few px from an even division), splits the sheet,
strips magenta lines/labels from each cell, removes the background per cell
(rembg — per cell because u2net expects one salient object), and saves one
transparent PNG per viewpoint.

Usage examples:
    # single-object 6cell sheet (2 rows x 3 cols)
    python nb_sheet_processor.py sheet.png --layout 6cell --prefix wall_stone -o tiles/wall_stone/

    # batch sheet: two 6cell blocks stacked vertically (4 rows x 3 cols)
    python nb_sheet_processor.py sheet.png --layout 6cell --groups door_leaf,window --prefix b1

    # with watermark removal and no rembg (fast dry run)
    python nb_sheet_processor.py sheet.png --watermark-region 0.65,0.65,1.0,1.0 --keep-bg

Output naming: {prefix}_{viewpoint}.png, or {prefix}_{group}_{viewpoint}.png
when --groups lists several objects (one layout block per group, stacked
top-to-bottom in the sheet).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from sheet_grid import detect_grid, strip_linework
from sheet_utils import SheetLayout, load_image, remove_background, remove_watermark, split_cells


def parse_watermark_region(text: str | None) -> tuple[float, float, float, float] | None:
    """Parse 'x1,y1,x2,y2' into a 4-tuple, or return None."""
    region = None
    if text is not None:
        try:
            parts = [float(p.strip()) for p in text.split(",")]
            if len(parts) != 4:
                raise ValueError
        except ValueError as exc:
            msg = "--watermark-region must be x1,y1,x2,y2"
            raise argparse.ArgumentTypeError(msg) from exc
        region = (parts[0], parts[1], parts[2], parts[3])
    return region


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process Nano Banana tile-sheets into transparent per-view PNGs."
    )
    parser.add_argument("input", help="Path to input tile-sheet PNG")
    parser.add_argument(
        "--layout", choices=["6cell", "2cell", "1cell"], default="6cell",
        help="Layout of one object block (default: 6cell)",
    )
    parser.add_argument(
        "--groups", default=None,
        help="Comma-separated object names for a batch sheet with one layout "
             "block per object, stacked vertically (default: single object)",
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
        help="Watermark region as x1,y1,x2,y2 in 0..1 relative coords "
             "(e.g. 0.65,0.65,1.0,1.0). None disables watermark removal.",
    )
    parser.add_argument(
        "--padding", type=int, default=0,
        help="Pixels to trim from each cell edge (default: 0)",
    )
    parser.add_argument(
        "--keep-bg", action="store_true",
        help="Skip rembg background removal (magenta is still stripped)",
    )
    return parser.parse_args()


def _apply_watermark_removal(img: Image.Image, region_text: str | None) -> Image.Image:
    region = parse_watermark_region(region_text)
    result = img
    if region is not None:
        print("Removing watermark region...")
        w, h = img.size
        abs_region = (
            int(w * region[0]),
            int(h * region[1]),
            int(w * region[2]),
            int(h * region[3]),
        )
        result = remove_watermark(img, region=abs_region)
    return result


def _cell_jobs(layout: SheetLayout, groups: list[str]) -> list[tuple[str, str]]:
    """(group, label) per grid cell in reading order — blocks stack vertically."""
    jobs = []
    for group in groups:
        for row in layout.grid:
            for label in row:
                jobs.append((group, label))
    return jobs


def _out_name(prefix: str, group: str, label: str, single: bool) -> str:
    name = f"{prefix}_{label}.png" if single else f"{prefix}_{group}_{label}.png"
    return name


def run(args: argparse.Namespace) -> list[Path]:
    """Main processing pipeline."""
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    layout = SheetLayout.get(args.layout)
    groups = args.groups.split(",") if args.groups else [args.prefix]
    rows = layout.rows * len(groups)
    cols = layout.cols

    img = load_image(Path(args.input))
    img = _apply_watermark_removal(img, getattr(args, "watermark_region", None))
    xs, ys = detect_grid(img, rows, cols)
    print(f"grid    : {rows}x{cols} — cols at {xs}, rows at {ys}")
    cells = split_cells(img, xs, ys, padding=args.padding)

    saved: list[Path] = []
    jobs = _cell_jobs(layout, groups)
    for (group, label), cell_img in zip(jobs, cells):
        if label == "CAPTION":
            print(f"  [skip] CAPTION cell ({group})")
            continue
        cell_img = strip_linework(cell_img)
        if not args.keep_bg:
            cell_img = remove_background(cell_img)
        out_path = out_dir / _out_name(args.prefix, group, label, len(groups) == 1)
        cell_img.save(out_path)
        saved.append(out_path)
        print(f"  -> {out_path}")

    print(f"Done. {len(saved)} view(s) saved under {out_dir}")
    return saved


def main() -> None:
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()
