#!/usr/bin/env python3
"""layout_parse.py — text-grid scene layout DSL → validated Layout model (F1 input)."""

from dataclasses import dataclass, field
from pathlib import Path

WALL, FLOOR, VOID, DOOR, WINDOW = "#", ".", " ", "D", "W"
# Stairs are directional (the arrow points toward the ascent) so that grid
# rotation can remap them and every view sees the same physical staircase.
STAIR_N, STAIR_E, STAIR_S, STAIR_W = "^", ">", "v", "<"
STAIRS = {STAIR_N, STAIR_E, STAIR_S, STAIR_W}
_STAIR_CW = {STAIR_N: STAIR_E, STAIR_E: STAIR_S, STAIR_S: STAIR_W, STAIR_W: STAIR_N}
SOLID = {WALL, DOOR, WINDOW}
KNOWN = SOLID | STAIRS | {FLOOR, VOID}
DEFAULT_WALL_H = 4  # grid units, matches the W5 H4 tile-guide era


@dataclass
class Layout:
    name: str
    grid: list  # list[str], rectangular (right-padded)
    wall_h: int = DEFAULT_WALL_H
    rows: int = 0
    cols: int = 0
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def kind(self, u, v):
        """Cell at column u, row v — VOID outside bounds."""
        if 0 <= v < self.rows and 0 <= u < self.cols:
            return self.grid[v][u]
        return VOID


def rotate_cw(layout, turns=1):
    """New Layout turned 90° clockwise `turns` times; stair arrows follow."""
    grid = layout.grid
    for _ in range(turns % 4):
        grid = ["".join(_STAIR_CW.get(ch, ch) for ch in col) for col in zip(*grid[::-1])]
    out = Layout(layout.name, grid, layout.wall_h, len(grid), len(grid[0]) if grid else 0)
    out.errors, out.warnings = layout.errors, layout.warnings
    return out


def _split_directives(lines):
    directives, grid_lines, in_grid = {}, [], False
    for line in lines:
        stripped = line.rstrip("\n")
        if not in_grid and not stripped.strip():
            continue
        head = stripped.split(":")[0].strip()
        if not in_grid and ":" in stripped and head.isidentifier():
            directives[head] = stripped.partition(":")[2].strip()
            continue
        in_grid = True
        grid_lines.append(stripped)
    while grid_lines and not grid_lines[-1].strip():
        grid_lines.pop()
    return directives, grid_lines


def _in_wall_run(layout, u, v):
    """True if (u,v) sits in a straight wall run along either axis."""
    horizontal = layout.kind(u - 1, v) in SOLID and layout.kind(u + 1, v) in SOLID
    vertical = layout.kind(u, v - 1) in SOLID and layout.kind(u, v + 1) in SOLID
    return horizontal or vertical


def validate(layout):
    for v, row in enumerate(layout.grid):
        for u, ch in enumerate(row):
            if ch not in KNOWN:
                layout.errors.append(f"({u},{v}) unknown cell {ch!r}")
            elif ch in (DOOR, WINDOW) and not _in_wall_run(layout, u, v):
                layout.errors.append(f"({u},{v}) {ch!r} not inside a straight wall run")
    return layout


def parse_text(text, name="layout"):
    directives, grid_lines = _split_directives(text.splitlines())
    cols = max((len(line) for line in grid_lines), default=0)
    grid = [line.ljust(cols) for line in grid_lines]
    layout = Layout(
        name=directives.get("name", name),
        grid=grid,
        wall_h=int(directives.get("wall_h", DEFAULT_WALL_H)),
        rows=len(grid),
        cols=cols,
    )
    if not grid:
        layout.errors.append("empty grid")
    return validate(layout)


def load(path):
    p = Path(path)
    return parse_text(p.read_text(encoding="utf-8"), name=p.stem)
