#!/usr/bin/env python3
"""layout_parse.py — text-grid scene layout DSL → validated Layout model (F1 input)."""

import re
from dataclasses import dataclass, field
from pathlib import Path

from layout_groups import DIAG, ENCLOSE, ROOF_FORMS, SIDE_NAME, STAIR_TYPES, grp_base_data, grp_cell_voxels

WALL, FLOOR, VOID, DOOR, WINDOW = "#", ".", " ", "D", "W"
# Stairs are directional (the arrow points toward the ascent) so that grid
# rotation can remap them and every view sees the same physical staircase.
STAIR_N, STAIR_E, STAIR_S, STAIR_W = "^", ">", "v", "<"
STAIRS = {STAIR_N, STAIR_E, STAIR_S, STAIR_W}
_STAIR_CW = {STAIR_N: STAIR_E, STAIR_E: STAIR_S, STAIR_S: STAIR_W, STAIR_W: STAIR_N}
SOLID = {WALL, DOOR, WINDOW}
# v2 (T2/T3): R/S are group-surface voxel markers, not real grid content — see Group below.
MARKERS = {"R", "S"}
KNOWN = SOLID | STAIRS | DIAG | MARKERS | {FLOOR, VOID}
DEFAULT_WALL_H = 3  # voxels; 1 voxel = 1.5 m side, so walls are 4.5 m tall
_COMPASS_TO_ARROW = {v: k for k, v in SIDE_NAME.items()}


@dataclass
class Level:
    """v2 (T2/T3, .loop/dsl-v2-python/3-arch.md) — one `level N:` block: grid + per-cell attr grids.

    NEW dataclass, additive only — not yet wired into Layout/parse_text/rotate_cw/validate (Loop 4b).
    g: list[str] grid rows. side/type/wmat: dict["r,c"->int|arrow] sparse attr grids. fh: dict["r,c"->int]
    floor-height overlay (rig.frag lay.side/type/wmat/fh maps).
    """
    g: list
    side: dict = field(default_factory=dict)
    type: dict = field(default_factory=dict)
    wmat: dict = field(default_factory=dict)
    fh: dict = field(default_factory=dict)


@dataclass
class Group:
    """v2 (T2/T3) — one roof/stair sloped-surface group (rig.frag `grps` entries).

    NEW dataclass, additive only — not yet produced by parse_text (Loop 4b). cells: list[(r,c)]
    reconstructed from R/S markers per DECISION D3 (3-arch.md). form: index into ROOF_FORMS or
    STAIR_TYPES (layout_groups.py). dir: arrow char ("^"|">"|"v"|"<"). incl: ft/cell (2.5 or 5 for
    stairs). z: base height, voxels. enclose: index into ENCLOSE, roof-only (None for stairs).
    """
    kind: str  # "roof" | "stair"
    cells: list
    form: int
    dir: str
    incl: float
    z: float
    enclose: int = None


@dataclass
class Layout:
    name: str
    grid: list  # list[str], rectangular (right-padded)
    wall_h: int = DEFAULT_WALL_H
    rows: int = 0
    cols: int = 0
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    # v2 (T2/T3), additive: levels[N] = Level for "level N:" blocks; groups = roof/stair Group list.
    # Empty for v1 (flat-grid) layouts — .grid/.rows/.cols stay the single source of truth then.
    levels: dict = field(default_factory=dict)
    groups: list = field(default_factory=list)

    def kind(self, u, v):
        """Cell at column u, row v — VOID outside bounds."""
        if 0 <= v < self.rows and 0 <= u < self.cols:
            return self.grid[v][u]
        return VOID


def _rotate_grid_cw(grid, turns):
    for _ in range(turns % 4):
        grid = ["".join(_STAIR_CW.get(ch, ch) for ch in col) for col in zip(*grid[::-1])]
    return grid


def rotate_cw(layout, turns=1):
    """New Layout turned 90° clockwise `turns` times; stair arrows follow.

    v2: rotates every level's grid the same way. Group cells/dir are NOT re-oriented (no current
    seam exercises rotate_cw on a Layout with groups) — carried over as-is, a known limitation.
    """
    turns = turns % 4
    if layout.levels:
        new_levels = {
            lvl: Level(g=_rotate_grid_cw(level.g, turns), side=level.side, type=level.type,
                       wmat=level.wmat, fh=level.fh)
            for lvl, level in layout.levels.items()
        }
        base_grid = new_levels[min(new_levels)].g
        out = Layout(layout.name, base_grid, layout.wall_h, len(base_grid),
                     len(base_grid[0]) if base_grid else 0)
        out.levels, out.groups = new_levels, layout.groups
        out.errors, out.warnings = layout.errors, layout.warnings
        return out
    grid = _rotate_grid_cw(layout.grid, turns)
    out = Layout(layout.name, grid, layout.wall_h, len(grid), len(grid[0]) if grid else 0)
    out.errors, out.warnings = layout.errors, layout.warnings
    return out


def rotate_point(u, v, rows, cols, turns=1):
    """Continuous-coordinate twin of rotate_cw: one CW turn maps (u, v) → (rows − v, u)."""
    for _ in range(turns % 4):
        u, v = rows - v, u
        rows, cols = cols, rows
    return u, v


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


_HAS_LEVEL = re.compile(r"(?m)^level \d+:$")


def parse_text(text, name="layout"):
    if _HAS_LEVEL.search(text):
        import layout_dsl_v2  # local import: avoids a layout_parse <-> layout_dsl_v2 import cycle
        return layout_dsl_v2.parse_text_v2(text, name)
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
