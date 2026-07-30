#!/usr/bin/env python3
"""layout_rotate.py — clockwise grid rotation primitives, on plain data (no Layout dataclasses, so
layout_parse can import this without a cycle).

One CW turn of an `rows x cols` grid maps cell (r, c) -> (c, rows-1-r): `grid[::-1]` reverses the
rows, then `zip(*)` transposes, which is exactly that composition. Everything keyed by cell must
travel through `rotate_cell` — the grid itself, a group's cells, and the per-cell attribute overlays
(side/type/wmat/fh). Missing any one of them leaves a layout whose geometry rotated and whose
metadata did not; the wmat overlay is what would silently repaint materials onto other cells when a
view switches.

Direction chars (stair arrows in the grid, a group's ascent arrow) advance one step CW per turn.
"""

from layout_groups import ARROW_CW


def rotate_arrow(ch, turns=1):
    """Advance a direction char (^ > v <) `turns` steps clockwise; anything else passes through."""
    for _ in range(turns % 4):
        ch = ARROW_CW.get(ch, ch)
    return ch


def rotate_grid_cw(grid, turns=1):
    """`turns` CW quarter-turns of a list[str] grid; stair arrows inside it follow the rotation."""
    for _ in range(turns % 4):
        grid = ["".join(ARROW_CW.get(ch, ch) for ch in col) for col in zip(*grid[::-1])]
    return grid


def rotate_cells(cells, rows, cols, turns=1):
    """List of (r, c) after `turns` CW turns, tracking the row/col swap between turns."""
    for _ in range(turns % 4):
        cells = [(c, rows - 1 - r) for (r, c) in cells]
        rows, cols = cols, rows
    return cells


def rotate_attrs(attrs, rows, cols, turns=1):
    """The "r,c"-keyed per-cell overlay (Level.side/type/wmat/fh) remapped; arrow values follow."""
    for _ in range(turns % 4):
        turned = {}
        for key, value in attrs.items():
            r, c = (int(part) for part in key.split(","))
            turned[f"{c},{rows - 1 - r}"] = rotate_arrow(value) if isinstance(value, str) else value
        attrs = turned
        rows, cols = cols, rows
    return attrs
