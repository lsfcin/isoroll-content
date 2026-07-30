#!/usr/bin/env python3
"""
make_tile_guide.py — Generate the color-coded multiview schematic guide for a wall tile (S0-E1).

Face-ID colors (bound to these meanings in the NB prompt, see SPECS.md → Chosen Pipeline):
  red = top · gray = north/back · green = south/front · blue = west end · purple = east end

Layouts:
  9panel — all cardinal + diagonal + TOP, dev/QC reference (matches hand-drawn prototype deck)
  6cell  — NW/NE/TOP over SW/SE/caption, 3x2 aspect — the full NB input format
  2cell  — SW/NE/TOP/caption, one row, 4x1 — one corner per long face, for
           assets where the end caps (blue/purple) don't matter: SW already
           implies SE (same green face, cap ignored) and NE implies NW (same
           gray face, cap ignored). Cardinal N/S panels are never used
           standalone — the module only ever renders corner views (see
           SPECS.md "View count: 4+1"). TOP is always included even here —
           isoroll's top-down view mode needs a real top reference on every
           asset, not just the oblique-implicit sliver in the SW/NE panels.
  1cell  — SW/TOP/caption, one row, 3x1 — simplest case: symmetric content
           where one face + one cap fully implies the rest (e.g. a wall with
           identical front/back and identical west/east end caps). TOP is
           still included for the same top-down-view-mode reason as 2cell.

Cardinal (N/S/W/E) panels are drawn "unfolded-net" style: the TOP face is folded
flat above the body, so N/S panels are W cols x (D+H) rows and W/E panels are
D cols x (W+H) rows — verified against the reference deck (pipeline/prompts/reference).

Thin wrapper over tile_guide_matrix.py: expresses each fixed LAYOUTS layout as a
cells-list (shared W/H/D, per-cell orientation) and delegates rendering to it.

Usage:
  python pipeline/make_tile_guide.py --width 5 --height 4 --layout 6cell --output out.png
"""

import argparse
from pathlib import Path

import tile_guide_matrix

CELL_PX = 320

LAYOUTS = {
    "9panel": [["NW", "N", "NE"], ["W", "TOP", "E"], ["SW", "S", "SE"]],
    "6cell": [["NW", "NE", "TOP"], ["SW", "SE", "CAPTION"]],
    "2cell": [["SW", "NE", "TOP", "CAPTION"]],
    "1cell": [["SW", "TOP", "CAPTION"]],
}


def _panel_label(row, col, cols, kind):
    index = row * cols + col + 1
    suffix = " ▼" if kind == "TOP" else ""
    return f"{index} {kind}{suffix}"


def _layout_to_spec(w, d, h, layout):
    rows_kinds = LAYOUTS[layout]
    cols = len(rows_kinds[0])
    cells = []
    for r, row_kinds in enumerate(rows_kinds):
        for c, kind in enumerate(row_kinds):
            label = f"W{w} H{h} D{d}" if kind == "CAPTION" else _panel_label(r, c, cols, kind)
            cells.append({"row": r, "col": c, "orientation": kind, "w": w, "h": h, "d": d, "label": label})
    return {"rows": len(rows_kinds), "cols": cols, "cells": cells}


def generate(w, d, h, layout, out_path: Path, shared_scale=True):
    spec = _layout_to_spec(w, d, h, layout)
    rows, cols, grid = tile_guide_matrix.parse_spec(spec)
    img, scale_info = tile_guide_matrix.render_cells(rows, cols, grid, CELL_PX, shared_scale)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    tile_guide_matrix.write_scale_sidecar(out_path, scale_info)
    print(f"Saved: {out_path}  ({cols * CELL_PX}x{rows * CELL_PX} px, {layout}, W{w}xH{h}xD{d})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, required=True, help="wall width, grid units (east-west)")
    parser.add_argument("--height", type=int, required=True, help="wall height, grid units")
    parser.add_argument("--depth", type=int, default=1, help="wall thickness, grid units (default 1)")
    parser.add_argument("--layout", choices=list(LAYOUTS), default="6cell")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--legacy-autofit", action="store_true",
                         help="per-cell autofit scale (pre-scale-consistency behavior)")
    args = parser.parse_args()
    generate(args.width, args.depth, args.height, args.layout, args.output, shared_scale=not args.legacy_autofit)
