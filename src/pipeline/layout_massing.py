#!/usr/bin/env python3
"""layout_massing.py — Layout grid → box list: merged wall runs with openings, floor strips, stair steps."""

from dataclasses import dataclass, field

from layout_parse import DOOR, FLOOR, SOLID, STAIRS, STAIR_E, STAIR_N, STAIR_S, STAIR_W, WINDOW

STEPS = 4  # sub-boxes per stair cell
STAIR_RISE = 1.0  # total stair height, grid units
_ASCENT = {STAIR_N: (0, -1), STAIR_E: (1, 0), STAIR_S: (0, 1), STAIR_W: (-1, 0)}


@dataclass
class Opening:
    kind: str  # "door" | "window"
    offset: int  # cell index along the run's major axis, 0-based


@dataclass
class Box:
    u0: float
    v0: float
    l: float  # extent along u
    d: float  # extent along v
    h: float  # extent along z (0 = flat)
    kind: str  # "wall" | "floor" | "step"
    openings: list = field(default_factory=list)
    axis: str = "u"  # wall-run axis; openings pierce across it


def _run_openings(layout, u0, v0, length, axis):
    openings = []
    for i in range(length):
        u, v = (u0 + i, v0) if axis == "u" else (u0, v0 + i)
        ch = layout.kind(u, v)
        if ch in (DOOR, WINDOW):
            openings.append(Opening("door" if ch == DOOR else "window", i))
    return openings


def _cell_axis(layout, u, v):
    """Wall-run axis a cell belongs to; horizontal wins ties (matches merge order)."""
    if layout.kind(u - 1, v) in SOLID or layout.kind(u + 1, v) in SOLID:
        return "u"
    if layout.kind(u, v - 1) in SOLID or layout.kind(u, v + 1) in SOLID:
        return "v"
    return "u"


def _cell_wall_boxes(layout, wall_h):
    """One 1x1 box per solid cell — exact painter's order for rendering."""
    boxes = []
    for v in range(layout.rows):
        for u in range(layout.cols):
            if layout.kind(u, v) in SOLID:
                boxes.append(Box(u, v, 1, 1, wall_h, "wall",
                                 _run_openings(layout, u, v, 1, "u"), _cell_axis(layout, u, v)))
    return boxes


def _merged_wall_boxes(layout, wall_h):
    """Greedy merge: horizontal runs ≥2 first, then vertical runs of the rest, then singletons."""
    used, boxes = set(), []
    for v in range(layout.rows):
        u = 0
        while u < layout.cols:
            run = 0
            while layout.kind(u + run, v) in SOLID and (u + run, v) not in used:
                run += 1
            if run > 1:
                used.update((u + i, v) for i in range(run))
                boxes.append(Box(u, v, run, 1, wall_h, "wall", _run_openings(layout, u, v, run, "u"), "u"))
            u += max(run, 1)
    for u in range(layout.cols):
        v = 0
        while v < layout.rows:
            run = 0
            while layout.kind(u, v + run) in SOLID and (u, v + run) not in used:
                run += 1
            if run > 1:
                used.update((u, v + i) for i in range(run))
                boxes.append(Box(u, v, 1, run, wall_h, "wall", _run_openings(layout, u, v, run, "v"), "v"))
            v += max(run, 1)
    for v in range(layout.rows):
        for u in range(layout.cols):
            if layout.kind(u, v) in SOLID and (u, v) not in used:
                boxes.append(Box(u, v, 1, 1, wall_h, "wall"))
    return boxes


def _floor_boxes(layout):
    boxes = []
    for v in range(layout.rows):
        u = 0
        while u < layout.cols:
            run = 0
            while layout.kind(u + run, v) == FLOOR:
                run += 1
            if run:
                boxes.append(Box(u, v, run, 1, 0, "floor"))
            u += max(run, 1)
    return boxes


def _stair_boxes(layout):
    """Each stair cell becomes STEPS sub-boxes rising toward the arrow direction."""
    boxes = []
    for v in range(layout.rows):
        for u in range(layout.cols):
            ch = layout.kind(u, v)
            if ch not in STAIRS:
                continue
            du, dv = _ASCENT[ch]
            for i in range(STEPS):
                t = (i + 0.5) / STEPS  # step center along ascent, 0 = low end
                height = STAIR_RISE * (i + 1) / STEPS
                if du:  # ascent along u: thin slices across u
                    su = u + (t - 0.5 / STEPS if du > 0 else 1 - t - 0.5 / STEPS)
                    boxes.append(Box(su, v, 1 / STEPS, 1, height, "step"))
                else:  # ascent along v
                    sv = v + (t - 0.5 / STEPS if dv > 0 else 1 - t - 0.5 / STEPS)
                    boxes.append(Box(u, sv, 1, 1 / STEPS, height, "step"))
    return boxes


def massing(layout, merge=True):
    """All boxes for one layout orientation, unsorted (renderer sorts per view).

    merge=True (export/manifest lane) fuses wall runs; merge=False (render lane)
    keeps 1x1 cell boxes so simple (u+v) painter sorting is exact."""
    walls = _merged_wall_boxes if merge else _cell_wall_boxes
    return _floor_boxes(layout) + _stair_boxes(layout) + walls(layout, layout.wall_h)
