#!/usr/bin/env python3
"""layout_dsl_v2.py — v2 grammar: "level N:"/"layer X:"/"roof:"/"stair:" blocks -> Layout.

T2/T3 (.loop/dsl-v2-python/3-arch.md): parser + D3 union/double-book validation, split out of
layout_parse.py to stay under the project's per-file line cap. Only layout_parse.parse_text calls
into this module (lazily, to dodge the import cycle) — no other module should import it directly.
"""

import re

from layout_groups import ENCLOSE, ROOF_FORMS, STAIR_TYPES, grp_base_data, grp_cell_voxels
from layout_parse import DEFAULT_WALL_H, DOOR, KNOWN, MARKERS, SOLID, VOID, WINDOW, Group, Layout, Level, _COMPASS_TO_ARROW

_LEVEL_RE = re.compile(r"^level (\d+):$")
_LAYER_RE = re.compile(r"^layer (side|type|wmat|fh):$")
_GROUP_RE = re.compile(
    r"^(roof|stair): (\d+),(\d+) (\d+),(\d+) form=(\w+) dir=([NESW]) "
    r"incl=([\d.]+)ft z=(-?[\d.]+)(?: enclose=(\w+))?$"
)


def _num(s):
    return float(s) if "." in s else int(s)


def _make_group(m):
    kind = m.group(1)
    r0, c0, r1, c1 = (int(m.group(i)) for i in (2, 3, 4, 5))
    cells = [(r, c) for r in range(min(r0, r1), max(r0, r1) + 1) for c in range(min(c0, c1), max(c0, c1) + 1)]
    form_names = STAIR_TYPES if kind == "stair" else ROOF_FORMS
    enclose_name = m.group(10)
    enclose = (ENCLOSE.index(enclose_name) if enclose_name else 0) if kind == "roof" else None
    return Group(kind=kind, cells=cells, form=form_names.index(m.group(6)), dir=_COMPASS_TO_ARROW[m.group(7)],
                 incl=_num(m.group(8)), z=_num(m.group(9)), enclose=enclose)


def _is_header(line):
    stripped = line.strip()
    return bool(_LEVEL_RE.match(stripped) or _LAYER_RE.match(stripped) or _GROUP_RE.match(stripped))


def _read_block(lines, i):
    """Raw content lines from i until a boundary. A v2 grid/attr row is never a zero-length string
    (VOID is a literal " ", length >= 1) so an empty line unambiguously means a block separator."""
    rows = []
    while i < len(lines) and lines[i] != "" and not _is_header(lines[i]):
        rows.append(lines[i])
        i += 1
    return rows, i


def _read_directives(lines):
    directives, i = {}, 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == "":
            i += 1
            continue
        if _is_header(lines[i]):
            break
        head = stripped.split(":")[0].strip()
        if ":" not in stripped or not head.isidentifier():
            break
        directives[head] = stripped.partition(":")[2].strip()
        i += 1
    return directives, i


def _parse_body(lines, i):
    levels, groups = {}, []
    while i < len(lines):
        if lines[i] == "":
            i += 1
            continue
        level_m = _LEVEL_RE.match(lines[i].strip())
        if level_m:
            levels[int(level_m.group(1))], i = _parse_level_block(lines, i + 1)
            continue
        group_m = _GROUP_RE.match(lines[i].strip())
        if group_m:
            groups.append(_make_group(group_m))
            i += 1
            continue
        i += 1  # stray/unrecognized line — ignored, not fatal
    return levels, groups


def _parse_level_block(lines, i):
    grid_rows, i = _read_block(lines, i)
    cols = max((len(r) for r in grid_rows), default=0)
    level = Level(g=[r.ljust(cols) for r in grid_rows])
    while i < len(lines) and lines[i] != "":
        layer_m = _LAYER_RE.match(lines[i].strip())
        if not layer_m:
            break
        attr_rows, i = _read_block(lines, i + 1)
        target = getattr(level, layer_m.group(1))
        for r, row in enumerate(attr_rows):
            for c, ch in enumerate(row):
                if ch not in (".", " "):
                    target[f"{r},{c}"] = ch
    return level, i


def _touches_wall(rows, r, c):
    """v2 opening rule: >=1 solid orthogonal neighbor (looser than v1's straight-run check — v2
    doors may sit at a level's floor/interior boundary, e.g. a hatch between levels)."""
    def cell(rr, cc):
        return rows[rr][cc] if 0 <= rr < len(rows) and 0 <= cc < len(rows[rr]) else VOID

    return any(cell(rr, cc) in SOLID for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)))


def _validate_level(layout, lvl, level):
    for r, row in enumerate(level.g):
        for c, ch in enumerate(row):
            if ch not in KNOWN:
                layout.errors.append(f"level {lvl} ({c},{r}) unknown cell {ch!r}")
            elif ch in (DOOR, WINDOW) and not _touches_wall(level.g, r, c):
                layout.errors.append(f"level {lvl} ({c},{r}) {ch!r} not adjacent to any wall")


def _validate_groups(layout):
    """D3 union check: every authored R/S marker must be covered by exactly one group's computed
    voxel span (misplaced marker / wrong type), and no voxel may be claimed twice (double-book)."""
    gvox = {}
    for group in layout.groups:
        if group.incl not in (2.5, 5):
            layout.errors.append(f"group incl must be 2.5 or 5 (ft/cell): {group.incl}")
            continue
        base = grp_base_data(group)
        marker = "S" if group.kind == "stair" else "R"
        for (r, c) in group.cells:
            lo, hi = grp_cell_voxels(base, group, r, c)
            for lvl in range(lo, hi):
                gvox.setdefault((lvl, r, c), []).append(marker)
    for (lvl, r, c), markers in gvox.items():
        if len(markers) > 1:
            layout.errors.append(f"level {lvl} ({c},{r}) double-booked by {len(markers)} groups")
    for lvl, level in layout.levels.items():
        for r, row in enumerate(level.g):
            for c, ch in enumerate(row):
                if ch not in MARKERS:
                    continue
                markers = gvox.get((lvl, r, c))
                if not markers:
                    layout.errors.append(f"level {lvl} ({c},{r}) marker {ch!r} not covered by any group")
                elif len(markers) == 1 and markers[0] != ch:
                    layout.errors.append(f"level {lvl} ({c},{r}) marker {ch!r} != group type {markers[0]!r}")


def parse_text_v2(text, name):
    lines = text.splitlines()
    directives, i = _read_directives(lines)
    levels, groups = _parse_body(lines, i)
    base_grid = levels[min(levels)].g if levels else []
    layout = Layout(name=directives.get("name", name), grid=base_grid,
                     wall_h=int(directives.get("wall_h", DEFAULT_WALL_H)),
                     rows=len(base_grid), cols=len(base_grid[0]) if base_grid else 0)
    layout.levels, layout.groups = levels, groups
    if not levels:
        layout.errors.append("empty grid")
    _validate_groups(layout)
    for lvl, level in levels.items():
        _validate_level(layout, lvl, level)
    return layout
