#!/usr/bin/env python3
"""tile_guide_matrix.py — generic per-cell orientation/dims tile guide matrix renderer.

Generalizes make_tile_guide.py: instead of a fixed named layout sharing one
W/H/D across all panels, this takes an explicit matrix size plus a list of
cells, each with its own orientation, W/H/D, and label. Missing (row, col)
combos render blank. Reuses tile_guide_render.py's per-panel drawing
primitives unchanged.

Usage:
  python pipeline/tile_guide_matrix.py --cells cells.json --output out.png
  python pipeline/tile_guide_matrix.py --cells '{"rows":1,"cols":2,"cells":[...]}' --output out.png
"""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from generate_sheet_template import load_font
from tile_guide_render import (
    FACE_TOP, FACE_LONG, FACE_CAP,
    draw_iso_panel, draw_flat_grid, draw_square_grid,
)

BG = (0, 0, 0)
MAGENTA = (255, 0, 255)
ORIENTATIONS = {"N", "S", "E", "W", "NE", "NW", "SE", "SW", "TOP", "CAPTION"}
OBLIQUE = {"NW", "NE", "SW", "SE"}
REQUIRED_KEYS = ("row", "col", "orientation", "w", "h", "d")


@dataclass
class CellSpec:
    row: int
    col: int
    orientation: str
    w: int
    h: int
    d: int
    label: str = ""
    mark: bool = False


def draw_panel(img, draw, orientation, w, d, h, box, mark=False):
    if orientation in ("NW", "NE", "SW", "SE"):
        draw_iso_panel(img, w, d, h, orientation, box, mark_edge=mark)
    elif orientation in ("N", "S"):
        draw_flat_grid(draw, w, d + h, FACE_LONG, d, box)
    elif orientation in ("W", "E"):
        draw_flat_grid(draw, d, w + h, FACE_CAP, w, box)
    elif orientation == "TOP":
        draw_square_grid(draw, w, d, FACE_TOP, box)


def draw_caption(draw, box, font, label):
    cx, cy, cw, ch = box
    draw.text((cx + cw / 2 - 40, cy + ch / 2 - 8), label, font=font, fill=MAGENTA)


def _validate_dims(index, orientation, w, h, d):
    dims = (w, h, d)
    for key, val in zip(("w", "h", "d"), dims):
        if not isinstance(val, int) or val < 0:
            raise ValueError(f"cells[{index}]: {key} must be a non-negative int, got {val!r}")
    zeros = [v for v in dims if v == 0]
    allow_one_zero = orientation in OBLIQUE or orientation == "TOP"
    if allow_one_zero and len(zeros) > 1:
        raise ValueError(f"cells[{index}]: {orientation} may have at most one zero dim (flat), got {dims}")
    if not allow_one_zero and orientation != "CAPTION" and zeros:
        raise ValueError(f"cells[{index}]: {orientation} panel needs w/h/d all positive, got {dims}")


def _validate_cell(raw, index, rows, cols, seen):
    missing = [k for k in REQUIRED_KEYS if k not in raw]
    if missing:
        raise ValueError(f"cells[{index}]: missing required keys {missing}")
    row, col = raw["row"], raw["col"]
    if not (0 <= row < rows):
        raise ValueError(f"cells[{index}]: row {row} out of bounds for rows={rows}")
    if not (0 <= col < cols):
        raise ValueError(f"cells[{index}]: col {col} out of bounds for cols={cols}")
    if (row, col) in seen:
        raise ValueError(f"cells[{index}]: duplicate cell at (row={row}, col={col})")
    orientation = raw["orientation"]
    if orientation not in ORIENTATIONS:
        raise ValueError(f"cells[{index}]: invalid orientation {orientation!r}, must be one of {sorted(ORIENTATIONS)}")
    _validate_dims(index, orientation, raw["w"], raw["h"], raw["d"])
    seen.add((row, col))
    return CellSpec(row, col, orientation, raw["w"], raw["h"], raw["d"], raw.get("label", ""), bool(raw.get("mark", False)))


def parse_spec(spec):
    if "rows" not in spec or "cols" not in spec:
        raise ValueError("spec must have top-level 'rows' and 'cols'")
    rows, cols = spec["rows"], spec["cols"]
    if not (isinstance(rows, int) and rows > 0):
        raise ValueError(f"rows must be a positive int, got {rows!r}")
    if not (isinstance(cols, int) and cols > 0):
        raise ValueError(f"cols must be a positive int, got {cols!r}")
    seen = set()
    grid = {}
    for index, raw in enumerate(spec.get("cells", [])):
        cell = _validate_cell(raw, index, rows, cols, seen)
        grid[(cell.row, cell.col)] = cell
    return rows, cols, grid


def render_cells(rows, cols, grid, cell_px=320):
    img = Image.new("RGB", (cols * cell_px, rows * cell_px), BG)
    draw = ImageDraw.Draw(img)
    font = load_font(16)
    for r in range(rows):
        for c in range(cols):
            cell = grid.get((r, c))
            if cell is None:
                continue
            box = (c * cell_px, r * cell_px, cell_px, cell_px)
            if cell.orientation == "CAPTION":
                draw_caption(draw, box, font, cell.label)
            else:
                draw_panel(img, draw, cell.orientation, cell.w, cell.d, cell.h, box, cell.mark)
            if cell.label and cell.orientation != "CAPTION":
                draw.text((box[0] + 6, box[1] + 4), cell.label, font=font, fill=MAGENTA)
    for c in range(1, cols):
        x = c * cell_px
        draw.line([(x, 0), (x, rows * cell_px)], fill=MAGENTA, width=2)
    for r in range(1, rows):
        y = r * cell_px
        draw.line([(0, y), (cols * cell_px, y)], fill=MAGENTA, width=2)
    return img


def generate(spec, out_path: Path, cell_px=320):
    rows, cols, grid = parse_spec(spec)
    img = render_cells(rows, cols, grid, cell_px)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"Saved: {out_path}  ({cols * cell_px}x{rows * cell_px} px, {len(grid)} cells, {rows}x{cols} matrix)")


def resolve_cells_arg(raw: str):
    try:
        spec = json.loads(raw)
    except json.JSONDecodeError:
        spec = json.loads(Path(raw).read_text())
    return spec


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", required=True, help="literal JSON string or path to a JSON file")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cell-px", type=int, default=320, dest="cell_px")
    args = parser.parse_args()
    generate(resolve_cells_arg(args.cells), args.output, args.cell_px)
